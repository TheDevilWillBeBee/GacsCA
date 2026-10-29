#!/usr/bin/env python3
"""Exact conditional second-period left true-frame Flag1 cofactors.

The source-data premises require a separate physical first-boundary proof.
This probe permits arbitrary Age/WF1 at upper cell120 and other data/I free.
"""
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,Compiled
import proposed_sparse_short_force1024 as proposed


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    start=time.monotonic();p=proposed.parameters();out=ROOT/'figs/robustness'
    a,b=124416,139264;strips=((a-512,a),(b-512,b))
    def blocked(j,d,phase):
        lo,hi=sorted((j*p.Q+phase,(j+d)*p.Q+phase))
        return any(lo+8*max(0,(left-lo+7)//8)<=min(hi,right-1) for left,right in strips)
    records=[]
    for j in range(83,121):
        class Captured(Net):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,field,bit=key;col=j+d
                    if field in ('addr','age','f1','wf1'):
                        phase=next(row['address'] for row in proposed.dependency_table(p)
                                   if (row['field'],row['bit'])==(field,bit))
                        erased=blocked(j,d,phase)
                        if erased:return 0
                        assert col<=120,(j,key,col)
                        if field=='addr':return ((col%p.Q)>>bit)&1
                        if field=='f1':return 0
                        if field=='age':
                            return super().input(('upper120_Age',bit)) if col==120 else ((p.age_code(1)>>bit)&1)
                        if field=='wf1':
                            return super().input(('upper120_WF1',bit)) if col==120 else 0
                return super().input(key)
        net,_=proposed.full_net(p,Captured)
        node=net.outputs['y','f1',0]
        records.append(dict(true_colony=j,Flag1_constant=node if node in (0,1) else None,
                            nonconstant_node=None if node in (0,1) else node,
                            netlist_sha256=Compiled(net).digest))
    result=dict(scope='Conditional algebraic second-left-signal probe; physical boundary premises separately required',
        Q=p.Q,U=p.U,records=records,
        arbitrary_upper120_Age_and_WF1_allowed=True,all_other_circuit_fields_and_I_free=True,
        source_GF_canonical_through120_and_zero_if_path_crosses_first_boundary_strip_assumed=True,
        source_Age1_and_Flag1_WF1_zero_before120_assumed=True,
        source_Flag1_at120_zero_assumed=True,
        physical_first_boundary_source_data_proved_in_this_probe=False,
        exact_second_left_signal_proved_in_this_probe=False,
        active_G17_modified=False,rule_or_constant_changed=False,global_reliability_established=False,
        checker_sha256=digest(__file__),proposal_source_sha256=digest(proposed.__file__),
        seconds=time.monotonic()-start)
    (out/'SP29_second_left_signal_probe.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(constant_ones=[r['true_colony'] for r in records if r['Flag1_constant']==1],
                         nonconstant=[r['true_colony'] for r in records if r['Flag1_constant'] is None],
                         seconds=result['seconds'])),flush=True)


if __name__=='__main__':main()
