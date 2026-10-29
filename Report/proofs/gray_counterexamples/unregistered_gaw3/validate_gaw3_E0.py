"""Read-only provenance and equation replay of the isolated GAW3 checkpoint.

The infinite-line/whole-word/period implications are the written proof;
this replays exact finite reductions and checks its unchanged GAW2R base.
"""
from pathlib import Path
from dataclasses import asdict
import sys,json,hashlib,time,importlib.util
ROOT=Path(__file__).resolve().parents[4]
S=Path(__file__).resolve().parent
D=ROOT/'figs/gray_counterexamples/unregistered_gaw3'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def stable(data):
    if isinstance(data,dict):return {str(k):stable(v) for k,v in data.items() if k!='elapsed_seconds'}
    if isinstance(data,(list,tuple)):return [stable(v) for v in data]
    return data


def main():
    start=time.monotonic();path=D/'GAW3_standalone_assets.json'
    manifest=json.loads(path.read_text());assets=manifest['assets_sha256']
    for p,h in assets.items():assert sha(ROOT/p)==h,('source/receipt mismatch',p)
    c=json.loads((D/'GAW3_pure_E0_period_certificate.json').read_text())
    assert c['proof_sha256']==sha(S/'GAW3_PURE_E0_PERIOD.md')
    assert (c['Q'],c['U'],c['error_lambda'],c['error_separation'])==(8192,1048576,24,104)
    assert c['all_upper_raw_bits_quantified']==49037
    assert c['actual_global_encoded_start_required'] and not c['prepared_bank_assumed']
    assert c['computed_boundary_exact_encoding'] and c['raw_boundary_current_error_envelope_only']
    assert c['majority_decoder_exact'] and c['two_section_SF_invariant_proved']
    assert c['continuing_pure_E0_period_proved'] and c['all_time_pure_E0_iteration_proved']
    assert c['native_quiet_row']==98*8192+9104==811920
    assert c['universal_actual_late_execution_bound']==141557<147455
    for name in ('full_Gray_refinement_proved','Gray_counterexample_proved','iid_reliability_proved',
                 'higher_error_recovery_proved','recursive_intact_witness_proved','own_beta_Q_bit_fit_proved',
                 'shorter_U_proved','active_rule_modified','frozen_GAW2R_rule_modified','registered_main_updated'):
        assert not c[name],name
    # Recheck the prior universal all-raw/noiseless component against its
    # exact previously frozen source and receipt inventory, without writes.
    previous=ROOT/'Report/proofs/gray_counterexamples/unregistered_gaw2/validate_gaw2_period_v2.py'
    sys.path.insert(0,str(previous.parent))
    spec=importlib.util.spec_from_file_location('previous_gaw2_checkpoint',previous)
    replay=importlib.util.module_from_spec(spec);spec.loader.exec_module(replay);replay.main()
    import check_gaw3_E0 as checker
    rom=json.loads((ROOT/'figs/gray_counterexamples/unregistered_gaw2/GAW2R_rom.json').read_text())
    rom['dictionary']=[int(v,0) if isinstance(v,str) else v for v in rom['dictionary']]
    assert json.loads(json.dumps(asdict(checker.own.ROM)))==rom, 'actual simulator/emitted ROM mismatch'
    result=checker.main(write=False)
    retained=json.loads((D/'GAW3_E0_contracts.json').read_text())
    assert stable(result)==stable(retained)
    assert result['fronts']['exhaustive_replacement_flag_payloads']==119746
    assert result['metric']['cone_pair_metric_checks']==561
    assert result['metric']['exhaustive_majority_bit_patterns']==714
    assert result['actual_WF_wake']['error_support']==[[8189,786433]]
    assert result['actual_WF_wake']['WF_gap_sites']==list(range(8187,8192))
    assert result['actual_WF_wake']['SF_wake_sites']==[8189]
    for p,h in assets.items():assert sha(ROOT/p)==h,('read-only replay mutated asset',p)
    print(json.dumps(dict(passed=True,assets_verified=len(assets),previous_GAW2R_replayed=True,
        actual_simulator_emitted_ROM_equal=True,original_E0_front_payloads=119746,
        continuing_pure_E0_theorem_scope='global encoded lower start; all raw upper cells; shared isolated history',
        raw_boundary='N_current_errors(E(F(C),0)); exact pre-overwrite layer',
        Gray_iid_higher_or_shorter_U=False,registered_main_modified=False,
        checkpoint_sha256=sha(path),elapsed_seconds=time.monotonic()-start)))

if __name__=='__main__':main()
