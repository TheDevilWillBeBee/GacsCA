"""Freeze new GBC5 sources/receipts, preserving all inherited pins."""
from hashlib import sha256
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[4];S=Path(__file__).resolve().parent
D=ROOT/'figs/gray_counterexamples/unregistered_gbc5'
OLD=ROOT/'figs/gray_counterexamples/unregistered_gbc4/GBC4_manifest.json'
def digest(p):return sha256(p.read_bytes()).hexdigest()
def run():
    old=json.loads(OLD.read_text());assets=dict(old['assets'])
    for rel,h in assets.items():assert digest(ROOT/rel)==h,rel
    assets[str(OLD.relative_to(ROOT))]=digest(OLD)
    for name in ('GBC4_readonly_own_validation01.json','GBC4_readonly_own_replay01.log'):
        p=OLD.parent/name;assets[str(p.relative_to(ROOT))]=digest(p)
    prior=json.loads((OLD.parent/'GBC4_readonly_own_validation01.json').read_text())
    assert prior['passed'] and prior['hashes_unchanged'] and prior['manifest_sha256']==digest(OLD)
    for p in sorted(S.iterdir()):
        if p.is_file() and p.suffix in ('.py','.md'):assets[str(p.relative_to(ROOT))]=digest(p)
    for p in sorted(D.iterdir()):
        if p.is_file() and p.name.startswith('GBC5_') and not p.name.startswith(('GBC5_manifest','GBC5_freeze','GBC5_readonly')):
            assets[str(p.relative_to(ROOT))]=digest(p)
    out={'schema':'GBC5 isolated frozen checkpoint v1','assets':assets,
         'Q':8192,'U':1048576,'lambda':24,'c':104,'unchanged_total_rule':True,
         'no_added_state_or_opcode':True,'scratch_free_reader_contract_proved':True,
         'actual_reader_RAW80_preservation_proved':True,'listed_return_bank_liveness_proved':True,
         'universal_component_deadline':3104,'whole_own_beta':False,
         'universal_emitter_equivalence':False,'universal_full_runtime':False,
         'physical_period':False,'gray_refutation':False,'iid_failure':False,'shorter_U_proved':False}
    p=D/'GBC5_manifest.json';p.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'passed':True,'assets':len(assets),'manifest':str(p.relative_to(ROOT)),
                      'manifest_sha256':digest(p)},indent=2))
if __name__=='__main__':run()
