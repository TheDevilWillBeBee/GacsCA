"""Plot actual decoded middle-layer states, with explicit checkpoint sampling."""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from gacsca.engine_np import repair
from experiments.third_link_checkpoint import build


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input", type=Path)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    paths = [args.output.with_suffix(ext) for ext in (".png", ".pdf", ".json")]
    if any(q.exists() for q in paths): p.error("refusing to overwrite trace figures")
    with np.load(args.input, allow_pickle=False) as z:
        meta = json.loads(str(z["_metadata"]))
        t = z["period"]
        fields = {k:z["middle_" + k] for k in ("f1", "f2", "wf1", "wf2")}
        values = repair(z["middle_trk"])
        physical_flags = z["physical_flags_nonzero"]
    ident = meta["identity"]["source_identity"]
    outer, middle, _ = build(ident["R"], ident["middle"]["ncol"])
    if len(t) < 2 or not np.all(np.diff(t) > 0): p.error("need increasing sampled periods")
    edges = np.r_[t[0] - (t[1]-t[0])/2, (t[1:]+t[:-1])/2, t[-1] + (t[-1]-t[-2])/2]
    fig = plt.figure(figsize=(12, 9), layout="constrained")
    grid = fig.add_gridspec(3, 2, height_ratios=(1, 1, .65))
    panels = [(fields["f1"], "Middle Flag1"), (fields["f2"], "Middle Flag2"),
              (values[..., middle.T["INFO"]], "Middle Info (majority-repaired)"),
              (values[..., middle.T["HOLD"]], "Middle HOLD (working output)")]
    for i, (bits, label) in enumerate(panels):
        ax = fig.add_subplot(grid[i // 2, i % 2])
        ax.pcolormesh(np.arange(middle.p.L + 1), edges, bits, vmin=0, vmax=1,
                      cmap="Greys", shading="flat", rasterized=True)
        ax.set(xlabel="Middle cell", ylabel="Middle transitions (= outer periods)", title=label)
        ax.set_ylim(t[-1], t[0])
        ax.axhline(middle.sched.compute_end, color="#0072B2", lw=.6, alpha=.7)
    ax = fig.add_subplot(grid[2, :])
    ax.plot(t, physical_flags / outer.p.L, label="Physical cells with any flag", color="#CC79A7")
    ax.plot(t, fields["f1"].mean(1), label="Middle Flag1 fraction", color="#E69F00")
    ax.plot(t, fields["f2"].mean(1), label="Middle Flag2 fraction", color="#009E73")
    ax.axvspan(*middle.sched.trickle, color="gray", alpha=.12, label="Middle trickle interval")
    ax.set(xlabel="Middle transitions", ylabel="Cell fraction", ylim=(0, 1))
    ax.legend(fontsize=8, ncol=4)
    ax.grid(alpha=.2)
    fig.suptitle(f"Physical third link: {len(t)} actual checkpoint samples, periods {t[0]}–{t[-1]}\n"
                 "No injected noise; one periodic top cell. Blue lines: middle computation ends.")
    fig.savefig(paths[0], dpi=170)
    fig.savefig(paths[1])
    plt.close(fig)
    result = dict(input=str(args.input), input_sha256=hashlib.sha256(args.input.read_bytes()).hexdigest(),
                  samples=len(t), first_period=int(t[0]), last_period=int(t[-1]),
                  sampling_gaps=np.unique(np.diff(t)).tolist(),
                  max_physical_flag_fraction=float((physical_flags / outer.p.L).max()),
                  script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  scope="observed middle-state frames only; no reconstruction of unsampled times; any flag includes Workspace flags")
    with paths[2].open("x") as f: json.dump(result, f, indent=2)
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
