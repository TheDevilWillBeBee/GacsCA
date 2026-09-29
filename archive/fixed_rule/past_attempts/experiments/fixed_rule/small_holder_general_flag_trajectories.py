"""Exact GPU forcing/clearing trajectories with all two-colony Signal patterns."""
import argparse,hashlib,itertools,json,resource,time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import small_holder_flags_gpu as gpu,small_holder_rule as f


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def counts(raw):return [sum(int(v).bit_count() for v in raw[:,i]) for i in range(2)]


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();stem=Path(args.output)
    for ext in ('.json','.npz','.progress.json'):
        if stem.with_suffix(ext).exists():raise FileExistsError('preserve evidence')
    started=time.perf_counter();ages=(f.WF_START-1,f.WF_START,f.WF_START+1,f.WF_START+f.Q//2,f.WF_START+f.Q,f.WF_END-1,f.WF_END,f.WF_END+f.Q//2,f.WF_END+f.Q)
    frames=[];patterns=[];records=[];gpu_seconds=0.;device_bytes=0
    for case,pattern in enumerate(itertools.product((0,1),repeat=4)):
        right=pattern[:2];left=pattern[2:];saved=[];rows=[]
        with gpu.World(right,left) as world:
            device_bytes=max(device_bytes,world.device_bytes)
            for age in ages:
                tick=time.perf_counter();world.run(age-world.age);gpu_seconds+=time.perf_counter()-tick
                raw=world.read();saved.append(raw);rows.append(dict(age=age,counts=counts(raw)))
                if age>=f.WF_END+f.Q//2:assert not np.any(raw[:,0])
                if age>=f.WF_END+f.Q:assert not np.any(raw)
            # Previous restricted profile would incorrectly force these bits to zero.
            if any(left):assert any(row['counts'][1] for row in rows)
        patterns.append(pattern);frames.append(saved);records.append(dict(right=right,left=left,frames=rows))
        stem.with_suffix('.progress.json').write_text(json.dumps(dict(status='running',cases_complete=case+1,gpu_run_seconds=gpu_seconds))+'\n')
    # Bound from arbitrary initial F1/F2, not just an already organized front.
    rng=np.random.default_rng(551);random_initial=rng.integers(0,2**64,size=(3*gpu.WORDS,2),dtype=np.uint64)
    bound=[]
    with gpu.World((1,0,1),(1,1,0),age=f.WF_END,initial=random_initial) as world:
        for age in (f.WF_END+f.Q//2,f.WF_END+f.Q):
            tick=time.perf_counter();world.run(age-world.age);gpu_seconds+=time.perf_counter()-tick;raw=world.read();bound.append(raw)
            assert not np.any(raw[:,0])
            if age==f.WF_END+f.Q:assert not np.any(raw)
        device_bytes=max(device_bytes,world.device_bytes)
    np.savez_compressed(stem.with_suffix('.npz'),ages=np.array(ages,dtype=np.uint64),patterns=np.array(patterns,dtype=np.uint8),frames=np.array(frames),random_initial=random_initial,random_clearing=np.array(bound))
    result=dict(passed=True,cases=records,signal_patterns=16,each_case_physical_sites=2*f.Q,each_case_physical_ticks=3*f.Q+1,random_clearing_sites=3*f.Q,random_clearing_ticks=f.Q,gpu_run_seconds=gpu_seconds,seconds=time.perf_counter()-started,explicit_flag_device_bytes=device_bytes,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,descriptor_sha256=f.self_description().digest(),source_sha256={str(path):sha(path) for path in (Path(__file__),Path(gpu.__file__),Path(gpu.__file__).with_suffix('.cu'))},binary_sha256=sha(gpu.library()._name),artifact_sha256=sha(stem.with_suffix('.npz')),scope='exact physical flag projection on canonical geometry with coherent fixed Signals; all two-colony patterns and an arbitrary-flag clearing test; controller execution and noisy geometry are separate obligations')
    stem.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');stem.with_suffix('.progress.json').write_text(json.dumps(dict(status='complete'))+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('cases','source_sha256')},indent=2),flush=True)


if __name__=='__main__':main()
