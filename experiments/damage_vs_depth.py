"""Injected damage (misaligned islands or space-time bursts) at depth 0 (trickle disabled) vs
depth 1, on a 512-colony ring (two level-2 cells).  Logs per-period level-0 and level-1 damage."""
import sys, time, json, argparse, numpy as np, torch
from gacsca.build import make_system
from gacsca.hierarchy import encode_info
ap = argparse.ArgumentParser()
ap.add_argument("--kind", default="island")          # island | burst
ap.add_argument("--n_island", type=int, default=2)
ap.add_argument("--shift", type=int, default=100)
ap.add_argument("--age_off", type=int, default=0)     # time misalignment of the island
ap.add_argument("--w", type=int, default=300)         # burst width (cells)
ap.add_argument("--tau", type=int, default=100)       # burst duration (steps)
ap.add_argument("--rate", type=float, default=1.0)    # burst replacement probability
ap.add_argument("--nper", type=int, default=120)
ap.add_argument("--ncol", type=int, default=512)
ap.add_argument("--seed", type=int, default=0)
ap.add_argument("--tag", default="")
a = ap.parse_args()
Q, U = 256, 8192
sysm = make_system(Q=Q, U=U, ncol=a.ncol, R=3, D=3)
p, T, L, sched = sysm.p, sysm.T, sysm.L, sysm.sched
eng = sysm.np_engine()
ref = np.arange(p.L) % Q
c0 = 20


def initial():
    level1 = [dict(addr=i % Q, age=0, f1=0, f2=0) for i in range(a.ncol)]
    S = eng.initial(1, info_bits=encode_info(level1, L, Q)[None, :])
    if a.kind == "island":
        base = c0 * Q + a.shift
        src = {k: S[k][:, c0 * Q:(c0 + a.n_island) * Q].copy() for k in ("addr", "age", "f1", "f2", "wf1", "wf2", "trk")}
        for k in src: S[k][:, base:base + a.n_island * Q] = src[k]
        if a.age_off:
            S["age"][:, base:base + a.n_island * Q] = (S["age"][:, base:base + a.n_island * Q] + a.age_off) % U
    return S


def run(trickle):
    g = sysm.gpu_engine(seed=a.seed, trickle=trickle)
    st = g.to_gpu(initial())
    log = []
    t = 0
    if a.kind == "burst":
        # burst: cells in [c0*Q, c0*Q + w) replaced with prob rate for tau steps (via mask-less high eps on a slice)
        rng = np.random.default_rng(a.seed)
        buf = torch.empty_like(st)
        for k in range(a.tau):
            g.step(st, buf, t + 1, 0.0); st, buf = buf, st; t += 1
            N = g.to_np(st)
            hit = rng.random(a.w) < a.rate
            idx = np.arange(c0 * Q, c0 * Q + a.w)[hit]
            N["addr"][0, idx] = rng.integers(0, Q, len(idx)); N["age"][0, idx] = rng.integers(0, U, len(idx))
            for kk in ("f1", "f2", "wf1", "wf2"): N[kk][0, idx] = rng.integers(0, 2, len(idx))
            N["trk"][0, idx] = rng.integers(0, 2, (len(idx),) + N["trk"].shape[2:])
            st = g.to_gpu(N)
    t0 = time.time()
    for per in range(1, a.nper + 1):
        st = g.run(st, U - (t % U) if per == 1 else U, 0.0, t0=t); t = per * U
        N = g.to_np(st); d = np.where(N["addr"][0] != ref)[0]
        info = g.info_bits(st).cpu().numpy()[0]
        bad1 = [i for i in range(a.ncol) if (lambda dd: dd["ADDR"] != i % Q or dd["AGE"] != per % U)(L.decode(info[i * Q + L.b0:i * Q + L.b0 + L.K]))]
        rec = dict(per=per, l0=int(len(d)), l0_lo=int(d.min()) if len(d) else -1, l0_hi=int(d.max()) if len(d) else -1, l1=len(bad1))
        log.append(rec)
        if rec["l0"] == 0 and rec["l1"] == 0:
            break
    print(f"{a.tag} trickle={trickle}: periods={log[-1]['per']} final l0={log[-1]['l0']} l1={log[-1]['l1']}  first l0={log[0]['l0']} ({time.time()-t0:.0f}s)", flush=True)
    return log


res = dict(args=vars(a), depth0=run(False), depth1=run(True))
json.dump(res, open(f"figs/dvd_{a.tag}.json", "w"))
