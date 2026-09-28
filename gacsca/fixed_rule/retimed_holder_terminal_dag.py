"""Independent diagnostic terminal-memory expression using DAG last writers.

No instruction interpreter or physical evolution is invoked. Every surviving
scratch location is retained. This module is a mathematical oracle only.
"""
import numpy as np
from . import retimed_holder_rule as f,retimed_holder_core as c,retimed_holder_projected as r,retimed_holder_program as p
from .wordcode import arithmetic,LIT,MASK


def terminal(parents):
    parents=tuple(parents);g=p.layout();description=p.compiled_description();n=len(parents)
    if not 1<=n<=64 or any(not isinstance(x,r.Cell) for x in parents):raise ValueError('bounded diagnostic parent configuration required')
    raw=tuple(f.encode_cell(r.lift(cell)) for cell in parents);bank=np.zeros((n,g.memory_count+5),dtype=np.uint64)
    temp=g.memory_count-6;signals=np.empty((n,2),dtype=np.uint64)
    for col in range(n):
        values=[value for offset in f.NEIGHBORHOOD for value in raw[(col+offset)%n]]
        for i,(kind,a,b) in enumerate(description.operations):
            value=a if kind==LIT else arithmetic(kind,values[a],values[b]);values.append(value)
            bank[col,g.wires[description.inputs+i]]=value
        for offset in f.NEIGHBORHOOD:
            for field,value in enumerate(raw[(col+offset)%n]):
                for stage in range(3):bank[col,g.history(stage,offset,field)]=value
                bank[col,g.votes[(offset+7)*f.FIELDS+field]]=value
        output=[values[wire] for wire in description.outputs]
        address=output[f.COL['address']]
        for offset in f.STATIC_OFFSETS:
            metadata=r.record((address+offset)%f.Q)
            for name in c.STATIC:output[f.COL[f'p{offset+3}_{name}']]=metadata[name]
        bank[col,list(g.hold)]=output;bank[col,list(g.info)]=raw[col]
        query=(address+3)&(f.Q-1)
        bank[col,temp]=3;bank[col,temp+1]=f.Q-1;bank[col,temp+2]=(~query)&MASK;bank[col,temp+5]=query
        signals[col]=(output[f.COL['f2']],output[f.COL['f1']])
    committed=bank.copy();committed[:,list(g.info)]=bank[:,list(g.hold)]
    return dict(precommit_bank=bank,committed_bank=committed,signals=signals)
