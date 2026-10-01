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

E0 is computed exactly for any finite E (`level0_points`, with a bucket grid
so that large sets stay fast): a point is a level-0 error when the singleton
or one of the two adjacent pairs containing it is (24, 24)-separated from the
rest of E. A set S that contains level-0 errors is not a candidate level-1
error (Gray takes S inside E minus E0); `classify` then reports level1=False
and classifies S minus E0 separately as 'core'.
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


def _near(Es, buckets, p, limit):
    """Points of Es other than p within 23 of p in both coordinates; stops after `limit`."""
    x, t = p
    found = []
    bx, bt = x // 24, t // 24
    for i in (bx - 1, bx, bx + 1):
        for j in (bt - 1, bt, bt + 1):
            for q in buckets.get((i, j), ()):
                if q != p and abs(q[0] - x) < 24 and abs(q[1] - t) < 24:
                    found.append(q)
                    if len(found) >= limit:
                        return found
    return found


def level0_points(E):
    """E0: the union of the level-0 errors of E (exact for any finite E).

    A candidate level-0 error C (one site, or two adjacent sites at one tick)
    is a level-0 error when C and E minus C are (24, 24)-separated, i.e. no
    other point is within 23 of a point of C in both coordinates."""
    Es = set(map(tuple, E))
    buckets = {}
    for p in Es:
        buckets.setdefault((p[0] // 24, p[1] // 24), []).append(p)
    near = {}

    def nb(p):
        if p not in near:
            near[p] = _near(Es, buckets, p, 3)
        return near[p]
    e0 = set()
    for p in Es:
        n = nb(p)
        if not n:
            e0.add(p)                                   # an isolated single site
            continue
        if len(n) == 1:
            q = n[0]
            if q[1] == p[1] and abs(q[0] - p[0]) == 1 and nb(q) == [p]:
                e0.add(p)                               # an isolated adjacent pair
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
    e0 = level0_points(E)
    if S & e0:
        # Gray's candidate level-1 errors are subsets of E minus E0: S itself is not one
        res = dict(points=len(S), level0=len(S & e0), extent=None, candidate_level1=False, level1=False,
                   witness=None, method='S contains level-0 errors of E')
        if S - e0:
            res['core'] = classify(S - e0, E, Q, U, exact_limit)
        return res
    core = S
    xs = [p[0] for p in core]
    ts = [p[1] for p in core]
    res = dict(points=len(S), level0=0, extent=None, candidate_level1=False, level1=False,
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
    elif (dec := _decide_iii(core)) is not None:
        cond3, res['method'], res['witness'] = dec
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


def _has_linked_pair(core):
    """(ii) for a large set: two distinct points within 23 in both coordinates
    are two disjoint, (24, 24)-linked candidate level-0 errors (as singletons)."""
    Es = set(core)
    buckets = {}
    for p in Es:
        buckets.setdefault((p[0] // 24, p[1] // 24), []).append(p)
    return any(_near(Es, buckets, p, 1) for p in Es)


def _decide_iii(core, max_outside_pairs=20000):
    """Exact decision of (iii) for a large set, with a 104 x 104 window R over its dense part.

    (iii) fails iff two 2-point minimal candidates (two linked single sites each) are
    (104, 104)-separated: separated sets have separated subsets, and every minimal candidate
    contains two linked single sites. A pair with a point in R is linked to every point of R
    (R spans at most 103 in each coordinate), so in any separated configuration one of the two
    pairs lies outside R. Hence (iii) fails iff some linked pair (c, d) outside R is separated
    from some linked pair of the set. Returns (holds, method, witness) or None when no window
    keeps the outside pairs below `max_outside_pairs`."""
    Es = set(core)
    pts = np.array(sorted(Es))
    for x0, t0 in _windows(Es, pts):
        inside = (pts[:, 0] >= x0) & (pts[:, 0] < x0 + 104) & (pts[:, 1] >= t0) & (pts[:, 1] < t0 + 104)
        out = set(map(tuple, pts[~inside].tolist()))
        ob = {}
        for p in out:
            ob.setdefault((p[0] // 24, p[1] // 24), []).append(p)
        pairs = set()
        for p in out:
            pairs.update(tuple(sorted((p, q))) for q in _near(out, ob, p, max_outside_pairs + 1))
            if len(pairs) > max_outside_pairs:
                break
        if len(pairs) > max_outside_pairs:
            continue
        if not pairs:
            return True, 'hub window', None
        for c, d in sorted(pairs):
            far = (((np.abs(pts[:, 0] - c[0]) >= 104) | (np.abs(pts[:, 1] - c[1]) >= 104))
                   & ((np.abs(pts[:, 0] - d[0]) >= 104) | (np.abs(pts[:, 1] - d[1]) >= 104)))
            F = set(map(tuple, pts[far].tolist()))
            fb = {}
            for p in F:
                fb.setdefault((p[0] // 24, p[1] // 24), []).append(p)
            for p in F:
                q = _near(F, fb, p, 1)
                if q:
                    return False, 'witness', [sorted([c, d]), sorted([p, q[0]])]
        return True, 'window and outside pairs', None
    return None


def _windows(Es, pts):
    """Candidate 104 x 104 windows: around the median point, and around the bounding box of the
    points with at least three others within 23 (a dense burst plus a few stragglers)."""
    buckets = {}
    for p in Es:
        buckets.setdefault((p[0] // 24, p[1] // 24), []).append(p)
    out = [(int(np.median(pts[:, 0])) - 52, int(np.median(pts[:, 1])) - 52)]
    dense = np.array([p for p in Es if len(_near(Es, buckets, p, 3)) >= 3]) if len(Es) < 200000 else pts
    if len(dense):
        lo, hi = dense.min(axis=0), dense.max(axis=0)
        if (hi - lo).max() < 104:
            mid = (lo + hi) // 2
            out += [(int(mid[0]) - 52, int(mid[1]) - 52), (int(lo[0]), int(lo[1])),
                    (int(hi[0]) - 103, int(hi[1]) - 103)]
    return list(dict.fromkeys(out))


def _hub_window(core):
    """A 104 x 104 window R such that no two points outside R are (24, 24)-linked, or None.
    Then every minimal candidate (two linked candidate level-0 errors) has a point in R, any
    two minimal candidates are (104, 104)-linked through R, and (iii) holds. Tried: windows
    around the median point and around the bounding box of the points with at least three
    others within 23 (a dense burst plus a few linked stragglers)."""
    Es = set(core)
    pts = np.array(sorted(Es))
    buckets = {}
    for p in Es:
        buckets.setdefault((p[0] // 24, p[1] // 24), []).append(p)
    dense = np.array([p for p in Es if len(_near(Es, buckets, p, 3)) >= 3]) if len(Es) < 200000 else pts
    starts = {(int(np.median(pts[:, 0])) - 52, int(np.median(pts[:, 1])) - 52)}
    if len(dense):
        lo, hi = dense.min(axis=0), dense.max(axis=0)
        if (hi - lo).max() < 104:
            mid = (lo + hi) // 2
            starts.add((int(mid[0]) - 52, int(mid[1]) - 52))
            starts.add((int(lo[0]), int(lo[1])))
            starts.add((int(hi[0]) - 103, int(hi[1]) - 103))
    for x0, t0 in sorted(starts):
        inside = (pts[:, 0] >= x0) & (pts[:, 0] < x0 + 104) & (pts[:, 1] >= t0) & (pts[:, 1] < t0 + 104)
        out = set(map(tuple, pts[~inside].tolist()))
        ob = {}
        for p in out:
            ob.setdefault((p[0] // 24, p[1] // 24), []).append(p)
        if not any(_near(out, ob, p, 1) for p in out):
            return x0, t0
    return None


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


def classify_burst_in_noise(S, E, Q=None, U=None):
    """A burst S inside a larger finite error set E (for instance with dense level-0 noise around
    it): Gray's class of S itself within E, and of S together with the points of E linked to it
    (within 23 in both coordinates, transitively), which Gray's isolation condition (iv) would
    otherwise count against it."""
    S, E = set(map(tuple, S)), set(map(tuple, E))
    rest = E - S
    buckets = {}
    for p in rest:
        buckets.setdefault((p[0] // 24, p[1] // 24), []).append(p)
    linked, frontier = set(), set(S)
    while frontier:
        new = set()
        for f in frontier:
            bx, bt = f[0] // 24, f[1] // 24
            for i in (bx - 1, bx, bx + 1):
                for j in (bt - 1, bt, bt + 1):
                    for q in buckets.get((i, j), ()):
                        if q not in linked and abs(q[0] - f[0]) < 24 and abs(q[1] - f[1]) < 24:
                            new.add(q)
        linked |= new
        frontier = new
    return dict(alone=classify(S, E, Q, U), with_linked=classify(S | linked, E, Q, U),
                linked_points=len(linked), other_points=len(rest - linked))


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
