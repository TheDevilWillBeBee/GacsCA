"""Issue one isolated manifest after checking all inherited frozen assets."""
from pathlib import Path
import hashlib,json
S=Path(__file__).resolve().parent;ROOT=S.parents[3]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw16'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    ancestor=ROOT/'figs/gray_counterexamples/unregistered_gaw15/GAW15_standalone_assets.json'
    prior=json.loads(ancestor.read_text());assets=dict(prior['assets_sha256'])
    assert len(assets)==417
    for p,h in assets.items():assert sha(ROOT/p)==h,(p,'accepted prior asset changed')
    for p in (ancestor,ROOT/'figs/gray_counterexamples/unregistered_gaw15/GAW15_readonly_replay02.log'):
        assets[str(p.relative_to(ROOT))]=sha(p)
    for folder in (S,D):
        for p in sorted(folder.iterdir()):
            if not p.is_file() or p.name=='GAW16_standalone_assets.json' or p.name.startswith('GAW16_readonly_replay'):continue
            assert p.suffix in ('.py','.md','.json','.log'),('unrecognized checkpoint file',p)
            assets[str(p.relative_to(ROOT))]=sha(p)
    issued=json.loads((D/'GAW16_word_burst_certificate.json').read_text())
    for p,h in issued['dependencies_sha256'].items():assert assets[p]==h
    r=dict(name='GAW16 frozen four actual Word100/native-control 16x16 bursts',
        Q=8192,U=1048576,error_lambda=24,error_separation=104,
        inherited_manifest=str(ancestor.relative_to(ROOT)),inherited_assets=417,assets_sha256=assets,
        unchanged_CA_and_registered_main=True,actual_recursive_intact_H_start=True,
        four_actual_original_real1_16by16_U_legal_singleton_and2U_shadow=True,
        actual_full_Programme_operand_and_final_computed_primary_Workspace=True,
        actual_delayed_nonboolean_Programme_to_Out_premise_witness=True,
        future_command_Head_or_tape_supplied=False,universal_mixed_repair_or_Gray_iid_shorter_U=False,
        new_CA_or_beta_fit_Q_or_dictionary512=False)
    p=D/'GAW16_standalone_assets.json';assert not p.exists(),'manifest already issued; do not overwrite a frozen checkpoint'
    p.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(dict(passed=True,assets=len(assets),manifest_sha256=sha(p))),flush=True)

if __name__=='__main__':main()
