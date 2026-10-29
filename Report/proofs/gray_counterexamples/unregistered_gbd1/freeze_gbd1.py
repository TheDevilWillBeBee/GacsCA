"""Freeze the corrected component, preserving the original GBD0 claims."""
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
DATA=ROOT/'figs/gray_counterexamples/unregistered_gbd1'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    old=ROOT/'figs/gray_counterexamples/unregistered_gbd0/GBD0_manifest.json'
    om=json.loads(old.read_text());assets=dict(om['assets'])
    for path,h in assets.items():assert sha(ROOT/path)==h,(path,'old asset changed')
    added=[old,
      ROOT/'figs/gray_counterexamples/unregistered_gbd0/GBD0_readonly_own_validation01.json',
      ROOT/'figs/gray_counterexamples/unregistered_gbd0/GBD0_readonly_own_replay01.log']
    for base in (HERE,DATA):
        added.extend(p for p in base.iterdir() if p.is_file() and
                     p.name!='GBD1_manifest.json' and
                     not p.name.startswith('GBD1_readonly'))
    for p in added:assets[str(p.relative_to(ROOT))]=sha(p)
    r=json.loads((DATA/'GBD1_certificate_attempt01.json').read_text())
    assert r['passed'] and r['universal_matching_slot_formula']
    m=dict(schema='GBD1 corrected physical source ports v1',assets=assets,
           inherited_manifest=str(old.relative_to(ROOT)),
           inherited_replay='figs/gray_counterexamples/unregistered_gbd0/GBD0_readonly_own_validation01.json',
           receipt='figs/gray_counterexamples/unregistered_gbd1/GBD1_certificate_attempt01.json',
           correction_of_GBD0_single_payload_source_model=True,
           old_sources_unchanged=True,actual_inverse_slot=(0,4,3,2,1),
           universal_raw_source_identity=True,
           universal_data_identity=True,physical_stencil=(-7,8),
           full_rule=False,own_beta=False,actual_packing=False,
           universal_runtime=False,physical_period=False,
           faithful_Gray=False,gray_refutation=False,iid_failure=False,shorter_U=False)
    (DATA/'GBD1_manifest.json').write_text(json.dumps(m,indent=2)+'\n')
    print(json.dumps(dict(passed=True,assets=len(assets),
                        manifest_sha256=sha(DATA/'GBD1_manifest.json')),indent=2))

if __name__=='__main__':main()
