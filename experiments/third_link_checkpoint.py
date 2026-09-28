"""Checkpointed physical third-link execution; every middle transition checked.

Default: one whole middle colony, hence ONE top cell with periodic aliasing.
Use --middle-colonies 64 for a whole top colony in these reduced geometries.
No reference state is ever installed in the running physical automaton.
"""
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import time

import numpy as np
import torch

from gacsca.build import make_tower, make_simulation_layer
from gacsca.checkpoint import save_checkpoint, load_checkpoint
from gacsca.engine_np import redistribute, repair
from gacsca.gpu import field
from gacsca.gpu_engine import CleanGraphRunner
from gacsca.hierarchy import encode_state_info, decode_state_info
from experiments.phase_size import archive_sources
from experiments.quiescent import advance_certified
from experiments.tower_checkpoint import fingerprint, mismatch_counts


def build(R, middle_colonies):
    if R not in (3, 5) or middle_colonies < 1 or (middle_colonies > 64 and middle_colonies % 64):
        raise ValueError("R must be 3 or 5; middle-colonies must be 1..64 or a multiple of 64")
    kw = dict(R=R, D=3 if R == 3 else 1, Q0=256 if R == 3 else 512,
              U0=16384 if R == 3 else 32768, U1=8192 if R == 3 else 16384)
    middle, top = make_tower(ncol0=middle_colonies, full_registers=True, **kw)
    Q, U = (256, 16384) if R == 3 else (512, 32768)
    return make_simulation_layer(middle, Q=Q, U=U), middle, top


def run(args):
    if args.checkpoint_every < 1 or args.graph_block < 1:
        raise ValueError("checkpoint-every and graph-block must be positive")
    if any(x is not None and x < 1 for x in (args.periods, args.stop_after)):
        raise ValueError("periods and stop-after must be positive")
    outer, middle, top = build(args.R, args.middle_colonies)
    gpu, direct = outer.gpu_engine(), middle.np_engine()
    target = args.periods or middle.p.U
    path = args.output.with_suffix(".npz")
    archive = args.output.with_name(args.output.name + "_sources.tar.gz")
    if not args.resume and (path.exists() or archive.exists()):
        raise FileExistsError("refusing to overwrite an existing checkpoint or archive")
    hashes = fingerprint()
    for name in (__file__, "experiments/quiescent.py", "experiments/phase_size.py"):
        source = Path(name).resolve()
        relative = str(source.relative_to(Path(__file__).resolve().parents[1]))
        hashes[relative] = hashlib.sha256(source.read_bytes()).hexdigest()
    identity = dict(schema=1, experiment="finite_third_link", R=args.R,
                    outer=asdict(outer.p), middle=asdict(middle.p), top=asdict(top.p),
                    target_middle_transitions=target, seed=args.seed, noise=0.0,
                    full_registers_all_layers=True,
                    certified_skip=args.certified_skip, fingerprints=hashes)
    if args.resume:
        meta, arrays = load_checkpoint(path, identity)
        if meta["status"] == "failed":
            raise ValueError("failed checkpoint is retained for diagnosis; cannot resume as success")
        if meta["status"] == "complete":
            print("Already complete; no steps repeated.", flush=True)
            return meta
        reference = {k[7:]:v for k,v in arrays.items() if k.startswith("middle_")}
        top_reference = {k[4:]:v for k,v in arrays.items() if k.startswith("top_")}
        state = torch.from_numpy(arrays["physical"]).cuda()
        if hashlib.sha256(archive.read_bytes()).hexdigest() != meta["source_archive_sha256"]:
            raise ValueError("source archive hash mismatch")
        del arrays
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        archive_sources(archive, hashes)
        n = args.middle_colonies
        top_reference = {k:v[:, :n].copy() for k,v in top.np_engine().initial(1).items()}
        assert top_reference["addr"].shape == (1, n)
        top_reference["addr"][:] = (5 + np.arange(n)) % top.p.Q
        top_reference["age"][:] = next(o.t0 for o in top.prog.ops if o.kind == "BITOP")
        top_reference["f1"][:] = np.arange(n) % 2
        top_reference["f2"][:] = (np.arange(n) + 1) % 2
        rng = np.random.default_rng(args.seed)
        for name in ("simage", "simaddr"):
            top_reference[name][:] = rng.integers(0, 65536, (1, n), dtype=np.int32)
        top_reference["trk"] = redistribute(rng.integers(0, 2, (1, n, top.T.NT), dtype=np.uint8), args.R)
        reference = direct.initial(1, info_bits=encode_state_info(top_reference, middle.L, middle.p.Q))
        physical = outer.np_engine().initial(1, info_bits=encode_state_info(reference, outer.L, outer.p.Q))
        state = gpu.to_gpu(physical)
        del physical
        meta = dict(identity=identity, status="running", completed_periods=0, physical_steps=0,
                    elapsed_seconds=0.0, log=[], top_checks=[], skipped_steps=0, certificates=0,
                    top_cells=n, top_neighborhood_aliasing=n < 11,
                    whole_top_colonies=n % top.p.Q == 0,
                    source_archive=str(archive), source_archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
                    gpu=torch.cuda.get_device_name(), graph_block=args.graph_block)
    runner = CleanGraphRunner(gpu, state, args.graph_block)
    start_period = meta["completed_periods"]
    stop = min(target, start_period + (args.stop_after or target))
    started, elapsed_before = time.monotonic(), meta["elapsed_seconds"]
    ideal = torch.arange(outer.p.L, device=state.device) % outer.p.Q

    def save():
        meta["elapsed_seconds"] = elapsed_before + time.monotonic() - started
        arrays = dict(physical=runner.state.cpu().numpy())
        arrays.update({"middle_" + k:v for k,v in reference.items()})
        arrays.update({"top_" + k:v for k,v in top_reference.items()})
        save_checkpoint(path, meta, arrays)

    if not args.resume: save()
    for period in range(start_period + 1, stop + 1):
        certificates = []
        if args.certified_skip: advance_certified(runner, outer.p.U, certificates)
        else: runner.run(outer.p.U)
        reference = direct.step(reference)
        decoded = decode_state_info(gpu.info_bits(runner.state).cpu().numpy(), outer.L, outer.p.Q)
        counts = mismatch_counts(decoded, reference)
        bad_structure = int(((field(runner.state, "addr") != ideal) | (field(runner.state, "age") != 0)).sum().item())
        failed = any(counts.values()) or bad_structure > 0
        meta["log"].append(dict(period=period, middle_mismatches=counts, physical_bad_structure=bad_structure))
        meta["skipped_steps"] += sum(c["steps"] for c in certificates)
        meta["certificates"] += len(certificates)
        if period % middle.p.U == 0:
            top_reference = top.np_engine().step(top_reference)
            def decode_top(s):
                return decode_state_info(repair(s["trk"])[..., middle.T["INFO"]], middle.L, middle.p.Q)
            check = dict(period=period, physical=mismatch_counts(decode_top(decoded), top_reference),
                         direct=mismatch_counts(decode_top(reference), top_reference))
            meta["top_checks"].append(check)
            failed |= any(check["physical"].values()) or any(check["direct"].values())
        meta["completed_periods"], meta["physical_steps"] = period, period * outer.p.U
        meta["status"] = "failed" if failed else "complete" if period == target else "running"
        if failed or period == stop or period % args.checkpoint_every == 0:
            save()
            print(json.dumps(dict(period=period, target=target, status=meta["status"],
                                  middle_mismatches=sum(counts.values()), physical_bad_structure=bad_structure,
                                  skipped_steps=meta["skipped_steps"], elapsed_seconds=round(meta["elapsed_seconds"], 2))), flush=True)
        if failed: raise RuntimeError("third-link validation failed; exact checkpoint retained")
    return meta


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--R", type=int, choices=(3, 5), default=3)
    p.add_argument("--middle-colonies", type=int, default=1)
    p.add_argument("--periods", type=int)
    p.add_argument("--stop-after", type=int)
    p.add_argument("--checkpoint-every", type=int, default=8)
    p.add_argument("--graph-block", type=int, default=256)
    p.add_argument("--seed", type=int, default=1350)
    p.add_argument("--certified-skip", action="store_true")
    p.add_argument("--resume", action="store_true")
    p.add_argument("--output", type=Path, required=True)
    run(p.parse_args())


if __name__ == "__main__":
    main()
