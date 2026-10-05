r"""Brute-force check of the facts of Gray's section 5.1 with the constants as parameters.

lam: the link / isolation distance (Gray: 24).  c: the separation in condition (iii) (Gray: 104).
For random finite error sets E (a few clusters, so that every case occurs) the script computes
E0 and E1 exactly from the definitions and checks, for levels 1 and 2:

  F1  every point of E \ E0 lies in a candidate level-1 error, and every point of E \ E1 lies in
      a candidate level-2 error (the lemma whose proof uses c = 4(lam+2) in Gray's text);
  F2  a level-1 error is at most c + 2 lam - 2 wide and long; a level-2 error (when E \ E1 is
      one) at most (c + 2 lam + 4) Q wide and (c + 2 lam + 4) U long;

Usage: lemma_bruteforce.py [trials]     (pure Python, a few minutes)
"""
import itertools
import random
import sys


def linked(A, B, m, n):
    return any(abs(a[0] - b[0]) < m and abs(a[1] - b[1]) < n for a in A for b in B)


def fits(S, m, n):
    xs, ts = [p[0] for p in S], [p[1] for p in S]
    return max(xs) - min(xs) < m and max(ts) - min(ts) < n


def cand0(E):
    Es = set(E)
    out = [frozenset([p]) for p in E]
    out += [frozenset([p, (p[0] + 1, p[1])]) for p in E if (p[0] + 1, p[1]) in Es]
    return out


def level0(E, lam):
    Es = set(E)
    e0 = set()
    for S in cand0(E):
        if not linked(S, Es - S, lam, lam):
            e0 |= S
    return e0


def minimal1(F, lam):
    """Minimal candidate level-1 errors inside the point set F: two disjoint candidate level-0
    errors that are (lam, lam)-linked."""
    c0 = cand0(F)
    out = set()
    for A, B in itertools.combinations(c0, 2):
        if not (A & B) and linked(A, B, lam, lam):
            out.add(A | B)
    return list(out)


def components(F, m, n):
    F = list(F)
    comp, seen = [], set()
    for p in F:
        if p in seen:
            continue
        stack, cur = [p], set()
        while stack:
            q = stack.pop()
            if q in cur:
                continue
            cur.add(q)
            stack += [r for r in F if r not in cur and abs(r[0] - q[0]) < m and abs(r[1] - q[1]) < n]
        seen |= cur
        comp.append(frozenset(cur))
    return comp


def level1(E, e0, lam, c, Q, U):
    """E1 minus E0: the union of the real level-1 errors. By (iv) such an error is a whole
    component of E \\ E0 under (lam Q, lam U)-linking."""
    F = set(E) - e0
    real = []
    for S in components(F, lam * Q, lam * U):
        if not fits(S, Q, U):
            continue
        mins = minimal1(S, lam)
        if not mins:
            continue                                   # (ii) fails
        if any(not linked(A, B, c, c) for A, B in itertools.combinations(mins, 2)):
            continue                                   # (iii) fails
        real.append(S)
    return real


def cand1_small(F, lam, Q, U):
    """Small candidate level-1 errors inside F: a minimal one, possibly with one more point."""
    mins = minimal1(F, lam)
    out = set(mins)
    for M in mins:
        for p in F:
            if p not in M and fits(M | {p}, Q, U):
                out.add(M | frozenset([p]))
    return [S for S in out if fits(S, Q, U)]


def has_candidate2(F, lam, Q, U):
    """F contains two disjoint candidate level-1 errors that are (lam Q, lam U)-linked."""
    c1 = cand1_small(F, lam, Q, U)
    for A, B in itertools.combinations(c1, 2):
        if not (A & B) and linked(A, B, lam * Q, lam * U):
            return True
    return False


def candidates2_small(F, lam, Q, U):
    c1 = cand1_small(F, lam, Q, U)
    out = []
    for A, B in itertools.combinations(c1, 2):
        if not (A & B) and linked(A, B, lam * Q, lam * U):
            out.append(A | B)
    return out


def random_set(rng, lam, Q, U, span):
    pts = set()
    for _ in range(rng.randint(1, 4)):                 # clusters, some of them close together
        cx, ct = rng.randrange(0, span * Q), rng.randrange(0, span * U)
        for _ in range(rng.randint(1, 2)):             # sub-clusters at the scale of lam
            sx, st = cx + rng.randrange(-3 * lam, 3 * lam + 1), ct + rng.randrange(-3 * lam, 3 * lam + 1)
            for _ in range(rng.randint(1, 3)):
                pts.add((sx + rng.randrange(-lam, lam + 1), st + rng.randrange(-lam, lam + 1)))
    return sorted(pts)


def main():
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    rng = random.Random(1)
    for lam, c, Q in ((3, 20, 40), (3, 5, 40), (3, 2, 40), (3, 1, 40), (4, 3, 48), (4, 24, 48)):
        U = Q
        stats = dict(sets=0, with_level1_errors=0, points_above_level1=0, f1_violations=0,
                     max_level1_extent=0, level2_errors=0, max_level2_extent_in_Q=0.0,
                     f2_violations=0)
        for _ in range(trials):
            E = random_set(rng, lam, Q, U, rng.choice((2, 6, min(c + 2 * lam + 8, 18))))
            e0 = level0(E, lam)
            F = set(E) - e0
            # F1 at level 1
            mins = minimal1(F, lam)
            covered = set().union(*mins) if mins else set()
            if F - covered:
                stats['f1_violations'] += 1
            real1 = level1(E, e0, lam, c, Q, U)
            e1 = set(e0).union(*real1) if real1 else set(e0)
            stats['sets'] += 1
            stats['with_level1_errors'] += bool(real1)
            for S in real1:
                ext = max(max(p[0] for p in S) - min(p[0] for p in S), max(p[1] for p in S) - min(p[1] for p in S)) + 1
                stats['max_level1_extent'] = max(stats['max_level1_extent'], ext)
                if ext > c + 2 * lam - 2:
                    stats['f2_violations'] += 1
            G = set(E) - e1
            stats['points_above_level1'] += len(G)
            # F1 at level 2: every component (lam Q^2 linking: here everything is one) of E \ E1
            # must contain two disjoint linked candidate level-1 errors; all of E fits a Q^2 box
            if G and not has_candidate2(G, lam, Q, U):
                stats['f1_violations'] += 1
            # F2 at level 2: if E \ E1 is itself a real level-2 error, bound its extent
            if G:
                c2 = candidates2_small(G, lam, Q, U)
                if c2 and not any(not linked(A, B, c * Q, c * U) for A, B in itertools.combinations(c2, 2)):
                    stats['level2_errors'] += 1
                    ex = (max(p[0] for p in G) - min(p[0] for p in G)) / Q
                    et = (max(p[1] for p in G) - min(p[1] for p in G)) / U
                    stats['max_level2_extent_in_Q'] = max(stats['max_level2_extent_in_Q'], ex, et)
                    if max(ex, et) >= c + 2 * lam + 4:
                        stats['f2_violations'] += 1
        stats['max_level2_extent_in_Q'] = round(stats['max_level2_extent_in_Q'], 2)
        print(f'lam {lam} c {c} (4(lam+2) = {4 * (lam + 2)}) Q = U = {Q}: bounds {c + 2 * lam - 2} and {c + 2 * lam + 4} Q:', stats, flush=True)


if __name__ == '__main__':
    main()
