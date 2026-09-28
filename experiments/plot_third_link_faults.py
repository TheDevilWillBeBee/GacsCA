"""Summarize and plot physical-island recovery without treating scratch as payload."""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def recovery_interval(times, counts, fault_stop):
    """Final uninterrupted sampled zero interval; None means right-censored."""
    select = times >= fault_stop
    t, bad = times[select] - fault_stop, counts[select] != 0
    if not len(t): return None
    if bad[-1]: return None
    indices = np.flatnonzero(bad)
    if not len(indices): return [0, int(t[0])]
    last = indices[-1]
    return [int(t[last]), int(t[last + 1])]


def summarize(meta):
    times = np.array([s["step"] for s in meta["samples"]])
    structure = np.array([s["bad_structure"] for s in meta["samples"]])
    labels, U = meta["identity"]["labels"], meta["identity"]["U"]
    rows = []
    for phase in ("early", "late"):
        for width in sorted({s["width"] for s in labels if s["phase"] == phase}):
            indices = [i for i,s in enumerate(labels) if s["phase"] == phase and s["width"] == width]
            stop = 17 if phase == "early" else U - 1
            final = meta["commits"][-1]
            rows.append(dict(phase=phase, width=width, trials=len(indices), batches=indices,
                             final_bad_structure=[meta["samples"][-1]["bad_structure"][i] for i in indices],
                             final_flag2=[meta["samples"][-1]["flag2"][i] for i in indices],
                             final_decoded_error_cells=[final["ground"]["any_state_cells"][i] for i in indices],
                             final_info_bit_errors=[final["ground"]["middle_info_bits"][i] for i in indices],
                             final_conditional_error_cells=[final["conditional_transition"]["any_state_cells"][i] for i in indices],
                             sampled_structure_recovery_intervals=[recovery_interval(times, structure[:, i], stop) for i in indices]))
    return rows


def render(meta, bins, output):
    times = np.array([s["step"] for s in meta["samples"]])
    rows = summarize(meta)
    widths = sorted({r["width"] for r in rows})
    U, Q, L = (meta["identity"][k] for k in ("U", "Q", "physical_cells"))
    fig, axes = plt.subplots(2, len(widths), figsize=(4 * len(widths), 6), squeeze=False)
    for row in rows:
        ax = axes[int(row["phase"] == "late"), widths.index(row["width"])]
        stop = 17 if row["phase"] == "early" else U - 1
        use = times >= stop
        for key, label, color in (("bad_structure", "Address/clock errors", "#0072B2"),
                                   ("flag1", "Flag1 count", "#E69F00"), ("flag2", "Flag2 count", "#CC79A7")):
            values = np.array([s[key] for s in meta["samples"]])[use][:, row["batches"]]
            x = times[use] - stop
            ax.plot(x, values.mean(1), color=color, label=label, marker=".", ms=3)
            ax.fill_between(x, values.min(1), values.max(1), color=color, alpha=.12)
        ax.set(xscale="symlog", yscale="symlog", title=f'{row["phase"]}, width {row["width"]}',
               xlabel="Steps since fault ended", ylabel="Physical cells")
        peak = max(max(s[k][i] for i in row["batches"]) for s in meta["samples"] for k in ("bad_structure", "flag1", "flag2"))
        if peak <= 2: ax.set_yscale("linear")
        ax.set_ylim(bottom=0)
        ax.grid(alpha=.2)
    axes[0, 0].legend(fontsize=8)
    fig.suptitle("Third-link transient islands: trial mean and min–max (not confidence intervals)")
    fig.tight_layout()
    fig.savefig(output.with_name(output.name + "_recovery.png"), dpi=170)
    fig.savefig(output.with_name(output.name + "_recovery.pdf"))
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    for ax, metric, title in zip(axes, ("structural_cells", "middle_info_bits", "any_state_cells"),
                                 ("Decoded structural cells", "Repaired middle Info bits", "Any decoded state/copy error")):
        nperiod = len(meta["commits"])
        for j, commit in enumerate(meta["commits"]):
            series = [np.array(commit["ground"][metric])[r["batches"]] for r in rows]
            mean = np.array([a.mean() for a in series])
            err = np.array([[m-a.min() for m,a in zip(mean, series)], [a.max()-m for m,a in zip(mean, series)]])
            ax.bar(np.arange(len(rows)) + (j - (nperiod - 1) / 2) * .8 / nperiod,
                   mean, width=.8 / nperiod, yerr=err, capsize=2, label=f'period {commit["period"]}')
        ax.set(title=title, yscale="symlog", xticks=np.arange(len(rows)),
               xticklabels=[f'{r["phase"]}\n{r["width"]}' for r in rows])
        peak = max(max(commit["ground"][metric]) for commit in meta["commits"])
        if peak <= 2:
            ax.set_yscale("linear")
            ax.set_ylim(0, max(1, peak) * 1.1)
        else: ax.set_ylim(bottom=0)
        if peak == 0: ax.text(.5, .5, "No observed errors", ha="center", transform=ax.transAxes)
        ax.grid(axis="y", alpha=.2)
    axes[0].legend()
    fig.suptitle("Ground-reference errors; middle Info is not an arbitrary logical-memory observable")
    fig.tight_layout()
    fig.savefig(output.with_name(output.name + "_decoded.png"), dpi=170)
    fig.savefig(output.with_name(output.name + "_decoded.pdf"))
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    center_colony = L // (2 * Q)
    left, right = max(0, (center_colony - 2) * Q // 16), min(L // 16, (center_colony + 3) * Q // 16)
    for ax, phase in zip(axes, ("early", "late")):
        row = next(r for r in rows if r["phase"] == phase and r["width"] == max(widths))
        stop = 17 if phase == "early" else U - 1
        use = (times >= stop) & (times <= stop + 1024)
        image = bins[use][:, row["batches"], left:right].mean(1) / 16
        im = ax.imshow(image, origin="upper", aspect="auto", vmin=0, vmax=1, cmap="magma",
                       extent=(16 * left / Q - center_colony, 16 * right / Q - center_colony, len(image) - .5, -.5))
        ax.set(yticks=np.arange(len(image)), yticklabels=times[use]-stop,
               xlabel="Colony coordinate relative to injected colony", ylabel="Sampled delay (steps)",
               title=f"{phase}, width {max(widths)}")
        for x in (0, 1): ax.axvline(x, color="white", linewidth=.6, alpha=.6)
    fig.colorbar(im, ax=axes, label="Mean fraction of bad Address/clock cells per 16-site bin", shrink=.8)
    fig.suptitle("Sampled spatial recovery (rows are observations, not equally spaced times)")
    fig.savefig(output.with_name(output.name + "_space_time.png"), dpi=170, bbox_inches="tight")
    fig.savefig(output.with_name(output.name + "_space_time.pdf"), bbox_inches="tight")
    plt.close(fig)
    return rows


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input", type=Path)
    p.add_argument("--output", type=Path, required=True, help="new artifact prefix")
    args = p.parse_args()
    paths = [args.output.with_suffix(".json")] + [args.output.with_name(args.output.name + f"_{kind}.{ext}")
              for kind in ("recovery", "decoded", "space_time") for ext in ("png", "pdf")]
    if any(q.exists() for q in paths): p.error("refusing to overwrite analysis or figures")
    with np.load(args.input, allow_pickle=False) as data:
        meta = json.loads(str(data["_metadata"]))
        bins = data["physical_structure_bins"]
    if meta["identity"]["protocol"] != "third-link-physical-islands" or meta["status"] != "complete":
        p.error("requires a complete physical-island experiment")
    rows = render(meta, bins, args.output)
    result = dict(input=str(args.input), input_sha256=hashlib.sha256(args.input.read_bytes()).hexdigest(),
                  script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), rows=rows,
                  scope="small transient-island pilot; sampled recovery bounds, not a noise threshold or logical lifetime")
    with paths[0].open("x") as f: json.dump(result, f, indent=2)
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
