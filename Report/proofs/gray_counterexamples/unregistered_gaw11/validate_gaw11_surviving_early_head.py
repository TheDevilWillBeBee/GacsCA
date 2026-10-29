"""Read-only actual-head/reset replay and exact frozen-rule provenance."""
from pathlib import Path
from dataclasses import asdict
import hashlib,importlib.util,json,subprocess,sys,tempfile,time
ROOT=Path(__file__).resolve().parents[4];S=Path(__file__).resolve().parent
D=ROOT/'figs/gray_counterexamples/unregistered_gaw11'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    start=time.monotonic();manifest_path=D/'GAW11_standalone_assets.json'
    assets=json.loads(manifest_path.read_text())['assets_sha256']
    for name,h in assets.items():assert sha(ROOT/name)==h,('asset mismatch',name)
    cert=json.loads((D/'GAW11_surviving_early_head_certificate.json').read_text())
    assert cert['proof_sha256']==sha(S/'GAW11_SURVIVING_EARLY_HEAD.md')
    assert cert['receipt_sha256']==sha(D/'GAW11_surviving_early_head_receipt.json')
    assert (cert['Q'],cert['U'],cert['error_lambda'],cert['error_separation'])==(8192,1048576,24,104)
    for key in ('actual_recursively_intact_H','same_chronological_physical_error_history',
        'actual_original_c104_real1','actual_full_SF_prefix_replayed','derived_actual_WF_zero_with_head_present',
        'actual_two_label_native_event_partition_proved','all_head_holder_rest_clocks_protected',
        'surviving_extra_head_stationary_until_real_reset','all_three_actual_banks_Info_Programme_preserved',
        'global_complete_shadow_from102Q_and_all_later','actual_reset_and_next_birth_checked'):
        assert cert[key],key
    for key in ('arbitrary_native_control_real1_repair','all24_campaign_cases_replayed_through_recovery',
        'whole_grid_U_simulation_claimed','Gray_or_G17_refutation','iid_reliability_or_failure',
        'shorter_U_proved','new_rule_created','active_rule_modified','registered_main_modified'):
        assert not cert[key],key
    batch=(S/'gaw11_native_batch.c').read_text()
    event=(S/'gaw11_clock_head_observer.c').read_text()
    assert '#include "../unregistered_gaw9/gaw9_native_info.c"' in batch
    assert '#include "../unregistered_gaw7/gaw7_clock_events.c"' in event
    assert 'b[x]=native(&v,x)' in batch
    assert 'events+=step(&a,&next);a=next;t++' in event
    with tempfile.TemporaryDirectory(prefix='gaw11_readonly_') as td:
        for source,name,shared in (('gaw11_native_batch.c','gaw11_native_batch.so',True),
                                   ('gaw11_clock_head_observer.c','gaw11_clock_head_observer',False)):
            output=Path(td)/name
            command=['gcc','-O3','-std=c11','-Wall','-Wextra']+(['-shared','-fPIC'] if shared else [])
            subprocess.run(command+[str(S/source),'-o',str(output)],check=True)
            assert sha(output)==sha(D/name),('diagnostic binary identity',name)
    previous_path=ROOT/'Report/proofs/gray_counterexamples/unregistered_gaw2/validate_gaw2_period_v2.py'
    sys.path.insert(0,str(previous_path.parent));spec=importlib.util.spec_from_file_location('gaw2_for_gaw11',previous_path)
    previous=importlib.util.module_from_spec(spec);spec.loader.exec_module(previous);previous.main()
    sys.path.insert(0,str(S));import check_gaw11_surviving_early_head as checker
    rom=json.loads((ROOT/'figs/gray_counterexamples/unregistered_gaw2/GAW2R_rom.json').read_text())
    rom['dictionary']=[int(v,0) if isinstance(v,str) else v for v in rom['dictionary']]
    assert json.loads(json.dumps(asdict(checker.own.ROM)))==rom,'actual whole-rule own ROM mismatch'
    result=checker.main(write=False)
    assert len(result['cases'])==2
    for i,c in enumerate(result['cases']):
        assert c['actual_original_c104_classification']['level0']==0
        assert c['actual_original_c104_classification']['level1']
        n=c['actual_native_event_certificate']
        assert n['clock_recovery_tick']==(1450,1453)[i]
        assert n['native_quiet_tick']==(5545,5548)[i]
        assert n['last_wrong_head_holder_clock_tick']==(2,5)[i]
        assert [h['pc'] for h in c['held_head_at128']]==[(3595,3597)[i]]*5
        assert c['exact_full_shadow_from102Q_onward'] and not c['first_U_decoded_bad_receivers']
        assert c['actual_reset_shadow_composition']['actual_derived_reset_birth_full_local_R_checks']==dict(reset=1598,birth=1598)
    for name,h in assets.items():assert sha(ROOT/name)==h,('read-only replay changed asset',name)
    print(json.dumps(dict(passed=True,assets_verified=len(assets),actual_rule_ROM_equal=True,
        exact_selected_intact_start_histories_replayed=2,native_clock_recovery_ticks=[1450,1453],
        native_flag_quiet_ticks=[5545,5548],last_wrong_head_holder_clocks=[2,5],
        extra_Heads_held_pcs=[3595,3597],full_shadow_from102Q_and_all_later=True,
        native_scalar_checks=result['native_batch_checks']['actual_scalar_native_checks'],
        full_kernel_cache_checks=result['full_kernel_cache_checks']['full_raw_local_R_cache_comparisons'],
        ordinary_unbatched_actual_prefix_checks=sum(c['direct_unbatched_birth_source_checks'] for c in result['cases']),
        actual_reset_birth_checks_per_case=dict(reset=1598,birth=1598),
        general_repair_Gray_iid_or_shorter_U=False,checkpoint_sha256=sha(manifest_path),
        elapsed_seconds=time.monotonic()-start)),flush=True)

if __name__=='__main__':main()
