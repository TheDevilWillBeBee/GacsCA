"""Descriptor support check for composing a one-head event with quiet exterior.

Canonical coherent hypotheses make all non-procedure fields independent of the
head. A holder outside the checked +/-4 window then sees the same USED inputs as
a quiet-state instance, even if unused raw input slots still contain head copies.
"""
import argparse
from dataclasses import replace
import json
from pathlib import Path
import resource
import time
from gacsca.fixed_rule import small_holder_rule as f
from gacsca.fixed_rule.wordcode import LIT
from experiments.fixed_rule.prove_small_holder_boundary import validate
from experiments.fixed_rule.audit_small_holder_position_events import sha


def certify(description=None):
    desc=f.self_description() if description is None else description
    validate(desc)
    visited=set();used=set();pending=list(desc.outputs)
    while pending:
        wire=pending.pop()
        if wire in visited:continue
        visited.add(wire)
        if wire<desc.inputs:used.add(wire);continue
        kind,a,b=desc.operations[wire-desc.inputs]
        if kind!=LIT:pending.extend((a,b))
    support={}
    for wire in used:
        row,field=divmod(wire,f.FIELDS);name=f.SCHEMA[field][0]
        parts=name.split('_',1)
        if len(parts)==2 and parts[0] in ('s0','s1','s2','s3','s4'):
            logical=f.NEIGHBORHOOD[row]+int(parts[0][1])-2
            support.setdefault(logical,set()).add(parts[1])
    assert support and set(support)<=set(range(-4,5)), 'event window does not cover all used logical procedure inputs'
    return dict(passed=True,used_raw_input_words=len(used),logical_procedure_offsets=sorted(support),
                procedure_fields_by_offset={str(k):sorted(v) for k,v in sorted(support.items())},
                checked_event_holder_offsets=list(range(-4,5)),descriptor_sha256=desc.digest())


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();result=certify()
    result.update(source_sha256=sha(__file__),seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  limitation='Syntactic support bound. Quiet exterior follows only with coherent procedure copies and the canonical uniform-clock/zero-flag/Signal/Wf one-head hypotheses of the event lemmas; no damaged-state compression or whole-period claim.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
