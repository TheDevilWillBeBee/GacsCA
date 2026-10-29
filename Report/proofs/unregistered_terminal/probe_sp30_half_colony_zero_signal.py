#!/usr/bin/env python3
"""Unregistered prepared half-colony pulse with zero observed signal tracks.

This probes a terminal geometry outside the L<R bank theorem. It does not
derive an actual intact-start command or a later full-rule trajectory.
It changes neither the frozen factor nor the SP30/G17 rule.
"""
from pathlib import Path
import hashlib,json,subprocess,time
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
PARENT=ROOT/'figs/robustness';OUT=PARENT/'unregistered_terminal'


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    start=time.monotonic();OUT.mkdir(exist_ok=True)
    template=PARENT/'SP30_fourth_pulse_domains_generated.c';source=template.read_text()
    changes={
        '#include "SP29_third_pulse_domains_factor_generated.c"':
            '#include "../SP29_third_pulse_domains_factor_generated.c"',
        'initial_a=110*Q-512,initial_b=120*Q,initial_lo=109*Q':
            'initial_a=104*Q-512,initial_b=104*Q,initial_lo=103*Q',
        'lo=105*Q-margin,hi=154*Q+margin':'lo=103*Q-margin,hi=105*Q+margin',
        'info_mode=94':'info_mode=95',
        '/tmp/SP30_fourth_pulse_domains_final.bin':'/tmp/SP30_half_colony_zero_signal_final.bin',
        '    assert(initial_a-3*r<=a && a<=initial_a+3*r);\n'
        '    assert(initial_b-3*r<=b && b<=initial_b+3*r);\n'
        '    if(r){assert(a>=previous_a-3);assert(b<=previous_b+3);}':
        '    /* Hull contraction is unrestricted; retain only the checked exterior cone. */'}
    for old,new in changes.items():assert source.count(old)==1,old;source=source.replace(old,new)
    a=source.index('        int col=x/Q,residue=x&(Q-1);')
    b=source.index('\n    }\n    certify_row(0);',a)
    source=source[:a]+'        info[x]=0;\n'+source[b:]
    wrapper=OUT/'half_colony_zero_signal_generated.c';wrapper.write_text(source)
    exe=Path('/tmp/SP30_half_colony_zero_signal_certificate')
    compiled=subprocess.run(['cc','-O3','-std=c11','-Wall','-Wextra','-Werror','-Wno-parentheses',str(wrapper),'-o',str(exe)],capture_output=True,text=True)
    (OUT/'compile.log').write_text(compiled.stdout+compiled.stderr)
    assert compiled.returncode==0,compiled.stderr
    log=OUT/'half_colony_zero_signal.jsonl'
    with log.open('w') as stream:run=subprocess.run([str(exe),'0'],stdout=stream,stderr=subprocess.PIPE,text=True)
    (OUT/'stderr.log').write_text(run.stderr)
    raw_log=log.read_text();lines=raw_log.split('\n')[:-1]
    rows=[json.loads(line) for line in lines]
    complete=run.returncode==0;summary=rows.pop() if complete else None
    if complete:
        assert summary['certificate_complete'] and len(rows)==6145
        raw=Path('/tmp/SP30_half_colony_zero_signal_final.bin').read_bytes();N=262144
        assert len(raw)==11*N
        native=np.frombuffer(raw,np.uint8,8*N).reshape(8,N).copy()
        code=np.frombuffer(raw,np.uint16,N,8*N).copy();info=np.frombuffer(raw,np.uint8,N,10*N).copy()
        asset=OUT/'endpoint.npz';np.savez_compressed(asset,native=native,code=code,Info=info)
        endpoint=dict(wrong_GF_sites=int(native[0].sum()),GF_support=[rows[-1]['left'],rows[-1]['right_exclusive']],
            native_nonzero_sites_by_plane=[int(np.count_nonzero(row)) for row in native],
            code_nonzero_sites=int(np.count_nonzero(code)),Info_nonzero_sites=int(np.count_nonzero(info)))
    else:endpoint=None;asset=None
    r=dict(scope='Unregistered prepared half-colony geometry/zero observed alias signals; finite projected experiment only',
        Q=1024,U=475136,T_wf=278401,force_duration=2048,updates=6144,
        initial_template_L_R=[104,104],initial_wrong_GF_interval=[105984,106496],
        seed_interval=[103*1024,105*1024],prepared_observed_signal_tracks_zero=True,
        finite_domain_recurrence_complete=complete,exit_code=run.returncode,summary=summary,endpoint=endpoint,
        checker_sha256=digest(__file__),inherited_wrapper_sha256=digest(template),
        frozen_factor_sha256=digest(PARENT/'SP29_third_pulse_domains_factor_generated.c'),
        new_rule_projection_receipt_sha256=digest(PARENT/'SP30_native_pulse_certificate.json'),
        wrapper_sha256=digest(wrapper),executable_sha256=digest(exe),run_log_sha256=digest(log),
        endpoint_asset_sha256=digest(asset) if asset else None,
        retained_initial_harness_failure_sha256=digest(OUT/'initial_failure.json'),
        inherited_hull_contraction_bound_removed_from_wrapper=True,
        removed_bound_used_as_support_proof_or_rule_change=False,
        actual_intact_start_signal_or_history_or_later_pulses_proved=False,
        half_colony_terminal_repair_theorem_or_general_eroder_proved=False,
        noise_or_iid_or_full_rule_counterexample_proved=False,
        additional_rule_or_constant_change=False,active_G17_modified=False,global_reliability_established=False,
        elapsed_seconds=time.monotonic()-start)
    (OUT/'receipt.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(dict(complete=complete,endpoint=endpoint,actual_history_proved=False,
        elapsed_seconds=r['elapsed_seconds'])),flush=True)


if __name__=='__main__':main()
