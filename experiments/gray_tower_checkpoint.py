"""Checkpointed physical Gray tower: one complete lower work period.

One whole Q1=8192 upper colony is represented by 67,108,864 physical cells.
The initial upper state has seeded arbitrary workspace/backup bits and one
damaged Address, at the upper signal-write phase. Every encoded output field
and raw track copy is checked against a direct upper transition. This is one
upper microstep, NOT a complete upper work period or a robustness experiment.
"""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile
import time

import numpy as np
import torch

from gacsca.build import make_tower
from gacsca.checkpoint import load_checkpoint, save_checkpoint
from gacsca.gpu import field
from gacsca.gpu_engine import CleanGraphRunner
from gacsca.hierarchy import encode_state_info, decode_state_info
from experiments.tower_checkpoint import fingerprint, mismatch_counts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--stop-after", type=int)
    parser.add_argument("--chunk", type=int, default=8192)
    parser.add_argument("--seed", type=int, default=921)
    parser.add_argument("--certified-skip", action="store_true")
    parser.add_argument("--fork-from", type=Path,
                        help="explicitly fork an existing checkpoint under the same physical rule; never overwrite it")
    args = parser.parse_args()
    if args.chunk < 1 or (args.stop_after is not None and args.stop_after < 1):
        parser.error("chunk and stop-after must be positive")
    if args.resume and args.fork_from:
        parser.error("fork and resume are distinct operations")
    path = args.output.with_suffix(".npz")
    archive = args.output.with_name(args.output.name + "_sources.tar.gz")
    if not args.resume and (path.exists() or archive.exists()):
        parser.error("refusing to overwrite checkpoint/source archive")
    lower, upper = make_tower(Q0=8192, U0=1048576, Q1=8192, U1=1048576,
                              ncol0=8192, R=5, D=1, schedule="gray")
    gpu = lower.gpu_engine()
    root = Path(__file__).resolve().parents[1]
    hashes = fingerprint()
    hashes[str(Path(__file__).relative_to(root))] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    if args.certified_skip:
        from experiments.quiescent import advance_certified
        skip_source = Path(__file__).with_name("quiescent.py")
        hashes[str(skip_source.relative_to(root))] = hashlib.sha256(skip_source.read_bytes()).hexdigest()
    identity = dict(protocol="whole-colony-gray-transition", schema=2, fingerprints=hashes,
                    seed=args.seed, Q0=lower.p.Q, U0=lower.p.U, Q1=upper.p.Q, U1=upper.p.U,
                    physical_cells=lower.p.L, upper_cells=upper.p.L,
                    upper_age=upper.sched.signal_write, encoded_bits=lower.L.K,
                    flag2_erase="printed", noise=0.0, certified_skip=args.certified_skip)
    fork_arrays, parent = None, None
    if args.fork_from:
        # Keep one file descriptor open while loading and hashing: the parent
        # job may atomically replace its path with a newer checkpoint meanwhile.
        with args.fork_from.open("rb") as source:
            with np.load(source, allow_pickle=False) as data:
                parent = json.loads(str(data["_metadata"]))
                if parent["status"] != "running" or not 0 <= parent["steps"] < lower.p.U:
                    parser.error("fork requires a nonfailed, unfinished parent checkpoint")
                for key, value in identity.items():
                    if key not in ("schema", "fingerprints", "certified_skip") and parent["identity"].get(key) != value:
                        parser.error(f"parent physical configuration differs: {key}")
                for name, digest in parent["identity"]["fingerprints"].items():
                    # Only this driver is allowed to change on an explicit
                    # executor migration. Every rule/backend file must match.
                    if name != str(Path(__file__).relative_to(root)):
                        if not (root / name).is_file() or hashlib.sha256((root / name).read_bytes()).hexdigest() != digest:
                            parser.error(f"parent rule or dependency changed: {name}")
                fork_arrays = {k:data[k].copy() for k in data.files if k != "_metadata"}
            source.seek(0)
            digest = hashlib.sha256()
            while block := source.read(1 << 20):
                digest.update(block)
            parent_hash = digest.hexdigest()
    if args.resume:
        meta, arrays = load_checkpoint(path, identity)
        if meta["status"] == "failed":
            parser.error("retain failed checkpoint for diagnosis; do not resume as success")
        if meta["status"] == "complete":
            print("Already complete; no steps repeated.")
            return
        expected = {k[9:]: v for k, v in arrays.items() if k.startswith("expected_")}
        initial = {k[8:]: v for k, v in arrays.items() if k.startswith("initial_")}
        state = torch.from_numpy(arrays["physical"]).cuda()
        del arrays
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with tarfile.open(archive, "x:gz") as tar:
            for name, digest in hashes.items():
                if hashlib.sha256((root / name).read_bytes()).hexdigest() != digest:
                    raise RuntimeError(f"source changed during archive: {name}")
                tar.add(root / name, arcname=name, recursive=False)
        if fork_arrays is not None:
            initial = {k[8:]:v for k,v in fork_arrays.items() if k.startswith("initial_")}
            expected = {k[9:]:v for k,v in fork_arrays.items() if k.startswith("expected_")}
            for name, value in upper.np_engine().step(initial).items():
                np.testing.assert_array_equal(expected[name], value, err_msg=name)
            state = torch.from_numpy(fork_arrays["physical"]).cuda()
            del fork_arrays
        else:
            initial = upper.np_engine().initial(1)
            initial["age"][:] = upper.sched.signal_write
            rng = np.random.default_rng(args.seed)
            initial["trk"][:] = rng.integers(0, 2, initial["trk"].shape, dtype=np.uint8)
            for name in ("simage", "simaddr"):
                initial[name][:] = rng.integers(0, 65536, initial[name].shape, dtype=np.int32)
            initial["addr"][:, 3] = 100
            expected = upper.np_engine().step(initial)
            info = encode_state_info(initial, lower.L, lower.p.Q)
            state = gpu.initial(1, info)
            del info
        meta = dict(identity=identity, steps=0, status="running", elapsed_seconds=0.0,
                    samples=[], comparison=None, full_upper_period_validated=False,
                    torch=torch.__version__, gpu=torch.cuda.get_device_name(),
                    source_archive=str(archive), source_archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
                    skip_certificates=[], skipped_steps=0)
        if parent is not None:
            meta["steps"] = parent["steps"]
            meta["forked_from"] = dict(path=str(args.fork_from), sha256=parent_hash,
                                       identity=parent["identity"], steps=parent["steps"],
                                       elapsed_seconds=parent["elapsed_seconds"])
    runner = CleanGraphRunner(gpu, state, block_steps=16)
    del state
    started, previous_elapsed = time.monotonic(), meta["elapsed_seconds"]
    ideal = torch.arange(lower.p.L, device=runner.state.device) % lower.p.Q

    def save():
        meta["elapsed_seconds"] = previous_elapsed + time.monotonic() - started
        arrays = dict(physical=runner.state.cpu().numpy())
        arrays.update({"initial_" + k: v for k, v in initial.items()})
        arrays.update({"expected_" + k: v for k, v in expected.items()})
        save_checkpoint(path, meta, arrays)

    if not args.resume:
        save()
    stop = min(lower.p.U, meta["steps"] + (args.stop_after or lower.p.U))
    while meta["steps"] < stop:
        end = min(stop, meta["steps"] + args.chunk)
        if args.certified_skip:
            certificates = []
            advance_certified(runner, end - meta["steps"], certificates)
            meta["skip_certificates"].extend(certificates)
            meta["skipped_steps"] += sum(c["steps"] for c in certificates)
        else:
            runner.run(end - meta["steps"])
        meta["steps"] = end
        bad = int(((field(runner.state, "addr") != ideal) |
                   (field(runner.state, "age") != end % lower.p.U)).sum())
        meta["samples"].append(dict(step=end, physical_bad_structure=bad))
        failed = bool(bad)
        if end == lower.p.U:
            decoded = decode_state_info(gpu.info_bits(runner.state).cpu().numpy(), lower.L, lower.p.Q)
            meta["comparison"] = mismatch_counts(decoded, expected)
            failed |= any(meta["comparison"].values())
        meta["status"] = "failed" if failed else "complete" if end == lower.p.U else "running"
        save()
        print(json.dumps(dict(step=end, target=lower.p.U, status=meta["status"],
                              physical_bad_structure=bad, comparison=meta["comparison"],
                              elapsed_seconds=meta["elapsed_seconds"], skipped_steps=meta["skipped_steps"])), flush=True)
        if failed:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
