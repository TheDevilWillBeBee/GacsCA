"""Pin the isolated GBC3 checkpoint; never modify prior assets."""
from hashlib import sha256
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[4]
S=Path(__file__).resolve().parent
D=ROOT/'figs/gray_counterexamples/unregistered_gbc3'
OLD=ROOT/'figs/gray_counterexamples/unregistered_gbc2/GBC2_complete_manifest.json'


def digest(p):return sha256(p.read_bytes()).hexdigest()


def run():
    old=json.loads(OLD.read_text())
    assets={}
    for rel,hashvalue in old['assets'].items():
        p=ROOT/rel
        assert digest(p)==hashvalue,rel
        assets[rel]=hashvalue
    assets[str(OLD.relative_to(ROOT))]=digest(OLD)
    for p in sorted(S.iterdir()):
        if p.is_file() and p.suffix in ('.py','.md'):
            assets[str(p.relative_to(ROOT))]=digest(p)
    for p in sorted(D.iterdir()):
        if p.is_file() and p.name.startswith('GBC3_') and not p.name.startswith(('GBC3_manifest','GBC3_readonly','GBC3_freeze')):
            assets[str(p.relative_to(ROOT))]=digest(p)
    out={'schema':'GBC3 frozen component checkpoint v1','assets':assets,
         'inherited_GBC2_manifest_sha256':digest(OLD),
         'Q':8192,'U':1048576,'lambda':24,'c':104,
         'head_bits':553,'frame_bits':3087,
         'generic_primitive_proved':True,'counted_helper_contract_proved':True,
         'complete_emitted_equivalence_proved':False,'whole_own_beta':False,
         'universal_whole_deadline_proved':False,'physical_period':False,
         'physical_errors':[],'gray_refutation':False,'iid_failure':False,
         'shorter_U_proved':False}
    p=D/'GBC3_manifest.json';p.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'passed':True,'assets':len(assets),'manifest':str(p.relative_to(ROOT)),
                      'manifest_sha256':digest(p)},indent=2))


if __name__=='__main__':run()
