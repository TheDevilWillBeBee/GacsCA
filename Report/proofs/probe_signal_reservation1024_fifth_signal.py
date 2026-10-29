#!/usr/bin/env python3
"""Conditional fourth-boundary native bit boxes and fifth Flag1 enclosure.

This calculation does not establish the physical store/commit bridge or
a fifth pulse. It preserves every earlier accepted source and receipt.
"""
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,Compiled
import proposed_sparse_signal_reservation1024 as proposed
from check_signal_reservation1024_second_signal import blocked


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fourth_source_net(j,p,previous_sources):
    phases={(r['field'],r['bit']):r['address'] for r in proposed.dependency_table(p)}
    strips=((109*p.Q,110*p.Q-512),(120*p.Q-512,120*p.Q));left=j<=102
    class Captured(Net):
        def input(self,key):
            if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                _,d,field,bit=key;col=j+d
                if field in ('addr','age','f1','wf1'):
                    if blocked(strips,j,d,phases[field,bit],p.Q):return 0
                    if left:
                        assert col<=108
                        if field=='addr':return ((col%p.Q)>>bit)&1
                        if field=='f1':return 0
                        if col==108:return super().input(('third_'+field,col,bit))
                        return (p.age_code(3)>>bit)&1 if field=='age' else 0
                    assert col>=120
                    if col<=127:
                        return 0 if field in ('addr','f1') else super().input(('third_'+field,col,bit))
                    if col>=188:
                        return ((col%p.Q)>>bit)&1 if field=='addr' else (p.age_code(3)>>bit)&1 if field=='age' else 0
                    value=previous_sources[col]['constant_output_bits'][field][bit]
                    if value is not None:return value
                    return super().input(('third_'+field,col,bit))
            return super().input(key)
    return proposed.full_net(p,Captured)[0]


def source_enclosure(p,c,previous_sources):
    records=[]
    for j in (*range(71,103),*range(120,192)):
        n=fourth_source_net(j,p,previous_sources);bits={};words={}
        for field in ('addr','age','f1','wf1'):
            nodes=[n.outputs['y',field,b] for b in range(dict(c.schema)[field])]
            bits[field]=[v if v in (0,1) else None for v in nodes]
            words[field]=sum(v<<b for b,v in enumerate(nodes)) if all(v in (0,1) for v in nodes) else None
        if j<=102:assert words==dict(addr=j,age=p.age_code(4),f1=0,wf1=0)
        records.append(dict(colony=j,constant_output_words=words,constant_output_bits=bits,
            netlist_sha256=Compiled(n).digest))
    return records


def fifth_cofactors(p,c,source_records):
    source={r['colony']:r for r in source_records};table=proposed.dependency_table(p)
    phases={(r['field'],r['bit']):r['address'] for r in table}
    strips=((103*p.Q,104*p.Q-512),(112*p.Q-512,112*p.Q));records=[];routes=0
    for j in (*range(65,103),*range(112,192)):
        left=j<=102
        for row in table:
            if row['field'] not in ('addr','age','f1','wf1'):continue
            for d in (0,*row['offsets']):
                crossing=blocked(strips,j,d,row['address'],p.Q)
                assert crossing==blocked(strips,j,d,59,p.Q)
                assert crossing or (j+d<=102 if left else j+d>=112)
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
                            if col==102:return super().input(('fourth_'+field,col,bit))
                            return (p.age_code(4)>>bit)&1 if field=='age' else 0
                        if col<=119:
                            return 0 if field in ('addr','f1') else super().input(('fourth_'+field,col,bit))
                        if col>=192:
                            return ((col%p.Q)>>bit)&1 if field=='addr' else (p.age_code(4)>>bit)&1 if field=='age' else 0
                        value=source[col]['constant_output_bits'][field][bit]
                        if value is not None:return value
                        return super().input(('fourth_'+field,col,bit))
                return super().input(key)
        n,_=proposed.full_net(p,Captured);node=n.outputs['y','f1',0]
        records.append(dict(colony=j,side='left' if left else 'right',
            Flag1_constant=node if node in (0,1) else None,netlist_sha256=Compiled(n).digest))
    assert 64+37<102 and 192-37>152
    return records,routes


def calculate():
    p=proposed.parameters();c=proposed.load_artifact()
    previous=json.loads((ROOT/'figs/robustness/SP30_fourth_signal_certificate.json').read_text())
    previous_sources={r['colony']:r for r in previous['third_native_source_cofactor_records']}
    sources=source_enclosure(p,c,previous_sources);fifth,routes=fifth_cofactors(p,c,sources)
    ones=[r['colony'] for r in fifth if r['Flag1_constant']==1]
    optional=[r['colony'] for r in fifth if r['Flag1_constant'] is None]
    fixed=lambda rows:sum(v is not None for r in rows for bits in r['constant_output_bits'].values() for v in bits)
    return dict(fourth_boundary_native_source_cofactors=sources,
        native_constant_bit_equalities=fixed(sources),
        native_left_constant_bit_equalities=fixed([r for r in sources if r['colony']<=102]),
        native_right_constant_bit_equalities=fixed([r for r in sources if r['colony']>=120]),
        fifth_true_Flag1_cofactors=fifth,fifth_native_capture_routes=routes,
        fifth_MF509_fixed_one_colonies=list(range(104,112)),
        fifth_MF1021_fixed_one_colonies=ones,fifth_MF1021_unspecified_colonies=optional,
        optional_bit_count=len(optional),concrete_enclosure_masks=1<<len(optional))


def main():
    start=time.monotonic();p=proposed.parameters();c=proposed.load_artifact();out=ROOT/'figs/robustness'
    fourth=json.loads((out/'SP30_fourth_signal_certificate.json').read_text())
    assert fourth['proposed_candidate_sha256']==c.digest() and fourth['actual_fourth_shrinking_projected_pulse_on_Z_proved']
    result=calculate()
    receipt=dict(proposal='SP30',scope='Conditional fourth-boundary fixed-bit boxes and fifth Flag1 cofactor enclosure; physical bridge and pulse unproved',
        Q=p.Q,U=p.U,T_wf=p.T_wf,checker_sha256=digest(__file__),
        proposal_source_sha256=digest(proposed.__file__),proposed_candidate_sha256=c.digest(),proposed_netlist_sha256=c.comp.digest,
        fourth_signal_receipt_sha256=digest(out/'SP30_fourth_signal_certificate.json'),
        source_helper_sha256=digest(ROOT/'Report/proofs/check_signal_reservation1024_second_signal.py'),results=result,
        all_H2_Info_and_unmentioned_source_fields_and_I_free=True,
        physical_fourth_boundary_or_complete_fifth_signal_or_pulse_proved=False,
        general_eroder_or_higher_map_or_iid_threshold_proved=False,
        numerical_whole_CA_trajectory_used=False,additional_rule_programme_or_constant_change=False,
        active_G17_modified=False,global_reliability_established=False,seconds=time.monotonic()-start)
    (out/'SP30_fifth_signal_probe.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(fifth_MF1021_fixed_one_colonies=result['fifth_MF1021_fixed_one_colonies'],
        fifth_MF1021_unspecified_colonies=result['fifth_MF1021_unspecified_colonies'],
        constant_bit_equalities=result['native_constant_bit_equalities'],
        seconds=receipt['seconds'],actual_fifth_signal_proved=False)),flush=True)


if __name__=='__main__':main()
