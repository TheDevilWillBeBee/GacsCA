"""Two whole periods from explicit reset data, with complete physical handoffs.

C(x,old Signals) is initialized once. Every later C(G(x)) comparison is read-only;
no encoded state or healthy reference is installed during evolution.
"""
import argparse
from dataclasses import replace
import hashlib,json,resource,time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import small_holder_reset_encoding as encoding
from gacsca.fixed_rule import small_holder_rule as f,small_holder_projected as r,small_holder_native as native,small_holder_core as c
from gacsca.fixed_rule import small_holder_resident_general as gpu
from experiments.fixed_rule.small_holder_execution import initial_ring
from experiments.fixed_rule.small_holder_temporal_repair import no_host,raw
from experiments.fixed_rule.small_holder_gather_two_periods import memory


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();stem=Path(args.output)
    for ext in ('.json','.npz','.progress.json'):
        if stem.with_suffix(ext).exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();parents=tuple(replace(x,f2=1,address=30000 if i==7 else x.address) for i,x in enumerate(initial_ring()))
    initial=encoding.Encoding(parents,left=tuple(i%2 for i in range(15)),right=tuple((i+1)%2 for i in range(15)))
    archive=dict(initial=raw(parents),initial_left=np.array(initial.left,dtype=np.uint64),initial_right=np.array(initial.right,dtype=np.uint64))
    checkpoints=[];seconds=0.;observed=[];verification_seconds=0.
    with gpu.World(parents,age=1,logical=initial.initial_records()) as world:
        tick=time.perf_counter();first=initial.verify(world);verification_seconds+=time.perf_counter()-tick
        observed.append(memory());expected=parents
        for period in range(2):
            expected=tuple(r.project(x) for x in native.step_ring(tuple(r.lift(x) for x in expected)))
            model=encoding.Encoding(expected);stop=(period+1)*f.U-1
            while world.time<stop:
                tick=time.perf_counter()
                with no_host():world.advance(min(c.T,stop-world.time))
                seconds+=time.perf_counter()-tick
                stem.with_suffix('.progress.json').write_text(json.dumps(dict(status='running',time=world.time,age=world.age,gpu_seconds=seconds))+'\n')
            assert world.age==0
            actual=world.decode();np.testing.assert_array_equal(raw(actual),raw(expected));archive[f'decoded{period+1}']=raw(actual)
            tick=time.perf_counter();before=model.verify(world,before_reset=True);verification_seconds+=time.perf_counter()-tick
            probe=tuple(col*f.Q+a for col in range(15) for a in (0,1,3,7,f.Q-5,f.Q-3,f.Q-1))
            archive[f'probe{period+1}']=np.array(probe,dtype=np.uint64)
            archive[f'before_reset{period+1}']=raw(world.physical_cells(probe))
            tick=time.perf_counter()
            with no_host():world.advance(1)
            seconds+=time.perf_counter()-tick
            tick=time.perf_counter();after=model.verify(world);verification_seconds+=time.perf_counter()-tick
            archive[f'after_reset{period+1}']=raw(world.physical_cells(probe))
            np.testing.assert_array_equal(archive[f'after_reset{period+1}'],raw(tuple(model.physical(pos) for pos in probe)))
            checkpoints.append(dict(period=period+1,physical_time=world.time,before_reset=before,after_reset=after,center_address=actual[7].address,center_data=actual[7].s2_data,all_decoded_raw_fields=True))
            observed.append(memory());print(json.dumps(checkpoints[-1]),flush=True)
    np.savez_compressed(stem.with_suffix('.npz'),**archive)
    paths=[Path(__file__),Path(encoding.__file__),Path(gpu.__file__),Path('experiments/fixed_rule/small_holder_temporal_repair.py')]
    result=dict(passed=True,initial=first,checkpoints=checkpoints,physical_ticks=2*f.U,physical_sites=15*f.Q,gpu_seconds=seconds,verification_seconds=verification_seconds,seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,observed_process_gpu_mib=observed,physical_descriptor_sha256=f.self_description().digest(),source_sha256={str(path):sha(path) for path in paths},controller_binary_sha256=sha(gpu.library()._name),artifact_sha256=sha(stem.with_suffix('.npz')),scope='Two complete single-link reset-to-reset cycles with arbitrary old Signals and active represented controller/Address repair; every physical coherent row checked at initialization, both commits and both resets. No general macrostep theorem, intermediate-time reconstruction, nested macrostep or noise guarantee.')
    stem.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');stem.with_suffix('.progress.json').write_text(json.dumps(dict(status='complete',time=2*f.U))+'\n');print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__':main()
