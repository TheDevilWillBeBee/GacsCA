"""Canonical all-clock Signal/flag formulas and directed flag clearing bound.

Selected outputs of the complete physical descriptor, with arbitrary other raw
fields. No execution backend or host replacement of simulated transitions.
"""
import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import resource
import time

from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_core as c, compact16_holder_program as p
from gacsca.fixed_rule.wordcode import ADD, EQ, LT, SHR, Program
from gacsca.fixed_rule.word_prune import prune
from gacsca.fixed_rule.word_bdd import BDD
from experiments.fixed_rule.certify_compact16_holder_clock_mail_factorization import ClockTerms

NAMES=('address','age','f1','f2','signal',*(f'w{d+2}_{name}' for d in f.OFFSETS for name in ('wf1','wf2')))


def prepare(*,zero_wf=False,interval=(0,f.U-1)):
    t=ClockTerms(p.base_rom());zero,one=t.const(0),t.const(1)
    address=t.variable('base_address',(f.Q-1).bit_length());age=t.bounded('physical_age',32,*interval)
    @lru_cache(None)
    def raw(site):
        return tuple(t.modular_add(address,site,(f.Q-1).bit_length()) if name=='address' else age if name=='age'
                     else zero if zero_wf and name.startswith('w')
                     else t.variable(f'raw_{site}_{name}',width) for name,width in f.SCHEMA)
    def field(site,name):return raw(site)[f.COL[name]]
    def eq(x,value):return t.op(EQ,x,t.const(value))
    def threshold(bits,k):
        count=zero
        for value in bits:count=t.op(ADD,count,value)
        return t.not_(t.op(LT,count,t.const(k)))
    def inside(site,offset):
        a=field(site,'address')
        return t.not_(t.op(LT,a,t.const(-offset))) if offset<0 else t.op(LT,a,t.const(f.Q-offset)) if offset>0 else one
    @lru_cache(None)
    def flags(site):
        right=[t.band(inside(site,j),field(site+j,'f1')) for j in range(1,6)]
        force1=threshold([t.band(inside(site,j),field(site+j,'w2_wf1')) for j in range(-5,6)],3)
        new1=t.any(force1,threshold(right,3),t.band(field(site,'f1'),threshold(right,2)))
        left=[field(site-j,'f2') for j in range(1,6)]
        local=[t.band(inside(site,-j),field(site-j,'f2')) for j in range(1,6)]
        force2=threshold([t.band(inside(site,j),field(site+j,'w2_wf2')) for j in range(-5,6)],3)
        born=t.any(threshold(local,4),t.band(new1,threshold(left,4)),force2)
        erase=t.any(t.all(t.not_(new1),t.not_(threshold(local,2))),t.all(new1,t.not_(t.any(*left))))
        new2=t.select(field(site,'f2'),t.any(force2,t.not_(erase)),born)
        return new1,new2
    @lru_cache(None)
    def signal_vote(primary):
        return threshold([t.band(t.op(SHR,field(primary+e,'signal'),t.const(2-e)),one) for e in f.OFFSETS],3)
    def corrected_data(site):
        a,b,d,e,g=[field(site+offset,f's{2-offset}_data') for offset in f.OFFSETS]
        triple=t.band(t.band(a,b),d)
        pairs=t.bor(t.bor(t.band(a,b),t.band(a,d)),t.band(b,d))
        any3=t.bor(t.bor(a,b),d)
        return t.bor(t.bor(triple,t.band(pairs,t.bor(e,g))),t.band(any3,t.band(e,g)))
    def expected(site):
        at=field(site,'address');next_age=t.modular_add(age,1,(f.U-1).bit_length())
        f1,f2=flags(site);signal=zero;capture=eq(next_age,c.CAPTURE_AGE)
        data=t.band(corrected_data(site),one)
        for delta in f.OFFSETS:
            hit=t.any(*(eq(at,target-delta) for target in (3,f.Q-3)))
            bit=t.select(t.all(capture,hit),data,signal_vote(site+delta))
            for _ in range(delta+2):bit=t.op(ADD,bit,bit)
            signal=t.bor(signal,bit)
        result=dict(address=at,age=next_age,f1=f1,f2=f2,signal=signal)
        window=t.all(t.not_(t.op(LT,next_age,t.const(c.WF_START))),t.op(LT,next_age,t.const(c.WF_END)))
        for delta in f.OFFSETS:
            a=field(site+delta,'address')
            # Keep the exact logical target, including adjacent-colony Signals.
            wf1=t.any(*(t.all(eq(a,k),signal_vote(site+delta+f.Q-3-k)) for k in range(f.Q-5,f.Q)))
            wf2=t.any(*(t.all(eq(a,k),signal_vote(site+delta+3-k)) for k in range(5)))
            result[f'w{delta+2}_wf1']=t.all(window,wf1)
            result[f'w{delta+2}_wf2']=t.all(window,t.not_(flags(site+delta)[0]),wf2)
        return result
    return t,raw,flags,expected


def certify_formulas():
    t,raw,_,expected=prepare();desc=f.self_description()
    selected=prune(Program(desc.inputs,desc.operations,tuple(desc.outputs[f.COL[name]] for name in NAMES)))
    actual=t.expression(selected,tuple(word for j in f.NEIGHBORHOOD for word in raw(j)))
    wanted=expected(0)
    for name,value in zip(NAMES,actual):
        assert value==wanted[name],('canonical boundary formula',name,t.nodes[value],t.nodes[wanted[name]] )
    return dict(passed=True,checked_words=list(NAMES),all_addresses=f.Q,all_clock_ages=f.U,
                arbitrary_raw_fields=True,symbolic_terms=len(t.nodes),selected_operations=len(selected.operations))


def clearing_implications():
    b=BDD(6);own=b.variable(0);neighbors=[b.variable(i) for i in range(1,6)]
    def threshold(bits,k):
        count=[1]+[0]*k
        for bit in bits:
            for j in range(k,0,-1):count[j]=b.or_(count[j],b.and_(count[j-1],bit))
        return count[k]
    one=b.or_(threshold(neighbors,3),b.and_(own,threshold(neighbors,2)))
    two=b.or_(b.and_(own,threshold(neighbors,2)),b.and_(b.inv(own),threshold(neighbors,4)))
    distant=0
    for bit in neighbors[1:]:distant=b.or_(distant,bit)
    assert b.and_(one,b.inv(distant))==0
    assert b.and_(two,b.inv(distant))==0
    assert b.value(one,0)==b.value(two,0)==0
    result=dict(passed=True,assignments=64,BDD_nodes=len(b.nodes),
                Flag1='With Wf1=0, a new one requires an old in-colony Flag1 at offset +2..+5.',
                Flag2='With Wf2=0 and computed Flag1=0, a new one requires an old in-colony Flag2 at offset -2..-5.',
                per_flag_clearing_ticks=(f.Q+1)//2,total_clearing_ticks=2*((f.Q+1)//2))
    b.binary.cache_clear();return result


def off_window():
    rows=[]
    for interval in ((0,c.WF_START-2),(c.WF_END,f.U-2),(f.U-1,f.U-1)):
        t,raw,_,expected=prepare(zero_wf=True,interval=interval)
        wanted=expected(0)
        assert all(wanted[name]==t.const(0) for name in NAMES if name.startswith('w'))
        rows.append(dict(old_age_interval=interval,passed=True,new_Wf_all_zero=True))
    assert c.WF_END+f.Q<c.RESET_AGES[4]
    assert c.CAPTURE_AGE<c.WF_START
    return dict(passed=True,intervals=rows,clearing_start_age=c.WF_END,
                both_flags_zero_by_age=c.WF_END+f.Q,final_evaluation_entry_age=c.RESET_AGES[4],
                margin_before_final_evaluation=c.RESET_AGES[4]-c.WF_END-f.Q,
                limitation='Clearing assumes zero Wf throughout the interval. At old Age WF_END-1 the formula sets all next Wf to zero; flags at that cutoff may be arbitrary.')

