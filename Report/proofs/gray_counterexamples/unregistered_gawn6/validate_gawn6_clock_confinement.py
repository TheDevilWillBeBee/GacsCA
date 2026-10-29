#!/usr/bin/env python3
"""Freeze and read-only replay GAWN6; no inherited asset is written."""
from pathlib import Path
import argparse,hashlib,json,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE))
from check_gawn6_clock_confinement import compute
FIG=ROOT/'figs/gray_counterexamples/unregistered_gawn6'
BASE=ROOT/'figs/gray_counterexamples/unregistered_gawn5/GAWN5_standalone_assets.json'
MANIFEST=FIG/'GAWN6_standalone_assets.json'
RECEIPT=FIG/'GAWN6_clock_confinement_certificate.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--issue',action='store_true');args=parser.parse_args()
    started=time.monotonic();d=json.loads(RECEIPT.read_text())
    assert d['passed'] and (d['Q'],d['U'],d['lambda_original'],d['error_separation'])==(4096,524288,24,104)
    assert d['Age_damage_confined_to_true_colony0_proved']
    assert d['conditional_complete2U_reduction_for_only_Age_flags_Info_replacements_proved']
    for key in ('universal_native_quiet_deadline_proved','any_new_quiet_trajectory_measured',
        'complete2U_physical_simulation','GF_changing_E0_surroundings_higher_iid',
        'Gray_G17_counterexample_or_global_minimal_change','rule_ROM_constants_G17_changed'):
        assert not d[key],key
    for path,value in d['source_sha256'].items():assert sha(ROOT/path)==value,path
    inherited=json.loads(BASE.read_text())['assets_sha256']
    for path,value in inherited.items():assert sha(ROOT/path)==value,path
    if args.issue:
        assets=dict(inherited)
        for p in [BASE,RECEIPT,ROOT/'figs/robustness/GAWN6_initial_cofactor_run01.log']+list(HERE.glob('*.py'))+list(HERE.glob('*.md')):
            assets[str(p.relative_to(ROOT))]=sha(p)
        m=dict(name='GAWN6 universal canonical-Address exterior and conditional repair',
            assets_sha256=dict(sorted(assets.items())),inherited_assets=len(inherited),
            universal_native_confinement=True,complete2U_repair_conditional_on_native_quiet=True,
            universal_native_termination=False,complete2U_physical_simulation=False,
            rule_ROM_constants_G17_changed=False)
        MANIFEST.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
        print(json.dumps(dict(issued=True,assets=len(assets),inherited_assets=len(inherited),
            manifest_sha256=sha(MANIFEST))),flush=True);return
    m=json.loads(MANIFEST.read_text())
    for path,value in m['assets_sha256'].items():assert sha(ROOT/path)==value,path
    assert compute()==d,'finite cofactor/kernel replay differs'
    for path,value in m['assets_sha256'].items():assert sha(ROOT/path)==value,path
    print(json.dumps(dict(passed=True,readonly=True,assets=len(m['assets_sha256']),
        inherited_assets=m['inherited_assets'],all_new_cofactors_kernel_checks_recomputed=True,
        certificate_sha256=sha(RECEIPT),manifest_sha256=sha(MANIFEST),
        universal_native_confinement=True,complete2U_reduction_conditional=True,
        universal_native_termination=False,full_reliability=False,
        rule_ROM_constants_G17_changed=False,elapsed=time.monotonic()-started)),flush=True)
if __name__=='__main__':main()
