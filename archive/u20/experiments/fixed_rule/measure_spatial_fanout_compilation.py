"""Certify static full-DAG fanout repair under the fixed spatial alphabet.

This checks all gate/route slots and transformed output values. It does not
assign physical gate switch times or packet launch times.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import random
import resource
import time

from gacsca.fixed_rule import spatial_epoch as physical
from gacsca.fixed_rule import spatial_fanout_compiler as compiler
from gacsca.fixed_rule import stream28_holder_program as reference
from gacsca.fixed_rule import stream28_holder_rule as raw


def check():
    started=time.perf_counter()
    compiled=compiler.compile_capacity()
    assert compiler.validate_compilation(compiled)
    program=reference.compiled_description()
    rng=random.Random(2026092834)
    comparisons=[]
    for case in range(3):
        words=tuple(rng.getrandbits(width) for _ in range(15)
                    for _,width in raw.SCHEMA)
        observed=compiler.evaluate_compiled(words,compiled)
        expected=program.evaluate(words)
        assert observed==expected
        comparisons.append(dict(case=case,outputs=len(observed),matched=True))
    copied=[dict(gate=index,instances=count)
            for index,count in enumerate(compiled.copy_counts) if count>1]
    occupancy=Counter(compiled.site_gate_counts)
    return dict(passed=True,description_sha256=compiled.description_sha256,
                rule_width_bits=physical.WIDTH,Q=physical.Q,
                route_slots_per_site=physical.ROUTE_SLOTS,
                gate_slots_per_site=physical.GATE_SLOTS,
                original_gate_count=len(program.operations),
                physical_gate_instances=len(compiled.nodes),
                extra_gate_copies=sum(count-1 for count in compiled.copy_counts),
                copied_gates=copied,
                routed_operand_uses=len(compiled.uses),
                max_gate_site_routes=max(compiled.site_route_counts),
                max_raw_site_routes=max(compiled.raw_route_counts),
                static_gate_capacity=sum(compiled.site_gate_counts)+
                                     sum(physical.GATE_SLOTS-count
                                         for count in compiled.site_gate_counts),
                unused_gate_slots=sum(physical.GATE_SLOTS-count
                                      for count in compiled.site_gate_counts),
                gate_site_occupancy={str(key):value for key,value in sorted(occupancy.items())},
                pinned_first_eight_gates=compiled.first_eight_pinned,
                numeric_full_output_cases=comparisons,
                seconds=time.perf_counter()-started,
                max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                compiler_source_sha256=hashlib.sha256(Path(compiler.__file__).read_bytes()).hexdigest(),
                physical_rule_source_sha256=hashlib.sha256(Path(physical.__file__).read_bytes()).hexdigest(),
                limitation='Static capacity and diagnostic graph evaluation only; '
                           'no full-DAG physical timing, packet collision proof, '
                           'own-rule integration, or macrostep.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result=check()
    print(json.dumps(result,indent=2))
    if args.output:
        if args.output.exists():raise FileExistsError(args.output)
        args.output.write_text(json.dumps(result,indent=2)+'\n')
