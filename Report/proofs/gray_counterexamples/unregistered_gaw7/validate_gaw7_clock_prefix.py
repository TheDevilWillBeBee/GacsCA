"""Read-only provenance, simulator identity and exact event replay for GAW7."""
from pathlib import Path
from dataclasses import asdict
import hashlib,importlib.util,json,subprocess,sys,tempfile,time
ROOT=Path(__file__).resolve().parents[4];S=Path(__file__).resolve().parent
D=ROOT/'figs/gray_counterexamples/unregistered_gaw7'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    start=time.monotonic();p=D/'GAW7_standalone_assets.json';m=json.loads(p.read_text())
    assets=m['assets_sha256']
    for name,h in assets.items():assert sha(ROOT/name)==h,('asset mismatch',name)
    c=json.loads((D/'GAW7_clock_prefix_certificate.json').read_text())
    assert c['proof_sha256']==sha(S/'GAW7_UNIFORM_CLOCK_PREFIX.md')
    assert c['receipt_sha256']==sha(D/'GAW7_clock_prefix_receipt.json')
    assert (c['Q'],c['U'],c['error_lambda'],c['error_separation'])==(8192,1048576,24,104)
    for key in ('intact_H_actual96Q_same_fault','arbitrary_uniform_replacement_Age_proved',
        'canonical_GF_all_raw_clock_closure_proved','actual_source_cone_proved',
        'actual_WF_zero_derived','universal_binary_native_factor_proved',
        'all_Q_phases_exact_event_replay','native_recovery_before97Q_proved',
        'fixed_two_adjacent_colonies_entire_native_trajectory_proved',
        'native_correct_through_first_U_boundary_proved'):
        assert c[key],key
    for key in ('arbitrary_mixed_Age_or_control_recovery_proved','actual_late_History_or_output_map_proved',
        'Gray_or_G17_refutation_proved','iid_memory_failure_proved','shorter_U_proved',
        'new_rule_created','active_rule_modified','registered_main_modified'):
        assert not c[key],key
    # Rebuild exactly the source used for the finite update certificate;
    # compare both binary identities and the complete deterministic table.
    with tempfile.TemporaryDirectory(prefix='gaw7_readonly_') as td:
        t=Path(td);binary=t/'gaw7_clock_events';library=t/'gaw7_clock_events.so'
        flags=['gcc','-O3','-std=c11','-Wall','-Wextra']
        subprocess.run(flags+[str(S/'gaw7_clock_events.c'),'-o',str(binary)],check=True)
        subprocess.run(flags+['-shared','-fPIC',str(S/'gaw7_clock_events.c'),'-o',str(library)],check=True)
        assert sha(binary)==sha(D/'gaw7_clock_events'),'event executable identity'
        assert sha(library)==sha(D/'gaw7_clock_events.so'),'cofactor library identity'
        result=subprocess.run([str(binary),'0','8191','16','32768'],capture_output=True,check=True)
        assert result.stdout==(D/'clock_uniform_width16.csv').read_bytes(),'event trajectory table differs'
        assert result.stderr==(D/'clock_uniform_width16.log').read_bytes(),'event summary differs'
        print(json.dumps(dict(all8192_event_trajectories_replayed=True,
            event_checks=1064790382,event_binary_identity=True,
            elapsed_seconds=time.monotonic()-start)),flush=True)
    # The frozen all-raw own-programme/native/courier proof dependencies
    # are unchanged. Replay their existing compact contract validator;
    # unrelated old native-error campaigns need not be recomputed.
    old=ROOT/'Report/proofs/gray_counterexamples/unregistered_gaw2/validate_gaw2_period_v2.py'
    sys.path.insert(0,str(old.parent));spec=importlib.util.spec_from_file_location('gaw2_for_gaw7',old)
    previous=importlib.util.module_from_spec(spec);spec.loader.exec_module(previous);previous.main()
    import check_gaw7_clock_prefix as checker
    rom=json.loads((ROOT/'figs/gray_counterexamples/unregistered_gaw2/GAW2R_rom.json').read_text())
    rom['dictionary']=[int(v,0) if isinstance(v,str) else v for v in rom['dictionary']]
    assert json.loads(json.dumps(asdict(checker.own.ROM)))==rom,'actual rule ROM mismatch'
    result=checker.main(write=False)
    assert result['native_factor']['exhaustive_actual_scalar_checks']==720896
    assert result['source_cone_cofactors']['actual_total_local_R_checks']==480
    assert len(result['selected_actual_faults']['cases'])==64
    for name,h in assets.items():assert sha(ROOT/name)==h,('read-only replay changed asset',name)
    print(json.dumps(dict(passed=True,assets_verified=len(assets),actual_rule_ROM_equal=True,
        universal_uniform_Age_native_prefix=True,maximum_clock_recovery=2736,maximum_native_quiet=6831,
        arbitrary_mixed_Age_or_full_period_proved=False,Gray_iid_or_shorter_U=False,
        checkpoint_sha256=sha(p),elapsed_seconds=time.monotonic()-start)),flush=True)

if __name__=='__main__':main()
