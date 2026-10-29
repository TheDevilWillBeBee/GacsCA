#!/usr/bin/env python3
"""Freeze or read-only replay GAWN5's scoped native-clock checkpoint."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,tempfile,time
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FIG=ROOT/'figs/gray_counterexamples/unregistered_gawn5'
MANIFEST=FIG/'GAWN5_standalone_assets.json'
RECEIPT=FIG/'GAWN5_actual_clock_Info_probe.json'
BASE=ROOT/'figs/gray_counterexamples/unregistered_gawn4/GAWN4_late_SF_certificate.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def checks(d):
    assert d['passed'] and (d['Q'],d['U'],d['error_lambda'],d['error_separation'])==(4096,524288,24,104)
    assert d['flags_cases']==16 and d['width']==104 and d['actual_fault_row']==409602
    assert d['uniform_replacement_Age']==393215 and d['projection_horizon']==16384
    assert d['classification']['level1'] and d['classification']['level0']==0
    assert d['classification']['extent']==[104,1]
    assert d['actual_full_kernel_cofactor_checks']==420
    assert (d['maximum_Age_quiet'],d['maximum_all_native_quiet'])==(2566,4095)
    assert d['actual_current_GAWN2_native_Info_projection_proved_in_companion_text']
    assert d['complete_U_boundary_and_2U_repair_reduction_proved_under_native_history_hypotheses']
    for key in ('future_WF_externally_selected','full2U_physical_simulation_performed',
        'arbitrary_GF_changing_real1_or_continuing_higher_or_iid_proved',
        'full_SF_period_repair_or_decoder_proved','Gray_or_G17_counterexample','new_rule_or_constants_changed'):
        assert not d[key],key
    assert len(d['measured_cases'])==16
    assert all(r['status']==0 and r['min_age_x']==0 and r['max_age_x']<4096 for r in d['measured_cases'])
    assert d['measured_cases'][0]['max_age_count']==2799 and d['measured_cases'][0]['max_age_x']==4095
    assert max(r['source_updates'] for r in d['measured_cases'])==167
    for path,value in d['source_sha256'].items():assert sha(ROOT/path)==value,path
    assert sha(FIG/'gawn5_clock_info_projection.so')==d['library_sha256']
    for name,value in d['asset_sha256'].items():assert sha(FIG/name)==value,name
    initial=json.loads((FIG/'GAWN5_initial_clock_Info_probe.json').read_text())
    old_checker=initial['source_sha256']['Report/proofs/gray_counterexamples/unregistered_gawn5/check_gawn5_clock_info_projection.py']
    assert sha(FIG/'GAWN5_initial_checker.py.txt')==old_checker
    assert initial['measured_cases']==d['measured_cases']
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--issue',action='store_true');args=parser.parse_args()
    start=time.monotonic();d=json.loads(RECEIPT.read_text());checks(d)
    inherited=json.loads(BASE.read_text())['assets_sha256']
    for path,value in inherited.items():assert sha(ROOT/path)==value,path
    if args.issue:
        assets=dict(inherited);paths=[BASE]+list(HERE.glob('*.py'))+list(HERE.glob('*.c'))+list(HERE.glob('*.md'))
        paths += [ROOT/'figs/robustness/GAWN5_initial_projection_run01.log']
        paths += [p for p in FIG.iterdir() if p.is_file() and p!=MANIFEST and not p.name.startswith('GAWN5_readonly')]
        for p in paths:assets[str(p.relative_to(ROOT))]=sha(p)
        m=dict(name='GAWN5 frozen actual-source native-clock finite family and conditional physical reduction',
            assets_sha256=dict(sorted(assets.items())),inherited_assets=len(inherited),
            exact_closed_projection_and_full2U_reduction_conditional=True,
            sixteen_native_trajectories_measured=True,full2U_physical_simulation=False,
            arbitrary_real1_higher_iid=False,rule_ROM_constants_G17_unchanged=True)
        MANIFEST.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
        print(json.dumps(dict(issued=True,assets=len(assets),inherited_assets=len(inherited),manifest_sha256=sha(MANIFEST))),flush=True)
        return
    m=json.loads(MANIFEST.read_text())
    for path,value in m['assets_sha256'].items():assert sha(ROOT/path)==value,path
    with tempfile.TemporaryDirectory(prefix='gawn5_readonly_') as directory:
        fresh=Path(directory)
        subprocess.run([sys.executable,str(HERE/'check_gawn5_clock_info_projection.py'),
                        '--outdir',str(fresh)],check=True,cwd=ROOT)
        new=json.loads((fresh/RECEIPT.name).read_text());assert new==d,'new native checkpoint differs'
        for name in d['asset_sha256']:
            with np.load(FIG/name) as old,np.load(fresh/name) as replay:
                assert set(old.files)==set(replay.files)
                for key in old.files:assert np.array_equal(old[key],replay[key]),(name,key)
    for path,value in m['assets_sha256'].items():assert sha(ROOT/path)==value,path
    print(json.dumps(dict(passed=True,readonly=True,assets=len(m['assets_sha256']),
        inherited_assets=m['inherited_assets'],all_new_native_checks_recomputed=True,
        certificate_sha256=sha(RECEIPT),manifest_sha256=sha(MANIFEST),
        native_projection_and_full2U_reduction_conditional=True,
        all16_native_histories_measured=True,full2U_physical_simulation=False,
        general_real1_higher_iid=False,rule_ROM_constants_G17_changed=False,
        elapsed=time.monotonic()-start)),flush=True)
if __name__=='__main__':main()
