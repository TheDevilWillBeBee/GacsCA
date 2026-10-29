"""Freeze only the new GBC4 checkpoint and inherited immutable hash pins."""
from hashlib import sha256
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[4];S=Path(__file__).resolve().parent
D=ROOT/'figs/gray_counterexamples/unregistered_gbc4'
OLD=ROOT/'figs/gray_counterexamples/unregistered_gbc3/GBC3_manifest.json'
def digest(p):return sha256(p.read_bytes()).hexdigest()
def run():
    old=json.loads(OLD.read_text());assets=dict(old['assets'])
    for rel,h in assets.items():assert digest(ROOT/rel)==h,rel
    assets[str(OLD.relative_to(ROOT))]=digest(OLD)
    for p in sorted(S.iterdir()):
        if p.is_file() and p.suffix in ('.py','.md'):assets[str(p.relative_to(ROOT))]=digest(p)
    for p in sorted(D.iterdir()):
        if p.is_file() and p.name.startswith('GBC4_') and not p.name.startswith(('GBC4_manifest','GBC4_freeze','GBC4_readonly')):
            assets[str(p.relative_to(ROOT))]=digest(p)
    out={'schema':'GBC4 isolated frozen checkpoint v1','assets':assets,
         'Q':8192,'U':1048576,'lambda':24,'c':104,'head_bits':553,'frame_bits':3087,
         'generic_control_contract_proved':True,'shared_reader_contract_proved':True,
         'exact_tail_rewrite_contract_proved':True,'whole_own_beta':False,
         'universal_emitter_equivalence_proved':False,'universal_full_runtime_proved':False,
         'physical_period':False,'gray_refutation':False,'iid_failure':False,'shorter_U_proved':False}
    p=D/'GBC4_manifest.json';p.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'passed':True,'assets':len(assets),'manifest':str(p.relative_to(ROOT)),
                      'manifest_sha256':digest(p)},indent=2))
if __name__=='__main__':run()
