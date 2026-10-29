"""Freeze the new design checkpoint without mutating inherited assets."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
SOURCE=Path(__file__).resolve().parent
DATA=ROOT/'figs/gray_counterexamples/unregistered_gbd0'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    oldpath=ROOT/'figs/gray_counterexamples/unregistered_gbc6/GBC6_manifest.json'
    old=json.loads(oldpath.read_text())
    assets=dict(old['assets'])
    for name,h in assets.items():
        assert sha(ROOT/name)==h,(name,'frozen inheritance changed')
    inherited=[oldpath,
        ROOT/'figs/gray_counterexamples/unregistered_gbc6/GBC6_readonly_own_validation01.json',
        ROOT/'figs/gray_counterexamples/unregistered_gbc6/GBC6_readonly_own_replay01.log',
        ROOT/'figs/gray_counterexamples/unregistered_gbc6/GBC6_parent_readonly_validation.json',
        ROOT/'papers_txt/gray_readers_guide.txt',
        ROOT/"papers/A Reader's Guide to Gacs's ``Positive Rates'' Paper.pdf"]
    own=[]
    for base in (SOURCE,DATA):
        own.extend(p for p in base.iterdir() if p.is_file() and
                   p.name not in ('GBD0_manifest.json',) and
                   not p.name.startswith('GBD0_readonly'))
    for p in inherited+own:
        assets[str(p.relative_to(ROOT))]=sha(p)
    for p in inherited[1:2]+inherited[3:4]:
        r=json.loads(p.read_text())
        assert r['passed'] and r['hashes_unchanged']
        assert r['manifest_sha256']==sha(oldpath)
        assert not r['whole_own_beta'] and not r['faithful_Gray']
    receipt=DATA/'GBD0_certificate_attempt04.json'
    r=json.loads(receipt.read_text());assert r['passed']
    result=dict(schema='GBD0 isolated whole-budget and window design v1',
        assets=assets, inherited_manifest=str(oldpath.relative_to(ROOT)),
        inherited_child_replay=str(inherited[1].relative_to(ROOT)),
        inherited_parent_replay=str(inherited[3].relative_to(ROOT)),
        receipt=str(receipt.relative_to(ROOT)),
        baseline=r['baseline'],exact_listing_bits=42716,
        exact_layout_obstruction=True,universal_packed_window=True,
        packed_window_radius=8,hybrid_state_count_only=3262,
        old_rule_changed=False,new_rule_emitted=False,
        whole_own_beta=False,universal_runtime=False,physical_period=False,
        faithful_Gray=False,gray_refutation=False,iid_failure=False,
        shorter_U=False)
    (DATA/'GBD0_manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,assets=len(assets),
                         manifest_sha256=sha(DATA/'GBD0_manifest.json')),indent=2))


if __name__=='__main__':main()
