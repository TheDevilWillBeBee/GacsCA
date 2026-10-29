"""Read-only bootstrap replay and interfaces for the new16Q history.

Repeats full-net cofactors and checks frozen factor wrappers/row traces;
does not rerun the 944-second domain executions or trillion-tick CA.
The written proof supplies physical-history and infinite-line inductions.
"""
from pathlib import Path
from types import FunctionType
import hashlib,json,subprocess,sys,tempfile,time
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'Report/proofs'))
import proposed_sparse_signal_reservation1024 as proposed
import check_short_force1024_GF_bank_closure as bank
import probe_sp30_16Q_source_bootstrap as driver

OUT=ROOT/'figs/robustness';CAMPAIGN=OUT/'unregistered_16Q_source_bootstrap'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def normal(v):return json.loads(json.dumps(v))
def model_read(path):
    m=json.loads(path.read_text());m['records']={int(k):v for k,v in m['records'].items()};return m

def main(write=True):
    started=time.monotonic();p=proposed.parameters();c=proposed.load_artifact()
    assert (p.Q,p.U,p.T_wf)==(1024,475136,278401)
    assert c.digest()=='add9c6c446d80fcd1f19e7b154944479421a0d40c86db8af8f4c0c2de8f9eb8e'
    assert c.comp.digest=='dc8b5065401fc4e363082224535317ee8814a9a94e6e48e6d1769939793fa19b'
    run=json.loads((CAMPAIGN/'receipt.json').read_text())
    assert run['checker_sha256']==sha(driver.__file__)
    assert run['candidate_sha256']==c.digest() and run['completed_periods']==7
    assert not run['actual_rule_history_or_global_reliability_proved']
    receipts={};dep_names=(
        'SP30_native_pulse_certificate.json','SP29_third_domain_pulse_certificate.json',
        'SP30_GF_bank_closure_certificate.json','SP30_left_source_contract_certificate.json',
        'SP30_translation_class_certificate.json','unregistered_quiet_frame/certificate.json',
        'unregistered_pulse_store/certificate.json','unregistered_finite_regeneration/certificate.json')
    for name in dep_names:
        receipts[name]=json.loads((OUT/name).read_text())
        assert not receipts[name]['global_reliability_established']
    assert receipts['SP30_native_pulse_certificate.json']['unrestricted_native_header_output_node_equalities']==73
    domains=receipts['SP29_third_domain_pulse_certificate.json']
    assert domains['actual_domain_inclusion_proved_by_induction']
    assert domains['domain_primitive_set_image_checks']==1062
    assert domains['domain_GF_selector_set_image_checks']==36
    assert domains['domain_factor_C_source_sha256']==sha(OUT/'SP29_third_pulse_domains_factor_generated.c')
    protocol=receipts['unregistered_quiet_frame/certificate.json']
    assert protocol['conditional_Mail_Info_and_complete_frame_execution_proved']
    assert protocol['native_outputs_structurally_instruction_independent']==31
    assert protocol['complete_frame_SF_holder_interval']==[1,1023]
    assert protocol['native_footprint_interval']==[-36,1060]
    store=receipts['unregistered_pulse_store/certificate.json']
    assert store['Hold_ROM_keys']==90112 and store['pending_presence_kind_cases']==256
    assert store['left_edge_clearance']==449 and store['right_GF_clearance']==20
    finite=receipts['unregistered_finite_regeneration/certificate.json']
    assert finite['bootstrap_period']==6 and finite['bootstrap_template_L_R']==[92,98]
    assert finite['bootstrap_full_left_last_colony']==89
    assert finite['bootstrap_edge_GF_F1_colony']==90
    assert finite['bootstrap_right_GF_zero_colonies']==[98,120]
    assert finite['pulse_periods_inclusive']==[6,278400]
    Q,U,TF,S=p.Q,p.U,p.T_wf,p.T_wf+6144
    expected=[(128,143,122,135,142),(122,135,116,127,139),
        (116,127,110,119,135),(110,119,104,111,130),
        (104,111,98,104,125),(98,104,92,98,120),(92,98,86,92,115)]
    model=dict(left_canonical_through=127,right_canonical_from=144,records={})
    cofactor_count=site_checks=background_checks=0;asset_hashes={};period_results=[]
    quiet_fn=FunctionType(bank.quiet.__code__,dict(bank.__dict__,proposed=proposed),'quiet')
    route_fn=FunctionType(bank.routes.__code__,dict(bank.__dict__,proposed=proposed),'routes')
    with tempfile.TemporaryDirectory(prefix='SP30_16Q_read_only_check_') as temporary:
        temporary=Path(temporary)
        for period,(L,R,nextL,nextR,lastzero) in enumerate(expected):
            d=CAMPAIGN/f'p{period}';saved=model_read(d/'source_model.json')
            assert saved==model,(period,'source model')
            signals,native=driver.signal_and_outputs(p,period,L,R,model)
            assert normal(list(signals.values()))==json.loads((d/'cofactors.json').read_text())
            cofactor_count+=len(signals)
            for j,out in native.items():
                if j<=L-9:assert out==driver.canonical(p,j,period+1),(period,j,out)
            for f in ('addr','f1'):
                assert native[L-8][f]==driver.canonical(p,L-8,period+1)[f]
            pulse=json.loads((d/'receipt.json').read_text())
            assert pulse==run['pulse_receipts'][period]
            assert pulse['initial_L_R']==[L,R] and pulse['endpoint_L_R']==[nextL,nextR]
            assert pulse['endpoint_wrong_GF_sites']==(nextR-nextL)*Q+512
            assert pulse['all_row_GF_hull']==[L*Q-7616,R*Q]
            assert pulse['finite_domain_complete'] and not pulse['actual_rule_history_proved']
            tempd=temporary/f'p{period}';tempd.mkdir()
            generated,seed,ones,free=driver.wrapper(period,L,R,signals,tempd)
            assert generated.read_bytes()==(d/'generated.c').read_bytes()
            assert pulse['seed_interval']==list(seed)
            assert pulse['MF1021_one_colonies']==ones and pulse['MF1021_free_colonies']==free
            for key,name in (('source_sha256','generated.c'),('log_sha256','trace.jsonl'),
                ('asset_sha256','endpoint.npz')):assert pulse[key]==sha(d/name)
            assert pulse['factor_sha256']==sha(OUT/'SP29_third_pulse_domains_factor_generated.c')
            executable=temporary/f'p{period}_rebuilt'
            subprocess.run(['cc','-O3','-std=c11','-Wall','-Wextra','-Werror','-Wno-parentheses',
                str(d/'generated.c'),'-o',str(executable)],check=True,capture_output=True)
            assert sha(executable)==pulse['executable_sha256']
            rows=[json.loads(v) for v in (d/'trace.jsonl').read_text().splitlines()]
            summary=rows.pop();assert summary==pulse['summary']
            assert [r['row'] for r in rows]==list(range(6145))
            assert summary['GF_support_sites_checked']==6145*262144
            assert summary['background_site_equalities']==sum(
                262144-r['background_hi']+r['background_lo'] for r in rows)
            assert summary['refined_wipe_copy_mask_disagreements']==0
            assert summary['refined_wipe_active_majority_disagreements']==0
            for r in rows:
                assert r['background_lo']==seed[0]-8*(r['row']+1)-37
                assert r['background_hi']==seed[1]+8*(r['row']+1)+37
                assert Q+37<r['background_lo']<r['background_hi']<262144-37
                assert r['wrong_Addresses']>0
            assert [min(r['left'] for r in rows),max(r['right_exclusive'] for r in rows)]==pulse['all_row_GF_hull']
            with np.load(d/'endpoint.npz',allow_pickle=False) as a:
                assert set(a.files)=={'native','code','Info'}
                x=np.arange(262144);lo=nextL*Q-512;hi=nextR*Q
                assert a['native'].shape==(8,262144)
                assert np.array_equal(a['native'][0],(lo<=x)&(x<hi))
                assert np.array_equal(a['native'][1],((lo-512<=x)&(x<lo))|((hi-512<=x)&(x<hi)))
                assert not a['native'][2:].any() and not a['code'].any()
                assert np.all(a['Info']<=2)
            quiet=quiet_fn(p,L,R);routes=route_fn(p,L,R)
            assert quiet['quiet_gate_cofactors']==28
            assert routes['complete_foreign_frames']==list(range(L,R))
            model=driver.next_model(p,period,L,R,pulse,native)
            assert normal(model)==json.loads((d/'next_source_model.json').read_text())
            assert model['left_canonical_through']==nextL-3
            assert model['right_zero_GF_prefix']==[nextR,lastzero]
            for f in ('addr','f1'):
                assert model['records'][nextL-2][f]==driver.canonical(p,nextL-2,period+1)[f]
            if period==5:
                assert nextL==92 and nextR==98
                assert all(driver.fixed_word(model['records'][j]['addr'])==0 for j in range(98,121))
            site_checks+=summary['GF_support_sites_checked'];background_checks+=summary['background_site_equalities']
            period_results.append(dict(period=period,template=[L,R],endpoint=[nextL,nextR],
                right_zero_GF_prefix=[nextR,lastzero],quiet=quiet,foreign_routes=routes,
                exact_native_cofactors=len(signals)))
            for name in ('receipt.json','source_model.json','cofactors.json','next_source_model.json',
                'generated.c','compile.log','stderr.log','trace.jsonl','endpoint.npz'):
                asset_hashes[str((d/name).relative_to(ROOT))]=sha(d/name)
    # Dense16Q original class at c16: complete support/no exterior.
    start,end=127*Q,143*Q
    assert end-start==16384 and end-start-1<16*Q<24*Q
    assert end-start-7>=15*Q and end-start<Q*Q
    assert (end-1-start)<Q*Q
    alias_mask=(set(range(58,901))-{509,515})|{901,902,965}
    alias_checks=0
    for phase in (3,509,515,1021):
        for shift in (0,512):
            for slot in proposed.SLOTS:
                assert ((phase-slot+shift)%Q+slot)%Q not in alias_mask;alias_checks+=1
    def interval(period):return [(122-6*period)*Q-512,(128-6*period)*Q]
    spatial=[6,347];temporal=[6,29703];distance=1706
    spatial_width=interval(spatial[0])[1]-interval(spatial[1])[0]
    time_span=(temporal[1]-temporal[0])*U
    min_error_distance=start-interval(distance)[0]
    assert spatial_width==2101760>2*Q*Q
    assert time_span==14110113792>U*U//16
    assert min_error_distance==10487296>10*Q*Q
    assert all(6<=v<TF for v in (*spatial,*temporal,distance))
    proof=Path(__file__).with_name('SP30_16Q_ACTUAL_REGENERATION.md')
    for name in ('receipt.json',):asset_hashes[str((CAMPAIGN/name).relative_to(ROOT))]=sha(CAMPAIGN/name)
    asset_hashes['figs/robustness/SP30_16Q_source_bootstrap_unregistered_run.log']=sha(OUT/'SP30_16Q_source_bootstrap_unregistered_run.log')
    result=dict(name='SP30 original c16 real2 history/bootstrap/finite translating endpoints',
        Q=Q,U=U,T_wf=TF,pulse_end=S,checker_sha256=sha(__file__),proof_sha256=sha(proof),
        driver_sha256=sha(driver.__file__),candidate_sha256=c.digest(),netlist_sha256=c.comp.digest,
        source_dependencies_sha256={name:sha(ROOT/name) for name in (
            'Report/proofs/proposed_sparse_signal_reservation1024.py','gacsca/netlist.py',
            'Report/proofs/check_short_force1024_GF_bank_closure.py',
            'Report/proofs/check_signal_reservation1024_second_signal.py')},
        proof_dependencies_sha256={name:sha(ROOT/'Report/proofs'/name) for name in (
            'SP30_OWN_RULE.md','SP30_FIRST_SIGNAL.md','SP30_NATIVE_PULSE.md',
            'SP30_GF_BANK_CLOSURE.md','SP30_TRANSLATION_CLASS.md',
            'unregistered_terminal/SP30_QUIET_FRAME_PROTOCOL.md',
            'unregistered_terminal/SP30_PULSE_STORE_PROTECTION.md',
            'unregistered_terminal/SP30_FINITE_REGENERATION.md')},
        receipt_dependencies_sha256={name:sha(OUT/name) for name in dep_names},
        retained_assets_sha256=asset_hashes,primary_Gray_text_sha256=sha(ROOT/'papers_txt/gray_readers_guide.txt'),
        dense_original_support=[start,end],error_time=0,real_error_level_at_c16=2,
        real0_or_real1_or_higher_original_errors=False,
        minimum_integer_c_for_this_row_real2=16,
        source_full_net_cofactors_replayed=cofactor_count,period_results=period_results,
        GF_site_checks_in_retained_executions=site_checks,background_domain_checks=background_checks,
        commit_alias_checks=alias_checks,bootstrap_period=6,bootstrap_H6_template=[92,98],
        bootstrap_H6_left_prefix_last=89,bootstrap_H6_edge=90,bootstrap_H6_right_GF_zero=[98,120],
        actual_variable_width_prefix_and_store_composition_proved=True,
        actual_six_period_H6_bootstrap_on_Z_proved=True,
        existing_J216_H_invariant_induction_applies_verbatim_after_bootstrap=True,
        actual_finite_translating_pulse_count=TF-6,actual_finite_pulse_periods=[6,TF-1],
        literal_Prop5_class2_spatial_witness=spatial,literal_Prop5_required_width=spatial_width,
        literal_Prop5_class2_temporal_witness=temporal,literal_Prop5_required_time_span=time_span,
        R_spatial_distance_witness_period=distance,R_minimum_original_error_distance=min_error_distance,
        literal_Prop5_and_R_envelopes_false_for_frozen_F30_at_c16=True,
        upper_WF_or_permanent_defect_or_general_eroder_or_alternate_envelope_proved=False,
        iid_memory_failure_or_reliability_or_minimum_sufficient_change_proved=False,
        G17_or_Gray_construction_refuted=False,active_rule_or_frozen_SP30_changed=False,
        direct_trillion_tick_whole_CA_execution_claimed=False,
        global_reliability_established=False,elapsed_seconds=time.monotonic()-started)
    dest=OUT/'unregistered_16Q_actual_regeneration';dest.mkdir(exist_ok=True)
    if write:(dest/'certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('source_full_net_cofactors_replayed',
        'actual_six_period_H6_bootstrap_on_Z_proved','actual_finite_translating_pulse_count',
        'literal_Prop5_and_R_envelopes_false_for_frozen_F30_at_c16',
        'global_reliability_established','elapsed_seconds')}),flush=True)

if __name__=='__main__':main()
