"""Compile the complete word rule, with local radius-five retrieval and feedback."""
from dataclasses import dataclass
from functools import lru_cache
import numpy as np
from . import word_rule as r
from .wordcode import LIT,ADD


@dataclass(frozen=True)
class Instruction:
    kind:int
    a:int
    b:int
    d:int


@dataclass(frozen=True)
class Layout:
    memory_count:int
    instructions:tuple
    description_sha256:str
    info_start:int=5*r.FIELDS
    info_width:int=r.FIELDS

    @property
    def colony_cells(self):return r.Q
    @property
    def computation_cells(self):return self.memory_count+len(self.instructions)+1
    @property
    def hold_start(self):return r.self_description().wires
    @property
    def description_instruction(self):return 10*r.FIELDS+3
    @property
    def regeneration_instruction(self):return self.description_instruction+len(r.self_description().operations)+r.FIELDS
    @property
    def commit_instruction(self):return self.regeneration_instruction+2*len(r.STATIC)

    def schedule(self):
        phase,ticks=0,0;cycle=2*self.computation_cells;rows=[]
        for i,op in enumerate(self.instructions):
            p=self.memory_count+i;targets=(p,)
            if op.kind in r.ALU_KINDS:targets+=(op.a,op.b,op.d)
            elif op.kind==r.LIT:targets+=(op.d,)
            elif op.kind in (r.SEND,r.LOAD):targets+=(op.a,)
            times=[]
            for target in targets:
                ticks+=(target-phase)%cycle+1;phase=(target+1)%cycle;times.append(ticks)
            if op.kind==r.WAIT:ticks+=5*r.Q;times[-1]=ticks
            if op.kind==r.META:
                ticks+=4*self.computation_cells+op.a-p;phase=op.a+1;times.append(ticks)
            rows.append(tuple(times))
        ticks+=(self.computation_cells-1-phase)%cycle+1+self.computation_cells
        return ticks,tuple(rows)

    @property
    def period_ticks(self):return self.schedule()[0]

    def timing_certificate(self):
        period,rows=self.schedule();packets=[]
        for op,times in zip(self.instructions,rows):
            if op.kind==r.SEND:
                hops=op.d>>1;direction=op.d&1
                packets.append((direction,times[-1],op.a,hops*(r.Q-r.FIELDS)))
        last_arrival=max(t+distance for _,t,_,distance in packets)
        first_read=rows[self.description_instruction][1]-1
        # The first description operation is a LIT, hence its first RAM access
        # is a write. Requiring all arrivals before it is conservative.
        for i,(direction,t,source,distance) in enumerate(packets):
            line=(source+t if direction else source-t)%r.Q
            for direction2,u,source2,distance2 in packets[i+1:]:
                if u>=t+distance:continue
                if direction!=direction2:continue
                if line==(source2+u if direction2 else source2-u)%r.Q:
                    raise ValueError('packet trajectories collide on a track')
        if last_arrival>first_read:raise ValueError('retrieval did not finish')
        return dict(period_ticks=period,last_arrival=last_arrival,first_description_access=first_read,
                    arrival_margin=first_read-last_arrival,pipelined_tracks_distinct=True,
                    computation_cells=self.computation_cells,period_over_Q=period/r.Q)


@lru_cache(maxsize=1)
def layout():
    desc=r.self_description();temp=desc.wires+r.FIELDS;memory=temp+1;ops=[]
    for hops in range(1,6):
        for field in range(r.FIELDS):
            source=5*r.FIELDS+field
            ops.append(Instruction(r.SEND,source,(5+hops)*r.FIELDS+field,(hops<<1)|r.LEFT))
            ops.append(Instruction(r.SEND,source,(5-hops)*r.FIELDS+field,(hops<<1)|r.RIGHT))
    ops.extend((Instruction(r.LIT,5*r.Q,0,temp),Instruction(r.LOAD,temp,0,0),Instruction(r.WAIT,0,0,0)))
    for i,(kind,a,b) in enumerate(desc.operations):ops.append(Instruction(kind,a,b,desc.inputs+i))
    zero=next(desc.inputs+i for i,(kind,a,_) in enumerate(desc.operations) if kind==LIT and a==0)
    for i,wire in enumerate(desc.outputs):ops.append(Instruction(ADD,wire,zero,desc.wires+i))
    for selector,name in enumerate(r.STATIC):
        ops.append(Instruction(r.LOAD,desc.wires+r.COL['address'],0,0))
        ops.append(Instruction(r.META,desc.wires+r.COL[name],selector,0))
    for i in range(r.FIELDS):ops.append(Instruction(ADD,desc.wires+i,zero,5*r.FIELDS+i))
    result=Layout(memory,tuple(ops),desc.digest())
    if result.computation_cells>=r.Q or max(memory,len(ops))>=1<<32:raise ValueError('fixed capacity exceeded')
    result.timing_certificate();return result


@lru_cache(maxsize=1)
def template():
    g=layout()
    cells=[r.Cell(index=i,address=i,first=int(i==0),head=int(i==0)) for i in range(g.memory_count)]
    cells.extend(r.Cell(kind=op.kind,index=i,a=op.a,b=op.b,d=op.d,address=g.memory_count+i) for i,op in enumerate(g.instructions))
    cells.append(r.Cell(kind=r.LOOP,index=len(g.instructions),last=1,address=g.computation_cells-1))
    array=np.array([r.encode_cell(c) for c in cells],dtype=np.uint64);array.flags.writeable=False
    return array


def encode_cores(cells):
    cells=tuple(cells)
    if not cells:raise ValueError('nonempty represented configuration required')
    g=layout();result=np.tile(template(),(len(cells),1))
    for i,c in enumerate(cells):result[i*g.computation_cells+g.info_start:i*g.computation_cells+g.info_start+r.FIELDS,r.COL['data']]=r.encode_cell(c)
    return result
