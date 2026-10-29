#!/usr/bin/env python3
"""Prepared sixth cofactors, not an actual-history or repair certificate.

Uses only the fifth certificate's fixed native bits. Unmentioned bits,
private inputs and instructions remain arbitrary. No accepted asset changes.
"""
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'Report/proofs'))
from gacsca.netlist import Net,Compiled
import proposed_sparse_signal_reservation1024 as proposed
from check_signal_reservation1024_second_signal import blocked


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def calculate():
    p=proposed.parameters();c=proposed.load_artifact()
    old=json.loads((ROOT/'figs/robustness/SP30_fifth_signal_certificate.json').read_text())
    old_sources={r['colony']:r for r in old['fourth_native_source_cofactor_records']}
    phases={(r['field'],r['bit']):r['address'] for r in proposed.dependency_table(p)}
    native=('addr','age','f1','wf1')
    prior_strips=((103*p.Q,104*p.Q-512),(112*p.Q-512,112*p.Q))
    sources=[]
    for j in (*range(65,97),*range(112,204)):
        left=j<=96
        class Captured(Net):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,field,bit=key;col=j+d
                    if field in native:
                        if blocked(prior_strips,j,d,phases[field,bit],p.Q):return 0
                        if left:
                            assert col<=102
                            if field=='addr':return ((col%p.Q)>>bit)&1
                            if field=='f1':return 0
                            if col==102:return super().input(('fourth_'+field,col,bit))
                            return (p.age_code(4)>>bit)&1 if field=='age' else 0
                        assert col>=112
                        if col<=119:
                            return 0 if field in ('addr','f1') else super().input(('fourth_'+field,col,bit))
                        if col>=192:
                            return ((col%p.Q)>>bit)&1 if field=='addr' else (p.age_code(4)>>bit)&1 if field=='age' else 0
                        value=old_sources[col]['constant_output_bits'][field][bit]
                        if value is not None:return value
                        return super().input(('fourth_'+field,col,bit))
                return super().input(key)
        n,_=proposed.full_net(p,Captured);bits={};words={}
        for field in native:
            nodes=[n.outputs['y',field,b] for b in range(dict(c.schema)[field])]
            bits[field]=[v if v in (0,1) else None for v in nodes]
            words[field]=sum(v<<b for b,v in enumerate(nodes)) if all(v in (0,1) for v in nodes) else None
        if left:assert words==dict(addr=j,age=p.age_code(5),f1=0,wf1=0)
        sources.append(dict(colony=j,constant_output_words=words,constant_output_bits=bits,netlist_sha256=Compiled(n).digest))
    source={r['colony']:r for r in sources}
    strips=((97*p.Q,98*p.Q-512),(104*p.Q-512,104*p.Q));cofactors=[];routes=0
    for j in (*range(59,97),*range(104,216)):
        left=j<=96
        for row in proposed.dependency_table(p):
            if row['field'] not in native:continue
            for d in (0,*row['offsets']):
                crossing=blocked(strips,j,d,row['address'],p.Q)
                assert crossing==blocked(strips,j,d,59,p.Q)
                assert crossing or (j+d<=96 if left else j+d>=104)
                routes+=1
        class Captured(Net):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,field,bit=key;col=j+d
                    if field in native:
                        if blocked(strips,j,d,phases[field,bit],p.Q):return 0
                        if left:
                            if field=='addr':return ((col%p.Q)>>bit)&1
                            if field=='f1':return 0
                            if col==96:return super().input(('fifth_'+field,col,bit))
                            return (p.age_code(5)>>bit)&1 if field=='age' else 0
                        if col<=111:
                            return 0 if field in ('addr','f1') else super().input(('fifth_'+field,col,bit))
                        if col>=204:
                            return ((col%p.Q)>>bit)&1 if field=='addr' else (p.age_code(5)>>bit)&1 if field=='age' else 0
                        value=source[col]['constant_output_bits'][field][bit]
                        if value is not None:return value
                        return super().input(('fifth_'+field,col,bit))
                return super().input(key)
        n,_=proposed.full_net(p,Captured);node=n.outputs['y','f1',0]
        cofactors.append(dict(colony=j,side='left' if left else 'right',Flag1_constant=node if node in (0,1) else None,
            netlist_sha256=Compiled(n).digest))
    # Far-left and far-right canonical extensions need only these support
    # exclusions; physical protection and outputs are not proved here.
    assert 58+37<96 and 204-37>152
    exception=[r['colony'] for r in sources if r['constant_output_words']!=dict(addr=r['colony'],age=p.age_code(5),f1=0,wf1=0)]
    assert 216-37>max(exception)
    ones=[r['colony'] for r in cofactors if r['Flag1_constant']==1]
    optional=[r['colony'] for r in cofactors if r['Flag1_constant'] is None]
    fixed=lambda rs:sum(v is not None for r in rs for bits in r['constant_output_bits'].values() for v in bits)
    return dict(fifth_boundary_native_source_cofactors=sources,native_constant_bit_equalities=fixed(sources),
        native_left_constant_bit_equalities=fixed([r for r in sources if r['colony']<=96]),
        native_right_constant_bit_equalities=fixed([r for r in sources if r['colony']>=112]),
        sixth_true_Flag1_cofactors=cofactors,sixth_native_capture_routes=routes,
        sixth_MF509_fixed_one_colonies=list(range(98,104)),sixth_MF1021_fixed_one_colonies=ones,
        sixth_MF1021_unspecified_colonies=optional,optional_bit_count=len(optional),concrete_enclosure_masks=1<<len(optional),
        far_right_noncanonical_source_last_colony=max(exception))


def main():
    start=time.monotonic();p=proposed.parameters();c=proposed.load_artifact();out=ROOT/'figs/robustness/unregistered_sixth'
    out.mkdir(exist_ok=True)
    old=ROOT/'figs/robustness/SP30_fifth_signal_certificate.json'
    result=calculate()
    receipt=dict(scope='Prepared fifth-boundary native bit boxes and sixth F1 enclosure; physical history/Z pulse unproved',
        Q=p.Q,U=p.U,T_wf=p.T_wf,checker_sha256=digest(__file__),proposal_source_sha256=digest(proposed.__file__),
        proposed_candidate_sha256=c.digest(),proposed_netlist_sha256=c.comp.digest,
        prior_fifth_certificate_sha256=digest(old),results=result,
        all_H2_Info_unmentioned_native_private_fields_and_instruction_inputs_free=True,
        actual_fifth_boundary_or_sixth_signal_or_pulse_or_terminal_history_proved=False,
        additional_rule_programme_layout_or_constant_change=False,active_G17_modified=False,
        general_eroder_or_higher_error_map_or_positive_iid_proved=False,global_reliability_established=False,
        seconds=time.monotonic()-start)
    (out/'signal_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({key:result[key] for key in ('sixth_MF1021_fixed_one_colonies','sixth_MF1021_unspecified_colonies',
        'native_constant_bit_equalities','far_right_noncanonical_source_last_colony')}),flush=True)
    print(json.dumps(dict(seconds=receipt['seconds'],actual_history_proved=False)),flush=True)


if __name__=='__main__':main()
