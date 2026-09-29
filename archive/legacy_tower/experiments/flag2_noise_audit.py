"""Paired D8-variant audit of Masumori's 500-noisy/500-clean protocol.

This compares candidate rules, NOT published replication. Each ring has the
same counter-generated fault locations/replacements across erasure variants.
Workspace flags are excluded, matching the local-only model. Both valid-field
and full-bit-width replacements are measured because Q=271 is not a power of 2.
"""
import argparse
from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path
import time

import numpy as np
import torch

from gacsca import gpu
from gacsca.params import Params, Variant
from experiments.tower_checkpoint import fingerprint


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--trials", type=int, default=128)
    parser.add_argument("--seed", type=int, default=920)
    args = parser.parse_args()
    if args.trials < 2 or args.output.exists():
        parser.error("need >=2 trials and a new output path")
    p = Params(Q=271, ncol=4)
    hashes = fingerprint()
    script = Path(__file__)
    hashes[str(script.relative_to(script.parents[1]))] = hashlib.sha256(script.read_bytes()).hexdigest()
    result = dict(parameters=asdict(p), trials=args.trials, seed=args.seed,
                  noisy_steps=500, clean_steps=500, workspace_noise=False, noise_version=2,
                  fingerprints=hashes, complete=False, records=[], comparisons=[],
                  gpu=torch.cuda.get_device_name(), torch=torch.__version__)
    started = time.monotonic()
    initial_addr = torch.arange(p.L, device="cuda") % p.Q
    for base_name, base in (("gray", Variant.gray()), ("masumori", Variant.masumori())):
        for replacement in ("valid", "bits"):
            for epsilon in (.4, .5, .6):
                baseline = None
                for eraser in ("printed", "no_ones", "at_most_one"):
                    variant = replace(base, flag2_healthy_erase=eraser)
                    engine = gpu.Level0GPU(p, variant, seed=args.seed, addr_mode=replacement)
                    state = gpu.initial(p, args.trials)
                    out = torch.empty_like(state)
                    for t in range(1, 1001):
                        engine.step(state, out, t, epsilon if t <= 500 else 0)
                        out[..., 2] = (gpu.flags(out) & 3).to(torch.uint32)
                        state, out = out, state
                    address = gpu.field(state, "addr")
                    age = gpu.field(state, "age")
                    offset = (address - initial_addr) % p.Q
                    original = (offset == 0).all(1).cpu().numpy()
                    ordered = (offset == offset[:, :1]).all(1)
                    full_structure = ((address == initial_addr) & (age == 1000)).all(1)
                    record = dict(base=base_name, variant=asdict(variant), replacement=replacement,
                                  epsilon=epsilon, original_phase=int(original.sum()),
                                  any_phase=int(ordered.sum()), full_structure=int(full_structure.sum()),
                                  original_by_trial=original.tolist(),
                                  final_phase_by_trial=torch.where(ordered, offset[:, 0], -1).cpu().tolist(),
                                  residual_flag1_by_trial=gpu.field(state, "f1").sum(1).cpu().tolist(),
                                  residual_flag2_by_trial=gpu.field(state, "f2").sum(1).cpu().tolist())
                    result["records"].append(record)
                    if baseline is None:
                        baseline = original
                    else:
                        delta = original.astype(float) - baseline.astype(float)
                        rng = np.random.default_rng(args.seed)
                        bootstrap = rng.choice(delta, (4000, args.trials), replace=True).mean(1)
                        result["comparisons"].append(dict(base=base_name, replacement=replacement,
                            epsilon=epsilon, eraser=eraser, paired_original_phase_difference=float(delta.mean()),
                            paired_ring_bootstrap_95=np.quantile(bootstrap, [.025, .975]).tolist()))
                    result["elapsed_seconds"] = time.monotonic() - started
                    args.output.parent.mkdir(parents=True, exist_ok=True)
                    args.output.write_text(json.dumps(result, indent=2) + "\n")
                    print(base_name, replacement, epsilon, eraser,
                          'original',record['original_phase'],'any',record['any_phase'],flush=True)
    result["complete"] = True
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
