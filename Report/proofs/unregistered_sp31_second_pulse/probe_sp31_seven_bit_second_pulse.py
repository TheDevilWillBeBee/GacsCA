#!/usr/bin/env python3
"""Enumerate every member of J232's actual seven-bit source enclosure.

The immutable J231 diagnostic applies the previously proved quotient.
This driver does not supply reachable-mask claims or a repeated bank.
"""
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
import hashlib,json,subprocess,time
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'figs/robustness/unregistered_sp31_seven_bit_second_pulse'
OLD=ROOT/'figs/robustness/unregistered_sp31_second_pulse'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    started=time.monotonic();OUT.mkdir(exist_ok=True)
    dep=ROOT/'figs/robustness/SP31_protected_foreign_age_certificate.json'
    c=json.loads(dep.read_text());assert c['actual_seven_bit_source_enclosure_proved']
    binary=OLD/'sp31_second_enclosure_cases'
    assert sha(binary)=='cbb8f1084b299966c84c8be02cf30f2e6b4c00a4cb374b527af28d8e909ae8f2'
    def run(index):
        mask=(index&63)|((index>>6)<<17);trace=OUT/f'mask{index}_trace.jsonl'
        start=time.monotonic()
        with trace.open('w') as fh:
            proc=subprocess.run([str(binary),str(mask),'6144'],stdout=fh,stderr=subprocess.PIPE,text=True)
        (OUT/f'mask{index}_stderr.log').write_text(proc.stderr);assert proc.returncode==0,(index,proc.stderr)
        lines=[json.loads(line) for line in trace.read_text().splitlines()]
        rows=lines[:-1];last=rows[-1];footer=lines[-1]
        assert len(rows)==6145 and [r['row'] for r in rows]==list(range(6145))
        assert footer['mask']==mask and footer['exact_event_execution_complete']
        rec=dict(enclosure_mask=index,diagnostic18_mask=mask,trace_sha256=sha(trace),
            endpoint_segments=footer['endpoint_segments'],endpoint_Info=footer['endpoint_Info'],
            final_native_counts={k:last[k] for k in ('GF_sites','GF_left','GF_right_exclusive','GF_holes',
                'Flag1_sites','WF1_sites','Flag2_sites','WF2_sites','Info_ones','segments')},
            GF_width_change=last['GF_sites']-11776,total_exact_event_intervals=last['events'],
            maximum_native_segments=max(r['segments'] for r in rows),
            rows_with_GF_holes=sum(r['GF_holes']!=0 for r in rows),seconds=time.monotonic()-start)
        print(json.dumps(dict(mask=index,GF_width_change=rec['GF_width_change'],
            endpoint_segments=rec['endpoint_segments'],seconds=rec['seconds'])),flush=True)
        return rec
    cases=[]
    with ThreadPoolExecutor(max_workers=12) as pool:
        futures=[pool.submit(run,index) for index in range(128)]
        for future in as_completed(futures):cases.append(future.result())
    cases.sort(key=lambda r:r['enclosure_mask'])
    result=dict(scope='Complete128-member finite execution of J232 source enclosure; actual mask values and later banks unspecified',
        driver_sha256=sha(__file__),diagnostic_binary_sha256=sha(binary),
        C_source_sha256=sha(ROOT/'Report/proofs/unregistered_sp31_second_pulse/sp31_second_enclosure_cases.c'),
        included_frozen_factor_sha256=sha(ROOT/'Report/proofs/sp31_two_flag2_sources.c'),
        J232_certificate_sha256=sha(dep),cases=cases,
        all128_enclosure_members_run=True,all128_members_GF_width_decrease=all(r['GF_width_change']<0 for r in cases),
        conditional_cases_supply_actual_mask_reachability=False,
        actual_second_pulse_proof_by_composition_supplied_by_this_driver=False,
        repeated_bank_or_arbitrary_higher_or_iid_or_smallest_change_proved=False,
        additional_rule_change=False,active_G17_modified=False,Gray_G17_refutation=False,
        global_reliability_established=False,seconds=time.monotonic()-started)
    (OUT/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(complete=True,masks=len(cases),all_shrink=result['all128_members_GF_width_decrease'],
        width_changes=sorted({r['GF_width_change'] for r in cases}),seconds=result['seconds'])),flush=True)
if __name__=='__main__':main()
