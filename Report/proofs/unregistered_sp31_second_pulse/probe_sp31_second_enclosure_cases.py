#!/usr/bin/env python3
"""Four conditional native/Info pulses; actual Flag2 reachability stays open."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib,json,subprocess,time
ROOT=Path(__file__).resolve().parents[3];S=Path(__file__).resolve().parent
OUT=ROOT/'figs/robustness/unregistered_sp31_second_pulse'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    start=time.monotonic();OUT.mkdir(exist_ok=True)
    source=S/'sp31_second_enclosure_cases.c';binary=OUT/'sp31_second_enclosure_cases'
    assert sha(S.parent/'sp31_two_flag2_sources.c')=='9dddb6a9661f801f7d625ba1560742aa3310d667dde2efa2f5f771a2f29479d4'
    prior=ROOT/'figs/robustness/SP31_second_source_enclosure_certificate.json'
    cert=json.loads(prior.read_text())
    assert cert['actual_second_Flag1_source_enclosure_proved'] and cert['second_Flag2_enclosure_free_bits']==18
    compiled=subprocess.run(['gcc','-O3','-std=c11','-Wall','-Wextra',str(source),'-o',str(binary)],capture_output=True,text=True)
    (OUT/'build.log').write_text(compiled.stdout+compiled.stderr);assert compiled.returncode==0
    masks=(0,(1<<18)-1,1,1<<17)
    def run(mask):
        path=OUT/f'mask{mask}_trace.jsonl';started=time.monotonic()
        with path.open('w') as fh:
            proc=subprocess.run([str(binary),str(mask),'6144'],stdout=fh,stderr=subprocess.PIPE,text=True)
        (OUT/f'mask{mask}_stderr.log').write_text(proc.stderr);assert proc.returncode==0,(mask,proc.stderr)
        lines=[json.loads(s) for s in path.read_text().splitlines()];summary=lines.pop()
        assert [r['row'] for r in lines]==list(range(6145)) and summary['exact_event_execution_complete']
        assert not summary['physical_source_reachability_proved']
        first,last=lines[0],lines[-1]
        assert (first['GF_left'],first['GF_right_exclusive'],first['GF_sites'])==(137728,149504,11776)
        result=dict(mask=mask,events=last['events'],initial=first,endpoint=last,
            endpoint_segments=summary['endpoint_segments'],endpoint_Info=summary['endpoint_Info'],
            width_change=last['GF_sites']-first['GF_sites'],max_segments=max(r['segments'] for r in lines),
            maximum_GF_holes=max(r['GF_holes'] for r in lines),noninterval_GF_rows=sum(r['GF_holes']>0 for r in lines),
            native_GF_clock_actual_source_reachability_or_general_repair_proved=False,
            trace_sha256=sha(path),seconds=time.monotonic()-started)
        print(json.dumps(dict(mask=mask,endpoint=last,width_change=result['width_change'],
            actual_Flag2_mask_reachability_proved=False)),flush=True)
        return result
    with ThreadPoolExecutor(max_workers=4) as pool:cases=list(pool.map(run,masks))
    result=dict(scope='Four selected members of J229 second-source enclosure; conditional native/Info event quotient only',
        checker_sha256=sha(__file__),C_source_sha256=sha(source),included_frozen_factor_sha256=sha(S.parent/'sp31_two_flag2_sources.c'),
        binary_sha256=sha(binary),build_log_sha256=sha(OUT/'build.log'),J229_certificate_sha256=sha(prior),
        Q=1024,U=475136,elapsed_ticks=6144,free_Flag2_bits=cert['second_Flag2_free_source_bits'],cases=cases,
        all18bit_masks_checked=False,physical_source_masks_reachability_proved=False,
        actual_second_pulse_proved=False,whole_CA_simulation=False,additional_rule_change=False,active_G17_modified=False,
        global_reliability_established=False,seconds=time.monotonic()-start)
    (OUT/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(complete=True,cases=len(cases),actual_second_pulse_proved=False,seconds=result['seconds'])),flush=True)
if __name__=='__main__':main()
