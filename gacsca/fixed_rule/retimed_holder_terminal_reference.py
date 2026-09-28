"""Diagnostic complete terminal-bank formula for the unchanged retimed rule.

This is NOT a physical executor and is never installed into an evolving world.
It replays the fixed final instruction stream to expose every surviving scratch
word, not just the simulated output. Correctness outside the declared noiseless
entry domain requires additional proof; there is no hierarchy-depth argument.
"""
from functools import lru_cache
import numpy as np
from . import retimed_holder_rule as f,retimed_holder_core as c,retimed_holder_projected as r
from . import retimed_holder_program as p
from .wordcode import LIT,arithmetic


@lru_cache(None)
def metadata():
    return tuple(tuple(r.record(address)[name] for name in c.STATIC) for address in range(f.Q))


def terminal(parents,*,max_bytes=32*1024**2):
    parents=tuple(parents);n=len(parents);g=p.layout()
    if not n or any(not isinstance(cell,r.Cell) for cell in parents):raise ValueError('complete projected parent states required')
    if type(max_bytes) is not int or max_bytes<1 or 2*n*(g.memory_count+5)*8>max_bytes:raise ValueError('diagnostic memory budget exceeded')
    raw=tuple(f.encode_cell(r.lift(cell)) for cell in parents)
    precommit=np.zeros((n,g.memory_count+5),dtype=np.uint64)
    for col in range(n):
        memory=[0]*(g.memory_count+5)
        for offset in range(-7,8):
            for field,value in enumerate(raw[(col+offset)%n]):
                for stage in range(3):memory[g.history(stage,offset,field)]=value
                memory[g.votes[(offset+7)*f.FIELDS+field]]=value
        for at,value in zip(g.info,raw[col]):memory[at]=value
        loaded=None;start,end=g.stage_ranges[4]
        for index in range(start,end):
            op=g.instructions[index]
            if op.kind==LIT:memory[op.d]=op.a
            elif op.kind in c.ALU_KINDS:memory[op.d]=arithmetic(op.kind,memory[op.a],memory[op.b])
            elif op.kind==c.LOAD:loaded=memory[op.a]
            elif op.kind==c.META:
                assert loaded is not None and 0<=loaded<f.Q and 0<=op.b<len(c.STATIC)
                memory[op.a]=metadata()[loaded][op.b]
            elif op.kind==c.IF_THIRD:
                assert index==end-1,'final phase must halt before Signal SEND'
            else:raise AssertionError(('unexpected final fixed instruction',index,op))
        precommit[col]=memory
    committed=precommit.copy();committed[:,list(g.info)]=precommit[:,list(g.hold)]
    # Signals were captured from the first identical evaluation; both Data buffer
    # sets were then cleared by actual stage-three/four resets.
    signals=precommit[:,[g.hold[f.COL['f2']],g.hold[f.COL['f1']]]].copy()
    assert np.all(signals<=1)
    return dict(precommit_bank=precommit,committed_bank=committed,signals=signals)
