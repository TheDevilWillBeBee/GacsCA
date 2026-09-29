import json, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
res = json.load(open("figs/level0_sweep_gpu.json"))
fig, axes = plt.subplots(1, 3, figsize=(16, 4.2))
def sel(pred): return sorted([r for r in res if pred(r)], key=lambda r: r["eps"])
ax = axes[0]
for name, pred in [("Gray rules", lambda r: r["Q"]==271 and r["ncol"]==4 and r["variant"]["flag1_ii_in_colony"]),
                   ("Masumori variant", lambda r: r["Q"]==271 and r["ncol"]==4 and not r["variant"]["flag1_ii_in_colony"])]:
    rr = sel(pred); ax.plot([r["eps"] for r in rr], [r["addr_rec"] for r in rr], "o-", label=name+" (Address)")
    ax.plot([r["eps"] for r in rr], [r["frac_ok_noisy"] for r in rr], "x--", alpha=.6, label=name+" (frac correct during noise)")
ax.set_xlabel("error rate eps"); ax.set_ylabel("P(recovered) / fraction"); ax.set_title("Q=271, 4 colonies, 500 noisy + 500 clean steps"); ax.legend(fontsize=7)
ax = axes[1]
for Q in [32, 64, 128, 271, 512, 1024]:
    rr = sel(lambda r: r["Q"]==Q and r["ncol"]==4 and r["variant"]["flag1_ii_in_colony"] and 0.29 < r["eps"] < 0.49)
    ax.plot([r["eps"] for r in rr], [r["addr_rec"] for r in rr], "o-", label=f"Q={Q}")
ax.set_xlabel("eps"); ax.set_title("Q dependence (4 colonies)"); ax.legend(fontsize=7)
ax = axes[2]
for n in [2, 4, 8, 16, 32]:
    rr = sel(lambda r: r["Q"]==271 and r["ncol"]==n and r["variant"]["flag1_ii_in_colony"] and 0.35 < r["eps"] < 0.45)
    ax.plot([r["eps"] for r in rr], [r["addr_rec"] for r in rr], "o-", label=f"{n} colonies")
ax.set_xlabel("eps"); ax.set_title("system-size dependence (Q=271)"); ax.legend(fontsize=7)
plt.tight_layout(); plt.savefig("figs/level0_recovery.png", dpi=110)
