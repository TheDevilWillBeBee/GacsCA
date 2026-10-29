"""Issue a new standalone GAW20 manifest; no accepted ancestor edits."""
from pathlib import Path
import hashlib,json
S=Path(__file__).resolve().parent;ROOT=S.parents[3]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw20'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    prior=ROOT/'figs/gray_counterexamples/unregistered_gaw19/GAW19_standalone_assets02.json'
    inherited=json.loads(prior.read_text());assets=dict(inherited['assets_sha256']);assert len(assets)==518
    for p,h in assets.items():assert sha(ROOT/p)==h,(p,'accepted ancestor differs')
    for p in (prior,ROOT/'figs/gray_counterexamples/unregistered_gaw19/GAW19_readonly_replay02.log'):
        assets[str(p.relative_to(ROOT))]=sha(p)
    for directory in (S,D):
        for p in sorted(directory.rglob('*')):
            if not p.is_file() or '__pycache__' in p.parts or p.name=='GAW20_standalone_assets.json' or p.name.startswith('GAW20_readonly_replay'):continue
            assets[str(p.relative_to(ROOT))]=sha(p)
    r=dict(name='GAW20 all-phase canonical/coherent single raw496 Word100 record repair',
        Q=8192,U=1048576,error_lambda=24,error_separation=104,
        inherited_manifest=str(prior.relative_to(ROOT)),inherited_assets=518,assets_sha256=assets,
        all_phase_conditional_padding_congruence_four_clean_vote_absorption_and_complete_prepared_period=True,
        all_actual_RnH_zero_flags_and_coherence_follow_from_written_first_positive_time_proof=True,
        any49600bit_record_at_any_location_and_intact_phase_repairs_next_clean_boundary=True,
        final_upper_Workspace_not_assumed_zero_on_arbitrary_coherent_background=True,
        direct_Intact_H_Info_only_member_realization_without_supplied_future_tape=True,
        uniform_error_class_generic_padding_quotient_arbitrary_damaged_work_geometry_or_multiple_records=False,
        Gray_Gacs_faithfulness_iid_higher_reliability_memory_rate_or_shorter_U=False,
        accepted_ancestors_main_G17_rule_and_ROM_unchanged=True)
    target=D/'GAW20_standalone_assets.json';assert not target.exists()
    target.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(dict(passed=True,assets=len(assets),manifest_sha256=sha(target))),flush=True)
if __name__=='__main__':main()
