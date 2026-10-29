#!/usr/bin/env python3
"""Complete finite source enclosure -> actual second native F31 pulse.

The written proof supplies the universal quotient/physical composition.
All128 event executions are pinned and checked; two extreme traces are
independently replayed with the identical rebuilt quotient binary.
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib,json,subprocess,tempfile,time
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'figs/robustness'
DIR=OUT/'unregistered_sp31_seven_bit_second_pulse'
SOURCE=Path(__file__).parent/'unregistered_sp31_second_pulse/sp31_second_enclosure_cases.c'
DRIVER=SOURCE.with_name('probe_sp31_seven_bit_second_pulse.py')
PROOF=Path(__file__).with_name('SP31_SECOND_PULSE.md')
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    started=time.monotonic();receipt_path=DIR/'receipt.json';r=json.loads(receipt_path.read_text())
    age_path=OUT/'SP31_protected_foreign_age_certificate.json';age=json.loads(age_path.read_text())
    assert r['J232_certificate_sha256']==sha(age_path)
    assert age['actual_seven_bit_source_enclosure_proved'] and age['second_Flag2_enclosure_free_bits']==7
    assert age['all_initial_upper_Info_allowed'] and age['no_future_tape_or_Workspace_or_controller_supplied']
    assert r['driver_sha256']==sha(DRIVER) and r['C_source_sha256']==sha(SOURCE)
    assert r['included_frozen_factor_sha256']==sha(SOURCE.parent.parent/'sp31_two_flag2_sources.c')=='9dddb6a9661f801f7d625ba1560742aa3310d667dde2efa2f5f771a2f29479d4'
    assert r['diagnostic_binary_sha256']=='cbb8f1084b299966c84c8be02cf30f2e6b4c00a4cb374b527af28d8e909ae8f2'
    assert r['all128_enclosure_members_run'] and r['all128_members_GF_width_decrease']
    assert [c['enclosure_mask'] for c in r['cases']]==list(range(128))
    expected=[[144384,144896,2],[144896,152064,1],[152064,152576,3]]
    counts=('GF_sites','GF_left','GF_right_exclusive','GF_holes','Flag1_sites','WF1_sites','Flag2_sites','WF2_sites','Info_ones','segments')
    checked_rows=0;events=0;summaries=[]
    for case in r['cases']:
        index=case['enclosure_mask'];mask=(index&63)|((index>>6)<<17)
        assert case['diagnostic18_mask']==mask
        path=DIR/f'mask{index}_trace.jsonl';assert sha(path)==case['trace_sha256']
        records=[json.loads(line) for line in path.read_text().splitlines()];footer=records.pop()
        assert len(records)==6145 and [row['row'] for row in records]==list(range(6145))
        checked_rows+=len(records);first,last=records[0],records[-1]
        assert (first['GF_sites'],first['GF_left'],first['GF_right_exclusive'],first['Flag1_sites'])==(11776,137728,149504,1024)
        assert first['Info_ones']==30+index.bit_count()
        assert first['Flag2_sites']==first['WF1_sites']==first['WF2_sites']==0
        assert all(a['events']<b['events'] for a,b in zip(records,records[1:]))
        assert footer['mask']==mask and footer['endpoint_segments']==case['endpoint_segments']==expected
        assert footer['endpoint_Info']==case['endpoint_Info']
        assert footer['exact_event_execution_complete'] and not footer['physical_source_reachability_proved']
        assert {key:last[key] for key in counts}==case['final_native_counts']
        assert (last['GF_sites'],last['GF_left'],last['GF_right_exclusive'],last['GF_holes'],last['Flag1_sites'],last['segments'])==(7680,144896,152576,0,1024,3)
        assert last['Flag2_sites']==last['WF1_sites']==last['WF2_sites']==0
        assert case['GF_width_change']==last['GF_sites']-first['GF_sites']==-4096
        assert case['total_exact_event_intervals']==last['events']
        assert case['maximum_native_segments']==max(row['segments'] for row in records)
        assert case['rows_with_GF_holes']==sum(row['GF_holes']!=0 for row in records)
        assert (DIR/f'mask{index}_stderr.log').read_text()==''
        events+=last['events'];summaries.append(dict(enclosure_mask=index,diagnostic18_mask=mask,
            endpoint_segments=expected,GF_width_change=-4096,exact_event_intervals=last['events'],
            maximum_native_segments=case['maximum_native_segments'],rows_with_GF_holes=case['rows_with_GF_holes'],trace_sha256=sha(path)))
    with tempfile.TemporaryDirectory(prefix='sp31-second-pulse-readonly-') as tmp:
        binary=Path(tmp)/'sp31_second_enclosure_cases'
        build=subprocess.run(['gcc','-O3','-std=c11','-Wall','-Wextra',str(SOURCE),'-o',str(binary)],capture_output=True,text=True)
        assert build.returncode==0 and not build.stdout+build.stderr
        assert sha(binary)==r['diagnostic_binary_sha256']
        def replay(index):
            mask=(index&63)|((index>>6)<<17)
            proc=subprocess.run([str(binary),str(mask),'6144'],capture_output=True,text=True)
            assert proc.returncode==0 and proc.stdout==(DIR/f'mask{index}_trace.jsonl').read_text() and not proc.stderr
            return index
        with ThreadPoolExecutor(max_workers=2) as pool:replayed=list(pool.map(replay,(0,127)))
    assert 'Draft awaiting' not in PROOF.read_text()
    deps=('SP31_first_pulse_certificate.json','SP31_second_source_enclosure_certificate.json',
        'SP31_protected_foreign_age_certificate.json','SP31_encoded_certificate.json')
    result=dict(proposal='SP31',scope='J234 complete actual seven-bit enclosure, exact128 pulses, same J225 history second native4Q shrink and2U native-reset boundary; third banks/general repair unproved',
        Q=1024,U=475136,T_wf=278401,radius=37,candidate_sha256=age['candidate_sha256'],
        netlist_sha256=age['netlist_sha256'],checker_sha256=sha(__file__),proof_sha256=sha(PROOF),
        exploration_receipt_sha256=sha(receipt_path),diagnostic_binary_sha256=r['diagnostic_binary_sha256'],
        source_dependencies_sha256={str(path.relative_to(ROOT)):sha(path) for path in
            (SOURCE,DRIVER,SOURCE.parent.parent/'sp31_two_flag2_sources.c')},
        proof_dependencies_sha256={name:sha(PROOF.parent/name) for name in
            ('SP31_OWN_RULE.md','SP31_FIRST_PULSE.md','SP31_SECOND_SOURCE_ENCLOSURE.md','SP31_PROTECTED_FOREIGN_AGE_BANK.md')},
        receipt_dependencies_sha256={name:sha(OUT/name) for name in deps},
        retained_exact_execution_assets_sha256={str(path.relative_to(OUT)):sha(path) for path in sorted(DIR.iterdir()) if path.is_file()},
        retained_exploration_run_sha256=sha(OUT/'SP31_seven_bit_second_pulse_exploration_run.log'),
        abstract_suffix_exploration_assets_sha256={str(path.relative_to(ROOT)):sha(path) for path in
            (SOURCE.with_name('probe_sp31_abstract_native_late_suffix.py'),
             OUT/'SP31_abstract_native_late_suffix_exploration.json',OUT/'SP31_abstract_native_late_suffix_exploration.log')},
        conditional_exact_pulse_summaries=summaries,total_masks=128,total_all_row_records_checked=checked_rows,
        total_exact_event_intervals=events,read_only_masks_replayed=replayed,
        initial_native_template=[135,146],endpoint_native_template=[142,149],
        initial_wrong_GF_interval=[137728,149504],endpoint_wrong_GF_interval=[144896,152576],
        initial_wrong_GF_width=11776,endpoint_wrong_GF_width=7680,GF_width_change=-4096,
        second_source_physical_time=753537,second_pulse_endpoint_physical_time=759681,second_boundary_physical_time=950272,
        all128_source_assignments_exactly_classified=True,actual_second_native_pulse_proved=True,
        all_initial_upper_Info_and_actual_unknown_vote_correlations_allowed=True,
        no_future_tape_or_Workspace_or_physical_boundary_supplied=True,
        actual_second_native_boundary_and807_private_alias_zero_reset_proved=True,
        all_source_masks_physically_reachable_proved=False,whole_upper_Info_successor_at2U_proved=False,
        abstract_suffix_terms_are_physical_failures=False,third_pulse_proved=False,
        repeated_bank_invariant_or_arbitrary_higher_repair_or_positive_iid_or_minimum_change_proved=False,
        global_reliability_established=False,additional_rule_change=False,active_G17_modified=False,
        Gray_or_G17_refutation=False,seconds=time.monotonic()-started)
    (OUT/'SP31_second_pulse_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,source_masks=128,all_row_records=checked_rows,
        exact_event_intervals=events,read_only_masks_replayed=replayed,actual_second_native_pulse_proved=True,
        second_endpoint_template=[142,149],GF_width_change=-4096,global_reliability_established=False,
        seconds=result['seconds'])),flush=True)
if __name__=='__main__':main()
