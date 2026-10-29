"""Read-only replay of the two actual intact GAW5 real1 repair instances."""
from pathlib import Path
from dataclasses import asdict
import sys,json,hashlib,time,importlib.util
ROOT=Path(__file__).resolve().parents[4]
S=Path(__file__).resolve().parent
D=ROOT/'figs/gray_counterexamples/unregistered_gaw5'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    start=time.monotonic();path=D/'GAW5_standalone_assets.json'
    manifest=json.loads(path.read_text());assets=manifest['assets_sha256']
    for p,h in assets.items():assert sha(ROOT/p)==h,('source/receipt mismatch',p)
    c=json.loads((D/'GAW5_history_bursts_certificate.json').read_text())
    assert c['proof_sha256']==sha(S/'GAW5_HISTORY_BURSTS.md')
    assert (c['Q'],c['U'],c['error_lambda'],c['error_separation'])==(8192,1048576,24,104)
    for name in ('intact_initializer_every_level_proved','actual_Programme_choices_proved',
        'one_original_real1_no_E0_per_case','actual_first_prefix_and_held_banks_derived',
        'first_raw_record_difference_only_colony0','first_padding_case_outside_narrow_legal_upper_E',
        'actual_second_banks_derived_from_same_history','all34_affected_early_flags_zero',
        'complete_actual_second_boundary_shadow_recovery_proved','ordinary_sacrificed_upper_error_relation_satisfied'):
        assert c[name],name
    for name in ('all_native_control_bursts_recovery_proved','operational_reliability_failure',
        'independent_preloaded_history_assumed','complete_physical_period_direct_simulation_claimed',
        'Gray_construction_refuted','iid_memory_failure_proved','shorter_U_proved',
        'new_rule_created','active_rule_modified','registered_main_modified'):
        assert not c[name],name
    previous=ROOT/'Report/proofs/gray_counterexamples/unregistered_gaw2/validate_gaw2_period_v2.py'
    sys.path.insert(0,str(previous.parent))
    spec=importlib.util.spec_from_file_location('frozen_gaw2_for_gaw5',previous)
    replay=importlib.util.module_from_spec(spec);spec.loader.exec_module(replay);replay.main()
    import check_gaw5_history_burst as checker
    rom=json.loads((ROOT/'figs/gray_counterexamples/unregistered_gaw2/GAW2R_rom.json').read_text())
    rom['dictionary']=[int(v,0) if isinstance(v,str) else v for v in rom['dictionary']]
    assert json.loads(json.dumps(asdict(checker.own.ROM)))==rom
    receipt=checker.main(write=False);cases=receipt['cases']
    assert [x['case'] for x in cases]==['shift1','padding99']
    assert [x['first_actual_execution']['updates'] for x in cases]==[66185,65117]
    assert [x['first_native_output'] for x in cases]==[
        ['0x1','0x1','0x0','0x0','0x0','0x0'],
        ['0x8000000000000000000000000','0x1','0x1','0x0','0x0','0x0']]
    for x in cases:
        assert x['actual_lower_error_support']==[(p,786432) for p in (3847,3848,3849)]
        assert x['classification']['level0']==0 and x['classification']['level1']
        assert x['classification']['sep']==104
        assert len(x['second_actual_receiver_executions'])==17
        assert x['second_boundary_complete_shadow_recovery']
        assert x['ordinary_sacrificed_upper_fault_permitted'] and not x['operational_reliability_failure']
    for p,h in assets.items():assert sha(ROOT/p)==h,('read-only replay mutated asset',p)
    print(json.dumps(dict(passed=True,assets_verified=len(assets),
        frozen_GAW2R_replayed=True,actual_simulator_emitted_ROM_equal=True,
        intact_start=True,original_real1_support=[(p,786432) for p in (3847,3848,3849)],
        complete_second_boundary_recovers=True,positive_permitted_error_map_instances=2,
        operational_Gray_iid_failure=False,registered_main_modified=False,
        checkpoint_sha256=sha(path),elapsed_seconds=time.monotonic()-start)))

if __name__=='__main__':main()
