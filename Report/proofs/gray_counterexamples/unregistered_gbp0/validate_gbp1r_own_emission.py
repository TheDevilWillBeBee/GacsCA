"""Read-only hash and all-new mathematical replay for the GBP1R diagnostic.

Outputs are limited to --output and stdout. Mathematical replays run in a
temporary directory and compare all retained full values except wall time.
No registered or frozen receipt is overwritten.
"""
import argparse
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[4]
SOURCE=Path(__file__).resolve().parent
DATA=ROOT/'figs/gray_counterexamples/unregistered_gbp0'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized(v):
    if isinstance(v,dict):
        return {k:normalized(x) for k,x in v.items() if k not in ('elapsed_seconds','time_seconds')}
    if isinstance(v,list):return [normalized(x) for x in v]
    return v


def replay(script,args,receipt,temp):
    output=temp/(receipt.name+'.replayed.json')
    command=[sys.executable,str(SOURCE/script),*args,'--output',str(output)]
    begin=time.monotonic()
    env=dict(os.environ);env['PYTHONDONTWRITEBYTECODE']='1'
    process=subprocess.run(command,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    assert process.returncode==0,(script,process.returncode,process.stdout)
    actual=json.loads(output.read_text());expected=json.loads(receipt.read_text())
    assert normalized(actual)==normalized(expected),(script,'exact receipt disagreement')
    return {'script':str(SOURCE.relative_to(ROOT)/script),'receipt':str(receipt.relative_to(ROOT)),
            'receipt_sha256':sha(receipt),'exit_code':process.returncode,'full_values_equal':True,
            'elapsed_seconds':time.monotonic()-begin}


def run():
    start=time.monotonic();manifest_path=DATA/'GBP1R_manifest.json'
    manifest=json.loads(manifest_path.read_text());assets=manifest['assets']
    for name,digest in assets.items():assert sha(ROOT/name)==digest,(name,'source/receipt/dependency changed')
    assert manifest['scope']['frozen'] and not manifest['scope']['Q_beta_fit']
    assert not manifest['scope']['gray_counterexample'] and not manifest['scope']['iid_failure']
    failed=json.loads((DATA/'GBP1R_simultaneous_capture_checker_failure.json').read_text())
    for kind in ('source','log'):
        assert sha(ROOT/failed['failed_'+kind])==failed['failed_'+kind+'_sha256']
    assert not failed['rule_changed']
    with tempfile.TemporaryDirectory(prefix='gbp1r_replay_') as temporary:
        temp=Path(temporary);results=[]
        for script,args,receipt in (
            ('check_gbp1r_resources.py',[],DATA/'GBP1R_resources.json'),
            ('check_native_source_prefix.py',['--count','20'],DATA/'GBP1_native_source_prefix_internal_test.json'),
            ('check_full_rom_execution.py',['--cases','all'],DATA/'GBP1R_full_execution_all_with_cutoffs.json'),
            ('check_selected_clean_period.py',[],DATA/'GBP1R_selected_clean_period_certificate.json')):
            result=replay(script,args,receipt,temp);results.append(result)
            print(json.dumps({'stage':script,'passed':True,'seconds':result['elapsed_seconds']}),flush=True)
    # Registered and active files are dependencies, never destinations. Check
    # them again after replay to detect any unexpected mutation.
    for name,digest in assets.items():assert sha(ROOT/name)==digest,(name,'changed during replay')
    resource=json.loads((DATA/'GBP1R_resources.json').read_text())
    period=json.loads((DATA/'GBP1R_selected_clean_period_certificate.json').read_text())
    traces=json.loads((DATA/'GBP1R_full_execution_all_with_cutoffs.json').read_text())['traces']
    halt=next(t for t in traces if t['name']=='halt_heads')
    assert len(halt['deadline_wrong_bits'])==1887 and len(halt['whole_fifth_stage_wrong_bits'])==407
    assert halt['deadline_raw_record']==period['cutoff_raw_record']
    from check_selected_clean_period import decode
    parsed=asdict(decode(tuple(map(int,halt['expected_raw_record']))))
    assert json.loads(json.dumps(parsed))==period['desired_successor_C_100']
    assert resource['GBP1R_beta_sha256']==period['beta_sha256']
    return {'passed':True,'scope':manifest['scope'],'asset_count':len(assets),
      'manifest_sha256':sha(manifest_path),'asset_hashes':assets,'replays':results,
      'selected_encoded_clean_period_identity_false':True,'fault_history_empty':True,
      'literal_active_R_checks':65534,'native_phases':8192,'gather_source_checks':745,
      'complete_prepared_cases':25,'halt_measured_ticks':147051,
      'deadline_wrong_bits':1887,'hypothetical_full_fifth_wrong_bits':407,
      'universal_compiler_identity':False,'Q_beta_fit':False,'intact_recursive_start':False,
      'noise_proof':False,'gray_refutation':False,'iid_failure':False,'shorter_U':False,
      'elapsed_seconds':time.monotonic()-start}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    options=parser.parse_args();result=run()
    options.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('asset_hashes','replays')},sort_keys=True),flush=True)
