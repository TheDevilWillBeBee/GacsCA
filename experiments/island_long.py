"""Misaligned-colony island on a ring with two level-2 cells (512 colonies): per-period level-0
damage and level-1 damage (colonies whose decoded level-1 state is wrong)."""
import sys, time, json, numpy as np, torch
from gacsca.build import make_system
from gacsca.hierarchy import encode_info
Q, U = 256, 8192
ncol = int(sys.argv[1]) if len(sys.argv) > 1 else 512
nper = int(sys.argv[2]) if len(sys.argv) > 2 else 180
shift, n_island, c0 = 100, 2, 20
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
log = []
t0 = time.time()
for per in range(1, nper + 1):
    st = g.run(st, U, 0.0, t0=(per - 1) * U)
    N = g.to_np(st); d = np.where(N["addr"][0] != ref)[0]
    info = g.info_bits(st).cpu().numpy()[0]
    bad1 = []
    for i in range(ncol):
        dd = L.decode(info[i * Q + L.b0:i * Q + L.b0 + L.K])
        if dd["ADDR"] != i % Q or dd["AGE"] != per % U: bad1.append(i)
    rec = dict(per=per, l0_damaged=int(len(d)), l0_lo=int(d.min()) if len(d) else -1, l0_hi=int(d.max()) if len(d) else -1,
               l1_bad=len(bad1), l1_lo=min(bad1) if bad1 else -1, l1_hi=max(bad1) if bad1 else -1)
    log.append(rec)
    if per % 5 == 0 or per <= 3:
        print(f"period {per}: level-0 damaged {rec['l0_damaged']} in colonies [{rec['l0_lo']/Q:.2f},{rec['l0_hi']/Q:.2f}], "
              f"level-1 bad cells {rec['l1_bad']} in [{rec['l1_lo']},{rec['l1_hi']}]  ({time.time()-t0:.0f}s)", flush=True)
    if rec["l0_damaged"] == 0 and rec["l1_bad"] == 0:
        print("fully healed at period", per); break
json.dump(log, open(f"figs/island_long_n{ncol}.json", "w"))
