#!/usr/bin/env python3
"""New exploratory seeds for the frozen factor; never rewrite parent assets."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
OUT=ROOT/'figs/robustness/unregistered_sp31_front_wrap_probe'
parent=ROOT/'Report/proofs/unregistered_sp31_moving_front/sp31_moving_front_probe01.c'
target=HERE/'sp31_wrap_probe01.c'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(parent)=='95775503c8b7d4b1db67165fcd7280a5608f65249687fc86f3ba24206b7c7624'
assert not target.exists()
s=parent.read_text()
old='''    if(argc<2||argc>4)return 1;
    int ticks=argc>2?atoi(argv[2]):6144,stop_fixed=argc>3?atoi(argv[3]):0;
    if(ticks<1||ticks>196735||(stop_fixed!=0&&stop_fixed!=1))return 1;
'''
new='''    if(argc<2||argc>6)return 1;
    int ticks=argc>2?atoi(argv[2]):6144,stop_fixed=argc>3?atoi(argv[3]):0;
    int nforeign=argc>4?atoi(argv[4]):3,nright=argc>5?atoi(argv[5]):2;
    if(ticks<1||ticks>196735||(stop_fixed!=0&&stop_fixed!=1)||nforeign<1||nforeign>3||nright<0||nright>3)return 1;
    int R=155,L=R-nforeign;
'''
assert s.count(old)==1;s=s.replace(old,new)
s=s.replace('const int aa=152*Q-512,bb=155*Q;','const int aa=L*Q-512,bb=R*Q;')
s=s.replace('int fixed=(p==509&&152<=col&&col<=154)||(p==1021&&155<=col&&col<=157);',
            'int fixed=(p==509&&L<=col&&col<R)||(p==1021&&R<=col&&col<R+nright);')
s=s.replace('sp31_moving_front_cofactor','sp31_wrap_probe_cofactor')
target.write_text(s);OUT.mkdir(parents=True,exist_ok=True)
r=dict(parent_sha256=sha(parent),source_sha256=sha(target),native_algebra_unchanged=True,
       changed_analysis_seeds_only=True,default_foreign_ones=3,default_true_right_ones=2,
       status='exploratory factor seeds at excluded upper boundary; actual physical source/bank lift not proved',
       actual_after293U_physical_successor_proved=False,all_time_glider_eventual_repair_or_iid_proved=False,
       rule_ROM_constants_or_G17_changed=False,global_reliability_established=False)
(OUT/'preparation_receipt01.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
