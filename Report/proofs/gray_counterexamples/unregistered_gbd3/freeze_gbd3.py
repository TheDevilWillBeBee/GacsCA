"""Pin GBD3 and the unchanged accepted GBD2/1/0 provenance chain."""
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
DATA=ROOT/'figs/gray_counterexamples/unregistered_gbd3'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    old=ROOT/'figs/gray_counterexamples/unregistered_gbd2/GBD2_manifest.json'
    om=json.loads(old.read_text());assets=dict(om['assets'])
    for path,h in assets.items():assert sha(ROOT/path)==h,(path,'inherited asset changed')
    inherited_replays=[ROOT/'figs/gray_counterexamples/unregistered_gbd2'/name for name in
        ('GBD2_readonly_own_validation01.json','GBD2_parent_readonly_validation.json')]
    for path in inherited_replays:
        r=json.loads(path.read_text())
        assert r['passed'] and r['hashes_unchanged'] and r['manifest_sha256']==sha(old)
    added=[old,*inherited_replays,
           ROOT/'figs/gray_counterexamples/unregistered_gbd2/GBD2_readonly_own_replay01.log',
           ROOT/'figs/robustness/GBD2_parent_readonly_run01.log']
    for base in (HERE,DATA):
        added.extend(p for p in base.iterdir() if p.is_file() and
                     p.name!='GBD3_manifest.json' and not p.name.startswith('GBD3_readonly'))
    for p in added:assets[str(p.relative_to(ROOT))]=sha(p)
    receipts=dict(controller=DATA/'GBD3_certificate_attempt06.json',
                  packing=DATA/'GBD3_packing_certificate_attempt01.json',
                  binding=DATA/'GBD3_binding_certificate_attempt01.json')
    for receipt in receipts.values():
        r=json.loads(receipt.read_text());assert r['passed']
        for path,h in r['source_hashes'].items():assert sha(ROOT/path)==h
    c=json.loads(receipts['controller'].read_text())
    p=json.loads(receipts['packing'].read_text())
    b=json.loads(receipts['binding'].read_text())
    assert c['Head_bits']==204 and c['proposed_total_K']==3387
    assert p['K']==3387 and p['chunks']==170 and p['max_travel']==3217
    assert b['actual_new_K_packing'] and b['literal_computed_port_reset_birth']
    m=dict(schema='GBD3 counted finite controller and fresh packing component v1',
        assets=assets,inherited_manifest=str(old.relative_to(ROOT)),
        inherited_replays=[str(p.relative_to(ROOT)) for p in inherited_replays],
        receipts={name:str(p.relative_to(ROOT)) for name,p in receipts.items()},
        radius_witness='figs/gray_counterexamples/unregistered_gbd3/GBD3_one_sided20_radius_witness_attempt06.json',
        Q=8192,U=1048576,lambda_=24,c=104,Head_bits=204,K=3387,twoK=6774,
        chunks=170,packed_by_computed_port_age=593064,
        balanced_component_radius=7,alternative_one_sided16_radius=8,
        rejected_one_sided20_stipulated_radius=9,
        FGET_bits=140,FPUT_bits=137,helper_caller_bits=396,
        actual_lower_backup_and_upper_SF_votes_distinguished=True,
        actual_new_K_packing=True,conditional_computed_port_reset_birth=True,
        conditional_helper_register_liveness=True,
        native_ports_and_History_origins_are_premises=True,
        complete_own_beta=False,beta_fit=False,full_rule=False,physical_period=False,
        noise_map=False,faithful_Gray=False,Gray_refutation=False,iid_failure=False,shorter_U=False)
    out=DATA/'GBD3_manifest.json';out.write_text(json.dumps(m,indent=2)+'\n')
    print(json.dumps(dict(passed=True,assets=len(assets),manifest_sha256=sha(out)),indent=2))


if __name__=='__main__':main()
