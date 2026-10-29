#!/usr/bin/env python3
"""Separate maximal-left-domain moving-front probe, not a new CA."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
OUT=ROOT/'figs/robustness/unregistered_sp31_moving_front'
parent=ROOT/'Report/proofs/unregistered_sp31_fifth_ternary/sp31_fifth_ternary_probe01.c'
target=HERE/'sp31_moving_front_probe01.c'
assert hashlib.sha256(parent.read_bytes()).hexdigest()=='88fdc5610ce2ab8c8cfcad03f6b76da8f23fd16afaa4cc78f5beb19fa30aedc9'
assert not target.exists()
s=parent.read_text()
old='''        /* J251 actual fifth-source enclosure, with correlations enlarged.
         * Native F2 and both WF were reset and remain0 through the prefix. */
        a[0][i]=152*Q-512<=x&&x<155*Q?1:142*Q+1<=x&&x<152*Q-512?2:0;
        a[1][i]=155*Q-512<=x&&x<155*Q?1:142*Q-2<=x&&x<152*Q-512?2:0;
        int fixed=(p==509&&152<=col&&col<=154)||(p==1021&&((100<=col&&col<=139)||(155<=col&&col<=157)));
        int free=(p==509&&142<=col&&col<=151)||(p==1021&&140<=col&&col<=150)||(p==3&&133<=col&&col<=151)||(p==515&&142<=col&&col<=154);
'''
new='''        /* Proposed generic front: all binary GF/F1 and alias commands
         * to the left are unknown. Native F2/WF start reset0. */
        const int aa=152*Q-512,bb=155*Q;
        a[0][i]=x<aa?2:x<bb?1:0;
        a[1][i]=x<aa?2:bb-512<=x&&x<bb?1:0;
        int alias=p==3||p==509||p==515||p==1021;
        int fixed=(p==509&&152<=col&&col<=154)||(p==1021&&155<=col&&col<=157);
        int free=alias&&(x<aa||(p==515&&aa<=x&&x<bb));
'''
assert s.count(old)==1;s=s.replace(old,new)
old='if(i<2*BORDER||i>=NX-2*BORDER)'
assert s.count(old)==1;s=s.replace(old,'if(i>=NX-2*BORDER)')
old='''        for(int i=0;i<BORDER;i++)keep[i]=keep[NX-1-i]=1;
'''
new='''        /* Omitted left cells are unknown domains, not forced repairs.
         * They contain every concrete left continuation. Right cells0
         * are justified only by the checked canonical exterior guard. */
        for(int i=0;i<BORDER;i++){
            keep[i]=2;keep[NX-1-i]=1;
            for(int j=0;j<5;j++)b[j][i]=(j==2||j==4)&&t>=2*Q?0:2;
        }
'''
assert s.count(old)==1;s=s.replace(old,new)
old='''        int same=t>=2*Q&&!memcmp(a,b,sizeof(a));
'''
new='''        for(int i=0;i<BORDER;i++)nextinfo[i]=2;
        int same=t>=2*Q&&!memcmp(a,b,sizeof(a));
'''
assert s.count(old)==1;s=s.replace(old,new)
s=s.replace('sp31_fifth_ternary_cofactor','sp31_moving_front_cofactor')
target.write_text(s);OUT.mkdir(parents=True,exist_ok=True)
r=dict(parent_sha256=hashlib.sha256(parent.read_bytes()).hexdigest(),source_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
    maximal_left_domains=True,proposed_front=[152*1024-512,155*1024],native_F2_WF_reset_zero=True,
    fixed_commands='MF509152..154/MF1021155..157; leftaliases free andcoreMF515free',
    omitted_left_cells_top_domains=True,right_exterior_guard_checked_each_row=True,
    status='exploratory generic factor analysis; physical replenishment and universal soundness not yet registered',
    rule_ROM_constants_G17_changed=False,all_time_repair_or_failure_proved=False,global_reliability_established=False)
(OUT/'preparation_receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
