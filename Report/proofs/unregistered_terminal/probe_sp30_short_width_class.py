"""Prepared small-width signal classes in the unchanged SP30 projection.

No actual original-error history is supplied by this probe. A successful
domain recurrence supports a conditional theorem only after a Z proof.
"""
from pathlib import Path
import hashlib,json,subprocess,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'figs/robustness'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def expected_wrapper(width):
    assert 1<=width<=5
    R=128+width;hi=R+18
    source=(OUT/'unregistered_translation_force2048/generated.c').read_text()
    changes={
        'initial_a=128*Q-512,initial_b=134*Q,initial_lo=127*Q':
            f'initial_a=128*Q-512,initial_b={R}*Q,initial_lo=127*Q',
        'lo=72*Q-margin,hi=152*Q+margin':f'lo=72*Q-margin,hi={hi}*Q+margin',
        'duration=2048;info_mode=100':f'duration=2048;info_mode={110+width}',
        '/tmp/SP30_translation_class_force2048_final.bin':f'/tmp/SP30_short_width{width}_final.bin',
        '        info[x]=residue==509?(128<=col && col<=133):\n'
        '            residue!=1021?0:(col<72 || col>=152 || col==123)?2:\n'
        '            ((124<=col && col<=126)||(134<=col && col<=151));':
            f'        info[x]=residue==509?(128<=col && col<{R}):\n'
            f'            residue!=1021?0:(col<72 || col>={hi} || col==123)?2:\n'
            f'            ((124<=col && col<=126)||({R}<=col && col<{hi}));'}
    for old,new in changes.items():assert source.count(old)==1,old;source=source.replace(old,new)
    return source


def main(width,write=True):
    start=time.monotonic();assert 1<=width<=5;R=128+width;hi=R+18
    dest=OUT/f'unregistered_short_width{width}';dest.mkdir(exist_ok=True)
    wrapper=dest/'generated.c';wrapper.write_text(expected_wrapper(width))
    exe=Path(f'/tmp/SP30_short_width{width}')
    compile_run=subprocess.run(['cc','-O3','-std=c11','-Wall','-Wextra','-Werror',
        '-Wno-parentheses',str(wrapper),'-o',str(exe)],capture_output=True,text=True)
    (dest/'compile.log').write_text(compile_run.stdout+compile_run.stderr)
    assert compile_run.returncode==0,compile_run.stderr
    log=dest/'trace.jsonl'
    with log.open('w') as stream:run=subprocess.run([str(exe),'0'],stdout=stream,stderr=subprocess.PIPE,text=True)
    (dest/'stderr.log').write_text(run.stderr)
    rows=[json.loads(line) for line in log.read_text().splitlines()]
    complete=run.returncode==0;summary=witness=None;endpoint=None
    if complete:
        summary=rows.pop();assert summary['certificate_complete'] and len(rows)==6145
        raw=Path(f'/tmp/SP30_short_width{width}_final.bin').read_bytes()
    elif run.returncode==41:
        witness=rows.pop();assert witness['abstract_GF_unresolved']
        raw=Path(f'/tmp/SP28_info_factor_2048_mode{110+width}_unresolved_'+str(witness['offset'])+'.bin').read_bytes()
    else:
        result=dict(scope='Prepared short-width harness failed, no concrete CA counterexample',
            width=width,exit_code=run.returncode,stderr=run.stderr,
            checker_sha256=sha(__file__),wrapper_sha256=sha(wrapper),run_log_sha256=sha(log),
            actual_original_error_history_proved=False,global_reliability_established=False)
        (dest/'failure.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));return result
    N=262144;assert len(raw)==11*N
    arrays=dict(native=np.frombuffer(raw,np.uint8,8*N).reshape(8,N).copy(),
        code=np.frombuffer(raw,np.uint16,N,8*N).copy(),Info=np.frombuffer(raw,np.uint8,N,10*N).copy())
    asset=dest/'endpoint.npz';np.savez_compressed(asset,**arrays)
    if complete:
        final=rows[-1];left,right=final['left'],final['right_exclusive'];x=np.arange(N)
        nonempty=final['wrong_Addresses']>0
        quiet=not arrays['native'][2:].any() and not arrays['code'].any()
        if nonempty:
            quiet=quiet and np.array_equal(arrays['native'][0],(left<=x)&(x<right)) and \
                np.array_equal(arrays['native'][1],((left-512<=x)&(x<left))|((right-512<=x)&(x<right)))
        else:quiet=quiet and not arrays['native'].any()
        endpoint=dict(wrong_GF_interval=[left,right] if nonempty else None,
            wrong_GF_sites=final['wrong_Addresses'],wrong_GF_width=right-left if nonempty else 0,
            native_quiet_template=bool(quiet),template_L_R=[(left+512)//1024,right//1024] if nonempty else None)
    tracks={str(phase):dict(fixed_one_colonies=np.flatnonzero(arrays['Info'][phase::1024]==1).tolist(),
        free_quotient_colonies=np.flatnonzero(arrays['Info'][phase::1024]==2).tolist()) for phase in (509,1021)}
    result=dict(scope='Prepared small-width signal class; unchanged finite projected domain equations only',
        Q=1024,U=475136,T_wf=278401,width_parameter=width,force_duration=2048,updates=6144,
        initial_template_L_R=[128,R],initial_wrong_GF_interval=[128*1024-512,R*1024],
        initial_MF509_one_colonies=list(range(128,R)),
        initial_MF1021_one_colonies=[124,125,126,*range(R,hi)],
        initial_MF1021_free_colonies_infinite=True,initial_free_near_left_colony=123,
        seed_interval=[72*1024,hi*1024],final_protected_interval=[72*1024-8*6145-37,hi*1024+8*6145+37],
        finite_domain_recurrence_complete=complete,exit_code=run.returncode,
        first_unresolved_GF=witness,summary=summary,endpoint=endpoint,retained_Info_tracks=tracks,
        checker_sha256=sha(__file__),inherited_wrapper_sha256=sha(OUT/'unregistered_translation_force2048/generated.c'),
        frozen_factor_sha256=sha(OUT/'SP29_third_pulse_domains_factor_generated.c'),
        wrapper_sha256=sha(wrapper),executable_sha256=sha(exe),run_log_sha256=sha(log),
        endpoint_asset_sha256=sha(asset),finite_equations_changed=False,
        only_prepared_initial_native_and_signal_box_changed=True,
        actual_original_error_history_or_infinite_line_theorem_proved=False,
        complete_rule_counterexample_or_general_eroder_or_higher_or_iid_proved=False,
        active_G17_or_frozen_SP30_modified=False,global_reliability_established=False,
        elapsed_seconds=time.monotonic()-start)
    if write:(dest/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('width_parameter','finite_domain_recurrence_complete',
        'first_unresolved_GF','endpoint','actual_original_error_history_or_infinite_line_theorem_proved',
        'global_reliability_established','elapsed_seconds')}),flush=True)
    return result


if __name__=='__main__':main(int(sys.argv[1]))
