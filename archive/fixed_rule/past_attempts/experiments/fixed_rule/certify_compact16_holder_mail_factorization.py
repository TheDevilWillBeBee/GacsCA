"""General mail erasure/decomposition relation for the complete physical rule.

The baseline is F with old mail erased; only Data/mail outputs are replaced by
explicit transport, delivery, write and send formulas. This is a diagnostic
reduction lemma, not an evolution backend or independent proof of baseline F.
"""
import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import resource
import time

from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_core as c, compact16_holder_program as p
from gacsca.fixed_rule.wordcode import ADD, EQ, LT, NAND, SHR, LIT, MASK
from experiments.fixed_rule import certify_compact16_holder_clock_events as clock
from experiments.fixed_rule.prove_small_holder_boundary import validate

MAIL=tuple(name for name,_ in c.SCHEMA if name.startswith(('lp_','rp_')))


class BooleanTerms(clock.Intervals):
    def boolean_multiple(self,x):
        if self.width(x)<=1:return x,1
        node=self.nodes[x]
        if node[0]=='op' and node[1]==ADD:
            a=self.boolean_multiple(node[2]);b=self.boolean_multiple(node[3])
            if a is not None and b is not None and a[0]==b[0] and a[1]+b[1]<=MASK:
                return a[0],a[1]+b[1]
        return None
    def op(self,kind,a,b):
        if kind==LT and self.value(b) is not None:
            multiple=self.boolean_multiple(a)
            if multiple is not None and 1<=self.value(b)<=multiple[1]:
                return self.op(EQ,multiple[0],self.const(0))
        if kind==EQ:
            for x,y in ((a,b),(b,a)):
                value=self.value(y)
                if value==1 and self.width(x)<=1:return x
                node=self.nodes[x]
                if value==0 and node[0]=='op' and node[1]==EQ:
                    for inner,z in ((node[2],node[3]),(node[3],node[2])):
                        if self.value(z)==0 and self.width(inner)<=1:return inner
        return super().op(kind,a,b)
    def not_(self,x):return self.op(EQ,x,self.const(0))
    def nonzero(self,x):return self.not_(self.not_(x))
    def all(self,*values):
        out=self.const(1)
        for value in values:out=self.band(out,value)
        return out
    def select(self,condition,yes,no):
        if yes==no:return yes
        mask=self.op(ADD,self.inv(condition),self.const(1))
        return self.op(NAND,self.op(NAND,mask,yes),self.op(NAND,self.inv(mask),no))


def certify_support(description=None):
    desc=f.self_description() if description is None else description;validate(desc)
    @lru_cache(None)
    def used(wire):
        if wire<desc.inputs:return frozenset((wire,))
        kind,a,b=desc.operations[wire-desc.inputs]
        return frozenset() if kind==LIT else used(a)|used(b)
    result={};controller=0
    for (name,_),wire in zip(f.SCHEMA,desc.outputs):
        fields={f.SCHEMA[x%f.FIELDS][0] for x in used(wire)}
        suffix=name.split('_',1)[1] if name.startswith(tuple('s'+str(k)+'_' for k in range(5))) else None
        packet_inputs=sorted(x for x in fields if x.split('_',1)[-1] in MAIL)
        if suffix not in ('data',*MAIL):
            assert not packet_inputs,('mail affects non-Data/non-mail output',name,packet_inputs)
            if suffix in ('head',*c.CONTROL):controller+=1
        if suffix in MAIL:
            channel=suffix[:2]
            assert all(x.split('_',1)[1].startswith(channel+'_') for x in packet_inputs),('cross-track dependency',name)
        result[name]=packet_inputs
    assert controller==5*(1+len(c.CONTROL))
    return dict(passed=True,controller_outputs_independent_of_all_old_mail=controller,
                all_other_nonData_nonmail_outputs_independent=True,packet_outputs_track_separable=True,
                mail_input_fields_by_output=result,descriptor_sha256=desc.digest(),
                domain='Every raw finite-alphabet neighborhood; no coherence, clock, head-count or noise hypothesis.')


def prepare(phase,interval):
    assert phase is None or phase in range(8)
    t=BooleanTerms(p.base_rom());zero,one=t.const(0),t.const(1)
    address=t.variable('base_address',(f.Q-1).bit_length());age=t.bounded('physical_age',32,*interval)
    cells={}
    for site in range(-16,17):
        row={name:zero for name,_ in c.SCHEMA}
        row.update({name:t.variable(f'meta_{site}_{name}',dict(c.SCHEMA)[name]) for name in c.STATIC})
        row.update({name:t.variable(f'proc_{site}_{name}',dict(c.SCHEMA)[name]) for name in ('data',*MAIL)})
        row.update(address=t.modular_add(address,site,(f.Q-1).bit_length()),age=age)
        if site==0 and phase is not None:
            row.update({name:t.variable('old_'+name,dict(c.SCHEMA)[name]) for name in c.CONTROL})
            row.update(head=one,phase=t.const(phase))
        cells[site]=row
    def raw(pos,mail=True):
        row={name:zero for name,_ in f.SCHEMA}
        row.update(address=t.modular_add(address,pos,(f.Q-1).bit_length()),age=age)
        for delta in f.STATIC_OFFSETS:
            for name in c.STATIC:row[f'p{delta+3}_{name}']=cells[pos+delta][name]
        for delta in f.OFFSETS:
            for name,_ in f.PROCEDURE:
                row[f's{delta+2}_{name}']=zero if not mail and name in MAIL else cells[pos+delta][name]
        return tuple(row[name] for name,_ in f.SCHEMA)
    def local_outputs(site):
        own=cells[site];result={};data=own['data']
        eq=lambda x,y:t.op(EQ,x,y)
        def condition(mode,register):
            return t.all(eq(own['kind'],t.const(c.MEM)),eq(own['phase'],t.const(mode)),eq(own['index'],own[register]))
        executing=t.all(own['head'],t.not_(own['direction']))
        sending=t.band(executing,condition(c.TRANSMIT,'ra'))
        for channel,offset,edge_value in (('lp',1,0),('rp',-1,f.Q-1)):
            source=cells[site+offset];count=source[channel+'_remaining']
            edge=eq(source['address'],t.const(edge_value))
            valid=t.all(source[channel+'_valid'],t.not_(t.all(edge,t.not_(count))))
            remaining=t.select(t.all(edge,t.nonzero(count)),t.op(ADD,count,t.const(MASK)),count)
            hit=t.all(valid,t.not_(remaining),eq(own['kind'],t.const(c.MEM)),eq(own['index'],source[channel+'_target']))
            moving=t.all(valid,t.not_(hit));data=t.select(hit,source[channel+'_data'],data)
            direction=t.band(own['rd'],one)
            emit=t.band(sending,direction if channel=='lp' else t.not_(direction))
            for suffix,value,fresh in (('target',source[channel+'_target'],t.mask(own['rb'],32)),
                                       ('data',source[channel+'_data'],own['data']),
                                       ('remaining',remaining,t.mask(t.op(SHR,own['rd'],one),3)),('valid',one,one)):
                result[channel+'_'+suffix]=t.select(emit,fresh,t.select(moving,value,zero))
        result['data']=t.select(t.band(executing,condition(c.WRITE,'rd')),own['value'],data)
        return result
    return t,raw,local_outputs


def certify_case(phase,interval):
    desc=f.self_description();t,raw,local=prepare(phase,interval)
    outputs=range(-4,5) if phase is not None else (0,)
    for pos in outputs:
        actual=t.expression(desc,tuple(w for j in f.NEIGHBORHOOD for w in raw(pos+j)))
        wanted=list(t.expression(desc,tuple(w for j in f.NEIGHBORHOOD for w in raw(pos+j,mail=False))))
        for delta in f.OFFSETS:
            for name,value in local(pos+delta).items():wanted[f.COL[f's{delta+2}_{name}']]=value
        for (name,_),a,b in zip(f.SCHEMA,actual,wanted):
            if a!=b:raise AssertionError((phase,interval,pos,name,t.nodes[a],t.nodes[b]))
    return dict(phase=phase,interval=interval,passed=True,holders=list(outputs),full_raw_output_words=len(outputs)*f.FIELDS,
                symbolic_terms=len(t.nodes),arbitrary_packet_words=True,arbitrary_direction_and_metadata=True)

