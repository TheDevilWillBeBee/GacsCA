"""Read-only original-c104 large-history replay, including illegal U scope."""
from pathlib import Path
from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader,module_from_spec
import hashlib,json,subprocess,sys,tempfile,time
S=Path(__file__).resolve().parent;ROOT=S.parents[3]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw17'
sys.path.insert(0,str(S))
import search_gaw17_large_bursts as m
import continue_gaw17_large_bursts as full
import check_gaw17_padding_lineage as padding
import certify_gaw17_large_bursts as cert

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name):return json.loads((D/name).read_text())
def assets(v):
    for p,h in v['assets_sha256'].items():assert sha(ROOT/p)==h,(p,'frozen asset differs')
def same(a,b,label):assert m.previous.stable(a)==m.previous.stable(b),(label,'exact replay differs')
def announce(stage,**more):print(json.dumps(dict(stage=stage,**more)),flush=True)

def serialization_failure():
    f=load('GAW17_failure_provenance.json');assets(f)
    assert f['planned_support_audit_passed_before_serialization'] and f['no_actual_trajectory_was_run']
    assert f['no_classifier_CA_or_mathematical_classification_changed']
    loader=SourceFileLoader('gaw17_classification01_snapshot',str(S/'search_gaw17_large_bursts.py.classification01_snapshot'))
    spec=spec_from_loader(loader.name,loader);old=module_from_spec(spec);loader.exec_module(old)
    raw=old.support_audit()
    try:json.dumps(raw)
    except TypeError as ex:assert str(ex)=='Object of type int64 is not JSON serializable'
    else:raise AssertionError('retained classifier serialization failure no longer reproduced')
    converted=json.loads(json.dumps(raw,default=lambda v:v.item()))
    same(converted,load('GAW17_support_classification.json'),'same old/new classification, exact scalar conversion')
    same(m.support_audit(),converted,'all planned dense and sparse supports')

def main():
    started=time.monotonic();path=D/'GAW17_standalone_assets.json';manifest=load(path.name);assets(manifest)
    ancestor=ROOT/manifest['inherited_manifest'];inherited=json.loads(ancestor.read_text());assets(inherited)
    assert manifest['inherited_assets']==len(inherited['assets_sha256'])==443
    assert all(manifest['assets_sha256'][p]==h for p,h in inherited['assets_sha256'].items())
    assert manifest['assets_sha256'][str(ancestor.relative_to(ROOT))]==sha(ancestor)
    assert (m.k.Q,m.k.U,m.P,m.T)==(8192,1048576,3848,839681)
    issued=load('GAW17_large_burst_certificate.json')
    for p,h in issued['dependencies_sha256'].items():assert manifest['assets_sha256'][p]==h and sha(ROOT/p)==h
    serialization_failure();announce('retained_pretrajectory_serialization_failure_and_exact_classification_replayed')
    source=ROOT/'Report/proofs/gray_counterexamples/unregistered_gaw15/gaw15_native.c'
    old_dir=ROOT/'figs/gray_counterexamples/unregistered_gaw15'
    with tempfile.TemporaryDirectory(prefix='gaw17_readonly_replay_') as temp:
        t=Path(temp);native=t/'gaw15_native.so'
        subprocess.run(['gcc','-O3','-std=c11','-shared','-fPIC','-I',str(source.parent),str(source),'-o',str(native)],check=True,cwd=ROOT)
        assert sha(native)==sha(old_dir/'gaw15_native.so'),'rebuilt frozen diagnostic binary differs'
        announce('all_frozen_hashes_and_exact_native_binary_verified',assets=len(manifest['assets_sha256']))
        saved=m.previous.D;m.previous.D=t
        try:
            for recipe in m.recipes():
                actual,_=m.run(recipe,limit=32);same(actual,load(recipe['tag']+'_discovery.json'),recipe['tag']+' original32')
                announce('bounded_discovery_replayed',tag=recipe['tag'])
            for recipe in m.recipes():
                actual=full.run(recipe);same(actual,load(recipe['tag']+'_complete.json'),recipe['tag']+' actual full history')
                b=actual['actual_U_and2U_boundary']
                announce('complete_actual_history_replayed',tag=recipe['tag'],rows=len(actual['actual_rows']),
                    bad_U=b['actual_U_bad_normal_receivers'],illegal_native_words=len(b['actual_U_illegal_native_words']),
                    second_boundary='proved shadow' if b['actual_U_legal_E_encoding'] else 'unproved; no legal-upper theorem')
            same(padding.check(),load('GAW17_padding_lineage_certificate.json'),'actual Programme to native-Age Out lineage')
            announce('actual_delayed_native_padding_write_replayed')
        finally:m.previous.D=saved
    same(cert.check(),issued,'aggregate legal/illegal boundary scopes');assets(manifest);assets(inherited)
    witness=load('GAW17_padding_lineage_certificate.json')
    assert witness['actual_native_Age_primary']==3849 and witness['actual_later_Out_time']==839787
    assert len(witness['actual_following_full_local_R_checks'])==224
    r=dict(passed=True,assets_verified=len(manifest['assets_sha256']),inherited_assets_verified=443,
        exact_frozen_local_R_own_ROM_and_rebuilt_native_binary=True,
        actual_recursive_intact_H_and_all_future_WF_SF_derived=True,
        original_real1_complete_histories=5,genuine_whole_cell_replacements=54082,
        original_dense104by104_histories=4,sparse_span150_by104_history=1,
        dense150by104_rejected_and_not_executed=True,pretrajectory_serialization_failure_replayed=True,
        bounded32row_discoveries_replayed=5,actual_total_prefix_rows=20547,
        actual_prefix_full_local_R_checks=9239,actual_U_commit_reset_checks=15166,
        actual_next_upper_full_local_R_checks=52,actual_delayed_native_padding_following_checks=224,
        four_legal_U_adjacent_pair_and_full2U_shadow=True,
        actual_illegal_U_Age_Flag_WF_record_and_narrow_E_obstruction=True,
        illegal_case_decoder_2U_eventual_repair_or_memory_failure_proved=False,
        universal_mixed_repair_or_Gray_iid_counterexample=False,
        new_CA_shorter_U_or_main_active_rule_modification=False,
        manifest_sha256=sha(path),aggregate_receipt_sha256=sha(D/'GAW17_large_burst_certificate.json'),
        elapsed_seconds=time.monotonic()-started)
    print(json.dumps(r),flush=True);return r

if __name__=='__main__':main()
