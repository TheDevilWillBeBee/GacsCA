"""Physical faults around nested IEVAL or rollover from reference-prepared states.

The CPU prepares the middle state ONCE; this is not a physically executed prefix.
After encoding, every transition is physical CUDA. References are observers only.
Each physical boundary is retained for independent decoding/mechanism analysis.
"""
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import time

import numpy as np
import torch

from gacsca.checkpoint import load_checkpoint, save_checkpoint
from gacsca.gpu import field
from gacsca.gpu_engine import CleanGraphRunner
from gacsca.hierarchy import encode_state_info, decode_state_info
from gacsca.engine_np import repair
from experiments.cache_bootstrap import cached_initial
from experiments.gray_faults import FaultBox, advance
from experiments.phase_size import archive_sources
from experiments.replay_third_link_completion import initial_top
from experiments.third_link_checkpoint import build
from experiments.third_link_faults import decoded_metrics
from experiments.tower_checkpoint import fingerprint


def phase_spec(outer, middle, top, phase, n, target_cell=None):
    """Place faults in the holder of an actually selected BITOP destination."""
    op = next(o for o in top.prog.ops if o.kind == "BITOP")
    index = top.prog.ops_at(op.t0).index(op)
    evaluation = next(o for o in middle.prog.ops if o.kind == "IEVAL" and o.param == index)
    if phase not in ("evaluation", "rollover"):
        raise ValueError("unknown phase")
    age = evaluation.t0 - 1 if phase == "evaluation" else middle.p.U - 2
    cell = n // 2 if target_cell is None else target_cell
    if not 0 <= cell < n: raise ValueError("target cell is outside top ring")
    # initial_top assigns top Address = 5 + cell, inside this BITOP's domain.
    if not op.lo <= (5 + cell) % top.p.Q < op.hi:
        raise ValueError("selected top cell is outside the BITOP's address domain")
    holder = cell * middle.p.Q + middle.sched.ictx.pos(op.dst, middle.T.R // 2)
    centers = dict(control=outer.L.b0 + outer.L.fields["SIMAGE"][0] + 8,
                   info=outer.L.b0 + outer.L.track_base + middle.T["INFO"] * middle.T.R + middle.T.R // 2,
                   hold=outer.L.b0 + outer.L.track_base + middle.T["HOLD"] * middle.T.R + middle.T.R // 2)
    return dict(phase=phase, age=age, evaluation_age=evaluation.t0, opcode=asdict(op),
                opcode_index=index, top_cell=cell, middle_holder=holder, centers=centers)


def scenarios(outer, spec, widths, trials):
    if trials < 1 or not widths or len(set(widths)) != len(widths):
        raise ValueError("positive trials and distinct widths required")
    labels = [dict(target="clean", width=0, trial=0)]
    boxes = []
    for target, center in spec["centers"].items():
        for width in widths:
            left = center - width // 2
            if width < 1 or left < 0 or left + width > outer.p.Q:
                raise ValueError("island must fit in its targeted physical colony")
            for trial in range(trials):
                b = len(labels)
                labels.append(dict(target=target, width=width, trial=trial))
                site = spec["middle_holder"] * outer.p.Q + left
                boxes.append(FaultBox(b, outer.p.U - 2, outer.p.U - 1, site, site + width))
    return labels, boxes


def prepare(middle, top, n, seed, age, progress=False):
    direct = middle.np_engine()
    raw = initial_top(top, n, seed)
    state = cached_initial(middle, raw)
    for t in range(age):
        state = direct.step(state)
        if progress and (t + 1) % 2048 == 0:
            print(json.dumps(dict(prepared_middle_steps=t + 1, target=age)), flush=True)
    if not np.all(state["age"] == age):
        raise ValueError("prepared middle clocks are not synchronized")
    return state


def validate_evaluation(middle, top, initial, spec):
    """Reject an inactive or value-preserving target before using the GPU."""
    if spec["phase"] != "evaluation": return {}
    before = middle.np_engine().step(initial)
    after = middle.np_engine().step(before)
    h = spec["middle_holder"]
    age, addr = int(before["simage"][0, h]), int(before["simaddr"][0, h])
    active = top.prog.ops_at(age)
    index = spec["opcode_index"]
    if (len(active) <= index or active[index].kind != "BITOP"
            or not active[index].lo <= addr < active[index].hi):
        raise ValueError("prepared target does not execute the intended BITOP")
    old = int(repair(before["trk"])[0, h, middle.T["HOLD"]])
    new = int(repair(after["trk"])[0, h, middle.T["HOLD"]])
    if old == new: raise ValueError("selected BITOP does not change the targeted HOLD bit")
    return dict(simage=age, simaddr=addr, holder=h, hold_before=old, hold_after=new,
                middle_age=int(before["age"][0, h]), opcode_index=index)


def run(args):
    if args.periods < 2 or args.chunk < 1 or (args.stop_after is not None and args.stop_after < 1):
        raise ValueError("at least two periods and positive chunk/stop-after required")
    outer, middle, top = build(3, args.top_cells)
    spec = phase_spec(outer, middle, top, args.phase, args.top_cells, getattr(args, "top_cell", None))
    labels, boxes = scenarios(outer, spec, args.widths, args.trials)
    path = args.output.with_suffix(".npz")
    archive = args.output.with_name(args.output.name + "_sources.tar.gz")
    gpu, direct = outer.gpu_engine(seed=args.seed, noise_version=2), middle.np_engine()
    root = Path(__file__).resolve().parents[1]
    hashes = fingerprint()
    for name in (__file__, "experiments/third_link_checkpoint.py", "experiments/gray_faults.py",
                 "experiments/third_link_faults.py", "experiments/phase_size.py",
                 "experiments/replay_third_link_completion.py", "experiments/verify_third_link_checkpoint.py",
                 "experiments/cache_bootstrap.py"):
        p = Path(name).resolve()
        hashes[str(p.relative_to(root))] = hashlib.sha256(p.read_bytes()).hexdigest()
    identity = dict(schema=2, protocol="reference-prepared-nested-phase-physical-islands",
                    cache_initialization="input_age_address",
                    fingerprints=hashes, seed=args.seed, initialization_seed=args.initialization_seed,
                    top_cells=args.top_cells, top_neighborhood_aliasing=args.top_cells < 11,
                    spec=spec, labels=labels, boxes=[asdict(b) for b in boxes],
                    periods=args.periods, chunk=args.chunk, noise_version=2, flag2_rule="printed",
                    physical=asdict(outer.p), middle=asdict(middle.p), top=asdict(top.p))
    if args.resume:
        meta, arrays = load_checkpoint(path, identity)
        if hashlib.sha256(archive.read_bytes()).hexdigest() != meta["source_archive_sha256"]:
            raise ValueError("source archive mismatch")
        if meta["status"] == "failed": raise ValueError("failed run requires diagnosis")
        if meta["status"] == "complete": return meta
        state = torch.from_numpy(arrays["physical"]).cuda()
        initial = {k[8:]:v for k,v in arrays.items() if k.startswith("initial_")}
        ground = {k[7:]:v for k,v in arrays.items() if k.startswith("ground_")}
        previous = {k[9:]:v for k,v in arrays.items() if k.startswith("previous_")}
    else:
        if path.exists() or archive.exists() or list(args.output.parent.glob(args.output.name + "_boundary*.npz")):
            raise FileExistsError("existing results require --resume")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        initial = prepare(middle, top, args.top_cells, args.initialization_seed, spec["age"], progress=True)
        validation = validate_evaluation(middle, top, initial, spec)
        # CPU work ends at initialization. The physical configuration is never
        # replaced by the reference, even when a fault changes decoded controls.
        ground = {k:v.copy() for k,v in initial.items()}
        previous = {k:np.repeat(v, len(labels), axis=0) for k,v in initial.items()}
        physical = outer.np_engine().initial(1, info_bits=encode_state_info(initial, outer.L, outer.p.Q))
        state = gpu.to_gpu(physical).repeat(len(labels), 1, 1)
        del physical
        archive_sources(archive, hashes)
        meta = dict(identity=identity, status="running", steps=0, samples=[], commits=[],
                    elapsed_seconds=0.0, source_archive=str(archive), phase_validation=validation,
                    source_archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
                    scope="CPU-prepared initial phase; physical transitions thereafter; no physical prefix or depth-scaling claim")
    runner = CleanGraphRunner(gpu, state)
    noise = torch.empty_like(state)
    ideal = torch.arange(outer.p.L, device=state.device) % outer.p.Q
    target = args.periods * outer.p.U
    stop = min(target, meta["steps"] + (args.stop_after or args.periods) * outer.p.U)
    events = {i * outer.p.U for i in range(1, args.periods + 1)}
    for b in boxes:
        events.update((b.start, b.stop))
        events.update(b.stop + d for d in (1, 16, 64, 256, 1024))
    start, elapsed = time.monotonic(), meta["elapsed_seconds"]

    def save(boundary=False):
        meta["elapsed_seconds"] = elapsed + time.monotonic() - start
        arrays = dict(physical=runner.state.cpu().numpy())
        for prefix, values in (("initial_", initial), ("ground_", ground), ("previous_", previous)):
            arrays.update({prefix + k:v for k,v in values.items()})
        save_checkpoint(path, meta, arrays)
        if boundary:
            p = args.output.with_name(args.output.name + f"_boundary{meta['steps'] // outer.p.U}.npz")
            if p.exists():
                old_meta, old_arrays = load_checkpoint(p, identity)
                if old_meta["steps"] != meta["steps"] or any(not np.array_equal(v, old_arrays[k]) for k,v in arrays.items()):
                    raise ValueError("existing boundary differs; refusing to overwrite")
            else:
                save_checkpoint(p, meta, arrays)

    if not args.resume: save()
    try:
        while meta["steps"] < stop:
            t = meta["steps"]
            end = min([stop, t + args.chunk] + [e for e in events if e > t])
            advance(runner, t, end, boxes, noise)
            meta["steps"] = end
            bad = (field(runner.state, "addr") != ideal) | (field(runner.state, "age") != end % outer.p.U)
            sample = dict(step=end, bad_structure=bad.sum(1).cpu().tolist(),
                          flag1=field(runner.state, "f1").sum(1).cpu().tolist(),
                          flag2=field(runner.state, "f2").sum(1).cpu().tolist())
            meta["samples"].append(sample)
            if sample["bad_structure"][0]: raise RuntimeError("clean physical control lost structure")
            if end % outer.p.U == 0:
                ground = direct.step(ground)
                conditional = direct.step(previous)
                decoded = decode_state_info(gpu.info_bits(runner.state).cpu().numpy(), outer.L, outer.p.Q)
                record = dict(period=end // outer.p.U, middle_age=int(ground["age"][0, 0]),
                              ground=decoded_metrics(decoded, ground, middle.T),
                              conditional_transition=decoded_metrics(decoded, conditional, middle.T))
                meta["commits"].append(record)
                if record["ground"]["any_state_cells"][0]: raise RuntimeError("clean decoded transition mismatch")
                previous = decoded
                print(json.dumps(record), flush=True)
            meta["status"] = "complete" if end == target else "running"
            # Boundaries and samples near the fault are recoverable; regular
            # chunks also checkpoint for exact interruption/resume semantics.
            save(boundary=end % outer.p.U == 0)
    except Exception as exc:
        meta["status"], meta["error"] = "failed", repr(exc)
        save()
        raise
    return meta


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--phase", choices=("evaluation", "rollover"), default="evaluation")
    p.add_argument("--top-cells", type=int, default=11)
    p.add_argument("--top-cell", type=int, default=8, help="target a value-changing BITOP holder (default seed: cell 8)")
    p.add_argument("--widths", type=int, nargs="+", default=[21])
    p.add_argument("--trials", type=int, default=2)
    p.add_argument("--periods", type=int, default=3)
    p.add_argument("--chunk", type=int, default=4096)
    p.add_argument("--seed", type=int, default=1400)
    p.add_argument("--initialization-seed", type=int, default=1350)
    p.add_argument("--stop-after", type=int)
    p.add_argument("--resume", action="store_true")
    args = p.parse_args()
    result = run(args)
    print(json.dumps(dict(status=result["status"], steps=result["steps"], elapsed_seconds=result["elapsed_seconds"])), flush=True)


if __name__ == "__main__":
    main()
