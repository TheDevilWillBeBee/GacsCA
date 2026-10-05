"""Error patterns beyond Gray's level-0 class: two sites at distance d (same tick), healthy slice.
usage: GACS_COPIES=3 python3 negctl.py cand_x.npz | GACS_COPIES=5 python3 negctl.py G15"""
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
C = cand.c_backend(); Q = p.Q
rng = np.random.default_rng(11)
n = 16
top = codec.random_upper(cand, 1, rng)
full = codec.encode(cand, top)
up = full[:, (np.arange(n) + Q // 2 - n // 2) % Q]
lo_site, hi_site = (n // 2 - 1) * Q, (n // 2 + 1) * Q - 8
X0 = codec.encode(cand, up); N = X0.shape[1]
times = np.sort(rng.integers(0, p.U - 1, 10))
res = {d: [0, 0] for d in (1, 2, 3, 4)}
P = C.pack(X0); t_prev = 0
for t in times:
    P = C.run_packed(P, int(t - t_prev), threads=3); t_prev = int(t)
    X = C.unpack(P, N)
    ref1 = C.unpack(C.run_packed_scalar(P.copy(), 1), N)
    for d in res:
        for _ in range(100):
            x = int(rng.integers(lo_site, hi_site))
            Y = X.copy()
            for s in (x, x + d):
                Y[:, s] = rng.random(cand.W) < 0.5
            Y1 = C.unpack(C.run_packed_scalar(C.pack(Y), 1), N)
            res[d][0] += 1; res[d][1] += int((Y1 != ref1).any())
print(json.dumps(dict(copies=rule_g.NC, Q=Q, pairs_at_distance={d: dict(trials=v[0], not_gone_after_one_tick=v[1]) for d, v in res.items()})))
