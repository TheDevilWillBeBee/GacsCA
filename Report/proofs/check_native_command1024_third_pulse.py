#!/usr/bin/env python3
"""Full finite native third-pulse certificate; no general eroder/iid claim."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib,importlib.util,json,re,struct,subprocess,sys,tempfile,time
import numpy as np
ROOT=Path(__file__).resolve().parents[2];S=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT),str(S),str(S/'unregistered_sp31_third_sources')]
import proposed_native_command1024 as proposed
import check_sp31_third_dense_exploration as gpu
OUT=ROOT/'figs/robustness';D=OUT/'unregistered_sp31_third_gpu';PROOF=S/'SP31_THIRD_PULSE.md'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical_cuda_binary(path):
    """Ignore only nvcc's PID in one nonallocated STT_FILE string.

    All ELF headers/sections, host instructions and device fatbin remain
    byte-compared. No loaded byte or executable metadata is normalized.
    """
    data=bytearray(Path(path).read_bytes());assert data[:6]==b'\x7fELF\x02\x01'
    offset=struct.unpack_from('<Q',data,40)[0]
    size,num,names=struct.unpack_from('<3H',data,58)
    assert size==64
    sections=[struct.unpack_from('<IIQQQQIIQQ',data,offset+i*size) for i in range(num)]
    sh=sections[names];strings=data[sh[4]:sh[4]+sh[5]]
    named={bytes(strings[s[0]:]).split(b'\0',1)[0]:s for s in sections}
    s=named[b'.strtab'];assert s[1]==3 and not s[2]&2 # SHT_STRTAB, !SHF_ALLOC
    a,b=s[4],s[4]+s[5];old=bytes(data[a:b])
    new,count=re.subn(rb'tmpxft_[0-9a-f]{8}_00000000-6_sp31_third_dense\.cudafe1\.cpp',
        b'tmpxft_00000000_00000000-6_sp31_third_dense.cudafe1.cpp',old)
    assert count==1 and len(old)==len(new)
    data[a:b]=new;return bytes(data)
def canonical_states(run,selected):
    meta,masks,metrics,nc,ic,tr,ip,indices=run
    return [(sorted(tr[row,selected,:int(nc[row,selected])].tolist()),sorted(ip[row,selected,:int(ic[row,selected])].tolist())) for row in range(meta['ticks']+1)]
def main():
    start=time.monotonic();p=proposed.parameters();c=proposed.load_artifact()
    sources=json.loads((OUT/'SP31_third_source_enclosure_certificate.json').read_text())
    assert sources['candidate_sha256']==c.digest() and sources['actual_full_third_source_enclosure_proved']
    assert sources['third_Flag2_enclosure_free_bits']==12 and sources['third_source_enclosure_members']==4096
    exploration_path=D/'exploration_receipt.json';exploration=json.loads(exploration_path.read_text())
    assert exploration['all4096_execution']['masks']==4096 and exploration['all4096_execution']['all_row_records']==25169920
    assert exploration['CUDA_source_sha256']==sha(S/'unregistered_sp31_third_sources/sp31_third_dense.cu')
    assert exploration['checker_sha256']==sha(gpu.__file__) and exploration['source_certificate_sha256']==sha(OUT/'SP31_third_source_enclosure_certificate.json')
    for name,value in exploration['assets_sha256'].items():assert sha(ROOT/name)==value
    old=gpu.load(D/'all4096');assert old[1].tolist()==list(range(4096))
    oldmetrics=old[2]
    assert oldmetrics.shape==(4096,6145,9) and not np.any(oldmetrics[:,:,8])
    assert np.all(oldmetrics[:,-1,0]==3584) and np.all(oldmetrics[:,-1,3]==1024) and not np.any(oldmetrics[:,-1,4:7])
    assert np.all(np.max(oldmetrics[:,:,1],axis=1)==196608-144896) and np.all(np.max(oldmetrics[:,:,2],axis=1)==155648)
    replays=[]
    with tempfile.TemporaryDirectory(prefix='sp31-third-pulse-replay-') as temp:
        temp=Path(temp);binary=temp/'sp31_third_dense';reference=temp/'third_reference';refsrc=temp/'sp31_third_reference.c'
        build=subprocess.run(['/usr/local/cuda/bin/nvcc','-O3','-std=c++17','-arch=sm_89',str(S/'unregistered_sp31_third_sources/sp31_third_dense.cu'),'-o',str(binary)],capture_output=True,text=True)
        assert build.returncode==0 and build.stdout+build.stderr==(D/'build.log').read_text()
        assert canonical_cuda_binary(binary)==canonical_cuda_binary(D/'sp31_third_dense'),'CUDA executable differs beyond nonallocated compiler PID string'
        refsrc.write_text(gpu.generated_reference());assert refsrc.read_bytes()==(D/'reference/sp31_third_reference.c').read_bytes()
        build=subprocess.run(['gcc','-O3','-std=c11','-Wall','-Wextra',str(refsrc),'-o',str(reference)],capture_output=True,text=True)
        assert build.returncode==0
        assert (build.stdout+build.stderr).replace(str(refsrc),str(D/'reference/sp31_third_reference.c'))==(D/'reference/build.log').read_text()
        assert sha(reference)==sha(D/'reference/third_reference'),'C binary rebuild differs'
        target=temp/'all4096';target.mkdir()
        def rerun_gpu():
            proc=subprocess.run([str(binary),str(target),'0','4096','6144'],capture_output=True,text=True)
            assert proc.returncode==0,proc.stderr[-4000:]
            new=gpu.load(target);assert new[1].tolist()==old[1].tolist() and np.array_equal(new[2],oldmetrics)
            assert np.array_equal(new[3],old[3]) and np.array_equal(new[4],old[4]) and np.array_equal(new[7],old[7])
            for k in range(4):assert canonical_states(new,k)==canonical_states(old,k)
            return dict(all4096_masks_replayed=True,all25169920_row_metrics_equal=True,
                selected_whole_states_equal=True,rebuilt_executable_identical_except_nonallocated_nvcc_PID_string=True,seconds=new[0]['seconds'])
        def rerun_c(mask):
            trace=temp/f'mask{mask}_trace.jsonl';state=temp/f'mask{mask}_state.bin'
            with trace.open('w') as fh:proc=subprocess.run([str(reference),str(mask),'6144',str(state)],stdout=fh,stderr=subprocess.PIPE,text=True)
            assert proc.returncode==0 and proc.stderr==(D/'reference'/f'mask{mask}_stderr.log').read_text()
            assert state.read_bytes()==(D/'reference'/f'mask{mask}_state.bin').read_bytes()
            assert trace.read_bytes()==(D/'reference'/f'mask{mask}_trace.jsonl').read_bytes()
            return dict(mask=mask,all6145_full_state_and_trace_records_equal=True,rebuilt_binary_identical=True)
        with ThreadPoolExecutor(max_workers=5) as pool:
            future=pool.submit(rerun_gpu);others=[pool.submit(rerun_c,m) for m in (0,2047,2048,4095)]
            replays=[f.result() for f in others];gpureplay=future.result()
    # Independent retained selected C/native/Info comparisons, beyond counts.
    pilot=gpu.load(D/'pilot')
    for k,mask in enumerate((0,2047,2048,4095)):
        assert gpu.compare_reference(pilot,D/'reference'/f'mask{mask}_state.bin',k)==exploration['pilot_whole_state_replays'][k]
    result=dict(proposal='SP31',scope='Same actual J225 original-c16 native-only dense16Q real2/all initial upperInfo/no latererrors; all4096 third native pulse and quiet3U reset boundary',
        Q=p.Q,U=p.U,T_wf=p.T_wf,radius=37,candidate_sha256=c.digest(),netlist_sha256=c.comp.digest,
        checker_sha256=sha(__file__),proof_sha256=sha(PROOF),exploration_receipt_sha256=sha(exploration_path),
        source_dependencies_sha256={str(path.relative_to(ROOT)):sha(path) for path in (Path(gpu.__file__),S/'unregistered_sp31_third_sources/sp31_third_dense.cu',S/'unregistered_sp31_third_sources/sp31_third_enclosure_cases.c',S/'sp31_two_flag2_sources.c',ROOT/'gacsca/rule_g.py',ROOT/'gacsca/netlist.py',Path(proposed.__file__))},
        proof_dependencies_sha256={name:sha(S/name) for name in ('SP31_OWN_RULE.md','SP31_FIRST_PULSE.md','SP31_SECOND_PULSE.md','SP31_THIRD_SOURCE_ENCLOSURE.md')},
        receipt_dependencies_sha256={name:sha(OUT/name) for name in ('SP31_encoded_certificate.json','SP31_third_source_enclosure_certificate.json','SP31_interface_certificate.json','SP31_symbolic_schedule.json')},
        retained_exact_execution_assets_sha256=exploration['assets_sha256'],retained_exploration_run_sha256=sha(OUT/'SP31_third_dense_exploration_run.log'),
        CUDA_canonical_executable_sha256=hashlib.sha256(canonical_cuda_binary(D/'sp31_third_dense')).hexdigest(),
        retained_initial_binary_provenance_diagnostics_sha256={str(path.relative_to(ROOT)):sha(path) for path in
            (D/'initial_checker_binary_hash.py.txt',D/'initial_binary_hash_failure.log',D/'sp31_third_dense_rebuild_relative',D/'rebuild_relative.log',D/'rebuild_relative/sp31_third_dense',D/'rebuild_relative/build.log',D/'initial_checker_build_path.py.txt',D/'initial_build_path_failure.log')},
        native_integer_kernel_clause_correspondence_proved=True,every_row_zero_border_infinite_extension_proved=True,
        finite_domain=[81920,196608],border_width=64,source_masks=4096,all_row_records=25169920,represented_native_cell_updates=2886218022912,
        GPU_full_readonly_replay=gpureplay,C_selected_full_readonly_replays=replays,selected_C_GPU_whole_state_rows=24580,
        initial_native_template=[142,149],endpoint_native_template=[149,152],initial_wrong_GF_width=7680,endpoint_wrong_GF_width=3584,GF_width_change=-4096,
        endpoint_segments=[[151552,152064,2],[152064,155136,1],[155136,155648,3]],all_case_GF_hulls=[144896,155648],
        third_source_physical_time=2*p.U+p.T_wf,third_pulse_endpoint_physical_time=2*p.U+p.T_wf+6144,third_boundary_physical_time=3*p.U,
        all4096_source_assignments_exactly_classified=True,actual_third_native_pulse_proved=True,
        actual_third_native_boundary_and807_private_alias_zero_reset_proved=True,
        all_initial_upper_Info_and_actual_unknown_vote_correlations_allowed=True,no_future_tape_or_Workspace_or_physical_boundary_supplied=True,
        all_source_masks_physically_reachable_proved=False,whole_upper_Info_successor_at3U_proved=False,fourth_actual_banks_sources_or_pulse_proved=False,
        repeated_bank_invariant_or_arbitrary_higher_repair_or_positive_iid_or_minimum_change_proved=False,
        additional_rule_change=False,active_G17_modified=False,Gray_or_G17_refutation=False,global_reliability_established=False,seconds=time.monotonic()-start)
    (OUT/'SP31_third_pulse_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,source_masks=4096,all_row_records=25169920,GPU_all_masks_replayed=True,
        selected_C_GPU_whole_state_rows=24580,actual_third_native_pulse_proved=True,endpoint_template=[149,152],GF_width_change=-4096,
        global_reliability_established=False,seconds=result['seconds'])),flush=True)
if __name__=='__main__':main()
