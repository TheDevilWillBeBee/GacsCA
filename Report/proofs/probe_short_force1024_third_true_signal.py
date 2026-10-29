#!/usr/bin/env python3
"""Conditional third true-frame Flag1 cofactors, source bridge separate.

The right enclosure leaves GF141..143, Age128..146 and WF1128..135 free.
Every optional result is an enclosure bit, with no independence claim.
"""
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,Compiled
import proposed_sparse_short_force1024 as proposed
from check_short_force1024_protected_scratch import blocked


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    begin=time.monotonic();p=proposed.parameters();out=ROOT/'figs/robustness'
    table=proposed.dependency_table(p);phases={(r['field'],r['bit']):r['address'] for r in table}
    strips=((115*p.Q,115*p.Q+512),(127*p.Q+512,128*p.Q));records=[]
    for side,indices in (('left',range(77,115)),('right',range(128,184))):
        for j in indices:
            class Captured(Net):
                def input(self,key):
                    if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                        _,d,field,bit=key;col=j+d
                        if field in ('addr','age','f1','wf1'):
                            if blocked(strips,j,d,phases[field,bit],p.Q):return 0
                            if side=='left':
                                assert col<=114,(side,j,key,col)
                                if field=='addr':return ((col%p.Q)>>bit)&1
                                if field=='f1':return 0
                                if col==114:return super().input(('upper_'+field,col,bit))
                                return ((p.age_code(2)>>bit)&1) if field=='age' else 0
                            assert col>=128,(side,j,key,col)
                            if field=='addr':
                                if col<=140:return 0
                                if col<=143:return super().input(('upper_GF',col,bit))
                                return ((col%p.Q)>>bit)&1
                            if field=='f1':return int(136<=col<=146)
                            if field=='age':return super().input(('upper_Age',col,bit)) if col<=146 else ((p.age_code(2)>>bit)&1)
                            if field=='wf1':return super().input(('upper_WF1',col,bit)) if col<=135 else 0
                    return super().input(key)
            net,_=proposed.full_net(p,Captured);node=net.outputs['y','f1',0]
            records.append(dict(side=side,colony=j,Flag1_constant=node if node in (0,1) else None,nonconstant_node=node if node not in (0,1) else None,netlist_sha256=Compiled(net).digest))
    receipt=dict(proposal='SP29',scope='Conditional third true-frame native Flag1 cofactors; actual second boundary and complete third mask separate',
        records=records,left_GF_canonical_Age2_before114_and_Age_WF1_free_at114_assumed=True,
        left_Flag1_zero_assumed=True,right_GF_zero128_through140_free141_through143_canonical_from144_assumed=True,
        right_Flag1_one136_through146_and_zero_elsewhere_assumed=True,
        right_Age_free128_through146_and_Age2_from147_assumed=True,
        right_WF1_free128_through135_and_zero_elsewhere_assumed=True,
        other_fields_and_I_free=True,source_enclosure_physical_bridge_proved_by_this_probe=False,
        complete_third_signal_or_pulse_proved=False,optional_Flag1_bits_independence_proved=False,
        global_reliability_established=False,active_G17_modified=False,rule_programme_or_constant_change=False,
        checker_sha256=digest(__file__),proposal_source_sha256=digest(proposed.__file__),
        helper_sha256=digest(ROOT/'Report/proofs/check_short_force1024_protected_scratch.py'),
        receipt_dependencies_sha256={name:digest(out/name) for name in ('SP29_protected_scratch_certificate.json','SP29_right_boundary_native_word_probe.json')},
        seconds=time.monotonic()-begin)
    (out/'SP29_third_true_signal_probe.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(ones={side:[r['colony'] for r in records if r['side']==side and r['Flag1_constant']==1] for side in ('left','right')},
        optional={side:[r['colony'] for r in records if r['side']==side and r['Flag1_constant'] is None] for side in ('left','right')},seconds=receipt['seconds'])),flush=True)


if __name__=='__main__':main()
