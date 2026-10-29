#!/usr/bin/env python3
"""Retain a prepared actual-factor pulse; not an actual-history theorem."""
from pathlib import Path
import hashlib,json,subprocess,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'figs/robustness'


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    started=time.monotonic()
    source=ROOT/'Report/proofs/probe_short_force1024_signal_pulse.c'
    included=ROOT/'Report/proofs/native_address_info_factor.c'
    binary=Path('/tmp/SP29_prepared_history_signal_pulse')
    subprocess.run(['gcc','-O3','-std=c99',str(source),'-o',str(binary)],check=True)
    log=OUT/'SP29_prepared_history_signal_pulse.jsonl'
    with log.open('w') as stream:
        result=subprocess.run([str(binary)],stdout=stream,stderr=subprocess.PIPE,text=True)
    if result.returncode:raise RuntimeError((result.returncode,result.stderr))
    rows=[json.loads(line) for line in log.read_text().splitlines()]
    assert rows[0]['stage']=='initial' and rows[-1]['stage']=='final'
    assert rows[-1]['offset']==6144
    arrays={};n=262144
    for stage,offset in [('initial',0),('final',6144)]:
        data=Path(f'/tmp/SP28_info_factor_2048_mode3_{stage}_{offset}.bin').read_bytes()
        assert len(data)==11*n
        arrays[stage+'_native']=np.frombuffer(data,dtype=np.uint8,count=8*n).reshape(8,n).copy()
        arrays[stage+'_code']=np.frombuffer(data,dtype=np.uint16,count=n,offset=8*n).copy()
        arrays[stage+'_Info']=np.frombuffer(data,dtype=np.uint8,count=n,offset=10*n).copy()
    asset=OUT/'SP29_prepared_history_signal_states.npz';np.savez_compressed(asset,**arrays)
    receipt=dict(scope='finite prepared native/Info-factor pulse with six extra true-phase signal bits; actual preceding history not established by this experiment',
        proposal='SP29',proposed_rule_change=False,additional_rule_change=False,
        active_G17_modified=False,SP28_modified=False,
        driver_sha256=digest(Path(__file__)),C_wrapper_sha256=digest(source),
        included_transition_source_sha256=digest(included),
        log_sha256=digest(log),state_asset_sha256=digest(asset),
        Q=1024,U=475136,T_wf=278401,force_duration=2048,pulse_updates=6144,
        initial_ghost_MF509_one_colonies=list(range(128,144)),
        initial_true_MF1021_one_colonies=[124,125,126,144,145,146],
        initial_native_GF_interval=[130560,147456],
        initial_summary=rows[0],final_summary=rows[-1],
        measured_only=True,actual_preceding_physical_programme_history_established=False,
        finite_quotient_infinite_line_lift_proved=False,
        eroder_higher_map_or_iid_threshold_established=False,
        global_reliability_established=False,seconds=time.monotonic()-started)
    (OUT/'SP29_prepared_history_signal_pulse.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt),flush=True)


if __name__=='__main__':main()
