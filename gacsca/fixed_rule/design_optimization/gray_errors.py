"""Gray's error classes (reader's guide section 5.1) for finite error sets.

Error sets are collections of space-time points (x, t). Definitions, for the
first two levels (Q^0 = U^0 = 1):

  * A and B are (m, n)-linked if some box [x, x+m) x [y, y+n) contains a
    member of each, i.e. some a in A, b in B have |dx| < m and |dt| < n;
    otherwise they are (m, n)-separated.
  * candidate level-0 error: a nonempty subset of E inside [x, x+1] x [t, t]
    (one site, or two adjacent sites at the same tick);
    level-0 error: a candidate S with S and E \\ S (24, 24)-separated.
  * candidate level-1 error: S in E \\ E0 with (i) S inside a Q x U box and
    (ii) two disjoint candidate level-0 errors in S that are (24, 24)-linked;
    level-1 error: (iii) S contains no two (104, 104)-separated candidate
    level-1 errors, and (iv) S and E \\ (S u E0) are (24Q, 24U)-separated.

Condition (iii) only needs minimal candidates (two linked candidate level-0
errors, 2-4 points): separated sets have separated subsets. A dense box of
side <= 104 therefore satisfies (iii) (no two of its points are 104 apart in
a coordinate), while a dense 200 x 200 box contains two linked pairs 150
sites apart and fails it: such a box is a union of level-1 errors, not one.
"""
from itertools import combinations
import numpy as np


def linked(A, B, m, n):
    return any(abs(a[0] - b[0]) < m and abs(a[1] - b[1]) < n for a in A for b in B)


def candidate_level0(E):
    """All candidate level-0 errors of the point set E (as frozensets)."""
    Es = set(E)
    out = [frozenset([p]) for p in Es]
    for (x, t) in Es:
        if (x + 1, t) in Es:
            out.append(frozenset([(x, t), (x + 1, t)]))
    return out


def level0_points(E):
    """E0: the union of the level-0 errors of E."""
    Es = set(E)
    pts = np.array(sorted(Es)) if Es else np.zeros((0, 2), int)
    e0 = set()
    for S in candidate_level0(Es):
        rest = Es - S
        iso = True
        for (x, t) in S:
            if rest and np.any((np.abs(pts[:, 0] - x) < 24) & (np.abs(pts[:, 1] - t) < 24)
                               & ~np.array([tuple(q) in S for q in pts])):
                iso = False
                break
        if iso:
            e0 |= S
    return e0


def minimal_candidates_level1(S):
    """Unions of two disjoint (24, 24)-linked candidate level-0 errors in S."""
    c0 = candidate_level0(S)
    out = []
    for A, B in combinations(c0, 2):
        if A & B:
            continue
        if linked(A, B, 24, 24):
            out.append(A | B)
    return out


def classify(S, E=None, Q=None, U=None, exact_limit=300):
    """Classify the error set S (within the full error set E, default S).

    Returns a dict: level0 (points of S that are level-0 errors),
    candidate_level1 (conditions i-ii on S minus E0), level1 (i-iv),
    and, when (iii) fails, a witness pair of separated minimal candidates.
    Dense sets beyond `exact_limit` points are decided by the window
    argument (extent <= 103 in both coordinates: (iii) holds) or by an
    explicit separated witness; otherwise 'undecided'."""
    S = set(map(tuple, S))
    E = set(map(tuple, E)) if E is not None else set(S)
    assert S <= E
    e0 = level0_points(E) if len(E) <= 4 * exact_limit else _level0_dense(E)
    core = S - e0
    xs = [p[0] for p in core]
    ts = [p[1] for p in core]
    res = dict(points=len(S), level0=len(S & e0), extent=None, candidate_level1=False, level1=False,
               witness=None, method=None)
    if not core:
        return res
    ext = (max(xs) - min(xs) + 1, max(ts) - min(ts) + 1)
    res['extent'] = ext
    in_box = (Q is None or ext[0] <= Q) and (U is None or ext[1] <= U)
    # (ii): two disjoint linked candidate level-0 errors
    if len(core) <= exact_limit:
        mins = minimal_candidates_level1(core)
        cond2 = bool(mins)
    else:
        mins = None
        cond2 = _has_linked_pair(core)
    res['candidate_level1'] = bool(in_box and cond2)
    if not res['candidate_level1']:
        return res
    # (iii)
    if ext[0] <= 104 and ext[1] <= 104:
        cond3, res['method'] = True, 'window'
    elif mins is not None:
        cond3, res['method'] = True, 'exact'
        arr = [np.array(sorted(M)) for M in mins]
        for i in range(len(arr)):
            for j in range(i + 1, len(arr)):
                a, b = arr[i], arr[j]
                dx = np.abs(a[:, None, 0] - b[None, :, 0])
                dt = np.abs(a[:, None, 1] - b[None, :, 1])
                if not np.any((dx < 104) & (dt < 104)):
                    cond3 = False
                    res['witness'] = [sorted(mins[i]), sorted(mins[j])]
                    break
            if not cond3:
                break
    else:
        w = _separated_witness(core)
        if w is not None:
            cond3, res['method'], res['witness'] = False, 'witness', w
        else:
            res['method'] = 'undecided'
            return res
    # (iv): isolation from the remaining errors
    rest = E - core - e0
    cond4 = True
    if rest and Q is not None:
        cond4 = not linked(core, rest, 24 * Q, 24 * U)
    elif rest:
        cond4 = False
    res['level1'] = bool(cond3 and cond4)
    return res


def _level0_dense(E):
    """Level-0 points of a large set: a point with another point within 23
    in both coordinates (other than its own adjacent partner) is not level-0.
    Exact for sets whose candidate level-0 errors are isolated singletons or
    pairs; used for dense boxes, where no point is level-0."""
    arr = np.array(sorted(E))
    e0 = set()
    for i, (x, t) in enumerate(arr):
        near = (np.abs(arr[:, 0] - x) < 24) & (np.abs(arr[:, 1] - t) < 24)
        if near.sum() == 1:
            e0.add((int(x), int(t)))
    return e0


def _has_linked_pair(core):
    arr = np.array(sorted(core))
    for i in range(min(len(arr), 2000)):
        x, t = arr[i]
        far = (np.abs(arr[:, 0] - x) >= 2) | (arr[:, 1] != t)
        near = (np.abs(arr[:, 0] - x) < 24) & (np.abs(arr[:, 1] - t) < 24) & far
        if near.any():
            return True
    return False


def _separated_witness(core):
    """Two separated minimal candidates near the extremes of a large set."""
    S = set(core)
    arr = np.array(sorted(S))
    for axis in (0, 1):
        order = np.argsort(arr[:, axis])
        lo_pts, hi_pts = arr[order[:50]], arr[order[-50:]]
        lo = _minimal_around(S, lo_pts)
        hi = _minimal_around(S, hi_pts)
        if lo and hi and not linked(lo, hi, 104, 104):
            return [sorted(lo), sorted(hi)]
    return None


def _minimal_around(S, pts):
    for p in map(tuple, pts):
        for q in S:
            if q != p and abs(q[0] - p[0]) < 24 and abs(q[1] - p[1]) < 24 and \
                    not (abs(q[0] - p[0]) <= 1 and q[1] == p[1]):
                return {p, q}
    return None


def dense_box(x0, t0, w, h):
    return [(x, t) for x in range(x0, x0 + w) for t in range(t0, t0 + h)]


def random_level1_cluster(rng, x0, t0, pairs=4, window=104, adjacent=0.5):
    """A sparse error set built to be one level-1 error: `pairs` linked pairs
    of candidate level-0 errors (single sites or two adjacent sites at one
    tick); pair anchors in a window x window box, partners within 23 in
    space and time. Returns (points, boxes) with boxes as (x, w, t, h)."""
    pts, boxes = [], []
    for _ in range(pairs):
        ax, at = x0 + int(rng.integers(0, window)), t0 + int(rng.integers(0, window))
        bx, bt = ax + int(rng.integers(-23, 24)), at + int(rng.integers(0, 24))
        if bt == at and abs(bx - ax) <= 2:
            bx = ax + 3
        for (x, t) in ((ax, at), (bx, bt)):
            w = 2 if rng.random() < adjacent else 1
            boxes.append((x, w, t, 1))
            pts += [(x + d, t) for d in range(w)]
    return pts, boxes
