"""Persistent-noise Gray phase-memory pilot, with erasures and censoring.

Gray pp.15–16 remembers Address phase, not arbitrary per-site payload. The
observer selects one of two initial phases only if it occupies a strict
majority of the ring; otherwise it reports an erasure. Sampled first failures
are interval-censored. These local-only runs have no simulated repair layer.
"""
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import time

import numpy as np
import torch

from gacsca import gpu
from gacsca.params import Params, Variant
from experiments.tower_checkpoint import fingerprint


def phase_histogram(address, Q):
    if address.ndim != 2 or Q < 2:
        raise ValueError("need a batch of rings and Q >= 2")
    offsets = (address.to(torch.int64) - torch.arange(address.shape[1], device=address.device)) % Q
    counts = torch.zeros((address.shape[0], Q), dtype=torch.int64, device=address.device)
    counts.scatter_add_(1, offsets, torch.ones_like(offsets))
    return counts


def observe(counts, phases):
    """Return 0/1 for strict-majority phase, -1 for erasure (including ties)."""
    if len(phases) != 2 or phases[0] == phases[1] or min(phases) < 0 or max(phases) >= counts.shape[1]:
        raise ValueError("need two distinct valid phases")
    votes = counts[:, list(phases)]
    mass, which = votes.max(1)
    return torch.where(2 * mass > counts.sum(1), which, -1)


def first_passage_intervals(samples, flags, horizon):
    """[last earlier sample, first positive sample], or right-censored at horizon.

    A failure may occur and recover between samples; these intervals locate
    the first *observed* failure, not necessarily the first physical failure.
    """
    times = np.asarray(samples)
    flags = np.asarray(flags, dtype=bool)
    if (flags.ndim != 2 or len(times) != len(flags) or len(times) < 2 or
            times[0] != 0 or np.any(np.diff(times) <= 0) or times[-1] != horizon or flags[0].any()):
        raise ValueError("need ordered samples covering [0, horizon] with a nonfailed initial observation")
    rows = []
    for trial in range(flags.shape[1]):
        hits = np.flatnonzero(flags[:, trial])
        if len(hits):
            i = int(hits[0])
            rows.append(dict(observed=True, lower=int(times[i - 1]), upper=int(times[i])))
        else:
            rows.append(dict(observed=False, lower=int(horizon), upper=None))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--Q", type=int, default=271)
    parser.add_argument("--ncol", type=int, default=4)
    parser.add_argument("--trials", type=int, default=64)
    parser.add_argument("--steps", type=int, default=1000)
    parser.add_argument("--sample-every", type=int, default=10)
    parser.add_argument("--epsilon", type=float, nargs="+", default=[.2, .4])
    parser.add_argument("--seed", type=int, default=922)
    args = parser.parse_args()
    if (args.output.exists() or min(args.ncol, args.steps, args.sample_every) < 1 or
            args.trials < 2 or args.trials % 2 or args.Q < 2 or
            any(not 0 <= e <= 1 for e in args.epsilon)):
        parser.error("need a new output, valid parameters, and an even trial count")
    p = Params(Q=args.Q, ncol=args.ncol)
    phases = [0, p.Q // 2]
    bits = torch.arange(args.trials, device="cuda") % 2
    initial_phases = torch.tensor(phases, device="cuda")[bits]
    hashes = fingerprint()
    script = Path(__file__)
    hashes[str(script.relative_to(script.parents[1]))] = hashlib.sha256(script.read_bytes()).hexdigest()
    result = dict(protocol="persistent-local-phase-memory", parameters=asdict(p), phases=phases,
                  observer="strict majority of ring in one selected phase, else erasure",
                  trials=args.trials, initial_bit_by_trial=bits.cpu().tolist(),
                  steps=args.steps, sample_every=args.sample_every, noise_version=2, seed=args.seed,
                  replacement="uniform valid whole local state; Workspace flags forced zero after noise",
                  pairing="same counter draws across erasers at each epsilon; rings are independent units",
                  first_passage_scope="first observed failure; unsampled transient failures can be missed",
                  hierarchy_links=0, complete=False, records=[], fingerprints=hashes,
                  gpu=torch.cuda.get_device_name(), torch=torch.__version__)
    start = time.monotonic()
    for eps in args.epsilon:
        for eraser in ("printed", "at_most_one"):
            engine = gpu.Level0GPU(p, Variant(flag2_healthy_erase=eraser), seed=args.seed)
            state = gpu.initial(p, args.trials)
            state[..., 0] = ((torch.arange(p.L, device="cuda") + initial_phases[:, None]) % p.Q).to(torch.uint32)
            out = torch.empty_like(state)
            times, observations, original_mass = [], [], []
            for t in range(args.steps + 1):
                if t:
                    engine.step(state, out, t, eps)
                    out[..., 2] = (gpu.flags(out) & 3).to(torch.uint32)
                    state, out = out, state
                if t % args.sample_every == 0 or t == args.steps:
                    counts = phase_histogram(gpu.field(state, "addr"), p.Q)
                    times.append(t)
                    observations.append(observe(counts, phases).cpu().numpy())
                    original_mass.append((counts.gather(1, initial_phases[:, None])[:, 0] / p.L).cpu().tolist())
            observed = np.asarray(observations)
            target = bits.cpu().numpy()
            wrong = (observed >= 0) & (observed != target)
            erasures = observed < 0
            record = dict(epsilon=eps, eraser=eraser, times=times,
                          observed_bit_by_sample_trial=observed.tolist(),
                          original_phase_mass_by_sample_trial=original_mass,
                          final_phase_histogram=counts.cpu().tolist(),
                          first_observed_noncorrect=first_passage_intervals(times, wrong | erasures, args.steps),
                          first_observed_wrong_bit=first_passage_intervals(times, wrong, args.steps),
                          rings_with_observed_wrong_bit=int(wrong.any(0).sum()),
                          rings_with_observed_erasure=int(erasures.any(0).sum()),
                          final_wrong_bit=int(wrong[-1].sum()), final_erasure=int(erasures[-1].sum()))
            result["records"].append(record)
            result["elapsed_seconds"] = time.monotonic() - start
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(result, indent=2) + "\n")
            print(json.dumps({k:record[k] for k in ("epsilon", "eraser", "rings_with_observed_wrong_bit", "rings_with_observed_erasure", "final_wrong_bit", "final_erasure")}), flush=True)
    result["complete"] = True
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
