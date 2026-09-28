"""Reset-safe interpretation with full Gray parameters and full state alphabets.

Dynamic phase tests use a 16-cell arbitrary upper ring (no neighbor aliasing,
but NOT a complete Q1=8192 colony). Factory tests separately check full geometry.
"""
import numpy as np
import pytest
import torch

from gacsca.build import make_system, make_tower
from gacsca.engine_np import redistribute
from gacsca.gpu_engine import CleanGraphRunner
from gacsca.hierarchy import encode_state_info, decode_state_info
from gacsca.params import Variant
from experiments.gray_protocol import track_bits


def test_full_gray_tower_geometry_and_stage_budget():
    lower, upper = make_tower(Q0=8192, U0=1048576, Q1=8192, U1=1048576,
                              ncol0=8192, R=5, D=1, schedule="gray")
    assert lower.p.L == 67108864 and upper.p.L == 8192
    assert lower.T.NT == upper.T.NT == 87
    assert lower.L.K == 504 and upper.L.K == 51
    assert lower.L.fields["SIMAGE"][1] == 16
    for system in (lower, upper):
        assert system.sched.compute_end <= 15 * system.p.U // 16
        assert system.p.Q >= 2 * system.L.K
    lo, hi = lower.sched.reg_window
    assert 7 * lower.p.U // 8 < lo < hi == lower.sched.compute_start < lower.sched.iphase[0]
    with pytest.raises(ValueError, match="whole upper colonies"):
        make_tower(Q0=8192, U0=1048576, Q1=8192, U1=1048576,
                   ncol0=16, R=5, D=1, schedule="gray")


@pytest.mark.parametrize("eraser", ["printed", "at_most_one"])
def test_gray_input_reload_and_interpreted_phases_on_arbitrary_upper_ring(eraser):
    variant = Variant(flag2_healthy_erase=eraser)
    upper = make_system(Q=8192, U=1048576, ncol=1, R=5, D=1,
                        Qs=16, Us=2048, Qss=2, Uss=2, schedule="gray", variant=variant)
    lower = make_system(Q=8192, U=1048576, ncol=16, R=5, D=1,
                        Qs=upper.p.Q, Us=upper.p.U, Qss=16, Uss=2048,
                        with_tracks=True, schedule="gray", variant=variant, prog_up=upper.prog, L_up=upper.L,
                        trickle_up=upper.sched.trickle, regwin_up=upper.sched.reg_window)
    ages = [0, upper.p.U // 4, upper.sched.gather_starts[0] + 5 * upper.p.Q + 1,
            upper.sched.signal_write, upper.sched.trickle[0] - 1, upper.p.U - 1]
    B = len(ages)
    engine = upper.np_engine()
    S = {k: v[:, :16].copy() for k, v in engine.initial(B).items()}
    S["age"][:] = np.array(ages)[:, None]
    S["addr"][:] = (8190 + np.arange(16)) % 8192
    rng = np.random.default_rng(605)
    for name in ("simage", "simaddr"):
        S[name][:] = rng.integers(0, 65536, S[name].shape, dtype=np.int32)
    for name in ("f1", "f2", "wf1", "wf2", "trk"):
        S[name][:] = rng.integers(0, 2, S[name].shape, dtype=np.uint8)
    expected = engine.step(S)
    bits = encode_state_info(S, lower.L, lower.p.Q)
    physical = lower.np_engine().initial(B)
    physical["age"][:] = 7 * lower.p.U // 8
    physical["simage"][:] = (1 << 20) - 1
    physical["simaddr"][:] = (1 << 20) - 1
    V = np.zeros((B, lower.p.L, lower.T.NT), np.uint8)
    V[..., lower.T["INFO"]] = bits
    for bank in "ABC":
        for j in range(-5, 6):
            V[..., lower.T.arg(j, bank)] = np.roll(bits, -j * lower.p.Q, axis=1)
    physical["trk"] = redistribute(V, 5)
    del V
    gpu = lower.gpu_engine()
    assert gpu.register_bits == 20 and gpu.track_base == 5
    runner = CleanGraphRunner(gpu, gpu.to_gpu(physical))
    del physical
    start = 7 * lower.p.U // 8
    reload_end = lower.sched.reg_window[1]
    runner.run(reload_end - start)
    for word, name in ((3, "age"), (4, "addr")):
        actual = runner.state[..., word].cpu().numpy()
        np.testing.assert_array_equal(actual, np.repeat(S[name], lower.p.Q, axis=1))
    runner.run(lower.sched.compute_end - reload_end)
    decoded = decode_state_info(track_bits(gpu, runner.state, lower.T["HOLD"]), lower.L, lower.p.Q)
    for name in expected:
        np.testing.assert_array_equal(decoded[name], expected[name], err_msg=f"HOLD.{name}")
    # Gray mode retains the loaded INPUT controls through this period, not an
    # output cache. The next period resets and reloads them from fresh gathers.
    np.testing.assert_array_equal(runner.state[..., 3].cpu().numpy(), np.repeat(S["age"], lower.p.Q, axis=1))
    # Separate commit microstep test, not a claim of executing the skipped rest.
    runner.state[..., 1] = lower.p.U - 1
    state = gpu.step(runner.state, torch.empty_like(runner.state), 0)
    decoded = decode_state_info(gpu.info_bits(state).cpu().numpy(), lower.L, lower.p.Q)
    for name in expected:
        np.testing.assert_array_equal(decoded[name], expected[name], err_msg=f"Info.{name}")
