"""Plot source-prescribed active/rest timing versus the current compressed rule."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    data = json.loads(args.input.read_text())
    Q, U = data["parameters"]["Q"], data["parameters"]["U"]
    fig, ax = plt.subplots(figsize=(11, 3.2), constrained_layout=True)
    colors = ["#66c2a5"] * 3 + ["#fc8d62", "#8da0cb"]
    def segment(a, b, y, color, label=None):
        ax.broken_barh([(a / Q, (b - a) / Q)], (y - .24, .48), facecolors=color)
        if label:
            ax.text((a + b) / (2 * Q), y, label, ha="center", va="center", fontsize=8)
    for s, color, name in zip(data["prescribed_stages"], colors, ("G1", "G2", "G3 + flags", "Trickle", "Vote +\ncompute")):
        segment(*s["active"], 1, color, name)
        segment(*s["rest"], 1, "#eeeeee", "Rest")
    segment(0, U, 0, "#eeeeee")
    for i, start in enumerate(data["actual_gather_starts"]):
        segment(start, start + 6 * Q + 2, 0, colors[0], f"G{i+1}")
    segment(*data["actual_compute"], 0, colors[4])
    segment(data["actual_compute"][1], data["actual_trickle"][0], 0, "#e5c494")
    segment(*data["actual_trickle"], 0, colors[3])
    ax.annotate("Compute / signals / trickle", xy=(data["actual_compute"][0] / Q, -.15),
                xytext=(36, -.42), fontsize=8,
                arrowprops=dict(arrowstyle="->", color="#555555"), color="#555555")
    for y in (0, 1):
        ax.scatter([U / Q], [y], marker="|", color="black", s=250)
    witness = data["rest_witness"]["old_age"] / Q
    ax.annotate(f"Clean rest-period write\n{data['rest_witness']['changed_track_cells']} track cells change",
                xy=(witness, .15), xytext=(42, .25), fontsize=9,
                arrowprops=dict(arrowstyle="->", color="#b2182b"), color="#b2182b")
    ax.set(yticks=[0, 1], yticklabels=["Current compiler", "Gray pp.34–35"],
           xticks=list(range(0, 129, 8)), xlabel="Age / Q (U = 128Q)",
           xlim=(-1, 130), ylim=(-.55, 1.55),
           title="Three gathers alone do not implement Gray's temporal isolation")
    ax.text(.99, .98, "Commit at next period boundary; source resets at each stage start",
            transform=ax.transAxes, ha="right", va="top", fontsize=8)
    ax.grid(axis="x", alpha=.15)
    for ext in (".png", ".pdf"):
        fig.savefig(args.input.with_suffix(ext), dpi=170)


if __name__ == "__main__":
    main()
