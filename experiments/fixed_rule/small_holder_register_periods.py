"""Compare scalar-register events with frozen complete physical checkpoints."""
import argparse
import hashlib
import json
import resource
import time
from pathlib import Path
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import small_holder_register_events as gpu
from gacsca.fixed_rule import small_holder_resident_gather as gather
from gacsca.fixed_rule import small_holder_resident_period as period
from gacsca.fixed_rule import small_holder_resident_independent as independent
from gacsca.fixed_rule import small_holder_rule as f, small_holder_core as c
from gacsca.fixed_rule import small_holder_projected as r, small_holder_quotient as q
from gacsca.fixed_rule import small_holder_native as native, small_holder_program as p
from gacsca.fixed_rule.wordcode import Program
from experiments.fixed_rule.small_holder_gather_two_periods import memory


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--reference',default='figs/fixed_rule/small_holder_resident_two_periods_v1')
    parser.add_argument('--timing-reference',default='figs/fixed_rule/small_holder_gather_two_periods_v1.json')
    parser.add_argument('--output',required=True)
    args=parser.parse_args(); ref=Path(args.reference); stem=Path(args.output)
    for suffix in ('.json','.progress.json'):
        if stem.with_suffix(suffix).exists():raise FileExistsError('preserve evidence')
    baseline=json.loads(ref.with_suffix('.json').read_text())
    previous=json.loads(Path(args.timing_reference).read_text())
    assert baseline['passed'] and previous['passed']
    for evidence in (baseline,previous):
        for path,wanted in evidence['source_sha256'].items():assert digest(path)==wanted,path
    assert digest(ref.with_suffix('.npz'))==baseline['artifact_sha256']
    assert f.self_description().digest()==previous['descriptor_sha256']
    start=time.perf_counter();lib=gpu.library();seconds=0.;metrics={};checkpoints=[];intervals=[];observed=[]
    with np.load(ref.with_suffix('.npz'),allow_pickle=False) as archive:
        top=r.cells_from_array(archive['initial_top']); layout=p.layout()
        with gpu.World(top) as world:
            allocated=world.device_bytes;observed.append(memory())
            for which,key in enumerate(('first_stored','second_stored')):
                target=(which+1)*f.U
                while world.time<target:
                    before=world.time;age=world.age;tick=time.perf_counter()
                    with patch.object(Program,'evaluate',side_effect=AssertionError('host evaluator')),patch.object(f,'local_step',side_effect=AssertionError('host upper rule')),patch.object(r,'local_step',side_effect=AssertionError('host upper rule')),patch.object(native,'local_step',side_effect=AssertionError('host physical rule')):
                        row=world.advance(min(c.T,target-world.time))
                    dt=time.perf_counter()-tick;seconds+=dt
                    intervals.append(dict(time=before,age=age,ticks=world.time-before,seconds=dt,metrics=row))
                    for name,value in row.items():metrics[name]=max(metrics.get(name,0),value) if name=='extra_device_bytes' else metrics.get(name,0)+value
                    stem.with_suffix('.progress.json').write_text(json.dumps(dict(status='running',time=world.time,gpu_seconds=seconds))+'\n')
                np.testing.assert_array_equal(native.array_from_cells(tuple(r.lift(x) for x in world.decode())),archive['decoded'][which])
                actual=world.stored();expected=archive[key]
                np.testing.assert_array_equal(actual,expected)
                sha=hashlib.sha256(actual.tobytes()).hexdigest();del actual,expected
                assert sha==baseline['periods'][which]['stored_sha256']
                gap=hashlib.sha256()
                for col in range(world.colonies):
                    for at in range(layout.computation_cells,f.Q-5,period.MAX_READ):
                        positions=tuple(range(at,min(f.Q-5,at+period.MAX_READ)))
                        cells=world.logical_cells(tuple(col*f.Q+a for a in positions))
                        assert all(cell==q.Cell(address=a) for cell,a in zip(cells,positions))
                        gap.update(q.array_from_cells(cells).tobytes())
                assert gap.hexdigest()==baseline['periods'][which]['gap_sha256']
                checkpoints.append(dict(period=which+1,stored_sha256=sha,gap_sha256=gap.hexdigest(),all_decoded_fields_match=True,complete_physical_checkpoint_matches=True,gpu_seconds=seconds))
                observed.append(memory());print(json.dumps(checkpoints[-1]),flush=True)
    assert metrics==previous['metrics'],(metrics,previous['metrics'])
    paths=[Path(__file__),Path(gpu.__file__),Path(gather.__file__),Path(gather.__file__).with_suffix('.cu'),Path(period.__file__),Path(period.__file__).with_suffix('.cu'),Path(independent.__file__),Path(independent.__file__).with_suffix('.cu')]
    result=dict(passed=True,checkpoints=checkpoints,metrics=metrics,intervals=intervals,
        descriptor_sha256=f.self_description().digest(),rom_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest(),event_expression_sha256=gpu.event_program().digest(),event_operations=len(gpu.event_program().operations),gpu_seconds=seconds,previous_gpu_seconds=previous['gpu_run_seconds'],speedup=previous['gpu_run_seconds']/seconds,seconds=time.perf_counter()-start,physical_sites=len(top)*f.Q,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,observed_process_gpu_mib=observed,explicit_resident_bytes=allocated,explicit_peak_bytes=allocated+metrics['extra_device_bytes'],binary_sha256=digest(lib._name),source_sha256={str(path):digest(path) for path in paths},baseline_manifest_sha256=digest(ref.with_suffix('.json')),baseline_artifact_sha256=digest(ref.with_suffix('.npz')),timing_reference_sha256=digest(args.timing_reference),limitation='same one-link restricted coherent domain; two-level upper macrostep remains unexecuted; comparison is historical single-run timing, not a throughput guarantee')
    stem.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    stem.with_suffix('.progress.json').write_text(json.dumps(dict(status='complete',time=2*f.U,seconds=result['seconds']))+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='intervals'},indent=2),flush=True)

if __name__=='__main__':main()
