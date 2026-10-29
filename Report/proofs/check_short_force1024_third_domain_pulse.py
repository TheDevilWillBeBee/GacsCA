#!/usr/bin/env python3
"""Sound-domain third-pulse proof certificate and physical/Z bridge.

Finite C domain inclusion, actual source/factor and support arguments are
specified in the written proof. No general eroder, higher map or iid rate.
"""
from pathlib import Path
import ctypes,hashlib,itertools,json,subprocess,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
OUT=ROOT/'figs/robustness'
import proposed_sparse_short_force1024 as proposed


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    begin=time.monotonic();p=proposed.parameters();candidate=proposed.load_artifact()
    probe=json.loads((OUT/'SP29_third_pulse_domain_probe.json').read_text())
    assert probe['checker_sha256']==digest(ROOT/'Report/proofs/probe_short_force1024_third_pulse_domains.py')
    assert probe['finite_domain_recurrence_complete'] and probe['all_6144_steps_GF_determined']
    assert probe['exit_code']==0 and probe['first_unresolved_GF'] is None
    assert probe['domain_values']=={'0':[0],'1':[1],'2':[0,1]}
    assert probe['full_concrete_mask_count']==8192 and probe['domains_do_not_assume_input_independence']
    for key,name in [('inherited_corrected_factor_sha256','SP29_refined_wipe_factor_generated.c'),
        ('inherited_corner_wrapper_sha256','SP29_third_pulse_corners_generated.c'),
        ('generated_domain_factor_sha256','SP29_third_pulse_domains_factor_generated.c'),
        ('generated_domain_wrapper_sha256','SP29_third_pulse_domains_generated.c'),
        ('run_log_sha256','SP29_third_pulse_domains.jsonl'),
        ('final_or_unresolved_state_asset_sha256','SP29_third_pulse_domain_states.npz')]:assert probe[key]==digest(OUT/name),key
    for name,value in probe['receipt_dependencies_sha256'].items():assert value==digest(OUT/name),name
    # Independently evaluate the actual compiled domain tables against sets.
    primitive_source=OUT/'SP29_third_domain_primitive_checks.c'
    primitive_source.write_text(r'''#define main retained_domains_main
#include "SP29_third_pulse_domains_factor_generated.c"
#undef main
int domain_primitive(int op,int a,int b,int c){
    (void)refined_wipe_copy_mask_disagreements;
    (void)refined_wipe_active_majority_disagreements;
    if(op==0)return tri_not(a);
    if(op==1)return tri_and(a,b);
    if(op==2)return tri_or(a,b);
    if(op==3)return tri_mux(a,b,c);
    if(op==4)return tri_ge(a,b,c);
    return -1;
}
int domain_GF(int f1,int f2,int right,int left){
    int choice=tri_or(tri_not(f1),f2);
    return choice==2?right==left?right:2:choice?right:left;
}
''')
    so=Path('/tmp/SP29_third_domain_primitive_checks.so')
    subprocess.run(['cc','-O2','-std=c11','-shared','-fPIC','-Wall','-Wextra','-Werror',str(primitive_source),'-o',str(so)],check=True)
    library=ctypes.CDLL(str(so));primitive=library.domain_primitive;gf=library.domain_GF
    primitive.argtypes=gf.argtypes=[ctypes.c_int]*4;primitive.restype=gf.restype=ctypes.c_int
    values={0:{0},1:{1},2:{0,1}};primitive_checks=gf_checks=0
    for op,arity in ((0,1),(1,2),(2,2),(3,3)):
        for domains in itertools.product(range(3),repeat=arity):
            args=(*domains,*([0]*(3-arity)));actual=primitive(op,*args)
            concrete=set()
            for inputs in itertools.product(*(values[d] for d in domains)):
                if op==0:value=not inputs[0]
                elif op==1:value=inputs[0] and inputs[1]
                elif op==2:value=inputs[0] or inputs[1]
                else:value=inputs[1] if inputs[0] else inputs[2]
                concrete.add(int(value))
            assert actual in values and values[actual]==concrete,(op,domains,actual,concrete)
            primitive_checks+=1
    for low in range(12):
        for high in range(low,12):
            for threshold in range(13):
                actual=primitive(4,low,high,threshold);image={int(count>=threshold) for count in range(low,high+1)}
                assert actual in values and values[actual]==image,(low,high,threshold,actual,image)
                primitive_checks+=1
    for f1,f2,right,left in itertools.product(range(3),range(3),range(2),range(2)):
        actual=gf(f1,f2,right,left)
        image={right if (not a or b) else left for a,b in itertools.product(values[f1],values[f2])}
        assert values[actual]==image,(f1,f2,right,left,actual,image)
        gf_checks+=1
    assert primitive_checks==1062 and gf_checks==36
    log=OUT/'SP29_third_pulse_domains.jsonl';rows=[json.loads(line) for line in log.read_text().splitlines()]
    summary=rows.pop();assert len(rows)==6145 and [r['row'] for r in rows]==list(range(6145))
    assert summary['certificate_complete'] and summary['rows_checked']==6145
    assert summary['GF_support_sites_checked']==len(rows)*262144==1610874880
    assert summary['background_site_equalities']==sum(262144-r['background_hi']+r['background_lo'] for r in rows)==1062876070
    assert all(r['background_lo']==111*p.Q-(8*(r['row']+1)+37) and r['background_hi']==150*p.Q+8*(r['row']+1)+37 for r in rows)
    assert all(0<r['background_lo'] and r['background_hi']<262144 for r in rows)
    final=rows[-1];assert (final['left'],final['right_exclusive'],final['wrong_Addresses'])==(112128,122880,10752)
    assert rows[0]['wrong_Addresses']==12800
    assert sum(r['holes_in_support_hull']>0 for r in rows)==2 and max(r['holes_in_support_hull'] for r in rows)==2
    with np.load(OUT/'SP29_third_pulse_domain_states.npz',allow_pickle=False) as arrays:
        native,code,info=arrays['native'],arrays['code'],arrays['Info'];x=np.arange(262144)
        assert native.shape==(8,262144) and code.shape==info.shape==(262144,)
        assert np.array_equal(native[0],(112128<=x)&(x<122880))
        assert np.array_equal(native[1],((111616<=x)&(x<112128))|((122368<=x)&(x<122880)))
        assert not native[2:].any() and not code.any()
        assert set(np.unique(info))=={0,1,2}
        fixed509=np.flatnonzero(info[509::1024]==1).tolist()
        fixed1021=np.flatnonzero(info[1021::1024]==1).tolist();unknown1021=np.flatnonzero(info[1021::1024]==2).tolist()
        assert fixed509==list(range(116,120)) and fixed1021==[*range(128,136),*range(141,145)]
        assert unknown1021==[*range(136,141),*range(145,150)]
        assert np.flatnonzero(info==2).tolist()==[j*p.Q+1021 for j in unknown1021]
        assert int((info==1).sum())==16 and int((info==2).sum())==10
        assert all(info[j*p.Q+phase]==0 for j,phase in ((111,1021),(115,509),(127,1021)))
    corner=json.loads((OUT/'SP29_third_pulse_corner_probe.json').read_text())
    assert corner['tested_enclosure_masks']==[0,8191] and not corner['all_enclosure_masks_checked']
    assert probe['two_concrete_corner_endpoints_enclosed'] is True
    source=json.loads((OUT/'SP29_recovered_right_retained_certificate.json').read_text())
    assert source['actual_third_complete_signal_thirteen_bit_enclosure_proved']
    assert source['third_complete_signal_unspecified_bit_count']==13 and not source['unspecified_bits_assumed_independent']
    factor=json.loads((OUT/'SP29_refined_wipe_certificate.json').read_text())
    assert factor['corrected_refined_old_GF_factor_proved']
    deps=('SP29_third_pulse_domain_probe.json','SP29_third_pulse_corner_probe.json',
        'SP29_recovered_right_retained_certificate.json','SP29_refined_wipe_certificate.json',
        'SP29_second_signal_enclosure_certificate.json','SP29_second_right_boundary_certificate.json',
        'SP29_crossing_history_certificate.json','SP29_foreign_cache_erasure_certificate.json',
        'SP29_emerging_foreign_source_certificate.json','SP29_protected_scratch_certificate.json',
        'SP29_next_ghost_signal_certificate.json','SP29_first_signal_certificate.json',
        'SP29_third_domain_initial_library_failure.json')
    receipt=dict(proposal='SP29',scope='Actual third shrinking pulse on Z for original clock0 error/arbitrary upper Info/no later errors; all thirteen-bit masks enclosed by sound domain; no fourth signal/eroder/iid',
        Q=p.Q,U=p.U,T_wf=p.T_wf,third_pulse_start_computed_time=2*p.U+p.T_wf,
        third_pulse_end_computed_time=2*p.U+p.T_wf+6144,pulse_updates=6144,force_duration=2048,
        initial_wrong_GF_interval=[118272,131072],final_wrong_GF_interval=[112128,122880],
        initial_wrong_GF_width=12800,final_wrong_GF_width=10752,width_decrease=2048,left_displacement=-6144,right_displacement=-8192,
        domain_primitive_set_image_checks=primitive_checks,domain_GF_selector_set_image_checks=gf_checks,
        input_unspecified_bit_count=13,concrete_input_mask_count=8192,input_bit_correlations_allowed=True,
        actual_domain_inclusion_proved_by_induction=True,all_update_rows_GF_and_header_code_exact=True,
        all_6145_rows_finite_domain_checked=True,GF_site_checks=summary['GF_support_sites_checked'],
        exterior_background_equalities=summary['background_site_equalities'],
        final_infinite_line_protected_interval=[64467,202797],quotient_size=262144,
        final_native_singleton_quiet_template_proved=True,all_8192_masks_have_same_native_endpoint=True,
        final_MF509_known_one_colonies=fixed509,final_MF1021_known_one_colonies=fixed1021,
        final_MF1021_unspecified_colonies=unknown1021,final_Info_known_one_primary_count=16,final_Info_unspecified_primary_count=10,
        initial_unspecified_111_1021_115_509_127_1021_erased_to_known_zero=True,
        intermediate_noninterval_GF_rows=2,maximum_intermediate_GF_holes=2,
        inherited_domain_log_flag_and_Info_sum_keys_are_domain_code_sums=True,
        inherited_domain_log_raw_wipe_diagnostic_counters_used_or_validated=False,
        domain_GF_stop_witness_occurred=False,actual_third_pulse_on_Z_proved=True,
        fourth_signal_or_general_eroder_higher_map_or_positive_iid_rate_proved=False,
        global_reliability_established=False,active_G17_modified=False,rule_programme_or_constant_change=False,
        numerical_whole_CA_trajectory_used=False,checker_sha256=digest(__file__),
        written_proof_sha256=digest(ROOT/'Report/proofs/SP29_THIRD_DOMAIN_PULSE.md'),
        proposal_source_sha256=digest(proposed.__file__),proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        primitive_C_source_sha256=digest(primitive_source),primitive_shared_library_sha256=digest(so),
        domain_factor_C_source_sha256=digest(OUT/'SP29_third_pulse_domains_factor_generated.c'),
        domain_wrapper_C_source_sha256=digest(OUT/'SP29_third_pulse_domains_generated.c'),
        domain_run_log_sha256=digest(log),domain_endpoint_asset_sha256=digest(OUT/'SP29_third_pulse_domain_states.npz'),
        receipt_dependencies_sha256={name:digest(OUT/name) for name in deps},seconds=time.monotonic()-begin)
    (OUT/'SP29_third_domain_pulse_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({key:receipt[key] for key in ('domain_primitive_set_image_checks','domain_GF_selector_set_image_checks',
        'third_pulse_end_computed_time','final_wrong_GF_interval','actual_third_pulse_on_Z_proved','seconds','global_reliability_established')}),flush=True)


if __name__=='__main__':main()
