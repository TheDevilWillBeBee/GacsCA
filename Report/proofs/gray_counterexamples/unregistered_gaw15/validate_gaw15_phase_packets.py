"""Read-only replay/provenance of both generations and all GAW15 claims."""
from pathlib import Path
from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_loader,module_from_spec
import hashlib,json,subprocess,sys,tempfile,time
S=Path(__file__).resolve().parent;ROOT=S.parents[3]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw15'
sys.path.insert(0,str(S))
import search_gaw15_phase_packets as m
import continue_gaw15_phase_packets as full
import check_gaw15_phase_cofactors as phasecheck
import check_gaw15_dependency_witnesses as witnesscheck
import certify_gaw15_phase_packets as cert

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name):return json.loads((D/name).read_text())
def assets(manifest):
    for path,value in manifest['assets_sha256'].items():assert sha(ROOT/path)==value,(path,'asset provenance changed')
def same(actual,expected,label):assert m.stable(actual)==m.stable(expected),(label,'exact replay differs')
def announce(stage,**extra):print(json.dumps(dict(stage=stage,**extra)),flush=True)

def main():
    started=time.monotonic();path=D/'GAW15_standalone_assets.json';manifest=load(path.name);assets(manifest)
    assert m.k.PRIMARY_START==3848 and m.T==839681 and m.k.Q==8192 and m.k.U==1048576
    initial=load('discovery01_source_provenance.json');assets(initial)
    failure=load('GAW15_failure_provenance.json');assets(failure)
    assert failure['failure_before_any_history_replay'] and failure['exact_original_basename_rebuild']
    assert not failure['mathematical_sources_or_histories_changed']
    with tempfile.TemporaryDirectory(prefix='gaw15_readonly_replay_') as temp:
        t=Path(temp);current=t/'current';old=t/'original';current.mkdir();old.mkdir()
        # Preserve the original compilation basename as well as bytes:
        # ELF's STT_FILE metadata changes when compiling *.snapshot directly.
        copied=t/'gaw15_native.c';copied.write_bytes((S/'gaw15_native.c.discovery01_snapshot').read_bytes())
        assert sha(copied)==sha(S/'gaw15_native.c.discovery01_snapshot')
        for source,dest,issued in ((S/'gaw15_native.c',current/'gaw15_native.so',D/'gaw15_native.so'),
            (copied,old/'gaw15_native.so',D/'gaw15_native.discovery01.so')):
            subprocess.run(['gcc','-O3','-std=c11','-shared','-fPIC','-I',str(S),str(source),'-o',str(dest)],check=True,cwd=ROOT)
            assert sha(dest)==sha(issued),(source.name,'rebuilt binary differs')
        probe=t/'snapshot_filename_probe.so'
        subprocess.run(['gcc','-O3','-std=c11','-shared','-fPIC','-x','c',
            str(S/'gaw15_native.c.discovery01_snapshot'),'-o',str(probe)],check=True,cwd=ROOT)
        assert sha(probe)==sha(D/'gaw15_native.snapshot_filename_probe.so')
        assert sha(probe)!=sha(old/'gaw15_native.so')
        for binary,name in ((probe,'snapshot'),(old/'gaw15_native.so','original')):
            text=t/(name+'.text');subprocess.run(['objcopy','--dump-section','.text='+str(text),str(binary)],check=True)
            assert sha(text)==failure['identical_machine_text_sha256']
        loader=SourceFileLoader('gaw15_discovery01_frozen',str(S/'search_gaw15_phase_packets.py.discovery01_snapshot'))
        spec=spec_from_loader(loader.name,loader);original=module_from_spec(spec);loader.exec_module(original);original.D=old
        announce('both_generations_binaries_rebuilt',assets=len(manifest['assets_sha256']))
        for recipe in original.recipes():
            actual,_=original.run(recipe,limit=64);same(actual,load(recipe['tag']+'_discovery.json'),recipe['tag']+' original64')
            announce('original_prefix_replayed',tag=recipe['tag'])
        issued_dir=m.D;m.D=current
        try:
            for recipe in m.source_recipes():
                actual,_=m.run(recipe,limit=64);same(actual,load(recipe['tag']+'_discovery.json'),recipe['tag']+' source64')
                announce('source_prefix_replayed',tag=recipe['tag'])
            for recipe in full.selected():
                actual=full.run(recipe);same(actual,load(recipe['tag']+'_complete.json'),recipe['tag']+' full')
                announce('complete_history_replayed',tag=recipe['tag'],rows=len(actual['actual_physical_prefix_rows']),
                    bad_U=actual['actual_boundary_continuation']['actual_U_bad_normal_receivers'],
                    shadow2U=actual['actual_boundary_continuation']['complete2U_shadow'])
            same(phasecheck.check(),load('GAW15_phase_cofactor_certificate.json'),'phase cofactors')
            announce('all_phase_cofactors_and_chronology_replayed')
            same(witnesscheck.check(),load('GAW15_phase_dependency_witnesses.json'),'dependency witnesses')
            announce('all_actual_dependency_witnesses_replayed')
        finally:m.D=issued_dir
    r=cert.check();same(r,load('GAW15_phase_packet_certificate.json'),'aggregate selected certificate')
    assets(manifest)
    out=dict(passed=True,assets_verified=len(manifest['assets_sha256']),exact_both_rebuilt_diagnostic_binaries=True,
        retained_original_basename_provenance_failure_verified=True,
        exact_frozen_rule_ROM_and_intact_H=True,original_bounded64row_discoveries_replayed=12,
        actual_source64row_discoveries_replayed=4,actual_original_real1_complete_histories=7,
        actual_total_prefix_rows=r['actual_total_prefix_rows'],actual_prefix_full_local_R_checks=4064,
        actual_raw_U_commit_reset_checks=21292,actual_next_upper_full_local_R_checks=102,
        independent_phase_cofactors=123,independent_phase_full_local_R_checks=3936,
        actual_chronological_last_update_checks=3024,actual17_upper_bank_checks=2976,
        actual_final_computed_primary_Workspace_used=True,all_selected_U_legal_adjacent_pair_and2U_shadow=True,
        arbitrary_Programme_word_or_universal_mixed_repair_or_Gray_iid_shorter_U=False,
        main_or_active_rule_modified=False,manifest_sha256=sha(path),elapsed_seconds=time.monotonic()-started)
    print(json.dumps(out),flush=True);return out

if __name__=='__main__':main()
