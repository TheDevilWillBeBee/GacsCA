"""Reproduce the qualitative setting of Masumori et al. Fig. 7: Q=271, noise with rate eps for the
first 500 steps, then no noise. Space-time plots of damaged cells (black) and Flag1=1 (gray)."""
import sys, time, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from gacsca.params import Params, Variant
from gacsca.sim_np import run, damage

Q = int(sys.argv[1]) if len(sys.argv) > 1 else 271
ncol = 4
T = int(sys.argv[2]) if len(sys.argv) > 2 else 1500
p = Params(Q=Q, ncol=ncol)
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
for ax, eps in zip(axes, [0.05, 0.5, 0.6]):
    t0 = time.time()
    rec, S = run(p, T, lambda t: eps if t <= 500 else 0.0, B=1, seed=1)
    dmg = rec["addr"][:, 0, :] != (np.arange(p.L) % Q)
    dmg |= rec["age"][:, 0, :] != (np.arange(T + 1)[:, None] % p.U)
    img = np.ones(dmg.shape + (3,))
    img[rec["f1"][:, 0, :] == 1] = 0.6
    img[dmg] = 0.0
    ax.imshow(img.transpose(1, 0, 2), aspect="auto", interpolation="nearest")
    ax.set_title(f"eps={eps}  final damaged={dmg[-1].sum()}  ({time.time()-t0:.1f}s)")
    ax.set_xlabel("time"); ax.set_ylabel("site")
    print(eps, "damaged at t=500:", dmg[500].sum(), " at end:", dmg[-1].sum(), "flag1 end:", rec["f1"][-1].sum(), flush=True)
plt.tight_layout(); plt.savefig("figs/masumori_fig7_np.png", dpi=110)
