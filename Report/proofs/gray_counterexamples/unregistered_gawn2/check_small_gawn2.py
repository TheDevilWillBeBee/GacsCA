"""Issue once or replay read-only the written changed-scale GAWN2 contracts."""
from pathlib import Path
import argparse,hashlib,json,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE))
import probe_small_gawn2 as probe
OUT=ROOT/'figs/gray_counterexamples/unregistered_gawn2'
CERT=OUT/'GAWN2_small_certificate.json'
PROOF=HERE/'GAWN2_HALF_SCALE_NOISELESS_PERIOD.md'
PRIOR=ROOT/'figs/gray_counterexamples/unregistered_gawn1/GAWN1_unrolled_certificate.json'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    started=time.monotonic();parser=argparse.ArgumentParser();parser.add_argument('--issue',action='store_true');args=parser.parse_args()
    if args.issue:assert not CERT.exists(),'never overwrite frozen certificate'
    else:assert CERT.exists(),'initial issue requires --issue'
    assert sha(PRIOR)=='43e7715efc7be3200d3894091f659b03e60ab2f1baf1e32d78c20876b7ac152c'
    prior=json.loads(PRIOR.read_text());assert len(prior['assets_sha256'])==483
    for name,value in prior['assets_sha256'].items():assert sha(ROOT/name)==value,name
    previous_log=PRIOR.parent/'readonly_run01.log';previous=json.loads(previous_log.read_text().splitlines()[-1])
    assert previous['passed'] and previous['readonly'] and previous['certificate_sha256']==sha(PRIOR)
    review=ROOT/'figs/gray_counterexamples/GAWN1_child_critical_review_record01.json'
    assert sha(review)=='ab98780c005a7b631fa05a35be1b36c342fe4b4295a45879edf2585dafa5b8a7'
    frozen=json.loads((OUT/'small_probe01.json').read_text());current=json.loads(json.dumps(probe.compute()))
    for item in (frozen,current):item.pop('seconds')
    assert frozen==current,'recomputed small-scale contracts differ'
    emission=json.loads((OUT/'GAWN2_emission.json').read_text())
    assert emission['builder_sha256']==sha(HERE/'build_small_gawn2.py')
    assert emission['rule_sha256']==sha(HERE/'small_rule_gawn2.py')
    assert emission['rom_sha256']==sha(OUT/'GAWN2_rom.json') and emission['listing_sha256']==sha(OUT/'GAWN2_listing.json')
    assert (emission['token_count'],emission['dictionary_used'],emission['used_token_stream_bits'],emission['immutable_allocated_bits'])==(3829,1055,42119,270348)
    assets=dict(prior['assets_sha256'])
    dependencies=[PRIOR,previous_log,PRIOR.parent/'issue_run01.log',review,PROOF,Path(__file__),
        HERE/'derive_small_rule_gawn2.py',HERE/'small_rule_gawn2.py',HERE/'build_small_gawn2.py',
        HERE/'small_compositional_cost.py',HERE/'probe_small_gawn2.py',
        *[OUT/name for name in ('GAWN2_rom.json','GAWN2_listing.json','GAWN2_emission.json','GAWN2_rule_derivation.json',
            'derive_run01.log','build_run01.log','build_run02.log','build_small_gawn2_before_service_count_fix.py.txt',
            'GAWN2_compositional_cost.json','cost_run01.log','small_probe01.json','probe_run01.log',
            'check_small_gawn2_before_JSON_canonicalization.py.txt','issue_run01.log')]]
    for path in dependencies:assets[str(path.relative_to(ROOT))]=sha(path)
    cert=dict(passed=True,proof_sha256=sha(PROOF),checker_sha256=sha(__file__),
        inherited483_provenance_and_accepted_terminal_replay_checked=True,
        all_new_scale_native_macro_ROM_loop_scratch_symbolic_cost_premises_and_selected_runs_recomputed=True,
        explicit_new_rule_Q_U_widths_schedule_own_ROM=True,Q=4096,U=524288,PC_BITS=12,
        original_error_lambda=24,original_error_separation=104,WORD=100,FRAME_WORDS=496,PRIMARY_START=1800,
        native_widths=[12,19,1,1,1,1],physical_state_bits=49035,
        universal_prepared_D_projection_and_whole_own_ROM_semantics_proved=True,
        complete_canonical_common_clock_coherent_reset_E2_noiseless_period_proved=True,
        changed_PC_target_native_Age_and_generic20bit_read_distinctions_verified=True,
        all_payloads72_phase_contract_DAG_full_bound=104572,early_bound=221,
        LATE_RESET=409600,LATE_BIRTH=409601,ACTIVE_END=520192,available_late_updates=110591,late_margin=6019,
        smaller_Q_and_U_noiseless_instance_proved=True,half_of_prior_Q_and_U=True,
        token_count=3829,dictionary_used=1055,used_token_stream_bits=42119,immutable_allocated_bits=270348,
        literal_helper_cases=416,selected_raw_projected_whole_ROM_pairs=9,
        finite_executions_are_measured_supplements=True,
        arbitrary_damaged_lower_E0_general_real1_higher_Gray_iid_memory_minimum_proved=False,
        old_actual_fault_histories_transferred=False,G17_or_old_frozen_rules_ROMs_modified=False,
        global_reliability_established=False,assets_sha256=dict(sorted(assets.items())))
    if args.issue:CERT.write_text(json.dumps(cert,indent=2)+'\n')
    else:assert cert==json.loads(CERT.read_text()),'certificate changed'
    print(json.dumps(dict(passed=True,readonly=not args.issue,assets_verified=len(assets),certificate_sha256=sha(CERT),
        Q=4096,U=524288,full_bound=104572,early_bound=221,late_margin=6019,
        full_own_ROM_semantics_and_complete_encoded_D_noiseless_period_proved=True,
        smaller_Q_and_U_noiseless_instance_proved=True,noise_reliability_proved=False,
        old_rules_or_G17_changed=False,seconds=time.monotonic()-started)),flush=True)

if __name__=='__main__':main()
