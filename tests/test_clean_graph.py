"""Graph acceleration must preserve every state word and never capture noise."""
import numpy as np
import pytest
import torch

from gacsca.build import make_tower
from gacsca.gpu_engine import CleanGraphRunner


@pytest.mark.parametrize("R", [3, 5])
def test_clean_graph_chunks_tails_and_full_period(R):
    kw = dict(R=5, D=1, Q0=512, U0=32768, U1=8192) if R == 5 else {}
    lower, _ = make_tower(ncol0=2, **kw)
    gpu = lower.gpu_engine()
    S = lower.np_engine().initial(2)
    rng = np.random.default_rng(334)
    S["trk"][:] = rng.integers(0, 2, S["trk"].shape, dtype=np.uint8)
    S["age"][1] = lower.p.U - 5
    S["age"][:, 91] = 13
    S["addr"][:, 11] = 17
    S["simage"][:] = 37
    S["simaddr"][:] = 19
    initial = gpu.to_gpu(S)
    original = initial.clone()
    runner = CleanGraphRunner(gpu, initial, block_steps=64)
    expected = initial.clone()
    pointer = runner.state.data_ptr()
    for steps in (0, 1, 63, 64, 65, 257, lower.p.U):
        expected = gpu.run(expected, steps, 0)
        actual = runner.run(steps)
        assert actual.data_ptr() == pointer
        assert torch.equal(actual, expected), (R, steps)
        assert torch.equal(initial, original)
    # Reloading a checkpoint into the same storage also preserves graph validity.
    runner.state.copy_(initial)
    assert torch.equal(runner.run(65), gpu.run(initial.clone(), 65, 0))
    assert runner.steps == sum((0, 1, 63, 64, 65, 257, lower.p.U, 65))
    with pytest.raises(ValueError, match="nonnegative"):
        runner.run(-1)
    with pytest.raises(ValueError, match="construction CUDA stream"):
        with torch.cuda.stream(torch.cuda.Stream()):
            runner.run(1)
    with pytest.raises(TypeError):
        runner.run(1, eps=0.01)


@pytest.mark.parametrize("block", [0, -2, 1, 63])
def test_clean_graph_rejects_bad_block(block):
    with pytest.raises(ValueError, match="positive even"):
        CleanGraphRunner(None, torch.zeros(1), block_steps=block)
