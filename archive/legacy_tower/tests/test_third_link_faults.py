"""Fault placement, diagnostic distinctions and full-state local injection."""
import numpy as np
import pytest
import torch

from experiments.third_link_checkpoint import build
from experiments.third_link_faults import scenarios, decoded_metrics
from experiments.gray_faults import FaultBox, advance
from gacsca.engine_np import redistribute
from gacsca.gpu_engine import CleanGraphRunner


def test_third_link_island_geometry_and_independent_trial_indices():
    outer, _, _ = build(3, 1)
    base = 384 * outer.p.U
    labels, boxes = scenarios(outer, base, [1, 21, 101, 256], 3)
    assert len(labels) == 25 and len(boxes) == 24
    assert [b.batch for b in boxes] == list(range(1, 25))
    for box in boxes:
        box.validate(len(labels), outer.p.L)
        label = labels[box.batch]
        assert box.right - box.left == label["width"]
        assert box.stop - box.start == 1
        assert box.left // outer.p.Q == (box.right - 1) // outer.p.Q
        assert box.start - base == (16 if label["phase"] == "early" else outer.p.U - 2)
    with pytest.raises(ValueError): scenarios(outer, base, [257], 1)
    with pytest.raises(ValueError): scenarios(outer, base, [1], 0)


def test_third_link_metrics_distinguish_raw_copies_structure_and_info():
    _, middle, _ = build(3, 1)
    T, R, L = middle.T, middle.T.R, 16
    reference = dict(addr=np.zeros((1, L), np.int32),
                     trk=np.zeros((1, L, T.NT, R), np.uint8))
    decoded = {k:np.repeat(v, 3, axis=0) for k,v in reference.items()}
    decoded["trk"][1, 7, T["INFO"], 1] = 1  # one raw copy; majority remains zero
    V = np.zeros((1, L, T.NT), np.uint8)
    V[0, 7, T["INFO"]] = 1
    decoded["trk"][2] = redistribute(V, R)[0]
    decoded["addr"][2, 7] = 1
    result = decoded_metrics(decoded, reference, T)
    assert result["fields"]["trk"] == [0, 1, 3]
    assert result["middle_info_bits"] == [0, 0, 1]
    assert result["structural_cells"] == [0, 0, 1]
    assert result["any_state_cells"] == [0, 1, 3]


@pytest.mark.parametrize("R", [3, 5])
def test_spatial_fault_injector_includes_second_control_pair_and_absolute_time(R):
    outer, _, _ = build(R, 1)
    gpu = outer.gpu_engine(seed=1370, noise_version=2)
    state = gpu.to_gpu(outer.np_engine().initial(2))
    time = 2 ** 40
    expected = gpu.step(state, torch.empty_like(state), time + 1, eps=0.0)
    noisy = gpu.step(state, torch.empty_like(state), time + 1, eps=1.0)
    expected[1, 100:121] = noisy[1, 100:121]
    runner = CleanGraphRunner(gpu, state, block_steps=2)
    advance(runner, time, time + 1, [FaultBox(1, time, time + 1, 100, 121)], torch.empty_like(state))
    assert torch.equal(runner.state, expected)
    assert bool((runner.state[1, 100:121, gpu.nested_base] != 0).any())
    later = gpu.step(state, torch.empty_like(state), time + 2, eps=1.0)
    assert not torch.equal(noisy[1, 100:121], later[1, 100:121])
