"""Issue only the new GAW22 manifest; preserve every accepted ancestor."""
from pathlib import Path
import hashlib,json
S=Path(__file__).resolve().parent;ROOT=S.parents[3]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw22'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    prior=ROOT/'figs/gray_counterexamples/unregistered_gaw21/GAW21_standalone_assets.json'
    old=json.loads(prior.read_text());assets=dict(old['assets_sha256']);assert len(assets)==555
    for p,h in assets.items():assert sha(ROOT/p)==h,(p,'frozen ancestor differs')
    for p in (prior,ROOT/'figs/gray_counterexamples/unregistered_gaw21/GAW21_readonly_replay01.log'):
        assets[str(p.relative_to(ROOT))]=sha(p)
    issue=(D/'GAW22_recurrence_issue01.log').read_text()
    assert json.loads(issue.strip())['passed']
    for directory in (S,D):
        for p in sorted(directory.rglob('*')):
            if not p.is_file() or '__pycache__' in p.parts or p.name=='GAW22_standalone_assets.json' or p.name.startswith('GAW22_readonly_replay'):continue
            assets[str(p.relative_to(ROOT))]=sha(p)
    r=dict(name='GAW22 same actual shared real2 exact recurrence and U-squared full raw repair',
        Q=8192,U=1048576,error_lambda=24,error_separation=104,
        inherited_manifest=str(prior.relative_to(ROOT)),inherited_assets=555,assets_sha256=assets,
        same_actual_GAW21_intact_start_fifteen_point_shared_real2_no_new_errors=True,
        exact_all_row_upper_recurrence_and_legal_native_actual_physical_period_lift=True,
        full_raw_first_physical_repair_time=1099511627776,
        encoded_Info4054_continuous_persistence_half_open=[1048576,1099511627776],
        temporary_rescaled_real1_transplanted_literal_all_SF_P4_R_failure=True,
        earlier_GAW21_eventual_recovery_status_remains_historical_unproved=True,
        Gray_Address_P5_operational_eventual_repair_iid_memory_or_shorter_U_failure_claim=False,
        accepted_ancestors_main_G17_rule_ROM_and_schedule_unchanged=True)
    p=D/'GAW22_standalone_assets.json';assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(dict(passed=True,assets=len(assets),manifest_sha256=sha(p))),flush=True)

if __name__=='__main__':main()
