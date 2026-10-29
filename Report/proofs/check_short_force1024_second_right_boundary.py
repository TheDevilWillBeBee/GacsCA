#!/usr/bin/env python3
"""Actual second right boundary and third complete true-frame signal bridge.

Written proof supplies the physical prefix/suffix/gather/courier lifts.
No full third signal/pulse or iid theorem is asserted.
"""
from pathlib import Path
import hashlib,json,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,Compiled
import proposed_sparse_short_force1024 as proposed
from check_short_force1024_protected_scratch import blocked


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    begin=time.monotonic();out=ROOT/'figs/robustness';p=proposed.parameters();candidate=proposed.load_artifact()
    listing_path=out/'SP29_program_listing.json';listing=json.loads(listing_path.read_text())
    table=proposed.dependency_table(p);phases={(r['field'],r['bit']):r['address'] for r in table}
    right=json.loads((out/'SP29_right_boundary_native_word_probe.json').read_text())
    third=json.loads((out/'SP29_third_true_signal_probe.json').read_text())
    assert right['checker_sha256']==digest(ROOT/'Report/proofs/probe_short_force1024_right_boundary_native_words.py')
    assert third['checker_sha256']==digest(ROOT/'Report/proofs/probe_short_force1024_third_true_signal.py')
    assert right['proposed_candidate_sha256']==candidate.digest()
    for probe in (right,third):
        assert probe['global_reliability_established'] is False
        for name,value in probe['receipt_dependencies_sha256'].items():assert value==digest(out/name),name
    copies=(13,77,141,205,269)
    assert [row['bit'] for row in right['first_suffix_five_rank13_H2_copy_outputs']]==list(copies)
    assert all(row['constant']==0 for row in right['first_suffix_five_rank13_H2_copy_outputs'])
    first_hold=[]
    for bit in copies:
        phase=phases['h2',bit];rows=[row for row in listing if row[4]==phase and row[6]==1]
        assert len(rows)==1
        row=rows[0];age=p.E0+row[1]*p.PL+row[2]
        assert age>p.E0+280*p.PL
        assert np.flatnonzero(((candidate.rom[phase]>>2)&3)==1).tolist()==[row[1]+(row[3]<<p.logNP)]
        first_hold.append(dict(bit=bit,phase=phase,input_issue_age=age,materialization_age=age+2))
    old_strips=((121*p.Q,121*p.Q+512),(135*p.Q+512,136*p.Q));h2_routes=direct=0
    for j in range(136,184):
        for bit in copies:
            row=next(r for r in table if r['field']=='h2' and r['bit']==bit)
            assert j>=136;direct+=1
            for d in row['offsets']:
                assert j+d>=136 or blocked(old_strips,j,d,row['address'],p.Q)
                for gather in p.gathers_q:
                    assert gather*p.Q+abs(d)*(p.Q//8)+1<p.E0
                    h2_routes+=1
    assert (direct,h2_routes)==(240,5760)
    records=right['records'];assert [r['colony'] for r in records]==list(range(136,184))
    equalities=0
    for row in records:
        j=row['colony'];values=row['outputs']
        expected=dict(addr=0 if j<=140 else None if j<=143 else j,
                      age=None if j<=146 else p.age_code(2),f1=int(j<=146),wf1=0)
        for field,value in expected.items():
            assert values[field]['constant']==value,(j,field)
            if value is not None:equalities+=dict(candidate.schema)[field]
        assert values['h2_copies']=={str(bit):0 for bit in copies}
        equalities+=5
    left=[]
    for j in range(83,115):
        class Captured(Net):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,field,bit=key;col=j+d
                    if field in ('addr','age','f1','wf1'):
                        if blocked(old_strips,j,d,phases[field,bit],p.Q):return 0
                        assert col<=120,(j,key,col)
                        if field=='addr':return ((col%p.Q)>>bit)&1
                        if field=='f1':return 0
                        if col==120:return super().input(('upper_'+field,col,bit))
                        return ((p.age_code(1)>>bit)&1) if field=='age' else 0
                return super().input(key)
        net,_=proposed.full_net(p,Captured);checks=0
        for field,value in dict(addr=j,age=p.age_code(2),f1=0,wf1=0).items():
            for bit in range(dict(candidate.schema)[field]):
                assert net.outputs['y',field,bit]==((value>>bit)&1),(j,field,bit)
                checks+=1
        left.append(dict(colony=j,constant_output_equalities=checks,netlist_sha256=Compiled(net).digest))
    assert sum(r['constant_output_equalities'] for r in left)==992
    pulse=json.loads((out/'SP29_protected_scratch_certificate.json').read_text())
    assert all(row['all_row_GF_support_hull']==[117312,139264] for row in pulse['second_pulse_all_eight_GF_support_hulls'])
    assert 114*p.Q+88+2+37<117312 and 136*p.Q+1>=139264
    recovered=[];keys=0;issues=[]
    for phase in (*range(59,69),88):
        for shift in (0,512):
            current=phase+shift;rows=[row for row in listing if row[4]==current and row[6]==1]
            assert len(rows)==1
            row=rows[0];age=p.E0+row[1]*p.PL+row[2]
            assert age>p.T_wf+6144 if shift else age+2<p.T_wf
            assert np.flatnonzero(((candidate.rom[current]>>2)&3)==1).tolist()==[row[1]+(row[3]<<p.logNP)]
            keys+=candidate.rom.shape[1]
            issues.append(dict(phase=current,shift=shift,input_issue_age=age,materialization_age=age+2))
    for j in range(128,136):
        for phase in (*range(59,69),88):
            y=j*p.Q+phase
            assert 124416<=y-2 and y+2<139264 and y-2>=131072
            recovered.append(dict(colony=j,normal_phase=phase,primary=y))
    assert (keys,len(recovered))==(90112,88)
    new_strips=((115*p.Q,115*p.Q+512),(127*p.Q+512,128*p.Q));routes=0
    for j in (*range(77,115),*range(128,184)):
        for row in table:
            if row['field'] not in ('addr','age','f1','wf1'):continue
            for d in (0,*row['offsets']):
                crossed=blocked(new_strips,j,d,row['address'],p.Q)
                assert crossed==blocked(new_strips,j,d,59,p.Q)
                assert crossed or (j+d<=114 if j<=114 else j+d>=128)
                routes+=1
    assert routes==179070
    assert [r['colony'] for r in third['records'] if r['side']=='left']==list(range(77,115))
    assert [r['colony'] for r in third['records'] if r['side']=='right']==list(range(128,184))
    ones={side:[r['colony'] for r in third['records'] if r['side']==side and r['Flag1_constant']==1] for side in ('left','right')}
    optional={side:[r['colony'] for r in third['records'] if r['side']==side and r['Flag1_constant'] is None] for side in ('left','right')}
    assert ones==dict(left=[112,113,114],right=[*range(128,136),141,142,143,144])
    assert optional==dict(left=[111],right=[*range(136,141),*range(145,150)])
    assert 76+37<114 and 184-37>146
    dependencies=('SP29_right_boundary_native_word_probe.json','SP29_third_true_signal_probe.json',
        'SP29_protected_scratch_certificate.json','SP29_first_boundary_signal_data_certificate.json',
        'SP29_second_signal_enclosure_certificate.json','SP29_next_ghost_signal_certificate.json',
        'SP29_refined_wipe_certificate.json','SP29_symbolic_schedule.json',
        'SP29_front_certificate.json','SP29_encoding_family_certificate.json')
    receipt=dict(proposal='SP29',scope='Actual first five rank13H2 zeros/second right native+retained boundary/third true-frame Flag1 enclosure; same original error/no later errors; no full third pulse or iid',
        Q=p.Q,U=p.U,T_wf=p.T_wf,first_boundary_zero_raw_H2_bits=list(copies),first_boundary_encoded_zero_Info_copies_per_frame=25,
        first_suffix_instructions=right['first_suffix_late_instructions'],first_suffix_terms=right['first_suffix_terms'],
        first_five_H2_actual_Hold_issue_records=first_hold,
        second_right_H2_direct_primary_checks=direct,second_right_H2_capture_route_checks=h2_routes,
        second_right_native_and_H2_constant_output_equalities=equalities,
        second_left_native_cofactor_records=left,second_left_native_constant_output_equalities=992,
        protected_upper114_native_GF_Flag1_proved=True,recovered_128_through135_GF_Flag1_zero_proved=True,
        recovered_native_zero_primary_records=recovered,recovered_native_zero_copy_count=5*len(recovered),
        two_phase_native_Hold_issue_records=issues,two_phase_native_Hold_ROM_key_checks=keys,
        second_right_GF_zero_colonies=list(range(128,141)),second_right_GF_unspecified_colonies=[141,142,143],
        second_right_GF_canonical_from_colony=144,second_right_Flag1_one_colonies=list(range(136,147)),
        second_right_WF1_zero_from_colony=136,second_right_Age_unspecified_colonies=list(range(128,147)),
        second_right_Age_two_from_colony=147,second_right_retained_MF509_zero_from_colony=136,
        third_native_capture_gate_route_checks=routes,third_left_true_Flag1_cofactor_count=38,third_right_true_Flag1_cofactor_count=56,
        third_true_MF1021_one_colonies=[*ones['left'],*ones['right']],
        third_true_MF1021_unspecified_colonies=[*optional['left'],*optional['right']],
        third_true_MF1021_optional_bit_count=11,third_signal_computed_time=2*p.U+p.T_wf,
        actual_first_five_H2_raw_copy_zeros_proved=True,actual_second_right_native_and_retained_boundary_proved=True,
        actual_third_complete_true_frame_Flag1_enclosure_proved=True,
        optional_bits_actual_values_or_independence_proved=False,
        complete_third_signal_or_third_pulse_proved=False,interior_partial_or_recovered_right_retained_data_all_proved=False,
        entire_second_boundary_upper_successor_restored=False,general_eroder_higher_map_or_positive_iid_rate_proved=False,
        global_reliability_established=False,numerical_whole_CA_trajectory_used=False,active_G17_modified=False,rule_programme_or_constant_change=False,
        checker_sha256=digest(__file__),written_proof_sha256=digest(ROOT/'Report/proofs/SP29_SECOND_RIGHT_BOUNDARY.md'),
        proposal_source_sha256=digest(proposed.__file__),helper_sha256=digest(ROOT/'Report/proofs/check_short_force1024_protected_scratch.py'),
        listing_sha256=digest(listing_path),proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        receipt_dependencies_sha256={name:digest(out/name) for name in dependencies},seconds=time.monotonic()-begin)
    (out/'SP29_second_right_boundary_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({key:receipt[key] for key in ('second_right_native_and_H2_constant_output_equalities','second_left_native_constant_output_equalities',
        'third_native_capture_gate_route_checks','third_true_MF1021_one_colonies','third_true_MF1021_unspecified_colonies','seconds','global_reliability_established')}),flush=True)


if __name__=='__main__':main()
