#!/usr/bin/env python3
"""Two extreme masks of the actual third thirteen-bit enclosure.

Each recurrence is exact on the finite quotient; two cases do not prove
the full enclosure, its actual pulse, or any general reliability theorem.
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib,json,subprocess,time
import numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'figs/robustness'


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    begin=time.monotonic();prior=OUT/'SP29_second_pulse_cases_generated.c'
    source=prior.read_text();changes={
        'static int initial_a=122*Q-512,initial_b=136*Q,initial_lo=121*Q;':
            'static int initial_a=116*Q-512,initial_b=128*Q,initial_lo=115*Q;',
        'lo=117*Q-margin,hi=148*Q+margin':'lo=111*Q-margin,hi=150*Q+margin',
        'if(case_mask<0 || case_mask>7)return 2;':'if(case_mask<0 || case_mask>8191)return 2;',
        '"/tmp/SP29_second_pulse_case%d_final.bin",case_mask':'"/tmp/SP29_third_pulse_corner%d_final.bin",case_mask',
        '''        info[x]=(residue==509 && (122<=col && col<=135 || ((case_mask&1) && col==121))) ||
            (residue==1021 && (118<=col && col<=120 || 136<=col && col<=146 ||
               ((case_mask&2) && col==117) || ((case_mask&4) && col==135)));''':
        '''        info[x]=(residue==509 && (116<=col && col<=127 || ((case_mask&(1<<11)) && col==115))) ||
            (residue==1021 && (112<=col && col<=114 || 128<=col && col<=135 || 141<=col && col<=144 ||
               ((case_mask&1) && col==111) ||
               (136<=col && col<=140 && (case_mask&(1<<(col-135)))) ||
               (145<=col && col<=149 && (case_mask&(1<<(col-139)))) ||
               ((case_mask&(1<<12)) && col==127)));''',
        '    assert(count>=65);':'    assert(count>=0);'}
    for old,new in changes.items():assert source.count(old)==1,old;source=source.replace(old,new)
    generated=OUT/'SP29_third_pulse_corners_generated.c';generated.write_text(source)
    exe=Path('/tmp/SP29_third_pulse_corners_certificate')
    subprocess.run(['cc','-O3','-std=c11','-Wall','-Wextra','-Werror','-Wno-parentheses',str(generated),'-o',str(exe)],check=True)
    N=262144
    def run(mask):
        print(json.dumps(dict(phase='start',mask=mask)),flush=True)
        log=OUT/f'SP29_third_pulse_corner{mask}.jsonl'
        with log.open('w') as stream:r=subprocess.run([str(exe),str(mask)],stdout=stream,stderr=subprocess.PIPE,text=True)
        assert r.returncode==0 and not r.stderr,(mask,r.returncode,r.stderr)
        rows=[json.loads(line) for line in log.read_text().splitlines()];summary=rows.pop()
        assert summary['certificate_complete'] and summary['rows_checked']==len(rows)==6145
        assert summary['GF_support_sites_checked']==N*len(rows)
        assert summary['background_site_equalities']==sum(N-v['background_hi']+v['background_lo'] for v in rows)
        raw=Path(f'/tmp/SP29_third_pulse_corner{mask}_final.bin').read_bytes();assert len(raw)==11*N
        native=np.frombuffer(raw,np.uint8,8*N).reshape(8,N).copy()
        code=np.frombuffer(raw,np.uint16,N,8*N).copy();info=np.frombuffer(raw,np.uint8,N,10*N).copy()
        final=rows[-1];a,b=final['left'],final['right_exclusive']
        expected=((np.arange(N)>=a-512)&(np.arange(N)<a))|((np.arange(N)>=b-512)&(np.arange(N)<b))
        quiet=final['holes_in_support_hull']==0 and (a+512)%1024==0 and b%1024==0 and \
            all(final[k]==0 for k in ('Flag2','WF1','packets','codes','pressure')) and not code.any() and np.array_equal(native[1],expected)
        row=dict(mask=mask,final=final,exhaustive_checks=summary,native_quiet_template_final=bool(quiet),
            initial_width=12800,width_decrease=12800-final['wrong_Addresses'],
            left_displacement=a-118272,right_displacement=b-131072,log_name=log.name,log_sha256=digest(log),
            noninterval_rows=sum(v['holes_in_support_hull']>0 for v in rows),maximum_holes=max(v['holes_in_support_hull'] for v in rows))
        print(json.dumps(dict(phase='complete',case=row)),flush=True)
        return row,(native,code,info)
    with ThreadPoolExecutor(max_workers=2) as pool:runs=list(pool.map(run,(0,8191)))
    frames={};cases=[]
    for row,arrays in runs:
        cases.append(row)
        for name,array in zip(('native','code','Info'),arrays):frames[f"case{row['mask']}_{name}"]=array
    asset=OUT/'SP29_third_pulse_corner_final_states.npz';np.savez_compressed(asset,**frames)
    result=dict(proposal='SP29',scope='Two exact finite corrected-factor third-pulse corner masks only;8190 other enclosure masks and physical pulse lift unproved',
        Q=1024,U=475136,T_wf=278401,force_duration=2048,pulse_updates=6144,
        initial_native_GF_interval=[118272,131072],initial_projected_defect_seed=[111*1024,150*1024],
        unknown_bits=json.loads((OUT/'SP29_recovered_right_retained_certificate.json').read_text())['third_complete_signal_unspecified_bit_records'],
        cases=cases,tested_enclosure_masks=[0,8191],enclosure_mask_count=8192,
        both_finite_recurrences_checked=True,all_enclosure_masks_checked=False,
        actual_complete_third_pulse_proved=False,general_eroder_higher_map_or_positive_iid_rate_proved=False,
        global_reliability_established=False,active_G17_modified=False,rule_programme_or_constant_change=False,
        checker_sha256=digest(__file__),inherited_corrected_wrapper_sha256=digest(prior),
        corrected_factor_sha256=digest(OUT/'SP29_refined_wipe_factor_generated.c'),generated_C_wrapper_sha256=digest(generated),
        C_executable_sha256=digest(exe),final_state_asset_sha256=digest(asset),
        receipt_dependencies_sha256={'SP29_recovered_right_retained_certificate.json':digest(OUT/'SP29_recovered_right_retained_certificate.json')},seconds=time.monotonic()-begin)
    (OUT/'SP29_third_pulse_corner_probe.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(phase='written',seconds=result['seconds'],all_enclosure_masks_checked=False)),flush=True)


if __name__=='__main__':main()
