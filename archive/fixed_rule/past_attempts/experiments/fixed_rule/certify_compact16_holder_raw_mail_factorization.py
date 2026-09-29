"""All-clock factorization with independent raw mail replicas and physical flags.

The corrected mail is the actual five-holder bitwise majority, including the
valid bit. Output copies are masked by each holder's computed Flag1. This keeps
mail replica incoherence explicit instead of projecting it away.
"""
import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import resource
import time

from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_core as c, compact16_holder_program as p
from gacsca.fixed_rule.wordcode import ADD, LT
from experiments.fixed_rule import certify_compact16_holder_clock_mail_factorization as clock

MAIL=clock.regular.MAIL


def prepare(phase):
    original,old_raw,old_local=clock.prepare(phase)
    terms=clock.ClockTerms(p.base_rom());zero,one=terms.const(0),terms.const(1);mapping={}
    for x,(lo,hi) in original.ranges.items():
        node=original.nodes[x];mapping[x]=terms.bounded(node[1],node[2],lo,hi)
    def word(holder,slot,name):
        return terms.variable(f'mail_{holder}_{slot}_{name}',dict(c.SCHEMA)[name])
    @lru_cache(None)
    def corrected(site,name):
        values=[word(site+e,2-e,name) for e in f.OFFSETS]
        if dict(c.SCHEMA)[name]==1:
            count=zero
            for value in values:count=terms.op(ADD,count,value)
            return terms.not_(terms.op(LT,count,terms.const(3)))
        a,b,d,e,g=values
        triple=terms.band(terms.band(a,b),d)
        pairs=terms.bor(terms.bor(terms.band(a,b),terms.band(a,d)),terms.band(b,d))
        any3=terms.bor(terms.bor(a,b),d)
        return terms.bor(terms.bor(triple,terms.band(pairs,terms.bor(e,g))),terms.band(any3,terms.band(e,g)))
    def transfer(x):
        if x in mapping:return mapping[x]
        node=original.nodes[x]
        if node[0]=='const':y=terms.const(node[1])
        elif node[0]=='variable':
            parts=node[1].split('_',2)
            if len(parts)==3 and parts[0]=='proc' and parts[2] in MAIL:
                y=corrected(int(parts[1]),parts[2])
            else:y=terms.variable(node[1],node[2])
        elif node[0]=='op':y=terms.op(node[1],transfer(node[2]),transfer(node[3]))
        elif node[0]=='not':y=terms.inv(transfer(node[1]))
        elif node[0]=='modadd':y=terms.modular_add(transfer(node[1]),node[2],node[3])
        else:raise AssertionError(node)
        mapping[x]=y;return y
    def raw(pos,mail=True):
        values=[transfer(x) for x in old_raw(pos,mail=False)]
        if mail:
            for delta in f.OFFSETS:
                for name in MAIL:values[f.COL[f's{delta+2}_{name}']]=word(pos,delta+2,name)
        return tuple(values)
    def local(site,holder_flag):
        proxy=original.variable('bridge_flag_'+str(holder_flag),1)
        mapping[proxy]=holder_flag
        return {name:transfer(value) for name,value in old_local(site,proxy).items()}
    return terms,raw,local


def certify_case(phase):
    terms,raw,local=prepare(phase);description=f.self_description()
    holders=tuple(range(-4,5)) if phase is not None else (0,)
    for pos in holders:
        actual=terms.expression(description,tuple(w for j in f.NEIGHBORHOOD for w in raw(pos+j)))
        baseline=terms.expression(description,tuple(w for j in f.NEIGHBORHOOD for w in raw(pos+j,mail=False)))
        assert baseline[f.COL['address']]==raw(pos)[f.COL['address']]
        assert baseline[f.COL['age']]==terms.modular_add(raw(pos)[f.COL['age']],1,(f.U-1).bit_length())
        wanted=list(baseline)
        for delta in f.OFFSETS:
            for name,value in local(pos+delta,baseline[f.COL['f1']]).items():wanted[f.COL[f's{delta+2}_{name}']]=value
        for (name,_),a,b in zip(f.SCHEMA,actual,wanted):
            if a!=b:raise AssertionError((phase,pos,name,terms.nodes[a],terms.nodes[b]))
    return dict(phase=phase,passed=True,holders=list(holders),complete_raw_output_words=len(holders)*f.FIELDS,
                symbolic_terms=len(terms.nodes),all_clock_ages=f.U,independent_raw_mail_replicas=True,
                arbitrary_physical_flags_Signals_Wf=True,canonical_geometry_preserved=True)

