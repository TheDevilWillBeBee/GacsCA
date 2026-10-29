#!/usr/bin/env python3
"""Create a separate fifth-pulse analysis; frozen F31 and parent stay fixed."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
OUT=ROOT/'figs/robustness/unregistered_sp31_fifth_ternary'
parent=ROOT/'Report/proofs/unregistered_sp31_fourth_ternary/sp31_fourth_ternary.c'
target=HERE/'sp31_fifth_ternary_probe01.c'
assert hashlib.sha256(parent.read_bytes()).hexdigest()=='7f499105ab6c88adc59f14c95f83c8818d2462895ab147acbb2ba1d6052aa7f6'
assert not target.exists()
text=parent.read_text()
old='''        a[0][i]=149*Q-512<=x&&x<152*Q;
        a[1][i]=(148*Q<=x&&x<149*Q-512)||(152*Q-512<=x&&x<152*Q);
        int fixed=(p==509&&149<=col&&col<=151)||(p==1021&&((106<=col&&col<=147)||(152<=col&&col<=154)));
        int free=(p==3&&132<=col&&col<=148)||(p==515&&148<=col&&col<=151);
'''
new='''        /* J251 actual fifth-source enclosure, with correlations enlarged.
         * Native F2 and both WF were reset and remain0 through the prefix. */
        a[0][i]=152*Q-512<=x&&x<155*Q?1:142*Q+1<=x&&x<152*Q-512?2:0;
        a[1][i]=155*Q-512<=x&&x<155*Q?1:142*Q-2<=x&&x<152*Q-512?2:0;
        int fixed=(p==509&&152<=col&&col<=154)||(p==1021&&((100<=col&&col<=139)||(155<=col&&col<=157)));
        int free=(p==509&&142<=col&&col<=151)||(p==1021&&140<=col&&col<=150)||(p==3&&133<=col&&col<=151)||(p==515&&142<=col&&col<=154);
'''
assert text.count(old)==1
text=text.replace(old,new).replace('sp31_fourth_ternary_cofactor','sp31_fifth_ternary_cofactor').replace('actual_fourth_endpoint_or_repair_proved','actual_fifth_endpoint_or_repair_proved')
target.write_text(text)
OUT.mkdir(parents=True,exist_ok=True)
receipt=dict(parent_analysis_sha256=hashlib.sha256(parent.read_bytes()).hexdigest(),
    new_analysis_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
    generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    source_proof='Report/proofs/unregistered_sp31_fourth_reset/SP31_FOURTH_RESET_FIFTH_SOURCES.md',
    free_fifth_votes=53,fixed_one_votes=46,native_F2_WF_reset_zero=True,
    concrete_free_assignment_reachability_or_independence=False,
    analysis_update_equations_unchanged=True,rule_ROM_constants_G17_modified=False,
    actual_fifth_pulse_or_higher_iid_reliability_proved=False)
(OUT/'preparation_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt),flush=True)
