#!/usr/bin/env python3
"""Prepared width6.5Q class, free exterior; optional HYPOTHETICAL force edit.

2048 is unchanged SP30. Other durations explicitly change the RF force
projection, without constructing or compiling a new fixed own rule.
No actual history, infinite-line theorem, eroder or noise result here.
"""
from pathlib import Path
import hashlib,json,subprocess,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[3];PARENT=ROOT/'figs/robustness'


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def expected_wrapper(force):
    assert force in (2048,3072,4096)
    source=(PARENT/'unregistered_terminal_controlled/half_colony_controlled_signal_generated.c').read_text()
    updates=force+4096
    replacements={
        'initial_a=128*Q-512,initial_b=128*Q,initial_lo=127*Q':
            'initial_a=128*Q-512,initial_b=134*Q,initial_lo=127*Q',
        'lo=72*Q-margin,hi=129*Q+margin':'lo=72*Q-margin,hi=152*Q+margin',
        '17*Q<lo':'Q<lo',
        'int ref=16*Q+(x&(Q-1))':'int ref=(x&(Q-1))',
        'duration=2*Q;info_mode=98':f'duration={force};info_mode=100',
        'r<6*Q':f'r<{updates}',
        'duration,6*Q+1':f'duration,{updates+1}',
        '/tmp/SP30_half_colony_controlled_signal_final.bin':f'/tmp/SP30_translation_class_force{force}_final.bin',
        '        info[x]=(x&(Q-1))!=1021?0:\n'
        '            (col<72 || col>=128 || col==123)?2:(124<=col && col<=126);':
            '        int residue=x&(Q-1);\n'
            '        info[x]=residue==509?(128<=col && col<=133):\n'
            '            residue!=1021?0:(col<72 || col>=152 || col==123)?2:\n'
            '            ((124<=col && col<=126)||(134<=col && col<=151));'}
    for old,new in replacements.items():assert source.count(old)==1,old;source=source.replace(old,new)
    return source


def main():
    force=int(sys.argv[1]);start=time.monotonic();updates=force+4096
    out=PARENT/f'unregistered_translation_force{force}';out.mkdir(exist_ok=True)
    wrapper=out/'generated.c';wrapper.write_text(expected_wrapper(force));exe=Path(f'/tmp/SP30_translation_class_force{force}')
    compile_run=subprocess.run(['cc','-O3','-std=c11','-Wall','-Wextra','-Werror','-Wno-parentheses',str(wrapper),'-o',str(exe)],capture_output=True,text=True)
    (out/'compile.log').write_text(compile_run.stdout+compile_run.stderr);assert compile_run.returncode==0,compile_run.stderr
    log=out/'trace.jsonl'
    with log.open('w') as stream:run=subprocess.run([str(exe),'0'],stdout=stream,stderr=subprocess.PIPE,text=True)
    (out/'stderr.log').write_text(run.stderr);rows=[json.loads(line) for line in log.read_text().splitlines()]
    complete=run.returncode==0
    if complete:
        summary=rows.pop();assert summary['certificate_complete'] and len(rows)==updates+1
        raw=Path(f'/tmp/SP30_translation_class_force{force}_final.bin').read_bytes();witness=None
    elif run.returncode==41:
        witness=rows.pop();assert witness['abstract_GF_unresolved'];summary=None
        raw=Path(f'/tmp/SP28_info_factor_{force}_mode100_unresolved_'+str(witness['offset'])+'.bin').read_bytes()
    else:
        failure=dict(scope='Prepared free-exterior translation force harness failure, no concrete counterexample',
            exit_code=run.returncode,stderr=run.stderr,checker_sha256=digest(__file__),wrapper_sha256=digest(wrapper),
            run_log_sha256=digest(log),hypothetical_force_change=force!=2048,global_reliability_established=False)
        (out/'failure.json').write_text(json.dumps(failure,indent=2)+'\n');print(json.dumps(failure),flush=True);return
    N=262144;assert len(raw)==11*N
    arrays=dict(native=np.frombuffer(raw,np.uint8,8*N).reshape(8,N).copy(),code=np.frombuffer(raw,np.uint16,N,8*N).copy(),Info=np.frombuffer(raw,np.uint8,N,10*N).copy())
    asset=out/'endpoint.npz';np.savez_compressed(asset,**arrays)
    endpoint=dict(wrong_GF_sites=int(arrays['native'][0].sum()),GF_support=[rows[-1]['left'],rows[-1]['right_exclusive']],
        native_nonzero_sites_by_plane=[int(np.count_nonzero(row)) for row in arrays['native']],
        code_nonzero_sites=int(np.count_nonzero(arrays['code'])),Info_fixed_ones=int(np.count_nonzero(arrays['Info']==1)),
        Info_free_bits=int(np.count_nonzero(arrays['Info']==2)))
    receipt=dict(scope='Prepared width6.5Q and finite controlled signal window, arbitrary exterior; finite domain only',
        Q=1024,U=475136,T_wf=278401,force_duration=force,updates=updates,initial_template_L_R=[128,134],
        initial_wrong_GF_interval=[130560,137216],initial_MF509_fixed_ones=list(range(128,134)),
        initial_MF1021_fixed_ones=[124,125,126,*range(134,152)],
        initial_MF1021_fixed_zero_colonies=[*range(72,123),127,*range(128,134)],
        initial_MF1021_free_quotient_colonies=[*range(72),123,*range(152,256)],
        seed_interval=[72*1024,152*1024],final_protected_interval=[72*1024-8*(updates+1)-37,152*1024+8*(updates+1)+37],
        finite_domain_recurrence_complete=complete,exit_code=run.returncode,first_unresolved_GF=witness,summary=summary,endpoint=endpoint,
        checker_sha256=digest(__file__),inherited_wrapper_sha256=digest(PARENT/'unregistered_terminal_controlled/half_colony_controlled_signal_generated.c'),
        frozen_factor_sha256=digest(PARENT/'SP29_third_pulse_domains_factor_generated.c'),
        new_rule_projection_receipt_sha256=digest(PARENT/'SP30_native_pulse_certificate.json'),
        wrapper_sha256=digest(wrapper),executable_sha256=digest(exe),run_log_sha256=digest(log),endpoint_asset_sha256=digest(asset),
        periodic_exterior_is_a_domain_box_not_one_physical_background=True,
        hypothetical_RF_force_projection_constant_change=force!=2048,new_fixed_own_rule_compiled=False,
        actual_period_signal_supply_or_original_history_proved=False,infinite_line_translation_class_or_eroder_proved=False,
        noise_or_iid_or_full_rule_counterexample_or_reliability_proved=False,
        active_G17_or_frozen_SP30_modified=False,global_reliability_established=False,seconds=time.monotonic()-start)
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(force_duration=force,complete=complete,first_unresolved_GF=witness,endpoint=endpoint,
        hypothetical_projection_force_change=force!=2048,seconds=receipt['seconds'])),flush=True)


if __name__=='__main__':main()
