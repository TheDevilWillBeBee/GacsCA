"""Read-only replay preserving the frozen issuer and its failed first harness.

The original harness compared Python tuple intervals with JSON list intervals.
This wrapper checks exact canonical JSON equality, including every digest/value.
It changes no rule, proof, checker, accepted certificate or original manifest.
"""
import argparse,hashlib,json,time
from pathlib import Path
import check_gawn23_all_phase_sf as c
ROOT=c.ROOT;OUT=c.OUT
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check(assets):
    for path,value in assets.items():assert sha(ROOT/path)==value,path
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    start=time.perf_counter()
    mp=OUT/'GAWN23_standalone_assets.json';vm=OUT/'GAWN23_validation_assets.json'
    old=json.loads(mp.read_text());manifest=json.loads(vm.read_text())
    assert len(old['assets_sha256'])==765 and len(manifest['assets_sha256'])==770
    for path,value in old['assets_sha256'].items():assert manifest['assets_sha256'][path]==value,path
    check(manifest['assets_sha256'])
    cp=OUT/'GAWN23_all_phase_SF_certificate.json';accepted=json.loads(cp.read_text())
    fresh=c.compute()
    # Retain an explicit witness of the original harness type mismatch.
    assert isinstance(fresh['all_phase_capture_windows']['conservative_capture_fault_windows'][0],tuple)
    assert isinstance(accepted['all_phase_capture_windows']['conservative_capture_fault_windows'][0],list)
    assert fresh!=accepted
    canonical=json.loads(json.dumps(fresh))
    assert canonical==accepted,'Canonical recomputed JSON differs'
    historical=json.loads((OUT/'GAWN23_diagnostic_recomputed_attempt02.json').read_text())
    assert historical==accepted
    check(manifest['assets_sha256'])
    r=dict(passed=True,readonly=True,assets=770,theorem_assets=765,inherited_theorem_assets=760,
        original_manifest_sha256=sha(mp),validation_manifest_sha256=sha(vm),certificate_sha256=sha(cp),
        hashes_unchanged=True,all_new_claims_recomputed=True,exact_canonical_JSON_equality=True,
        retained_first_harness_tuple_list_mismatch=True,no_computed_mathematical_value_or_digest_changed=True,
        all524288_first_fault_phases_checked=True,native_quiet_physical_row=99*c.k.Q,
        all_stated_all_phase_SF_only_complete2U_repair_proved=True,
        global_reliability_proved=False,rule_ROM_constants_CURRENT_changed=False,
        elapsed_seconds=time.perf_counter()-start)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    assert not args.output.exists(),'Never overwrite a replay receipt'
    args.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2),flush=True)
if __name__=='__main__':main()
