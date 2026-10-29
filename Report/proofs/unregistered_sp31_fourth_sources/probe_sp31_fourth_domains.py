#!/usr/bin/env python3
"""Unregistered conditional fourth-pulse domain study; no physical bank lift."""
from pathlib import Path
import hashlib,json,subprocess,time
ROOT=Path(__file__).resolve().parents[3]
S=Path(__file__).resolve().parent
OUT=ROOT/'figs/robustness/unregistered_sp31_fourth_sources'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    start=time.monotonic();OUT.mkdir(exist_ok=True)
    source=S/'sp31_fourth_domains.c';binary=OUT/'sp31_fourth_domains'
    compile=subprocess.run(['gcc','-O3','-std=c11','-Wall','-Wextra',str(source),'-o',str(binary)],capture_output=True,text=True)
    (OUT/'domains_compile.log').write_text(compile.stdout+compile.stderr)
    assert compile.returncode==0,compile.stderr
    log=OUT/'domains_run.jsonl';state=OUT/'domains_final_or_unresolved.bin'
    with log.open('w') as fh:
        run=subprocess.run([str(binary),str(state)],stdout=fh,stderr=subprocess.PIPE,text=True)
    (OUT/'domains_stderr.log').write_text(run.stderr)
    rows=[json.loads(x) for x in log.read_text().splitlines()]
    assert run.returncode in (0,41,42),(run.returncode,run.stderr)
    receipt=dict(scope='Prepared fourth native-command enclosure, exact-GF sound Boolean domains; physical bank/source lift and universal transcription remain to be proved',
        Q=1024,U=475136,initial_template=[149,152],
        MF509_fixed_one_colonies=list(range(149,152)),
        MF1021_fixed_one_colonies=[*range(106,148),152,153,154],
        MF3_free_colonies=list(range(132,149)),MF515_free_colonies=list(range(148,152)),
        free_bits=21,concrete_enclosure_members=1<<21,
        exit_code=run.returncode,finite_domain_complete=run.returncode==0,
        last_record=rows[-1],rows_completed=sum('row' in r for r in rows),
        driver_sha256=sha(__file__),source_sha256=sha(source),binary_sha256=sha(binary),
        assets_sha256={str(p.relative_to(ROOT)):sha(p) for p in (log,state,OUT/'domains_compile.log',OUT/'domains_stderr.log')},
        actual_fourth_source_enclosure_or_pulse_proved=False,
        global_reliability_established=False,additional_rule_change=False,active_G17_modified=False,
        seconds=time.monotonic()-start)
    (OUT/'domains_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ('exit_code','finite_domain_complete','rows_completed','last_record','seconds')}),flush=True)
if __name__=='__main__':main()
