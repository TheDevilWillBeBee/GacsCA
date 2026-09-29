"""Wide controls must survive packing, repair, faults, interpretation and reload."""
import numpy as np
import pytest
import torch

from gacsca.build import make_system, make_tower
from gacsca.gpu_engine import CleanGraphRunner
from gacsca.hierarchy import encode_state_info, decode_state_info
from gacsca.microcode import Op
from gacsca.noise import cell_noise_word, splitmix64


@pytest.mark.parametrize("R", [3, 5])
@pytest.mark.parametrize("bits", [20, 31])
def test_wide_roundtrip_and_local_rule_match_numpy(R, bits):
    s = make_system(Q=256, U=32768, ncol=2, R=R, D=1, Qs=16, Us=2048)
    gpu, reference = s.gpu_engine(register_bits=bits), s.np_engine()
    S = reference.initial(2)
    rng = np.random.default_rng(bits + R)
    for field in ("simage", "simaddr"):
        S[field][:] = rng.integers(0, 1 << bits, S[field].shape, dtype=np.int32)
        S[field][0, 0] = (1 << bits) - 1
        S[field][0, 1] = 1 << 16
        S[field][0, 2] = 0
    S["trk"][:] = rng.integers(0, 2, S["trk"].shape, dtype=np.uint8)
    S["age"][:] = 10
    S["age"][0, 100] = 19
    S["addr"][0, 200] = 17
    state = gpu.to_gpu(S)
    assert gpu.track_base == 5 and state.shape[-1] == 5 + R * gpu.NW
    got = gpu.to_np(state)
    for name in S:
        np.testing.assert_array_equal(got[name], S[name], err_msg=name)
    for t in range(3):
        S = reference.step(S)
        state = gpu.step(state, torch.empty_like(state), t)
        got = gpu.to_np(state)
        for name in S:
            np.testing.assert_array_equal(got[name], S[name], err_msg=name)
    # Graph replay must respect the extra header word, including odd tails.
    runner = CleanGraphRunner(gpu, state)
    assert torch.equal(runner.run(259), gpu.run(state.clone(), 259, 0))


@pytest.mark.parametrize("bits", [20, 31])
@pytest.mark.parametrize("version", [1, 2])
def test_wide_noise_exact_scalar_oracle(bits, version):
    s = make_system(ncol=1)
    gpu = s.gpu_engine(register_bits=bits, noise_version=version, seed=173)
    state = gpu.to_gpu(s.np_engine().initial(2))
    t = (1 << 43) + 21
    actual = gpu.step(state, torch.empty_like(state), t, 1).cpu().numpy()
    for b, x in ((0, 0), (1, 17), (1, 220)):
        h = cell_noise_word(gpu.seed, t, b, x, version)
        h2 = splitmix64(h); h3 = splitmix64(h2); h4 = splitmix64(h3); h5 = splitmix64(h4)
        expected = [h2 % s.p.Q, h3 % s.p.U, h4 & 15,
                    h5 & ((1 << bits) - 1), (h5 >> 32) & ((1 << bits) - 1)]
        g = h5
        for _ in range(gpu.R * gpu.NW):
            g = splitmix64(g); expected.append(g & 0xFFFFFFFF)
        np.testing.assert_array_equal(actual[b, x], expected)
    assert actual[..., 3:5].max() < 1 << bits
    assert (actual[..., 3:5] >= 1 << 16).any()


def test_wide_schema_rejects_truncation_and_wrong_buffers():
    s = make_system(Q=512, U=65536, Qs=8192, Us=1048576, ncol=1)
    gpu = s.gpu_engine()
    assert gpu.register_bits == 20
    assert s.np_engine().register_bits == 20
    with pytest.raises(ValueError, match="at least 20"):
        s.gpu_engine(register_bits=16)
    with pytest.raises(ValueError, match="16,31"):
        s.gpu_engine(register_bits=32)
    S = s.np_engine().initial(1)
    S["simage"][0, 0] = 1 << 20
    with pytest.raises(ValueError, match="does not fit"):
        gpu.to_gpu(S)
    S["simage"][0, 0] = -1
    with pytest.raises(ValueError, match="does not fit"):
        gpu.to_gpu(S)
    S["simage"][0, 0] = 0
    state = gpu.to_gpu(S)
    with pytest.raises(ValueError, match="state width"):
        gpu.to_np(state[..., :-1])
    wrong = torch.empty((*state.shape[:-1], state.shape[-1] - 1), dtype=state.dtype, device=state.device)
    with pytest.raises(RuntimeError, match="output shape"):
        gpu.step(state, wrong, 0)


def test_twenty_bit_clock_interpretation_commit_and_register_reload():
    lower, upper = make_tower(Q0=512, U0=65536, U1=1048576, R=5, D=1)
    high_age = (1 << 18) + 1
    upper.prog.add(Op("CONST", high_age, high_age + 1, 0, upper.p.Q,
                      dst=upper.T["BF0"], param=1))
    engine = upper.np_engine()
    S = engine.initial(3)
    S["age"][:] = np.array([65535, high_age, upper.p.U - 1])[:, None]
    S["trk"][:] = np.random.default_rng(893).integers(0, 2, S["trk"].shape, dtype=np.uint8)
    physical = lower.np_engine().initial(3, info_bits=encode_state_info(S, lower.L, lower.p.Q))
    physical["simage"][:] = np.repeat(S["age"], lower.p.Q, axis=1)
    physical["simaddr"][:] = np.repeat(S["addr"], lower.p.Q, axis=1)
    gpu = lower.gpu_engine()
    assert gpu.register_bits == 20
    runner = CleanGraphRunner(gpu, gpu.to_gpu(physical))
    for _ in range(2):
        runner.run(lower.p.U)
        S = engine.step(S)
        decoded = decode_state_info(gpu.info_bits(runner.state).cpu().numpy(), lower.L, lower.p.Q)
        for name in S:
            np.testing.assert_array_equal(decoded[name], S[name], err_msg=name)
        raw = gpu.to_np(runner.state)
        np.testing.assert_array_equal(raw["simage"], np.repeat(S["age"], lower.p.Q, axis=1))
        np.testing.assert_array_equal(raw["simaddr"], np.repeat(S["addr"], lower.p.Q, axis=1))
