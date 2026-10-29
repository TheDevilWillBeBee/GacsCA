#!/usr/bin/env python3
"""Separate sound-domain fourth-pulse study; physical lift needs a proof.

The frozen exact domain factor is included unchanged. This driver changes
only the prepared initial enclosure and certificate/output filenames.
It stops on unresolved GF and never treats that as a concrete failure.
"""
from pathlib import Path
import hashlib,json,subprocess,time
import numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'figs/robustness'


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def member_c(values):return '('+' || '.join('col=='+str(x) for x in values)+')' if values else '0'


def main():
    started=time.monotonic();probe_path=OUT/'SP30_fourth_signal_probe.json'
    enclosure=json.loads(probe_path.read_text());result=enclosure['results']
    assert enclosure['checker_sha256']==digest(ROOT/'Report/proofs/probe_signal_reservation1024_fourth_signal.py')
    assert not enclosure['physical_third_boundary_or_complete_fourth_signal_or_pulse_proved']
    parent=OUT/'SP29_third_pulse_domains_generated.c';source=parent.read_text()
    changes={
        'initial_a=116*Q-512,initial_b=128*Q,initial_lo=115*Q':
            'initial_a=110*Q-512,initial_b=120*Q,initial_lo=109*Q',
        'lo=111*Q-margin,hi=150*Q+margin':'lo=105*Q-margin,hi=154*Q+margin',
        'info_mode=90':'info_mode=94',
        '/tmp/SP29_third_pulse_domains_final.bin':'/tmp/SP30_fourth_pulse_domains_final.bin'}
    for old,new in changes.items():assert source.count(old)==1,old;source=source.replace(old,new)
    a=source.index('        int fixed=');b=source.index('\n    }\n    certify_row(0);',a)
    source=source[:a]+('        int fixed=(residue==509 && 110<=col && col<=119) ||\n'
        '            (residue==1021 && '+member_c(result['fourth_MF1021_fixed_one_colonies'])+');\n'
        '        int uncertain=residue==1021 && '+member_c(result['fourth_MF1021_unspecified_colonies'])+';\n'
        '        assert(!(fixed && uncertain));info[x]=uncertain?2:fixed;\n')+source[b:]
    wrapper=OUT/'SP30_fourth_pulse_domains_generated.c';wrapper.write_text(source)
    exe=Path('/tmp/SP30_fourth_pulse_domains_certificate')
    compiled=subprocess.run(['cc','-O3','-std=c11','-Wall','-Wextra','-Werror','-Wno-parentheses',str(wrapper),'-o',str(exe)],capture_output=True,text=True)
    (OUT/'SP30_fourth_pulse_domains_compile.log').write_text(compiled.stdout+compiled.stderr)
    assert compiled.returncode==0,compiled.stderr
    log=OUT/'SP30_fourth_pulse_domains.jsonl'
    with log.open('w') as stream:run=subprocess.run([str(exe),'0'],stdout=stream,stderr=subprocess.PIPE,text=True)
    (OUT/'SP30_fourth_pulse_domains_stderr.log').write_text(run.stderr)
    lines=[json.loads(line) for line in log.read_text().splitlines()];complete=run.returncode==0
    if complete:
        summary=lines.pop();assert summary['certificate_complete'] and summary['rows_checked']==len(lines)==6145
        raw=Path('/tmp/SP30_fourth_pulse_domains_final.bin').read_bytes();witness=None
    else:
        assert run.returncode==41 and lines[-1]['abstract_GF_unresolved'],(run.returncode,run.stderr)
        summary=None;witness=lines.pop();raw=Path('/tmp/SP28_info_factor_2048_mode94_unresolved_'+str(witness['offset'])+'.bin').read_bytes()
    N=262144;assert len(raw)==11*N
    arrays=dict(native=np.frombuffer(raw,np.uint8,8*N).reshape(8,N).copy(),
        code=np.frombuffer(raw,np.uint16,N,8*N).copy(),Info=np.frombuffer(raw,np.uint8,N,10*N).copy())
    asset=OUT/'SP30_fourth_pulse_domain_states.npz';np.savez_compressed(asset,**arrays)
    quiet=False;endpoint=None;tracks=None
    if complete:
        row=lines[-1];left,right=row['left'],row['right_exclusive'];x=np.arange(N)
        quiet=row['holes_in_support_hull']==0 and (left+512)%1024==0 and right%1024==0 and \
            not arrays['native'][[2,3,4,6,7]].any() and not arrays['code'].any() and \
            np.array_equal(arrays['native'][1],((left-512<=x)&(x<left))|((right-512<=x)&(x<right)))
        endpoint=dict(wrong_GF_interval=[left,right],width=right-left,width_decrease=10752-(right-left),
            native_quiet_template=bool(quiet),template_L_R=[(left+512)//1024,right//1024])
        tracks={str(p):dict(known_one_colonies=np.flatnonzero(arrays['Info'][p::1024]==1).tolist(),
            unknown_colonies=np.flatnonzero(arrays['Info'][p::1024]==2).tolist()) for p in (509,1021)}
    r=dict(proposal='SP30',scope='Prepared fourth-signal enclosure, sound domain only; actual source/store bridge and Z lift need separate proof',
        Q=1024,U=475136,T_wf=278401,force_duration=2048,pulse_updates=6144,
        initial_native_template_L_R=[110,120],initial_wrong_GF_interval=[112128,122880],
        seed_interval=[105*1024,154*1024],final_protected_interval=[105*1024-8*6145-37,154*1024+8*6145+37],
        optional_bit_count=result['optional_bit_count'],concrete_enclosure_masks=result['concrete_enclosure_masks'],
        finite_domain_recurrence_complete=complete,exit_code=run.returncode,rows_checked=len(lines),
        all6144_GF_selections_determined=complete,first_unresolved_GF=witness,summary=summary,
        endpoint=endpoint,retained_Info_tracks=tracks,
        final_or_unresolved_unknown_native_domain_sites=int((arrays['native']==2).sum()),
        final_or_unresolved_unknown_Info_domain_sites=int((arrays['Info']==2).sum()),
        checker_sha256=digest(__file__),enclosure_receipt_sha256=digest(probe_path),
        inherited_domain_factor_sha256=digest(OUT/'SP29_third_pulse_domains_factor_generated.c'),
        inherited_domain_wrapper_sha256=digest(parent),generated_wrapper_sha256=digest(wrapper),
        executable_sha256=digest(exe),run_log_sha256=digest(log),endpoint_asset_sha256=digest(asset),
        stderr_sha256=digest(OUT/'SP30_fourth_pulse_domains_stderr.log'),
        actual_fourth_signal_or_pulse_on_Z_proved_by_this_probe=False,
        arbitrary_defect_eroder_or_higher_error_map_or_iid_threshold_proved=False,
        numerical_whole_CA_trajectory_used=False,additional_rule_programme_or_constant_change=False,
        active_G17_modified=False,global_reliability_established=False,seconds=time.monotonic()-started)
    (OUT/'SP30_fourth_pulse_domain_probe.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(dict(complete=complete,endpoint=endpoint,retained_Info_tracks=tracks,first_unresolved_GF=witness,
        seconds=r['seconds'],actual_fourth_signal_or_pulse_on_Z_proved=False)),flush=True)


if __name__=='__main__':main()
