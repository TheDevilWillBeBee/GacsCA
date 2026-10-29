"""Freeze new GBD4 sources/receipts plus accepted unchanged provenance."""
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
DATA=ROOT/'figs/gray_counterexamples/unregistered_gbd4'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    old=ROOT/'figs/gray_counterexamples/unregistered_gbd3/GBD3_manifest.json'
    om=json.loads(old.read_text());assets=dict(om['assets'])
    for path,h in assets.items():assert sha(ROOT/path)==h,(path,'inherited change')
    replays=[ROOT/'figs/gray_counterexamples/unregistered_gbd3'/name for name in
             ('GBD3_readonly_own_validation01.json','GBD3_parent_readonly_validation.json')]
    for path in replays:
        r=json.loads(path.read_text());assert r['passed'] and r['hashes_unchanged']
        assert r['manifest_sha256']==sha(old)
    added=[old,*replays,
           ROOT/'figs/gray_counterexamples/unregistered_gbd3/GBD3_readonly_own_replay01.log',
           ROOT/'figs/robustness/GBD3_parent_readonly_run01.log',
           ROOT/'gacsca/maintenance.py',
           ROOT/'Report/proofs/gray_counterexamples/literal_maintenance.py']
    for directory in (HERE,DATA):
        added.extend(p for p in directory.rglob('*') if p.is_file()
             and '__pycache__' not in p.parts and p.name!='GBD4_manifest.json'
             and p.name!='GBD4_freeze.log'
             and not p.name.startswith('GBD4_readonly') and not p.name.startswith('GBD4_parent'))
    for p in added:assets[str(p.relative_to(ROOT))]=sha(p)
    receipt=DATA/'attempt03/GBD4_certificate.json'
    native=json.loads(receipt.read_text())
    assert native['universal_native_runtime']==33937 and native['layout']['Scratch_Out_positions']==9
    assert native['programmes']['h1']['code_bits']==7051
    assert native['programmes']['printed']['code_bits']==7106
    assert not native['full_own_beta'] and not native['full_period']
    arithmetic=DATA/'GBD4_arithmetic_liveness_certificate.json'
    ar=json.loads(arithmetic.read_text());assert ar['passed'] and ar['native_unsigned_arithmetic_checks']==180224
    m=dict(schema='GBD4 actual counted native software component v1',assets=assets,
        inherited_manifest=str(old.relative_to(ROOT)),
        inherited_replays=[str(p.relative_to(ROOT)) for p in replays],
        native_receipt=str(receipt.relative_to(ROOT)),arithmetic_receipt=str(arithmetic.relative_to(ROOT)),
        native_artifact_directory=str(receipt.parent.relative_to(ROOT)),
        Q=8192,U=1048576,lambda_=24,c=104,K=3387,Head_bits=204,
        h1_native_beta_bits=7051,printed_native_beta_bits=7106,
        universal_prepared_native_updates=33937,new_READ_bank_selector_bits=1,
        actual_native_software_no_oracle=True,printed_and_h1_separate=True,
        actual_scratch_Out_words=9,port_level_radius_at_most=7,
        all_upper_raw_native_words=True,coherent_quiet_lower_execution_is_premise=True,
        complete_own_beta=False,beta_fit=False,full_rule=False,physical_period=False,
        autonomous_ports=False,authentic_History_origin=False,error_history=False,
        faithful_Gray=False,Gray_refutation=False,iid_failure=False,shorter_U=False)
    target=DATA/'GBD4_manifest.json';target.write_text(json.dumps(m,indent=2)+'\n')
    print(json.dumps(dict(passed=True,assets=len(assets),manifest_sha256=sha(target)),indent=2))

if __name__=='__main__':main()
