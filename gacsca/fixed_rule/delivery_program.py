"""One fixed full-description ROM with local stage-three flag delivery.

A failed timing certificate must reject execution, not trigger a depth-specific
program variant. Tail buffers are supplied by the described static fallback.
"""
from dataclasses import dataclass
from functools import lru_cache
import numpy as np
from . import delivery_rule as r
from .word_program import Instruction
from .wordcode import LIT,ADD

HISTORY_OFFSETS=(0,2,3)
RESERVED=8

@dataclass(frozen=True)
class Layout:
    memory_count:int
    instructions:tuple
    entries:tuple
    info:tuple
    hold:tuple
    votes:tuple
    wires:tuple
    stage_ranges:tuple
    description_sha256:str
    delivery_range:tuple
    @property
    def computation_cells(self):return self.memory_count+len(self.instructions)+1
    @property
    def colony_cells(self):return r.Q
    @property
    def period_ticks(self):return r.U
    @property
    def description_instruction(self):return self.entries[4]
    def history(self,stage,neighbor,field):return RESERVED+4*((neighbor+5)*r.FIELDS+field)+HISTORY_OFFSETS[stage]

    def schedule(self,start,end):
        # Reset creates the head at cell 0 in the first local transition.
        phase,ticks=0,1;cycle=2*self.computation_cells;rows=[]
        for i in range(start,end):
            op=self.instructions[i];position=self.memory_count+i;targets=(position,)
            if op.kind in r.ALU_KINDS:targets+=(op.a,op.b,op.d)
            elif op.kind==r.LIT:targets+=(op.d,)
            elif op.kind in (r.SEND,r.LOAD):targets+=(op.a,)
            times=[]
            for target in targets:
                ticks+=(target-phase)%cycle+1;phase=(target+1)%cycle;times.append(ticks)
            if op.kind==r.META:
                ticks+=4*self.computation_cells+op.a-position;phase=op.a+1;times.append(ticks)
            rows.append(tuple(times))
        return ticks,tuple(rows)

    def timing_certificate(self):
        gathers=[]
        for stage,(start,end) in enumerate(self.stage_ranges[:3]):
            stopped,rows=self.schedule(start,end);packets=[]
            for op,times in zip(self.instructions[start:end],rows):
                if op.kind!=r.SEND:continue
                hops,direction=op.d>>1,op.d&1
                distance=hops*r.Q+(op.a-op.b if direction==r.LEFT else op.b-op.a)
                packets.append((direction,times[-1],op.a,distance))
            for i,(direction,t,source,distance) in enumerate(packets):
                line=(source+t if direction else source-t)%r.Q
                for direction2,u,source2,_ in packets[i+1:]:
                    if u>=t+distance or direction!=direction2:continue
                    if line==(source2+u if direction2 else source2-u)%r.Q:raise ValueError('same-track packet collision')
            arrival=max(t+distance for _,t,_,distance in packets)
            deadline=(6 if stage==2 else 16)*r.Q
            gathers.append(dict(stage=stage+1,head_stopped=stopped,last_arrival=arrival,deadline=deadline,margin=deadline-max(stopped,arrival)))
        evaluation,rows=self.schedule(*self.stage_ranges[4])
        third,rows3=self.schedule(*self.delivery_range)
        last_delivery=0
        for op,times in zip(self.instructions[slice(*self.delivery_range)],rows3):
            if op.kind==r.SEND:
                distance=op.a-op.b if op.d&1 else op.b-op.a
                last_delivery=max(last_delivery,times[-1]+distance)
        result=dict(stage3_head_stopped=third,stage3_last_delivery=last_delivery,
                    capture_budget=r.CAPTURE_AGE-r.VOTE_AGES[0],capture_margin=r.CAPTURE_AGE-r.VOTE_AGES[0]-last_delivery,
                    stage3_stop_margin=80*r.Q-r.VOTE_AGES[0]-third)
        result['fits']=all(x['margin']>0 for x in gathers) and evaluation<8*r.Q and result['capture_margin']>0 and result['stage3_stop_margin']>0
        return dict(**result,Q=r.Q,U=r.U,core_cells=self.computation_cells,descriptor_operations=len(r.self_description().operations),
                    gathers=gathers,evaluation_ticks=evaluation,evaluation_budget=8*r.Q,evaluation_margin=8*r.Q-evaluation,
                    stage3_vote_old_age=r.VOTE_AGES[0],stage5_vote_old_age=112*r.Q,commit_old_age=r.U-1)


@lru_cache(maxsize=1)
def layout():
    desc=r.self_description();votes=tuple(RESERVED+4*i+1 for i in range(desc.inputs))
    info_start=RESERVED+4*desc.inputs;info=tuple(info_start+2*i for i in range(r.FIELDS));hold=tuple(i+1 for i in info)
    wire_base=info_start+2*r.FIELDS;wires=votes+tuple(wire_base+i for i in range(len(desc.operations)))
    temp=wire_base+len(desc.operations);memory=temp+1;ops=[];entries=[];ranges=[]
    for stage in range(3):
        start=len(ops);entries.append(start)
        if stage==0:
            for selector,name in enumerate(r.STATIC):
                ops.extend((Instruction(r.LOAD,info[r.COL['address']],0,0),Instruction(r.META,info[r.COL[name]],selector,0)))
        ops.append(Instruction(r.LIT,0,0,temp))
        for i,source in enumerate(info):ops.append(Instruction(ADD,source,temp,RESERVED+4*(5*r.FIELDS+i)+HISTORY_OFFSETS[stage]))
        for hops in range(1,6):
            for field,source in enumerate(info):
                for direction,neighbor in ((r.LEFT,hops),(r.RIGHT,-hops)):
                    target=RESERVED+4*((5+neighbor)*r.FIELDS+field)+HISTORY_OFFSETS[stage]
                    ops.append(Instruction(r.SEND,source,target,(hops<<1)|direction))
        ops.append(Instruction(r.HALT,0,0,0));ranges.append((start,len(ops)))
    # Signal-to-Wf is automatic in F; stage four needs no evaluator head.
    entries.append(len(ops));ops.append(Instruction(r.HALT,0,0,0));ranges.append((entries[3],len(ops)))
    entries.append(len(ops));start=len(ops)
    for i,(kind,a,b) in enumerate(desc.operations):
        ops.append(Instruction(kind,a if kind==LIT else wires[a],0 if kind==LIT else wires[b],wires[desc.inputs+i]))
    zero=next(wires[desc.inputs+i] for i,(kind,a,_) in enumerate(desc.operations) if kind==LIT and a==0)
    for target,output in zip(hold,desc.outputs):ops.append(Instruction(ADD,wires[output],zero,target))
    for selector,name in enumerate(r.STATIC):
        ops.append(Instruction(r.LOAD,hold[r.COL['address']],0,0))
        ops.append(Instruction(r.META,hold[r.COL[name]],selector,0))
    ops.append(Instruction(r.IF_THIRD,0,0,0));ranges.append((start,len(ops)))
    for target in range(1,6):ops.append(Instruction(r.SEND,hold[r.COL['f2']],target,r.LEFT))
    for target in range(r.Q-5,r.Q):ops.append(Instruction(r.SEND,hold[r.COL['f1']],target,r.RIGHT))
    ops.append(Instruction(r.HALT,0,0,0))
    delivery_range=(start,len(ops))
    g=Layout(memory,tuple(ops),tuple(entries),info,hold,votes,wires,tuple(ranges),desc.digest(),delivery_range)
    if g.computation_cells>=r.Q or max(memory,len(ops))>=1<<32:raise ValueError('fixed capacity exceeded')
    return g


@lru_cache(maxsize=1)
def template():
    g=layout();cells=[r.Cell(index=i,address=i,a=31,first=int(i==0)) for i in range(g.memory_count)]
    from dataclasses import replace
    for word,vote in enumerate(g.votes):
        group=RESERVED+4*word
        for stage,offset in enumerate(HISTORY_OFFSETS):cells[group+offset]=replace(cells[group+offset],a=(1<<(stage+1))-1)
        cells[vote]=replace(cells[vote],a=31|r.VOTE)
    for address in g.info:cells[address]=replace(cells[address],a=r.INFO)
    cells[0]=replace(cells[0],a=g.entries[0]|g.entries[1]<<32,b=g.entries[2]|g.entries[3]<<32,d=g.entries[4])
    cells.extend(r.Cell(kind=op.kind,index=i,a=op.a,b=op.b,d=op.d,address=g.memory_count+i) for i,op in enumerate(g.instructions))
    cells.append(r.Cell(kind=r.LOOP,index=len(g.instructions),last=1,address=g.computation_cells-1))
    array=np.array([r.encode_cell(c) for c in cells],dtype=np.uint64);array.flags.writeable=False;return array


def encode_cores(cells):
    cells=tuple(cells)
    if not cells:raise ValueError('nonempty represented configuration required')
    g=layout();result=np.tile(template(),(len(cells),1))
    for i,c in enumerate(cells):result[i*g.computation_cells+np.array(g.info),r.COL['data']]=r.encode_cell(c)
    return result
