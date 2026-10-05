"""Small level-1 probe (CPU, C kernel) of a scratch candidate: one dense side x side box of
random-valued errors (Gray: a dense box of side <= 104 is one level-1 error) in the middle
colony of a slice of a healthy upper colony; compare with the error-free ring at the next
period boundaries (decoded upper state and every physical bit).
usage: GACS_COPIES=3 python3 level1_mini.py cand_x.npz [side] [slice]"""
import sys, os, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np
from gacsca import machine, codec, rule_g
z = np.load(os.path.join(HERE, sys.argv[1]), allow_pickle=False)
side = int(sys.argv[2]) if len(sys.argv) > 2 else 100
n = int(sys.argv[3]) if len(sys.argv) > 3 else 24
THREADS = 3
params = json.loads(str(z['params']))
for key in ('skew', 'gathers_q'): params[key] = tuple(params[key])
p = rule_g.ParamsG(**params).check(); cand = machine.Candidate(p, z['rom'], z['layout'])
C = cand.c_backend(); Q, U = p.Q, p.U
rng = np.random.default_rng(3)
top = codec.random_upper(cand, 1, rng)
full = codec.encode(cand, top)                       # one healthy upper colony (Q upper cells)
idx = (np.arange(n) + Q // 2 - n // 2) % Q
up = full[:, idx]
X0 = codec.encode(cand, up); N = X0.shape[1]
tc = n // 2                                          # target colony
NB = 4                                               # boundaries followed
t0 = time.time()
P = C.pack(X0); ref = []
for b in range(NB):
    P = C.run_packed(P, U, threads=THREADS); ref.append(P.copy())
ref_dec = [codec.decode(cand, C.unpack(R, N)) for R in ref]
print(json.dumps(dict(copies=rule_g.NC, Q=Q, U=U, slice=n, side=side, ref_seconds=round(time.time() - t0))), flush=True)
E0, PL = p.E0, p.PL
phases = dict(gather1=300, rest1=8 * Q, gather3=24 * Q + 200, early=E0 + 5 * PL, phaseA=E0 + (p.NPe + 20) * PL,
              match=E0 + p.MP * PL - 50, final_early=E0 + (p.MP + 10) * PL, final_late=E0 + (p.NP - 20) * PL,
              commit=U - side // 2)
places = dict(mid=tc * Q + Q // 2 - side // 2, left=tc * Q - side // 2)
todo = [(ph, 'mid') for ph in phases] + [(ph, 'left') for ph in ('gather1', 'phaseA', 'final_late', 'commit')]
for ph, pl in todo:
    t1 = time.time()
    ta, x0 = phases[ph], places[pl]
    r2 = np.random.default_rng(abs(hash((ph, pl))) % (2 ** 32))
    P = C.run_packed(C.pack(X0), ta, threads=THREADS)
    for dt in range(side):                           # errors at (x, t), x in [x0, x0+side), t in (ta, ta+side]
        P = C.run_packed(P, 1, threads=1)
        X = C.unpack(P, N)
        X[:, x0:x0 + side] = r2.random((cand.W, side)) < 0.5
        P = C.pack(X)
    age = ta + side
    rec = dict(phase=ph, place=pl, t=ta, x=x0 - tc * Q, boundaries=[])
    for b in range(NB):
        tb = (b + 1) * U
        if tb < age:
            continue
        P = C.run_packed(P, tb - age, threads=THREADS); age = tb
        X = C.unpack(P, N)
        dec = codec.decode(cand, X)
        wrong = sorted(set(np.nonzero((dec != ref_dec[b]).any(axis=0))[0].tolist()))
        phys = int((X != C.unpack(ref[b], N)).sum())
        rec['boundaries'].append(dict(b=b + 1, wrong_upper_cells=[w - tc for w in wrong], physical_bits_differ=phys))
    rec['seconds'] = round(time.time() - t1)
    print(json.dumps(rec), flush=True)
