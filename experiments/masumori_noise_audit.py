"""Distinguish field noise and workspace participation in Masumori Fig.7.

Also separate original-phase memory from recovery to any uniformly shifted
address pattern. This is a protocol audit, not a claim of published replication.
"""
import argparse
import json
from pathlib import Path

import torch

from gacsca.params import Params, Variant
from gacsca import gpu


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("figs/masumori_noise_audit_20260920.json"))
    args = parser.parse_args()
    if args.output.exists():
        parser.error("refusing to overwrite existing results")
    p = Params(Q=271, ncol=4)
    B, seed = 128, 920
    records = []
    for vname, variant in (("gray", Variant.gray()), ("masumori", Variant.masumori())):
        for mode in ("valid", "bits"):
            for use_wf in (True, False):
                for epsilon in (0.4, 0.5, 0.6):
                    engine = gpu.Level0GPU(p, variant, seed=seed, addr_mode=mode)
                    state = gpu.initial(p, B)
                    buf = torch.empty_like(state)
                    for t in range(1, 1001):
                        engine.step(state, buf, t, epsilon if t <= 500 else 0)
                        if not use_wf:
                            buf[..., 2] = (gpu.flags(buf) & 3).to(torch.uint32)
                        state, buf = buf, state
                    offset = (gpu.field(state, "addr") - torch.arange(p.L, device=state.device)) % p.Q
                    original = (offset == 0).all(1)
                    ordered = (offset == offset[:, :1]).all(1)
                    age = gpu.field(state, "age")
                    synchronized = (age == age[:, :1]).all(1)
                    rec = dict(variant=vname, replacement=mode, workspace_noise=use_wf, epsilon=epsilon,
                               original_phase=int(original.sum()), any_uniform_phase=int(ordered.sum()),
                               ordered_and_synchronized=int((ordered & synchronized).sum()),
                               final_phase_by_trial=torch.where(ordered, offset[:, 0], -1).cpu().tolist())
                    records.append(rec)
                    print(vname, mode, "noisy-WF", use_wf, "eps", epsilon,
                          "original", rec["original_phase"], "any-phase", rec["any_uniform_phase"], flush=True)
    args.output.write_text(json.dumps(dict(Q=p.Q, U=p.U, ncol=p.ncol, trials=B,
                                           noisy_steps=500, clean_steps=500, seed=seed, records=records), indent=2) + "\n")


if __name__ == "__main__":
    main()
