"""Compare a certified fork with a later saved direct state, without mutating either."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import torch

from gacsca.build import make_tower
from gacsca.gpu_engine import CleanGraphRunner
from experiments.quiescent import try_skip_quiescent


def read_snapshot(path):
    # Pin one checkpoint inode despite concurrent atomic checkpoint replacement.
    with path.open("rb") as stream:
        with np.load(stream, allow_pickle=False) as data:
            meta = json.loads(str(data["_metadata"]))
            state = data["physical"]
        stream.seek(0)
        digest = hashlib.sha256()
        while block := stream.read(1 << 20):
            digest.update(block)
    return meta, state, digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("direct", type=Path)
    parser.add_argument("certified", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("refusing to overwrite comparison")
    dm, direct, dh = read_snapshot(args.direct)
    cm, certified, ch = read_snapshot(args.certified)
    if dm["identity"] != cm["forked_from"]["identity"]:
        parser.error("direct checkpoint does not have the fork's original identity")
    root = Path(__file__).resolve().parents[1]
    for name, digest in cm["identity"]["fingerprints"].items():
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != digest:
            parser.error(f"certified source/binary changed: {name}")
    lower, upper = make_tower(Q0=8192, U0=1048576, Q1=8192, U1=1048576,
                              ncol0=8192, R=5, D=1, schedule="gray")
    gpu = lower.gpu_engine()
    if direct.shape != certified.shape or direct.shape != (1, lower.p.L, gpu.W):
        parser.error("wrong whole-colony geometry")
    runner = CleanGraphRunner(gpu, torch.from_numpy(certified).cuda(), block_steps=16)
    delta = dm["steps"] - cm["steps"]
    if delta <= 0:
        parser.error("need a later direct checkpoint")
    cert = try_skip_quiescent(runner, delta)
    if cert is None:
        parser.error("the intervening interval cannot be certified; no fallback that could hide differences")
    equal = torch.equal(runner.state, torch.from_numpy(direct).cuda())
    result = dict(direct_path=str(args.direct), direct_sha256=dh,
                  certified_path=str(args.certified), certified_sha256=ch,
                  direct_steps=dm["steps"], fork_steps=cm["forked_from"]["steps"],
                  pilot_steps=cm["steps"], extra_certificate=cert,
                  all_packed_words_equal=equal, compared_words=int(direct.size),
                  executor_fingerprints=cm["identity"]["fingerprints"],
                  comparison_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k:v for k,v in result.items() if k != "executor_fingerprints"}), flush=True)
    if not equal:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
