"""Finite-size phase memory with paired global and fixed-window observers.

Local-only Gray rules, persistent noise, no simulated repair. Sizes use separate
seeds; the two observers share each trajectory. Sampled failures can recover.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import tarfile
import time

import numpy as np
import torch

from experiments.phase_memory import phase_histogram, observe, first_passage_intervals
from experiments.tower_checkpoint import fingerprint
from gacsca import gpu
from gacsca.params import Params, Variant


def window_histogram(address, Q, start, cells):
    """Histogram in absolute ring coordinates; window does not wrap."""
    if address.ndim != 2 or start < 0 or cells < 1 or start + cells > address.shape[1]:
        raise ValueError("invalid observation window")
    return phase_histogram(address[:, start:start + cells].to(torch.int64) - start, Q)


def summarize(times, observations, bits, horizon):
    observed = np.asarray(observations)
    bits = np.asarray(bits)
    if observed.ndim != 2 or observed.shape[1] != len(bits):
        raise ValueError("need sample by trial outcomes")
    wrong = (observed >= 0) & (observed != bits)
    erased = observed < 0
    bad = wrong | erased
    # Strata remain separate: the two phase encodings need not be symmetric.
    strata = []
    for bit in (0, 1):
        select = bits == bit
        strata.append(dict(initial_bit=bit, rings=int(select.sum()),
                           ever_noncorrect=int(bad[:, select].any(0).sum()),
                           ever_wrong_bit=int(wrong[:, select].any(0).sum()),
                           final_erased=int(erased[-1, select].sum())))
    return dict(first_observed_noncorrect=first_passage_intervals(times, bad, horizon),
                first_observed_wrong_bit=first_passage_intervals(times, wrong, horizon),
                strata=strata, rings_with_observed_erasure=int(erased.any(0).sum()),
                rings_with_observed_wrong_bit=int(wrong.any(0).sum()),
                final_erasure=int(erased[-1].sum()),
                recovered_by_horizon=int((bad.any(0) & ~bad[-1]).sum()))


def archive_sources(path, hashes):
    """Archive precisely the bytes whose hashes appear in the run metadata."""
    root = Path(__file__).resolve().parents[1]
    with tarfile.open(path, "x:gz") as tar:
        for name, expected in hashes.items():
            data = (root / name).read_bytes()
            if hashlib.sha256(data).hexdigest() != expected:
                raise RuntimeError(f"source changed: {name}")
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))


def save_json(path, result):
    temp = path.with_name(path.name + ".tmp")
    with temp.open("x") as stream:
        json.dump(result, stream, separators=(",", ":"), allow_nan=False)
        stream.write("\n")
    temp.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--Q", type=int, default=271)
    parser.add_argument("--ncol", type=int, nargs="+", default=[1, 4, 16])
    parser.add_argument("--trials", type=int, default=64)
    parser.add_argument("--steps", type=int, default=10000)
    parser.add_argument("--sample-every", type=int, default=10)
    parser.add_argument("--epsilon", type=float, nargs="+", default=[.30, .34])
    parser.add_argument("--seed", type=int, default=923)
    args = parser.parse_args()
    archive = args.output.with_name(args.output.stem + "_sources.tar.gz")
    if (args.output.exists() or archive.exists() or args.Q < 2 or
            min(args.ncol + [args.steps, args.sample_every]) < 1 or
            args.trials < 2 or args.trials % 2 or len(set(args.ncol)) != len(args.ncol) or
            any(not 0 <= eps <= 1 for eps in args.epsilon)):
        parser.error("need unused output/archive, positive sizes, valid noise, and an even trial count")
    hashes = fingerprint()
    root = Path(__file__).resolve().parents[1]
    for name in ("experiments/phase_size.py", "experiments/phase_memory.py"):
        hashes[name] = hashlib.sha256((root / name).read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    archive_sources(archive, hashes)
    phases = [0, args.Q // 2]
    bits = torch.arange(args.trials, device="cuda") % 2
    target = bits.cpu().tolist()
    initial_phases = torch.tensor(phases, device="cuda")[bits]
    result = dict(protocol="persistent-local-phase-size", schema=1, Q=args.Q,
                  ncol=args.ncol, trials=args.trials, steps=args.steps,
                  sample_every=args.sample_every, epsilon=args.epsilon,
                  phases=phases, initial_bit_by_trial=target, base_seed=args.seed,
                  seed_rule="base_seed + ncol; same seed across epsilon; no cross-size pairing claim",
                  observer="strict majority in selected phase, else erasure",
                  window="fixed physical sites [0,Q); not moved to follow damaged colonies",
                  pairing="two observers on the same independent ring; do not count observers as trials",
                  noise_version=2, eraser="printed", hierarchy_links=0,
                  replacement="uniform valid local state; Workspace flags forced zero after noise",
                  first_passage_scope="first observed failure; between-sample excursions may be missed",
                  fingerprints=hashes, source_archive=str(archive),
                  gpu=torch.cuda.get_device_name(), torch=torch.__version__, complete=False, records=[])
    save_json(args.output, result)
    started = time.monotonic()
    for ncol in args.ncol:
        p = Params(Q=args.Q, ncol=ncol)
        for eps in args.epsilon:
            engine = gpu.Level0GPU(p, Variant(), seed=args.seed + ncol)
            state = gpu.initial(p, args.trials)
            state[..., 0] = ((torch.arange(p.L, device="cuda") + initial_phases[:, None]) % p.Q).to(torch.uint32)
            out = torch.empty_like(state)
            samples = []
            observations = dict(global_ring=[], fixed_window=[])
            masses = dict(global_ring=[], fixed_window=[])
            for t in range(args.steps + 1):
                if t:
                    engine.step(state, out, t, eps)
                    out[..., 2] = (gpu.flags(out) & 3).to(torch.uint32)
                    state, out = out, state
                if t % args.sample_every == 0 or t == args.steps:
                    samples.append(t)
                    address = gpu.field(state, "addr")
                    for name, cells in (("global_ring", p.L), ("fixed_window", p.Q)):
                        counts = window_histogram(address, p.Q, 0, cells)
                        observations[name].append(observe(counts, phases).cpu().tolist())
                        masses[name].append((counts.gather(1, initial_phases[:, None])[:, 0] / cells).cpu().tolist())
            record = dict(ncol=ncol, cells=p.L, epsilon=eps, seed=args.seed + ncol,
                          U=p.U, times=samples, observers={})
            for name in observations:
                record["observers"][name] = dict(
                    observed_bit_by_sample_trial=observations[name],
                    original_phase_mass_by_sample_trial=masses[name],
                    **summarize(samples, observations[name], target, args.steps))
            # Paired binary ring outcomes, not pooled time observations.
            global_bad = (np.asarray(observations["global_ring"]) != target).any(0)
            window_bad = (np.asarray(observations["fixed_window"]) != target).any(0)
            record["paired_ever_noncorrect"] = [[int(((global_bad == i) & (window_bad == j)).sum())
                                                  for j in (0, 1)] for i in (0, 1)]
            result["records"].append(record)
            result["elapsed_seconds"] = time.monotonic() - started
            save_json(args.output, result)
            print(json.dumps(dict(ncol=ncol, epsilon=eps, paired=record["paired_ever_noncorrect"],
                                  elapsed_seconds=result["elapsed_seconds"])), flush=True)
    result["complete"] = True
    save_json(args.output, result)


if __name__ == "__main__":
    main()
