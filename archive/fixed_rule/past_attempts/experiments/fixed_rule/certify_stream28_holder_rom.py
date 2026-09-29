"""Conditional complete own-ROM dataflow for the streaming-gather candidate.

The gather histories are supplied as symbolic terms only after independently
checking the fixed local stream route schedule.  The late controller program
is then executed instruction by instruction against this candidate's own ROM.
This is a dataflow certificate, not a physical-period replay.
"""
from types import FunctionType
import hashlib
import json
from pathlib import Path
import time
import random

from gacsca.fixed_rule import stream28_holder_rule as f, stream28_holder_core as c
from gacsca.fixed_rule import stream28_holder_program as p
from experiments.fixed_rule.certify_packed28_holder_rom import (
    Terms as PreviousTerms, Checker as PreviousChecker,
)


def bind(function):
    namespace=dict(function.__globals__)
    namespace.update(f=f,c=c,p=p)
    if 'Terms' in globals():namespace['Terms']=Terms
    result=FunctionType(function.__code__,namespace,function.__name__,
                        function.__defaults__,function.__closure__)
    result.__kwdefaults__=function.__kwdefaults__
    return result


class Terms(PreviousTerms):
    lookup=bind(PreviousTerms.lookup)
    normalize=bind(PreviousTerms.normalize)


class Checker(PreviousChecker):
    __init__=bind(PreviousChecker.__init__)
    _base_reset=bind(PreviousChecker._base_reset)
    reset=bind(PreviousChecker.reset)
    _base_execute=bind(PreviousChecker.execute)
    mem=bind(PreviousChecker.mem)
    deliver=bind(PreviousChecker.deliver)
    vote=bind(PreviousChecker.vote)
    check=bind(PreviousChecker.check)

    def execute(self,col,entry,*,third=False):
        stage=getattr(self,'_gather_stage',None)
        if stage in range(3) and entry==self.entries[stage] and not third:
            for wire in self.g.gathered_inputs:
                neighbor,field=divmod(wire,f.FIELDS)
                target=self.g.history(stage,neighbor-7,field)
                self.memory[col][target]=self.normal[(col+neighbor-7)%self.n][field]
            return dict(ticks=1,messages=[],accesses=set(),writes=set(),stop_pc=entry)
        return self._base_execute(col,entry,third=third)


def equivalence():
    original=f.self_description();compiled=p.compiled_description()
    terms=Terms(p.base_rom())
    inputs=tuple(terms.variable('input_'+str(i),width)
                 for i,(_,width) in enumerate(f.SCHEMA*15))
    expected=terms.expression(original,inputs)
    actual=terms.expression(compiled,inputs)
    assert len(expected)==len(actual)==f.FIELDS
    unresolved=[name for (name,_),got,want in zip(f.SCHEMA,actual,expected)
                if got!=want]
    assert not unresolved,('symbolic compiled/original difference',unresolved)
    rng=random.Random(2026092818)
    for _ in range(96):
        words=tuple(rng.getrandbits(width) for _ in range(15)
                    for _,width in f.SCHEMA)
        assert compiled.evaluate(words)==original.evaluate(words)
    return dict(passed=True,raw_outputs=f.FIELDS,
                structurally_equal_outputs=f.FIELDS-len(unresolved),
                structurally_unresolved_outputs=unresolved,
                randomized_complete_cases=96,
                original_sha256=original.digest(),compiled_sha256=compiled.digest())


def check():
    g=p.layout();timing=g.timing_certificate()
    assert timing['fits']
    assert len(g.gathered_inputs)==sum(int(p.base_rom()[a,4]&(1<<31)!=0)
                                       for a in range(g.memory_count))//3
    equal=equivalence()
    flow=Checker().check()
    assert flow['complete_raw_outputs_per_colony']==f.FIELDS
    return dict(passed=True,Q=f.Q,U=f.U,core_cells=g.computation_cells,
                full_description_operations=len(f.self_description().operations),
                compiled_operations=len(p.compiled_description().operations),
                gathered_words=len(g.gathered_inputs),
                gathered_histories=3*len(g.gathered_inputs)*15,
                stream_histories_symbolically_supplied=True,
                physical_period_executed=False,equivalence=equal,
                dataflow=flow,timing=timing,
                ROM_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest())


if __name__=='__main__':
    start=time.perf_counter();result=check();result['seconds']=time.perf_counter()-start
    path=Path('figs/fixed_rule/stream28_holder_rom_v2.json')
    if path.exists():raise FileExistsError(path)
    path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:value for key,value in result.items() if key not in ('dataflow','timing')},indent=2))
