"""Independent finite counterexamples for round-two Gray-class claims."""
import json
from pathlib import Path
from gacsca.fixed_rule.design_optimization import gray_errors as g

ROOT = Path('figs/fixed_rule/design_optimization/level1_campaign')
M = (1 << 64) - 1


def mix(z):
    z = (z + 0x9E3779B97F4A7C15) & M
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & M
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M
    return z ^ (z >> 31)


def grid_near(seed, ext, grid=50):
    a, b, c, d = (ext[k] for k in ('x_lo', 'x_hi', 't_lo', 't_hi'))
    near, inside = set(), set()
    for cx in range((a - 23) // grid, (b + 23) // grid + 1):
        for ct in range((c - 23) // grid, (d + 23) // grid + 1):
            h = mix(seed ^ mix((cx << 24) ^ ct))
            x, t = cx * grid + h % (grid - 25), ct * grid + ((h >> 20) % (grid - 25))
            if a <= x <= b and c <= t <= d:
                inside.add((x, t))
            elif max(a - x, 0, x - b) < 24 and max(c - t, 0, t - d) < 24:
                near.add((x, t))
    return sorted(near), sorted(inside)


S = set(g.dense_box(0, 0, 36, 36))
pair = {(1000, 0), (1001, 0)}
print('shortcut isolated pair is E0:', g.level0_points(pair) == pair)
print('shortcut S alone:', g.classify(S, Q=512, U=112608)['level1'])
print('shortcut S with isolated E0 pair:', g.classify(S, S | pair, Q=512, U=112608))
S0 = set(g.dense_box(0, 0, 3, 3)) | {(1000, 0)}
print('S containing E0', g.level0_points(S0), g.classify(S0, Q=512, U=112608))

for batch in ('b81', 'b82'):
    p = next(ROOT.glob(f'G15_{batch}*.json'))
    r = json.loads(p.read_text())['rings'][0]
    e = r['extent']
    S = set(g.dense_box(e['x_lo'], e['t_lo'], e['x_hi'] - e['x_lo'] + 1,
                        e['t_hi'] - e['t_lo'] + 1))
    near, inside = grid_near(r['noise_seed'], e)
    print(batch, 'seed', r['noise_seed'], 'near-outside', near, 'inside', inside)
    print(batch, 'receipt verdict', r['gray']['level1'],
          'full-E local witness verdict', g.classify(S, S | set(near), Q=512, U=112608)['level1'])
