"""Exact replay and space-time capture of one recorded finite-size trajectory.

Every sampled observation and phase mass for every ring, under both observers,
must match the archived experiment. Only the selected ring's images are stored.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import torch

from experiments.phase_memory import observe
from experiments.phase_size import window_histogram
from gacsca import gpu
from gacsca.checkpoint import save_checkpoint
from gacsca.params import Params, Variant


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--ncol", type=int, default=16)
    parser.add_argument("--epsilon", type=float, default=.30)
    parser.add_argument("--trial", type=int, default=105)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("refusing to overwrite a replay")
    source_bytes = args.input.read_bytes()
    data = json.loads(source_bytes)
    if not data["complete"] or not 0 <= args.trial < data["trials"]:
        parser.error("need a completed source and valid trial")
    root = Path(__file__).resolve().parents[1]
    for name, expected in data["fingerprints"].items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != expected:
            raise RuntimeError(f"source changed; replay requires archived environment: {name}")
    points = [r for r in data["records"] if r["ncol"] == args.ncol and r["epsilon"] == args.epsilon]
    if len(points) != 1:
        parser.error("need exactly one matching recorded point")
    record = points[0]
    p = Params(Q=data["Q"], U=record["U"], ncol=args.ncol)
    engine = gpu.Level0GPU(p, Variant(), seed=record["seed"], noise_version=data["noise_version"])
    bits = torch.tensor(data["initial_bit_by_trial"], device="cuda")
    phases = data["phases"]
    initial_phases = torch.tensor(phases, device="cuda")[bits]
    state = gpu.initial(p, data["trials"])
    state[..., 0] = ((torch.arange(p.L, device="cuda") + initial_phases[:, None]) % p.Q).to(torch.uint32)
    out = torch.empty_like(state)
    offsets, flag_frames, age_errors, histograms = [], [], [], []
    sample = 0
    sample_times = record["times"]
    for t in range(data["steps"] + 1):
        if t:
            engine.step(state, out, t, record["epsilon"])
            out[..., 2] = (gpu.flags(out) & 3).to(torch.uint32)
            state, out = out, state
        if sample < len(sample_times) and t == sample_times[sample]:
            address = gpu.field(state, "addr")
            pair = []
            for name, cells in (("global_ring", p.L), ("fixed_window", p.Q)):
                counts = window_histogram(address, p.Q, 0, cells)
                actual = observe(counts, phases).cpu().numpy()
                mass = (counts.gather(1, initial_phases[:, None])[:, 0] / cells).cpu().numpy()
                expected = record["observers"][name]
                np.testing.assert_array_equal(actual, expected["observed_bit_by_sample_trial"][sample])
                np.testing.assert_array_equal(mass, expected["original_phase_mass_by_sample_trial"][sample])
                pair.append(counts[args.trial].cpu().numpy())
            histograms.append(pair)
            offsets.append(((address[args.trial].to(torch.int64) - torch.arange(p.L, device="cuda")) % p.Q).cpu().numpy())
            flag_frames.append(gpu.flags(state)[args.trial].cpu().numpy())
            age_errors.append((gpu.field(state, "age")[args.trial] != t % p.U).cpu().numpy())
            sample += 1
    assert sample == len(sample_times)
    meta = dict(protocol="exact-phase-excursion-replay", complete=True, input=str(args.input),
                input_sha256=hashlib.sha256(source_bytes).hexdigest(),
                script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                fingerprints=data["fingerprints"], trial=args.trial, Q=p.Q, U=p.U, ncol=p.ncol,
                epsilon=record["epsilon"], seed=record["seed"], initial_bit=int(bits[args.trial]),
                phases=phases, hierarchy_links=0, observers=["global_ring", "fixed_window"],
                replay_checks="all sampled observer outputs and original phase masses, every ring and both observers",
                checked_observer_outputs=sample * data["trials"] * 2)
    save_checkpoint(args.output, meta, dict(times=np.asarray(sample_times),
                    phase_offsets=np.asarray(offsets, dtype=np.uint16),
                    flags=np.asarray(flag_frames, dtype=np.uint8),
                    age_errors=np.asarray(age_errors, dtype=bool),
                    phase_histograms=np.asarray(histograms, dtype=np.int32)))
    print(json.dumps(meta), flush=True)


if __name__ == "__main__":
    main()
