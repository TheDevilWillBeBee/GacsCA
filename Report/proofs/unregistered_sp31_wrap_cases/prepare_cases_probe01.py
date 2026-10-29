#!/usr/bin/env python3
"""Split the four formerly free core Flag2 alias votes; analysis only."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
OUT=ROOT/'figs/robustness/unregistered_sp31_wrap_cases'
parent=ROOT/'Report/proofs/unregistered_sp31_front_wrap_probe/sp31_wrap_probe01.c'
target=HERE/'sp31_wrap_cases01.c'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(parent)=='731030ed2717d78203dd5f98fd1f02c9b25953f80f8a444892339fb08f1d1481'
assert not target.exists();s=parent.read_text()
s=s.replace('if(argc<2||argc>6)return 1;','if(argc<2||argc>7)return 1;')
old='''    int R=155,L=R-nforeign;
'''
new='''    int commandMask=argc>6?atoi(argv[6]):-1;
    if(commandMask<-1||commandMask>15)return 1;
    int R=155,L=R-nforeign;
'''
assert s.count(old)==1;s=s.replace(old,new)
old='''        info[i]=free?2:fixed;
'''
new='''        info[i]=free?2:fixed;
        if(commandMask>=0&&p==515&&aa<=x&&x<bb){
            int bit=col-L+1;
            if(bit<0||bit>3)return 4;
            info[i]=(commandMask>>bit)&1;
        }
'''
assert s.count(old)==1;s=s.replace(old,new)
s=s.replace('sp31_wrap_probe_cofactor','sp31_wrap_cases_cofactor')
target.write_text(s);OUT.mkdir(parents=True,exist_ok=True)
r=dict(parent_sha256=sha(parent),source_sha256=sha(target),all_native_domain_equations_unchanged=True,
       four_core_MF515_votes_split_into16_analysis_classes=True,left_alias_commands_and_native_left_remain_free=True,
       status='exploratory finite disjunctive native factors; physical wrap sources/banks not yet proved',
       actual294U_or_later_physical_boundary_proved=False,all_time_or_eventual_higher_iid_or_minimum_proved=False,
       rule_ROM_constants_or_G17_changed=False,global_reliability_established=False)
(OUT/'preparation_receipt01.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
