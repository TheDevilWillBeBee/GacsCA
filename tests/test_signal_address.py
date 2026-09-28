"""Gray p.35 signal writes use computed, not raw, holder Address."""
import numpy as np
import pytest
import torch

from gacsca.build import make_system
from gacsca.engine_np import redistribute
from gacsca.gpu_engine import CleanGraphRunner
from gacsca.hierarchy import encode_state_info, decode_state_info
from experiments.gray_protocol import track_bits


@pytest.mark.parametrize("target,source", [(3, "T1"), (8192 - 3, "T0")])
def test_signal_write_repairs_address_before_choosing_destination(target, source):
    s = make_system(Q=8192, U=1048576, ncol=1, R=5, D=1,
                    Qs=16, Us=2048, schedule="gray")
    engine, gpu = s.np_engine(), s.gpu_engine()
    state = engine.initial(2)
    state["age"][:] = s.sched.signal_write
    primary = np.zeros((2, s.p.L, s.T.NT), dtype=np.uint8)
    primary[:, :, s.T[source]] = 1
    state["trk"] = redistribute(primary, 5)
    state["addr"][0, target] = 100  # missed write under a raw-address guard
    state["addr"][1, 100] = target  # spurious write under a raw-address guard
    expected = np.zeros((2, s.p.L), dtype=np.uint8)
    expected[:, target] = 1
    packed = gpu.to_gpu(state)
    outputs = (engine.step(state), gpu.to_np(gpu.step(packed, torch.empty_like(packed), 1)))
    for out in outputs:
        assert not out["f1"].any()  # no wiping can hide the addressing distinction
        np.testing.assert_array_equal(out["trk"][:, :, s.T["INFO"], :], redistribute(expected, 5))
    for name in outputs[0]:
        np.testing.assert_array_equal(outputs[0][name], outputs[1][name])


def test_gray_interpreter_uses_computed_holder_address_for_both_signals():
    # 32 distinct upper sites, no radius aliasing; this is a damaged-state
    # phase test, NOT a whole upper colony or complete lower work period.
    upper = make_system(Q=8192, U=1048576, ncol=1, R=5, D=1,
                        Qs=16, Us=2048, schedule="gray")
    lower = make_system(Q=8192, U=1048576, ncol=32, R=5, D=1,
                        Qs=8192, Us=1048576, Qss=16, Uss=2048,
                        with_tracks=True, schedule="gray", prog_up=upper.prog, L_up=upper.L,
                        trickle_up=upper.sched.trickle, regwin_up=upper.sched.reg_window)
    state = {k: v[:, :32].copy() for k, v in upper.np_engine().initial(2).items()}
    state["addr"][:] = (8176 + np.arange(32)) % 8192
    state["age"][:] = upper.sched.signal_write
    primary = np.zeros((2, 32, upper.T.NT), dtype=np.uint8)
    primary[:, :, upper.T["T0"]] = primary[:, :, upper.T["T1"]] = 1
    state["trk"] = redistribute(primary, 5)
    state["addr"][0, 13] = 100  # true Q-3
    state["addr"][1, 19] = 100  # true 3
    expected = upper.np_engine().step(state)
    for batch, site in [(0, 13), (1, 19)]:
        assert expected["f1"][batch, site] == 0
        assert expected["trk"][batch, site, upper.T["INFO"], 2] == 1
    bits = encode_state_info(state, lower.L, lower.p.Q)
    physical = lower.np_engine().initial(2)
    start = 7 * lower.p.U // 8
    physical["age"][:] = start
    values = np.zeros((2, lower.p.L, lower.T.NT), dtype=np.uint8)
    values[:, :, lower.T["INFO"]] = bits
    for bank in "ABC":
        for j in range(-5, 6):
            values[:, :, lower.T.arg(j, bank)] = np.roll(bits, -j * lower.p.Q, axis=1)
    physical["trk"] = redistribute(values, 5)
    gpu = lower.gpu_engine()
    runner = CleanGraphRunner(gpu, gpu.to_gpu(physical))
    del physical, values
    runner.run(lower.sched.compute_end - start)
    decoded = decode_state_info(track_bits(gpu, runner.state, lower.T["HOLD"]), lower.L, lower.p.Q)
    for name in expected:
        np.testing.assert_array_equal(decoded[name], expected[name], err_msg=name)


def test_computed_signal_controls_do_not_read_beyond_radius_five():
    s = make_system(Q=8192, U=1048576, ncol=1, R=5, D=1,
                    Qs=16, Us=2048, schedule="gray")
    state = s.np_engine().initial(2)
    state["age"][:] = s.sched.signal_write
    rng = np.random.default_rng(3535)
    state["trk"][:] = rng.integers(0, 2, state["trk"].shape, dtype=np.uint8)[0:1]
    x = 3
    state["addr"][:, x] = 100
    outside = np.array([x - 7, x - 6, x + 6, x + 7]) % s.p.L
    for name in ("addr", "age", "f1", "f2", "wf1", "wf2", "simage", "simaddr"):
        state[name][1, outside] ^= 1
    state["trk"][1, outside] ^= 1
    gpu = s.gpu_engine()
    packed = gpu.to_gpu(state)
    for out in (s.np_engine().step(state), gpu.to_np(gpu.step(packed, torch.empty_like(packed), 1))):
        for name in out:
            np.testing.assert_array_equal(out[name][0, x], out[name][1, x], err_msg=name)
