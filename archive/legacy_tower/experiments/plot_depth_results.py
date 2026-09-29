import json, glob, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, axes = plt.subplots(1, 2, figsize=(14, 4.5))
ax = axes[0]
for f in sorted(glob.glob("figs/dvd_isl_*.json")):
    r = json.load(open(f)); tag = f.split("dvd_")[1][:-5]
    for key, ls in (("depth0", "--"), ("depth1", "-")):
        lg = r[key]
        ax.plot([e["per"] for e in lg], [e["l0"] for e in lg], ls, label=f"{tag} {key}")
ax.set_xlabel("work period (U = 8192 steps)"); ax.set_ylabel("level-0 cells with wrong Address"); ax.set_yscale("symlog")
ax.set_title("Injected misaligned islands: level-0 only (dashed) vs depth 1 (solid)"); ax.legend(fontsize=6)
ax = axes[1]
r = json.load(open("figs/stage1_l1_error_rate.json"))
eps = sorted(float(k) for k in r)
ax.loglog(eps, [np.mean(r[str(e)]["l1_err"][1:]) if str(e) in r else np.mean(r[repr(e)]["l1_err"][1:]) for e in eps], "o-", label="measured ε₁ (per level-1 cell-period)")
ax.loglog(eps, [2 * 256 * 8192 * e**2 for e in eps], "--", label="2QUε² (adjacent-pair estimate)")
ax.loglog(eps, [40 * e for e in eps], ":", label="40ε (linear guide)")
ax.set_xlabel("level-0 error rate ε"); ax.set_ylabel("level-1 error rate ε₁"); ax.set_title("Amplifier relation (stage 1, Q=256, U=8192, R=3)"); ax.legend(fontsize=7)
plt.tight_layout(); plt.savefig("figs/depth_results.png", dpi=110)
print("saved")
