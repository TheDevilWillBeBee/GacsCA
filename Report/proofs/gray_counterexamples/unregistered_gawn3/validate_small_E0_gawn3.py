"""Issue once/replay read-only the smaller frozen rule's pure-E0 checkpoint.

Universal whole-word/front/physical implications are in the written proof.
This checks frozen provenance and reruns the new exact finite premises.
"""
from pathlib import Path
import argparse,hashlib,json,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE))
import check_small_E0_gawn3 as reduced
OUT=ROOT/'figs/gray_counterexamples/unregistered_gawn3'
CERT=OUT/'GAWN3_pure_E0_certificate.json'
PRIOR=ROOT/'figs/gray_counterexamples/unregistered_gawn2/GAWN2_small_certificate.json'
PROOF=HERE/'GAWN3_SMALL_PURE_E0_PERIOD.md'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def stable(value):
    if isinstance(value,dict):return {str(k):stable(v) for k,v in value.items() if k!='elapsed_seconds'}
    if isinstance(value,(tuple,list)):return [stable(v) for v in value]
    return value

def source_derivative():
    old=HERE.parent/'unregistered_gaw3/check_gaw3_E0.py'
    assert sha(old)=='855726f3a9717c628c870c8dce2dd3978a9e65ddd56781534389f63fb6430be3'
    source=old.read_text()
    source=source.replace('GAW3: original-E0 geometry/fronts and an actual encoded WF wake.', 'GAWN3: pure-E0 reduction for the unchanged frozen half-scale GAWN2.')
    source=source.replace('Uses frozen GAW2R unchanged.', 'Uses frozen GAWN2 unchanged; a new proof checkpoint, no rule change.')
    source=source.replace("P=ROOT/'Report/proofs/gray_counterexamples/unregistered_gaw2'", "P=ROOT/'Report/proofs/gray_counterexamples/unregistered_gawn2'")
    source=source.replace('import gray_three_gather_gaw2r as k','import small_rule_gawn2 as k').replace('import gaw2r_compositional_cost as own','import small_compositional_cost as own')
    source=source.replace('unregistered_gaw3','unregistered_gawn3').replace('GAW3_E0_WF_witness.json','GAWN3_E0_WF_witness.json').replace('GAW3_E0_contracts.json','GAWN3_E0_contracts.json')
    source=source.replace('assert rows==4552','assert rows==2276').replace('quiet_before_R_birth=98*k.Q+2*rows<102*k.Q','quiet_before_new_reset=98*k.Q+2*rows<k.LATE_RESET')
    source=source.replace('result=k.predecessor.scalar_native(cells)','result=k.scalar_native(cells)')
    source=source.replace("native='actual inherited h1 scalar_native'", "native='actual new-Q/U h1 scalar_native'")
    source=source.replace('ticks<=213','ticks<=221')
    source=source.replace("only_changed_field='Address8189->8190'", "only_changed_field=f'Address{point}->{(point+1)%k.Q}'")
    source=source.replace('GAW2R actually encoded GF-only original-E0 WF discrepancy','GAWN2 actually encoded GF-only original-E0 WF discrepancy')
    source=source.replace('GAW3 pure-E0 actual GAW2R contracts','GAWN3 pure-E0 actual GAWN2 contracts')
    source=source.replace('old_GAW2R_rule_modified=False','frozen_GAWN2_rule_modified=False')
    source=source.replace('all legal native13/20/1-bit','all legal native12/19/1-bit')
    source=source.replace("if __name__=='__main__':main()", "if __name__=='__main__':\n    assert not (D/'GAWN3_E0_contracts.json').exists()\n    assert not (D/'GAWN3_E0_WF_witness.json').exists()\n    main()")
    assert source==Path(reduced.__file__).read_text(),'unlisted reduced-checker change'

def main():
    started=time.monotonic();parser=argparse.ArgumentParser();parser.add_argument('--issue',action='store_true');args=parser.parse_args()
    if args.issue:assert not CERT.exists(),'never overwrite frozen certificate'
    else:assert CERT.exists(),'initial issue requires --issue'
    assert sha(PRIOR)=='783abde52e2dbb52774f3e0de33285c53b15e16bfafcfd71a859f2c52ce2b489'
    prior=json.loads(PRIOR.read_text());assert len(prior['assets_sha256'])==508
    for name,value in prior['assets_sha256'].items():assert sha(ROOT/name)==value,name
    oldlog=PRIOR.parent/'readonly_run01.log';oldreplay=json.loads(oldlog.read_text().splitlines()[-1])
    assert oldreplay['passed'] and oldreplay['readonly'] and oldreplay['certificate_sha256']==sha(PRIOR)
    assert sha(oldlog)=='576b1ef019f7685662c2c3c861fb4b788a164d5ae78001bf236cc58b947d825d'
    source_derivative()
    result=reduced.main(write=False);frozen=json.loads((OUT/'GAWN3_E0_contracts.json').read_text())
    assert stable(result)==stable(frozen),'new exact premise replay differs'
    metric=result['metric'];front=result['fronts'];wake=result['actual_WF_wake']
    assert (metric['cone_pair_metric_checks'],metric['exhaustive_majority_bit_patterns'])==(561,714)
    assert (front['reduced_native_front_cases'],front['exhaustive_replacement_flag_payloads'])==(616,119746)
    assert metric['sweep_updates']==2276 and metric['quiet_row']==405960
    assert metric['quiet_before_new_reset'] and reduced.k.LATE_RESET==409600
    assert wake['error_support']==[[4093,393217]] and wake['WF_gap_sites']==list(range(4091,4096))
    assert wake['SF_wake_sites']==[4093] and wake['next_row_all_SF_and_WF_rejoin']
    assets=dict(prior['assets_sha256'])
    dependencies=[PRIOR,oldlog,PRIOR.parent/'issue_run02.log',PROOF,Path(__file__),Path(reduced.__file__),
        OUT/'GAWN3_E0_contracts.json',OUT/'GAWN3_E0_WF_witness.json',OUT/'reduction_run01.log']
    for path in dependencies:assets[str(path.relative_to(ROOT))]=sha(path)
    cert=dict(passed=True,proof_sha256=sha(PROOF),checker_sha256=sha(__file__),
        inherited508_asset_provenance_and_accepted_terminal_replay_checked=True,
        all_new_scale_native_front_metric_word_and_actual_WF_wake_premises_recomputed=True,
        frozen_GAWN2_same_rule_ROM_widths_schedule_and_constants_unchanged=True,
        Q=4096,U=524288,error_lambda=24,error_separation=104,physical_state_bits=49035,
        all_upper_raw_physical_bits_and_adaptive_full_cell_replacements_quantified=True,
        encoded_lower_start_required=True,upper_geometry_clock_or_SF_coherence_required=False,
        prepared_late_bank_or_external_source_command_assumed=False,
        current_previous_error_union_capacity_and_whole_word_vote_proved=True,
        computed_native_geometry_everywhere_correct_under_pure_E0=True,
        native_quiet_sweep_updates=2276,native_quiet_row=405960,quiet_to_late_reset_margin=3640,
        two_section_all13_physical_SF_invariant_proved=True,
        post96Q_global_physical_Mail_zero_proved=True,
        actual_continuing_E0_prepared_execution_coupling_proved=True,
        universal_actual_full_execution_bound=104572,early_bound=221,late_update_margin=6019,
        complete_pre_overwrite_boundary_exact_encoding_proved=True,
        raw_boundary_only_current_error_envelope_proved=True,
        five_holder_decoder_exact_and_all_time_pure_E0_iteration_proved=True,
        one_point_actual_WF_gap_and_one_site_SF_wake_proved=True,
        WF_equals_noiseless_shadow_during_pulse=False,
        cone_metric_pairs=561,one_bit_majority_cases=714,frontier_cases=616,flag_payload_cases=119746,
        finite_cofactors_are_premise_supplements_not_iid_reliability_experiments=True,
        general_real1_higher_error_Gray_iid_memory_minimum_proved=False,
        positive_iid_error_rate=None,global_reliability_established=False,
        G17_or_old_frozen_rules_ROMs_or_constants_modified=False,
        assets_sha256=dict(sorted(assets.items())))
    if args.issue:CERT.write_text(json.dumps(cert,indent=2)+'\n')
    else:assert cert==json.loads(CERT.read_text()),'certificate changed'
    for name,value in assets.items():assert sha(ROOT/name)==value,name
    print(json.dumps(dict(passed=True,readonly=not args.issue,assets_verified=len(assets),certificate_sha256=sha(CERT),
        Q=4096,U=524288,quiet_row=405960,all_time_pure_E0_same_rule_simulation_proved=True,
        actual_bank_and_packet_coupling_not_assumed=True,
        general_real1_higher_iid_memory_or_minimum_proved=False,
        rule_ROM_constants_or_G17_changed=False,seconds=time.monotonic()-started)),flush=True)

if __name__=='__main__':main()
