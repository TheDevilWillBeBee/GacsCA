"""Fault boxes act after a transition, on precisely the specified cells/times."""
import numpy as np
import pytest
import torch

from experiments.gray_faults import FaultBox, advance
from gacsca.build import make_system
from gacsca.gpu_engine import CleanGraphRunner


def test_spatial_faults_match_explicit_post_transition_replacement():
    system = make_system(Q=256, U=16384, ncol=2)
    gpu = system.gpu_engine(seed=912)
    original = gpu.to_gpu(system.np_engine().initial(3))
    runner = CleanGraphRunner(gpu, original, block_steps=4)
    boxes = [FaultBox(1, 2, 5, 0, 7), FaultBox(2, 4, 7, 509, 512)]
    scratch = torch.empty_like(original)
    advance(runner, 0, 9, boxes, scratch)
    expected = original.clone()
    for t in range(9):
        clean = gpu.step(expected, torch.empty_like(expected), t + 1)
        noisy = gpu.step(expected, torch.empty_like(expected), t + 1, eps=1.0)
        for box in boxes:
            if box.start <= t < box.stop:
                clean[box.batch, box.left:box.right].copy_(noisy[box.batch, box.left:box.right])
        expected = clean
    np.testing.assert_array_equal(runner.state.cpu().numpy(), expected.cpu().numpy())
    # A clean ring is bit-identical to uninterrupted graph replay.
    control = CleanGraphRunner(gpu, original, block_steps=4)
    control.run(9)
    np.testing.assert_array_equal(runner.state[0].cpu().numpy(), control.state[0].cpu().numpy())
    split = CleanGraphRunner(gpu, original, block_steps=4)
    advance(split, 0, 4, boxes, scratch)
    advance(split, 4, 9, boxes, scratch)
    np.testing.assert_array_equal(split.state.cpu().numpy(), expected.cpu().numpy())


def test_invalid_fault_boxes_and_aliasing_rejected():
    for box in [FaultBox(-1, 0, 1, 0, 1), FaultBox(0, 1, 1, 0, 1),
                FaultBox(0, 0, 1, -1, 1), FaultBox(0, 0, 1, 0, 17)]:
        with pytest.raises(ValueError, match="fault box"):
            box.validate(1, 16)
    system = make_system(Q=256, U=16384, ncol=1)
    gpu = system.gpu_engine()
    runner = CleanGraphRunner(gpu, gpu.to_gpu(system.np_engine().initial(1)))
    with pytest.raises(ValueError, match="distinct"):
        advance(runner, 0, 1, [], runner.state)
