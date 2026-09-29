"""Space-time picture of level-1 activity in the depth-2 tower: for each level-0 period, decode the
level-1 cells' primary track bits (MAILL, MAILR, SIG, ACC, HOLD, ARGA+1, T0) and plot them over
level-1 time (one row per level-0 period).  Usage: tower_viz.py <age1_start> <nper>"""
import sys, time, numpy as np, torch
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
a1s = int(sys.argv[1]) if len(sys.argv) > 1 else 0
nper = int(sys.argv[2]) if len(sys.argv) > 2 else 700
sys.argv = [sys.argv[0]]
import experiments.tower_acid as ta
T, L0, U0, Q0, Q1 = ta.T, ta.L0, ta.U0, ta.Q0, ta.Q1
rng = np.random.default_rng(0)
S1 = ta.level1_initial(rng, a1s)
S0 = ta.eng0.initial(1, info_bits=ta.encode_level1_into_level0(S1)[None, :])
S0["simage"][:] = a1s; S0["simaddr"][:] = (np.arange(ta.p0.L) // Q0) % Q1
st = ta.g0.to_gpu(S0)
names = ["MAILL", "MAILR", "SIG", "ACC", "ARGA+1", "T0", "BC", "HOLD"]
frames = {n: [] for n in names}
h = (T.R - 1) // 2
t = 0; t0 = time.time()
for per in range(nper):
    st = ta.g0.run(st, U0, 0.0, t0=t); t += U0
    dec = ta.decode_level0(st)
    for n in names:
        frames[n].append([d["tracks"][T[n], h] for d in dec])
print(f"done {nper} periods in {time.time()-t0:.0f}s")
fig, axes = plt.subplots(len(names), 1, figsize=(14, 2.0 * len(names)), sharex=True)
for ax, n in zip(axes, names):
    ax.imshow(np.array(frames[n]).T, aspect="auto", interpolation="nearest", cmap="Greys", extent=[a1s, a1s + nper, ta.ncol0, 0])
    ax.set_ylabel(n, fontsize=8)
axes[-1].set_xlabel("level-1 time (level-0 work periods)")
axes[0].set_title("Decoded level-1 track bits of 64 level-1 cells (one level-1 colony) simulated by 64 level-0 colonies")
plt.tight_layout(); plt.savefig(f"figs/tower_viz_{a1s}_{nper}.png", dpi=100)
