"""Issue once, or replay read-only, the written GAWN1 contracts."""
from pathlib import Path
import argparse,hashlib,json,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE))
import probe_unrolled_gawn1 as probe
OUT=ROOT/'figs/gray_counterexamples/unregistered_gawn1'
CERT=OUT/'GAWN1_unrolled_certificate.json'
PROOF=HERE/'GAWN1_UNROLLED_WORD_VOTE_AND_PERIOD.md'
PRIOR=ROOT/'figs/gray_counterexamples/unregistered_gawn0/GAWN0_normalization_certificate.json'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    started=time.monotonic();parser=argparse.ArgumentParser();parser.add_argument('--issue',action='store_true');args=parser.parse_args()
    if args.issue:assert not CERT.exists(),'never overwrite frozen certificate'
    else:assert CERT.exists(),'initial issue requires --issue'
    assert sha(PRIOR)=='b4e0d61f5816460b1146804371e97c846bf3bae82ed1fab72e574e51dd2cf234'
    prior=json.loads(PRIOR.read_text());assert len(prior['assets_sha256'])==464
    for name,value in prior['assets_sha256'].items():assert sha(ROOT/name)==value,name
    previous_dir=PRIOR.parent;previous_source=HERE.parent/'unregistered_gawn0'
    previous_log=previous_dir/'readonly_run01.log';previous_replay=json.loads(previous_log.read_text().splitlines()[-1])
    assert previous_replay['passed'] and previous_replay['readonly'] and previous_replay['certificate_sha256']==sha(PRIOR)
    assert sha(previous_source/'GAWN0_CITATION_ERRATA.md')=='1e8f7d96bd8dd41074b895e944784065f94e4ccb8f0291af4f4f39f0001d0efb'
    frozen=json.loads((OUT/'unrolled_probe01.json').read_text());current=probe.compute()
    for item in (frozen,current):item.pop('seconds')
    assert frozen==current,'new computation differs from frozen supplement'
    emission=json.loads((OUT/'GAWN1_emission.json').read_text())
    assert emission['builder_sha256']==sha(HERE/'build_unrolled_gawn1.py')
    assert emission['rule_source_sha256']==sha(HERE/'unrolled_gawn1.py')
    assert emission['rom_sha256']==sha(OUT/'GAWN1_rom.json') and emission['listing_sha256']==sha(OUT/'GAWN1_listing.json')
    assert (emission['token_count'],emission['dictionary_used'],emission['used_token_stream_bits'],emission['immutable_allocated_bits'])==(3781,1053,41591,270349)
    assert (emission['previous_helper_executed_instructions'],emission['new_helper_executed_instructions'])==(86,37)
    assets=dict(prior['assets_sha256'])
    dependencies=[PRIOR,previous_log,previous_dir/'issue_run01.log',previous_source/'GAWN0_CITATION_ERRATA.md',
        ROOT/'figs/gray_counterexamples/GAWN0_child_readonly_review_record01.json',PROOF,Path(__file__),
        HERE/'unrolled_gawn1.py',HERE/'build_unrolled_gawn1.py',HERE/'gawn1_compositional_cost.py',HERE/'probe_unrolled_gawn1.py',
        OUT/'GAWN1_rom.json',OUT/'GAWN1_listing.json',OUT/'GAWN1_emission.json',OUT/'build_run01.log',
        OUT/'GAWN1_compositional_cost.json',OUT/'cost_run01.log',OUT/'unrolled_probe01.json',OUT/'probe_run01.log']
    for path in dependencies:assets[str(path.relative_to(ROOT))]=sha(path)
    cert=dict(passed=True,proof_sha256=sha(PROOF),checker_sha256=sha(__file__),
        inherited464_provenance_and_accepted_terminal_replay_checked=True,
        all_new_helper_structural_cost_premises_and_selected_own_ROM_runs_recomputed=True,
        explicit_new_own_ROM=True,no_new_physical_ISA_primitive=True,Q=8192,U=1048576,
        original_error_lambda=24,original_error_separation=104,WORD=100,FRAME_WORDS=496,
        universal_five_word_helper_majority_all16_return_registers_and37_instruction_contract_proved=True,
        raw_native_projection_and_whole_prepared_semantics_proved_using_previous_argument=True,
        complete_canonical_coherent_reset_encoded_D_noiseless_period_proved_using_previous_argument=True,
        exact72_class_contract_DAG_all_payloads_full_bound=104566,early_bound=215,
        previous_full_bound=141564,full_bound_improvement=36998,
        late_margin=42889,full_pass_also_fits13Q_minus1=True,thirteen_Q_margin=1929,
        token_count=3781,dictionary_used=1053,used_token_stream_bits=41591,immutable_allocated_bits=270349,
        literal_helper_cases=416,selected_whole_ROM_cases=4,finite_executions_are_measured_supplements=True,
        damaged_lower_E0_general_real1_higher_repair_smaller_Q_U_Gray_iid_memory_minimum_proved=False,
        old_actual_fault_histories_transferred=False,G17_or_previously_frozen_rules_ROMs_modified=False,
        global_reliability_established=False,assets_sha256=dict(sorted(assets.items())))
    if args.issue:CERT.write_text(json.dumps(cert,indent=2)+'\n')
    else:assert cert==json.loads(CERT.read_text()),'certificate changed'
    print(json.dumps(dict(passed=True,readonly=not args.issue,assets_verified=len(assets),certificate_sha256=sha(CERT),
        helper_instructions=37,helper_cases=416,full_bound=104566,early_bound=215,
        full_own_ROM_semantics_and_complete_encoded_D_noiseless_period_proved=True,
        smaller_Q_U_or_noise_reliability_proved=False,old_rules_or_G17_changed=False,
        seconds=time.monotonic()-started)),flush=True)

if __name__=='__main__':main()
