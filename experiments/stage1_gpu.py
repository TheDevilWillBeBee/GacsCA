"""Stage-1 self-simulation on the GPU: (a) noiseless acid test over several work periods;
(b) with level-0 noise: per-period rate of level-1 cells whose decoded new state differs from the
direct one-step prediction (the induced level-1 error rate)."""
import sys, json, time, numpy as np, torch
from gacsca.build import make_system
from gacsca.hierarchy import encode_info, level1_to_arrays
from gacsca import level0_np as l0
from gacsca.params import Params

ncol = 64
sysm = make_system(Q=256, U=16384, ncol=ncol, R=3, D=3)
p, T, L = sysm.p, sysm.T, sysm.L
g = sysm.gpu_engine(seed=1)
eng = sysm.np_engine()
U, Q = p.U, p.Q
p1 = Params(Q=Q, U=U, ncol=1)


def decode(st):
    info = g.info_bits(st).cpu().numpy()
    B = info.shape[0]
    out = []
    for b in range(B):
        cols = [L.decode(info[b, i * Q + L.b0: i * Q + L.b0 + L.K]) for i in range(ncol)]
        out.append(dict(addr=np.array([[c["ADDR"] for c in cols]]), age=np.array([[c["AGE"] for c in cols]]),
                        f1=np.array([[c["F1"] for c in cols]]), f2=np.array([[c["F2"] for c in cols]]),
                        wf1=np.zeros((1, ncol), np.int8), wf2=np.zeros((1, ncol), np.int8)))
    return out


def run(eps, B, nper, seed):
    rng = np.random.default_rng(seed)
    level1 = [dict(addr=i % Q, age=0, f1=0, f2=0) for i in range(ncol)]
    for k in rng.choice(ncol, 6, replace=False):
        level1[int(k)] = dict(addr=int(rng.integers(0, Q)), age=int(rng.integers(0, U)), f1=int(rng.integers(0, 2)), f2=0)
    S = eng.initial(B, info_bits=np.tile(encode_info(level1, L, Q)[None, :], (B, 1)))
    st = g.to_gpu(S)
    g.seed = seed
    prev = decode(st)
    errs, l0dmg = [], []
    t = 0
    for per in range(nper):
        st = g.run(st, U, eps, t0=t); t += U
        cur = decode(st)
        n_err = 0
        for b in range(B):
            pred = l0.step(prev[b], p1); pred.pop("_info")
            for k in ("addr", "age", "f1", "f2"):
                n_err += int((pred[k] != cur[b][k]).any(0).sum()) if k == "addr" else 0
            mism = ((pred["addr"] != cur[b]["addr"]) | (pred["age"] != cur[b]["age"]) | (pred["f1"] != cur[b]["f1"]) | (pred["f2"] != cur[b]["f2"]))
            n_err = n_err - int((pred["addr"] != cur[b]["addr"]).sum()) + int(mism.sum())
        errs.append(n_err / (B * ncol))
        addr0 = g.to_np(st)["addr"]
        l0dmg.append(float((addr0 != np.arange(p.L) % Q).mean()))
        prev = cur
    return errs, l0dmg


if __name__ == "__main__":
    t0 = time.time()
    e, d = run(0.0, 2, 4, 0)
    print(f"noiseless: level-1 mismatch rate per period = {e}  level-0 damage = {d}  ({time.time()-t0:.0f}s)", flush=True)
    assert max(e) == 0.0
    res = {}
    for eps in [1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 3e-3]:
        t0 = time.time()
        e, d = run(eps, 16, 6, 1)
        res[eps] = dict(l1_err=e, l0_damage=d)
        print(f"eps={eps:g}: level-1 error rate per cell-period = {np.mean(e[1:]):.4f} (per period: {np.round(e,4).tolist()}), "
              f"level-0 damaged fraction = {np.mean(d):.4f}  ({time.time()-t0:.0f}s)", flush=True)
    json.dump(res, open("figs/stage1_l1_error_rate.json", "w"), indent=1)
