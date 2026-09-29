import numpy as np
import pytest
import torch

from experiments.phase_size import window_histogram, summarize
from experiments.phase_memory import phase_histogram, observe


@pytest.mark.parametrize("device", ["cpu", "cuda"])
def test_window_uses_absolute_coordinates_and_same_phase(device):
    address = (torch.arange(32, device=device).repeat(2, 1) + 4) % 8
    full = phase_histogram(address, 8)
    for start in (0, 3, 9, 24):
        local = window_histogram(address, 8, start, 8)
        assert local[:, 4].tolist() == [8, 8]
        assert observe(local, [0, 4]).tolist() == observe(full, [0, 4]).tolist()
    with pytest.raises(ValueError):
        window_histogram(address, 8, 25, 8)


def test_global_average_can_hide_a_fixed_window_failure():
    address = torch.arange(32)[None, :] % 8
    address[:, :8] = (address[:, :8] + 4) % 8
    assert observe(window_histogram(address, 8, 0, 32), [0, 4]).item() == 0
    assert observe(window_histogram(address, 8, 0, 8), [0, 4]).item() == 1


def test_recovery_is_not_irreversible_loss_and_strata_are_separate():
    out = summarize([0, 10, 20], [[0, 1], [-1, 0], [0, -1]], [0, 1], 20)
    assert out["recovered_by_horizon"] == 1
    assert out["rings_with_observed_erasure"] == 2
    assert out["rings_with_observed_wrong_bit"] == 1
    assert out["strata"][0]["ever_wrong_bit"] == 0
    assert out["strata"][1]["ever_wrong_bit"] == 1
    assert out["first_observed_noncorrect"] == [dict(observed=True, lower=0, upper=10)] * 2


def test_identical_observers_have_identical_summary():
    observations = np.array([[0, 1], [0, -1], [0, 1]])
    assert summarize([0, 10, 20], observations, [0, 1], 20) == summarize(
        [0, 10, 20], observations.copy(), [0, 1], 20)
