"""Measure a whole Gray upper-colony trajectory prefix, not a full work period.

Uses exact packed initialization and a genuine encoded upper configuration.
Timing extrapolations are planning estimates, not observed complete runs.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time

import torch

from gacsca.build import make_tower
from gacsca.gpu import field
from gacsca.gpu_engine import CleanGraphRunner
from gacsca.hierarchy import encode_state_info
from experiments.tower_checkpoint import fingerprint


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, default=256)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.steps < 1 or args.output.exists():
        parser.error("need positive steps and a new output path")
    lower, upper = make_tower(Q0=8192, U0=1048576, Q1=8192, U1=1048576,
                              ncol0=8192, R=5, D=1, schedule="gray")
    gpu = lower.gpu_engine()
    upper_initial = upper.np_engine().initial(1)
    info = encode_state_info(upper_initial, lower.L, lower.p.Q)
    torch.cuda.reset_peak_memory_stats()
    state = gpu.initial(1, info)
    del info
    torch.cuda.synchronize()
    begin = time.monotonic()
    runner = CleanGraphRunner(gpu, state, block_steps=16)
    runner.run(args.steps)
    torch.cuda.synchronize()
    elapsed = time.monotonic() - begin
    expected_addr = torch.arange(lower.p.L, device=state.device) % lower.p.Q
    bad = int(((field(runner.state, "addr") != expected_addr) |
               (field(runner.state, "age") != args.steps % lower.p.U)).sum())
    hashes = fingerprint()
    script = Path(__file__)
    hashes[str(script.relative_to(script.parents[1]))] = hashlib.sha256(script.read_bytes()).hexdigest()
    result = dict(physical_cells=lower.p.L, upper_cells=upper.p.L,
                  physical_words_per_cell=gpu.W, lower_period=lower.p.U,
                  upper_period=upper.p.U, measured_steps=args.steps,
                  seconds_including_first_graph_capture=elapsed,
                  seconds_per_step=elapsed / args.steps,
                  estimated_lower_period_hours=elapsed / args.steps * lower.p.U / 3600,
                  estimated_upper_period_years=elapsed / args.steps * lower.p.U * upper.p.U / (365.25 * 86400),
                  peak_torch_allocated_bytes=torch.cuda.max_memory_allocated(),
                  physical_bad_structure=bad, full_period_validated=False,
                  caveat="Prefix timing only; active computation throughput can differ. No simulated transition completed.",
                  gpu=torch.cuda.get_device_name(), torch=torch.__version__, fingerprints=hashes)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2), flush=True)
    if bad:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
