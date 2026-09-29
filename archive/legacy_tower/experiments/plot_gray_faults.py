"""Plot sampled spatial damage and distinguish structural from flag recovery."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checkpoint", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    with np.load(args.checkpoint, allow_pickle=False) as f:
        meta = json.loads(str(f["_metadata"]))
        spatial = f["structure_bins"]
    identity = meta["identity"]
    if identity["protocol"] != "gray-physical-transients":
        parser.error("expected a physical-transient checkpoint")
    samples = meta["samples"]
    times = np.array([sample["step"] for sample in samples])
    if len(times) != len(spatial) or not len(times):
        parser.error("checkpoint needs consistent nonempty samples")
    Q = identity["Q"]
    fig, axes = plt.subplots(2, 3, figsize=(12, 6.2), constrained_layout=True)
    for col, box in enumerate(identity["boxes"]):
        b, end = box["batch"], box["stop"]
        elapsed = times - end
        selected = (times >= box["start"]) & (elapsed <= 2 * Q)
        label = identity["scenarios"][b]
        axes[0, col].set_title(label)
        if selected.sum() < 2:
            for row in range(2):
                axes[row, col].text(.5, .5, "Not yet observed", ha="center", va="center",
                                    transform=axes[row, col].transAxes)
            continue
        centers = (np.arange(spatial.shape[-1]) + .5) * 64 / Q
        local = (centers >= box["left"] / Q - .15) & (centers <= box["right"] / Q + .15)
        ax = axes[0, col]
        im = ax.pcolormesh(centers[local], elapsed[selected],
                           spatial[selected, b][:, local] / 64, shading="nearest",
                           vmin=0, vmax=1, cmap="magma")
        ax.set_yscale("symlog", linthresh=256)
        ax.axhline(0, color="cyan", lw=.8, ls="--")
        ax.set_xlabel("Physical position / Q")
        ax.set_ylabel("Steps since fault ends")
        ax = axes[1, col]
        for name, color, style in (("bad_structure", "black", "-"),
                                   ("flag1", "#d95f02", "--"), ("flag2", "#1b9e77", ":")):
            counts = np.array([sample[name][b] for sample in samples])
            ax.plot(elapsed[selected], counts[selected], style, color=color,
                    marker=".", markersize=3, label=name.replace("_", " "))
        ax.set_xscale("symlog", linthresh=256)
        ax.set_yscale("symlog", linthresh=1)
        ax.axvline(0, color="gray", lw=.8, ls="--")
        ax.set_xlabel("Steps since fault ends")
        ax.set_ylabel("Number of physical cells")
        ax.grid(alpha=.15)
        ax.legend(fontsize=7)
    if "im" in locals():
        fig.colorbar(im, ax=axes[0, :], label="Sampled Address/Age errors per 64-cell bin", shrink=.75)
    variant = identity.get("variant", {}).get("flag2_healthy_erase", "printed")
    fig.suptitle(f"Gray physical transients ({variant}) — {meta['status']}, {meta['steps']:,} steps\n"
                 "One seed per scenario; sampled states, not an iid robustness estimate", fontsize=11)
    output = args.output or args.checkpoint.with_suffix("")
    fig.savefig(output.with_suffix(".png"), dpi=170)
    fig.savefig(output.with_suffix(".pdf"))
    print(output.with_suffix(".png"))


if __name__ == "__main__":
    main()
