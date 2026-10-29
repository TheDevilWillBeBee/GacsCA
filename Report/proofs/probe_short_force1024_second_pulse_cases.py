#!/usr/bin/env python3
"""Eight exact corrected-factor pulses from a proposed second-signal enclosure.

The enclosure's physical premises require a separate proof. Keep every
all-row certificate and endpoint even if shrinking/quieting fails.
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib,json,subprocess,time
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'figs/robustness'


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    start=time.monotonic();prior=ROOT/'Report/proofs/certify_info_native_shrinking_pulse.c'
    factor=OUT/'SP29_refined_wipe_factor_generated.c'
    source=prior.read_text()
    old='''    if(r==6*Q){
        assert(a==initial_a-6*Q && b==initial_b-8*Q && count==14848 && count==b-a);
        assert(flags[F1]==1024 && !flags[F2] && !flags[WF1] && !flags[PV] && !flags[CV] && !flags[BP]);
        assert(ones509==8 && ones1021==0);
        for(int x=0;x<N;x++){
            int expected_f1=(a-512<=x && x<a)||(b-512<=x && x<b);
            assert(state[F1][x]==expected_f1 && code[x]==0);
        }
    }
'''
    assert source.count(old)==1;source=source.replace(old,'')
    init='''        info[x]=(x&(Q-1))==509 && initial_a<=x && x<initial_b;'''
    assert source.count(init)==1
    source=source.replace(init,'''        int col=x/Q,residue=x&(Q-1);
        info[x]=(residue==509 && (122<=col && col<=135 || ((case_mask&1) && col==121))) ||
            (residue==1021 && (118<=col && col<=120 || 136<=col && col<=146 ||
               ((case_mask&2) && col==117) || ((case_mask&4) && col==135)));''')
    changes={
        '#include "native_address_info_factor.c"':'#include "SP29_refined_wipe_factor_generated.c"',
        'static int initial_a=128*Q-512,initial_b=144*Q,initial_lo=127*Q;':
            'static int initial_a=122*Q-512,initial_b=136*Q,initial_lo=121*Q;',
        'static int previous_a,previous_b;':'static int previous_a,previous_b,case_mask;',
        'lo=initial_lo-margin,hi=initial_b+margin':'lo=117*Q-margin,hi=148*Q+margin',
        'duration=atoi(argv[1]);info_mode=2;':'case_mask=atoi(argv[1]);duration=2*Q;info_mode=4+case_mask;',
        'if(duration!=Q && duration!=2*Q)return 2;':'if(case_mask<0 || case_mask>7)return 2;',
        '"/tmp/SP28_info_shrinking_pulse_%d_final.bin",duration':'"/tmp/SP29_second_pulse_case%d_final.bin",case_mask',
        '"\\\"background_site_equalities\\\":%llu,\\\"GF_support_sites_checked\\\":%llu}\\n",':
            '"\\\"background_site_equalities\\\":%llu,\\\"GF_support_sites_checked\\\":%llu,"\n'
            '           "\\\"refined_wipe_copy_mask_disagreements\\\":%llu,\\\"refined_wipe_active_majority_disagreements\\\":%llu}\\n",',
        '(unsigned long long)tested_GF_support_sites);':
            '(unsigned long long)tested_GF_support_sites,\n'
            '           (unsigned long long)refined_wipe_copy_mask_disagreements,\n'
            '           (unsigned long long)refined_wipe_active_majority_disagreements);'}
    for old,new in changes.items():
        assert source.count(old)==1,old;source=source.replace(old,new)
    generated=OUT/'SP29_second_pulse_cases_generated.c';generated.write_text(source)
    exe=Path('/tmp/SP29_second_pulse_cases_certificate')
    subprocess.run(['cc','-O3','-std=c11','-Wall','-Wextra','-Werror','-Wno-parentheses',str(generated),'-o',str(exe)],check=True)
    N=262144;frames={}
    def run(mask):
        log=OUT/f'SP29_second_pulse_case{mask}.jsonl'
        print(json.dumps(dict(phase='start',mask=mask)),flush=True)
        with log.open('w') as stream:
            process=subprocess.run([str(exe),str(mask)],stdout=stream,stderr=subprocess.PIPE,text=True)
        assert process.returncode==0 and not process.stderr,(mask,process.returncode,process.stderr)
        rows=[json.loads(line) for line in log.read_text().splitlines()];summary=rows.pop()
        assert summary['certificate_complete'] and summary['rows_checked']==len(rows)==6145
        assert summary['GF_support_sites_checked']==len(rows)*N
        assert summary['background_site_equalities']==sum(N-row['background_hi']+row['background_lo'] for row in rows)
        raw=Path(f'/tmp/SP29_second_pulse_case{mask}_final.bin').read_bytes();assert len(raw)==11*N
        native=np.frombuffer(raw,np.uint8,8*N).reshape(8,N).copy()
        code=np.frombuffer(raw,np.uint16,N,8*N).copy();info=np.frombuffer(raw,np.uint8,N,10*N).copy()
        final=rows[-1];a,b=final['left'],final['right_exclusive']
        qt=final['holes_in_support_hull']==0 and (a+512)%1024==0 and b%1024==0 and \
            all(final[key]==0 for key in ('Flag2','WF1','packets','codes','pressure')) and not code.any()
        expected_f1=((np.arange(N)>=a-512)&(np.arange(N)<a))|((np.arange(N)>=b-512)&(np.arange(N)<b))
        qt=bool(qt and np.array_equal(native[1],expected_f1))
        row=dict(mask=mask,initial_unknown_MF509_121=int(bool(mask&1)),
            initial_unknown_MF1021_117=int(bool(mask&2)),initial_unknown_MF1021_135=int(bool(mask&4)),
            final=final,exhaustive_checks=summary,native_quiet_template_final=qt,
            initial_width=14848,final_width=final['wrong_Addresses'],
            width_decrease=14848-final['wrong_Addresses'],
            left_displacement=a-124416,right_displacement=b-139264,
            log_name=log.name,log_sha256=digest(log),
            noninterval_rows=sum(r['holes_in_support_hull']>0 for r in rows),
            maximum_holes=max(r['holes_in_support_hull'] for r in rows))
        print(json.dumps(dict(phase='complete',case=row)),flush=True)
        return mask,row,(native,code,info)
    with ThreadPoolExecutor(max_workers=8) as pool:runs=list(pool.map(run,range(8)))
    cases=[]
    for mask,row,arrays in runs:
        cases.append(row)
        for suffix,array in zip(('native','code','Info'),arrays):frames[f'case{mask}_{suffix}']=array
    asset=OUT/'SP29_second_pulse_case_final_states.npz';np.savez_compressed(asset,**frames)
    result=dict(scope='Eight exact finite corrected-factor pulses from an algebraically proposed second-signal enclosure; physical enclosure and Z lift separate',
        Q=1024,U=475136,T_wf=278401,force_duration=2048,pulse_updates=6144,
        initial_native_GF_interval=[124416,139264],initial_MF509_ones=list(range(122,136)),
        initial_MF1021_fixed_ones=[118,119,120,*range(136,147)],
        unknown_bits=['MF509(121)','MF1021(117)','MF1021(135)'],cases=cases,
        all_eight_finite_recurrences_checked=True,
        all_eight_final_templates_quiet=all(c['native_quiet_template_final'] for c in cases),
        all_eight_final_widths_smaller=all(c['width_decrease']>0 for c in cases),
        actual_first_boundary_signal_enclosure_proved_by_this_probe=False,
        actual_second_pulse_proved_by_this_probe=False,general_eroder_or_iid_rate_proved=False,
        global_reliability_established=False,active_G17_modified=False,rule_programme_or_constant_change=False,
        checker_sha256=digest(__file__),inherited_wrapper_sha256=digest(prior),
        corrected_factor_sha256=digest(factor),generated_C_wrapper_sha256=digest(generated),
        C_executable_sha256=digest(exe),final_state_asset_sha256=digest(asset),seconds=time.monotonic()-start)
    (OUT/'SP29_second_pulse_case_probe.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(phase='written',seconds=result['seconds'],
                         all_eight_final_widths_smaller=result['all_eight_final_widths_smaller'])),flush=True)


if __name__=='__main__':main()
