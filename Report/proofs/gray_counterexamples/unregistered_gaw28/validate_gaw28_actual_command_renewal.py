"""Read-only NEW GAW28 math; hash-checked accepted GAW27 reuse.

All old assets/terminal replay results remain pinned. --full-inherited
explicitly requests the separate frozen GAW27 all-new replay too.
"""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,sys,tempfile,time
import discover_gaw28_native_renewal as r
import check_gaw28_symbolic_partial_heads as partial
import check_gaw28_writeback_contracts as contracts
import check_gaw28_actual_command_renewal as commands
S=Path(__file__).resolve().parent;ROOT=S.parents[3]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw28'
S27=S.parent/'unregistered_gaw27';D27=ROOT/'figs/gray_counterexamples/unregistered_gaw27'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def assets(m):
    for p,h in m['assets_sha256'].items():assert sha(ROOT/p)==h,(p,'asset differs')
def run(cmd):
    p=subprocess.run(list(map(str,cmd)),cwd=ROOT,capture_output=True,text=True)
    assert p.returncode==0,(cmd,p.returncode,p.stdout,p.stderr)
    assert not p.stderr,p.stderr
    return p.stdout
def inherited(m):
    mp=ROOT/m['inherited_manifest'];old=load(mp);assets(old)
    assert len(old['assets_sha256'])==m['inherited_assets']==739
    assert all(m['assets_sha256'][p]==h for p,h in old['assets_sha256'].items())
    for key in ('accepted_child_log','accepted_parent_log'):
        z=json.loads((ROOT/m[key]).read_text().splitlines()[-1])
        assert z['passed'] and z['assets_verified']==739 and z['inherited_assets_verified']==690
        assert z['manifest_sha256']==sha(mp)
        assert (z['Q'],z['U'],z['error_lambda'],z['error_separation'])==(8192,1048576,24,104)
        for field in ('inherited_GAW26_all_hashes_and_both_terminal_logs_checked','all_new_math_recomputed',
            'exact_frozen_GAW2R_own_ROM_dictionary_local_R_and_new_analysis_binary_identity',
            'same_intact_H_actual_original_c104_row1_GF_only139264site_real2_no_later_errors',
            'actual_fourth_full_late_banks_86_complete_emissions_two_coupled_pairs_and_all_raw4U',
            'actual_fifth_90_native_early_heads_31_right_sources_no_left_and_native_through5U',
            'conditional_RF_template_integer_Q_equivariance_left_barrier_and_plus3Q_translation_proved',
            'actual_fifth_core_all20488_event_rows_instantiates_conditional_template'):assert z[field] is True
        for field in ('full_5U_Out_Info_future_actual_command_renewal_erosion_or_persistence_proved',
            'canonical_E_relation_at4U_faithful_Gray_iid_higher_error_reliability_or_shorterU_claim',
            'old_registered_main_rules_ROM_or_constants_modified'):assert z[field] is False
        for field,path in [('proof_sha256',S27/'GAW27_FOURTH_BOUNDARY_AND_RF_RENEWAL_REDUCTION.md'),
            ('fourth_full_boundary_receipt_sha256',D27/'GAW27_full_4U_physical_certificate.json'),
            ('fifth_source_receipt_sha256',D27/'GAW27_actual_fifth_sources_certificate.json'),
            ('fifth_native_receipt_sha256',D27/'GAW27_actual_fifth_native_pulse_certificate.json'),
            ('conditional_RF_translation_receipt_sha256',D27/'GAW27_conditional_RF_translation_certificate.json')]:assert z[field]==sha(path)
    if '--full-inherited' in sys.argv:
        spec=importlib.util.spec_from_file_location('gaw28_frozen_gaw27_full',S27/'validate_gaw27_actual_fourth_boundary.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);assert module.main()['passed']
    print(json.dumps(dict(inherited739_asset_hashes_and_both_terminal_logs_checked=True,
        inherited_math_recomputed='--full-inherited' in sys.argv)),flush=True)
    return old
def main():
    start=time.monotonic();mp=D/'GAW28_standalone_assets.json';m=load(mp);assets(m);old=inherited(m)
    k=r.k;own=r.own
    assert (k.Q,k.U,k.WORD,k.FRAME_WORDS,k.PRIMARY_START)==(8192,1048576,100,496,3848)
    assert k.SLOTS==(0,-2,-1,1,2) and k.STAGE_STARTS==(0,32*k.Q,64*k.Q,96*k.Q,102*k.Q)
    # Stable accepted programme identity: the new checkpoint emits no CA.
    rom=r.old.d.own.ROM
    assert rom==own.ROM and rom.token_count==3742 and rom.used_dictionary==1049
    for p,h in m['unchanged_registered_and_active_sha256'].items():assert sha(ROOT/p)==h,(p,'registered/active file changed')
    flags=['gcc','-O3','-std=c11','-Wall','-Wextra','-Werror']
    with tempfile.TemporaryDirectory(prefix='gaw28_readonly_') as tmp:
        tmp=Path(tmp);exe=tmp/'masks'
        run(flags+[S27.relative_to(ROOT)/'gaw27_retained_bank_masks.c','-o',exe])
        assert sha(exe)==sha(D27/'gaw27_retained_bank_masks')
        for tag,events,raw,pre,hist in (
            ('template',D27/'GAW27_RF_template_native_events01.bin','GAW28_RF_template_retention_issue01.json','GAW28_RF_template_prefix_tags.bin','GAW28_RF_template_retention_tags.bin'),
            ('actual_fifth',D27/'GAW27_fifth_native_pulse_events01.bin','GAW28_actual_fifth_retention_issue01.json','GAW28_actual_fifth_prefix_tags.bin','GAW28_actual_fifth_retention_tags.bin')):
            p=tmp/(tag+'_prefix');h=tmp/(tag+'_history');z=json.loads(run([exe,events,p,h]))
            assert z==load(D/raw) and z['passed']
            assert z['prefix_Info_zero_tag_intervals']==[] and z['prefix_GF_wipe_holder_locations']==0
            assert z['pulse_GF_wipe_holder_locations']==49152 and z['all_final_tags_coherent0_or31']
            assert sha(p)==sha(D/pre) and sha(h)==sha(D/hist)
            # This is a stale printf field in the reused engine, not a
            # current-history premise. Exact events above identify inputs.
            assert z['same_actual_GAW26_fourth_native_event_history'] is True
    argv=sys.argv
    try:
        sys.argv=[str(S/'check_gaw28_symbolic_partial_heads.py')];partial.main()
        sys.argv=[str(S/'check_gaw28_writeback_contracts.py')];c=contracts.main()
        sys.argv=[str(S/'check_gaw28_actual_command_renewal.py')];z=commands.main()
    finally:sys.argv=argv
    p=load(D/'GAW28_symbolic_partial_heads_certificate.json')
    assert len(p['actual_partial_late_head_pairs_on_RF_renewal_before_first_Flag2'])==22
    assert p['universal_arbitrary_other_SF_words_by_taint_noninterference']
    assert all(q['both_ERROR_before_complete_data_updates_read'] and q['all_ten_special_source_History1_fields_remain_zero'] for q in p['actual_partial_late_head_pairs_on_RF_renewal_before_first_Flag2'])
    assert len(c['exact_emitted_Out_target_contracts'])==217
    assert c['actual_local_R_zero_History1_source_field_cofactors']==66 and c['canonical_zero_tail_Flag1_native_cofactors']==1664
    assert len(z['full_actual_native_bank_renewal_and_commands'])==12
    assert sum(len(v['actual_native_early_executions']) for v in z['full_actual_native_bank_renewal_and_commands'])==7980
    assert z['all_ten_History1_source_fields_initially_zero_in_actual4U_on15360_primaries']
    assert z['actual_native_GF_boundary_intervals_4U_through15U']==[[((3*n+13)*2+1)*4096,(3*n+17)*8192] for n in range(4,16)]
    birth=z['actual_Flag2_birth'];assert birth['derived_first_positive_native_Flag2_row']==16515073
    assert len(birth['positive_native_Flag2_sites_at_that_row'])==72 and birth['literal_local_R_WF_source_and_next_native_birth_cofactors']==342
    assert z['infinite_RF_only_persistence_extrapolation_for_this_history_invalidated']
    assert z['full_raw5U_to15U_boundaries_late16U_GF_erosion_or_eventual_repair_proved'] is False
    assert z['faithful_Gray_Gacs_higher_error_iid_or_shorterU_claim'] is False
    assets(m);assets(old)
    for p,h in m['unchanged_registered_and_active_sha256'].items():assert sha(ROOT/p)==h
    result=dict(passed=True,assets_verified=len(m['assets_sha256']),inherited_assets_verified=739,
        inherited_GAW27_all_hashes_manifest_and_both_accepted_terminal_logs_checked=True,
        all_NEW_math_recomputed=True,inherited_math_recomputed='--full-inherited' in sys.argv,
        Q=k.Q,U=k.U,error_lambda=24,error_separation=104,
        unchanged_frozen_local_R_own_ROM_dictionary_and_exact_rebuilt_retention_engine=True,
        same_original_intact_H_row1_GF_only139264site_real2_no_later_errors=True,
        actual_native_record_and_zero_special_Info_projection_through15U=True,
        actual_RF_only_command_supply_periods5_through15=True,
        actual_Flag2_command_birth_period16_true40_to48=True,
        actual_first_native_Flag2_row=16515073,
        zero_old_Flag2_noquorum_computed_Age16_source3_exact_emitted_birth=True,
        arbitrary_other_SF_writeback_universal_taint_partial_and_complete_typed_store_contracts=True,
        ten_source_History1_word_zero_induction_and_actual_raw_U_commit_reset=True,
        finite_Address_union_through15U=[0,507904],original_real2_P5_sized_allowance_still_fits=True,
        full_raw_SF_5U_to15U_late16U_or_eventual_GF_repair_proved=False,
        faithful_Gray_Gacs_higher_error_iid_memory_or_shorterU_claim=False,
        registered_main_actual_rule_or_constants_modified=False,
        proof_sha256=sha(S/'GAW28_ACTUAL_NATIVE_BANK_RENEWAL_AND_FIRST_FLAG2.md'),
        manifest_sha256=sha(mp),symbolic_partial_receipt_sha256=sha(D/'GAW28_symbolic_partial_heads_certificate.json'),
        writeback_contract_receipt_sha256=sha(D/'GAW28_writeback_contracts_certificate.json'),
        actual_command_renewal_receipt_sha256=sha(D/'GAW28_actual_command_renewal_certificate.json'),
        elapsed_seconds=time.monotonic()-start)
    print(json.dumps(result),flush=True);return result
if __name__=='__main__':main()
