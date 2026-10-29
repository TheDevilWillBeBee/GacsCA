#!/usr/bin/env python3
"""Exact right true-frame Flag1 cofactors under a first-boundary enclosure.

This does not establish physical reachability of that enclosure by itself.
"""
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,Compiled
import proposed_sparse_short_force1024 as proposed


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    start=time.monotonic();p=proposed.parameters();out=ROOT/'figs/robustness'
    table=proposed.dependency_table(p);phase_at={(row['field'],row['bit']):row['address'] for row in table}
    strips=((121*p.Q,122*p.Q-512),(136*p.Q-512,136*p.Q))
    def blocked(j,d,phase):
        lo,hi=sorted((j*p.Q+phase,(j+d)*p.Q+phase))
        return any(lo+8*max(0,(left-lo+7)//8)<=min(hi,right-1) for left,right in strips)
    records=[]
    for j in range(136,184):
        class Captured(Net):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,field,bit=key;col=j+d
                    if field in ('addr','age','f1','wf1'):
                        phase=phase_at[field,bit]
                        if blocked(j,d,phase):return 0
                        assert col>=136,(j,key,col)
                        if field=='addr':return 0 if col<=143 else ((col%p.Q)>>bit)&1
                        if field=='f1':return int(col in (144,145,146))
                        if field=='age':
                            return super().input(('upper_Age',col,bit)) if col<=143 else ((p.age_code(1)>>bit)&1)
                        if field=='wf1':
                            return super().input(('upper_WF1',col,bit)) if col<=143 else 0
                return super().input(key)
        net,_=proposed.full_net(p,Captured);node=net.outputs['y','f1',0]
        records.append(dict(true_colony=j,Flag1_constant=node if node in (0,1) else None,
                            nonconstant_node=None if node in (0,1) else node,netlist_sha256=Compiled(net).digest))
    receipt=dict(scope='Conditional exact algebraic second-right-signal probe, boundary source premises separate',
        records=records,source_GF_zero_at136_through143_and_canonical_from144_assumed=True,
        upper_Flag1_one_at144_145_146_and_zero_elsewhere_assumed=True,
        arbitrary_Age_WF1_at136_through143_allowed=True,
        other_source_Age1_and_WF1_zero_assumed=True,other_fields_and_I_free=True,
        physical_boundary_data_proved_in_this_probe=False,global_reliability_established=False,
        active_G17_modified=False,rule_or_constant_changed=False,checker_sha256=digest(__file__),
        proposal_sha256=digest(proposed.__file__),seconds=time.monotonic()-start)
    (out/'SP29_second_right_signal_probe.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(constant_ones=[r['true_colony'] for r in records if r['Flag1_constant']==1],
        nonconstant=[r['true_colony'] for r in records if r['Flag1_constant'] is None],seconds=receipt['seconds'])),flush=True)


if __name__=='__main__':main()
