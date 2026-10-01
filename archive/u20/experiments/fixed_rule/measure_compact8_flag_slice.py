"""Measure the stage-three Flag1/Flag2 backward slice of the changed own-F.

The slice is an architecture audit, not a new physical transition or a timed
second evaluator pass. A future fixed rule may run its one encoded evaluator
twice per upper work period and commit only these outputs on the early pass.
"""
import argparse
import hashlib
import json
from pathlib import Path
import random

from gacsca.fixed_rule import stream28_compact_vote_optimized8 as optimized
from gacsca.fixed_rule import stream28_holder_rule as holder
from gacsca.fixed_rule import stream28_compact_vote8 as physical
from gacsca.fixed_rule.word_prune import prune
from gacsca.fixed_rule.wordcode_and import Program,LIT


def flag_slice():
    full=optimized.build()
    requested=tuple(full.outputs[holder.COL[name]] for name in ('f1','f2'))
    reduced=prune(Program(full.inputs,full.operations,requested))
    return Program(reduced.inputs,reduced.operations,reduced.outputs)


def audit(cases=32):
    full=optimized.build()
    small=flag_slice()
    raw={w for opcode,a,b in small.operations if opcode!=LIT
         for w in (a,b) if w<small.inputs}
    raw.update(w for w in small.outputs if w<small.inputs)
    spatial=tuple(sorted(w for w in raw
                         if w%physical.FIELDS>=holder.FIELDS))
    static=tuple(sorted(w for w in raw
                        if w%physical.FIELDS<len(holder.STATIC)))
    rng=random.Random(2026092901)
    for case in range(cases):
        words=tuple(rng.getrandbits(width) for width in optimized.WIDTHS)
        want=full.evaluate(words)
        got=small.evaluate(words)
        if got!=(want[holder.COL['f1']],want[holder.COL['f2']]):
            raise AssertionError(('flag slice differs from full rule',case))
    if spatial:raise AssertionError(('flag slice reads spatial inputs',spatial))
    if len(small.operations)>=len(full.operations):
        raise AssertionError('flag slice did not reduce the own-F')
    return dict(passed=True,full_description_sha256=full.digest(),
                flag_description_sha256=small.digest(),
                full_operations=len(full.operations),
                flag_operations=len(small.operations),
                required_raw_inputs=len(raw),
                required_spatial_inputs=len(spatial),
                required_holder_static_inputs=len(static),
                required_holder_dynamic_inputs=len(raw)-len(static),
                static_holder_wires=static,
                random_typed_cases=cases,
                old_stage_three_serial_ticks=10651589,
                one_fixed_evaluator_period=65536,
                limitation='A dependency slice and exact output oracle, not '
                           'an early physical pass or a shortened U period.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--cases',type=int,default=32)
    args=parser.parse_args()
    result=audit(args.cases)
    result['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    print(json.dumps(result,indent=2))
    if args.output:
        if args.output.exists():raise FileExistsError(args.output)
        args.output.write_text(json.dumps(result,indent=2)+'\n')
