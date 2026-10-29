"""Freeze isolated GBC6 and exact inherited accepted provenance."""
from hashlib import sha256
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[4];S=Path(__file__).resolve().parent
D=ROOT/'figs/gray_counterexamples/unregistered_gbc6'
OLD=ROOT/'figs/gray_counterexamples/unregistered_gbc5/GBC5_manifest.json'
def digest(p):return sha256(p.read_bytes()).hexdigest()
def run():
    old=json.loads(OLD.read_text());assets=dict(old['assets'])
    for rel,h in assets.items():assert digest(ROOT/rel)==h,rel
    assets[str(OLD.relative_to(ROOT))]=digest(OLD)
    inherited=[]
    for name in ('GBC5_readonly_own_validation01.json','GBC5_readonly_own_replay01.log',
                 'GBC5_parent_readonly_validation.json'):
        p=OLD.parent/name;assets[str(p.relative_to(ROOT))]=digest(p);inherited.append(str(p.relative_to(ROOT)))
    for name in ('GBC5_readonly_own_validation01.json','GBC5_parent_readonly_validation.json'):
        r=json.loads((OLD.parent/name).read_text())
        assert r['passed'] and r['hashes_unchanged'] and r['manifest_sha256']==digest(OLD)
        assert all(x['terminal_exit']==0 and x['matched'] for x in r['new_replays'])
    for p in sorted(S.iterdir()):
        if p.is_file() and p.suffix in ('.py','.md'):assets[str(p.relative_to(ROOT))]=digest(p)
    for p in sorted(D.iterdir()):
        if p.is_file() and p.name.startswith('GBC6_') and not p.name.startswith(('GBC6_manifest','GBC6_freeze','GBC6_readonly')):
            assets[str(p.relative_to(ROOT))]=digest(p)
    out={'schema':'GBC6 isolated generic-register component v1','assets':assets,
         'inherited_validated_results':inherited,'Q':8192,'U':1048576,'lambda':24,'c':104,
         'rule_changed_REG_REGI':True,'state_bits_added':0,'frame_bits':3087,'head_bits':553,
         'raw_opcode_semantics_proved':True,'conditional_listed_own_branch_proved':True,
         'conditional_new_RAW80_return_liveness_proved':True,
         'conditional_branch_deadlines':{'REG':58171,'REGI':41817},
         'complete_bits':42716,'complete_instructions':3140,'invalid_references':384,
         'whole_own_beta':False,'universal_full_emitter':False,'universal_full_runtime':False,
         'physical_period':False,'faithful_Gray':False,'gray_refutation':False,
         'iid_failure':False,'shorter_U_proved':False}
    p=D/'GBC6_manifest.json';p.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'passed':True,'assets':len(assets),'manifest':str(p.relative_to(ROOT)),
                      'manifest_sha256':digest(p)},indent=2))
if __name__=='__main__':run()
