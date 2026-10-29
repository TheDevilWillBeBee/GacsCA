#!/usr/bin/env python3
"""Exploratory actual-bank cofactor analysis; unresolved nodes are not faults."""
from collections import Counter
from itertools import product
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'Report/proofs'),str(ROOT/'Report/proofs/unregistered_terminal')]
from gacsca.netlist import Compiled,const_word
from probe_sp30_symbolic_left_absorption import AbsorptionNet
import proposed_native_command1024 as proposed
import proposed_distant_native448 as distant
from check_native_command1024_second_source_enclosure import left_value
from check_native_command1024_first_pulse import blocked
OUT=ROOT/'figs/robustness/unregistered_sp31_third_sources'
NATIVE=('addr','age','f1','f2','wf1','wf2')

def third_left_value(n,p,s,f,b,a=0,q=0):
    if s>=141:return 0
    if s<=133:
        if f=='addr':value=s%p.Q if s<=129 else 130*a if s==130 else 0
        elif f=='age':
            if s in (124,130,131,132,133):return n.input(('second_true_free',s,f,b))
            value=p.age_code(2)
        elif f=='f1':value=int(118<=s<=133)
        elif f=='f2':
            if s in (124,130,131,132,133):return n.input(('second_true_free',s,f,b))
            value=0
        else:value=0
        return (value>>b)&1
    if f=='addr':return (q>>b)&1 if s==134 else 0
    if s==134:return n.input(('second_partial',s,f,b))
    if f in ('f1','f2'):return 0
    return n.input(('second_recovered',s,f,b))

def primitive(a,q,t,center,Q):
    vals=[];known=[]
    for v in range(-2,3):
        s=t+center+v
        raw=s%Q if s<=129 else 130*a if s==130 else q if s==134 else 0
        vals.append((raw-center-v)%Q)
        known.append(s<=129 and s!=124)
    votes=Counter(vals)
    for word,count in votes.items():
        if count>=3:
            assert word==t%Q and any(known[i] and vals[i]==word for i in range(5)),(a,q,t,center,word,count)
    if t==124 and center>0 or t>=130 and center>0:
        assert max(votes.values())<=2,(a,q,t,center)

def main():
    start=time.monotonic();p=proposed.parameters();c=proposed.load_artifact();build,_=proposed.proposed_build()
    OUT.mkdir(exist_ok=True);phases={(r['field'],r['bit']):r['address'] for r in proposed.dependency_table(p)}
    first=[]
    for j,q in product((124,125,126,127,128,129,130,131,132,133),(0,127,1023)):
        n=AbsorptionNet();cells={}
        for d in range(-5,9):
            s=j+d;cells[d]={f:[left_value(n,p,s,f,b,q) for b in range(p.k if f=='addr' else p.m)] if f in ('addr','age') else left_value(n,p,s,f,0,q) for f in NATIVE}
        got=build(n,cells,p.k,p.m,Q=p.Q,nb=p.nb,radix=p.R,pos_bits=p.PB,service_force=0)
        row={'j':j,'q':q}
        for f in ('addr','age_now','f1','f2'):
            vals=got[f] if isinstance(got[f],list) else [got[f]]
            row[f]=sum(v<<b for b,v in enumerate(vals)) if all(v in (0,1) for v in vals) else None
        first.append(row)
    print(json.dumps({'second_true_native_selected':first}),flush=True)
    checks=0
    for a,q,t,center in product(range(2),range(p.Q),range(120,147),distant.CENTERS):
        primitive(a,q,t,center,p.Q);checks+=1
    native=[]
    for a,j,q in product(range(2),range(105,141),(0,1,127,134,1023)):
        n=AbsorptionNet();cells={}
        for d in range(-5,9):
            s=j+d;cells[d]={f:[third_left_value(n,p,s,f,b,a,q) for b in range(p.k if f=='addr' else p.m)] if f in ('addr','age') else third_left_value(n,p,s,f,0,a,q) for f in NATIVE}
        got=build(n,cells,p.k,p.m,Q=p.Q,nb=p.nb,radix=p.R,pos_bits=p.PB,service_force=0)
        assert got['f1']==int(112<=j<=140),(a,j,q,got['f1'])
        if j<=130:assert got['f2']==0,(a,j,q,'F2',got['f2'])
        native.append(dict(a=a,j=j,q=q,F1=got['f1'],F2=got['f2'] if got['f2'] in (0,1) else None))
    full=[]
    strips=((141*p.Q,142*p.Q-512),(149*p.Q-512,149*p.Q))
    for a,j,q in product(range(2),range(105,141),(0,1023)):
        class Third(AbsorptionNet):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,f,b=key
                    if f in NATIVE:
                        return 0 if blocked(strips,j,d,phases[f,b],p.Q) else third_left_value(self,p,j+d,f,b,a,q)
                return super().input(key)
        n,_=proposed.full_net(p,Third)
        f1=n.outputs['y','f1',0];f2=n.outputs['y','f2',0]
        assert f1==int(112<=j<=140),(a,j,q,'fullF1',f1)
        if j<=130:assert f2==0,(a,j,q,'fullF2',f2)
        full.append(dict(a=a,j=j,q=q,F1=f1,F2=f2 if f2 in (0,1) else None,net_sha256=Compiled(n).digest))
    receipt=dict(scope='Exploratory cofactor/cohort checks against proposed actual third true-bank table; written physical proof not supplied by this probe',
        Q=p.Q,U=p.U,candidate_sha256=c.digest(),probe_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        second_true_native_selected=first,GF_cohort_checks=checks,selected_third_native_cofactors=native,
        selected_third_full_cofactors=full,global_reliability_established=False,additional_rule_change=False,seconds=time.monotonic()-start)
    (OUT/'exploration.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(passed=True,GF_cohort_checks=checks,native_cofactors=len(native),full_cofactors=len(full),seconds=receipt['seconds'])),flush=True)

if __name__=='__main__':main()
