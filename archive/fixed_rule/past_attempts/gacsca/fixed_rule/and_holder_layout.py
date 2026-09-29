"""Experimental fixed ROM using typed identities for the same complete rule.

The physical procedures are fivefold protected by and_holder_rule. This module
builds their logical instruction stream and checks its full schedule once.
"""
from dataclasses import dataclass,replace
from functools import lru_cache
import numpy as np
from . import and_holder_rule as r,and_holder_core as c
from .word_program import Instruction
from .wordcode_and import LIT,ADD,NAND,EQ,Program
from .word_allocation_and import allocate
from .word_identity_and import optimize
from .word_and_fusion import fuse_exclusive_and
from .word_dag_order import reorder,verify


@lru_cache(maxsize=1)
def compiled_description():
    widths=tuple(width for _ in r.NEIGHBORHOOD for _,width in r.SCHEMA)
    optimized=optimize(r.self_description(),input_widths=widths)[0]
    fused=fuse_exclusive_and(optimized)[0]
    ordered,permutation=reorder(fused,reverse_outputs=True,children='original')
    assert verify(fused,ordered,permutation)
    return Program(ordered.inputs,ordered.operations,ordered.outputs)

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
        result=dict(Q=r.Q,U=r.U,core_cells=self.computation_cells,descriptor_operations=len(compiled_description().operations),gathers=gathers,evaluation_ticks=evaluation,evaluation_budget=c.ACTIVE_ENDS[4]-c.RESET_AGES[4],evaluation_margin=c.ACTIVE_ENDS[4]-c.RESET_AGES[4]-evaluation,stage3_head_stopped=third,stage3_last_delivery=last,capture_budget=c.CAPTURE_AGE-c.VOTE_AGES[0],capture_margin=c.CAPTURE_AGE-c.VOTE_AGES[0]-last,stage3_stop_margin=r.ACTIVE_ENDS[2]-c.VOTE_AGES[0]-third,third_evaluation_old_age=c.VOTE_AGES[0])
        result['fits']=all(row['margin']>0 for row in gathers) and result['evaluation_margin']>0 and result['capture_margin']>0 and result['stage3_stop_margin']>0
        return result
