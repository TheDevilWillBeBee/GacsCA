"""A simulated stage reset must clear registers as well as selected tracks."""
import numpy as np
import pytest

from gacsca.build import make_tower
from gacsca.hierarchy import encode_state_info, decode_state_info
from gacsca.gpu_engine import CleanGraphRunner
from gacsca.interp import InterpCtx
from gacsca.microcode import Op


@pytest.mark.parametrize("R", [3, 5])
def test_interpreted_disjoint_resets_match_damaged_upper_rule(R):
    kw = dict(R=5, D=1, Q0=512, U0=32768, U1=8192) if R == 5 else {}
    lower, upper = make_tower(**kw)
    # Extend an otherwise unchanged upper program at an initially idle age.
    # Disjoint address masks also test that own registers use own address,
    # while redundant track copies use the holder-inferred target address.
    upper.prog.add(Op("RESET", 0, 1, 0, 32, dst=upper.T["HOLD"], param=upper.T["BF10"], param2=1))
    upper.prog.add(Op("RESET", 0, 1, 16, 64, dst=upper.T["MAILL"], param=upper.T.NT))
    # Four simultaneous resets need no value latches: do not index the
    # interpreter's three value-source slots for the fourth reset.
    for track in (upper.T.arg(-6), upper.T.arg(6, "B")):
        upper.prog.add(Op("RESET", 0, 1, 0, 64, dst=track, param=track + 1))
    engine = upper.np_engine()
    S = engine.initial(1)
    rng = np.random.default_rng(700 + R)
    S["trk"][:] = rng.integers(0, 2, S["trk"].shape, dtype=np.uint8)
    S["simage"][:] = 777; S["simaddr"][:] = 5
    S["age"][0, 19] = 17
    S["addr"][0, 40] = 29
    expected = engine.step(S)
    physical = lower.np_engine().initial(1, info_bits=encode_state_info(S, lower.L, lower.p.Q))
    physical["simage"][:] = np.repeat(S["age"], lower.p.Q, axis=1)
    physical["simaddr"][:] = np.repeat(S["addr"], lower.p.Q, axis=1)
    gpu = lower.gpu_engine()
    runner = CleanGraphRunner(gpu, gpu.to_gpu(physical))
    runner.run(lower.p.U)
    actual = decode_state_info(gpu.info_bits(runner.state).cpu().numpy(), lower.L, lower.p.Q)
    for k in expected:
        np.testing.assert_array_equal(actual[k], expected[k], err_msg=k)
    assert expected["simage"][0, 10] == 0
    assert expected["simage"][0, 19] == 777  # wrong clock skips this reset
    assert expected["simage"][0, 50] == 777  # outside the register-reset range


def test_unknown_simulated_instruction_is_rejected():
    lower, upper = make_tower()
    upper.prog.add(Op("UNSUPPORTED", 0, 1))
    with pytest.raises(NotImplementedError, match="UNSUPPORTED"):
        InterpCtx(lower.L, lower.T, upper.prog, upper.L, upper.sched.trickle, None)
