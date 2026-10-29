#!/usr/bin/env python3
"""Prepared half-colony pulse, MF509 zero and every MF1021 bit arbitrary.

All true-signal bits are enclosed independently, including the background.
The finite domain's exterior is a periodic box, not a selected physical
trajectory. A full-domain Z inclusion proof is needed for a theorem.
This adds no rule change and asserts no actual terminal-history bridge.
"""
from pathlib import Path
import hashlib,json,subprocess,time
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
PARENT=ROOT/'figs/robustness';OUT=PARENT/'unregistered_terminal_arbitrary'


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    start=time.monotonic();OUT.mkdir(exist_ok=True)
    template=PARENT/'unregistered_terminal/half_colony_zero_signal_generated.c'
    source=template.read_text();changes={
        'info_mode=95':'info_mode=97',
        '/tmp/SP30_half_colony_zero_signal_final.bin':'/tmp/SP30_half_colony_arbitrary_signal_final.bin',
        '        info[x]=0;':'        info[x]=(x&(Q-1))==1021?2:0;'}
    for old,new in changes.items():assert source.count(old)==1,old;source=source.replace(old,new)
    wrapper=OUT/'half_colony_arbitrary_signal_generated.c';wrapper.write_text(source)
    exe=Path('/tmp/SP30_half_colony_arbitrary_signal_certificate')
    compiled=subprocess.run(['cc','-O3','-std=c11','-Wall','-Wextra','-Werror','-Wno-parentheses',str(wrapper),'-o',str(exe)],capture_output=True,text=True)
    (OUT/'compile.log').write_text(compiled.stdout+compiled.stderr)
    assert compiled.returncode==0,compiled.stderr
    log=OUT/'half_colony_arbitrary_signal.jsonl'
    with log.open('w') as stream:run=subprocess.run([str(exe),'0'],stdout=stream,stderr=subprocess.PIPE,text=True)
    (OUT/'stderr.log').write_text(run.stderr)
    rows=[json.loads(line) for line in log.read_text().split('\n')[:-1]]
    complete=run.returncode==0
    if complete:
        summary=rows.pop();assert summary['certificate_complete'] and len(rows)==6145
        raw=Path('/tmp/SP30_half_colony_arbitrary_signal_final.bin').read_bytes();witness=None
    elif run.returncode==41:
        witness=rows.pop();assert witness['abstract_GF_unresolved'];summary=None
        raw=Path('/tmp/SP28_info_factor_2048_mode97_unresolved_'+str(witness['offset'])+'.bin').read_bytes()
    else:
        failure=dict(exit_code=run.returncode,stderr=run.stderr,parsed_rows=len(rows),
            scope='Prepared arbitrary-true-signal terminal domain harness failure; not a concrete counterexample',
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
    receipt=dict(scope='Unregistered prepared half-colony and all true-signal domains; finite sound-domain calculation only',
        Q=1024,U=475136,T_wf=278401,force_duration=2048,updates=6144,
        initial_template_L_R=[104,104],initial_wrong_GF_interval=[105984,106496],
        seed_interval=[103*1024,105*1024],
        initial_MF509_zero_everywhere=True,initial_MF1021_free_everywhere=True,
        initial_true_signal_bits_in_256Q_quotient=256,
        finite_domain_recurrence_complete=complete,exit_code=run.returncode,
        first_unresolved_GF=witness,summary=summary,endpoint=endpoint,
        checker_sha256=digest(__file__),inherited_wrapper_sha256=digest(template),
        frozen_factor_sha256=digest(PARENT/'SP29_third_pulse_domains_factor_generated.c'),
        new_rule_projection_receipt_sha256=digest(PARENT/'SP30_native_pulse_certificate.json'),
        wrapper_sha256=digest(wrapper),executable_sha256=digest(exe),run_log_sha256=digest(log),
        endpoint_asset_sha256=digest(asset),
        periodic_exterior_is_a_domain_box_not_one_physical_background=True,
        actual_terminal_signal_or_intact_start_history_proved=False,
        infinite_line_arbitrary_signal_terminal_theorem_or_general_eroder_proved=False,
        noise_or_iid_or_full_rule_counterexample_proved=False,
        additional_rule_or_constant_change=False,active_G17_modified=False,
        global_reliability_established=False,elapsed_seconds=time.monotonic()-start)
    (OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(complete=complete,first_unresolved_GF=witness,endpoint=endpoint,
        infinite_line_theorem_proved=False,elapsed_seconds=receipt['elapsed_seconds'])),flush=True)


if __name__=='__main__':main()
