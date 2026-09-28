"""Correlated physical initial faults through complete depth-two GPU endpoints.

All cases start from the healthy physical encoding. Explicit bottom bit faults
are applied before device decoding. The fixed transition implementation and
complete retained-output pipeline are unchanged across cases.
"""
import argparse,hashlib,json,resource,time
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import retimed_holder_endpoint_tiles as gpu,retimed_holder_endpoint_gpu as base
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_projected as r,retimed_holder_program as p,retimed_holder_native as native
from gacsca.fixed_rule import retimed_holder_terminal_dag as dag,retimed_holder_terminal_reference as replay,retimed_holder_terminal_image as image
from gacsca.fixed_rule import retimed_holder_initial_info_faults as faults,retimed_holder_endpoint_image_array as audit_image
from gacsca.fixed_rule.wordcode import Program


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(8*1024**2),b''):h.update(block)
    return h.hexdigest()


def guard():
    stack=ExitStack()
    for module,name in ((Program,'evaluate'),(f,'local_step'),(r,'local_step'),(r,'step_ring'),(native,'local_step'),(dag,'terminal'),(replay,'terminal'),(image.Image,'cell')):
        stack.enter_context(patch.object(module,name,side_effect=AssertionError('host transition or physical reconstruction during GPU evolution')))
    return stack


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);parser.add_argument('--case',choices=('healthy','two','three'),required=True);parser.add_argument('--periods',type=int,choices=(1,2),default=2);args=parser.parse_args()
    out=Path(args.output);stem=out.with_suffix('');initial_path=Path(str(stem)+'_initial_info.npy');artifact=Path(str(stem)+'_small.npz')
    banks=[Path(str(stem)+f'_period{k}_bank.npy') for k in range(1,args.periods+1)]
    if any(x.exists() for x in (out,initial_path,artifact,*banks)):raise FileExistsError('preserve all outputs')
    started=time.perf_counter();g=p.layout();seed=None
    fixture_path=Path('figs/fixed_rule/retimed_holder_depth2_repair_fixture_v1.json');fixture=json.loads(fixture_path.read_text());assert fixture['passed']
    assert sha(fixture_path.with_suffix('.npz'))==fixture['artifact_sha256']
    for name,digest in fixture['source_sha256'].items():assert sha(name)==digest,name
    with np.load(fixture_path.with_suffix('.npz'),allow_pickle=False) as z:
        healthy=(r.project(f.decode_cell(z['healthy'])),)
        top=healthy if args.case=='healthy' else (r.project(f.decode_cell(z['dirty_'+args.case])),)
        bit_faults=np.empty((0,3),dtype=np.uint64) if args.case=='healthy' else z[args.case+'_physical_faults'].copy()
    raw=lambda cells:np.array([f.encode_cell(r.lift(x)) for x in cells],dtype=np.uint64)
    expected=[top]
    for _ in range(args.periods):expected.append(r.step_ring(expected[-1]))
    saved=dict(initial_top=raw(top),healthy_initial_top=raw(healthy),physical_bit_faults=bit_faults);results=[]
    sources=[Path(__file__),Path(faults.__file__),Path(audit_image.__file__),Path(gpu.__file__),Path(gpu.__file__).with_suffix('.cu'),Path(base.__file__),Path(base.__file__).with_suffix('.cu')]
    gpu.library();peak_device=0;gpu_seconds=0.;initial_seconds=0.;tile_size=128;sites=f.Q*f.Q;fields=tuple(g.info)
    with gpu.Window(tile_size) as window,gpu.Source.raw(raw(healthy)) as original:
        # The initialized physical configuration is E_loc(E_loc(top)). Its lower
        # complete raw Info is the actual complete upper initial physical state.
        with original.initial_image() as encoded:
            initial=np.lib.format.open_memmap(initial_path,mode='w+',dtype=np.uint64,shape=(encoded.n,f.FIELDS))
            tick=time.perf_counter()
            with guard():
                for start in range(0,encoded.n,tile_size):
                    count=min(tile_size,encoded.n-start);initial[start:start+count]=window.cells(encoded,start,count)
            fault_statistics=faults.apply(initial,bit_faults)
            # Upload the actual damaged initial Info, then decode it. The damaged
            # top oracle is not used as a replacement for these physical changes.
            with gpu.Source.raw(initial) as actual_middle:
                with guard():current=window.decode(actual_middle);decoded_initial=window.cells(current,0,current.n)
                peak_device=max(peak_device,window.device_bytes+original.device_bytes+encoded.device_bytes+actual_middle.device_bytes+current.device_bytes)
                assert peak_device<=64*1024**2
            np.testing.assert_array_equal(decoded_initial,raw(top))
            # Establish the *whole* nested entry domain, not just its top decode.
            entry=np.zeros((1,g.memory_count+5),dtype=np.uint64);entry[:,list(g.info)]=decoded_initial
            np.testing.assert_array_equal(initial,audit_image.render(entry,np.zeros((1,2),dtype=np.uint64),0))
            initial_seconds=time.perf_counter()-tick;initial.flush();del initial
            saved['actual_device_decoded_initial_top']=decoded_initial
        try:
            for epoch in range(1,args.periods+1):
                period_started=time.perf_counter();top_before=window.cells(current,0,current.n)
                np.testing.assert_array_equal(top_before,raw(expected[epoch-1]));saved[f'period{epoch}_input_top']=top_before
                with guard():
                    tick=time.perf_counter();window.evaluate(current,0,current.n);upper_C=window.freeze_image();gpu_seconds+=time.perf_counter()-tick
                    bank_C,signals_C=window.read()
                    tick=time.perf_counter();window.evaluate(current,0,current.n,committed=True);upper_B=window.freeze_image();gpu_seconds+=time.perf_counter()-tick
                    bank_B,signals_B=window.read()
                saved[f'period{epoch}_upper_C_bank']=bank_C;saved[f'period{epoch}_upper_B_bank']=bank_B;saved[f'period{epoch}_upper_signals']=signals_B
                # The complete bottom output is retained, not reconstructed from
                # its decoded result. A GPU sink collects its actual raw Info.
                with upper_C,upper_B,gpu.Source.empty_raw(upper_C.n) as decoded_upper:
                    combined=window.device_bytes+original.device_bytes+current.device_bytes+upper_C.device_bytes+upper_B.device_bytes+decoded_upper.device_bytes
                    peak_device=max(peak_device,combined);assert peak_device<=64*1024**2
                    output=np.lib.format.open_memmap(banks[epoch-1],mode='w+',dtype=np.uint64,shape=(upper_C.n,g.memory_count+5))
                    all_signals=np.empty((upper_C.n,2),dtype=np.uint64);tile_hashes=[];samples=[];sample_positions=[]
                    wanted_samples={0,1,g.info[0]-1,g.info[0],g.hold[0],g.info[-1],g.hold[-1],g.memory_count-1,g.memory_count,g.computation_cells-1,g.computation_cells,f.Q-5,f.Q-3,f.Q-1}
                    for start in range(0,upper_C.n,tile_size):
                        count=min(tile_size,upper_C.n-start);tick=time.perf_counter()
                        with guard():
                            window.evaluate(upper_C,start,count,committed=True)
                            bank,signals=window.read();window.collect_info(decoded_upper)
                            expected_upper=window.cells(upper_B,start,count)
                        gpu_seconds+=time.perf_counter()-tick
                        np.testing.assert_array_equal(bank[:,fields],expected_upper,err_msg='every raw field across the inner simulation link')
                        output[start:start+count]=bank;all_signals[start:start+count]=signals
                        tile_hashes.append(hashlib.sha256(bank.tobytes()).hexdigest())
                        for pos in sorted(wanted_samples.intersection(range(start,start+count))):sample_positions.append(pos);samples.append(bank[pos-start].copy())
                    assert decoded_upper.ready and decoded_upper.progress==f.Q
                    tick=time.perf_counter()
                    with guard():following=window.decode(decoded_upper);actual_top=window.cells(following,0,following.n)
                    gpu_seconds+=time.perf_counter()-tick
                    peak_device=max(peak_device,combined+following.device_bytes)
                    np.testing.assert_array_equal(actual_top,raw(expected[epoch]));assert np.any(actual_top!=top_before)
                    saved[f'period{epoch}_output_top']=actual_top;saved[f'period{epoch}_signals']=all_signals
                    saved[f'period{epoch}_sample_positions']=np.array(sample_positions,dtype=np.uint64);saved[f'period{epoch}_sample_banks']=np.array(samples,dtype=np.uint64)
                    saved[f'period{epoch}_tile_hashes']=np.array(tile_hashes)
                    output.flush();del output
                current.close();current=following
                results.append(dict(period=epoch,represented_physical_time=epoch*f.U*f.U,all_lower_bank_words_stored=f.Q*(g.memory_count+5),all_intermediate_raw_words_checked=f.Q*f.FIELDS,complete_top_raw_fields_checked=f.FIELDS,actual_top_words_changed=int(np.count_nonzero(actual_top!=top_before)),seconds=time.perf_counter()-period_started,gpu_calls_seconds_so_far=gpu_seconds,bank_path=str(banks[epoch-1])))
                print(json.dumps(results[-1]),flush=True)
        finally:current.close()
    np.savez_compressed(artifact,**saved)
    result=dict(passed=True,case=args.case,fixture=str(fixture_path),fixture_sha256=sha(fixture_path),physical_fault_statistics=fault_statistics,seed=seed,initial_encoded_depth=2,top_cells=1,physical_sites=sites,periods=args.periods,represented_physical_ticks=args.periods*f.U*f.U,period_results=results,initial_encoding_seconds=initial_seconds,gpu_calls_seconds=gpu_seconds,peak_explicit_device_bytes=peak_device,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,seconds_before_hashing=time.perf_counter()-started,descriptor_sha256=f.self_description().digest(),rom_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest(),initial_info_path=str(initial_path),initial_info_sha256=sha(initial_path),small_artifact_path=str(artifact),small_artifact_sha256=sha(artifact),bank_sha256={str(path):sha(path) for path in banks},source_sha256={str(path):sha(path) for path in sources},binary=str(gpu.library()._name),binary_sha256=sha(gpu.library()._name),no_host_simulated_transition=True,following_top_decoded_from_actual_GPU_output=True,complete_bottom_banks_retained=True,scope='Complete depth-two GPU endpoints after explicit correlated initial physical bit faults that remain inside the verified nested entry domain. Every subsequent interval is noiseless. No general stochastic threshold, arbitrary fault-time evolution or robust-cap claim.')
    result['seconds']=time.perf_counter()-started
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
