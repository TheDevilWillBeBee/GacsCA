"""Freeze only new GAW17 assets after checking every accepted GAW16 asset."""
from pathlib import Path
import hashlib,json
S=Path(__file__).resolve().parent;ROOT=S.parents[3]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw17'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    ancestor=ROOT/'figs/gray_counterexamples/unregistered_gaw16/GAW16_standalone_assets.json'
    inherited=json.loads(ancestor.read_text());assets=dict(inherited['assets_sha256']);assert len(assets)==443
    for p,h in assets.items():assert sha(ROOT/p)==h,(p,'accepted ancestor changed')
    for p in (ancestor,ROOT/'figs/gray_counterexamples/unregistered_gaw16/GAW16_readonly_replay01.log'):
        assets[str(p.relative_to(ROOT))]=sha(p)
    for directory in (S,D):
        for p in sorted(directory.iterdir()):
            if not p.is_file() or p.name=='GAW17_standalone_assets.json' or p.name.startswith('GAW17_readonly_replay'):continue
            assets[str(p.relative_to(ROOT))]=sha(p)
    issued=json.loads((D/'GAW17_large_burst_certificate.json').read_text())
    for p,h in issued['dependencies_sha256'].items():assert assets[p]==h
    r=dict(name='GAW17 five actual original-c104 large bursts; illegal U record withheld from legal theorem',
        Q=8192,U=1048576,error_lambda=24,error_separation=104,
        inherited_manifest=str(ancestor.relative_to(ROOT)),inherited_assets=443,assets_sha256=assets,
        unchanged_CA_and_registered_main=True,actual_recursive_intact_H_start=True,
        actual_dense104by104_and_sparse_span150_original_real1=True,
        four_legal_U_adjacent_pair_and_full2U_shadow=True,
        actual_one_illegal_U_Age_Flags_WF_record_outside_literal_narrow_E=True,
        illegal_case_decoder_2U_or_eventual_repair_conclusion=False,
        actual_Programme_to_native_Age_Out_lineage=True,
        retained_pretrajectory_serialization_failure=True,
        future_WF_or_Head_or_tape_supplied=False,universal_mixed_Gray_iid_or_shorter_U=False)
    p=D/'GAW17_standalone_assets.json';assert not p.exists(),'already frozen; do not overwrite'
    p.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(passed=True,assets=len(assets),manifest_sha256=sha(p))),flush=True)

if __name__=='__main__':main()
