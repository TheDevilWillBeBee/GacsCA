"""Freeze a new GAW19 checkpoint; never update an accepted ancestor."""
from pathlib import Path
import hashlib,json
S=Path(__file__).resolve().parent;ROOT=S.parents[3]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw19'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    prior=ROOT/'figs/gray_counterexamples/unregistered_gaw18/GAW18_standalone_assets.json'
    inherited=json.loads(prior.read_text());assets=dict(inherited['assets_sha256'])
    assert len(assets)==492
    for p,h in assets.items():assert sha(ROOT/p)==h,(p,'frozen ancestor differs')
    for p in (prior,ROOT/'figs/gray_counterexamples/unregistered_gaw18/GAW18_readonly_replay01.log'):
        assets[str(p.relative_to(ROOT))]=sha(p)
    mainpins={
      'Report/GRAY_COUNTEREXAMPLES.md':'27efe30dca8bb4a94077158cc8b56f2c49143ddae927ecbc23c3af02170c775c',
      'Report/proofs/gray_counterexamples/validate_gray_counterexamples.py':'8e921ae50894401b0c133e5c280c9e02411dcf6760b5d985c1e88b536e39506d',
      'figs/gray_counterexamples/checkpoint_validation.json':'df969dd88774a8714a3dd019eed1f9f74b7cd0d92dd73ed1596712564267bb7d',
    }
    for p,h in mainpins.items():assert sha(ROOT/p)==h;assets[p]=h
    for directory in (S,D):
        for p in sorted(directory.rglob('*')):
            if not p.is_file() or '__pycache__' in p.parts or p.name=='GAW19_standalone_assets.json' or p.name.startswith('GAW19_readonly_replay'):continue
            assets[str(p.relative_to(ROOT))]=sha(p)
    sr=json.loads((D/'GAW19_symbolic_execution_certificate.json').read_text())
    pr=json.loads((D/'GAW19_prepared_period_certificate.json').read_text())
    assert sr['quantified_bits']==pr['quantified_arbitrary_record_bits']==49600
    assert sr['universal_single_prepared_record_emitted_outputs_and_deadline']
    assert pr['actual_global_period_composition_proved_by_universal_execution_and_written_factor']
    assert not pr['new_rule_native_projection_or_legal_upper_theorem_on_W']
    r=dict(name='GAW19 first-U intact-shadow arbitrary single496 Word100 prepared record repair',
        Q=8192,U=1048576,error_lambda=24,error_separation=104,
        inherited_manifest=str(prior.relative_to(ROOT)),inherited_assets=492,assets_sha256=assets,
        universal_prepared_49600bit_early_late_identity_deadline_and_physical_period=True,
        actual_intact_start_allM500_site_real2_member_repairs2U=True,
        no_input_projection_legal_malformed_theorem_or_rule_change=True,
        arbitrary_later_phase_general_error_Gray_iid_memory_or_shorterU=False)
    target=D/'GAW19_standalone_assets.json';assert not target.exists()
    target.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(dict(passed=True,assets=len(assets),manifest_sha256=sha(target))),flush=True)

if __name__=='__main__':main()
