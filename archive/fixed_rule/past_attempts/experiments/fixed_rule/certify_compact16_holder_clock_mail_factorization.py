"""All-clock mail factorization with canonical geometry and arbitrary raw flags.

Complete raw outputs are compared. The mail-erased physical F supplies baseline
control/geometry/Signal/Wf; independent clocked Data/mail formulas supply the
replacement fields. This is a reduction lemma, not an evolution backend.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time

from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_core as c, compact16_holder_program as p
from gacsca.fixed_rule.wordcode import ADD, EQ, LT, NAND, SHR
from experiments.fixed_rule import certify_compact16_holder_mail_factorization as regular


class ClockTerms(regular.BooleanTerms):
    def op(self,kind,a,b):
        if kind==NAND:
            left,right=self.nodes[a],self.nodes[b]
            if left[0]=='op' and left[1]==NAND and right[0]=='op' and right[1]==NAND:
                for x,m in ((left[2],left[3]),(left[3],left[2])):
                    for y,n in ((right[2],right[3]),(right[3],right[2])):
                        if x==y and self.inv(m)==n:
                            return x  # (m & x) | (~m & x) = x, for arbitrary words.
        return super().op(kind,a,b)
    def bor(self,a,b):return self.op(NAND,self.inv(a),self.inv(b))
    def any(self,*values):
        result=self.const(0)
        for value in values:result=self.bor(result,value)
        return result


def prepare(phase):
    original,original_raw,original_local=regular.prepare(phase,(0,f.U-1))
    terms=ClockTerms(p.base_rom());zero,one=terms.const(0),terms.const(1);mapping={}
    for x,(lo,hi) in original.ranges.items():
        node=original.nodes[x];mapping[x]=terms.bounded(node[1],node[2],lo,hi)
    def transfer(x):
        if x in mapping:return mapping[x]
        node=original.nodes[x]
        if node[0]=='const':y=terms.const(node[1])
        elif node[0]=='variable':y=terms.variable(node[1],node[2])
        elif node[0]=='op':y=terms.op(node[1],transfer(node[2]),transfer(node[3]))
        elif node[0]=='not':y=terms.inv(transfer(node[1]))
        elif node[0]=='modadd':y=terms.modular_add(transfer(node[1]),node[2],node[3])
        else:raise AssertionError(node)
        mapping[x]=y;return y
    def raw(pos,mail=True):
        values=[transfer(x) for x in original_raw(pos,mail=mail)]
        for name,width in (('f1',1),('f2',1),('signal',5),*((f'w{d+2}_{name}',1) for d in f.OFFSETS for name in ('wf1','wf2'))):
            values[f.COL[name]]=terms.variable(f'physical_{pos}_{name}',width)
        return tuple(values)
    def cell(site,name):
        key='p3_'+name if name in c.STATIC else name if name in ('address','age') else 's2_'+name
        return raw(site)[f.COL[key]]
    age=cell(0,'age')
    eq=lambda x,value:terms.op(EQ,x,terms.const(value))
    active=terms.any(*(terms.all(terms.not_(terms.op(LT,age,terms.const(lo))),terms.op(LT,age,terms.const(hi))) for lo,hi in zip(c.RESET_AGES,c.ACTIVE_ENDS)))
    reset=[eq(age,at) for at in c.RESET_AGES];any_reset=terms.any(*reset)
    def local(site,holder_flag):
        work={name:transfer(value) for name,value in original_local(site).items()}
        data=terms.select(active,work['data'],cell(site,'data'))
        marked=terms.any(*(terms.all(predicate,terms.band(terms.op(SHR,cell(site,'a'),terms.const(stage)),one)) for stage,predicate in enumerate(reset)))
        erase=terms.all(any_reset,terms.any(cell(site,'first'),terms.all(eq(cell(site,'kind'),c.MEM),marked)))
        data=terms.select(erase,zero,data)
        vote=terms.all(eq(cell(site,'kind'),c.MEM),terms.not_(cell(site,'first')),
                       terms.nonzero(terms.band(cell(site,'a'),terms.const(c.VOTE))),
                       terms.any(*(eq(age,at) for at in c.VOTE_AGES)))
        a,b,d=(cell(site+j,'data') for j in (-1,1,2))
        majority=terms.bor(terms.bor(terms.band(a,b),terms.band(a,d)),terms.band(b,d))
        data=terms.select(vote,majority,data)
        commit=terms.all(eq(cell(site,'kind'),c.MEM),terms.not_(cell(site,'first')),
                         terms.nonzero(terms.band(cell(site,'a'),terms.const(c.INFO))),eq(age,f.U-1))
        data=terms.select(commit,cell(site+1,'data'),data)
        result={'data':data}
        for name in regular.MAIL:
            value=terms.select(active,work[name],cell(site,name))
            value=terms.select(any_reset,zero,value)
            result[name]=terms.select(holder_flag,zero,value)
        return result
    return terms,raw,local


def certify_case(phase):
    terms,raw,local=prepare(phase);description=f.self_description()
    holders=tuple(range(-4,5)) if phase is not None else (0,)
    for pos in holders:
        actual=terms.expression(description,tuple(w for j in f.NEIGHBORHOOD for w in raw(pos+j)))
        baseline=terms.expression(description,tuple(w for j in f.NEIGHBORHOOD for w in raw(pos+j,mail=False)))
        # Canonical geometry is retained even with arbitrary physical flags/Wf.
        assert baseline[f.COL['address']]==raw(pos)[f.COL['address']],('Address',phase,pos)
        assert baseline[f.COL['age']]==terms.modular_add(raw(pos)[f.COL['age']],1,(f.U-1).bit_length()),('Age',phase,pos)
        wanted=list(baseline)
        for delta in f.OFFSETS:
            for name,value in local(pos+delta,baseline[f.COL['f1']]).items():
                wanted[f.COL[f's{delta+2}_{name}']]=value
        for (name,_),a,b in zip(f.SCHEMA,actual,wanted):
            if a!=b:raise AssertionError((phase,pos,name,terms.nodes[a],terms.nodes[b]))
    return dict(phase=phase,passed=True,holders=list(holders),complete_raw_output_words=len(holders)*f.FIELDS,
                symbolic_terms=len(terms.nodes),all_clock_ages=f.U,
                arbitrary_physical_flags_Signals_Wf=True,canonical_geometry_preserved=True)

