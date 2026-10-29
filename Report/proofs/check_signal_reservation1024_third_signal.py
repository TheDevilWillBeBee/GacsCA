#!/usr/bin/env python3
"""SP30 actual second-boundary sources, third signal/domain pulse and bank.

The written proof supplies the physical programme/store and infinite-line
inductions. No arbitrary-fault eroder, higher map or iid rate is asserted.
"""
from itertools import product
from pathlib import Path
from types import FunctionType
import hashlib,json,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,Compiled
from gacsca import rule_g
import proposed_sparse_signal_reservation1024 as proposed
from check_signal_reservation1024_second_signal import blocked
import check_short_force1024_GF_bank_closure as inherited_bank


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def left_source_words(p,c):
    phases={(r['field'],r['bit']):r['address'] for r in proposed.dependency_table(p)}
    strips=((121*p.Q,122*p.Q-512),(136*p.Q-512,136*p.Q));records=[]
    for j in range(83,115):
        class Captured(Net):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,field,bit=key;col=j+d
                    if field in ('addr','age','f1','wf1'):
                        if blocked(strips,j,d,phases[field,bit],p.Q):return 0
                        assert col<=120
                        if field=='addr':return ((col%p.Q)>>bit)&1
                        if field=='f1':return 0
                        if col==120:return super().input(('upper_'+field,col,bit))
                        return ((p.age_code(1)>>bit)&1) if field=='age' else 0
                return super().input(key)
        n,_=proposed.full_net(p,Captured);checks=0
        for field,value in dict(addr=j,age=p.age_code(2),f1=0,wf1=0).items():
            for bit in range(dict(c.schema)[field]):
                assert n.outputs['y',field,bit]==(value>>bit)&1,(j,field,bit)
                checks+=1
        records.append(dict(colony=j,GF=j,Age=p.age_code(2),Flag1=0,WF1=0,
            constant_bit_equalities=checks,netlist_sha256=Compiled(n).digest))
    assert len(records)==32 and sum(r['constant_bit_equalities'] for r in records)==992
    return records


def third_cofactors(p):
    table=proposed.dependency_table(p);phases={(r['field'],r['bit']):r['address'] for r in table}
    strips=((115*p.Q,116*p.Q-512),(128*p.Q-512,128*p.Q));records=[];routes=0
    for j in (*range(77,115),*range(128,184)):
        left=j<=114
        for row in table:
            if row['field'] not in ('addr','age','f1','wf1'):continue
            for d in (0,*row['offsets']):
                crossed=blocked(strips,j,d,row['address'],p.Q)
                assert crossed==blocked(strips,j,d,59,p.Q)
                assert crossed or (j+d<=114 if left else j+d>=128)
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
                            if col==114:return super().input(('upper_'+field,col,bit))
                            return ((p.age_code(2)>>bit)&1) if field=='age' else 0
                        if field=='addr':
                            if col<=140:return 0
                            if col<=143:return super().input(('upper_GF',col,bit))
                            return ((col%p.Q)>>bit)&1
                        if field=='f1':return int(136<=col<=146)
                        if field=='age':return super().input(('upper_Age',col,bit)) if col<=146 else ((p.age_code(2)>>bit)&1)
                        if field=='wf1':return super().input(('upper_WF1',col,bit)) if col<=135 else 0
                return super().input(key)
        n,_=proposed.full_net(p,Captured);node=n.outputs['y','f1',0]
        value=node if node in (0,1) else None
        records.append(dict(colony=j,side='left' if left else 'right',Flag1_constant=value,
            netlist_sha256=Compiled(n).digest,unrelated_fields_H2_Info_and_I_free=True))
    ones=[r['colony'] for r in records if r['Flag1_constant']==1]
    optional=[r['colony'] for r in records if r['Flag1_constant'] is None]
    assert ones==[112,113,114,*range(128,136),141,142,143,144]
    assert optional==[111,*range(136,141),*range(145,150)]
    assert routes==179070 and len(records)==94
    assert 76+37<114 and 184-37>146
    return records,routes,ones,optional


def main():
    started=time.monotonic();p=proposed.parameters();c=proposed.load_artifact();out=ROOT/'figs/robustness'
    second=json.loads((out/'SP30_second_signal_certificate.json').read_text())
    right=json.loads((out/'SP30_second_right_native_probe.json').read_text())
    domain=json.loads((out/'SP29_third_domain_pulse_certificate.json').read_text())
    assert second['actual_second_shrinking_native_Info_pulse_on_Z_proved']
    assert second['actual_second_boundary_and_third_complete_foreign_sources_proved']
    assert c.digest()==second['proposed_candidate_sha256']==right['proposed_candidate_sha256']
    assert right['checker_sha256']==digest(ROOT/'Report/proofs/probe_signal_reservation1024_second_right_native.py')
    assert right['source_helper_sha256']==digest(ROOT/'Report/proofs/check_signal_reservation1024_second_signal.py')
    assert right['second_signal_receipt_sha256']==digest(out/'SP30_second_signal_certificate.json')
    assert right['all_H2_and_other_unmentioned_fields_and_I_free'] and not right['physical_actual_output_words_or_third_signal_proved']
    right_equalities=0
    for row in right['records']:
        j=row['colony'];expected=dict(addr=0 if j<=140 else None if j<=143 else j,
            age=None if j<=146 else p.age_code(2),f1=int(j<=146),wf1=0)
        assert row['constant_output_words']==expected
        right_equalities+=sum(dict(c.schema)[f] for f,v in expected.items() if v is not None)
    assert right_equalities==1249 and len(right['records'])==48
    hulls=[];logs={}
    for mask in (0,2):
        path=out/f'SP29_second_pulse_case{mask}.jsonl'
        rows=[r for r in map(json.loads,path.read_text().splitlines()) if 'row' in r]
        hull=[min(r['left'] for r in rows),max(r['right_exclusive'] for r in rows)]
        assert len(rows)==6145 and hull==[117312,139264]
        hulls.append(dict(mask=mask,all_row_GF_support_hull=hull));logs[path.name]=digest(path)
    protected=[114*p.Q+phase+s for phase in (*range(59,69),88) for s in proposed.SLOTS]
    assert max(protected)+37<117312 and 113*p.Q+1022<117312 and 136*p.Q+1>=139264
    left=left_source_words(p,c)
    listing=json.loads((out/'SP30_program_listing.json').read_text());issues=[];keys=0
    for phase,shift in product((*range(59,69),88),(0,512)):
        current=phase+shift;selected=[r for r in listing if r[4]==current and r[6]==rule_g.K_HOLD]
        assert len(selected)==1
        row=selected[0];column=row[1]+(row[3]<<p.logNP);age=p.E0+row[1]*p.PL+row[2]
        assert np.flatnonzero(((c.rom[current]>>2)&3)==rule_g.K_HOLD).tolist()==[column]
        assert age+2<p.T_wf if shift==0 else age>p.T_wf+6144
        issues.append(dict(phase=current,phase_shift=shift,input_issue_age=age,materialized_age=age+2,ROM_column=column))
        keys+=c.rom.shape[1]
    assert keys==90112
    recovered=[]
    for j,phase in product(range(128,136),(*range(59,69),88)):
        y=j*p.Q+phase
        assert 124416<=y-2 and y+2<139264 and y-2>=131072
        recovered.append(dict(colony=j,normal_phase=phase,primary=y,initial_final_phases=[phase+512,phase]))
    mask=(set(range(58,901))-{509,515})|{901,902,965}
    for phase,shift,slot in product((3,509,515,1021),(0,512),proposed.SLOTS):
        assert ((phase-slot+shift)%p.Q+slot)%p.Q not in mask
    aliases=[]
    for j,phase in product(range(100,154),(509,1021)):
        y=j*p.Q+phase;labels=[int(118272<=y-s<131072) for s in proposed.SLOTS]
        assert len(set(labels))==1
        virtual=(phase+512*labels[0])%p.Q;active=virtual==1021
        assert active==((116<=j<=127) if phase==509 else (j<=114 or j>=128))
        aliases.append(dict(colony=j,physical_phase=phase,virtual_primary=virtual,special_write=active))
    assert [r['virtual_primary'] for r in aliases if (r['colony'],r['physical_phase']) in ((115,509),(127,1021))]==[509,509]
    third,routes,ones,optional=third_cofactors(p)
    assert len(optional)==11 and (1<<len(optional))==2048
    assert domain['actual_domain_inclusion_proved_by_induction'] and domain['all_update_rows_GF_and_header_code_exact']
    assert domain['all_8192_masks_have_same_native_endpoint'] and not domain['domain_GF_stop_witness_occurred']
    for key,name in (
        ('domain_factor_C_source_sha256','SP29_third_pulse_domains_factor_generated.c'),
        ('domain_wrapper_C_source_sha256','SP29_third_pulse_domains_generated.c'),
        ('domain_run_log_sha256','SP29_third_pulse_domains.jsonl'),
        ('domain_endpoint_asset_sha256','SP29_third_pulse_domain_states.npz')):assert domain[key]==digest(out/name)
    domain_rows=[json.loads(line) for line in (out/'SP29_third_pulse_domains.jsonl').read_text().splitlines()]
    summary=domain_rows.pop()
    assert len(domain_rows)==6145 and [r['row'] for r in domain_rows]==list(range(6145))
    assert summary['certificate_complete'] and summary['GF_support_sites_checked']==1610874880
    assert summary['background_site_equalities']==1062876070
    for row in domain_rows:
        assert row['background_lo']==111*p.Q-8*(row['row']+1)-37
        assert row['background_hi']==150*p.Q+8*(row['row']+1)+37
    assert sum(r['holes_in_support_hull']>0 for r in domain_rows)==2
    with np.load(out/'SP29_third_pulse_domain_states.npz',allow_pickle=False) as arrays:
        native,code,info=arrays['native'],arrays['code'],arrays['Info'];x=np.arange(262144)
        assert np.array_equal(native[0],(112128<=x)&(x<122880))
        assert np.array_equal(native[1],((111616<=x)&(x<112128))|((122368<=x)&(x<122880)))
        assert not native[2:].any() and not code.any()
        assert np.flatnonzero(info[509::1024]==1).tolist()==list(range(116,120))
        assert np.flatnonzero(info[1021::1024]==1).tolist()==[*range(128,136),*range(141,145)]
        assert np.flatnonzero(info==2).tolist()==[j*p.Q+1021 for j in (*range(136,141),*range(145,150))]
        assert all(info[j*p.Q+phase]==0 for j,phase in ((111,1021),(115,509),(127,1021)))
    assert (110<=116,120<=128-1)==(True,True)
    targets=[];true=foreign=0
    for j,bit in product(range(109,120),range(10)):
        y=j*p.Q+571+bit
        assert 112128<=y-2-37 and y+2+37<122880
        if j<115:origin=None;true+=1
        else:
            origin=(j+1)*p.Q-512
            assert 118272<=origin and origin+p.Q<=131072 and y-origin==59+bit;foreign+=1
        targets.append(dict(primary=y,bit=bit,previous_complete_foreign_origin=origin))
    assert (len(targets),true,foreign)==(110,60,50)
    namespace=dict(inherited_bank.__dict__,proposed=proposed)
    foreign_routes=FunctionType(inherited_bank.routes.__code__,namespace,'routes')(p,110,120)
    assert (foreign_routes['routes'],foreign_routes['direct_checks'])==(19500,300)
    deps=('SP30_second_signal_certificate.json','SP30_second_right_native_probe.json',
        'SP30_GF_bank_closure_certificate.json','SP30_native_pulse_certificate.json','SP30_encoded_certificate.json',
        'SP30_front_certificate.json','SP30_symbolic_schedule.json','SP29_third_domain_pulse_certificate.json',
        'SP29_third_pulse_domain_probe.json')
    r=dict(proposal='SP30',scope='J199 actual second-boundary native enclosure, eleven-bit complete third signal and third shrinking projected pulse on Z, next zero bank/fourth foreign sources; no general eroder/iid',
        Q=p.Q,U=p.U,T_wf=p.T_wf,force_duration=2048,
        checker_sha256=digest(__file__),written_proof_sha256=digest(ROOT/'Report/proofs/SP30_THIRD_SIGNAL.md'),
        proposal_source_sha256=digest(proposed.__file__),proposed_candidate_sha256=c.digest(),proposed_netlist_sha256=c.comp.digest,
        full_generated_source_sha256=hashlib.sha256(proposed.generated_source(p).encode()).hexdigest(),
        listing_sha256=digest(out/'SP30_program_listing.json'),
        source_dependencies_sha256={name:digest(ROOT/name) for name in ('gacsca/rule_g.py','gacsca/netlist.py',
            'Report/proofs/check_signal_reservation1024_second_signal.py','Report/proofs/probe_signal_reservation1024_second_right_native.py',
            'Report/proofs/check_short_force1024_GF_bank_closure.py','Report/proofs/SP29_THIRD_DOMAIN_PULSE.md',
            'Report/proofs/check_short_force1024_third_domain_pulse.py')},
        receipt_dependencies_sha256={name:digest(out/name) for name in deps},
        reused_second_pulse_logs_sha256=logs,
        reused_domain_assets_sha256={name:digest(out/name) for name in ('SP29_third_pulse_domains_factor_generated.c',
            'SP29_third_pulse_domains_generated.c','SP29_third_pulse_domains.jsonl','SP29_third_pulse_domain_states.npz')},
        second_pulse_GF_support_hulls=hulls,second_left_native_cofactor_records=left,second_left_native_constant_bit_equalities=992,
        second_right_native_cofactor_records=right['records'],second_right_native_constant_bit_equalities=right_equalities,
        protected_upper114_GF_Flag1_holders=protected,new_twenty_two_phase_Hold_issue_records=issues,
        new_twenty_two_phase_Hold_ROM_key_checks=keys,recovered_native_zero_primary_records=recovered,recovered_native_zero_Info_copies=440,
        actual_second_boundary_native_source_enclosure_proved=True,all_H2_and_other_unrelated_source_fields_and_I_free=True,
        actual_two_phase_commit_alias_zeros_and_partial_track_zeros_proved=True,third_alias_write_classes=aliases,
        third_new_native_capture_gate_routes=routes,third_new_complete_true_Flag1_cofactors=third,
        third_MF509_one_colonies=list(range(116,128)),third_MF509_unspecified_colonies=[],
        third_MF1021_fixed_one_colonies=ones,third_MF1021_unspecified_colonies=optional,
        third_partial_MF509_115_and_MF1021_127_zero=True,complete_actual_third_signal_eleven_bit_enclosure_proved=True,
        actual_optional_bit_values_or_independence_proved=False,third_optional_bit_count=11,third_concrete_enclosure_mask_count=2048,
        new_signal_subset_of_reused_sound_thirteen_bit_domain_proved=True,reused_domain_concrete_mask_count=8192,
        reused_domain_primitive_set_image_checks=1062,reused_domain_GF_selector_checks=36,
        domain_and_corrected_projected_equations_reused_after_actual_new_rule_identity=True,
        actual_new_private_trajectory_or_old_late_suffix_transferred=False,
        projected_Info_fields_restricted_to_two_relevant_alias_tracks=True,
        third_projected_start_computed_time=2*p.U+p.T_wf,third_projected_endpoint_computed_time=2*p.U+p.T_wf+6144,
        third_initial_wrong_GF_interval=[118272,131072],third_final_wrong_GF_interval=[112128,122880],
        third_width_decrease=2048,third_endpoint_template_L_R=[110,120],third_GF_site_checks=1610874880,
        third_background_equalities=1062876070,third_final_protected_interval_on_Z=[64467,202797],
        actual_third_shrinking_projected_pulse_on_Z_proved=True,third_native_endpoint_singleton_and_auxiliary_fields_zero=True,
        third_final_MF509_one_colonies=list(range(116,120)),third_final_MF1021_fixed_one_colonies=[*range(128,136),*range(141,145)],
        third_final_MF1021_unspecified_colonies=[*range(136,141),*range(145,150)],
        third_boundary_computed_time=3*p.U,third_boundary_zero_GF_Info_copies=550,
        third_boundary_zero_primary_records=targets,third_boundary_initially_true_primaries=true,third_boundary_old_foreign_primaries=foreign,
        fourth_source_computed_time=3*p.U+p.T_wf,fourth_complete_foreign_MF509_one_colonies=list(range(110,120)),
        fourth_complete_foreign_GF_source_routes=foreign_routes,actual_third_bank_and_fourth_complete_foreign_sources_proved=True,
        fourth_complete_signal_or_pulse_or_full_upper_data_proved=False,
        arbitrary_phase_width_clock_defects_or_continuing_E0_eroder_proved=False,
        higher_error_map_or_positive_iid_threshold_or_globally_minimal_change_proved=False,
        additional_rule_programme_layout_or_constant_change=False,active_G17_modified=False,
        numerical_whole_CA_trajectory_used=False,global_reliability_established=False,seconds=time.monotonic()-started)
    (out/'SP30_third_signal_certificate.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({key:r[key] for key in ('actual_second_boundary_native_source_enclosure_proved',
        'complete_actual_third_signal_eleven_bit_enclosure_proved','actual_third_shrinking_projected_pulse_on_Z_proved',
        'third_projected_endpoint_computed_time','third_boundary_zero_GF_Info_copies',
        'fourth_complete_foreign_MF509_one_colonies','seconds','global_reliability_established')}),flush=True)


if __name__=='__main__':main()
