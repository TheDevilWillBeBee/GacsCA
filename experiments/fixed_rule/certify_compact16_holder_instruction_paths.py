"""Conditional physical refinement of ordinary instructions in the fixed ROM.

Diagnostic only. Leaf identities come from the complete raw rule. Every flight
checks ROM/preconditions and preserves its full controller; memory is shared by
address so aliased operands denote the same old word. SEND ends at packet birth;
composition with its later transport is an explicit remaining obligation.
"""
import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import resource
import time

import numpy as np
from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_core as c, compact16_holder_program as p
from gacsca.fixed_rule.wordcode import LIT, EQ
from experiments.fixed_rule import certify_compact16_holder_clock_events as clock
from experiments.fixed_rule import certify_compact16_holder_meta_paths as meta
from experiments.fixed_rule.certify_compact16_holder_event_support import certify as support
from experiments.fixed_rule.audit_small_holder_position_events import sha

PACKETS=tuple(name for name,_ in c.SCHEMA if name.startswith(('lp_','rp_')))
PHASES=(c.READ_A,c.READ_B,c.WRITE,c.TRANSMIT,c.READ_LOAD)


def nonmemory_cases():
    return tuple(('nonmem',f'{role}_{phase}') for role in ('flight','reflect') for phase in PHASES)


def leaf_prepare(key,interval):
    family,name=key
    if family!='nonmem':
        return meta.leaf_prepare(key,interval)
    role,phase=name.split('_');phase=int(phase)
    original=('scan',f'right_{role}_{phase}')
    terms,raw=clock.prepare(meta.EVENTS[original],interval)
    # These phases can act on matching indices only when kind==MEM. No index
    # disequality is needed on an instruction/endpoint site of nonzero kind.
    terms.disequalities.clear()
    terms.unequal(raw(0)[f.COL['p3_kind']],terms.const(c.MEM))
    return terms,raw


def prove_leaf(key,interval):
    terms,raw=leaf_prepare(key,interval);desc=f.self_description()
    for pos in range(-4,5):
        actual=terms.expression(desc,tuple(w for j in f.NEIGHBORHOOD for w in raw(pos+j)))
        assert actual==raw(pos,after=True),(key,interval,pos)
    return dict(leaf=key,interval=interval,passed=True,full_raw_outputs=9*f.FIELDS)


@lru_cache(None)
def template(key,third):
    interval=clock.regular_intervals()[2 if third else 0]
    terms,raw=leaf_prepare(key,interval);before=raw(0)
    destinations=[d for d in (-1,0,1) if terms.value(raw(d,after=True)[f.COL['s2_head']])==1]
    assert len(destinations)<=1
    shift=destinations[0] if destinations else None
    return terms,before,raw(shift or 0,after=True),raw(0,after=True),shift


class InstructionPath:
    def __init__(self,pc,*,third=False):
        self.g=p.layout();self.rom=p.base_rom();self.L=len(self.rom);self.pc=pc;self.op=self.g.instructions[pc]
        assert self.op.kind!=c.META,'META has its separate full scan certificate'
        self.third=third;self.m=self.g.memory_count+pc;self.position=self.m;self.elapsed=0;self.live=True
        self.t=meta.Words(self.rom)
        self.initial={name:self.t.variable('initial_'+name,dict(c.SCHEMA)[name]) for name in c.CONTROL}
        self.initial.update(phase=self.t.const(c.FETCH),pc=self.t.const(pc),direction=self.t.const(c.RIGHT))
        self.control=dict(self.initial);self.initial_memory={};self.memory={};self.writes=[];self.emissions=[];self.steps=[]

    def read(self,address):
        assert 0<=address<self.g.memory_count,('operand outside scanned memory prefix',address)
        if address not in self.initial_memory:self.initial_memory[address]=self.t.variable('memory_'+str(address),64)
        return self.memory.get(address,self.initial_memory[address])

    def event(self,key,*,count=1,loop=False):
        assert self.live and type(count) is int and count>=0
        if not count:return
        source,before,after,own_after,shift=template(key,self.third)
        if loop:assert shift in (-1,1)
        else:assert count==1
        last=self.position+(count-1)*(shift or 0);lo,hi=sorted((self.position,last))
        assert 0<=lo<=hi<self.L
        head=self.t.const(lo) if lo==hi else self.t.bounded('flight_head_'+str(len(self.steps)),(f.Q-1).bit_length(),lo,hi)
        memory=self.t.variable('flight_data_'+str(len(self.steps)),64) if loop else self.read(self.position) if self.position<self.g.memory_count else self.t.const(0)
        mapping={}
        def transfer(x):
            if x in mapping:return mapping[x]
            node=source.nodes[x]
            if node[0]=='const':y=self.t.const(node[1])
            elif node[0]=='variable':
                name=node[1]
                if name.startswith('fetch_old_'):y=self.control[name[len('fetch_old_'):]]
                elif name.startswith('old_'):y=self.control[name[len('old_'):]]
                elif name=='base_address':y=head
                elif name.startswith('meta_0_'):y=self.t.lookup(head,c.STATIC.index(name[len('meta_0_'):]))
                elif name=='data_0':y=memory
                else:raise AssertionError(('unexpected controller dependency',key,node))
            elif node[0]=='op':y=self.t.op(node[1],transfer(node[2]),transfer(node[3]))
            elif node[0]=='not':y=self.t.inv(transfer(node[1]))
            elif node[0]=='modadd':y=self.t.modular_add(transfer(node[1]),node[2],node[3])
            else:raise AssertionError(node)
            mapping[x]=y;return y
        for name in c.CONTROL:
            assert transfer(before[f.COL['s2_'+name]])==self.control[name],('controller precondition',key,name)
        for selector,name in enumerate(c.STATIC):
            assert transfer(before[f.COL['p3_'+name]])==self.t.lookup(head,selector),('ROM precondition',key,name,lo,hi)
        for a,b in source.disequalities:
            a,b=transfer(a),transfer(b)
            if self.t.value(self.t.op(EQ,a,b))==0:continue
            if {a,b}=={self.t.lookup(head,0),self.t.const(c.MEM)}:
                assert np.all(self.rom[lo:hi+1,0]!=c.MEM),('non-MEM guard',key,lo,hi)
            else:raise AssertionError(('unproved flight guard',key,self.t.nodes[a],self.t.nodes[b]))
        new={name:transfer(after[f.COL['s2_'+name]]) for name in c.CONTROL}
        data=transfer(own_after[f.COL['s2_data']])
        packets={name:transfer(own_after[f.COL['s2_'+name]]) for name in PACKETS}
        has_packet=any(self.t.value(value)!=0 for value in packets.values())
        if loop:
            assert new==self.control and data==memory and not has_packet,('non-invariant flight',key)
        else:
            if data!=memory:self.writes.append((self.position,data));self.memory[self.position]=data
            if has_packet:self.emissions.append((self.position,packets))
        self.steps.append(dict(leaf=key,start=self.position,count=count,shift=shift,head_range=(lo,hi)))
        self.control=new;self.elapsed+=count
        if shift is None:self.live=False;self.position=None
        else:self.position+=shift*count

    def fly_right(self,stop,phase):
        """Reach stop without processing it; split memory/non-memory guards."""
        assert self.t.value(self.control['direction'])==c.RIGHT
        assert self.position<=stop<self.L
        if self.position<self.g.memory_count:
            end=min(stop,self.g.memory_count)
            self.event(('scan',f'right_flight_{phase}'),count=end-self.position,loop=True)
        if self.position<stop:
            self.event(('nonmem',f'flight_{phase}'),count=stop-self.position,loop=True)
        assert self.position==stop

    def seek(self,target,phase):
        assert 0<=target<self.g.memory_count and self.t.value(self.control['phase'])==phase
        start=self.position;before=self.elapsed
        if target<self.position:
            self.fly_right(self.L-1,phase)
            self.event(('nonmem',f'reflect_{phase}'))
            self.event(meta.LAST_LEFT)
            self.event(('scan','left_flight'),count=self.L-2,loop=True)
            self.event(('scan',f'left_reflect_{phase}'))
        self.fly_right(target,phase)
        assert self.elapsed-before==(target-start)%(2*self.L),'physical scan differs from cyclic schedule'

    def check(self):
        op=self.op;t=self.t;kind=op.kind;inputs={}
        if kind in c.ALU_KINDS:
            inputs={a:self.read(a) for a in (op.a,op.b)}
        elif kind in (c.LOAD,c.SEND):inputs={op.a:self.read(op.a)}
        self.event(('fetch',f'fetch_{kind}_0'))
        targets=[]
        if kind in c.ALU_KINDS:
            for address,phase,leaf in ((op.a,c.READ_A,'read_a'),(op.b,c.READ_B,f'read_b_{kind}'),(op.d,c.WRITE,'write')):
                self.seek(address,phase);self.event(('position',leaf));targets.append(address)
        elif kind==LIT:
            self.seek(op.d,c.WRITE);self.event(('position','write'));targets.append(op.d)
        elif kind==c.LOAD:
            self.seek(op.a,c.READ_LOAD);self.event(('position','load'));targets.append(op.a)
        elif kind==c.SEND:
            self.seek(op.a,c.TRANSMIT);self.event(('position',f'send_{op.d&1}_{op.d>>1}'));targets.append(op.a)
        elif kind not in (c.HALT,c.IF_THIRD):raise AssertionError(('unexpected fixed-ROM opcode',kind))
        # Independent completed-instruction contract, including stale fields.
        wanted=dict(self.initial);writes=[];emissions=[]
        if kind==c.HALT or (kind==c.IF_THIRD and not self.third):
            wanted={name:t.const(0) for name in c.CONTROL};end=None
        else:
            wanted.update(phase=t.const(c.FETCH),pc=t.const(self.pc+1),direction=t.const(c.RIGHT))
            end=(targets[-1]+1) if targets else self.m+1
            if kind in c.ALU_KINDS:
                result=t.op(kind,inputs[op.a],inputs[op.b]);wanted.update(ra=t.const(op.a),rb=t.const(op.b),rd=t.const(op.d),alu=t.const(kind),value=result);writes=[(op.d,result)]
            elif kind==LIT:
                result=t.const(op.a);wanted.update(rd=t.const(op.d),value=result);writes=[(op.d,result)]
            elif kind==c.LOAD:wanted.update(ra=t.const(op.a),rd=inputs[op.a])
            elif kind==c.SEND:
                wanted.update(ra=t.const(op.a),rb=t.const(op.b),rd=t.const(op.d))
                track='lp' if op.d&1 else 'rp';packet={name:t.const(0) for name in PACKETS}
                packet.update({track+'_target':t.const(op.b),track+'_data':inputs[op.a],track+'_remaining':t.const(op.d>>1),track+'_valid':t.const(1)})
                emissions=[(op.a,packet)]
        assert self.control==wanted,'incomplete final controller contract'
        assert self.writes==writes and self.emissions==emissions,'wrong Data/packet effect'
        assert self.position==end and self.live==(end is not None)
        phase=self.m;duration=0
        for target in (self.m,*targets):duration+=(target-phase)%(2*self.L)+1;phase=target+1
        assert self.elapsed==duration,'complete duration differs from schedule recipe'
        intervals=[]
        for lo,hi in clock.regular_intervals():
            is_third=c.RESET_AGES[2]<=lo<=hi<c.ACTIVE_ENDS[2]
            if kind==c.IF_THIRD and is_third!=self.third:continue
            assert duration<=hi-lo+1
            intervals.append((lo,hi-duration+1))
        return dict(pc=self.pc,kind=kind,third=self.third,duration=duration,final_head=end,targets=targets,
                    legal_start_age_intervals=intervals,leaf_segments=len(self.steps),memory_aliases=len(inputs)<(2 if kind in c.ALU_KINDS else len(inputs)),
                    full_controller_Data_and_packet_contract=True)

