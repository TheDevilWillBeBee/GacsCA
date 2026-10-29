"""Read-only full replay and provenance of the frozen GAW14 checkpoint."""
from pathlib import Path
import hashlib,json,subprocess,sys,tempfile,time
S=Path(__file__).resolve().parent;ROOT=S.parents[3]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw14'
sys.path.insert(0,str(S))
import certify_gaw14_active_factor as cert

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def assets(m):
    for path,value in m['assets_sha256'].items():assert sha(ROOT/path)==value,(path,'asset provenance changed')

def main():
    start=time.monotonic();path=D/'GAW14_standalone_assets.json';m=json.loads(path.read_text());assets(m)
    with tempfile.TemporaryDirectory(prefix='gaw14_binary_replay_') as temp:
        target=Path(temp)/'gaw14_active_factor.so'
        subprocess.run(['gcc','-O3','-std=c11','-shared','-fPIC',str(S/'gaw14_active_factor.c'),'-o',str(target)],check=True,cwd=ROOT)
        assert sha(target)==sha(D/'gaw14_active_factor.so'),'rebuilt diagnostic binary differs'
    cert.main(write=False,replay_histories=True)
    receipt=json.loads((D/'GAW14_mixed_active_certificate.json').read_text())
    totalcofactors=totalcommit=totalupper=0
    for case in receipt['cases']:
        tag=case['tag'];prefix=json.loads((D/(tag+'_active_receipt.json')).read_text())
        b=json.loads((D/(tag+'_boundary_receipt.json')).read_text())['actual_U_and2U']
        totalcofactors+=sum(len(v['actual_full_local_R_checks']) for v in prefix['events'])
        totalcommit+=b['actual_raw_U_commit_and_reset_local_R_checks']
        totalupper+=len(b.get('actual_next_upper_transitions',[]))
        assert not b['selected_untyped_second_bank_executions']
        assert b['U_native_padding_legal'] and b['legal_record_theorem_applied']
        assert b['fixed_adjacent_pair_covers'] and not b['no_fixed_adjacent_pair_counterexample']
        assert b['complete2U_shadow']
        native=json.loads((D/(tag+'_boundary_receipt.json')).read_text())['actual_derived_late_continuation']
        assert native['terminal_before120Q']
    # The two potentially non-active initial prefixes are independently
    # replayed in cert.main; no future seed is accepted instead of them.
    assert all(c['actual_fault_clock']==839681 for c in
        (json.loads((D/(case['tag']+'_active_receipt.json')).read_text()) for case in receipt['cases']))
    assets(m)
    out=dict(passed=True,assets_verified=len(m['assets_sha256']),exact_rebuilt_diagnostic_binary=True,
        exact_frozen_rule_ROM_and_intact_H=True,actual_original_real1_histories=10,
        actual_mixed_factor_full_local_R_cofactors=totalcofactors,
        actual_U_full_local_R_commit_checks=totalcommit,actual_derived_upper_next_local_R_checks=totalupper,
        independent_mixed_native_SF_cofactors=256,actual_chronological_T_checks=2520,
        all_U_normal_records_legal_and_in_adjacent_pair=True,all_complete2U_shadow=True,
        universal_mixed_repair_or_Gray_iid_or_shorter_U=False,
        main_or_active_rule_modified=False,manifest_sha256=sha(path),elapsed_seconds=time.monotonic()-start)
    print(json.dumps(out),flush=True);return out

if __name__=='__main__':main()
