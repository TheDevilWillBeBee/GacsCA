"""Independent-event scheduler against frozen complete two-period GPU evidence."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import time
from unittest.mock import patch

import numpy as np

from gacsca.fixed_rule import small_holder_resident_independent as gpu
from gacsca.fixed_rule import small_holder_resident_period as synchronous
from gacsca.fixed_rule import small_holder_rule as f,small_holder_core as c,small_holder_projected as r,small_holder_quotient as q,small_holder_program as p,small_holder_native as native
from gacsca.fixed_rule.wordcode import Program


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def memory():
    result=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,used_memory','--format=csv,noheader,nounits'],text=True)
    for line in result.splitlines():
        pid,value=line.split(',',1)
        if int(pid)==os.getpid():return int(value)
    return 0


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--reference',required=True);parser.add_argument('--output',required=True);args=parser.parse_args()
    reference=Path(args.reference);stem=Path(args.output)
    for ext in ('.json','.progress.json'):
        if stem.with_suffix(ext).exists():raise FileExistsError('preserve evidence')
    baseline=json.loads(reference.with_suffix('.json').read_text())
    assert baseline['passed'] and baseline['physical_rule_description']==f.self_description().digest()
    for path,wanted in baseline['source_sha256'].items():assert digest(path)==wanted,path
    assert digest(reference.with_suffix('.npz'))==baseline['artifact_sha256']
    started=time.perf_counter();gpu.library();seconds=0.;metrics={};periods=[];observed=[]
    with np.load(reference.with_suffix('.npz'),allow_pickle=False) as archive:
        top=r.cells_from_array(archive['initial_top']);g=p.layout()
        with gpu.World(top) as world:
            observed.append(memory());allocated=world.device_bytes
            for period,key in enumerate(('first_stored','second_stored')):
                target=(period+1)*f.U
                while world.time<target:
                    tick=time.perf_counter()
                    with patch.object(Program,'evaluate',side_effect=AssertionError('host evaluator')),patch.object(f,'local_step',side_effect=AssertionError('host upper rule')),patch.object(r,'local_step',side_effect=AssertionError('host upper rule')),patch.object(native,'local_step',side_effect=AssertionError('host physical rule')):
                        row=world.advance(min(c.T,target-world.time))
                    seconds+=time.perf_counter()-tick
                    for name,value in row.items():
                        if name=='extra_device_bytes':metrics[name]=max(metrics.get(name,0),value)
                        else:metrics[name]=metrics.get(name,0)+value
                    stem.with_suffix('.progress.json').write_text(json.dumps(dict(status='running',physical_time=world.time,age=world.age,gpu_run_seconds=seconds,metrics=metrics))+'\n')
                assert world.age==0
                decoded=native.array_from_cells(tuple(r.lift(x) for x in world.decode()))
                np.testing.assert_array_equal(decoded,archive['decoded'][period])
                actual=world.stored();expected=archive[key]
                np.testing.assert_array_equal(actual,expected)
                state_hash=hashlib.sha256(actual.tobytes()).hexdigest()
                assert state_hash==baseline['periods'][period]['stored_sha256']
                del actual,expected
                gap=hashlib.sha256()
                for col in range(world.colonies):
                    for start in range(g.computation_cells,f.Q-5,gpu.resident.MAX_READ):
                        addresses=tuple(range(start,min(f.Q-5,start+gpu.resident.MAX_READ)))
                        cells=world.logical_cells(tuple(col*f.Q+a for a in addresses))
                        assert all(cell==q.Cell(address=a) for cell,a in zip(cells,addresses))
                        gap.update(q.array_from_cells(cells).tobytes())
                assert gap.hexdigest()==baseline['periods'][period]['gap_sha256']
                periods.append(dict(period=period+1,complete_raw_decode_matches=True,complete_physical_checkpoint_matches=True,stored_sha256=state_hash,gap_sha256=gap.hexdigest(),gpu_run_seconds=seconds))
                observed.append(memory());print(json.dumps(periods[-1]),flush=True)
    assert metrics['physical_ticks']==2*f.U
    assert metrics['physical_ticks']==metrics['independent_ticks']+metrics['synchronous_literal_ticks']+metrics['synchronous_transport_or_quiet_ticks']
    assert metrics['colony_literal_ticks']+metrics['colony_transport_or_quiet_ticks']==len(top)*metrics['independent_ticks']
    paths=[Path(__file__),Path(gpu.__file__),Path(gpu.__file__).with_suffix('.cu'),Path(synchronous.__file__),Path(synchronous.__file__).with_suffix('.cu')]
    result=dict(passed=True,periods=periods,metrics=metrics,physical_sites=len(top)*f.Q,gpu_run_seconds=seconds,seconds=time.perf_counter()-started,gpu_advance_speedup=baseline['gpu_run_seconds']/seconds,explicit_resident_device_bytes=allocated,explicit_peak_with_staging_bytes=allocated+metrics['extra_device_bytes'],observed_process_gpu_mib=observed,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,descriptor_sha256=f.self_description().digest(),baseline_manifest_sha256=digest(reference.with_suffix('.json')),baseline_artifact_sha256=digest(reference.with_suffix('.npz')),source_sha256={str(path):digest(path) for path in paths},independent_binary_sha256=digest(gpu.library()._name),resident_binary_sha256=digest(synchronous.library()._name),one_resident_state=True,limitation='two work periods at one link with restricted coherent suffix; not nested execution or general noise correction')
    stem.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');stem.with_suffix('.progress.json').write_text(json.dumps(dict(status='complete',physical_time=2*f.U,seconds=result['seconds']))+'\n');print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
