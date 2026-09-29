import numpy as np
import pytest
import torch

from gacsca.build import make_system
from gacsca.engine_np import redistribute
from gacsca.gpu_engine import CleanGraphRunner
from experiments.quiescent import quiet_intervals, try_skip_quiescent, advance_certified


@pytest.fixture(params=["compressed", "gray"])
def system(request):
    if request.param == "gray":
        return make_system(Q=8192, U=1048576, ncol=2, R=5, D=1,
                           Qs=16, Us=2048, schedule="gray")
    return make_system(Q=256, U=16384, ncol=2, R=3, D=1, Qs=16, Us=2048)


def setup(system):
    gpu = system.gpu_engine()
    lo, hi = max(quiet_intervals(gpu), key=lambda ab: ab[1] - ab[0])
    state = system.np_engine().initial(2)
    state["age"][:] = lo
    rng = np.random.default_rng(214)
    primary = rng.integers(0, 2, (2, system.p.L, system.T.NT), dtype=np.uint8)
    state["trk"] = redistribute(primary, system.T.R)
    return gpu, state, lo, hi


def test_certificate_matches_every_packed_bit_and_preserves_graph_replay(system):
    gpu, state, lo, hi = setup(system)
    steps = min(257, hi - lo)
    actual = CleanGraphRunner(gpu, gpu.to_gpu(state), block_steps=16)
    direct = CleanGraphRunner(gpu, gpu.to_gpu(state), block_steps=16)
    address = actual.state.data_ptr()
    cert = try_skip_quiescent(actual, steps)
    assert cert is not None and cert["steps"] == steps
    assert actual.state.data_ptr() == address and actual.steps == steps
    direct.run(steps)
    torch.testing.assert_close(actual.state, direct.state, rtol=0, atol=0)
    actual.run(19); direct.run(19)
    torch.testing.assert_close(actual.state, direct.state, rtol=0, atol=0)


@pytest.mark.parametrize("damage", ["clock", "address", "flag", "register", "copy"])
def test_unsafe_state_is_not_skipped_or_mutated(system, damage):
    gpu, state, lo, hi = setup(system)
    if damage == "clock": state["age"][0, 100] += 1
    elif damage == "address": state["addr"][0, 100] = 101
    elif damage == "flag": state["f2"][0, 100] = 1
    elif damage == "register": state["simage"][0, 100] = 1
    else: state["trk"][0, 100, system.T["INFO"], 0] ^= 1
    packed = gpu.to_gpu(state)
    actual = CleanGraphRunner(gpu, packed, block_steps=16)
    assert try_skip_quiescent(actual, 17) is None
    assert actual.steps == 0
    torch.testing.assert_close(actual.state, packed, rtol=0, atol=0)
    direct = CleanGraphRunner(gpu, packed, block_steps=16)
    advance_certified(actual, 17)
    direct.run(17)
    torch.testing.assert_close(actual.state, direct.state, rtol=0, atol=0)


def test_clock_boundaries_rejected_and_mixed_execution_exact(system):
    gpu, state, lo, hi = setup(system)
    runner = CleanGraphRunner(gpu, gpu.to_gpu(state), block_steps=16)
    assert try_skip_quiescent(runner, hi - lo + 1) is None
    state["age"][:] = lo - 3
    actual = CleanGraphRunner(gpu, gpu.to_gpu(state), block_steps=16)
    direct = CleanGraphRunner(gpu, gpu.to_gpu(state), block_steps=16)
    certs = []
    advance_certified(actual, 35, certs)
    direct.run(35)
    torch.testing.assert_close(actual.state, direct.state, rtol=0, atol=0)
    # Regardless of whether the preceding op left a fixed point, results are exact.
    assert actual.steps == direct.steps == 35
    with pytest.raises(ValueError):
        advance_certified(actual, -1)
