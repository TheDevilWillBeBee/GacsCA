"""Two adjacent misaligned full colonies (Gray's 'misaligned level-1 cells'): a stable island for
the level-0 rules (no inconsistency at the left end of the left island colony, and the Flag1 wave
started at the island's right end cannot cross the internal colony boundary).  With the level-1
simulation active, F1* trickles down and the island erodes.  Proper level-1 ring: 256 colonies."""
import sys, time, json, numpy as np, torch
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from gacsca.build import make_system
from gacsca.hierarchy import encode_info

Q, U = 256, 16384
ncol = Q                      # level-1 ring is a full level-1 colony -> level-1 ground state
shift = int(sys.argv[1]) if len(sys.argv) > 1 else 100
nper = int(sys.argv[2]) if len(sys.argv) > 2 else 6
n_island = int(sys.argv[3]) if len(sys.argv) > 3 else 2
sysm = make_system(Q=Q, U=U, ncol=ncol, R=3, D=3)
p, T, L = sysm.p, sysm.T, sysm.L
eng = sysm.np_engine()
c0 = 20                       # island starts inside colony c0 at offset `shift`


def island_state():
    level1 = [dict(addr=i % Q, age=0, f1=0, f2=0) for i in range(ncol)]
    S = eng.initial(1, info_bits=encode_info(level1, L, Q)[None, :])
    a = c0 * Q + shift
    # n_island full colonies with base a: copy the ground-state colony pattern (local + tracks) shifted
    src = {k: S[k][:, c0 * Q:(c0 + n_island) * Q].copy() for k in ("addr", "age", "f1", "f2", "wf1", "wf2", "trk")}
    for k in src:
        S[k][:, a:a + n_island * Q] = src[k]
    # give the island colonies level-1 states consistent with their position (addr = c0, c0+1)
    return S


def run(trickle, every=32, lo=(c0 - 3) * Q, hi=(c0 + n_island + 3) * Q):
    g = sysm.gpu_engine(seed=0, trickle=trickle)
    st = g.to_gpu(island_state())
    fd, ff, ndmg = [], [], []
    ref = np.arange(p.L) % Q
    def cb(t, s):
        if t % every == 0:
            N = g.to_np(s)
            d = N["addr"][0] != ref
            fd.append(d[lo:hi]); ff.append(N["f1"][0, lo:hi] == 1); ndmg.append(int(d.sum()))
    t0 = time.time()
    st = g.run(st, nper * U, 0.0, callback=cb)
    print(f"trickle={trickle}: damaged cells per period: {ndmg[::U // every]} final={ndmg[-1]} ({time.time()-t0:.0f}s)", flush=True)
    return np.array(fd), np.array(ff), ndmg


fig, axes = plt.subplots(2, 1, figsize=(15, 8), sharex=True)
res = {}
for ax, tr in zip(axes, [False, True]):
    D_, F_, nd = run(tr)
    res[str(tr)] = nd
    img = np.ones(D_.shape + (3,)); img[F_] = 0.65; img[D_] = 0.0
    lo = (c0 - 3) * Q
    ax.imshow(img.transpose(1, 0, 2), aspect="auto", interpolation="nearest", extent=[0, nper * U, D_.shape[1] + lo, lo])
    for k in range(c0 - 3, c0 + n_island + 4): ax.axhline(k * Q, color="r", lw=0.3)
    for k in range(nper + 1): ax.axvline(k * U, color="b", lw=0.3)
    ax.set_ylabel("site"); ax.set_title(f"{'depth-1: trickle-down active' if tr else 'level-0 only (trickle-down disabled)'}: {n_island} misaligned full colonies (shift {shift}); damaged cells at end = {nd[-1]}")
axes[-1].set_xlabel("time (blue: work periods)")
plt.tight_layout(); plt.savefig(f"figs/island_trickle_n{n_island}_s{shift}.png", dpi=100)
json.dump(res, open(f"figs/island_trickle_n{n_island}_s{shift}.json", "w"))
