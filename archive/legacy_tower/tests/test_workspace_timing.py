"""A source-level ambiguity: neighbouring post-wipe SimBit is not range five."""
import numpy as np
import pytest

from gacsca.params import Params
from gacsca.microcode import Tracks, Layout, Program
from gacsca.engine_np import Engine, redistribute


@pytest.mark.parametrize("Q", [32, 8192])
def test_post_wipe_computed_simbit_would_break_range_five(Q):
    """A change at x-7 toggles computed primary Info[x-2], hence a literal WF.

    The implemented current-repaired-Info rule is identical at x. The large
    case uses Gray's Q lower bound, U=128Q and fivefold storage redundancy;
    this is not an artefact of the miniature hierarchy's parameter choices.
    """
    p = Params(Q=Q, ncol=2)
    T = Tracks(R=5)
    L = Layout(Q, p.U, T, Qs=16, Us=16, Qss=2, Uss=2, with_tracks=False)
    engine = Engine(p, T, L, Program(D=1))
    engine.trickle = (3 * p.U // 4, 3 * p.U // 4 + 2 * Q)
    S = engine.initial(1)
    S["age"][:] = engine.trickle[0] - 1
    V = np.zeros((1, p.L, T.NT), np.uint8)
    V[:, :, T["INFO"]] = 1
    S["trk"] = redistribute(V, 5)
    x, y = Q - 1, Q - 3
    S["addr"][0, x - 7:x - 4] = (S["addr"][0, x - 7:x - 4] + 7) % Q
    S["f1"][0, y:x + 1] = 1
    other = {k: v.copy() for k, v in S.items()}
    other["addr"][0, x - 7] = x - 7
    neighborhood = np.arange(x - 5, x + 6) % p.L
    for k in S:
        np.testing.assert_array_equal(S[k][:, neighborhood], other[k][:, neighborhood])
    a, b = engine.step(S), engine.step(other)
    for k in a:
        np.testing.assert_array_equal(a[k][:, x], b[k][:, x], err_msg=k)
    assert a["addr"][0, x] == b["addr"][0, x] == x
    assert a["wf1"][0, x] == b["wf1"][0, x] == 1
    assert a["trk"][0, y, T["INFO"], 2] == 0
    assert b["trk"][0, y, T["INFO"], 2] == 1
