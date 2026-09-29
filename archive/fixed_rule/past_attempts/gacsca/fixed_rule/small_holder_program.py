"""Fixed colony ROM computing the complete radius-seven holder rule.

The physical procedures are fivefold protected by small_holder_rule. This module
builds their logical instruction stream and checks its full schedule once.
"""
from dataclasses import dataclass,replace
from functools import lru_cache
import numpy as np
from . import small_holder_rule as r,small_holder_core as c
from .word_program import Instruction
from .wordcode import LIT,ADD,NAND,EQ
from .word_allocation import allocate

RADIUS=7
RESERVED=8
HISTORY_OFFSETS=(0,2,3)
RESULT_CAPACITY=384 # fixed compile-time layout choice, independent of depth

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
    description_instruction:int
    @property
    def computation_cells(self):return self.memory_count+len(self.instructions)+1
    @property
    def colony_cells(self):return r.Q
    @property
    def period_ticks(self):return r.U
    def history(self,stage,neighbor,field):return RESERVED+4*((neighbor+RADIUS)*r.FIELDS+field)+HISTORY_OFFSETS[stage]
    def schedule(self,start,end):
        phase,ticks=0,1;cycle=2*self.computation_cells;rows=[]
        for i in range(start,end):
            op=self.instructions[i];position=self.memory_count+i;targets=(position,)
            if op.kind in c.ALU_KINDS:targets+=(op.a,op.b,op.d)
            elif op.kind==LIT:targets+=(op.d,)
            elif op.kind in (c.SEND,c.LOAD):targets+=(op.a,)
            times=[]
            for target in targets:ticks+=(target-phase)%cycle+1;phase=(target+1)%cycle;times.append(ticks)
            if op.kind==c.META:ticks+=4*self.computation_cells+op.a-position;phase=op.a+1;times.append(ticks)
            rows.append(tuple(times))
        return ticks,tuple(rows)
    def timing_certificate(self):
        gathers=[]
        for stage,(start,end) in enumerate(self.stage_ranges[:3]):
            stopped,rows=self.schedule(start,end);packets=[]
            for op,times in zip(self.instructions[start:end],rows):
                if op.kind!=c.SEND:continue
                hops,direction=op.d>>1,op.d&1
                distance=hops*r.Q+(op.a-op.b if direction==c.LEFT else op.b-op.a)
                packets.append((direction,times[-1],op.a,distance))
            for i,(direction,t,source,distance) in enumerate(packets):
                line=(source+t if direction else source-t)%r.Q
                for direction2,u,source2,_ in packets[i+1:]:
                    if u>=t+distance or direction!=direction2:continue
                    if line==(source2+u if direction2 else source2-u)%r.Q:raise ValueError('same-track packet collision')
            arrival=max(t+distance for _,t,_,distance in packets);deadline=(c.VOTE_AGES[0] if stage==2 else c.ACTIVE_ENDS[stage])-c.RESET_AGES[stage]
            gathers.append(dict(stage=stage+1,head_stopped=stopped,last_arrival=arrival,deadline=deadline,margin=deadline-max(stopped,arrival)))
        evaluation,_=self.schedule(*self.stage_ranges[4]);third,rows=self.schedule(*self.delivery_range);last=0
        for op,times in zip(self.instructions[slice(*self.delivery_range)],rows):
            if op.kind==c.SEND:last=max(last,times[-1]+(op.a-op.b if op.d&1 else op.b-op.a))
        result=dict(Q=r.Q,U=r.U,core_cells=self.computation_cells,descriptor_operations=len(r.self_description().operations),gathers=gathers,evaluation_ticks=evaluation,evaluation_budget=c.ACTIVE_ENDS[4]-c.RESET_AGES[4],evaluation_margin=c.ACTIVE_ENDS[4]-c.RESET_AGES[4]-evaluation,stage3_head_stopped=third,stage3_last_delivery=last,capture_budget=c.CAPTURE_AGE-c.VOTE_AGES[0],capture_margin=c.CAPTURE_AGE-c.VOTE_AGES[0]-last,stage3_stop_margin=r.ACTIVE_ENDS[2]-c.VOTE_AGES[0]-third,third_evaluation_old_age=c.VOTE_AGES[0])
        result['fits']=all(row['margin']>0 for row in gathers) and result['evaluation_margin']>0 and result['capture_margin']>0 and result['stage3_stop_margin']>0
        return result


@lru_cache(maxsize=1)
def layout():
    desc=r.self_description();votes=tuple(RESERVED+4*i+1 for i in range(desc.inputs));info_start=RESERVED+4*desc.inputs
    info=tuple(info_start+2*i for i in range(r.FIELDS));hold=tuple(i+1 for i in info)
    # The output-copy ADDs still need the descriptor's zero after evaluation.
    zero_wire=next(desc.inputs+i for i,(kind,a,_) in enumerate(desc.operations) if kind==LIT and a==0)
    allocation=allocate(desc,pins=(zero_wire,),capacity=RESULT_CAPACITY)
    base=info_start+2*r.FIELDS;wires=votes+tuple(base+i for i in allocation.slots)
    temp=base+allocation.count;query=temp+5;memory=temp+6
    ops=[];entries=[];ranges=[]
    def regenerate(targets):
        for offset in r.STATIC_OFFSETS:
            source=targets[r.COL['address']]
            if offset:
                ops.extend((Instruction(LIT,offset&((1<<64)-1),0,temp),Instruction(ADD,source,temp,query),Instruction(LIT,r.Q-1,0,temp+1),Instruction(NAND,query,temp+1,temp+2),Instruction(NAND,temp+2,temp+2,query)));source=query
            for selector,name in enumerate(c.STATIC):ops.extend((Instruction(c.LOAD,source,0,0),Instruction(c.META,targets[r.COL[f'p{offset+3}_{name}']],selector,0)))
    for stage in range(3):
        start=len(ops);entries.append(start)
        if stage==0:regenerate(info)
        ops.append(Instruction(LIT,0,0,temp))
        for i,source in enumerate(info):ops.append(Instruction(ADD,source,temp,RESERVED+4*(RADIUS*r.FIELDS+i)+HISTORY_OFFSETS[stage]))
        for hops in range(1,RADIUS+1):
            for word,source in enumerate(info):
                for direction,neighbor in ((c.LEFT,hops),(c.RIGHT,-hops)):
                    target=RESERVED+4*((RADIUS+neighbor)*r.FIELDS+word)+HISTORY_OFFSETS[stage];ops.append(Instruction(c.SEND,source,target,(hops<<1)|direction))
        ops.append(Instruction(c.HALT,0,0,0));ranges.append((start,len(ops)))
    entries.append(len(ops));ops.append(Instruction(c.HALT,0,0,0));ranges.append((entries[3],len(ops)))
    entries.append(len(ops));start=len(ops)
    description_instruction=len(ops)
    for i,(kind,a,b) in enumerate(desc.operations):
        left,right=(a,0) if kind==LIT else (wires[a],wires[b])
        if kind in (NAND,ADD,EQ) and left>right:left,right=right,left
        ops.append(Instruction(kind,left,right,wires[desc.inputs+i]))
    zero=next(wires[desc.inputs+i] for i,(kind,a,_) in enumerate(desc.operations) if kind==LIT and a==0)
    for target,output in zip(hold,desc.outputs):ops.append(Instruction(ADD,wires[output],zero,target))
    regenerate(hold);ops.append(Instruction(c.IF_THIRD,0,0,0));ranges.append((start,len(ops)))
    for target in range(1,6):ops.append(Instruction(c.SEND,hold[r.COL['f2']],target,c.LEFT))
    for target in range(r.Q-5,r.Q):ops.append(Instruction(c.SEND,hold[r.COL['f1']],target,c.RIGHT))
    ops.append(Instruction(c.HALT,0,0,0));delivery=(start,len(ops))
    result=Layout(memory,tuple(ops),tuple(entries),info,hold,votes,wires,tuple(ranges),desc.digest(),delivery,description_instruction)
    if result.computation_cells>=r.Q or max(memory,len(ops))>=1<<32:raise ValueError('fixed capacity exceeded')
    return result


@lru_cache(maxsize=1)
def base_template():
    g=layout();cells=[c.Cell(index=i,address=i,a=31,first=int(i==0)) for i in range(g.memory_count)]
    for word,vote in enumerate(g.votes):
        group=RESERVED+4*word
        for stage,offset in enumerate(HISTORY_OFFSETS):cells[group+offset]=replace(cells[group+offset],a=(1<<(stage+1))-1)
        cells[vote]=replace(cells[vote],a=31|c.VOTE)
    for address in g.info:cells[address]=replace(cells[address],a=c.INFO)
    cells[0]=replace(cells[0],a=g.entries[0]|g.entries[1]<<32,b=g.entries[2]|g.entries[3]<<32,d=g.entries[4])
    cells.extend(c.Cell(kind=op.kind,index=i,a=op.a,b=op.b,d=op.d,address=g.memory_count+i) for i,op in enumerate(g.instructions))
    cells.append(c.Cell(kind=c.LOOP,index=len(g.instructions),address=len(cells),last=1))
    return tuple(cells)


@lru_cache(maxsize=1)
def base_rom():
    out=np.array([[getattr(cell,n) for n in c.STATIC] for cell in base_template()],dtype=np.uint64);out.flags.writeable=False;return out
