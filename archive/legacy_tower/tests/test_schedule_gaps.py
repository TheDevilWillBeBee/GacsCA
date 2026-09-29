"""Distinguishing witnesses for the *current compressed* schedule's source gaps.

These assert observed behavior, not fidelity: a Gray-scheduled alternative must
clear this scratch island at the period boundary. Keep the two contracts distinct.
"""
import numpy as np
import pytest
import torch

from gacsca.build import make_system
from gacsca.engine_np import repair, redistribute


@pytest.mark.parametrize("R,Q,U", [(3, 256, 16384), (5, 8192, 1048576)])
def test_compressed_rule_retains_scratch_island_across_period_boundary(R, Q, U):
    system = make_system(Q=Q, U=U, ncol=1, R=R, D=1, Qs=16, Us=2048)
    S = system.np_engine().initial(1)
    S["age"][:] = U - 1
    primary = repair(S["trk"])
    # One coherent scratch-bit island occupies exactly R neighboring holders.
    # It is not Info, gathered history, or data needed by the next stage.
    primary[0, 100, system.T["BF0"]] = 1
    S["trk"] = redistribute(primary, R)
    assert np.count_nonzero(S["trk"]) == R
    gpu = system.gpu_engine()
    state = gpu.to_gpu(S)
    for t in range(3):
        state = gpu.step(state, torch.empty_like(state), t)
        actual = gpu.to_np(state)
        assert repair(actual["trk"])[0, 100, system.T["BF0"]] == 1
        np.testing.assert_array_equal(actual["addr"][0], np.arange(Q))
        assert np.all(actual["age"] == t)
