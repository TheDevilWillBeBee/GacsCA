"""Complete typed-expression equality and symbolic optimized-ROM self-reference.

Compilation/diagnostic only: no host evaluator substitutes for physical dynamics.
This does not transfer the frozen ROM's physical schedule certificates to this
new ROM. Physical path recertification and complete execution remain required.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time

import numpy as np
from gacsca.fixed_rule import small_holder_rule as f,small_holder_core as c
from gacsca.fixed_rule import identity_holder_program as p,identity_holder_projected as r
from gacsca.fixed_rule.word_identity_optimization import optimize
from experiments.fixed_rule import certify_small_holder_rom_dataflow as batch
from experiments.fixed_rule.small_holder_identity_validation import StructuralTerms
from experiments.fixed_rule.audit_small_holder_position_events import sha


class Terms(StructuralTerms):
    normalize=batch.Terms.normalize


class Checker(batch.Checker):
    def __init__(self):
        self.rom=p.base_rom();self.g=p.layout();self.n=15;self.t=Terms(self.rom);self.zero=self.t.const(0)
        self.memory=[[self.zero]*f.Q for _ in range(self.n)]
        self.inputs=tuple(tuple(self.t.variable(f'raw_{col}_{name}',width) for name,width in f.SCHEMA) for col in range(self.n))
        self.normal=tuple(tuple(self.t.normalize(row)) for row in self.inputs)
        for col in range(self.n):
            for at,value in zip(self.g.info,self.inputs[col]):self.memory[col][at]=value
        header=self.rom[0]
        self.entries=tuple(int((int(header[2 if stage<2 else 3])>>(32*(stage%2)))&0xFFFFFFFF) if stage<4 else int(header[4]) for stage in range(5))
        assert self.entries==self.g.entries
        self.instructions=0;self.queries=0;self.packets=0;self.phases=[]


def equivalence(description=None):
    original=f.self_description();widths=tuple(w for _ in range(15) for _,w in f.SCHEMA)
    optimized,info=optimize(original,input_widths=widths)
    if description is not None:optimized=description
    t=StructuralTerms(p.base_rom());inputs=tuple(t.variable('input_'+str(i),w) for i,w in enumerate(widths))
    expected=t.expression(original,inputs);actual=t.expression(optimized,inputs)
    for (name,_),a,b in zip(f.SCHEMA,expected,actual):assert a==b,('optimized full output mismatch',name)
    assert len(actual)==len(expected)==f.FIELDS
    return dict(passed=True,complete_raw_outputs=f.FIELDS,arbitrary_typed_neighborhoods=True,
                symbolic_terms=len(t.nodes),**{k:v for k,v in info.items() if k!='input_widths'})


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();equal=equivalence();checker=Checker();dataflow=checker.check();timing=p.layout().timing_certificate()
    assert timing['fits']
    widths=dict(c.SCHEMA)
    for address in range(f.Q):
        assert all(0<=value<1<<widths[name] for name,value in r.record(address).items())
    controller_ticks=sum(p.layout().schedule(row[0],row[1])[0] for row in p.layout().stage_ranges)+p.layout().schedule(*p.layout().delivery_range)[0]
    # stage_ranges includes the final evaluation exactly once; delivery_range
    # adds the separate first evaluation and its Signal deliveries.
    result=dict(passed=True,equivalence=equal,dataflow=dataflow,timing=timing,
                compiled_program_instructions=len(p.layout().instructions),compiled_core_cells=len(p.base_rom()),
                controller_path_ticks=controller_ticks,minimum_power_of_two_from_controller_paths=1<<(controller_ticks-1).bit_length(),
                all_fixed_ROM_fields_typed=True,physical_descriptor_sha256=f.self_description().digest(),
                optimized_description_sha256=p.compiled_description().digest(),rom_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest(),
                source_sha256={str(path):sha(path) for path in (Path(__file__),Path(p.__file__),Path(r.__file__),Path(batch.__file__),
                    Path('gacsca/fixed_rule/word_identity_optimization.py'),Path('experiments/fixed_rule/small_holder_identity_validation.py'))},
                seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                limitation='Equivalent complete-description compiler and conditional symbolic ROM trajectory. The new ROM has not inherited the old physical path/packet certificates or complete-period executions. Q/U and raw F are unchanged; projected hard-wiring is a distinct fixed candidate, never selected by depth.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
