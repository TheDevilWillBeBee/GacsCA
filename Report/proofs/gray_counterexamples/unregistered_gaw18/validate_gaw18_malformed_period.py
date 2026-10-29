"""Read-only replay of selected unmasked actual GAW17 second period.

All inherited assets are hashed; old histories are not silently projected
or recomputed with changed definitions. New physical claims are replayed.
"""
from pathlib import Path
import hashlib,json,sys,time
S=Path(__file__).resolve().parent;ROOT=S.parents[3]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw18'
sys.path.insert(0,str(S))
import check_gaw18_malformed_period as m

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def assets(v):
    for p,h in v['assets_sha256'].items():assert sha(ROOT/p)==h,(p,'frozen asset differs')

def retained_projection(old,new,path=''):
    """Every initial exploratory value is unchanged; only new audit metadata.

    Explicit key additions are limited to bank/coupling/raw-comparison
    certificates. This does not mutate or retrofit an earlier receipt.
    """
    if isinstance(old,dict):
        assert isinstance(new,dict)
        extra=set(new)-set(old)
        assert extra<=set(('actual_gather_bank_sha256','actual_full_local_R_execution_checks',
            'actual_mode_movement_coverage','actual_control_contract','actual_2U_commit_contract',
            'selected_unmasked_raw_comparison','selected_malformed_physical_period_composed',
            'complete2U_and_all_later_no_error_shadow')),(path,'unexpected added audit keys',extra)
        for key,value in old.items():assert key in new;retained_projection(value,new[key],path+'/'+key)
    elif isinstance(old,list):
        assert isinstance(new,list) and len(old)==len(new),(path,'list differs')
        for i,(a,b) in enumerate(zip(old,new)):retained_projection(a,b,path+'/'+str(i))
    else:assert old==new,(path,'retained initial value differs')

def main():
    started=time.monotonic();mp=D/'GAW18_standalone_assets.json';manifest=load(mp);assets(manifest)
    ancestor=ROOT/manifest['inherited_manifest'];prior=load(ancestor);assets(prior)
    assert manifest['inherited_assets']==len(prior['assets_sha256'])==472
    assert all(manifest['assets_sha256'][p]==h for p,h in prior['assets_sha256'].items())
    assert manifest['assets_sha256'][str(ancestor.relative_to(ROOT))]==sha(ancestor)
    oldlog=ROOT/'figs/gray_counterexamples/unregistered_gaw17/GAW17_readonly_replay01.log'
    finished=load_log(oldlog)
    assert finished['passed'] and finished['assets_verified']==472
    assert finished['manifest_sha256']==sha(ancestor)
    assert not finished['illegal_case_decoder_2U_eventual_repair_or_memory_failure_proved']
    assert (m.k.Q,m.k.U,m.k.WORD,m.P,m.k.FRAME_WORDS)==(8192,1048576,100,3848,496)
    rom=load(ROOT/'figs/gray_counterexamples/unregistered_gaw2/GAW2R_rom.json')
    assert list(m.own.ROM.bits)==rom['bits'] and [hex(v) for v in m.own.ROM.dictionary]==rom['dictionary']
    for name in ('token_count','used_dictionary','token_bits','early_pc'):assert getattr(m.own.ROM,name)==rom[name]
    print(json.dumps(dict(stage='frozen_ancestor_rule_ROM_and_historical_null_verified',assets=len(manifest['assets_sha256']))),flush=True)
    actual=m.physical_run();issued=load(D/'GAW18_malformed_period_certificate02.json')
    assert actual==issued,'new actual physical-period replay differs'
    discovery=load(D/'GAW18_selected_execution_discovery02.json')
    retained_projection(discovery,actual)
    retained_projection(load(D/'GAW18_selected_execution_discovery.json'),discovery)
    retained_projection(load(D/'GAW18_malformed_period_certificate.json'),actual)
    assert load(D/'initial01/GAW18_selected_execution_discovery.json')==load(D/'GAW18_selected_execution_discovery.json')
    assert load(D/'initial01/GAW18_malformed_period_certificate.json')==load(D/'GAW18_malformed_period_certificate.json')
    assert sha(D/'initial01/physical_certificate01.log')==sha(D/'physical_certificate01.log')
    controls=actual['actual_control_contract'];commit=actual['actual_2U_commit_contract']
    checks=sum(c['early']['actual_full_local_R_execution_checks']+c['late']['actual_full_local_R_execution_checks'] for c in actual['cases'])
    for c in actual['cases']:
        assert c['early']['actual_gather_bank_sha256']==c['late']['actual_gather_bank_sha256']
        assert c['early']['updates']==150 and c['late']['updates']==65062
        assert c['early']['HALT'] and c['late']['HALT']
        assert c['early']['courier_seed_low_bits']==[0,0]
        assert not c['late']['literal_raw_helper_mismatched_indices'] and not c['late']['shadow_mismatched_indices']
        assert not c['late']['illegal_native_output_words']
    assets(manifest);assets(prior)
    final=dict(passed=True,assets_verified=len(manifest['assets_sha256']),inherited_assets_verified=472,
        exact_frozen_local_R_and_emitted_ROM=True,actual_recursive_intact_H_original_real1_history_unchanged=True,
        actual_unmasked_U_record_retained_without_legal_projection=True,
        actual_bad_normal_word_indices=list(range(1,220)),actual_illegal_native_word_indices=[1,2,3,4,5],
        affected_physical_colonies=list(range(-8,9)),actual_derived_three_gathers_and_temporal_vote=True,
        actual_early_executions_and_zero_couriers_and_WF=True,
        selected_early_updates=150,selected_late_updates=65062,
        actual_full_local_R_execution_checks=checks,actual_full_local_R_control_checks=controls['actual_full_local_R_control_checks'],
        actual_full_local_R_2U_commit_checks=commit['actual_2U_full_local_R_commit_reset_checks'],
        complete_actual_physical2U_and_all_later_shadow=True,
        selected_emitter_raw_helper_and_shadow_equal=True,
        universal_malformed_native_emitter_refinement=False,padding_projection_or_legal_upper_theorem_on_W=False,
        general_real1_higher_Gray_iid_or_shorterU_claim=False,
        main_registered_sources_or_active_G17_changed=False,
        manifest_sha256=sha(mp),physical_receipt_sha256=sha(D/'GAW18_malformed_period_certificate02.json'),
        elapsed_seconds=time.monotonic()-started)
    print(json.dumps(final),flush=True);return final

def load_log(p):return json.loads(Path(p).read_text().splitlines()[-1])

if __name__=='__main__':main()
