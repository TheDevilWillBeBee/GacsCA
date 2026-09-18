import sys, numpy as np, torch
from gacsca.build import make_system
from gacsca.hierarchy import encode_info
Q, U = 256, 16384
ncol = int(sys.argv[1]) if len(sys.argv) > 1 else 256
shift, n_island, nper, c0 = 100, 2, int(sys.argv[2]) if len(sys.argv) > 2 else 3, 20
sysm = make_system(Q=Q, U=U, ncol=ncol, R=3, D=3)
p, T, L, sched = sysm.p, sysm.T, sysm.L, sysm.sched
eng = sysm.np_engine(); g = sysm.gpu_engine(seed=0, trickle=True)
level1 = [dict(addr=i % Q, age=0, f1=0, f2=0) for i in range(ncol)]
S = eng.initial(1, info_bits=encode_info(level1, L, Q)[None, :])
a = c0 * Q + shift
src = {k: S[k][:, c0 * Q:(c0 + n_island) * Q].copy() for k in ("addr", "age", "f1", "f2", "wf1", "wf2", "trk")}
for k in src: S[k][:, a:a + n_island * Q] = src[k]
st = g.to_gpu(S)
ref = np.arange(p.L) % Q
def report(st, tag):
    N = g.to_np(st); d = np.where(N["addr"][0] != ref)[0]
    info = g.info_bits(st).cpu().numpy()[0]
    dec = lambda i: tuple(L.decode(info[i*Q+L.b0:i*Q+L.b0+L.K])[k] for k in ("ADDR","AGE","F1","F2"))
    if len(d): 
        lo, hi = d.min(), d.max()
        print(f"{tag}: damaged {len(d)} cells in [{lo},{hi}] = colonies [{lo/Q:.2f},{hi/Q:.2f}]; addr at lo..lo+3: {N['addr'][0,lo:lo+4].tolist()}, at hi-3..hi: {N['addr'][0,hi-3:hi+1].tolist()}; right neighbour addr {N['addr'][0,hi+1:hi+4].tolist()}; f1 sum in island {N['f1'][0,lo:hi+1].sum()}")
        print("   level-1 decoded (colonies lo/Q-2 .. hi/Q+3):", [(i, dec(i)) for i in range(int(lo//Q)-2, int(hi//Q)+4)])
    else:
        print(f"{tag}: no damage")
for per in range(nper):
    for (t_rel, tag) in [(sched.trickle[0] - 1, "before window"), (sched.trickle[1] + 300, "after window"), (U - 1, "period end")]:
        pass
    t0 = per * U
    st = g.run(st, sched.trickle[0] - 1, 0.0, t0=t0); report(st, f"period {per} before window (age {sched.trickle[0]-1})")
    st = g.run(st, 300, 0.0, t0=t0 + sched.trickle[0] - 1); report(st, f"period {per} mid-window (+300)")
    st = g.run(st, U - (sched.trickle[0] - 1) - 300, 0.0, t0=t0 + sched.trickle[0] - 1 + 300); report(st, f"period {per} end")
