"""Fresh CPU replay plus independent two-stage decoding of the completed run."""
import argparse
import hashlib
import json
from pathlib import Path
import time

import numpy as np

from gacsca.engine_np import redistribute, repair
from gacsca.hierarchy import encode_state_info
from experiments.third_link_checkpoint import build
from experiments.verify_third_link_checkpoint import audit, decode_packed_info


def initial_top(top, n, seed):
    raw = {k:v[:, :n].copy() for k,v in top.np_engine().initial(1).items()}
    raw["addr"][:] = (5 + np.arange(n)) % top.p.Q
    raw["age"][:] = next(o.t0 for o in top.prog.ops if o.kind == "BITOP")
    raw["f1"][:] = np.arange(n) % 2
    raw["f2"][:] = (np.arange(n) + 1) % 2
    rng = np.random.default_rng(seed)
    for field in ("simage", "simaddr"):
        raw[field][:] = rng.integers(0, 65536, (1, n), dtype=np.int32)
    raw["trk"] = redistribute(rng.integers(0, 2, (1, n, top.T.NT), dtype=np.uint8), top.T.R)
    return raw


def decode_top(middle_state, middle, top):
    info = repair(middle_state["trk"])[..., middle.T["INFO"]]
    bits = info.reshape(1, -1, middle.p.Q)[..., middle.L.b0:middle.L.b0 + middle.L.K]
    result = {}
    for name, (start, width) in middle.L.fields.items():
        result[name.lower()] = (bits[..., start:start+width] * (1 << np.arange(width))).sum(-1).astype(np.int32)
    result["trk"] = bits[..., middle.L.track_base:].reshape(1, -1, top.T.NT, top.T.R)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("checkpoint", type=Path)
    p.add_argument("trace", type=Path)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if args.output.exists(): p.error("refusing to overwrite replay evidence")
    verification = audit(args.checkpoint)
    if not verification["passed"] or not verification["run_complete"]:
        p.error("requires independently verified completion")
    with np.load(args.checkpoint, allow_pickle=False) as z:
        meta = json.loads(str(z["_metadata"]))
        packed = z["physical"]
        saved = {k[7:]:z[k] for k in z.files if k.startswith("middle_")}
        saved_top = {k[4:]:z[k] for k in z.files if k.startswith("top_")}
    with np.load(args.trace, allow_pickle=False) as z:
        tm = json.loads(str(z["_metadata"]))
        periods = z["period"]
        trace = {k[7:]:z[k] for k in z.files if k.startswith("middle_")}
    assert tm["status"] == "complete" and tm["identity"]["source_identity"] == meta["identity"]
    outer, middle, top = build(meta["identity"]["R"], meta["top_cells"])
    assert meta["completed_periods"] == middle.p.U  # first complete middle period
    raw = initial_top(top, meta["top_cells"], meta["identity"]["seed"])
    direct = middle.np_engine()
    state = direct.initial(1, info_bits=encode_state_info(raw, middle.L, middle.p.Q))
    index, elements, start = 0, 0, time.monotonic()
    for period in range(1, middle.p.U + 1):
        state = direct.step(state)
        if index < len(periods) and period == periods[index]:
            for name, values in trace.items():
                np.testing.assert_array_equal(state[name][0], values[index], err_msg=f"sample {period}.{name}")
                elements += values[index].size
            index += 1
        if period % 1024 == 0: print(json.dumps(dict(period=period, samples_checked=index, elapsed_seconds=round(time.monotonic()-start, 2))), flush=True)
    assert index == len(periods)
    decoded, _, _ = decode_packed_info(packed, outer, middle)
    for name in state:
        np.testing.assert_array_equal(state[name], decoded[name], err_msg=f"packed final.{name}")
        np.testing.assert_array_equal(state[name], saved[name], err_msg=f"saved final.{name}")
    expected_top = top.np_engine().step(raw)
    actual_top = decode_top(decoded, middle, top)
    for name in expected_top:
        np.testing.assert_array_equal(actual_top[name], expected_top[name], err_msg=f"top.{name}")
        np.testing.assert_array_equal(saved_top[name], expected_top[name], err_msg=f"saved top.{name}")
    result = dict(checkpoint=str(args.checkpoint), checkpoint_sha256=verification["input_sha256"],
                  trace=str(args.trace), trace_sha256=hashlib.sha256(args.trace.read_bytes()).hexdigest(),
                  fresh_middle_steps=middle.p.U, trace_samples_checked=index, sampled_elements_checked=elements,
                  independently_decoded_middle_fields=list(decoded), independently_decoded_top_fields=list(actual_top),
                  fresh_top_transition_matches=True, elapsed_seconds=time.monotonic()-start, passed=True,
                  script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  scope="one full middle work period and one top microstep on an aliased one-cell top ring; no full top work period or depth-noise scaling")
    with args.output.open("x") as f: json.dump(result, f, indent=2)
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
