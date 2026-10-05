"""Gray's error classes (reader's guide section 5.1) with the constants as parameters.

lam = link / isolation distance (Gray: 24), c = separation in condition (iii) (Gray: 104).
Only the level-0 / level-1 classes of a finite error set E are implemented, as in
gacsca/gray_errors.py, but by brute force (exact, small sets only).

Checks done by main():
  1. agreement with the repository's gacsca/gray_errors.py at (24, 104) on random sets;
  2. the maximal extent of a level-1 error, by exhaustive search on a line and by
     random search in the plane, against the formula  c + 2*lam - 2;
  3. the same for Gray's constants (24, 104): a certified level-1 error of extent 150.
"""
import itertools
import json
import sys
import numpy as np


def linked_pts(a, b, m, n):
    return abs(a[0] - b[0]) < m and abs(a[1] - b[1]) < n


def level0_points(E, lam):
    """E0: union of the level-0 errors of E (a candidate level-0 error is one site or two
    adjacent sites at one tick; it is a level-0 error when it is (lam, lam)-separated from
    the rest of E)."""
    E = set(E)
    e0 = set()
    for p in E:
        near = [q for q in E if q != p and linked_pts(p, q, lam, lam)]
        if not near:
            e0.add(p)
            continue
        for q in near:
            if q[1] == p[1] and abs(q[0] - p[0]) == 1:
                pair = {p, q}
                if not any(linked_pts(a, r, lam, lam) for a in pair for r in E - pair):
                    e0.add(p)
    return e0


def linked_pairs(S, lam):
    S = sorted(S)
    return [(a, b) for a, b in itertools.combinations(S, 2) if linked_pts(a, b, lam, lam)]


def is_level1(S, lam, c, E=None, Q=None, U=None):
    """S is one level-1 error of E (default E = S): S inside E minus E0, (i) fits Q x U,
    (ii) has two linked points, (iii) no two linked pairs are (c, c)-separated,
    (iv) S is (lam*Q, lam*U)-separated from the other errors that are not level-0."""
    S = set(S)
    E = set(E) if E is not None else set(S)
    e0 = level0_points(E, lam)
    if S & e0 or not S:
        return False
    xs = [p[0] for p in S]
    ts = [p[1] for p in S]
    if Q is not None and (max(xs) - min(xs) + 1 > Q or max(ts) - min(ts) + 1 > U):
        return False
    pairs = linked_pairs(S, lam)
    if not pairs:
        return False
    for P1, P2 in itertools.combinations(pairs, 2):
        if not any(linked_pts(a, b, c, c) for a in P1 for b in P2):
            return False
    rest = E - S - e0
    if rest:
        if Q is None:
            return False
        if any(linked_pts(a, b, lam * Q, lam * U) for a in S for b in rest):
            return False
    return True


def extent(S):
    xs = [p[0] for p in S]
    ts = [p[1] for p in S]
    return max(xs) - min(xs) + 1, max(ts) - min(ts) + 1


def max_extent_line(lam, c, span):
    """Exhaustive: all subsets of sites {0..span-1} at one tick that contain site 0;
    the largest extent of a subset that is one level-1 error."""
    best, arg = 0, None
    for mask in range(1, 1 << (span - 1)):
        S = [(0, 0)] + [(i + 1, 0) for i in range(span - 1) if mask >> i & 1]
        if len(S) > 7:
            continue
        w = S[-1][0] + 1
        if w <= best:
            continue
        if is_level1(S, lam, c):
            best, arg = w, S
    return best, arg


def extremal(lam, c):
    """Two linked pairs as far apart as (iii) allows: extent c + 2*lam - 2 in both coordinates."""
    a = lam - 1
    return [(0, 0), (a, a), (a + c - 1, a + c - 1), (2 * a + c - 1, 2 * a + c - 1)]


def main():
    out = {}
    rng = np.random.default_rng(0)
    # 1. agreement with the repository classifier at Gray's constants
    sys.path.insert(0, __import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), 'repo'))   # private copy, identical gray_errors.py
    from gacsca import gray_errors
    agree = 0
    for _ in range(400):
        n = int(rng.integers(2, 9))
        w = int(rng.integers(20, 260))
        S = {(int(rng.integers(0, w)), int(rng.integers(0, w))) for _ in range(n)}
        mine = is_level1(S, 24, 104)
        theirs = gray_errors.classify(S)['level1']
        assert mine == theirs, (sorted(S), mine, theirs)
        agree += 1
    out['agreement_with_gray_errors_py'] = agree
    # 2. exhaustive on a line for small constants
    rows = []
    for lam, c in [(2, 2), (2, 3), (2, 5), (3, 3), (3, 4), (3, 6), (3, 8), (4, 4), (4, 6), (4, 9), (5, 5), (5, 7)]:
        span = c + 2 * lam + 2
        if span > 22:
            continue
        best, arg = max_extent_line(lam, c, span)
        rows.append(dict(lam=lam, c=c, max_extent=best, formula=c + 2 * lam - 2, witness=[p[0] for p in arg]))
        assert best == c + 2 * lam - 2, rows[-1]
    out['exhaustive_line'] = rows
    # 3. the extremal set at the constants discussed in the report, and one site more fails
    cert = []
    for lam, c in [(24, 104), (24, 26), (24, 24), (18, 20), (17, 17), (12, 14)]:
        S = extremal(lam, c)
        ok = is_level1(S, lam, c)
        S2 = S[:3] + [(S[3][0] + 1, S[3][1])]
        S3 = S[:2] + [(S[2][0] + 1, S[2][1]), (S[3][0] + 1, S[3][1])]
        cert.append(dict(lam=lam, c=c, extent=extent(S), level1=ok,
                         one_wider_is_level1=[is_level1(S2, lam, c), is_level1(S3, lam, c)]))
        assert ok and extent(S)[0] == c + 2 * lam - 2
    out['extremal_sets'] = cert
    out['gray_104_repo_classifier_on_150'] = gray_errors.classify(extremal(24, 104))['level1']
    # random search in the plane: no level-1 error wider than the formula (lam, c small)
    worst = {}
    for lam, c in [(3, 4), (4, 6), (5, 9), (6, 6)]:
        best = 0
        for _ in range(60000):
            n = int(rng.integers(2, 7))
            w = c + 2 * lam + 3
            S = {(int(rng.integers(0, w)), int(rng.integers(0, w))) for _ in range(n)}
            if is_level1(S, lam, c):
                best = max(best, *extent(S))
        worst[f'{lam},{c}'] = dict(max_extent_found=best, formula=c + 2 * lam - 2)
        assert best <= c + 2 * lam - 2
    out['random_plane'] = worst
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
