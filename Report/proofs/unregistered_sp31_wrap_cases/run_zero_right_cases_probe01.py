#!/usr/bin/env python3
"""Eight independent prepared width2/zero-right factor cases; no CA edits."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib,json,subprocess,tempfile,time
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
OUT=ROOT/'figs/robustness/unregistered_sp31_wrap_cases';SOURCE=HERE/'sp31_wrap_cases01.c'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def intervals(v):
    result=[];start=0;LO=80*1024
    for i in range(1,len(v)+1):
        if i==len(v) or v[i]!=v[start]:
            if v[start]:result.append([LO+start,LO+i,v[start]])
            start=i
    return result
def main():
    started=time.monotonic();path=OUT/'zero_right_cases_probe01_receipt.json';assert not path.exists()
    with tempfile.TemporaryDirectory(prefix='sp31_zero_right_') as d:
        binary=Path(d)/'cases';args=['gcc','-O3','-std=c11','-Wall','-Wextra','-Werror',str(SOURCE),'-o',str(binary)]
        built=subprocess.run(args,capture_output=True,text=True)
        assert built.returncode==0 and not built.stdout and not built.stderr,(built.returncode,built.stdout,built.stderr)
        def one(mask):
            t=time.monotonic();stem=f'zero_mask{mask:02d}';log=OUT/(stem+'_trace01.jsonl');state=OUT/(stem+'_state01.bin');err=OUT/(stem+'_stderr01.log')
            with log.open('w') as fh,err.open('w') as ef:
                run=subprocess.run([str(binary),str(state),'6144','1','2','0',str(mask)],stdout=fh,stderr=ef,text=True)
            assert run.returncode==0 and not err.read_bytes(),(mask,run.returncode)
            rows=[json.loads(x) for x in log.read_text().splitlines()];numeric=rows[:-1]
            assert all(r['border_violations']==0 for r in numeric)
            assert [r['row'] for r in numeric]==list(range(len(numeric)))
            data=state.read_bytes();N=120*1024;assert len(data)==6*N
            r=dict(mask=mask,marker=rows[-1],endpoint=numeric[-1],
                   native_ranges={k:intervals(data[j*N:(j+1)*N]) for j,k in enumerate(('GF','F1','WF1','F2','WF2'))},
                   maximum_possible_GF_right=max(r['GF_possible_right_exclusive'] for r in numeric),
                   all_right_exterior_guards_zero=True,trace_sha256=sha(log),state_sha256=sha(state),stderr_sha256=sha(err),
                   seconds=time.monotonic()-t)
            print(json.dumps(dict(mask=mask,marker=r['marker'],native_ranges=r['native_ranges'])),flush=True);return r
        with ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(one,range(8)))
    assert [r['mask'] for r in results]==list(range(8))
    r=dict(source_sha256=sha(SOURCE),driver_sha256=sha(__file__),results=results,
           status='measured separate prepared width2/zero-right factor cases, not an actual physical succession',
           actual295U_or_later_physical_boundary_proved=False,all_time_or_eventual_higher_iid_or_minimum_proved=False,
           rule_ROM_constants_or_G17_changed=False,global_reliability_established=False,seconds=time.monotonic()-started)
    path.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(passed=True,receipt_sha256=sha(path),seconds=r['seconds'])),flush=True)
if __name__=='__main__':main()
