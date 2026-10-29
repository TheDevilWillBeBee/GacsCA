"""Create only this isolated checkpoint's manifest after sources settle."""
import hashlib,json
from pathlib import Path
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[4]
SOURCE=Path(__file__).resolve().parent
DATA=ROOT/'figs/gray_counterexamples/unregistered_gbp0'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

registered={
 'Report/GRAY_COUNTEREXAMPLES.md':'27efe30dca8bb4a94077158cc8b56f2c49143ddae927ecbc23c3af02170c775c',
 'Report/proofs/gray_counterexamples/validate_gray_counterexamples.py':'8e921ae50894401b0c133e5c280c9e02411dcf6760b5d985c1e88b536e39506d',
 'figs/gray_counterexamples/checkpoint_validation.json':'df969dd88774a8714a3dd019eed1f9f74b7cd0d92dd73ed1596712564267bb7d'}
for name,digest in registered.items():assert sha(ROOT/name)==digest,(name,'registered checkpoint changed')
paths=[]
for directory in (SOURCE,DATA):
    for path in directory.iterdir():
        if path.is_file() and path.suffix in ('.py','.md','.json','.log'):
            if path.name.startswith(('GBP1R_manifest','GBP1R_validation')):continue
            paths.append(path)
dependencies=[
 'gacsca/maintenance.py','gacsca/netlist.py','gacsca/__init__.py','gacsca/candidates.py',
 'papers_txt/gray_readers_guide.txt','papers_txt/gacs_2001.txt',
 "papers/A Reader's Guide to Gacs's ``Positive Rates'' Paper.pdf",
 'papers/Reliable Cellular Automata with Self-Organization.pdf',
 'Report/proofs/gray_counterexamples/unregistered_gi0/GI0_TOTAL_SOURCE_INTERFACE.md',
 'Report/proofs/gray_counterexamples/unregistered_gfd0/GFD0_BINARY_STAGE3_FLAG_DELIVERY.md',
 *registered]
paths.extend(ROOT/name for name in dependencies)
assets={str(path.relative_to(ROOT)):sha(path) for path in sorted(set(paths))}
scope={'frozen':True,'Q':8192,'U':1048576,'lambda':24,'c':104,
 'name':'GBP1R nine-Q immutable-ROM diagnostic; rejected Q-sized GBP1 listing retained',
 'total_declared_radius8_rule':True,'immutable_ROM_bits':73728,'emission_bits':66815,
 'K':4052,'2K':8104,'selected_global_E_clean_period_counterexample':True,
 'physical_error_history':[],'intact_recursive_start':False,
 'universal_emitted_identity':False,'Q_beta_fit':False,'noise_proof':False,
 'gray_counterexample':False,'iid_failure':False,'shorter_U':False,
 'active_rule_modified':False,'registered_checkpoint_modified':False}
r={'scope':scope,'assets':assets,
 'provenance':'All prior failure snapshots are historical rejected diagnostics. Replays check current specified sources only. Wall times are measurements.',
 'validator_command':'python3 Report/proofs/gray_counterexamples/unregistered_gbp0/validate_gbp1r_own_emission.py --output /tmp/GBP1R_parent_readonly_validation.json'}
(DATA/'GBP1R_manifest.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({'passed':True,'assets':len(assets),'manifest_sha256':sha(DATA/'GBP1R_manifest.json')}))
