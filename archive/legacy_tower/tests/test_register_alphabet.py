"""A simulated-cell encoding must cover its actual fault-generated alphabet."""
import numpy as np
import pytest

from gacsca.build import make_system, make_tower
from gacsca.gpu_engine import CleanGraphRunner
from gacsca.hierarchy import encode_state_info, decode_state_info


def test_legacy_encoding_cannot_represent_legal_faulty_register():
    lower, upper = make_tower()
    state = upper.np_engine().initial(1)
    state["simage"][:] = 65535
    # This is a legal packed16 state of the upper implementation.
    gpu = upper.gpu_engine()
    np.testing.assert_array_equal(gpu.to_np(gpu.to_gpu(state))["simage"], state["simage"])
    # Legacy encoding used only log2(U2)=11 bits; scalar encoding truncated it.
    assert lower.L.fields["SIMAGE"][1] == 11
    with pytest.raises(ValueError, match="SIMAGE"):
        encode_state_info(state, lower.L, lower.p.Q)


def test_full_register_encoding_and_interpretation_cover_fault_values():
    lower, upper = make_tower(Q0=512, U0=65536, U1=16384, R=5, D=1, full_registers=True)
    engine = upper.np_engine()
    upper_gpu = upper.gpu_engine()
    assert lower.L.fields["SIMAGE"][1] == upper_gpu.register_bits == 16
    assert lower.L.fields["SIMADDR"][1] == upper_gpu.register_bits
    state = engine.initial(3)
    state["age"][:] = np.array([0, upper.sched.compute_start + 200, upper.p.U - 1])[:, None]
    rng = np.random.default_rng(946)
    for name in ("simage", "simaddr"):
        state[name][:] = rng.integers(0, 65536, state[name].shape, dtype=np.int32)
        state[name][:, 7] = 65535
    state["trk"][:] = rng.integers(0, 2, state["trk"].shape, dtype=np.uint8)
    bits = encode_state_info(state, lower.L, lower.p.Q)
    decoded = decode_state_info(bits, lower.L, lower.p.Q)
    for k in state:
        np.testing.assert_array_equal(decoded[k], state[k])
    physical = lower.np_engine().initial(3, info_bits=bits)
    physical["simage"][:] = np.repeat(state["age"], lower.p.Q, axis=1)
    physical["simaddr"][:] = np.repeat(state["addr"], lower.p.Q, axis=1)
    gpu = lower.gpu_engine()
    runner = CleanGraphRunner(gpu, gpu.to_gpu(physical))
    runner.run(lower.p.U)
    expected = engine.step(state)
    actual = decode_state_info(gpu.info_bits(runner.state).cpu().numpy(), lower.L, lower.p.Q)
    for k in expected:
        np.testing.assert_array_equal(actual[k], expected[k], err_msg=k)


def test_gray_defaults_to_full_register_alphabet():
    s = make_system(Q=8192, U=1048576, R=5, D=1, Qs=16, Us=2048, schedule="gray")
    assert s.L.fields["SIMAGE"][1] == s.L.fields["SIMADDR"][1] == 16
    assert s.L.K == 51
