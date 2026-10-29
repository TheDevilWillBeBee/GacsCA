#!/usr/bin/env python3
"""Freeze/read-only replay GAWN7 without modifying inherited assets."""
from pathlib import Path
import argparse,hashlib,json,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE))
from check_gawn7_flag_clock_reduction import compute
FIG=ROOT/'figs/gray_counterexamples/unregistered_gawn7'
BASE=ROOT/'figs/gray_counterexamples/unregistered_gawn6/GAWN6_standalone_assets.json'
MANIFEST=FIG/'GAWN7_standalone_assets.json';RECEIPT=FIG/'GAWN7_flag_clock_certificate.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--issue',action='store_true');args=parser.parse_args()
    started=time.monotonic();d=json.loads(RECEIPT.read_text())
    assert d['passed'] and (d['Q'],d['U'],d['lambda_original'],d['error_separation'])==(4096,524288,24,104)
    assert (d['universal_Workspace_zero_row'],d['universal_Flag2_zero_row'])==(8193,12289)
    assert (d['conditional_full_native_quiet_row'],d['margin_before4Q'])==(15701,683)
    assert d['correct_first5_actual_raw_clocks_at_T_plus_3Q_plus1_REQUIRED']
    assert d['conditional_complete2U_for_only_Age_flags_Info_faults']
    for key in ('first5_clock_premise_for_every_payload_proved','universal_full_native_quiet_deadline_proved',
        'new_native_quiet_trajectory_or_full2U_simulation','GF_changing_E0_surroundings_higher_iid',
        'faithful_Gray_G17_refutation_or_minimum','rule_ROM_constants_G17_changed'):
        assert not d[key],key
    for path,value in d['source_sha256'].items():assert sha(ROOT/path)==value,path
    inherited=json.loads(BASE.read_text())['assets_sha256']
    for path,value in inherited.items():assert sha(ROOT/path)==value,path
    if args.issue:
        assets=dict(inherited)
        paths=[BASE,RECEIPT,ROOT/'figs/robustness/GAWN7_initial_cofactor_run01.log',
            ROOT/'figs/robustness/GAWN7_final_cofactor_run01.log',
            ROOT/'figs/robustness/GAWN7_final_cofactor_run02.log']
        paths+=list(HERE.glob('*.py'))+list(HERE.glob('*.md'))
        for path in paths:assets[str(path.relative_to(ROOT))]=sha(path)
        m=dict(name='GAWN7 universal field deadlines and conditional first-five-clock native reduction',
            assets_sha256=dict(sorted(assets.items())),inherited_assets=len(inherited),
            Workspace_Flag2_deadlines_and_bulk_identity_proved=True,
            first5_clock_premise_unproved=True,complete2U_repair_conditional=True,
            universal_native_termination=False,rule_ROM_constants_G17_changed=False)
        MANIFEST.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
        print(json.dumps(dict(issued=True,assets=len(assets),inherited_assets=len(inherited),
            manifest_sha256=sha(MANIFEST))),flush=True);return
    m=json.loads(MANIFEST.read_text())
    for path,value in m['assets_sha256'].items():assert sha(ROOT/path)==value,path
    assert compute()==d,'new cofactor/prefix supplements differ'
    for path,value in m['assets_sha256'].items():assert sha(ROOT/path)==value,path
    print(json.dumps(dict(passed=True,readonly=True,assets=len(m['assets_sha256']),
        inherited_assets=m['inherited_assets'],all_new_native_kernel_checks_recomputed=True,
        certificate_sha256=sha(RECEIPT),manifest_sha256=sha(MANIFEST),
        universal_Workspace_Flag2_deadlines=True,conditional_native_quiet=15701,
        first5_clock_premise_unproved=True,full_reliability=False,
        rule_ROM_constants_G17_changed=False,elapsed=time.monotonic()-started)),flush=True)
if __name__=='__main__':main()
