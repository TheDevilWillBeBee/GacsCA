#!/usr/bin/env python3
"""Observe actual first-pulse GF/keep at old foreign work frames135..142.

No late store, bank or command is supplied. This observer can support a
future same-history interpreter proof; its output alone is not that proof.
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib,json,subprocess,time
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent.parent
OUT=ROOT/'figs/robustness/unregistered_sp31_work_protection'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

GLOBALS=r'''
static unsigned work_bad[8];
static int work_first_t[8],work_first_x[8];
static unsigned work_first_code[8];
static unsigned long long work_intervals[8];
'''
OBSERVER=r'''
        /* Read-only proof observer; local/next/Info values are untouched. */
        unsigned failed=((at(s,a)&1)!=1) | (((v&1)!=1)<<1) |
            (((v&2)&&((v&1)!=((v>>5)&1)))<<2);
        for(int h=135;h<=142;h++){
            int start=h*Q-512+1,end=h*Q-512+1024,k=h-135;
            if(a<end&&start<b){
                work_intervals[k]++;
                if(failed&&!work_bad[k]){
                    work_first_t[k]=elapsed;work_first_x[k]=a>start?a:start;
                    work_first_code[k]=failed;
                }
                work_bad[k]|=failed;
            }
        }
'''
TAIL=r'''
int main(int argc,char **argv){
    int status=first_pulse_main(argc,argv);if(status)return status;
    printf("{\"work_protection_observer\":true,\"frames\":[");
    for(int k=0;k<8;k++)printf("%s{\"h\":%d,\"bad_mask\":%u,\"first_old_row\":%d,\"first_x\":%d,\"first_code\":%u,\"checked_intervals\":%llu}",
        k?",":"",k+135,work_bad[k],work_first_t[k],work_first_x[k],work_first_code[k],work_intervals[k]);
    printf("]}\n");return 0;
}
'''

def main():
    started=time.monotonic();OUT.mkdir(exist_ok=True)
    original=BASE/'sp31_two_flag2_sources.c'
    assert sha(original)=='9dddb6a9661f801f7d625ba1560742aa3310d667dde2efa2f5f771a2f29479d4'
    source=original.read_text();marker='        append(next,a,b,v&31);events++;'
    assert source.count(marker)==1 and source.count('int main(int argc,char **argv)')==1
    observed=GLOBALS+source.replace(marker,OBSERVER+marker).replace('int main(int argc,char **argv)','int first_pulse_main(int argc,char **argv)')+TAIL
    path=OUT/'sp31_first_pulse_work_protection.c';path.write_text(observed)
    binary=OUT/'sp31_first_pulse_work_protection'
    build=subprocess.run(['gcc','-O3','-std=c11','-Wall','-Wextra',str(path),'-o',str(binary)],capture_output=True,text=True)
    (OUT/'build.log').write_text(build.stdout+build.stderr);assert build.returncode==0
    def run(mask):
        trace=OUT/f'mask{mask}_trace.jsonl';start=time.monotonic()
        with trace.open('w') as fh:proc=subprocess.run([str(binary),str(mask),'6144'],stdout=fh,stderr=subprocess.PIPE,text=True)
        (OUT/f'mask{mask}_stderr.log').write_text(proc.stderr);assert proc.returncode==0
        lines=trace.read_text().splitlines();result=json.loads(lines.pop())
        assert result['work_protection_observer']
        old=ROOT/'figs/robustness/SP31_two_sources'/f'mask{mask}_trace.jsonl'
        assert '\n'.join(lines)+'\n'==old.read_text(),'observer changed actual first trajectory'
        record=dict(mask=mask,frames=result['frames'],trace_sha256=sha(trace),old_trace_sha256=sha(old),
            exact_old_trace_unchanged=True,seconds=time.monotonic()-start)
        print(json.dumps(dict(mask=mask,work_frames_with_no_GF_change_or_SF_wipe=[r['h'] for r in result['frames'] if not r['bad_mask']],
            failures=[r for r in result['frames'] if r['bad_mask']])),flush=True)
        return record
    with ThreadPoolExecutor(max_workers=4) as pool:cases=list(pool.map(run,range(4)))
    protected=sorted(set.intersection(*[{r['h'] for r in c['frames'] if not r['bad_mask']} for c in cases]))
    result=dict(scope='Read-only GF/keep observer of four actual first-pulse enclosures; no interpreter bank theorem claimed',
        driver_sha256=sha(__file__),frozen_factor_sha256=sha(original),generated_C_source_sha256=sha(path),binary_sha256=sha(binary),
        cases=cases,complete_old_foreign_frames_GF_constant_and_keep1_for_all_four_masks=protected,
        late_Age_WF_banks_or_second_Flag2_values_proved=False,second_pulse_or_general_repair_proved=False,
        additional_rule_change=False,active_G17_modified=False,global_reliability_established=False,seconds=time.monotonic()-started)
    (OUT/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(complete=True,protected_frames=protected,seconds=result['seconds'])),flush=True)
if __name__=='__main__':main()
