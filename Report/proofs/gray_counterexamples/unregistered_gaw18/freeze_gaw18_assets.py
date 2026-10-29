"""Freeze new selected unmasked period proof without editing ancestors."""
from pathlib import Path
import hashlib,json
S=Path(__file__).resolve().parent;ROOT=S.parents[3]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw18'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    ancestor=ROOT/'figs/gray_counterexamples/unregistered_gaw17/GAW17_standalone_assets.json'
    inherited=json.loads(ancestor.read_text());assets=dict(inherited['assets_sha256']);assert len(assets)==472
    for p,h in assets.items():assert sha(ROOT/p)==h,(p,'accepted ancestor changed')
    for p in (ancestor,ROOT/'figs/gray_counterexamples/unregistered_gaw17/GAW17_readonly_replay01.log'):
        assets[str(p.relative_to(ROOT))]=sha(p)
    for directory in (S,D):
        for p in sorted(directory.rglob('*')):
            if not p.is_file() or '__pycache__' in p.parts or p.name=='GAW18_standalone_assets.json' or p.name.startswith('GAW18_readonly_replay'):continue
            assets[str(p.relative_to(ROOT))]=sha(p)
    # Preserve the root's independent negative examples; no use as a
    # malformed-input positive refinement contract.
    rootpaths=(
        'Report/proofs/gray_counterexamples/unregistered_gaw_padding_quotient/PADDING_QUOTIENT_OBSTRUCTION.md',
        'Report/proofs/gray_counterexamples/unregistered_gaw_padding_quotient/check_padding_quotient.py',
        'figs/gray_counterexamples/unregistered_gaw_padding_quotient/padding_quotient_certificate.json',
    )
    for name in rootpaths:assets[name]=sha(ROOT/name)
    receipt=json.loads((D/'GAW18_malformed_period_certificate02.json').read_text())
    assert receipt['selected_malformed_physical_period_composed'] and receipt['complete2U_and_all_later_no_error_shadow']
    assert not receipt['legal_upper_theorem_on_malformed_record']
    r=dict(name='GAW18 selected actual malformed GAW17 second period, full2U shadow',
        Q=8192,U=1048576,error_lambda=24,error_separation=104,
        inherited_manifest=str(ancestor.relative_to(ROOT)),inherited_assets=472,assets_sha256=assets,
        unchanged_CA_ROM_and_registered_main=True,no_native_projection_or_new_errors=True,
        actual_three_gathers_reset_birth_sources_and_selected_early_late_executions=True,
        actual_raw_2U_complete_encoding_and_all_later_shadow=True,
        historical_GAW17_illegal_case_null_not_mutated=True,
        universal_malformed_real1_higher_Gray_iid_or_shorter_U=False)
    p=D/'GAW18_standalone_assets.json';assert not p.exists(),'already frozen; do not overwrite'
    p.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(passed=True,assets=len(assets),manifest_sha256=sha(p))),flush=True)

if __name__=='__main__':main()
