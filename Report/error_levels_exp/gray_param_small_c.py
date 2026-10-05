"""Extent of a level-1 error when c < lam (condition (iii) stricter than the link distance):
exhaustive on a line, random in the plane. Formula: c + 2*lam - 2."""
import json
import numpy as np
from gray_param import max_extent_line, is_level1, extent, extremal

out = dict(exhaustive_line=[], random_plane={}, extremal=[])
for lam, c in [(3, 1), (3, 2), (4, 1), (4, 2), (4, 3), (5, 1), (5, 2), (5, 4), (6, 1), (6, 3)]:
    span = c + 2 * lam + 2
    best, arg = max_extent_line(lam, c, span)
    out['exhaustive_line'].append(dict(lam=lam, c=c, max_extent=best, formula=c + 2 * lam - 2, witness=[p[0] for p in arg]))
rng = np.random.default_rng(1)
for lam, c in [(4, 1), (5, 2), (6, 3)]:
    best = 0
    for _ in range(60000):
        n = int(rng.integers(2, 7))
        w = c + 2 * lam + 3
        S = {(int(rng.integers(0, w)), int(rng.integers(0, w))) for _ in range(n)}
        if is_level1(S, lam, c):
            best = max(best, *extent(S))
    out['random_plane'][f'{lam},{c}'] = dict(max_extent_found=best, formula=c + 2 * lam - 2)
for lam, c in [(24, 16), (24, 20), (24, 1)]:
    # for c < lam the two middle points must be within c-1 of each other
    a = lam - 1
    S = [(0, 0), (a, a), (a + c - 1, a + c - 1), (2 * a + c - 1, 2 * a + c - 1)] if c > 1 else [(0, 0), (a, a), (2 * a, 2 * a)]
    out['extremal'].append(dict(lam=lam, c=c, extent=extent(S), level1=is_level1(S, lam, c), formula=c + 2 * lam - 2))
print(json.dumps(out, indent=1))
