#!/usr/bin/env python3
"""Four actual-source-enclosure pilots, retaining every exact quotient row."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib,json,subprocess,time
ROOT=Path(__file__).resolve().parents[3];S=Path(__file__).resolve().parent
D=ROOT/'figs/robustness/unregistered_sp31_third_pulse_pilot'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    start=time.monotonic();D.mkdir(exist_ok=True);src=S/'sp31_third_enclosure_cases.c';binary=D/'third_cases'
    proc=subprocess.run(['gcc','-O3','-std=c11','-Wall','-Wextra',str(src),'-o',str(binary)],capture_output=True,text=True)
    (D/'build.log').write_text(proc.stdout+proc.stderr);assert proc.returncode==0
    def run(mask):
        path=D/f'mask{mask}_trace.jsonl';t=time.monotonic()
        with path.open('w') as fh:proc=subprocess.run([str(binary),str(mask),'6144'],stdout=fh,stderr=subprocess.PIPE,text=True)
        (D/f'mask{mask}_stderr.log').write_text(proc.stderr);assert proc.returncode==0
        lines=path.read_text().splitlines();rows=[json.loads(line) for line in lines[:-1]];end=json.loads(lines[-1])
        assert len(rows)==6145 and [row['row'] for row in rows]==list(range(6145))
        return dict(mask=mask,trace_sha256=sha(path),endpoint=end,final_row=rows[-1],GF_hull=[min(r['GF_left'] for r in rows),max(r['GF_right_exclusive'] for r in rows)],seconds=time.monotonic()-t)
    with ThreadPoolExecutor(max_workers=4) as pool:cases=list(pool.map(run,(0,2047,2048,4095)))
    result=dict(proposal='SP31',scope='Selected exact third twelve-bit native/Info enclosure pulses; not all4096 members or physical mask reachability',
        wrapper_sha256=sha(src),driver_sha256=sha(__file__),frozen_factor_sha256=sha(S.parent/'sp31_two_flag2_sources.c'),binary_sha256=sha(binary),
        full_third_source_certificate_sha256=sha(ROOT/'figs/robustness/SP31_third_source_enclosure_certificate.json'),
        cases=cases,all4096_masks_exhausted=False,third_actual_physical_pulse_outcome_proved=False,global_reliability_established=False,
        additional_rule_change=False,active_G17_modified=False,seconds=time.monotonic()-start)
    (D/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(pilot_cases=[dict(mask=c['mask'],endpoint=c['endpoint']['endpoint_segments'],GF_width=c['final_row']['GF_sites']) for c in cases],all4096_masks_exhausted=False,seconds=result['seconds'])),flush=True)
if __name__=='__main__':main()
