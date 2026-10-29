"""Read-only replay of four actual bursts, Word100 factor and U/2U maps.

Frozen inherited theorems are reused only after checking every accepted
source/receipt dependency. No accepted receipt or registered file is written.
"""
from pathlib import Path
import hashlib,json,subprocess,sys,tempfile,time
S=Path(__file__).resolve().parent;ROOT=S.parents[3]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw16'
sys.path.insert(0,str(S))
import search_gaw16_word_bursts as m
import continue_gaw16_word_bursts as full
import check_gaw16_programme_factor as programme
import check_gaw16_collision_timeline as collision
import certify_gaw16_word_bursts as cert

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name):return json.loads((D/name).read_text())
def assets(manifest):
    for path,value in manifest['assets_sha256'].items():
        assert sha(ROOT/path)==value,(path,'asset provenance changed')
def same(actual,expected,label):
    assert m.previous.stable(actual)==m.previous.stable(expected),(label,'exact replay differs')
def announce(stage,**extra):print(json.dumps(dict(stage=stage,**extra)),flush=True)

def main():
    started=time.monotonic();path=D/'GAW16_standalone_assets.json';manifest=load(path.name);assets(manifest)
    inherited_path=ROOT/manifest['inherited_manifest']
    inherited=json.loads(inherited_path.read_text());assets(inherited)
    assert manifest['inherited_assets']==len(inherited['assets_sha256'])==417
    assert all(manifest['assets_sha256'][p]==h for p,h in inherited['assets_sha256'].items())
    assert manifest['assets_sha256'][str(inherited_path.relative_to(ROOT))]==sha(inherited_path)
    assert (m.k.Q,m.k.U,m.k.PRIMARY_START,m.T)==(8192,1048576,3848,839681)
    issued=load('GAW16_word_burst_certificate.json')
    for p,h in issued['dependencies_sha256'].items():
        assert manifest['assets_sha256'][p]==h and sha(ROOT/p)==h,(p,'unregistered result dependency')
    old_source=ROOT/'Report/proofs/gray_counterexamples/unregistered_gaw15/gaw15_native.c'
    old_dir=ROOT/'figs/gray_counterexamples/unregistered_gaw15'
    with tempfile.TemporaryDirectory(prefix='gaw16_readonly_replay_') as temp:
        target=Path(temp)/'gaw15_native.so'
        # Keep the frozen original source basename. Its ELF STT_FILE metadata
        # is part of the accepted binary identity, not just .text equivalence.
        subprocess.run(['gcc','-O3','-std=c11','-shared','-fPIC','-I',str(old_source.parent),
            str(old_source),'-o',str(target)],check=True,cwd=ROOT)
        assert sha(target)==sha(old_dir/'gaw15_native.so'),'rebuilt frozen diagnostic binary differs'
        announce('all_hashes_and_exact_diagnostic_binary_verified',assets=len(manifest['assets_sha256']),
            inherited_assets=len(inherited['assets_sha256']))
        issued_dir=m.previous.D;m.previous.D=Path(temp)
        try:
            for recipe in m.recipes():
                actual,_=m.run(recipe,limit=64)
                same(actual,load(recipe['tag']+'_discovery.json'),recipe['tag']+' bounded64')
                announce('bounded_discovery_replayed',tag=recipe['tag'],rows=len(actual['actual_rows']))
            for recipe in m.recipes():
                actual=full.run(recipe)
                same(actual,load(recipe['tag']+'_complete.json'),recipe['tag']+' actual full history')
                b=actual['actual_U_and2U_boundary']
                announce('complete_chronological_history_replayed',tag=recipe['tag'],rows=len(actual['actual_rows']),
                    bad_U=b['actual_U_bad_normal_receivers'],native_U_legal=b['actual_U_legal_E_encoding'],
                    full2U_shadow=b['complete2U_shadow'])
            same(programme.check(),load('GAW16_programme_factor_certificate.json'),'full Programme phase/witness checks')
            announce('full_Programme_cofactors_and_actual_delayed_Out_replayed')
            same(collision.check(),load('GAW16_collision_phase_certificate.json'),'actual collision/WF/phase timeline')
            announce('actual_collision_all_four_original_classifications_and_source_timelines_replayed')
        finally:m.previous.D=issued_dir
    same(cert.check(),issued,'aggregate selected certificate');assets(manifest);assets(inherited)
    result=dict(passed=True,assets_verified=len(manifest['assets_sha256']),inherited_assets_verified=417,
        exact_rebuilt_frozen_native_binary=True,exact_frozen_local_R_and_own_ROM=True,
        actual_recursive_H_and_same_chronological_start=True,original_c104_real1_16_by16_complete_histories=4,
        bounded_discoveries_replayed=4,actual_total_prefix_rows=20627,actual_prefix_full_local_R_checks=2808,
        actual_U_raw_commit_reset_checks=12132,actual_next_upper_full_local_R_checks=68,
        independent_full_Programme_phase_cofactors=54,independent_phase_full_local_R_checks=2646,
        actual_nonboolean_Programme_read_holder_checks=15,actual_delayed_read_following_full_local_R_checks=48,
        actual_Cprime_Aprime_and_F_Cprime_equals_F2_H=True,all_selected_complete2U_and_all_later_shadow=True,
        arbitrary_Programme_or_mixed16by16_repair_proved=False,faithful_Gray_or_iid_counterexample=False,
        new_CA_shorter_U_or_main_active_rule_modification=False,
        manifest_sha256=sha(path),aggregate_receipt_sha256=sha(D/'GAW16_word_burst_certificate.json'),
        elapsed_seconds=time.monotonic()-started)
    print(json.dumps(result),flush=True);return result

if __name__=='__main__':main()
