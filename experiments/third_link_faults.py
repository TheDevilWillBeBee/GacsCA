"""Transient physical islands from an immutable, verified third-link checkpoint.

Whole-cell replacement is applied after one local transition using noise v2.
The study measures physical structure/flags and decoded middle fields, not
arbitrary logical memory or asymptotic hierarchy-depth robustness.
"""
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import time

import numpy as np
import torch

from gacsca.checkpoint import save_checkpoint, load_checkpoint
from gacsca.engine_np import repair
from gacsca.gpu import field
from gacsca.gpu_engine import CleanGraphRunner
from gacsca.hierarchy import decode_state_info
from experiments.gray_faults import FaultBox, advance
from experiments.phase_size import archive_sources
from experiments.third_link_checkpoint import build
from experiments.tower_checkpoint import fingerprint
from experiments.verify_third_link_checkpoint import audit


def scenarios(outer, base, widths, trials):
    if trials < 1 or not widths or any(w < 1 or w > outer.p.Q for w in widths):
        raise ValueError("trials must be positive and island widths must fit one physical colony")
    center = outer.p.L // 2 + outer.p.Q // 2
    labels = [dict(phase="clean", width=0, trial=0)]
    boxes = []
    for phase, relative in (("early", 16), ("late", outer.p.U - 2)):
        for width in widths:
            for trial in range(trials):
                batch = len(labels)
                labels.append(dict(phase=phase, width=width, trial=trial))
                left = center - width // 2
                boxes.append(FaultBox(batch, base + relative, base + relative + 1, left, left + width))
    return labels, boxes


def decoded_metrics(decoded, reference, T):
    axes = lambda a:tuple(range(1, a.ndim))
    fields = {k:np.count_nonzero(decoded[k] != v, axis=axes(decoded[k])).tolist() for k,v in reference.items()}
    cells = np.zeros_like(decoded["addr"], dtype=bool)
    structural = np.zeros_like(cells)
    for k,v in reference.items():
        bad = decoded[k] != v
        if k == "trk": bad = bad.any(axis=(2, 3))
        cells |= bad
        if k in ("addr", "age", "f1", "f2", "wf1", "wf2"): structural |= bad
    info = repair(decoded["trk"])[..., T["INFO"]]
    expected_info = repair(reference["trk"])[..., T["INFO"]]
    return dict(fields=fields, any_state_cells=cells.sum(1).tolist(),
                structural_cells=structural.sum(1).tolist(),
                middle_info_bits=(info != expected_info).sum(1).tolist())


def run(args):
    if args.periods < 1 or args.chunk < 1: raise ValueError("periods and chunk must be positive")
    origin_check = audit(args.input)
    if not origin_check["passed"]: raise ValueError("origin checkpoint did not pass independent audit")
    with args.input.open("rb") as source:
        with np.load(source, allow_pickle=False) as data:
            origin_meta = json.loads(str(data["_metadata"]))
            origin = data["physical"]
            ground = {k[7:]:data[k] for k in data.files if k.startswith("middle_")}
        source.seek(0)
        digest = hashlib.sha256()
        while block := source.read(1 << 20): digest.update(block)
    if digest.hexdigest() != origin_check["input_sha256"]:
        raise ValueError("origin changed during loading; use an immutable snapshot")
    outer, middle, _ = build(origin_meta["identity"]["R"], origin_meta["top_cells"])
    base, Q, U = origin_meta["physical_steps"], outer.p.Q, outer.p.U
    labels, boxes = scenarios(outer, base, args.widths, args.trials)
    B = len(labels)
    gpu, direct = outer.gpu_engine(seed=args.seed, noise_version=2), middle.np_engine()
    hashes = fingerprint()
    root = Path(__file__).resolve().parents[1]
    for name in (__file__, "experiments/gray_faults.py", "experiments/phase_size.py",
                 "experiments/third_link_checkpoint.py", "experiments/verify_third_link_checkpoint.py"):
        p = Path(name).resolve()
        hashes[str(p.relative_to(root))] = hashlib.sha256(p.read_bytes()).hexdigest()
    identity = dict(schema=1, protocol="third-link-physical-islands", fingerprints=hashes,
                    source=str(args.input), source_sha256=digest.hexdigest(), origin_period=origin_meta["completed_periods"],
                    seed=args.seed, noise_version=2, periods=args.periods, chunk=args.chunk,
                    labels=labels, boxes=[asdict(b) for b in boxes], Q=Q, U=U, R=outer.T.R,
                    physical_cells=outer.p.L, middle_cells=middle.p.L,
                    flag2_rule="printed", top_cells=origin_meta["top_cells"],
                    top_neighborhood_aliasing=origin_meta["top_neighborhood_aliasing"])
    path = args.output.with_suffix(".npz")
    archive = args.output.with_name(args.output.name + "_sources.tar.gz")
    if args.resume:
        meta, arrays = load_checkpoint(path, identity)
        if hashlib.sha256(archive.read_bytes()).hexdigest() != meta["source_archive_sha256"]:
            raise ValueError("source archive hash mismatch")
        if meta["status"] == "failed": raise ValueError("failed control run must be diagnosed")
        if meta["status"] == "complete": return meta
        state = torch.from_numpy(arrays["physical"]).cuda()
        ground = {k[7:]:v for k,v in arrays.items() if k.startswith("ground_")}
        previous = {k[9:]:v for k,v in arrays.items() if k.startswith("previous_")}
        traces = list(arrays["physical_structure_bins"])
    else:
        if path.exists() or archive.exists(): raise FileExistsError("existing result requires --resume")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        archive_sources(archive, hashes)
        state = torch.from_numpy(origin).cuda().repeat(B, 1, 1)
        previous = {k:np.repeat(v, B, axis=0) for k,v in ground.items()}
        meta = dict(identity=identity, steps=0, status="running", samples=[], commits=[],
                    elapsed_seconds=0.0, origin_audit=origin_check,
                    source_archive=str(archive), source_archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
                    scope="whole-cell one-step transient islands; decoded middle state and structural recovery, not logical memory")
        traces = []
    runner = CleanGraphRunner(gpu, state)
    noise = torch.empty_like(state)
    ideal = torch.arange(outer.p.L, device=state.device) % Q
    target = args.periods * U
    events = {i * U for i in range(1, args.periods + 1)}
    for box in boxes:
        stop = box.stop - base
        events.update((box.start - base, stop))
        events.update(stop + delta for delta in (1, 16, 64, 256, 1024, Q, 2 * Q))
    started, elapsed = time.monotonic(), meta["elapsed_seconds"]

    def save():
        meta["elapsed_seconds"] = elapsed + time.monotonic() - started
        arrays = dict(physical=runner.state.cpu().numpy(), physical_structure_bins=np.asarray(traces, np.uint8).reshape(-1, B, outer.p.L // 16))
        arrays.update({"ground_" + k:v for k,v in ground.items()})
        arrays.update({"previous_" + k:v for k,v in previous.items()})
        save_checkpoint(path, meta, arrays)

    if not args.resume: save()
    try:
        while meta["steps"] < target:
            t = meta["steps"]
            end = min([target, t + args.chunk] + [e for e in events if e > t])
            advance(runner, base + t, base + end, boxes, noise)
            meta["steps"] = end
            bad = (field(runner.state, "addr") != ideal) | (field(runner.state, "age") != end % U)
            traces.append(bad.reshape(B, -1, 16).sum(-1).cpu().numpy().astype(np.uint8))
            sample = dict(step=end, bad_structure=bad.sum(1).cpu().tolist(),
                          flag1=field(runner.state, "f1").sum(1).cpu().tolist(),
                          flag2=field(runner.state, "f2").sum(1).cpu().tolist())
            meta["samples"].append(sample)
            if sample["bad_structure"][0]: raise RuntimeError("clean control lost physical structure")
            if end % U == 0:
                ground = direct.step(ground)
                conditional = direct.step(previous)
                decoded = decode_state_info(gpu.info_bits(runner.state).cpu().numpy(), outer.L, Q)
                record = dict(period=end // U, ground=decoded_metrics(decoded, ground, middle.T),
                              conditional_transition=decoded_metrics(decoded, conditional, middle.T))
                meta["commits"].append(record)
                if record["ground"]["any_state_cells"][0]: raise RuntimeError("clean control failed decoded transition")
                previous = decoded
                print(json.dumps(record), flush=True)
            meta["status"] = "complete" if end == target else "running"
            save()
    except Exception as exc:
        meta["status"], meta["error"] = "failed", repr(exc)
        save()
        raise
    return meta


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input", type=Path)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--widths", type=int, nargs="+", default=[1, 21, 101])
    p.add_argument("--trials", type=int, default=4)
    p.add_argument("--periods", type=int, default=2)
    p.add_argument("--chunk", type=int, default=2048)
    p.add_argument("--seed", type=int, default=1370)
    p.add_argument("--resume", action="store_true")
    args = p.parse_args()
    meta = run(args)
    print(json.dumps(dict(status=meta["status"], steps=meta["steps"], elapsed_seconds=meta["elapsed_seconds"])), flush=True)


if __name__ == "__main__":
    main()
