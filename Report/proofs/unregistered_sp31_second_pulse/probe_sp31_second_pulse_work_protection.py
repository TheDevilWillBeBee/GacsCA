#!/usr/bin/env python3
"""Read-only second-pulse work observer; no bank or later source is supplied.

Selected masks are measurements. Running all 128 enclosure members can
certify the quotient's geometric premise, not the interpreter conclusion.
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib,json,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'figs/robustness/unregistered_sp31_second_work_protection'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
GLOBALS=r'''
static unsigned work_bad[4];
static int work_first_t[4],work_first_x[4];
static unsigned work_first_code[4];
static unsigned long long work_intervals[4];
'''
OBSERVER=r'''
        /* Read-only observer: no old, new or Info value is assigned. */
        unsigned failed=((at(s,a)&1)!=1) | (((v&1)!=1)<<1) |
            (((v&2)&&((v&1)!=((v>>5)&1)))<<2);
        for(int h=142;h<=145;h++){
            int start=h*Q-512+1,end=h*Q-512+1024,k=h-142;
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
    int status=second_pulse_main(argc,argv);if(status)return status;
    printf("{\"work_protection_observer\":true,\"frames\":[");
    for(int k=0;k<4;k++)printf("%s{\"h\":%d,\"bad_mask\":%u,\"first_old_row\":%d,\"first_x\":%d,\"first_code\":%u,\"checked_intervals\":%llu}",
        k?",":"",k+142,work_bad[k],work_first_t[k],work_first_x[k],work_first_code[k],work_intervals[k]);
    printf("]}\n");return 0;
}
'''
def main():
    started=time.monotonic();OUT.mkdir(exist_ok=True)
    indices=[int(arg) for arg in sys.argv[1:]] if len(sys.argv)>1 else [0,127]
    assert len(set(indices))==len(indices) and all(0<=i<128 for i in indices)
    factor=ROOT/'Report/proofs/sp31_two_flag2_sources.c'
    wrapper=Path(__file__).parent/'sp31_second_enclosure_cases.c'
    assert sha(factor)=='9dddb6a9661f801f7d625ba1560742aa3310d667dde2efa2f5f771a2f29479d4'
    assert sha(wrapper)=='442fc7ff1ef7fcfe622169be0d5d7f3c5e88e4450966fd95aa8746769d007883'
    source=factor.read_text();marker='        append(next,a,b,v&31);events++;'
    assert source.count(marker)==1
    source=source.replace(marker,OBSERVER+marker).replace('int main(int argc,char **argv)','int sp31_previous_first_pulse_main(int argc,char **argv)')
    second=wrapper.read_text().split('int main(int argc,char **argv)',1)[1]
    generated=GLOBALS+source+'\nint second_pulse_main(int argc,char **argv)'+second+TAIL
    path=OUT/'sp31_second_pulse_work_protection.c';path.write_text(generated)
    binary=OUT/'sp31_second_pulse_work_protection'
    build=subprocess.run(['gcc','-O3','-std=c11','-Wall','-Wextra',str(path),'-o',str(binary)],capture_output=True,text=True)
    (OUT/'build.log').write_text(build.stdout+build.stderr);assert build.returncode==0
    def run(index):
        mask=(index&63)|((index>>6)<<17);trace=OUT/f'mask{index}_trace.jsonl'
        start=time.monotonic()
        with trace.open('w') as fh:
            proc=subprocess.run([str(binary),str(mask),'6144'],stdout=fh,stderr=subprocess.PIPE,text=True)
        (OUT/f'mask{index}_stderr.log').write_text(proc.stderr);assert proc.returncode==0
        lines=trace.read_text().splitlines();record=json.loads(lines.pop())
        assert record['work_protection_observer']
        old=ROOT/'figs/robustness/unregistered_sp31_seven_bit_second_pulse'/f'mask{index}_trace.jsonl'
        assert '\n'.join(lines)+'\n'==old.read_text(),'observer changed quotient trajectory'
        result=dict(enclosure_mask=index,diagnostic18_mask=mask,frames=record['frames'],
            trace_sha256=sha(trace),old_trace_sha256=sha(old),exact_old_trace_unchanged=True,
            seconds=time.monotonic()-start)
        print(json.dumps(dict(mask=index,protected_frames=[r['h'] for r in record['frames'] if not r['bad_mask']],
            failures=[r for r in record['frames'] if r['bad_mask']])),flush=True)
        return result
    with ThreadPoolExecutor(max_workers=min(12,len(indices))) as pool:
        cases=list(pool.map(run,indices))
    protected=sorted(set.intersection(*[{r['h'] for r in c['frames'] if not r['bad_mask']} for c in cases]))
    result=dict(scope='Read-only second native-Info quotient work observer; no late bank theorem',
        driver_sha256=sha(__file__),frozen_factor_sha256=sha(factor),frozen_wrapper_sha256=sha(wrapper),
        generated_C_source_sha256=sha(path),binary_sha256=sha(binary),cases=cases,
        complete128_member_enclosure=len(indices)==128,
        protected_frames_in_all_listed_cases=protected,
        late_Age_GF_Flag_banks_or_third_source_values_proved=False,
        additional_rule_change=False,active_G17_modified=False,global_reliability_established=False,
        seconds=time.monotonic()-started)
    receipt=OUT/('receipt_all128.json' if len(indices)==128 else 'receipt_selected.json')
    receipt.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(complete=True,cases=len(cases),protected_frames=protected,seconds=result['seconds'])),flush=True)
if __name__=='__main__':main()
