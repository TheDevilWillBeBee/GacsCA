"""D8 candidate rules: explicit opt-in, all backends and block simulation."""
import numpy as np
import pytest
import torch

from gacsca import level0_np, level0_spec
from gacsca.build import make_system, make_tower
from gacsca.gpu import Level0GPU, to_gpu, to_np
from gacsca.gpu_engine import CleanGraphRunner
from gacsca.hierarchy import encode_state_info, decode_state_info
from gacsca.params import Params, Variant


@pytest.mark.parametrize("eraser", ["printed", "no_ones", "at_most_one"])
def test_flag2_scalar_numpy_cuda_all_left_patterns_and_boundaries(eraser):
    p = Params(Q=32, ncol=2)
    v = Variant(flag2_healthy_erase=eraser)
    for x in (0, 1, 2, 5, 31, 32):
        S = level0_np.initial(p, 64)
        for i in range(6):
            S["f2"][:, (x - i) % p.L] = (np.arange(64) >> i) & 1
        expected = level0_np.step(S, p, v)
        gpu = Level0GPU(p, v)
        st = to_gpu(S)
        actual = to_np(gpu.step(st, torch.empty_like(st), 1))
        for k in S:
            np.testing.assert_array_equal(actual[k], expected[k])
        for b in range(64):
            cfg = level0_spec.Cfg(*(S[k][b] for k in ("addr", "age", "f1", "f2", "wf1", "wf2")))
            result = level0_spec.step_cell(cfg, x, p.Q, p.U, v)[:4]
            assert result == tuple(expected[k][b, x] for k in ("addr", "age", "f1", "f2"))


@pytest.mark.parametrize("eraser", ["no_ones", "at_most_one"])
def test_candidate_random_damaged_states_match_all_local_backends(eraser):
    p = Params(Q=32, ncol=2)
    v = Variant(flag2_healthy_erase=eraser)
    rng = np.random.default_rng(406)
    S = level0_np.random_state(p, 3, rng)
    for k in ("wf1", "wf2"):
        S[k][:] = rng.integers(0, 2, S[k].shape)
    expected = level0_np.step(S, p, v)
    g = Level0GPU(p, v)
    st = to_gpu(S)
    actual = to_np(g.step(st, torch.empty_like(st), 1))
    for k in S:
        np.testing.assert_array_equal(actual[k], expected[k])
    for b in range(3):
        cfg = level0_spec.Cfg(*(S[k][b] for k in ("addr", "age", "f1", "f2", "wf1", "wf2")))
        out = level0_spec.step(cfg, p.Q, p.U, v)
        for k in ("addr", "age", "f1", "f2"):
            np.testing.assert_array_equal(getattr(out, k), expected[k][b])


def test_research_variants_explicit_and_two_site_repair_distinguishes_them():
    assert Variant.gray().flag2_healthy_erase == Variant.masumori().flag2_healthy_erase == "printed"
    with pytest.raises(ValueError, match="Flag2"):
        Variant(flag2_healthy_erase="typo")
    p = Params(Q=8192, ncol=1)
    S = level0_np.initial(p, 1)
    S["f2"][:, 31:33] = 1
    for eraser, count in (("printed", 2), ("no_ones", 1), ("at_most_one", 0)):
        out = level0_np.step(S, p, Variant(flag2_healthy_erase=eraser))
        assert out["f2"].sum() == count


@pytest.mark.parametrize("eraser", ["no_ones", "at_most_one"])
def test_candidates_complete_colony_computation_of_flag2_patterns(eraser):
    v = Variant(flag2_healthy_erase=eraser)
    s = make_system(Q=256, U=16384, ncol=16, Qs=16, Us=2048,
                    full_registers=True, variant=v)
    upper_p = Params(Q=16, U=2048, ncol=1)
    upper = level0_np.initial(upper_p, 64)
    upper["age"][:] = 777
    for i in range(6):
        upper["f2"][:, 10 - i] = (np.arange(64) >> i) & 1
    expected = level0_np.step(upper, upper_p, v)
    expected.pop("_info")
    info = encode_state_info(upper, s.L, s.p.Q)
    gpu = s.gpu_engine()
    runner = CleanGraphRunner(gpu, gpu.to_gpu(s.np_engine().initial(64, info_bits=info)))
    runner.run(s.p.U)
    actual = decode_state_info(gpu.info_bits(runner.state).cpu().numpy(), s.L, s.p.Q)
    for k in expected:
        np.testing.assert_array_equal(actual[k], expected[k], err_msg=k)


@pytest.mark.parametrize("eraser", ["no_ones", "at_most_one"])
def test_candidate_fivefold_tower_matches_two_damaged_upper_transitions(eraser):
    v = Variant(flag2_healthy_erase=eraser)
    lower, upper = make_tower(Q0=512, U0=65536, U1=16384, R=5, D=1,
                              full_registers=True, variant=v)
    engine = upper.np_engine()
    S = engine.initial(3)
    S["age"][:] = np.array([0, upper.sched.trickle[0] - 1, upper.p.U - 1])[:, None]
    rng = np.random.default_rng(273)
    S["trk"][:] = rng.integers(0, 2, S["trk"].shape, dtype=np.uint8)
    S["f2"][:, 12:14] = 1
    S["f2"][:, 25:35] = 1
    S["addr"][:, 49] = 17
    S["age"][:, 60] = 63
    S["wf1"][:, 59:64] = 1
    S["wf2"][:, :5] = 1
    gpu_upper = upper.gpu_engine()
    u = gpu_upper.to_gpu(S)
    actual = gpu_upper.to_np(gpu_upper.step(u, torch.empty_like(u), 0))
    for k, value in engine.step(S).items():
        np.testing.assert_array_equal(actual[k], value)
    info = encode_state_info(S, lower.L, lower.p.Q)
    physical = lower.np_engine().initial(3, info_bits=info)
    physical["simage"][:] = np.repeat(S["age"], lower.p.Q, axis=1)
    physical["simaddr"][:] = np.repeat(S["addr"], lower.p.Q, axis=1)
    gpu = lower.gpu_engine()
    runner = CleanGraphRunner(gpu, gpu.to_gpu(physical))
    for _ in range(2):
        runner.run(lower.p.U)
        S = engine.step(S)
        actual = decode_state_info(gpu.info_bits(runner.state).cpu().numpy(), lower.L, lower.p.Q)
        for k in S:
            np.testing.assert_array_equal(actual[k], S[k], err_msg=k)
