"""Source-timing/reset contracts for the new Gray five-stage mode."""
import numpy as np
import pytest
import torch

from gacsca.build import make_system
from gacsca.engine_np import repair, redistribute
from gacsca.gray_schedule import reset_ranges, stage_windows
from gacsca.gpu_engine import CleanGraphRunner
from gacsca.hierarchy import encode_state_info, decode_state_info
from gacsca.params import Params
from gacsca import level0_np
from gacsca.interp import writes


@pytest.fixture(scope="module")
def system():
    return make_system(Q=8192, U=1048576, ncol=1, R=5, D=1,
                       Qs=16, Us=2048, schedule="gray")


def test_stage_timing_storage_and_rest_contract(system):
    s = system.sched
    assert s.gather_starts == [1, 262145, 524289]
    assert s.trickle == (786432, 802816)
    assert 524288 <= s.signal_compute[0] < s.signal_write < 655360
    assert 917504 <= s.compute_start < s.compute_end <= 983040
    assert system.T.NT == 87
    padding = {system.T.arg(j, bank) for bank in "ABCD" for j in (-6, 6)}
    assert all(not (writes(op, system.T) & padding) for op in system.prog.ops if op.kind != "RESET")
    assert len({system.T.arg(j, bank) for bank in "ABCD" for j in range(-6, 7)}) == 52
    for a, active_end, end in stage_windows(system.p.U):
        for op in system.prog.ops:
            if op.t0 == system.p.U - 1:  # commit produces next period's Age=0
                continue
            assert not max(active_end, op.t0) < min(end, op.t1), op
    for stage, (begin, _, _) in enumerate(s.stages):
        resets = [o for o in system.prog.ops_at(begin) if o.kind == "RESET"]
        assert [(o.dst, o.param) for o in resets] == reset_ranges(system.T, stage)
        assert sum(o.param2 for o in resets) == 1
        cleared = {t for o in resets for t in range(o.dst, o.param)}
        assert all(system.T.arg(j, bank) in cleared for bank in "ABCD" for j in (-6, 6))


@pytest.mark.parametrize("stage", range(5))
def test_reset_preserves_only_history_and_info_numpy_cuda(system, stage):
    engine, gpu = system.np_engine(), system.gpu_engine()
    S = engine.initial(1)
    S["age"][:] = system.sched.stages[stage][0]
    S["simage"][:] = 1201; S["simaddr"][:] = 513
    rng = np.random.default_rng(52 + stage)
    prim = rng.integers(0, 2, (1, system.p.L, system.T.NT), dtype=np.uint8)
    S["trk"] = redistribute(prim, 5)
    expected = prim.copy()
    for lo, hi in reset_ranges(system.T, stage):
        expected[..., lo:hi] = 0
    state = gpu.to_gpu(S)
    outputs = (engine.step(S), gpu.to_np(gpu.step(state, torch.empty_like(state), 0)))
    for out in outputs:
        np.testing.assert_array_equal(out["trk"], redistribute(expected, 5))
        assert not out["simage"].any() and not out["simaddr"].any()
    for k in outputs[0]:
        np.testing.assert_array_equal(outputs[0][k], outputs[1][k])


def test_reset_holder_control_fault_and_third_word_numpy_cuda(system):
    engine, gpu = system.np_engine(), system.gpu_engine()
    S = engine.initial(1)
    S["age"][:] = 0
    S["trk"][:] = np.random.default_rng(45).integers(0, 2, S["trk"].shape, dtype=np.uint8)
    S["age"][0, 100] = 9
    S["addr"][0, 200] = 17
    S["simage"][:] = 23; S["simaddr"][:] = 11
    state = gpu.to_gpu(S)
    actual = gpu.to_np(gpu.step(state, torch.empty_like(state), 1))
    expected = engine.step(S)
    for k in expected:
        np.testing.assert_array_equal(actual[k], expected[k], err_msg=k)
    # Only the faulty-clock holder skips the reset; other holders erase it.
    assert not repair(actual["trk"])[..., system.T["BF0"]].any()


def test_gray_mode_rejects_unimplemented_or_out_of_scope_settings():
    with pytest.raises(ValueError, match="Gray mode requires"):
        make_system(schedule="gray")
    with pytest.raises(ValueError, match="requires prog_up"):
        make_system(Q=8192, U=1048576, R=5, D=1, schedule="gray", with_tracks=True)


def test_fifth_stage_repairs_one_corrupt_gather_but_not_two():
    from experiments.gray_protocol import track_bits
    system = make_system(Q=8192, U=1048576, ncol=16, R=5, D=1,
                         Qs=16, Us=2048, schedule="gray")
    upper_p = Params(Q=16, U=2048, ncol=1)
    upper = level0_np.initial(upper_p, 5)
    upper["age"][:] = 777
    upper["f1"][:] = np.arange(16) % 3 == 0
    upper["f2"][:] = np.arange(16) % 2
    info = encode_state_info(upper, system.L, system.p.Q)
    S = system.np_engine().initial(5)
    S["age"][:] = system.sched.stages[4][0]
    V = np.zeros((5, system.p.L, system.T.NT), np.uint8)
    V[..., system.T["INFO"]] = info
    corrupted = ("", "A", "B", "C", "AB")
    for bank in "ABC":
        for j in range(-5, 6):
            source = np.roll(info, -j * system.p.Q, axis=1).copy()
            for b, banks in enumerate(corrupted):
                if bank in banks:
                    source[b] ^= 1
            V[..., system.T.arg(j, bank)] = source
    S["trk"] = redistribute(V, 5)
    del V
    gpu = system.gpu_engine()
    runner = CleanGraphRunner(gpu, gpu.to_gpu(S))
    del S
    runner.run(system.sched.compute_end - system.sched.stages[4][0])
    actual = decode_state_info(track_bits(gpu, runner.state, system.T["HOLD"]), system.L, system.p.Q)
    # With two bad histories the voted input is complemented, not repaired.
    # Verify this negative control against its own direct transition too.
    voted = {k: v.copy() for k, v in upper.items()}
    for name, (_, width) in system.L.fields.items():
        voted[name.lower()][4] ^= (1 << width) - 1
    expected = level0_np.step(voted, upper_p)
    clean = level0_np.step(upper, upper_p)
    for k in actual:
        np.testing.assert_array_equal(actual[k], expected[k], err_msg=k)
        np.testing.assert_array_equal(actual[k][:4], clean[k][:4], err_msg=k)
    assert np.any(actual["age"][4] != clean["age"][4])
