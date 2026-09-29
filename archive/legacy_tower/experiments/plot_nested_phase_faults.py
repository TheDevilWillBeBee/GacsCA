"""Boundary diagnostics for the independent nested-phase fault audit."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def matrices(result):
    records = result["records"]
    fields = ("simage", "simaddr")
    return {
        "Incorrect decoded register values": np.array([[sum(row["fields"].get(k, 0) for k in fields) for row in r["rows"]] for r in records]).T,
        "Incorrect raw track copies": np.array([[row["raw_track_copy_errors"] for row in r["rows"]] for r in records]).T,
        "Incorrect majority-repaired track bits": np.array([[row["repaired_track_errors"] for row in r["rows"]] for r in records]).T,
        "Middle cells differing from clean": np.array([r["ground"]["any_state_cells"] for r in records]).T,
        "Conditional-transition cell mismatches": np.array([r["conditional_transition"]["any_state_cells"] for r in records]).T,
        "Physical Flag2 cells (not excess)": np.array([r["physical_flag2"] for r in records]).T,
    }


def plot(result, output):
    labels = result["identity"]["labels"]
    names = ["clean" if x["target"] == "clean" else f"{x['target']} w{x['width']} / trial {x['trial'] + 1}" for x in labels]
    records = result["records"]
    ticklabels = [f"{r['period']}\nage {r['middle_age']}" for r in records]
    fig, axes = plt.subplots(2, 3, figsize=(13, max(5.4, len(labels) * .48 + 2.5)), constrained_layout=True)
    for ax, (title, values) in zip(axes.flat, matrices(result).items()):
        if values.shape != (len(labels), len(records)) or np.any(values < 0):
            raise ValueError("diagnostics require nonnegative label-by-boundary counts")
        ax.imshow(np.log1p(values), cmap="Blues", vmin=0, vmax=max(1., float(np.log1p(values).max())), aspect="auto")
        for (y, x), value in np.ndenumerate(values):
            white = np.log1p(value) > .55 * max(1., float(np.log1p(values).max()))
            ax.text(x, y, str(int(value)), ha="center", va="center", fontsize=8, color="white" if white else "black")
        ax.set_title(title, fontsize=10)
        ax.set_xticks(np.arange(len(records)), ticklabels)
        ax.set_yticks(np.arange(len(labels)), names, fontsize=8)
        ax.set_xlabel("Outer-period boundary / clean middle age")
    phase = result["identity"]["spec"]["phase"]
    fig.suptitle(f"Physical islands at nested {phase}: exact sampled counts\n"
                 "CPU-prepared starting phase; local physical evolution thereafter; colors are log(1 + count), scaled per panel", fontsize=11)
    for suffix in (".png", ".pdf"):
        path = output.with_suffix(suffix)
        if path.exists(): raise FileExistsError(path)
        fig.savefig(path, dpi=160)
    plt.close(fig)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input", type=Path)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    with args.input.open() as f: result = json.load(f)
    plot(result, args.output)


if __name__ == "__main__":
    main()
