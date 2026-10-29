#!/usr/bin/env python3
"""Prepared sixth signal domain; no actual-history or Z theorem here."""
from pathlib import Path
import hashlib,json,subprocess,time
import numpy as np
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'figs/robustness';DEST=OUT/'unregistered_sixth'


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def member_c(values):return '('+' || '.join('col=='+str(x) for x in values)+')' if values else '0'


def seed(result):
    touched=[97,104,*result['sixth_MF1021_fixed_one_colonies'],*result['sixth_MF1021_unspecified_colonies']]
    return min(touched),max(touched)+2


def expected_wrapper(result):
    lo,hi=seed(result);source=(OUT/'SP30_fifth_pulse_domains_generated.c').read_text()
    changes={
        '#include "SP29_third_pulse_domains_factor_generated.c"':'#include "../SP29_third_pulse_domains_factor_generated.c"',
        'initial_a=104*Q-512,initial_b=112*Q,initial_lo=103*Q':'initial_a=98*Q-512,initial_b=104*Q,initial_lo=97*Q',
        'lo=99*Q-margin,hi=167*Q+margin':f'lo={lo}*Q-margin,hi={hi}*Q+margin',
        'info_mode=96':'info_mode=98',
        '/tmp/SP30_fifth_pulse_domains_final.bin':'/tmp/SP30_sixth_pulse_domains_final.bin',
        '    assert(initial_a-3*r<=a && a<=initial_a+3*r);':'    if(count)assert(initial_a-3*r<=a);',
        '    assert(initial_b-3*r<=b && b<=initial_b+3*r);':'    if(count)assert(b<=initial_b+3*r);',
        '    if(r){assert(a>=previous_a-3);assert(b<=previous_b+3);}':
            '    if(r && count && previous_a<previous_b){assert(a>=previous_a-3);assert(b<=previous_b+3);}'}
    for old,new in changes.items():assert source.count(old)==1,old;source=source.replace(old,new)
    a=source.index('        int fixed=');b=source.index('\n    }\n    certify_row(0);',a)
    return source[:a]+('        int fixed=(residue==509 && 98<=col && col<=103) ||\n'
        '            (residue==1021 && '+member_c(result['sixth_MF1021_fixed_one_colonies'])+');\n'
        '        int uncertain=residue==1021 && '+member_c(result['sixth_MF1021_unspecified_colonies'])+';\n'
        '        assert(!(fixed && uncertain));info[x]=uncertain?2:fixed;\n')+source[b:]


def main():
    start=time.monotonic();DEST.mkdir(exist_ok=True);signal_path=DEST/'signal_receipt.json'
    enclosure=json.loads(signal_path.read_text());result=enclosure['results']
    assert enclosure['checker_sha256']==digest(ROOT/'Report/proofs/unregistered_terminal/probe_sp30_sixth_signal.py')
    assert not enclosure['actual_fifth_boundary_or_sixth_signal_or_pulse_or_terminal_history_proved']
    wrapper=DEST/'pulse_generated.c';wrapper.write_text(expected_wrapper(result));exe=Path('/tmp/SP30_sixth_pulse_domain_certificate')
    compiled=subprocess.run(['cc','-O3','-std=c11','-Wall','-Wextra','-Werror','-Wno-parentheses',str(wrapper),'-o',str(exe)],capture_output=True,text=True)
    (DEST/'compile.log').write_text(compiled.stdout+compiled.stderr);assert compiled.returncode==0,compiled.stderr
    log=DEST/'pulse.jsonl'
    with log.open('w') as stream:run=subprocess.run([str(exe),'0'],stdout=stream,stderr=subprocess.PIPE,text=True)
    (DEST/'stderr.log').write_text(run.stderr)
    complete=run.returncode==0;lines=[json.loads(line) for line in log.read_text().splitlines()]
    if complete:
        summary=lines.pop();assert summary['certificate_complete'] and len(lines)==6145
        witness=None;raw=Path('/tmp/SP30_sixth_pulse_domains_final.bin').read_bytes()
    elif run.returncode==41:
        summary=None;witness=lines.pop();assert witness['abstract_GF_unresolved']
        raw=Path('/tmp/SP28_info_factor_2048_mode98_unresolved_'+str(witness['offset'])+'.bin').read_bytes()
    else:
        failure=dict(scope='Prepared sixth-domain harness failure, no concrete counterexample',exit_code=run.returncode,
            stderr=run.stderr,checker_sha256=digest(__file__),wrapper_sha256=digest(wrapper),run_log_sha256=digest(log),global_reliability_established=False)
        (DEST/'pulse_failure.json').write_text(json.dumps(failure,indent=2)+'\n');print(json.dumps(failure),flush=True);return
    N=262144;assert len(raw)==11*N
    arrays=dict(native=np.frombuffer(raw,np.uint8,8*N).reshape(8,N).copy(),code=np.frombuffer(raw,np.uint16,N,8*N).copy(),Info=np.frombuffer(raw,np.uint8,N,10*N).copy())
    asset=DEST/'endpoint.npz';np.savez_compressed(asset,**arrays);endpoint=None;tracks=None
    if complete:
        row=lines[-1];left,right=row['left'],row['right_exclusive'];x=np.arange(N)
        quiet=not arrays['native'][2:].any() and not arrays['code'].any() and \
            np.array_equal(arrays['native'][1],((left-512<=x)&(x<left))|((right-512<=x)&(x<right)))
        endpoint=dict(wrong_GF_interval=[left,right],width=right-left,width_decrease=6656-(right-left),
            native_quiet_template=bool(quiet),template_L_R=[(left+512)//1024,right//1024])
        tracks={str(phase):dict(known_one_colonies=np.flatnonzero(arrays['Info'][phase::1024]==1).tolist(),
            unknown_colonies=np.flatnonzero(arrays['Info'][phase::1024]==2).tolist()) for phase in (509,1021)}
    lo,hi=seed(result)
    receipt=dict(scope='Prepared sixth-signal sound finite domain, actual stores/signals/Z/history unproved',
        Q=1024,U=475136,T_wf=278401,force_duration=2048,updates=6144,initial_template_L_R=[98,104],
        initial_wrong_GF_interval=[99840,106496],seed_interval=[lo*1024,hi*1024],
        final_protected_interval=[lo*1024-8*6145-37,hi*1024+8*6145+37],optional_bit_count=result['optional_bit_count'],
        finite_domain_recurrence_complete=complete,exit_code=run.returncode,first_unresolved_GF=witness,summary=summary,
        endpoint=endpoint,retained_Info_tracks=tracks,checker_sha256=digest(__file__),signal_receipt_sha256=digest(signal_path),
        inherited_wrapper_sha256=digest(OUT/'SP30_fifth_pulse_domains_generated.c'),frozen_factor_sha256=digest(OUT/'SP29_third_pulse_domains_factor_generated.c'),
        wrapper_sha256=digest(wrapper),executable_sha256=digest(exe),run_log_sha256=digest(log),endpoint_asset_sha256=digest(asset),
        arbitrary_domain_masks_enclosed_only_after_actual_source_bridge=True,
        actual_sixth_signal_pulse_or_terminal_history_or_general_eroder_proved=False,
        higher_map_or_iid_counterexample_or_reliability_proved=False,
        additional_rule_programme_layout_or_constant_change=False,active_G17_modified=False,
        global_reliability_established=False,seconds=time.monotonic()-start)
    (DEST/'pulse_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(complete=complete,endpoint=endpoint,retained_Info_tracks=tracks,first_unresolved_GF=witness,seconds=receipt['seconds'])),flush=True)


if __name__=='__main__':main()
