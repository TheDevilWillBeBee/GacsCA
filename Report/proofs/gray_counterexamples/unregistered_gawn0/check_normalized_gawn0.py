#!/usr/bin/env python3
"""Read-only provenance/new-premise replay for the written GAWN0 theorem."""
from pathlib import Path
import argparse,hashlib,json,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE))
import probe_normalized_gawn0 as probe
OUT=ROOT/'figs/gray_counterexamples/unregistered_gawn0'
PROOF=HERE/'GAWN0_NORMALIZED_NATIVE_EXECUTION_AND_PERIOD.md'
CERT=OUT/'GAWN0_normalization_certificate.json'
INHERITED=ROOT/'figs/gray_counterexamples/unregistered_gaw16/GAW16_standalone_assets.json'
OLD=ROOT/'figs/gray_counterexamples/unregistered_gaw_padding_quotient'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    start=time.monotonic();parser=argparse.ArgumentParser();parser.add_argument('--issue',action='store_true');args=parser.parse_args()
    if args.issue:assert not CERT.exists(),'never overwrite accepted certificate'
    else:assert CERT.exists(),'first issue requires explicit --issue'
    inherited=json.loads(INHERITED.read_text())
    assert len(inherited['assets_sha256'])==443
    for name,value in inherited['assets_sha256'].items():assert sha(ROOT/name)==value,name
    old_path=OLD/'padding_quotient_certificate.json';old=json.loads(old_path.read_text())
    assert old['passed'] and old['native_padding_projection_quotient_false']
    assert old['universal_malformed_native_emitter_refinement_false']
    assert not old['legal_native_record_evaluator_or_period_theorem_refuted']
    assert sha(INHERITED)==old['inherited_manifest_sha256']
    old_replay_path=OLD/'padding_quotient_readonly_run.log'
    replay=json.loads(old_replay_path.read_text().splitlines()[-1])
    assert replay['passed'] and replay['readonly'] and replay['certificate_sha256']==sha(old_path)
    contracts_path=ROOT/'figs/gray_counterexamples/unregistered_gaw2/GAW2R_contracts.json'
    cost_path=ROOT/'figs/gray_counterexamples/unregistered_gaw2/GAW2R_compositional_cost.json'
    contracts=json.loads(contracts_path.read_text());cost=json.loads(cost_path.read_text())
    assert contracts['structural_checks_pass'] and cost['maximum_ticks']==141557
    for name,value in contracts['sources_sha256'].items():assert sha(ROOT/name)==value,name
    frozen_path=OUT/'normalization_probe01.json';frozen=json.loads(frozen_path.read_text());new=probe.compute()
    for entry in (frozen,new):entry.pop('seconds')
    assert json.dumps(frozen,sort_keys=True)==json.dumps(new,sort_keys=True),'new replay differs from frozen supplement'
    emission_path=OUT/'GAWN0_emission.json';emission=json.loads(emission_path.read_text())
    assert emission['rom_sha256']==sha(OUT/'GAWN0_rom.json') and emission['listing_sha256']==sha(OUT/'GAWN0_listing.json')
    assert emission['builder_sha256']==sha(HERE/'build_normalized_gawn0.py')
    assert emission['rule_source_sha256']==sha(HERE/'normalized_gawn0.py')
    assert (emission['token_count'],emission['used_dictionary'],emission['used_token_stream_bits'],emission['immutable_allocated_bits'])==(3766,1050,41426,270349)
    assert emission['early_pc']==3616
    initial=OUT/'initial_build01'
    assert sha(initial/'GAWN0_rom.json')==sha(OUT/'GAWN0_rom.json')
    assert sha(initial/'GAWN0_listing.json')==sha(OUT/'GAWN0_listing.json')
    initial_emission=json.loads((initial/'GAWN0_emission.json').read_text())
    assert initial_emission['direct_emission_bits']==emission['uncompressed_instruction_bit_sum']==102760
    assert initial_emission['builder_sha256']==sha(initial/'build_normalized_gawn0_before_metadata_rename.py.txt')
    assets=dict(inherited['assets_sha256'])
    dependencies=[INHERITED,old_path,old_replay_path,OLD/'padding_quotient_issue_run.log',
        ROOT/'Report/proofs/gray_counterexamples/unregistered_gaw_padding_quotient/PADDING_QUOTIENT_OBSTRUCTION.md',
        ROOT/'Report/proofs/gray_counterexamples/unregistered_gaw_padding_quotient/check_padding_quotient.py',
        ROOT/'Report/proofs/gray_counterexamples/unregistered_gaw_padding_quotient/PADDING_CHANGES_FOR_CODING_AGENT.md',
        PROOF,Path(__file__),HERE/'normalized_gawn0.py',HERE/'build_normalized_gawn0.py',HERE/'probe_normalized_gawn0.py',
        OUT/'GAWN0_rom.json',OUT/'GAWN0_listing.json',emission_path,frozen_path,OUT/'probe_run01.log',
        initial/'GAWN0_rom.json',initial/'GAWN0_listing.json',initial/'GAWN0_emission.json',
        initial/'build_normalized_gawn0_before_metadata_rename.py.txt']
    for path in dependencies:assets[str(path.relative_to(ROOT))]=sha(path)
    cert=dict(passed=True,proof_sha256=sha(PROOF),checker_sha256=sha(__file__),
        inherited443_asset_provenance_and_accepted_old_obstruction_replay_checked=True,
        all_new_emission_static_premises_and_selected_executions_recomputed=True,
        explicit_new_own_ROM_instance_and_padded_extension=True,
        Q=8192,U=1048576,WORD=100,FRAME_WORDS=496,PRIMARY_START=3848,
        original_error_lambda=24,original_error_separation=104,
        local_projection_identity_proved=True,universal_prepared_raw_projected_relational_execution_proved=True,
        new_whole_local_semantics_proved_using_previous_compositional_argument=True,
        complete_physical_noiseless_period_on_coherent_reset_encoded_D_proved_using_previous_physical_argument=True,
        output_represented_native_words_legal_after_complete_period=True,
        native_padding_bits_not_added_to_physical_alphabet=True,
        no_SF_register_memory_or_Programme_word_projection=True,
        selected_finite_executions_measured_supplements=True,
        structural=new['structural'],full_pass_bound=141564,early_pass_bound=215,late_margin=5891,
        token_count=3766,dictionary_used=1050,used_token_stream_bits=41426,immutable_allocated_bits=270349,
        raw_encoded_start_assumes_canonical_lower_geometry_coherent_Info_and_reset_work=True,
        damaged_geometry_incoherent_holders_pure_E0_general_real1_or_higher_repair_proved=False,
        faithful_Gray_bit_layout_small_constants_iid_memory_positive_rate_or_minimum_fix_proved=False,
        old_physical_fault_histories_transferred_to_new_rule=False,
        G17_or_frozen_GAW2R_rule_ROM_or_constants_changed=False,global_reliability_established=False,
        assets_sha256=dict(sorted(assets.items())))
    if args.issue:CERT.write_text(json.dumps(cert,indent=2)+'\n')
    else:assert cert==json.loads(CERT.read_text()),'frozen certificate differs'
    print(json.dumps(dict(passed=True,readonly=not args.issue,assets_verified=len(assets),
        certificate_sha256=sha(CERT),explicit_new_own_ROM=True,native_mask_sites=24,
        full_pass_bound=141564,early_pass_bound=215,complete_encoded_D_noiseless_period_proved=True,
        arbitrary_damaged_lower_or_higher_iid_small_constants_proved=False,
        active_G17_or_frozen_GAW2R_changed=False,seconds=time.monotonic()-start)),flush=True)

if __name__=='__main__':main()
