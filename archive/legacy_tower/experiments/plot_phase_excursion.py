"""Visualize a replay-verified local phase excursion without declaring permanent loss."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch
import matplotlib.pyplot as plt
import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--start", type=int, default=6400)
    parser.add_argument("--stop", type=int, default=7800)
    args = parser.parse_args()
    with np.load(args.input, allow_pickle=False) as z:
        meta = json.loads(str(z["_metadata"]))
        time = z["times"]
        phases = z["phase_offsets"]
        counts = z["phase_histograms"]
    target = meta["phases"][meta["initial_bit"]]
    other = meta["phases"][1 - meta["initial_bit"]]
    Q = meta["Q"]
    selected = (time >= args.start) & (time <= args.stop)
    if selected.sum() < 2:
        parser.error("time window must contain at least two samples")
    t = time[selected]
    category = np.where(phases[selected] == target, 0, np.where(phases[selected] == other, 1, 2))
    cmap = ListedColormap(["#246a93", "#d26925", "#e4e4e4"])
    norm = BoundaryNorm([-.5, .5, 1.5, 2.5], 3)
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.6), constrained_layout=True)
    half_step = (t[1] - t[0]) / 2
    for ax, cells, title in ((axes[0], phases.shape[1], f"Entire {meta['ncol']}-colony ring"),
                             (axes[1], Q, "Fixed observer window")):
        # Nearest-neighbor rasterization: do not average discrete phase labels.
        ax.imshow(category[:, :cells], cmap=cmap, norm=norm, origin="lower", aspect="auto",
                  interpolation="nearest", extent=(-.5, cells - .5, t[0] - half_step, t[-1] + half_step))
        ax.set_xlabel("Physical site x")
        ax.set_ylabel("Physical time under persistent noise")
        ax.set_title(title)
    axes[0].axvline(Q - .5, color="black", linestyle="--", linewidth=1)
    axes[2].plot(time, counts[:, 0, target] / phases.shape[1], color="#246a93", label="Original phase, ring")
    axes[2].plot(time, counts[:, 1, target] / Q, color="#246a93", linestyle="--", label="Original phase, window")
    axes[2].plot(time, counts[:, 1, other] / Q, color="#d26925", label="Opposite phase, window")
    axes[2].axhline(.5, color="black", linestyle=":", linewidth=1)
    axes[2].set_xlim(args.start, args.stop)
    axes[2].set_ylim(0, 1)
    axes[2].set_xlabel("Physical time")
    axes[2].set_ylabel("Phase mass; strict-majority threshold 0.5")
    axes[2].set_title("Local opposite-bit excursion, then recovery")
    axes[2].legend(fontsize=7, loc="upper right")
    axes[2].grid(alpha=.2)
    axes[1].legend(handles=[Patch(color=cmap(i), label=label) for i, label in enumerate(
        (f"Original phase {target}", f"Opposite phase {other}", "Other Address phases"))], fontsize=7, loc="upper right")
    fig.suptitle(f"Replay-verified local phase excursion: ε={meta['epsilon']}, Q={Q}, trial {meta['trial']}\n"
                 f"No hierarchy; image samples every {t[1]-t[0]} steps; opposite-bit output is not permanent memory loss", fontsize=10)
    fig.savefig(args.input.with_suffix(".png"), dpi=190)
    fig.savefig(args.input.with_suffix(".pdf"))


if __name__ == "__main__":
    main()
