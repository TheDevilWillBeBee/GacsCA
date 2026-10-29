#!/usr/bin/env python3
"""Four prepared fourth-enclosure corners, no actual physical source claim."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib,json,subprocess,time
ROOT=Path(__file__).resolve().parents[3];S=Path(__file__).resolve().parent
OUT=ROOT/'figs/robustness/unregistered_sp31_fourth_sources/pulse_corners'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    start=time.monotonic();OUT.mkdir(exist_ok=True);source=S/'sp31_fourth_enclosure_cases.c';binary=OUT/'fourth_cases'
    build=subprocess.run(['gcc','-O3','-std=c11','-Wall','-Wextra',str(source),'-o',str(binary)],capture_output=True,text=True)
    (OUT/'build.log').write_text(build.stdout+build.stderr);assert build.returncode==0
    def evaluate(mask):
        begin=time.monotonic();log=OUT/f'mask{mask}_trace.jsonl'
        with log.open('w') as fh:run=subprocess.run([str(binary),str(mask),'6144'],stdout=fh,stderr=subprocess.PIPE,text=True)
        stderr=OUT/f'mask{mask}_stderr.log';stderr.write_text(run.stderr);assert run.returncode==0
        data=[json.loads(line) for line in log.read_text().splitlines()];endpoint=data.pop()
        assert len(data)==6145 and [r['row'] for r in data]==list(range(6145))
        return dict(mask=mask,trace_sha256=sha(log),stderr_sha256=sha(stderr),endpoint=endpoint,final_row=data[-1],seconds=time.monotonic()-begin)
    masks=(0,(1<<17)-1,((1<<4)-1)<<17,(1<<21)-1)
    with ThreadPoolExecutor(max_workers=4) as pool:cases=list(pool.map(evaluate,masks))
    receipt=dict(scope='Four corners of prepared fourth21bit command superset; no mask reachability, actual fourth bank/source theorem, or exhaustive pulse theorem',
        Q=1024,U=475136,initial_template=[149,152],free_bits=21,source_masks=masks,
        driver_sha256=sha(__file__),wrapper_sha256=sha(source),frozen_factor_sha256=sha(S.parent/'sp31_two_flag2_sources.c'),binary_sha256=sha(binary),
        cases=cases,all2097152_masks_exhausted=False,actual_fourth_source_enclosure_or_pulse_proved=False,
        global_reliability_established=False,additional_rule_change=False,active_G17_modified=False,seconds=time.monotonic()-start)
    (OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(cases=[dict(mask=r['mask'],GF_width=r['final_row']['GF_sites'],endpoint=r['endpoint']['endpoint_segments']) for r in cases],seconds=receipt['seconds'],actual_fourth_source_enclosure_or_pulse_proved=False)),flush=True)
if __name__=='__main__':main()
