"""Complete bottom checkpoints and timed encoded faults in a live middle program.

All cases use the same previously validated fixed GPU endpoint operator.
Complete retained banks and explicit physical pulses define each physical state.
"""
import argparse,json,resource,time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import compact16_holder_endpoint_tiles as gpu,compact16_holder_rule as f,compact16_holder_program as p
from gacsca.fixed_rule import compact16_holder_checkpoint_pulse as pulse
from experiments.fixed_rule.run_compact16_holder_streamed_depth2 import sha,guard


FIXTURE=Path('figs/fixed_rule/compact16_holder_active_faults_v1.json')
BASE=Path('figs/fixed_rule/compact16_holder_timed_depth2_checkpoint_v1.json')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--case',choices=('checkpoint','healthy','two','three'),required=True);parser.add_argument('--output',required=True);args=parser.parse_args()
    out=Path(args.output);stem=out.with_suffix('');small=Path(str(stem)+'_small.npz');steps=2 if args.case in ('healthy','two') else 1
    paths=[Path(str(stem)+f'_step{k}_bank.npy') for k in range(1,steps+1)]
    if any(x.exists() for x in (out,small,*paths)):raise FileExistsError('preserve evidence')
    started=time.perf_counter();g=p.layout();receipt=json.loads(FIXTURE.read_text());assert receipt['passed']
    assert sha(FIXTURE.with_suffix('.npz'))==receipt['artifact_sha256']
    saved={};expected=[];age=receipt['age'];pulse_bits=np.empty((0,3),dtype=np.uint64);updates=np.empty((0,3),dtype=np.uint64)
    with np.load(FIXTURE.with_suffix('.npz'),allow_pickle=False) as fixture:
        if args.case=='checkpoint':
            current=fixture['previous_raw'].copy();expected=[fixture['checkpoint_raw'].copy()];entry_time=(age-1)*f.U
        else:
            base=json.loads(BASE.read_text());assert base['passed'] and base['case']=='checkpoint'
            basepath=Path(base['bank_paths'][0]);assert sha(basepath)==base['bank_sha256'][str(basepath)]
            bank=np.load(basepath,mmap_mode='r',allow_pickle=False)
            if args.case in ('two','three'):
                count=2 if args.case=='two' else 3;faults=[]
                for col,field,xor in fixture[f'case{count}_faults']:
                    primary=int(col)*f.Q+g.info[int(field)]
                    for d in f.OFFSETS:faults.append(((primary-d)%(f.Q*f.Q),f.COL[f's{d+2}_data'],int(xor)))
                pulse_bits=np.array(faults,dtype=np.uint64)
            current,updates=pulse.apply(bank,pulse_bits)
            # Verify the complete checkpoint input, including its active controller.
            wanted=fixture['checkpoint_raw'].copy()
            for col,address,xor in updates:wanted[int(col),g.info.index(int(address))]^=xor
            np.testing.assert_array_equal(current,wanted)
            expected=[fixture['after_raw'].copy(),fixture['second_raw'].copy()]
            if args.case=='three':
                expected=[fixture['case3_after'].copy()]
            del bank;entry_time=age*f.U
    saved['input_middle']=current.copy();saved['physical_faults']=pulse_bits;saved['bank_updates']=updates
    results=[];gpu_seconds=0.;peak=0;gpu.library()
    with gpu.Window(128) as window:
        for step,path in enumerate(paths,1):
            tick=time.perf_counter();bank=np.lib.format.open_memmap(path,mode='w+',dtype=np.uint64,shape=(f.Q,g.memory_count+5))
            following=np.empty((f.Q,f.FIELDS),dtype=np.uint64);signals=np.empty((f.Q,2),dtype=np.uint64)
            with gpu.Source.raw(current) as source:
                peak=max(peak,window.device_bytes+source.device_bytes);assert peak<64*1024**2
                for start in range(0,f.Q,128):
                    count=min(128,f.Q-start);at=time.perf_counter()
                    with guard():window.evaluate(source,start,count,committed=True);part,bits=window.read()
                    gpu_seconds+=time.perf_counter()-at
                    bank[start:start+count]=part;signals[start:start+count]=bits
                    # Transport actual device-output Info only; no host transition.
                    following[start:start+count]=part[:,g.info]
                np.testing.assert_array_equal(following,expected[step-1])
            bank.flush();del bank;saved[f'step{step}_signals']=signals;saved[f'step{step}_middle']=following
            row=dict(step=step,physical_time=entry_time+step*f.U,all_retained_bank_words=f.Q*(g.memory_count+5),all_middle_raw_words_checked=f.Q*f.FIELDS,seconds=time.perf_counter()-tick)
            results.append(row);print(json.dumps(row),flush=True)
            current=following # exact uploaded data from the actual preceding GPU output
    np.savez_compressed(small,**saved)
    sources=[Path(__file__),Path(pulse.__file__),Path(gpu.__file__),Path(gpu.__file__).with_suffix('.cu')]
    result=dict(passed=True,case=args.case,steps=steps,entry_physical_time=entry_time,pulse_physical_time=None if args.case=='checkpoint' else entry_time,physical_bit_faults=len(pulse_bits),changed_Info_words=len(updates),middle_age=age,physical_sites=f.Q*f.Q,fixture=str(FIXTURE),fixture_sha256=sha(FIXTURE),complete_checkpoint=None if args.case=='checkpoint' else str(BASE),complete_checkpoint_receipt_sha256=None if args.case=='checkpoint' else sha(BASE),period_results=results,gpu_calls_seconds=gpu_seconds,explicit_GPU_peak_bytes=peak,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,bank_paths=list(map(str,paths)),bank_sha256={str(path):sha(path) for path in paths},small_artifact=str(small),small_sha256=sha(small),source_sha256={str(path):sha(path) for path in sources},descriptor_sha256=f.self_description().digest(),rom_sha256=__import__('hashlib').sha256(p.base_rom().tobytes()).hexdigest(),binary=str(gpu.library()._name),binary_sha256=sha(gpu.library()._name),scope='Exact complete bottom endpoint checkpoints during an actually running middle evaluator, followed by explicit coherent Info pulses. Fault-free lower intervals use the proved complete-state terminal identity; no literal U replay or general noise theorem.')
    result['seconds']=time.perf_counter()-started;out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__':main()
