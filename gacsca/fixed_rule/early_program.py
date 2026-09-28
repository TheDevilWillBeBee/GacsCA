"""Fixed clock ROM with Gray's early program-record overwrite before gathering.

The complete unprojected F is unchanged: its described LOAD/META controller
executes this prefix. P and therefore projected G change once for this revision,
never with hierarchy depth. Post-evaluation new-Address reconstruction remains.
"""
from functools import lru_cache
import numpy as np
from . import clock_rule as r,clock_program as baseline
from .clock_program import Layout,Instruction,HISTORY_OFFSETS,RESERVED

PREFIX_WORDS=2*len(r.STATIC)


@lru_cache(maxsize=1)
def layout():
    old=baseline.layout();prefix=[]
    for selector,name in enumerate(r.STATIC):
        prefix.append(Instruction(r.LOAD,old.info[r.COL['address']],0,0))
        prefix.append(Instruction(r.META,old.info[r.COL[name]],selector,0))
    n=len(prefix);entries=(0,*(value+n for value in old.entries[1:]))
    ranges=((0,old.stage_ranges[0][1]+n),*((a+n,b+n) for a,b in old.stage_ranges[1:]))
    result=Layout(old.memory_count,tuple(prefix)+old.instructions,entries,old.info,old.hold,
                  old.votes,old.wires,ranges,old.description_sha256)
    if result.computation_cells>=r.Q:raise ValueError('fixed colony capacity exceeded')
    result.timing_certificate();return result


def repair_ticks():return layout().schedule(0,PREFIX_WORDS)[0]


@lru_cache(maxsize=1)
def template():
    g=layout();memory=baseline.template()[:g.memory_count].copy()
    memory[0,r.COL['a']]=g.entries[0]|g.entries[1]<<32
    memory[0,r.COL['b']]=g.entries[2]|g.entries[3]<<32
    memory[0,r.COL['d']]=g.entries[4]
    instructions=[r.Cell(kind=op.kind,index=i,a=op.a,b=op.b,d=op.d,address=g.memory_count+i) for i,op in enumerate(g.instructions)]
    instructions.append(r.Cell(kind=r.LOOP,index=len(g.instructions),last=1,address=g.computation_cells-1))
    result=np.concatenate((memory,np.array([r.encode_cell(c) for c in instructions],dtype=np.uint64)))
    result.flags.writeable=False;return result


def encode_cores(cells):
    cells=tuple(cells)
    if not cells:raise ValueError('nonempty represented configuration required')
    g=layout();result=np.tile(template(),(len(cells),1))
    for i,c in enumerate(cells):result[i*g.computation_cells+np.array(g.info),r.COL['data']]=r.encode_cell(c)
    return result
