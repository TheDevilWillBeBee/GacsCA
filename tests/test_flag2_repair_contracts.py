"""Restricted recovery contracts for D8 candidate B, not a robustness theorem.

Whole local-field faults include Workspace flag inputs at the two faulty sites.
Persistent external Workspace forcing is a separate, explicitly pulsed test.
"""
import numpy as np
import torch

from gacsca import level0_np, level0_spec
from gacsca.gpu import Level0GPU, to_gpu, to_np, field
from gacsca.params import Params, Variant


def test_candidate_b_repairs_two_adjacent_arbitrary_local_faults_in_one_step():
    p = Params(Q=8192, ncol=2)
    v = Variant(flag2_healthy_erase="at_most_one")
    # Exhaust the eight flag-input bits at the two faulty sites. Address/Age
    # values are seeded samples, NOT an exhaustive test of their alphabets.
    B = 256
    S = level0_np.initial(p, B)
    phases = np.array([0, 3 * p.U // 4 - 1, p.U - 1])[np.arange(B) % 3]
    S["age"][:] = phases[:, None]
    sites = np.array([0, 1, 4, 31, p.Q - 2, p.Q - 1, p.Q, p.L - 1])[np.arange(B) % 8]
    rng = np.random.default_rng(20921)
    for offset in (0, 1):
        x = (sites + offset) % p.L
        S["addr"][np.arange(B), x] = rng.integers(0, p.Q, B)
        S["age"][np.arange(B), x] = rng.integers(0, p.U, B)
        for bit, name in enumerate(("f1", "f2", "wf1", "wf2")):
            S[name][np.arange(B), x] = (np.arange(B) >> (4 * offset + bit)) & 1
    g = Level0GPU(p, v)
    state = to_gpu(S)
    out = to_np(g.step(state, torch.empty_like(state), 1))
    np.testing.assert_array_equal(out["addr"], np.broadcast_to(np.arange(p.L) % p.Q, (B, p.L)))
    np.testing.assert_array_equal(out["age"], np.broadcast_to((phases[:, None] + 1) % p.U, (B, p.L)))
    assert not out["f1"].any() and not out["f2"].any()
    # Independent scalar checks around representative interior and wrap cases.
    for b in (0, 31, 63, 127, 191, 255):
        cfg = level0_spec.Cfg(*(S[k][b] for k in ("addr", "age", "f1", "f2", "wf1", "wf2")))
        for dx in range(-5, 7):
            x = (sites[b] + dx) % p.L
            result = level0_spec.step_cell(cfg, x, p.Q, p.U, v)[:4]
            assert result == (x % p.Q, (phases[b] + 1) % p.U, 0, 0)


def test_candidate_b_healthy_flag_wave_has_two_cell_fronts_and_cannot_cross_boundary():
    p = Params(Q=8192, ncol=2)
    v = Variant(flag2_healthy_erase="at_most_one")
    S = level0_np.initial(p, 1)
    left, right = 64, 264
    S["f2"][:, left:right] = 1
    g = Level0GPU(p, v)
    state = to_gpu(S)
    out = torch.empty_like(state)
    for t in range(1, (p.Q - left) // 2 + 2):
        g.step(state, out, t)
        state, out = out, state
        if t <= 4 or t % 128 == 0 or t >= (p.Q - left) // 2:
            expected = np.zeros((1, p.L), dtype=bool)
            expected[:, min(left + 2 * t, p.Q):min(right + 2 * t, p.Q)] = True
            np.testing.assert_array_equal(field(state, "f2").cpu().numpy(), expected)
            assert not field(state, "f1").any()
    assert not field(state, "f2").any()


def test_candidate_b_preserves_workspace_flag2_forcing_at_boundary():
    p = Params(Q=8192, ncol=2)
    v = Variant(flag2_healthy_erase="at_most_one")
    S = level0_np.initial(p, 1)
    S["age"][:] = 3 * p.U // 4
    # Explicit external pulse. This tests the local rule's Workspace input,
    # not the hierarchy's generation or correction of that input.
    S["wf2"][:, p.Q - 6:p.Q - 3] = 1
    g = Level0GPU(p, v)
    state = to_gpu(S)
    out = torch.empty_like(state)
    expected = level0_np.step(S, p, v)
    g.step(state, out, 1)
    actual = to_np(out)
    for name in S:
        np.testing.assert_array_equal(actual[name], expected[name])
    assert actual["f2"][0, p.Q - 4] == 1
    assert not actual["f2"][0, p.Q:].any()
    actual["wf2"][:] = 0
    state = to_gpu(actual)
    for t in range(2, 18):
        g.step(state, out, t)
        state, out = out, state
        assert not field(state, "f2")[0, p.Q:].any()
    assert not field(state, "f2").any()
