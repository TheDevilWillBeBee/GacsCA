"""New GAW21 snapshot, retaining all accepted GAW0--20 ancestors."""
from pathlib import Path
import hashlib,json
S=Path(__file__).resolve().parent;ROOT=S.parents[3]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw21'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    prior=ROOT/'figs/gray_counterexamples/unregistered_gaw20/GAW20_standalone_assets02.json'
    inherited=json.loads(prior.read_text());assets=dict(inherited['assets_sha256']);assert len(assets)==544
    for p,h in assets.items():assert sha(ROOT/p)==h,(p,'accepted ancestor differs')
    for p in (prior,ROOT/'figs/gray_counterexamples/unregistered_gaw20/GAW20_readonly_replay02.log'):
        assets[str(p.relative_to(ROOT))]=sha(p)
    for directory in (S,D):
        for p in sorted(directory.rglob('*')):
            if not p.is_file() or '__pycache__' in p.parts or p.name=='GAW21_standalone_assets.json' or p.name.startswith('GAW21_readonly_replay'):continue
            assets[str(p.relative_to(ROOT))]=sha(p)
    r=dict(name='GAW21 two raw records repair; actual intact three-record contraction witness',
        Q=8192,U=1048576,error_lambda=24,error_separation=104,
        inherited_manifest=str(prior.relative_to(ROOT)),inherited_assets=544,assets_sha256=assets,
        arbitrary_two_raw496Word100_prepared_records_all_phase_contraction=True,
        actual_three_record15_point_shared_c104_real2_one_period_contraction_counterexample=True,
        generic_malformed_quotient_uniform_error_class_operational_real2_or_eventual_failure=False,
        Gray_iid_memory_positive_rate_or_shorter_U_claim=False,
        accepted_ancestors_main_G17_rule_and_ROM_unchanged=True)
    p=D/'GAW21_standalone_assets.json';assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(dict(passed=True,assets=len(assets),manifest_sha256=sha(p))),flush=True)

if __name__=='__main__':main()
