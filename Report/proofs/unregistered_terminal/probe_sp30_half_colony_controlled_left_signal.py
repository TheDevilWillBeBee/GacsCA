#!/usr/bin/env python3
"""Prepared terminal pulse with a finite controlled left-signal window.

The same frozen domain factor is used without a rule change. True
signals outside the window are free, including the periodic exterior.
This driver alone supplies no physical terminal history or Z theorem.
"""
from pathlib import Path
import hashlib,json,subprocess,time
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
PARENT=ROOT/'figs/robustness';OUT=PARENT/'unregistered_terminal_controlled'


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def expected_wrapper():
    template=PARENT/'unregistered_terminal/half_colony_zero_signal_generated.c'
    source=template.read_text();changes={
        'initial_a=104*Q-512,initial_b=104*Q,initial_lo=103*Q':
            'initial_a=128*Q-512,initial_b=128*Q,initial_lo=127*Q',
        'lo=103*Q-margin,hi=105*Q+margin':'lo=72*Q-margin,hi=129*Q+margin',
        'info_mode=95':'info_mode=98',
        '/tmp/SP30_half_colony_zero_signal_final.bin':'/tmp/SP30_half_colony_controlled_signal_final.bin',
        '        info[x]=0;':
            '        int col=x/Q;\n'
            '        info[x]=(x&(Q-1))!=1021?0:\n'
            '            (col<72 || col>=128 || col==123)?2:(124<=col && col<=126);'}
    for old,new in changes.items():assert source.count(old)==1,old;source=source.replace(old,new)
    return source


def main():
    start=time.monotonic();OUT.mkdir(exist_ok=True)
    wrapper=OUT/'half_colony_controlled_signal_generated.c';wrapper.write_text(expected_wrapper())
    exe=Path('/tmp/SP30_half_colony_controlled_signal_certificate')
    compiled=subprocess.run(['cc','-O3','-std=c11','-Wall','-Wextra','-Werror','-Wno-parentheses',str(wrapper),'-o',str(exe)],capture_output=True,text=True)
    (OUT/'compile.log').write_text(compiled.stdout+compiled.stderr)
    assert compiled.returncode==0,compiled.stderr
    log=OUT/'half_colony_controlled_signal.jsonl'
    with log.open('w') as stream:run=subprocess.run([str(exe),'0'],stdout=stream,stderr=subprocess.PIPE,text=True)
    (OUT/'stderr.log').write_text(run.stderr)
    rows=[json.loads(line) for line in log.read_text().split('\n')[:-1]]
    complete=run.returncode==0
    if complete:
        summary=rows.pop();assert summary['certificate_complete'] and len(rows)==6145
        raw=Path('/tmp/SP30_half_colony_controlled_signal_final.bin').read_bytes();witness=None
    elif run.returncode==41:
        witness=rows.pop();assert witness['abstract_GF_unresolved'];summary=None
        raw=Path('/tmp/SP28_info_factor_2048_mode98_unresolved_'+str(witness['offset'])+'.bin').read_bytes()
    else:
        failure=dict(exit_code=run.returncode,stderr=run.stderr,parsed_rows=len(rows),
            scope='Prepared controlled-left terminal domain harness failure; no concrete counterexample',
            checker_sha256=digest(__file__),wrapper_sha256=digest(wrapper),run_log_sha256=digest(log),
            global_reliability_established=False)
        (OUT/'failure.json').write_text(json.dumps(failure,indent=2)+'\n');print(json.dumps(failure),flush=True);return
    N=262144;assert len(raw)==11*N
    arrays=dict(native=np.frombuffer(raw,np.uint8,8*N).reshape(8,N).copy(),
        code=np.frombuffer(raw,np.uint16,N,8*N).copy(),Info=np.frombuffer(raw,np.uint8,N,10*N).copy())
    asset=OUT/'endpoint.npz';np.savez_compressed(asset,**arrays)
    endpoint=dict(wrong_GF_sites=int(arrays['native'][0].sum()),
        GF_support=[rows[-1]['left'],rows[-1]['right_exclusive']],
        native_nonzero_sites_by_plane=[int(np.count_nonzero(row)) for row in arrays['native']],
        code_nonzero_sites=int(np.count_nonzero(arrays['code'])),
        Info_fixed_ones=int(np.count_nonzero(arrays['Info']==1)),
        Info_free_bits=int(np.count_nonzero(arrays['Info']==2)))
    receipt=dict(scope='Prepared half-colony with controlled finite left window and otherwise free true signals; finite domain only',
        Q=1024,U=475136,T_wf=278401,force_duration=2048,updates=6144,
        initial_template_L_R=[128,128],initial_wrong_GF_interval=[130560,131072],
        seed_interval=[72*1024,129*1024],
        final_protected_interval=[72*1024-8*6145-37,129*1024+8*6145+37],
        initial_MF509_zero_everywhere=True,initial_MF1021_fixed_ones=[124,125,126],
        initial_MF1021_fixed_zero_colonies=[*range(72,123),127],
        initial_MF1021_free_quotient_colonies=[*range(72),123,*range(128,256)],
        finite_domain_recurrence_complete=complete,exit_code=run.returncode,
        first_unresolved_GF=witness,summary=summary,endpoint=endpoint,
        checker_sha256=digest(__file__),
        inherited_wrapper_sha256=digest(PARENT/'unregistered_terminal/half_colony_zero_signal_generated.c'),
        frozen_factor_sha256=digest(PARENT/'SP29_third_pulse_domains_factor_generated.c'),
        new_rule_projection_receipt_sha256=digest(PARENT/'SP30_native_pulse_certificate.json'),
        wrapper_sha256=digest(wrapper),executable_sha256=digest(exe),run_log_sha256=digest(log),
        endpoint_asset_sha256=digest(asset),
        periodic_exterior_is_a_domain_box_not_one_physical_background=True,
        actual_terminal_signal_or_intact_start_history_proved=False,
        infinite_line_controlled_signal_terminal_theorem_or_general_eroder_proved=False,
        noise_or_iid_or_full_rule_counterexample_proved=False,
        additional_rule_or_constant_change=False,active_G17_modified=False,
        global_reliability_established=False,elapsed_seconds=time.monotonic()-start)
    (OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(complete=complete,first_unresolved_GF=witness,endpoint=endpoint,
        infinite_line_theorem_proved=False,elapsed_seconds=receipt['elapsed_seconds'])),flush=True)


if __name__=='__main__':main()
