#!/usr/bin/env python3
"""Read-only replay of conditional F31 enclosure countercase, not CA failure."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib,json,subprocess,tempfile,time
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'figs/robustness'
DIR=OUT/'unregistered_sp31_second_pulse'
SOURCE=Path(__file__).parent/'unregistered_sp31_second_pulse/sp31_second_enclosure_cases.c'
PROOF=Path(__file__).with_name('SP31_SECOND_ENCLOSURE_LIMIT.md')
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    start=time.monotonic();receipt_path=DIR/'receipt.json';r=json.loads(receipt_path.read_text())
    assert r['J229_certificate_sha256']==sha(OUT/'SP31_second_source_enclosure_certificate.json')
    assert r['C_source_sha256']==sha(SOURCE)
    assert r['checker_sha256']==sha(SOURCE.with_name('probe_sp31_second_enclosure_cases.py'))
    assert r['included_frozen_factor_sha256']==sha(SOURCE.parent.parent/'sp31_two_flag2_sources.c')=='9dddb6a9661f801f7d625ba1560742aa3310d667dde2efa2f5f771a2f29479d4'
    assert '#include "../sp31_two_flag2_sources.c"' in SOURCE.read_text()
    assert (r['Q'],r['U'],r['elapsed_ticks'])==(1024,475136,6144)
    for key in ('all18bit_masks_checked','physical_source_masks_reachability_proved',
        'actual_second_pulse_proved','whole_CA_simulation','additional_rule_change','active_G17_modified','global_reliability_established'):
        assert r[key] is False,key
    summaries=[]
    for c in r['cases']:
        mask=c['mask'];path=DIR/f'mask{mask}_trace.jsonl';assert sha(path)==c['trace_sha256']
        lines=[json.loads(s) for s in path.read_text().splitlines()];endpoint=lines.pop()
        assert [x['row'] for x in lines]==list(range(6145))
        assert endpoint['endpoint_segments']==c['endpoint_segments'] and endpoint['endpoint_Info']==c['endpoint_Info']
        assert endpoint['exact_event_execution_complete'] and not endpoint['physical_source_reachability_proved']
        assert lines[-1]==c['endpoint'] and lines[0]==c['initial']
        assert c['initial']['GF_sites']==11776 and c['width_change']==c['endpoint']['GF_sites']-11776
        expected=([135168,135680,2],[135680,152064,1],[152064,152576,3]) if mask==262143 else ([144384,144896,2],[144896,152064,1],[152064,152576,3])
        assert c['endpoint_segments']==list(expected)
        assert c['width_change']==(5120 if mask==262143 else -4096)
        assert c['endpoint']['Flag2_sites']==c['endpoint']['WF1_sites']==c['endpoint']['WF2_sites']==0
        assert not c['native_GF_clock_actual_source_reachability_or_general_repair_proved']
        summaries.append(dict(mask=mask,endpoint_segments=c['endpoint_segments'],GF_width_change=c['width_change'],
            exact_event_intervals=c['events'],trace_sha256=c['trace_sha256']))
    assert [c['mask'] for c in summaries]==[0,262143,1,131072]
    with tempfile.TemporaryDirectory(prefix='sp31_countercase_readonly_') as td:
        binary=Path(td)/'sp31_second_enclosure_cases'
        compiled=subprocess.run(['gcc','-O3','-std=c11','-Wall','-Wextra',str(SOURCE),'-o',str(binary)],capture_output=True,text=True)
        assert compiled.returncode==0 and sha(binary)==r['binary_sha256']
        def replay(mask):
            proc=subprocess.run([str(binary),str(mask),'6144'],capture_output=True,text=True)
            assert proc.returncode==0 and proc.stdout==(DIR/f'mask{mask}_trace.jsonl').read_text()
            assert proc.stderr==(DIR/f'mask{mask}_stderr.log').read_text()
            return mask
        with ThreadPoolExecutor(max_workers=2) as pool:replayed=list(pool.map(replay,(0,262143)))
    result=dict(proposal='SP31',scope='J231 conditional pulse countercase to width-decreasing implication from J22918bit enclosure; actual masks/later repair unknown',
        proof_sha256=sha(PROOF),checker_sha256=sha(__file__),exploration_receipt_sha256=sha(receipt_path),
        C_source_sha256=sha(SOURCE),included_frozen_factor_sha256=r['included_frozen_factor_sha256'],
        diagnostic_binary_sha256=r['binary_sha256'],J229_certificate_sha256=r['J229_certificate_sha256'],
        source_dependencies_sha256={str(path.relative_to(ROOT)):sha(path) for path in (SOURCE,
            SOURCE.with_name('probe_sp31_second_enclosure_cases.py'),SOURCE.parent.parent/'sp31_two_flag2_sources.c')},
        proof_dependencies_sha256={name:sha(PROOF.parent/name) for name in ('SP31_FIRST_PULSE.md','SP31_SECOND_SOURCE_ENCLOSURE.md')},
        retained_assets_sha256={str(path.relative_to(OUT)):sha(path) for path in sorted(DIR.iterdir()) if path.is_file()},
        selected_exact_conditional_pulses=summaries,read_only_masks_replayed=replayed,
        all_one_enclosure_member_conditional_GF_width_growth=5120,
        current_enclosure_implies_uniform_width_decrease=False,conditional_countercase_proved=True,
        physical_all_one_source_reachability_proved=False,actual_second_pulse_proved=False,all_masks_classified=False,
        global_reliability_established=False,additional_rule_change=False,active_G17_modified=False,
        arbitrary_higher_repair_or_positive_iid_or_smallest_change_proved=False,Gray_or_G17_refutation=False,
        seconds=time.monotonic()-start)
    (OUT/'SP31_second_enclosure_limit_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(conditional_countercase_proved=True,all_one_GF_width_growth=5120,
        masks_replayed=replayed,actual_second_pulse_or_Gray_iid_failure_proved=False,seconds=result['seconds'])),flush=True)
if __name__=='__main__':main()
