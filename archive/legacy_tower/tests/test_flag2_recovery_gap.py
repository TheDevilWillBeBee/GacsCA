"""Printed Gray p.21 Flag2(a) contradicts isolated-flag recovery prose.

These are fidelity-gap witnesses, NOT tests that certify error correction.
Alternative healthy-colony erasers below are hypothesis models only and do
not alter the production Gray/Masumori rule.
"""
import numpy as np
import pytest
import torch

from gacsca import level0_np, level0_spec
from gacsca.gpu import Level0GPU, to_gpu, to_np
from gacsca.params import Params


@pytest.mark.parametrize("width", [1, 2, 3])
def test_small_flag2_island_is_stationary_in_printed_rule(width):
    p = Params(Q=8192, ncol=1)
    state = level0_np.initial(p, 3)
    # No inconsistency or Workspace flags, at different phases including the
    # trickle interval. An isolated Flag2 never creates an Address/Age error.
    state["age"][:] = np.array([0, 3 * p.U // 4, p.U - 1])[:, None]
    x = 31
    state["f2"][:, x:x + width] = 1
    out = level0_np.step(state, p)
    gpu = Level0GPU(p)
    packed = to_gpu(state)
    actual = to_np(gpu.step(packed, torch.empty_like(packed), 1))
    for name in state:
        np.testing.assert_array_equal(actual[name], out[name], err_msg=name)
    np.testing.assert_array_equal(out["f2"], state["f2"])
    np.testing.assert_array_equal(out["addr"], state["addr"])
    np.testing.assert_array_equal(out["age"], (state["age"] + 1) % p.U)
    assert not out["f1"].any()
    # Independent scalar checks at every site that could change Flag2.
    for batch in range(3):
        cfg = level0_spec.Cfg(*(state[k][batch] for k in ("addr", "age", "f1", "f2", "wf1", "wf2")))
        for site in range(x - 5, x + width + 6):
            a, age, f1, f2, _ = level0_spec.step_cell(cfg, site, p.Q, p.U)
            assert (a, age, f1, f2) == tuple(out[k][batch, site] for k in ("addr", "age", "f1", "f2"))
    # Together with uniform-age independence, this one-step invariant proves
    # indefinite persistence in the healthy, zero-Workspace-flag subspace.


def healthy_flag2_step(bits, candidate):
    """Restricted hypothesis model: perfect one-colony structure, F1=WF2=0."""
    Q = len(bits)
    left = np.arange(Q)[:, None] - np.arange(1, 6)
    inside = left >= 0
    count = (bits[left % Q] * inside).sum(1)
    if candidate == "printed":
        erase = count == inside.sum(1)  # no left-colony zero
    elif candidate == "no_ones":
        erase = count == 0
    elif candidate == "at_most_one":
        erase = count <= 1
    else:
        raise ValueError(candidate)
    return np.where(bits, ~erase, count >= 4).astype(np.uint8)


def test_half_density_flag2_pattern_is_a_printed_rule_fixed_point():
    p = Params(Q=8192, ncol=1)
    state = level0_np.initial(p, 1)
    state["f2"][:, 1::2] = 1
    out = level0_np.step(state, p)
    np.testing.assert_array_equal(out["f2"], state["f2"])
    np.testing.assert_array_equal(out["addr"], state["addr"])
    assert out["f2"].sum() == 4096 and not out["f1"].any()


@pytest.mark.parametrize("width", [1, 2, 3, 5, 20])
def test_candidate_erasers_distinguish_island_recovery(width):
    initial = np.zeros(128, np.uint8)
    initial[16:16 + width] = 1
    for candidate in ("printed", "no_ones", "at_most_one"):
        bits = initial.copy()
        for _ in range(256):
            bits = healthy_flag2_step(bits, candidate)
        if candidate == "printed":
            # The leftmost 1 has a nonempty all-zero left neighborhood and
            # cannot clear, regardless of rightward offspring.
            assert bits[16] == 1
        else:
            assert not bits.any()
    if width == 2:
        # Changing only the printed zero to one clears a pair sequentially;
        # <=1 clears both immediately, matching two-site isolated repair.
        assert healthy_flag2_step(initial, "no_ones").sum() == 1
        assert healthy_flag2_step(initial, "at_most_one").sum() == 0
