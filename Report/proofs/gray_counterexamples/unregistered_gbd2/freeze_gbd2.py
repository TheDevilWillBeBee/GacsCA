"""Freeze GBD2 and preserve the exact accepted GBD1/GBD0 chain."""
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
DATA=ROOT/'figs/gray_counterexamples/unregistered_gbd2'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    old=ROOT/'figs/gray_counterexamples/unregistered_gbd1/GBD1_manifest.json'
    om=json.loads(old.read_text());assets=dict(om['assets'])
    for path,h in assets.items():assert sha(ROOT/path)==h,(path,'old asset changed')
    added=[old,
      ROOT/'figs/gray_counterexamples/unregistered_gbd1/GBD1_readonly_own_validation01.json',
      ROOT/'figs/gray_counterexamples/unregistered_gbd1/GBD1_readonly_own_replay01.log']
    for base in (HERE,DATA):
        added.extend(p for p in base.iterdir() if p.is_file() and
                     p.name!='GBD2_manifest.json' and
                     not p.name.startswith('GBD2_readonly'))
    for p in added:assets[str(p.relative_to(ROOT))]=sha(p)
    r=json.loads((DATA/'GBD2_certificate_attempt02.json').read_text())
    assert r['passed'] and r['conditional_quiet_coherent_packing']
    assert r['literal_seed_updates']==r['literal_chunk_load_updates']==3262
    assert r['literal_merge_updates']==61978
    assert r['complete_transport_rows']==3098
    m=dict(schema='GBD2 literal packing component v1',assets=assets,
           inherited_manifest=str(old.relative_to(ROOT)),
           inherited_replay='figs/gray_counterexamples/unregistered_gbd1/GBD1_readonly_own_validation01.json',
           receipt='figs/gray_counterexamples/unregistered_gbd2/GBD2_certificate_attempt02.json',
           Q=8192,U=1048576,lambda_=24,c=104,
           conditional_quiet_coherent_packing=True,
           native_ports_are_explicit_premise=True,
           block_radius=5,K=3262,chunks=164,done_age=592945,
           old_sources_unchanged=True,actual_slot_accesses=True,
           full_rule=False,own_beta=False,autonomous_gathers=False,
           full_execution_runtime=False,physical_period=False,
           faithful_Gray=False,gray_refutation=False,iid_failure=False,shorter_U=False)
    out=DATA/'GBD2_manifest.json'
    out.write_text(json.dumps(m,indent=2)+'\n')
    print(json.dumps(dict(passed=True,assets=len(assets),manifest_sha256=sha(out)),indent=2))

if __name__=='__main__':main()
