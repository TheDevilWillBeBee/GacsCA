"""Nonperiodic physical-prefix execution with streamed complete-state audit."""
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
from gacsca.fixed_rule import small_holder_resident_prefix as gpu,small_holder_prefix_world as cpu
from gacsca.fixed_rule import small_holder_rule as f,small_holder_projected as r,small_holder_quotient as q
from gacsca.fixed_rule import small_holder_native as native,small_holder_program as p
from gacsca.fixed_rule import word_workspace_source,word_allocation,small_holder_prefix_description,small_holder_packed


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def gpu_mib():
    text=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,used_memory','--format=csv,noheader,nounits'],text=True)
    for line in text.splitlines():
        pid,memory=map(str.strip,line.split(',',1))
        if pid==str(os.getpid()):return int(memory)
    return 0


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args()
    output=Path(args.output);output.parent.mkdir(parents=True,exist_ok=True)
    started=time.perf_counter();parents=tuple(r.Cell(address=29+i*73,age=31+i*11,s2_head=1,s2_pc=43+i,s2_value=123456+i,s1_rp_valid=1,s1_rp_data=987+i) for i in range(3))
    frames=[];observed=[];horizons=(100000,1000000,20000000)
    with gpu.World(parents) as world,cpu.World.encode(parents) as reference:
        allocated=world.device_bytes;observed.append(gpu_mib())
        for horizon in horizons:
            dt=horizon-world.age;stage=time.perf_counter()
            with patch.object(f,'local_step',side_effect=AssertionError('host F replacement')),patch.object(r,'local_step',side_effect=AssertionError('host upper replacement')),patch.object(native,'local_step',side_effect=AssertionError('host F replacement')):
                metrics=world.run(dt)
            gpu_seconds=time.perf_counter()-stage
            reference.run(dt);logical=np.empty((len(parents)*f.Q,len(q.SCHEMA)),dtype=np.uint64)
            for start in range(0,len(logical),gpu.MAX_READ):
                positions=tuple(range(start,min(len(logical),start+gpu.MAX_READ)))
                got=world.logical_cells(positions)
                expected=tuple(reference.logical_cell(*divmod(pos,f.Q)) for pos in positions)
                if got!=expected:
                    bad=next((pos for pos,a,b in zip(positions,got,expected) if a!=b),None)
                    raise AssertionError(f'full coherent physical state mismatch at age {horizon}, position {bad}')
                logical[start:start+len(got)]=q.array_from_cells(got)
            observed.append(gpu_mib())
            heads=np.flatnonzero(logical[:,q.COL['head']])
            frame=dict(age=horizon,gpu_run_seconds=gpu_seconds,metrics=metrics,complete_logical_rows_checked=len(logical),complete_physical_state_by_coherent_lift=True,head_positions=heads.tolist(),head_program_counters=logical[heads,q.COL['pc']].tolist(),pending_mail_records=int(np.count_nonzero(logical[:,q.COL['lp_valid']]|logical[:,q.COL['rp_valid']])),logical_sha256=hashlib.sha256(logical.tobytes()).hexdigest())
            frames.append(frame);output.with_suffix('.progress.json').write_text(json.dumps(dict(status='running',frames=frames,seconds=time.perf_counter()-started),indent=2)+'\n');print(json.dumps(frame),flush=True)
        assert any(x['metrics']['transport_or_quiet_ticks'] for x in frames)
        assert max(frames[-1]['head_program_counters'])>0
        assert frames[-1]['pending_mail_records']>0
    np.savez_compressed(output.with_suffix('.npz'),initial_parents=r.array_from_cells(parents),final_logical=logical)
    modules=(gpu,cpu,f,r,q,native,p,word_workspace_source,word_allocation,small_holder_prefix_description,small_holder_packed)
    paths=[Path(x.__file__) for x in modules]+[Path(gpu.__file__).with_suffix('.cu'),Path(cpu.__file__).with_suffix('.c'),Path(__file__)]
    result=dict(passed=True,physical_rule_description=f.self_description().digest(),physical_sites=len(parents)*f.Q,distinct_encoded_parents=len(parents),physical_ticks=horizons[-1],frames=frames,explicit_device_bytes=allocated,observed_process_gpu_mib=observed,max_observed_process_gpu_mib=max(observed),host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,seconds=time.perf_counter()-started,source_sha256={str(x):digest(x) for x in paths},binary_sha256=digest(gpu.library()._name),limitations=['coherent canonical zero-flag prefix only; no incoherent fault or Wf/suffix execution','20 million physical ticks of local metadata/gather computation; not a full work period','three distinct encoded parents, not an executed two-level hierarchy','host work only initialization, event indices, diagnostics and independent comparison; no host simulated transition substitution'])
    output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');output.with_suffix('.progress.json').write_text(json.dumps(dict(status='complete',seconds=result['seconds']))+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('frames','source_sha256')},indent=2),flush=True)


if __name__=='__main__':main()
