"""Finite-size observer comparison, with pointwise ring-level uncertainty."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def wilson(hits, trials, z=1.959963984540054):
    """Two-sided 95% Wilson score interval by default; one independent stratum."""
    hits, trials = np.asarray(hits), np.asarray(trials)
    if np.any(trials <= 0) or np.any(hits < 0) or np.any(hits > trials):
        raise ValueError("invalid binomial counts")
    p = hits / trials
    divisor = 1 + z * z / trials
    center = (p + z * z / (2 * trials)) / divisor
    half = z * np.sqrt(p * (1 - p) / trials + z * z / (4 * trials * trials)) / divisor
    return np.maximum(0, center - half), np.minimum(1, center + half)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    data = json.loads(args.input.read_text())
    epsilons = sorted({r["epsilon"] for r in data["records"]})
    fig, axes = plt.subplots(1, len(epsilons), figsize=(5 * len(epsilons), 4.2),
                             squeeze=False, constrained_layout=True)
    for ax, eps in zip(axes[0], epsilons):
        records = sorted((r for r in data["records"] if r["epsilon"] == eps), key=lambda r:r["ncol"])
        sizes = np.array([r["ncol"] for r in records])
        for observer, color in (("global_ring", "tab:blue"), ("fixed_window", "tab:orange")):
            for bit, marker in ((0, "o"), (1, "s")):
                strata = [next(s for s in r["observers"][observer]["strata"] if s["initial_bit"] == bit)
                           for r in records]
                hits = np.array([s["ever_noncorrect"] for s in strata])
                trials = np.array([s["rings"] for s in strata])
                rate = hits / trials
                lo, hi = wilson(hits, trials)
                # Small multiplicative offsets separate overlapping error bars.
                offset = (1 if observer == "fixed_window" else -1) * .025 + (bit - .5) * .04
                ax.errorbar(sizes * np.exp(offset), rate, yerr=[rate - lo, hi - rate],
                            color=color, marker=marker, linestyle="--" if bit else "-", capsize=3,
                            label=f"{'Whole ring' if observer == 'global_ring' else 'Fixed Q-site window'}, bit {bit}")
        ax.set_xscale("log", base=2)
        ax.set_xticks(sizes, labels=[str(s) for s in sizes])
        ax.set_ylim(-.04, 1.04)
        ax.set_xlabel("Number of physical colonies")
        ax.set_ylabel("Risk of at least one sampled erasure / wrong bit")
        ax.set_title(f"Persistent physical noise ε={eps:g}")
        ax.grid(alpha=.2)
    axes[0, 0].legend(fontsize=7)
    fig.suptitle(f"Local-only phase memory, Q={data['Q']}, {data['steps']:,} steps, sample every {data['sample_every']}\n"
                 f"{data['trials']//2} independent rings per initial bit; pointwise 95% Wilson intervals", fontsize=10)
    fig.savefig(args.input.with_suffix(".png"), dpi=170)
    fig.savefig(args.input.with_suffix(".pdf"))


if __name__ == "__main__":
    main()
