"""Read-only provenance and universal prepared-family period replay."""
from pathlib import Path
import hashlib,json,time
import gaw19_symbolic_executor as symbolic
import check_gaw19_prepared_period02 as physical
S=Path(__file__).resolve().parent;ROOT=S.parents[3]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw19'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def assets(m):
    for p,h in m['assets_sha256'].items():assert sha(ROOT/p)==h,(p,'frozen provenance differs')

def main():
    started=time.monotonic();mp=D/'GAW19_standalone_assets02.json';manifest=load(mp);assets(manifest)
    inherited=load(ROOT/manifest['inherited_manifest']);assets(inherited)
    assert len(inherited['assets_sha256'])==manifest['inherited_assets']==492
    assert all(manifest['assets_sha256'][p]==h for p,h in inherited['assets_sha256'].items())
    assert (symbolic.k.Q,symbolic.k.U,symbolic.k.WORD,symbolic.P,symbolic.k.FRAME_WORDS)==(8192,1048576,100,3848,496)
    rom=load(ROOT/'figs/gray_counterexamples/unregistered_gaw2/GAW2R_rom.json')
    assert list(symbolic.own.ROM.bits)==rom['bits']
    assert [hex(v) for v in symbolic.own.ROM.dictionary]==rom['dictionary']
    for name in ('token_count','used_dictionary','token_bits','early_pc'):assert getattr(symbolic.own.ROM,name)==rom[name]
    failed1=(D/'GAW19_symbolic_discovery01.log').read_text()
    failed2=(D/'GAW19_physical_contracts01.log').read_text()
    assert 'unresolved symbolic control' in failed1 and "('LDX lane', 3581)" in failed1
    assert 'AssertionError' in failed2 and "['level1']" in failed2
    assert not load(D/'GAW19_failure_provenance.json')['CA_or_emitted_code_changed']
    print(json.dumps(dict(stage='frozen_rule_ancestry_ROM_and_failures_checked',assets=len(manifest['assets_sha256']))),flush=True)
    sr=symbolic.main();pr=physical.main()
    assert sr==load(D/'GAW19_symbolic_execution_certificate.json')
    assert pr==load(D/'GAW19_prepared_period_certificate.json')
    assert sr['quantified_bits']==pr['quantified_arbitrary_record_bits']==49600
    assert not pr['new_rule_native_projection_or_legal_upper_theorem_on_W']
    for case in sr['cases']:
        e,l=case['early'],case['late']
        assert e['updates']==150 and l['updates']==65062
        assert e['universal_HALT'] and l['universal_HALT']
        assert e['all496_output_words_known'] and l['all496_output_words_known']
        assert 3848<=l['min_head_address']<=l['max_head_address']<=4343
        assert l['unresolved_branch_pcs']==([108] if case['receiver']==0 else [])
        assert e['unresolved_branch_pcs']==([3702] if case['receiver']==0 else [])
        assert l['final_symbolic_states']==e['final_symbolic_states']==1
    actual=pr['additional_actual_intact_start_allM_error']
    assert actual['points']==len(actual['full_whole_cell_payloads'])==500
    assert actual['exact_original_c104_class']=='one actual real2; no actual E0/E1 points'
    assert actual['complete2U_and_all_later_shadow_follows_from_universal_prepared_period']
    assets(manifest);assets(inherited)
    r=dict(passed=True,assets_verified=len(manifest['assets_sha256']),inherited_assets_verified=492,
        exact_frozen_GAW2R_scalar_local_R_and_immutable_ROM=True,
        prepared_background='E(R(H),0) with receiver0 arbitrary496 raw Word100 words',
        universal_prepared_bits=49600,unprojected_native_padding_and_all_SF=True,
        universal_bit_cube_emitted_early150_late65062_HALT_and_output_identity=True,
        actual_global_three_gather_temporal_vote_zero_source_and_copy_commit_lift=True,
        complete_raw_prepared_boundary_at_nextU_and_all_later_shadow=True,
        actual_intact_H_allM500_site_row_is_one_original_c104_real2=True,
        actual_intact_allM_member_complete2U_and_all_later_shadow=True,
        arbitrary_prepared_family_real1_reachability=False,
        arbitrary_later_phase_background_or_malformed_native_emitter_refinement=False,
        Gray_faithfulness_iid_memory_higher_reliability_or_shorterU=False,
        active_G17_or_registered_main_sources_changed=False,
        manifest_sha256=sha(mp),symbolic_receipt_sha256=sha(D/'GAW19_symbolic_execution_certificate.json'),
        period_receipt_sha256=sha(D/'GAW19_prepared_period_certificate.json'),
        elapsed_seconds=time.monotonic()-started)
    print(json.dumps(r),flush=True);return r

if __name__=='__main__':main()
