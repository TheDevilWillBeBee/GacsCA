"""Which phase of the work period carries the linear-in-eps level-1 error channel?  Level-0 noise
eps is applied only while the (level-0) age lies in a given window; the induced level-1 error rate
per period is measured as in stage1_gpu.py (stage-1 system, proper 256-colony ring)."""
import sys, json, time, numpy as np, torch
from gacsca.build import make_system
from gacsca.hierarchy import encode_info
from gacsca.params import Params
from gacsca import level0_np as l0

ncol, Q, U = 256, 256, 16384
sysm = make_system(Q=Q, U=U, ncol=ncol, R=3, D=3)
p, T, L, sched = sysm.p, sysm.T, sysm.L, sysm.sched
g = sysm.gpu_engine(seed=3); eng = sysm.np_engine()
p1 = Params(Q=Q, U=U, ncol=1)
def decode(st):
    info = g.info_bits(st).cpu().numpy()
    out = []
    for b in range(info.shape[0]):
        cols = [L.decode(info[b, i * Q + L.b0:i * Q + L.b0 + L.K]) for i in range(ncol)]
        out.append(dict(addr=np.array([[c["ADDR"] for c in cols]]), age=np.array([[c["AGE"] for c in cols]]),
                        f1=np.array([[c["F1"] for c in cols]]), f2=np.array([[c["F2"] for c in cols]]),
                        wf1=np.zeros((1, ncol), np.int8), wf2=np.zeros((1, ncol), np.int8),
                        simage=np.zeros((1, ncol), np.int32), simaddr=np.zeros((1, ncol), np.int32)))
    return out
windows = {"all": (0, U), "gather1": (sched.gather_starts[0], sched.gather_starts[1]), "gather2": (sched.gather_starts[1], sched.gather_starts[2]),
           "gather3": (sched.gather_starts[2], sched.compute_start), "compute": (sched.compute_start, sched.compute_end),
           "signal+rest": (sched.compute_end, sched.trickle[0]), "trickle": sched.trickle, "tail": (sched.trickle[1], U)}
eps = float(sys.argv[1]) if len(sys.argv) > 1 else 3e-4
B = int(sys.argv[2]) if len(sys.argv) > 2 else 8
nper = int(sys.argv[3]) if len(sys.argv) > 3 else 5
res = {}
for name, (lo, hi) in windows.items():
    level1 = [dict(addr=i % Q, age=0, f1=0, f2=0) for i in range(ncol)]
    S = eng.initial(B, info_bits=np.tile(encode_info(level1, L, Q)[None, :], (B, 1)))
    st = g.to_gpu(S); t = 0; t0 = time.time()
    prev = decode(st); errs = []
    for per in range(nper):
        st = g.run(st, U, lambda tt: eps if lo <= ((tt - 1) % U) < hi else 0.0, t0=t); t += U
        cur = decode(st)
        n_err = 0
        for b in range(B):
            pred = l0.step(prev[b], p1); pred.pop("_info")
            mism = (pred["addr"] != cur[b]["addr"]) | (pred["age"] != cur[b]["age"]) | (pred["f1"] != cur[b]["f1"]) | (pred["f2"] != cur[b]["f2"])
            n_err += int(mism.sum())
        errs.append(n_err / (B * ncol)); prev = cur
    hits = eps * (hi - lo) * Q     # expected hits per colony-period in the window
    res[name] = dict(window=(lo, hi), err=errs, hits_per_colony_period=hits)
    print(f"{name:12s} window [{lo},{hi}) hits/colony-period={hits:8.1f}: level-1 error rate {np.mean(errs[1:]):.4f} per period {np.round(errs, 4).tolist()} ({time.time()-t0:.0f}s)", flush=True)
json.dump(res, open(f"figs/phase_noise_{eps:g}.json", "w"))
