"""Read-only GAW20 provenance and all-phase compositional-contract replay."""
from pathlib import Path
import hashlib,importlib.util,json,sys,time
import check_gaw20_padding_congruence02 as congruence
import check_gaw20_native_absorption as absorption
S=Path(__file__).resolve().parent;ROOT=S.parents[3]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw20'
own=congruence.own;k=own.k

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def assets(m):
    for p,h in m['assets_sha256'].items():assert sha(ROOT/p)==h,(p,'frozen source or receipt differs')
def without_timer(d):return {key:value for key,value in d.items() if key!='elapsed_seconds'}
def canonical(d):return json.loads(json.dumps(d))
def module(path,name,argv=None):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec)
    old=sys.argv
    try:
        if argv is not None:sys.argv=argv
        spec.loader.exec_module(m)
    finally:sys.argv=old
    return m

def main():
    started=time.monotonic();mp=D/'GAW20_standalone_assets02.json';manifest=load(mp);assets(manifest)
    inherited=load(ROOT/manifest['inherited_manifest']);assets(inherited)
    assert len(inherited['assets_sha256'])==manifest['inherited_assets']==518
    assert all(manifest['assets_sha256'][p]==h for p,h in inherited['assets_sha256'].items())
    assert (k.Q,k.U,k.WORD,k.PRIMARY_START,k.FRAME_WORDS)==(8192,1048576,100,3848,496)
    rom=load(ROOT/'figs/gray_counterexamples/unregistered_gaw2/GAW2R_rom.json')
    assert list(own.ROM.bits)==rom['bits']
    assert [hex(v) for v in own.ROM.dictionary]==rom['dictionary']
    for name in ('token_count','used_dictionary','token_bits','early_pc'):
        assert getattr(own.ROM,name)==rom[name]
    listing=load(ROOT/'figs/gray_counterexamples/unregistered_gaw2/GAW2R_listing.json')
    # Listing is the exact frozen full instruction/layout object.
    assert listing['instructions']==own.LISTING and listing['labels']==own.LABEL
    failure=load(D/'GAW20_failure_provenance.json')
    assert not failure['rule_ROM_accepted_receipts_or_main_documents_changed']
    for name,h in failure['retained_assets_sha256'].items():assert sha(ROOT/name)==h
    assert 'AssertionError' in (D/'GAW20_contract_discovery01.log').read_text()
    manifest_failure=load(D/'GAW20_manifest_failure_provenance.json')
    assert not manifest_failure['rule_mathematical_receipts_or_accepted_ancestors_changed']
    for name,h in manifest_failure['retained_assets_sha256'].items():assert sha(ROOT/name)==h
    bad_manifest=load(D/'GAW20_standalone_assets.json')
    bad_path='figs/gray_counterexamples/unregistered_gaw20/GAW20_freeze01.log'
    assert bad_manifest['assets_sha256'][bad_path]==hashlib.sha256(b'').hexdigest()
    assert 'GAW20_freeze01.log' in (D/'GAW20_readonly_replay01.log').read_text()
    old=load(D/'GAW20_padding_congruence_certificate.json')
    cr=congruence.main();nr=absorption.main()
    assert all(cr[key]==value for key,value in old.items())
    assert cr['every_emitted_instruction_decoded_and_operands_width_checked']==3726
    assert len(cr['every_full_word_input_LDX_site'])==23
    assert len(cr['early_raw_native_LDX_sites'])==2
    assert cr['paired_prefix']['paired_prefix_states']==2139
    assert cr['paired_prefix']['body_cut_states']==51
    assert nr['computed_F1_F2zero_does_not_imply_final_Workspacezero']
    print(json.dumps(dict(stage='new_padding_and_native_category_contracts',assets=len(manifest['assets_sha256']))),flush=True)

    # R selection is import-time in the accepted checker. It runs read-only.
    contracts=module(S.parent/'unregistered_gaw2/check_gaw2_contracts.py',
        'gaw20_frozen_gaw2r_contracts',['check_gaw2_contracts.py','R'])
    actual=contracts.main(write=False)
    expected=load(ROOT/'figs/gray_counterexamples/unregistered_gaw2/GAW2R_contracts.json')
    assert canonical(without_timer(actual))==without_timer(expected)
    vc=actual['checks']['vote_contract']
    assert vc['instruction_updates']==86 and vc['call_sites']==120
    assert vc['preserved_registers']==[2,9,10,12,13,14,15]
    assert actual['checks']['native_recipe_instances']==7
    # Re-evaluate every exact phase class of the frozen bounded/travel DAG.
    cost=load(ROOT/'figs/gray_counterexamples/unregistered_gaw2/GAW2R_compositional_cost.json')
    assert len(cost['phase_partition'])-1==len(cost['records'])==72
    fresh=[own.run(clock) for clock in cost['phase_partition'][:-1]]
    assert canonical(fresh)==cost['records']
    assert max(r['tick_bound'] for r in fresh)==141557
    assert cost['available_ticks']==147455
    print(json.dumps(dict(stage='all_phase_native_helper_body_and_cost_contracts',phase_classes=len(fresh))),flush=True)

    period=module(S.parent/'unregistered_gaw2/check_gaw2_period.py','gaw20_frozen_physical_period')
    pr=load(ROOT/'figs/gray_counterexamples/unregistered_gaw2/GAW2_period_contracts.json')
    assert canonical(period.geometry_contract(k))==pr['geometry']
    assert canonical(period.courier_contract(k))==pr['couriers']
    assert canonical(period.native_contract(k))==pr['native_quiet']
    base=module(S.parent/'unregistered_gaw4/check_gaw4_real1_mail.py','gaw20_frozen_intact_H')
    intact=base.initializer_checks()
    assert intact['all496_fields_proved_by_definition'] and intact['intact_every_level']
    assert intact['unused_and_special_Info_zero'] and intact['Programme_uses_actual_beta']
    legal=load(ROOT/'figs/gray_counterexamples/unregistered_gaw2/GAW2_three_gather_period_certificate.json')
    assert legal['GAW2R_noiseless_physical_period_proved']
    assert legal['all_upper_raw_patterns_quantified'] and not legal['upper_SF_or_clock_coherence_assumed']
    assert legal['correctly_encoded_reset_lower_start_required']
    assert sha(S.parent/'unregistered_gaw2/GAW2_THREE_GATHER_PERIOD.md')==legal['proof_sha256']
    assert legal['universal_prepared_tick_bound']==141557
    assets(manifest);assets(inherited)
    r=dict(passed=True,assets_verified=len(manifest['assets_sha256']),inherited_assets_verified=518,
        Q=k.Q,U=k.U,error_lambda=24,error_separation=104,
        exact_unchanged_GAW2R_ROM_dictionary_listing_scalar_local_R=True,
        prepared_family='canonical common legal upper Age; zero old native F1/F2/WF; coherent SF; one arbitrary496 Word100 record anywhere',
        actual_unmasked_native_padding_and_all49600_replacement_bits_quantified=True,
        exact_conditional_native_padding_congruence_and_four_clean_vote_absorption=True,
        computed_repair_flags_zero_final_Workspace_equal_not_assumed_zero=True,
        all72_phase_helper_body_CFG_and141557_late213_early_deadlines_replayed=True,
        exact_actual_three_gather_temporal_bank_zero_early_flag_couriers_and_full_raw_commit=True,
        written_global_prepared_period_identity='R^U(E_raw(W,0))=E(R(C),0)',
        earlier_boundary_legal_period_and_actual_terminating_H_dependencies_checked=True,
        written_minimal_first_command_proves_all_RnH_zero_flags_and_SF_coherence=True,
        written_all_n_all_locations_single_raw_record_contraction_to_intact_shadow=True,
        direct_intact_start_Info_only_member_reachability_proved=True,
        uniform_original_error_class_for_all_prepared_members=False,
        arbitrary_multiple_records_lower_work_geometry_or_higher_noise_repair=False,
        generic_malformed_native_projection_quotient=False,
        faithful_Gray_Gacs_counterexample_iid_memory_rate_or_shorter_U=False,
        rule_ROM_G17_registered_main_or_accepted_assets_changed=False,
        manifest_sha256=sha(mp),padding_receipt_sha256=sha(D/'GAW20_padding_congruence_certificate02.json'),
        native_receipt_sha256=sha(D/'GAW20_native_absorption_certificate.json'),
        written_proof_sha256=sha(S/'GAW20_ALL_PHASE_SINGLE_RECORD.md'),elapsed_seconds=time.monotonic()-started)
    print(json.dumps(r),flush=True);return r

if __name__=='__main__':main()
