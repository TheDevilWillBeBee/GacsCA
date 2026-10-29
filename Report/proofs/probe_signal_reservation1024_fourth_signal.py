#!/usr/bin/env python3
"""Conditional third-boundary native cofactors and fourth Flag1 enclosure.

This algebraic probe alone supplies no physical store bridge, fourth
pulse, general eroder, higher-error map or iid theorem. All actual-history
claims require a separate written proof and receipt.
"""
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,Compiled
import proposed_sparse_signal_reservation1024 as proposed
from check_signal_reservation1024_second_signal import blocked


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def third_source_net(j,p):
    phases={(r['field'],r['bit']):r['address'] for r in proposed.dependency_table(p)}
    strips=((115*p.Q,116*p.Q-512),(128*p.Q-512,128*p.Q));left=j<=108
    class Captured(Net):
        def input(self,key):
            if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                _,d,field,bit=key;col=j+d
                if field in ('addr','age','f1','wf1'):
                    if blocked(strips,j,d,phases[field,bit],p.Q):return 0
                    if left:
                        assert col<=114
                        if field=='addr':return ((col%p.Q)>>bit)&1
                        if field=='f1':return 0
                        if col==114:return super().input(('upper_'+field,col,bit))
                        return (p.age_code(2)>>bit)&1 if field=='age' else 0
                    assert col>=128
                    if field=='addr':
                        if col<=140:return 0
                        if col<=143:return super().input(('upper_GF',col,bit))
                        return ((col%p.Q)>>bit)&1
                    if field=='f1':return int(136<=col<=146)
                    if field=='age':return super().input(('upper_Age',col,bit)) if col<=146 else (p.age_code(2)>>bit)&1
                    if field=='wf1':return super().input(('upper_WF1',col,bit)) if col<=135 else 0
            return super().input(key)
    return proposed.full_net(p,Captured)[0]


def source_enclosure(p,c):
    records=[]
    for j in (*range(77,109),*range(128,188)):
        n=third_source_net(j,p);bits={};words={}
        for field in ('addr','age','f1','wf1'):
            nodes=[n.outputs['y',field,b] for b in range(dict(c.schema)[field])]
            bits[field]=[v if v in (0,1) else None for v in nodes]
            words[field]=sum(v<<b for b,v in enumerate(nodes)) if all(v in (0,1) for v in nodes) else None
        gf=[n.outputs['y','addr',b] for b in range(dict(c.schema)['addr'])]
        variables={v for v in gf if v not in (0,1)}
        zero_or_canonical=len(variables)==1 and all(v==0 if not (j>>b)&1 else v in variables for b,v in enumerate(gf))
        if j<=108:assert words==dict(addr=j,age=p.age_code(3),f1=0,wf1=0)
        records.append(dict(colony=j,constant_output_words=words,constant_output_bits=bits,
            GF_zero_or_canonical_shared_node_identity=zero_or_canonical,netlist_sha256=Compiled(n).digest))
    return records


def fourth_cofactors(p,c,source_records):
    source={r['colony']:r for r in source_records};table=proposed.dependency_table(p)
    phases={(r['field'],r['bit']):r['address'] for r in table}
    strips=((109*p.Q,110*p.Q-512),(120*p.Q-512,120*p.Q));records=[];routes=0
    for j in (*range(71,109),*range(120,188)):
        left=j<=108
        for row in table:
            if row['field'] not in ('addr','age','f1','wf1'):continue
            for d in (0,*row['offsets']):
                crossing=blocked(strips,j,d,row['address'],p.Q)
                assert crossing==blocked(strips,j,d,59,p.Q)
                assert crossing or (j+d<=108 if left else j+d>=120)
                routes+=1
        class Captured(Net):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,field,bit=key;col=j+d
                    if field in ('addr','age','f1','wf1'):
                        if blocked(strips,j,d,phases[field,bit],p.Q):return 0
                        if left:
                            if field=='addr':return ((col%p.Q)>>bit)&1
                            if field=='f1':return 0
                            if col==108:return super().input(('third_'+field,col,bit))
                            return (p.age_code(3)>>bit)&1 if field=='age' else 0
                        if col<=127:
                            return 0 if field in ('addr','f1') else super().input(('third_'+field,col,bit))
                        if col>=188:
                            return ((col%p.Q)>>bit)&1 if field=='addr' else (p.age_code(3)>>bit)&1 if field=='age' else 0
                        value=source[col]['constant_output_bits'][field][bit]
                        if value is not None:return value
                        if field=='addr' and source[col]['GF_zero_or_canonical_shared_node_identity']:
                            assert (col>>bit)&1
                            return super().input(('third_GF_zero_or_canonical_choice',col))
                        return super().input(('third_'+field,col,bit))
                return super().input(key)
        n,_=proposed.full_net(p,Captured);node=n.outputs['y','f1',0]
        records.append(dict(colony=j,side='left' if left else 'right',
            Flag1_constant=node if node in (0,1) else None,netlist_sha256=Compiled(n).digest))
    assert routes==201930 and len(records)==106
    assert 70+37<108 and 188-37>149
    return records,routes


def calculate():
    p=proposed.parameters();c=proposed.load_artifact();source=source_enclosure(p,c)
    fourth,routes=fourth_cofactors(p,c,source)
    ones=[r['colony'] for r in fourth if r['Flag1_constant']==1]
    optional=[r['colony'] for r in fourth if r['Flag1_constant'] is None]
    return dict(third_boundary_native_source_cofactors=source,fourth_true_Flag1_cofactors=fourth,
        fourth_native_capture_routes=routes,fourth_MF509_fixed_one_colonies=list(range(110,120)),
        fourth_MF1021_fixed_one_colonies=ones,fourth_MF1021_unspecified_colonies=optional,
        optional_bit_count=len(optional),concrete_enclosure_masks=1<<len(optional),
        third_GF_zero_or_canonical_conditional_cells=[r['colony'] for r in source if r['GF_zero_or_canonical_shared_node_identity']])


def main():
    start=time.monotonic();p=proposed.parameters();c=proposed.load_artifact();out=ROOT/'figs/robustness'
    third=json.loads((out/'SP30_third_signal_certificate.json').read_text())
    assert third['proposed_candidate_sha256']==c.digest() and third['actual_third_shrinking_projected_pulse_on_Z_proved']
    result=calculate()
    r=dict(proposal='SP30',scope='Conditional third-boundary output/fourth Flag1 cofactor enclosure only; actual physical store bridge and pulse need separate proof',
        Q=p.Q,U=p.U,T_wf=p.T_wf,checker_sha256=digest(__file__),proposal_source_sha256=digest(proposed.__file__),
        proposed_candidate_sha256=c.digest(),proposed_netlist_sha256=c.comp.digest,
        third_signal_receipt_sha256=digest(out/'SP30_third_signal_certificate.json'),
        source_helper_sha256=digest(ROOT/'Report/proofs/check_signal_reservation1024_second_signal.py'),results=result,
        retained_initial_probe_failure_assets_sha256={name:digest(out/name) for name in (
            'SP30_fourth_signal_initial_probe.py.txt','SP30_fourth_signal_initial_probe_failure.log')},
        initial_probe_failure='missing logQ attribute; corrected to the actual addr schema width, before any cofactor conclusion',
        all_H2_Info_and_unmentioned_source_fields_and_I_free=True,
        physical_third_boundary_or_complete_fourth_signal_or_pulse_proved=False,
        global_eroder_or_iid_threshold_proved=False,active_G17_modified=False,additional_rule_change=False,
        numerical_whole_CA_trajectory_used=False,global_reliability_established=False,seconds=time.monotonic()-start)
    (out/'SP30_fourth_signal_probe.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(dict(fourth_MF1021_fixed_one_colonies=result['fourth_MF1021_fixed_one_colonies'],
        fourth_MF1021_unspecified_colonies=result['fourth_MF1021_unspecified_colonies'],
        third_GF_zero_or_canonical_conditional_cells=result['third_GF_zero_or_canonical_conditional_cells'],
        seconds=r['seconds'],physical_actual_fourth_signal_proved=False)),flush=True)


if __name__=='__main__':main()
