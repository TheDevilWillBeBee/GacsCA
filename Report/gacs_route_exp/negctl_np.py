"""Negative control with the NumPy reference stepper (no C kernel): two sites hit at the
same tick at distance d, healthy slice, at Ages 2, 3, 4. Many well-separated trials share a ring.
usage: GACS_COPIES=5 python3 negctl_np.py G15 | GACS_COPIES=3 python3 negctl_np.py cand_x.npz"""
import sys, os, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np
from gacsca import candidates, machine, codec, rule_g
if sys.argv[1] == 'G15':
    p, layout, prog = candidates.build('G15'); cand = machine.Candidate(p, prog.rom, layout)
else:
    z = np.load(os.path.join(HERE, sys.argv[1]), allow_pickle=False)
    params = json.loads(str(z['params']))
    for key in ('skew', 'gathers_q'): params[key] = tuple(params[key])
    p = rule_g.ParamsG(**params).check(); cand = machine.Candidate(p, z['rom'], z['layout'])
Q = p.Q; rng = np.random.default_rng(11); n = 8
top = codec.random_upper(cand, 1, rng)
full = codec.encode(cand, top)
up = full[:, (np.arange(n) + Q // 2 - n // 2) % Q]
X = codec.encode(cand, up); N = X.shape[1]
lo_site, hi_site = (n // 2 - 1) * Q, (n // 2 + 1) * Q - 8
res = {d: [0, 0] for d in (1, 2, 3, 4)}
t0 = time.time()
X = cand.step_numpy(X)
for age in range(3):
    X = cand.step_numpy(X)
    ref1 = cand.step_numpy(X)
    for d in res:
        for rep in range(5):
            # trials 40 cells apart do not interact within one tick (radius 5)
            starts = np.arange(lo_site + int(rng.integers(0, 40)), hi_site - 8, 40)
            Y = X.copy()
            for x in starts:
                for s in (x, x + d):
                    Y[:, s] = rng.random(cand.W) < 0.5
            Y1 = cand.step_numpy(Y)
            diff = (Y1 != ref1).any(axis=0)
            for x in starts:
                res[d][0] += 1
                res[d][1] += int(diff[x - 12:x + 17].any())
print(json.dumps(dict(copies=rule_g.NC, Q=Q, seconds=round(time.time() - t0),
      pairs_at_distance={d: dict(trials=v[0], not_gone_after_one_tick=v[1]) for d, v in res.items()})))
