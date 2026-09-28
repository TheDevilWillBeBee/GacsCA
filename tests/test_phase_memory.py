import numpy as np
import pytest
import torch

from experiments.phase_memory import phase_histogram, observe, first_passage_intervals


@pytest.mark.parametrize("device", ["cpu", "cuda"])
def test_phase_observer_distinguishes_correct_shifted_and_erased_states(device):
    address = torch.arange(32, device=device).repeat(4, 1) % 8
    address[1] = (address[1] + 4) % 8
    address[2, 16:] = (address[2, 16:] + 4) % 8
    address[3] = (address[3] + 2) % 8
    hist = phase_histogram(address, 8)
    assert hist.sum(1).tolist() == [32] * 4
    assert observe(hist, [0, 4]).tolist() == [0, 1, -1, -1]
    assert hist.argmax(1).tolist() == [0, 4, 0, 2]


def test_first_observed_passage_censoring():
    flags = [[False, False, False], [True, False, False], [False, False, True]]
    assert first_passage_intervals([0, 10, 20], flags, 20) == [
        dict(observed=True, lower=0, upper=10),
        dict(observed=False, lower=20, upper=None),
        dict(observed=True, lower=10, upper=20)]
    with pytest.raises(ValueError):
        first_passage_intervals([0, 20, 10], flags, 20)
