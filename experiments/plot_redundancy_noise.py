"""Plot independent-ring uncertainty for the matched redundancy experiment."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def wilson(k, n):
    z = 1.959963984540054
    p = k / n
    scale = 1 + z * z / n
    center = (p + z * z / (2 * n)) / scale
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / scale
    return max(0, center - half), min(1, center + half)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, nargs="+")
    parser.add_argument("--output", type=Path, help="output stem (default: first input)")
    args = parser.parse_args()
    datasets = [json.loads(path.read_text()) for path in args.input]
    data = datasets[0]
    if not all(d["complete"] for d in datasets):
        parser.error("experiment is not complete")
    cfg = data["parameters"]
    noise_version = cfg.get("noise_version", 1)
    for other in datasets[1:]:
        if any(other["parameters"][k] != cfg[k] for k in ("Q", "U", "ncol", "trials", "periods")):
            parser.error("cannot combine different experimental geometries or trial lengths")
        if other["parameters"].get("noise_version", 1) != noise_version:
            parser.error("cannot silently combine different noise-generator versions")
    points_all = [p for d in datasets for p in d["points"]]
    n = cfg["trials"]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
    floor = 1 / (n * cfg["ncol"] * cfg["periods"]) / 2
    for R, color in ((3, "#386cb0"), (5, "#d95f02")):
        points = sorted((p for p in points_all if p["R"] == R and p["epsilon"] > 0), key=lambda p: p["epsilon"])
        x = np.array([p["epsilon"] for p in points])
        rate = np.array([p["transition_error_rate"] for p in points])
        ci = np.array([p["trial_bootstrap_95"] for p in points])
        positive = rate > 0
        axes[0].plot(x, np.maximum(rate, floor), color=color, alpha=0.5)
        axes[0].errorbar(x[positive], rate[positive],
                         yerr=np.array([rate[positive] - np.maximum(ci[positive, 0], floor),
                                        ci[positive, 1] - rate[positive]]),
                         fmt="o", color=color, capsize=3, label=f"R={R}")
        axes[0].scatter(x[~positive], np.full((~positive).sum(), floor),
                        marker="v", color=color)
        risks = np.array([p["trials_with_error"] / n for p in points])
        limits = np.array([wilson(p["trials_with_error"], n) for p in points])
        axes[1].errorbar(x, risks, yerr=[risks - limits[:, 0], limits[:, 1] - risks],
                         color=color, fmt="o-", capsize=3, label=f"R={R}")
    axes[0].set(xscale="log", yscale="log", xlabel="Physical replacement probability ε",
                ylabel="Decoded transition errors / cell-period",
                title="Mean and 95% ring-bootstrap interval")
    axes[0].text(0.03, 0.96, "▼ zero observed (display floor, not a bound)",
                 transform=axes[0].transAxes, va="top", fontsize=8)
    axes[1].set(xscale="log", xlabel="Physical replacement probability ε",
                ylabel=f"P(ring has any error in {cfg['periods']} periods)",
                title="Independent rings; 95% Wilson interval", ylim=(-0.03, 1.03))
    for ax in axes:
        ax.grid(alpha=0.2); ax.legend()
    fig.suptitle(f"Matched controls: Q={cfg['Q']}, U={cfg['U']}, D=1; "
                 f"{n} rings × {cfg['ncol']} colonies; noise v{noise_version}")
    output = args.output or args.input[0]
    for suffix in (".png", ".pdf"):
        fig.savefig(output.with_suffix(suffix), dpi=160)
    print(output.with_suffix(".png"))


if __name__ == "__main__":
    main()
