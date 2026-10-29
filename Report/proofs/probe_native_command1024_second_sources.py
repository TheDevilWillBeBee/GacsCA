#!/usr/bin/env python3
"""Retained exploratory F31 source cofactors; no actual pulse assertion."""
from pathlib import Path
from itertools import product
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'Report/proofs/unregistered_terminal'))
from gacsca.netlist import Net,const_word
from probe_sp30_symbolic_left_absorption import AbsorptionNet
import proposed_native_command1024 as proposed
from check_native_command1024_first_pulse import blocked

def main():
    start=time.monotonic();p=proposed.parameters();c=proposed.load_artifact()
    phases={(r['field'],r['bit']):r['address'] for r in proposed.dependency_table(p)}
    old=((127*p.Q,128*p.Q-512),(143*p.Q-512,143*p.Q))
    records=[]
    for j in (*range(90,127),*range(146,182)):
        class First(AbsorptionNet):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,f,b=key
                    if f=='addr':return ((0 if blocked(old,j,d,phases[f,b],p.Q) else (j+d)%p.Q)>>b)&1
                    if f in ('age','f1','f2','wf1','wf2'):return 0
                return super().input(key)
        n,_=proposed.full_net(p,First)
        expected=dict(addr=j%p.Q,age=p.age_code(1),f1=int(j in (124,125,126)),f2=0,wf1=0,wf2=0)
        for f,val in expected.items():
            assert [n.outputs['y',f,b] for b in range(dict(c.schema)[f])]==const_word(val,dict(c.schema)[f]),(j,f)
        records.append(dict(j=j,**expected))
    print(json.dumps(dict(first_boundary_complete_words=len(records))),flush=True)
    strips=((134*p.Q,135*p.Q-512),(146*p.Q-512,146*p.Q));second=[]
    for j in (*range(90,134),*range(146,182)):
        class Second(AbsorptionNet):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,f,b=key;col=j+d
                    if f in ('addr','age','f1','f2','wf1','wf2'):
                        if blocked(strips,j,d,phases[f,b],p.Q):return 0
                        if j>=146:
                            assert col>=146
                            val=col%p.Q if f=='addr' else p.age_code(1) if f=='age' else 0
                            return (val>>b)&1
                        assert col<=133
                        if col<=126:
                            val=col%p.Q if f=='addr' else p.age_code(1) if f=='age' else int(col in (124,125,126)) if f=='f1' else 0
                            return (val>>b)&1
                        if f=='addr':return super().input(('partialGF',b)) if col==127 else 0
                        if f in ('f1','f2'):return super().input(('partial'+f,b)) if col==127 else 0
                        return super().input(('upper',col,f,b))
                return super().input(key)
        n,_=proposed.full_net(p,Second)
        values={f:(n.outputs['y',f,0] if n.outputs['y',f,0] in (0,1) else None) for f in ('f1','f2')}
        second.append(dict(j=j,**values))
        if j>=118 and j<=134 or j<=150 and j>=146:print(json.dumps(second[-1]),flush=True)
    out=ROOT/'figs/robustness/SP31_second_sources_exploration.json'
    out.write_text(json.dumps(dict(first=records,second=second,seconds=time.monotonic()-start),indent=2)+'\n')
    print(json.dumps(dict(seconds=time.monotonic()-start)),flush=True)

if __name__=='__main__':main()
