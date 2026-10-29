#!/usr/bin/env python3
"""Sound three-valued experiment for the thirteen-bit third pulse.

Flags/Info domains are0/1/2(unknown). Native GF/header/code stay exact;
the experiment stops and records a witness if GF becomes undetermined.
All-mask physical/Z lifts still require a separate written proof/checker.
"""
from pathlib import Path
import hashlib,json,subprocess,time
import numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'figs/robustness'


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


TRI_FLAGS=r'''
/* 0={0},1={1},2={0,1}. Every operation encloses its concrete images. */
static int tri_not(int a){return a==2?2:!a;}
static int tri_and(int a,int b){return a==0||b==0?0:a==1?b:b==1?a:2;}
static int tri_or(int a,int b){return a==1||b==1?1:a==0?b:b==0?a:2;}
static int tri_mux(int c,int a,int b){return c==0?b:c==1?a:a==b?a:2;}
static int tri_ge(int low,int high,int threshold){return low>=threshold?1:high<threshold?0:2;}
static void add_domain(int a,int *low,int *high){*low+=a==1;*high+=a!=0;}

static void flags(int x,int right,int force,int *f1,int *f2){
    int phase=(x+512*right)&(Q-1),mismatch=0,wf2=0;
    int rlo=0,rhi=0,qlo=0,qhi=0,llo=0,lhi=0,ilo=0,ihi=0,wlo=0,whi=0;
    for(int d=1;d<=5;d++){
        if(d<=phase){mismatch+=get(refined,x-d)!=right;add_domain(get(state[F2],x-d),&ilo,&ihi);}
        add_domain(get(state[F2],x-d),&llo,&lhi);
        if(get(refined,x+d)==right)add_domain(tri_not(get(state[F1],x+d)),&qlo,&qhi);
    }
    for(int d=1;d<=8;d++)if(phase+d<Q)add_domain(get(state[F1],x+d),&rlo,&rhi);
    for(int d=-5;d<=5;d++)if(0<=phase+d && phase+d<Q){
        add_domain(get(state[WF1],x+d),&wlo,&whi);wf2+=get(state[PV],x+d);
    }
    *f1=tri_or(mismatch>=3,tri_or(tri_ge(wlo,whi,3),tri_or(tri_ge(rlo,rhi,3),
         tri_or(tri_and(state[F1][x],tri_ge(rlo,rhi,2)),phase<Q-5?tri_not(tri_ge(qlo,qhi,3)):0))));
    int on=tri_or(tri_ge(ilo,ihi,4),tri_and(*f1,tri_ge(llo,lhi,4)));
    int erase=tri_or(tri_and(tri_not(*f1),tri_not(tri_ge(ilo,ihi,2))),
                     tri_and(*f1,tri_not(tri_ge(llo,lhi,1))));
    *f2=tri_or(tri_mux(state[F2][x],tri_not(erase),on),wf2>=3||force);
}
'''


def main():
    begin=time.monotonic();factor=OUT/'SP29_refined_wipe_factor_generated.c'
    source=factor.read_text();a=source.index('static void flags(');b=source.index('static void step(',a)
    source=source[:a]+TRI_FLAGS+'\n'+source[b:]
    changes={
        '        int selected=(!f1 || f2)?right:left;':r'''        int choice=tri_or(tri_not(f1),f2);
        if(choice==2 && right!=left){
            printf("{\"abstract_GF_unresolved\":true,\"offset\":%d,\"x\":%d,\"right\":%d,\"left\":%d,\"new_Flag1_domain\":%d,\"new_Flag2_domain\":%d}\n",offset,x,right,left,f1,f2);
            fflush(stdout);save("unresolved",offset);exit(41);
        }
        int selected=choice==2?right:choice?right:left;''',
        '        next[WF1][x]=output_address>=Q-5 && offset<2*Q && info[primary];':
            '        next[WF1][x]=(output_address>=Q-5 && offset<2*Q)?info[primary]:0;'}
    for old,new in changes.items():assert source.count(old)==1,old;source=source.replace(old,new)
    a=source.index('        int keeps=0,oldkeeps=0;');b=source.index('\n    }\n    memcpy(state,next',a)
    source=source[:a]+r'''        int klo=0,khi=0;
        for(int s=-2;s<=2;s++){
            int x=(y-s)&MASK;
            int keep=tri_not(tri_and(next[F1][x],next[LABEL][x]!=refined[x]));
            add_domain(keep,&klo,&khi);
        }
        newinfo[y]=tri_and(info[y],tri_ge(klo,khi,3));'''+source[b:]
    generated_factor=OUT/'SP29_third_pulse_domains_factor_generated.c';generated_factor.write_text(source)
    prior=OUT/'SP29_third_pulse_corners_generated.c';wrapper=prior.read_text()
    changes={
        '#include "SP29_refined_wipe_factor_generated.c"':'#include "SP29_third_pulse_domains_factor_generated.c"',
        'assert(state[LABEL][x]<=1 && state[PT][x]<16 && info[x]<=1);':'assert(state[LABEL][x]<=1 && state[PT][x]<16 && info[x]<=2);',
        'if(p!=PT)assert(state[p][x]<=1);':'if(p==F1||p==F2||p==WF1)assert(state[p][x]<=2);else if(p!=PT)assert(state[p][x]<=1);',
        '"/tmp/SP29_third_pulse_corner%d_final.bin",case_mask':'"/tmp/SP29_third_pulse_domains_final.bin"',
        'case_mask=atoi(argv[1]);duration=2*Q;info_mode=4+case_mask;':'case_mask=atoi(argv[1]);duration=2*Q;info_mode=90;',
        'if(case_mask<0 || case_mask>8191)return 2;':'if(case_mask!=0)return 2;'}
    for old,new in changes.items():assert wrapper.count(old)==1,old;wrapper=wrapper.replace(old,new)
    a=wrapper.index('        info[x]=(residue==509');b=wrapper.index('\n    }\n    certify_row(0);',a)
    wrapper=wrapper[:a]+r'''        int fixed=(residue==509 && 116<=col && col<=127) ||
            (residue==1021 && (112<=col && col<=114 || 128<=col && col<=135 || 141<=col && col<=144));
        int uncertain=(residue==509 && col==115) || (residue==1021 &&
            (col==111 || 136<=col && col<=140 || 145<=col && col<=149 || col==127));
        assert(!(fixed && uncertain));info[x]=uncertain?2:fixed;
'''+wrapper[b:]
    generated_wrapper=OUT/'SP29_third_pulse_domains_generated.c';generated_wrapper.write_text(wrapper)
    exe=Path('/tmp/SP29_third_pulse_domains_certificate')
    compile_result=subprocess.run(['cc','-O3','-std=c11','-Wall','-Wextra','-Werror','-Wno-parentheses',str(generated_wrapper),'-o',str(exe)],capture_output=True,text=True)
    (OUT/'SP29_third_pulse_domains_compile.log').write_text(compile_result.stdout+compile_result.stderr)
    assert compile_result.returncode==0,compile_result.stderr
    log=OUT/'SP29_third_pulse_domains.jsonl'
    with log.open('w') as stream:r=subprocess.run([str(exe),'0'],stdout=stream,stderr=subprocess.PIPE,text=True)
    stderr=OUT/'SP29_third_pulse_domains_stderr.log';stderr.write_text(r.stderr)
    lines=[json.loads(line) for line in log.read_text().splitlines()];complete=r.returncode==0
    arrays={};final=None;summary=None;unknown_counts=None;corners_enclosed=None;quiet=False
    if complete:
        summary=lines.pop();assert summary['certificate_complete'] and summary['rows_checked']==len(lines)==6145
        raw=Path('/tmp/SP29_third_pulse_domains_final.bin').read_bytes();N=262144;assert len(raw)==11*N
        arrays['native']=np.frombuffer(raw,np.uint8,8*N).reshape(8,N).copy()
        arrays['code']=np.frombuffer(raw,np.uint16,N,8*N).copy();arrays['Info']=np.frombuffer(raw,np.uint8,N,10*N).copy()
        unknown_counts=dict(native=int((arrays['native']==2).sum()),Info=int((arrays['Info']==2).sum()))
        final=lines[-1];a,b=final['left'],final['right_exclusive'];x=np.arange(N)
        expected=((a-512<=x)&(x<a))|((b-512<=x)&(x<b))
        quiet=final['holes_in_support_hull']==0 and (a+512)%1024==0 and b%1024==0 and \
            not arrays['native'][[2,3,4,6,7]].any() and not arrays['code'].any() and np.array_equal(arrays['native'][1],expected)
        with np.load(OUT/'SP29_third_pulse_corner_final_states.npz',allow_pickle=False) as concrete:
            corners_enclosed=all(np.all((domain==2)|(domain==concrete[f'case{mask}_{name}']))
                for mask in (0,8191) for name,domain in arrays.items())
        assert corners_enclosed
    else:
        assert r.returncode==41 and lines[-1]['abstract_GF_unresolved'],(r.returncode,r.stderr)
        raw=Path('/tmp/SP28_info_factor_2048_mode90_unresolved_'+str(lines[-1]['offset'])+'.bin').read_bytes()
        N=262144;assert len(raw)==11*N
        arrays['native']=np.frombuffer(raw,np.uint8,8*N).reshape(8,N).copy()
        arrays['code']=np.frombuffer(raw,np.uint16,N,8*N).copy();arrays['Info']=np.frombuffer(raw,np.uint8,N,10*N).copy()
    asset=OUT/'SP29_third_pulse_domain_states.npz';np.savez_compressed(asset,**arrays)
    receipt=dict(proposal='SP29',scope='Sound-domain finite study of all thirteen unspecified third-signal bits; physical/Z theorem requires separate proof',
        Q=1024,U=475136,T_wf=278401,force_duration=2048,domain_values={'0':[0],'1':[1],'2':[0,1]},
        full_concrete_mask_count=8192,domains_do_not_assume_input_independence=True,
        native_GF_and_header_code_values_exact_required=True,abstract_GF_undetermined_stops_run=True,
        finite_domain_recurrence_complete=complete,exit_code=r.returncode,rows_checked=len(lines) if complete else len(lines)-1,
        all_6144_steps_GF_determined=complete,final=final,summary=summary,final_unknown_domain_counts=unknown_counts,
        native_quiet_template_final=bool(quiet),two_concrete_corner_endpoints_enclosed=corners_enclosed,
        first_unresolved_GF=None if complete else lines[-1],
        actual_third_pulse_on_Z_proved_by_this_probe=False,general_eroder_higher_map_or_positive_iid_rate_proved=False,
        global_reliability_established=False,active_G17_modified=False,rule_programme_or_constant_change=False,
        checker_sha256=digest(__file__),inherited_corrected_factor_sha256=digest(factor),inherited_corner_wrapper_sha256=digest(prior),
        generated_domain_factor_sha256=digest(generated_factor),generated_domain_wrapper_sha256=digest(generated_wrapper),
        C_executable_sha256=digest(exe),run_log_name=log.name,run_log_sha256=digest(log),
        stderr_log_sha256=digest(stderr),final_or_unresolved_state_asset_sha256=digest(asset),
        receipt_dependencies_sha256={name:digest(OUT/name) for name in ('SP29_recovered_right_retained_certificate.json','SP29_third_pulse_corner_probe.json')},
        seconds=time.monotonic()-begin)
    (OUT/'SP29_third_pulse_domain_probe.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(complete=complete,final=final,unknown_counts=unknown_counts,first_unresolved_GF=receipt['first_unresolved_GF'],
        seconds=receipt['seconds'],actual_third_pulse_on_Z_proved_by_this_probe=False)),flush=True)


if __name__=='__main__':main()
