"""Read-only intact gather/capture/full-evaluation and literal-P4 transplant replay."""
from pathlib import Path
from dataclasses import asdict
import hashlib,importlib.util,json,re,sys,time
ROOT=Path(__file__).resolve().parents[4];S=Path(__file__).resolve().parent
D=ROOT/'figs/gray_counterexamples/unregistered_gaw13'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    start=time.monotonic();mp=D/'GAW13_standalone_assets.json'
    assets=json.loads(mp.read_text())['assets_sha256']
    for name,h in assets.items():assert sha(ROOT/name)==h,('asset mismatch',name)
    cert=json.loads((D/'GAW13_gather_sf_certificate.json').read_text())
    assert cert['proof_sha256']==sha(S/'GAW13_GATHER_SF_HISTORY.md')
    assert cert['checker_sha256']==sha(S/'check_gaw13_gather_sf.py')
    assert cert['validator_sha256']==sha(Path(__file__))
    assert cert['receipt_sha256']==sha(D/'GAW13_gather_sf_receipt.json')
    assert (cert['Q'],cert['U'],cert['error_lambda'],cert['error_separation'])==(8192,1048576,24,104)
    for name in ('actual_recursively_intact_H','same_original_c104_real1_physical_history',
        'actual_chronological_third_LOAD_and_capture_row','actual_raw_holder_copy_reads',
        'actual_retained_History_wide_common_row_witness',
        'transplanted_literal_printed_P4_all_raw_SF_property_refuted',
        'actual_temporal_voted_banks_and_early_flags_derived',
        'actual_bounded_couriers_special_sources_and_quiet102Q_bridge',
        'complete_U_shadow_first_two_cases','selected_third_U_native_padding_outside_legal_E',
        'all_three_complete2U_shadow_from_unmasked_actual_banks'):
        assert cert[name],name
    for name in ('existing_proved_GAW2R_operational_lemma_refuted','Gray_Gacs_refutation',
        'general_SF_real1_repair','sixteen_row_bursts_replayed','general_malformed_padding_repair',
        'iid_reliability_or_failure','shorter_U','new_rule_created','active_rule_modified','registered_main_modified'):
        assert not cert[name],name
    assert cert['fault_clock']==524289 and cert['fault_spatial_interval']==[3841,3857]
    assert cert['retained_History_common_witness_clock']==589826
    assert cert['extreme_witness_physical_cells']==[-61688,69384]
    for link in re.findall(r'\]\(([^)]+)\)',(S/'GAW13_GATHER_SF_HISTORY.md').read_text()):
        assert (S/link).exists(),('broken proof link',link)
    prior=ROOT/'Report/proofs/gray_counterexamples/unregistered_gaw2/validate_gaw2_period_v2.py'
    sys.path.insert(0,str(prior.parent));spec=importlib.util.spec_from_file_location('gaw2_for_gaw13',prior)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.main()
    sys.path.insert(0,str(S));import check_gaw13_gather_sf as checker
    rom=json.loads((ROOT/'figs/gray_counterexamples/unregistered_gaw2/GAW2R_rom.json').read_text())
    rom['dictionary']=[int(v,0) if isinstance(v,str) else v for v in rom['dictionary']]
    assert json.loads(json.dumps(asdict(checker.own.ROM)))==rom,'exact actual own ROM'
    source=Path(checker.k.__file__).read_text()
    assert '96*Q<=age<98*Q' in source
    assert "wipe=a['f1'] and addr!=cells[0].addr" in source
    result=checker.main(write=False);assert len(result['cases'])==3
    for i,c in enumerate(result['cases']):
        assert c['actual_same_intact_H_physical_history'] and c['fault_clock']==524289
        payload=c['payload']['complete_chronological_payloads'];assert len(payload)==16
        for offset,p in enumerate(payload):
            old=[int(v,16) for v in p['old_complete_words']]
            new=[int(v,16) for v in p['replacement_complete_words']]
            assert p['t']==524289 and p['x']==3841+offset
            assert len(old)==len(new)==496 and old!=new
            assert old[:6]==new[:6]==[p['x']%8192,524289,0,0,0,0]
        classification=c['payload']['original_c104_classification']
        assert classification['level0']==0 and classification['level1'] and tuple(classification['extent'])==(16,1)
        assert c['actual_source_capture']['actual_full_local_R_source_capture_reset_checks']==4420
        assert len(c['actual_source_capture']['event_clocks'])==10
        b=c['actual_bank_reduction']
        assert b['actual_voted_Mem_disagreement_normal_colonies']==([] if i<2 else [0])
        assert len(b['actual_changed_bank_words'])==(0 if i<2 else 9)
        assert b['actual_held_History_disagreement_normal_colonies']==([g for g in range(-8,9) if g] if i<2 else list(range(-8,9)))
        f=c['actual_retained_History_footprint'];assert len(f['actual_retained_third_History_noncentral_footprint'])==16
        assert f['physical_colonies']==[g for g in range(-8,9) if g]
        assert not f['one_fixed_adjacent_pair_raw_History_bound']
        e=c['actual_evaluation'];assert e['actual_core_early_flag_pair']==([0,0] if i<2 else [1,1])
        assert e['actual_core_early']['updates']==(150 if i<2 else 152)
        assert e['actual_core_late']['updates']==(66185 if i<2 else 72255)
        normal=[int(v,16) for v in e['actual_core_U_normal_record']]
        assert normal[:6]==([0,1,0,0,0,0] if i<2 else [(1<<100)-1,0,1,1,0,0])
        bridge=c['actual_courier_Workspace_quiet_bridge']
        assert bridge['actual_full_local_R_courier_source_checks']==176
        assert bridge['actual_early_seed_flag_pair']==([0,0] if i<2 else [1,1])
        assert bridge['Workspace_half_open_guard']==[96*8192,98*8192]
        assert bridge['native_flag_quiet_by']==99*8192
        boundary=c['actual_U_and_repair']
        assert boundary['actual_U_bad_normal_record_receivers']==([] if i<2 else [0])
        assert boundary['actual_U_native_padding_legal']==(i<2)
        assert boundary['complete_U_shadow_proved']==(i<2)
        assert boundary['actual_U_core_full_local_R_commit_checks']==506
        assert boundary['complete2U_shadow_proved'] and not boundary['legal_upper_period_theorem_used']
        runs=boundary['actual_derived_second_period_bank_executions']
        assert [r['receiver'] for r in runs]==list(range(-8,9))
        for r in runs:
            assert len(r['actual17_raw_input_records'])==17
            assert [int(v,16) for v in r['early']['out_words']][2:4]==[0,0]
            assert r['late']['updates']==65062
            assert [int(v,16) for v in r['late']['out_words']]==checker.k.cell_words(checker.base.next2H(r['receiver']))
            if i==2:
                for relative,words in r['actual17_raw_input_records']:
                    if r['receiver']+relative==0:assert int(words[0],16)==(1<<100)-1
    # Decisive common-row full raw fields, rather than joining different
    # receiver pairs or different capture times into a purported witness.
    case=checker.Actual('third_LOAD_Mail_mask');age=72*8192+2
    for d in (-8,8):
        y=checker.P-d*8192;lane=8+d
        for h,s in enumerate(checker.k.SLOTS):
            cell=case.row(y-s,age)
            assert ((cell.history3[h]>>(lane*100))&checker.k.MASK)==checker.k.MASK
            assert checker.base.I(checker.P)==0
    assert (checker.P+8*8192)-(checker.P-8*8192)==16*8192>2*8192
    for name,h in assets.items():assert sha(ROOT/name)==h,('read-only replay mutation',name)
    print(json.dumps(dict(passed=True,assets_verified=len(assets),exact_actual_ROM=True,
        actual_intact_start_original_real1_histories=3,actual_fault_clock=524289,
        source_capture_full_local_R_checks=13260,courier_source_full_local_R_checks=528,
        core_U_full_local_R_checks=1518,actual_derived_second_period_complete_executions=51,
        raw_History_witness_same_row=589826,extreme_witness_cells=[-61688,69384],
        transplanted_literal_P4_raw_SF_property=False,first_two_full_U_shadow=True,all_three_full2U_shadow=True,
        Gray_operational_iid_or_shorterU_refutation=False,manifest_sha256=sha(mp),
        elapsed_seconds=time.monotonic()-start)),flush=True)

if __name__=='__main__':main()
