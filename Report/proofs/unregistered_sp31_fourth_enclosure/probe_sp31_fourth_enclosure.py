#!/usr/bin/env python3
"""Fourth native-source cofactors of J241 banks; no actual pulse claim.

The written lift is separate. Free words remain shared symbolic inputs;
selected cofactor values alone do not characterize reachable commands.
"""
from collections import Counter
from itertools import product
from pathlib import Path
import hashlib,json,sys,time

ROOT=Path(__file__).resolve().parents[3]
S=ROOT/'Report/proofs'
sys.path[:0]=[str(ROOT),str(S),str(S/'unregistered_terminal')]
from gacsca.netlist import Compiled,const_word
from probe_sp30_symbolic_left_absorption import AbsorptionNet
from check_native_command1024_first_pulse import blocked
import proposed_native_command1024 as proposed
import proposed_distant_native448 as distant

NATIVE=('addr','age','f1','f2','wf1','wf2')
OUT=ROOT/'figs/robustness/unregistered_sp31_fourth_enclosure'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def fourth_left_value(n,p,s,f,b=0,a=0,q134=0,q141=0):
    if s>=148:return 0
    if f=='addr':
        value=s%p.Q if s<=132 else 133*a if s==133 else q134 if s==134 else q141 if s==141 else 0
        return (value>>b)&1
    if s<=132:
        if f=='age':value=p.age_code(3)
        elif f=='f1':value=int(112<=s<=132)
        elif f=='f2' and s in (131,132):return n.input(('fourth_true',s,f,b))
        else:value=0
        return (value>>b)&1
    if s==141:return n.input(('fourth_partial',s,f,b))
    if f=='f1':return int(s<=140)
    if f=='f2' and s>=142:return 0
    if f=='wf2' and s<=140:return 0
    if f=='wf1' and s<=140 and s!=134:return 0
    return n.input(('fourth_true' if s<=140 else 'fourth_recovered',s,f,b))

def fourth_foreign_value(n,p,s,f,b=0,q149=0):
    if s<=148 or s>=152:return 0
    if f=='addr':return (q149>>b)&1 if s==149 else 0
    if f=='f2':return n.input(('fourth_foreign149_F2',)) if s==149 else 0
    return n.input(('fourth_foreign',s,f,b))

def primitive(a,q,t,center,Q):
    """Exhaust a block's sole relevant free GF word, never a pair sample."""
    sources=[t+center+v for v in range(-2,3)]
    assert not (134 in sources and 141 in sources)
    vals=[];known=[]
    for v,s in zip(range(-2,3),sources):
        raw=s%Q if s<=132 else 133*a if s==133 else q if s in (134,141) else 0
        vals.append((raw-center-v)%Q)
        known.append(s<=132)
    votes=Counter(vals)
    for word,count in votes.items():
        if count>=3:
            assert word==t%Q and any(known[i] and vals[i]==word for i in range(5)),(a,q,t,center,word,count)
    if t>=133 and center>0:assert max(votes.values())<=2,(a,q,t,center)

def main():
    start=time.monotonic();p=proposed.parameters();c=proposed.load_artifact();build,source=proposed.proposed_build()
    OUT.mkdir(exist_ok=True)
    bankpath=ROOT/'figs/robustness/SP31_third_boundary_banks_certificate.json'
    banks=json.loads(bankpath.read_text())
    assert banks['candidate_sha256']==c.digest() and banks['actual_protected_third_true_native_banks_proved']
    assert banks['actual_one_exception_third_foreign_GF_F2_banks_proved']
    strips=((148*p.Q,149*p.Q-512),(152*p.Q-512,152*p.Q))
    phases={(r['field'],r['bit']):r['address'] for r in proposed.dependency_table(p)}
    selected=[]
    for a,j,q134,q141 in product(range(2),range(96,148),(0,134,1023),(0,141,1023)):
        n=AbsorptionNet()
        cells={d:{f:[fourth_left_value(n,p,j+d,f,b,a,q134,q141) for b in range(p.k if f=='addr' else p.m)] if f in ('addr','age') else fourth_left_value(n,p,j+d,f,0,a,q134,q141) for f in NATIVE} for d in range(-5,9)}
        got=build(n,cells,p.k,p.m,Q=p.Q,nb=p.nb,radix=p.R,pos_bits=p.PB,service_force=0)
        assert got['f1']==int(j>=106),(a,j,q134,q141,'F1',got['f1'])
        if j<=131:assert got['f2']==0,(a,j,q134,q141,'F2',got['f2'])
        selected.append(dict(a=a,j=j,q134=q134,q141=q141,F1=got['f1'],F2=got['f2'] if got['f2'] in (0,1) else None))
    print(json.dumps(dict(selected_native_cofactors=len(selected))),flush=True)
    cohorts=0
    for a,t,center in product(range(2),range(96,182),distant.CENTERS):
        sources=range(t+center-2,t+center+3)
        for q in range(p.Q) if 134 in sources or 141 in sources else (0,):
            primitive(a,q,t,center,p.Q);cohorts+=1
    full=[]
    for a,j,q134,q141 in product(range(2),range(126,148),(0,1023),(0,1023)):
        class Left(AbsorptionNet):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,f,b=key
                    if f in NATIVE:return 0 if blocked(strips,j,d,phases[f,b],p.Q) else fourth_left_value(self,p,j+d,f,b,a,q134,q141)
                return super().input(key)
        n,_=proposed.full_net(p,Left)
        assert n.outputs['y','f1',0]==1,(a,j,q134,q141,'fullF1')
        if j<=131:assert n.outputs['y','f2',0]==0,(a,j,q134,q141,'fullF2')
        full.append(dict(a=a,j=j,q134=q134,q141=q141,netlist_sha256=Compiled(n).digest))
    foreign=[]
    for h,q in product(range(149,152),range(p.Q)):
        n=AbsorptionNet()
        cells={d:{f:[fourth_foreign_value(n,p,h+d,f,b,q) for b in range(p.k if f=='addr' else p.m)] if f in ('addr','age') else fourth_foreign_value(n,p,h+d,f,0,q) for f in NATIVE} for d in range(-5,9)}
        got=build(n,cells,p.k,p.m,Q=p.Q,nb=p.nb,radix=p.R,pos_bits=p.PB,service_force=0)
        assert got['f1']==1,(h,q,'foreignF1')
        foreign.append(dict(h=h,q=q,F1=1,F2=got['f2'] if got['f2'] in (0,1) else None))
    result=dict(scope='Selected literal native/full-rule cofactors of actual J241 table; universal GF cohorts and foreign F1 single-GF cofactors; written full physical fourth lift not supplied by this probe',
        Q=p.Q,U=p.U,candidate_sha256=c.digest(),netlist_sha256=c.comp.digest,
        probe_sha256=sha(__file__),bank_certificate_sha256=sha(bankpath),
        maintenance_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        selected_native_cofactors=selected,GF_cohort_cases=cohorts,selected_full_left_cofactors=full,
        fourth_foreign_all_q_cofactors=foreign,actual_fourth_source_enclosure_proved=False,
        fourth_pulse_or_command_reachability_proved=False,global_reliability_established=False,
        additional_rule_change=False,active_G17_modified=False,seconds=time.monotonic()-start)
    (OUT/'cofactor_receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,selected_native_cofactors=len(selected),GF_cohort_cases=cohorts,selected_full_left_cofactors=len(full),foreign_all_q_cofactors=len(foreign),seconds=result['seconds'])),flush=True)
if __name__=='__main__':main()
