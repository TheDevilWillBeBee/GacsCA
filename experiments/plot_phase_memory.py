"""Plot phase mass and sampled first-failure survival without pooling ring samples."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    data = json.loads(args.input.read_text())
    eps = sorted({r["epsilon"] for r in data["records"]})
    colors = dict(zip(eps, plt.get_cmap("tab10").colors))
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), constrained_layout=True)
    for record in data["records"]:
        t = np.array(record["times"])
        mass = np.asarray(record["original_phase_mass_by_sample_trial"])
        observed = np.asarray(record["observed_bit_by_sample_trial"])
        bad = observed != np.asarray(data["initial_bit_by_trial"])
        survived = ~np.maximum.accumulate(bad, axis=0)
        style = "-" if record["eraser"] == "printed" else "--"
        color = colors[record["epsilon"]]
        label = f"ε={record['epsilon']:g}, {record['eraser']}"
        axes[0].plot(t, mass.mean(1), style, color=color, label=label)
        if record["eraser"] == "printed":
            lo, hi = np.quantile(mass, [.1, .9], axis=1)
            axes[0].fill_between(t, lo, hi, color=color, alpha=.12)
        axes[1].step(t, survived.mean(1), where="post", linestyle=style, color=color, label=label)
    axes[0].axhline(.5, color="gray", linestyle=":", linewidth=1)
    axes[0].set_ylabel("Original Address-phase mass")
    axes[0].set_title("Mean; shaded 10–90% ring range (not CI)")
    axes[1].set_ylabel("Fraction without observed wrong bit / erasure")
    axes[1].set_title("Sampled first-failure survival; right-censored")
    for ax in axes:
        ax.set_xscale("symlog", linthresh=data["sample_every"])
        ax.set_xlabel("Physical steps under persistent iid noise")
        ax.set_xlim(0, data["steps"])
        ax.set_ylim(-.03, 1.03)
        ax.grid(alpha=.2)
    axes[0].legend(fontsize=7)
    fig.suptitle(f"Local phase memory: Q={data['parameters']['Q']}, "
                 f"{data['parameters']['ncol']} colonies, {data['trials']} independent rings/point\n"
                 f"Sample interval {data['sample_every']}; no hierarchy or arbitrary payload", fontsize=10)
    output = args.output or args.input.with_suffix("")
    fig.savefig(output.with_suffix(".png"), dpi=170)
    fig.savefig(output.with_suffix(".pdf"))
    print(output.with_suffix(".png"))


if __name__ == "__main__":
    main()
