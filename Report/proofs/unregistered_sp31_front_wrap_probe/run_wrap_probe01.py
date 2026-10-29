#!/usr/bin/env python3
"""Exploratory abstract pulse receipts, not physical-history theorems."""
from pathlib import Path
import hashlib,json,subprocess,tempfile,time
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
OUT=ROOT/'figs/robustness/unregistered_sp31_front_wrap_probe';SOURCE=HERE/'sp31_wrap_probe01.c'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def runs(v,LO):
    out=[];start=0
    for i in range(1,len(v)+1):
        if i==len(v) or v[i]!=v[start]:
            if v[start]:out.append([LO+start,LO+i,v[start]])
            start=i
    return out
def main():
    receipt=OUT/'wrap_factor_probe01_receipt.json';assert not receipt.exists()
    started=time.monotonic();result=[]
    with tempfile.TemporaryDirectory(prefix='sp31_wrap_') as d:
        binary=Path(d)/'wrap';args=['gcc','-O3','-std=c11','-Wall','-Wextra','-Werror',str(SOURCE),'-o',str(binary)]
        built=subprocess.run(args,capture_output=True,text=True)
        assert built.returncode==0 and not built.stdout and not built.stderr,(built.returncode,built.stdout,built.stderr)
        for name,nforeign,nright in [('three_foreign_two_right',3,2),('two_foreign_zero_right',2,0)]:
            log=OUT/(name+'_trace01.jsonl');state=OUT/(name+'_state01.bin');err=OUT/(name+'_stderr01.log')
            t=time.monotonic()
            with log.open('w') as fh,err.open('w') as ef:
                run=subprocess.run([str(binary),str(state),'6144','1',str(nforeign),str(nright)],stdout=fh,stderr=ef,text=True)
            assert run.returncode==0 and not err.read_bytes(),(name,run.returncode)
            rows=[json.loads(x) for x in log.read_text().splitlines()];numeric=rows[:-1]
            assert all(x['border_violations']==0 for x in numeric)
            data=state.read_bytes();N=120*1024;assert len(data)==6*N
            result.append(dict(name=name,nforeign=nforeign,nright=nright,marker=rows[-1],
                               endpoint=numeric[-1],native_ranges={k:runs(data[j*N:(j+1)*N],80*1024) for j,k in enumerate(('GF','F1','WF1','F2','WF2'))},
                               trace_sha256=sha(log),state_sha256=sha(state),stderr_sha256=sha(err),
                               seconds=time.monotonic()-t))
            print(json.dumps(dict(case=name,marker=rows[-1],native_ranges=result[-1]['native_ranges'])),flush=True)
    r=dict(source_sha256=sha(SOURCE),driver_sha256=sha(__file__),results=result,
           status='measured abstract-factor trajectories only; source soundness/physical bank lift not registered',
           actual_after293U_physical_successor_proved=False,all_time_or_eventual_repair_or_iid_proved=False,
           rule_ROM_constants_or_G17_changed=False,global_reliability_established=False,seconds=time.monotonic()-started)
    receipt.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(passed=True,receipt_sha256=sha(receipt),seconds=r['seconds'])),flush=True)
if __name__=='__main__':main()
