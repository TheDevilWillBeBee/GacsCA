"""Read-only provenance and exact execution replay of isolated GAW6."""
from pathlib import Path
from dataclasses import asdict
import sys,json,hashlib,time,importlib.util,tempfile,subprocess
ROOT=Path(__file__).resolve().parents[4];S=Path(__file__).resolve().parent
D=ROOT/'figs/gray_counterexamples/unregistered_gaw6'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    start=time.monotonic();path=D/'GAW6_standalone_assets.json'
    m=json.loads(path.read_text());assets=m['assets_sha256']
    for p,h in assets.items():assert sha(ROOT/p)==h,('asset mismatch',p)
    with tempfile.TemporaryDirectory(prefix='gaw6_source_identity_') as temporary:
        binary=Path(temporary)/'gaw6_native_info.so'
        subprocess.run(['gcc','-O3','-std=c11','-Wall','-Wextra','-shared','-fPIC',str(S/'gaw6_native_info.c'),'-o',str(binary)],check=True)
        assert sha(binary)==sha(D/'gaw6_native_info.so'),'rebuilt simulator binary differs'
    c=json.loads((D/'GAW6_native_control_certificate.json').read_text())
    assert c['proof_sha256']==sha(S/'GAW6_NATIVE_CONTROL_MAP.md')
    assert (c['Q'],c['U'],c['error_lambda'],c['error_separation'])==(8192,1048576,24,104)
    for key in ('universal_common_clock_held_factor_proved','actual_computed_primary_sources_retained',
        'radius8_infinite_line_support_lift_proved','intact_H_same_history',
        'twenty_original_real1_no_E0_cases','twenty_native_quiet_before102Q',
        'actual_retained_banks_and_birth_derived','first_boundary_at_most_one_bad_upper_cell',
        'complete2Ushadow_encoding','permitted_error_map_instances'):
        assert c[key],key
    for key in ('arbitrary_real1_native_recovery_proved','independent_preloaded_history_assumed',
        'physical_full_period_direct_simulation_claimed','operational_reliability_failure',
        'Gray_construction_refuted','iid_memory_failure_proved','shorter_U_proved',
        'new_rule_created','active_rule_modified','registered_main_modified'):
        assert not c[key],key
    previous=ROOT/'Report/proofs/gray_counterexamples/unregistered_gaw2/validate_gaw2_period_v2.py'
    sys.path.insert(0,str(previous.parent));spec=importlib.util.spec_from_file_location('frozen_gaw2_for_gaw6',previous)
    replay=importlib.util.module_from_spec(spec);spec.loader.exec_module(replay);replay.main()
    import check_gaw6_native_factor as factor
    import check_gaw6_adaptive as adaptive
    import search_gaw6_GF_bursts as search
    import check_gaw6_actual_bank_map as bank
    rom=json.loads((ROOT/'figs/gray_counterexamples/unregistered_gaw2/GAW2R_rom.json').read_text())
    rom['dictionary']=[int(v,0) if isinstance(v,str) else v for v in rom['dictionary']]
    assert json.loads(json.dumps(asdict(factor.own.ROM)))==rom
    factor.main(write=False);adaptive.main(write=False)
    old=json.loads((D/'GAW6_GF_burst_search.json').read_text())
    assert len(old['cases'])==20
    for case in old['cases']:
        current=search.campaign(case['start'],case['delta'],case['requested_steps'])
        a=dict(case);a.pop('elapsed_seconds');current.pop('elapsed_seconds')
        assert json.loads(json.dumps(current))==a
    result=bank.main(write=False)
    assert max(c['native_quiet_by_elapsed'] for c in result['cases'])==6831
    assert sum(len(c['actual_first_late_executions']) for c in result['cases'])==16
    for p,h in assets.items():assert sha(ROOT/p)==h,('read-only replay mutated asset',p)
    print(json.dumps(dict(passed=True,assets_verified=len(assets),factor_actual_rule_checks=15840,
        actual_GF_fault_cases=20,actual_late_executions=16,all_first_boundaries_one_upper_error_or_none=True,
        all_complete_second_boundaries_shadow=True,actual_simulator_ROM_equal=True,
        arbitrary_native_bursts_proved=False,Gray_iid_or_shorter_U=False,registered_main_modified=False,
        checkpoint_sha256=sha(path),elapsed_seconds=time.monotonic()-start)))

if __name__=='__main__':main()
