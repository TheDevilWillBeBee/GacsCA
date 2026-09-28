"""GPU physical self-description evaluation through computed-flag capture.

Stops before physical Wf/repair waves and the later recomputation/commit. This
is a complete computation prefix, not a complete macrostep or nested execution.
"""
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
from gacsca.fixed_rule import small_holder_rule as f,small_holder_core as c,small_holder_projected as r,small_holder_quotient as q,small_holder_program as p
from gacsca.fixed_rule import small_holder_native as native,word_workspace_source,word_allocation,small_holder_prefix_description,small_holder_packed
from gacsca.fixed_rule.wordcode import Program
from experiments.fixed_rule.small_holder_execution import initial_ring


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def gpu_mib():
    text=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,used_memory','--format=csv,noheader,nounits'],text=True)
    for line in text.splitlines():
        pid,memory=map(str.strip,line.split(',',1))
        if pid==str(os.getpid()):return int(memory)
    return 0


def data_at(world,addresses):
    out=[]
    for col in range(world.colonies):
        row=[]
        for start in range(0,len(addresses),gpu.MAX_READ):row.extend(x.data for x in world.logical_cells(tuple(col*f.Q+a for a in addresses[start:start+gpu.MAX_READ])))
        out.append(row)
    return np.array(out,dtype=np.uint64)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();stem=Path(args.output)
    for ext in ('.json','.npz','.progress.json'):
        if stem.with_suffix(ext).exists():raise FileExistsError('preserve prior evidence')
    started=time.perf_counter();top=initial_ring();old=tuple(r.lift(x) for x in top);g=p.layout()
    initial=native.array_from_cells(old)
    expected=native.array_from_cells(tuple(r.lift(r.project(x)) for x in f.step_ring(old)))
    assert int(expected[7,f.COL['s2_data']])==0x123456789ABCDEF0
    neighborhoods=np.stack([initial[(np.arange(len(top))+j)%len(top)] for j in f.NEIGHBORHOOD],axis=1).reshape(len(top),-1)
    targets=(f.ACTIVE_ENDS[0],f.ACTIVE_ENDS[1],c.VOTE_AGES[0],c.VOTE_AGES[0]+1,c.CAPTURE_AGE)
    probes=[];histories=[];gpu_seconds=0.;metrics=dict(physical_ticks=0,literal_ticks=0,transport_or_quiet_ticks=0,logical_evaluations=0);observed=[]
    with gpu.World(top) as world,cpu.World.encode(top) as reference:
        allocated=world.device_bytes;observed.append(gpu_mib())
        for target in targets:
            while world.age<target:
                dt=min(c.T,target-world.age);stage=time.perf_counter()
                with patch.object(Program,'evaluate',side_effect=AssertionError('host evaluator')),patch.object(f,'local_step',side_effect=AssertionError('host upper F')),patch.object(r,'local_step',side_effect=AssertionError('host upper F')),patch.object(native,'local_step',side_effect=AssertionError('host F')):
                    row=world.run(dt)
                gpu_seconds+=time.perf_counter()-stage
                for k,v in row.items():metrics[k]+=v
                reference.run(dt)
                stem.with_suffix('.progress.json').write_text(json.dumps(dict(status='running',physical_age=world.age,gpu_run_seconds=gpu_seconds,seconds=time.perf_counter()-started,metrics=metrics),indent=2)+'\n')
            info=data_at(world,g.info);np.testing.assert_array_equal(info,initial)
            if target in targets[:3]:
                index=targets.index(target);addresses=tuple(g.history(index,j,k) for j in f.NEIGHBORHOOD for k in range(f.FIELDS))
                got=data_at(world,addresses);np.testing.assert_array_equal(got,neighborhoods);histories.append(got)
            if target==c.VOTE_AGES[0]+1:np.testing.assert_array_equal(data_at(world,g.votes),neighborhoods)
            point=dict(age=target,info_unchanged=True,gpu_run_seconds=gpu_seconds,metrics=dict(metrics));probes.append(point);print(json.dumps(point),flush=True)
        hold=data_at(world,g.hold);np.testing.assert_array_equal(hold,expected)
        buffers=data_at(world,tuple(range(1,6))+tuple(range(f.Q-5,f.Q)))
        np.testing.assert_array_equal(buffers,np.repeat(expected[:,[f.COL['f2'],f.COL['f1']]],5,axis=1))
        # Stream the entire coherent state; equality lifts to every raw physical
        # field in this certified domain. Host staging stays at one small block.
        stream=hashlib.sha256();final_core=np.empty((len(top),g.computation_cells+5,len(q.SCHEMA)),dtype=np.uint64)
        for col in range(len(top)):
            for start in range(0,f.Q,gpu.MAX_READ):
                addresses=tuple(range(start,min(f.Q,start+gpu.MAX_READ)));positions=tuple(col*f.Q+a for a in addresses)
                got=world.logical_cells(positions);want=tuple(reference.logical_cell(col,a) for a in addresses)
                if got!=want:raise AssertionError(f'complete physical-state mismatch in colony {col}, block {start}')
                rows=q.array_from_cells(got);stream.update(rows.tobytes())
                for index,a in enumerate(addresses):
                    if a<g.computation_cells:final_core[col,a]=rows[index]
                    elif a>=f.Q-5:final_core[col,g.computation_cells+a-(f.Q-5)]=rows[index]
        observed.append(gpu_mib())
    assert metrics['physical_ticks']==c.CAPTURE_AGE==metrics['literal_ticks']+metrics['transport_or_quiet_ticks']
    np.savez_compressed(stem.with_suffix('.npz'),initial_top=r.array_from_cells(top),initial_lifted=initial,expected_hold=expected,actual_hold=hold,histories=np.array(histories),buffers=buffers,final_stored=final_core.reshape(-1,len(q.SCHEMA)))
    modules=(gpu,cpu,f,c,r,q,p,native,word_workspace_source,word_allocation,small_holder_prefix_description,small_holder_packed)
    paths=[Path(x.__file__) for x in modules]+[Path(gpu.__file__).with_suffix('.cu'),Path(cpu.__file__).with_suffix('.c'),Path(__file__),Path('experiments/fixed_rule/small_holder_execution.py')]
    result=dict(passed=True,physical_rule_description=f.self_description().digest(),represented_parent_cells=len(top),physical_sites=len(top)*f.Q,physical_ticks=c.CAPTURE_AGE,complete_raw_fields=f.FIELDS,all_three_histories_match=True,temporal_vote_matches=True,complete_self_description_output_matches=True,active_simulated_write=int(hold[7,f.COL['s2_data']]),computed_flags_delivered=True,complete_coherent_rows_checked=len(top)*f.Q,complete_coherent_sha256=stream.hexdigest(),probes=probes,metrics=metrics,gpu_run_seconds=gpu_seconds,seconds=time.perf_counter()-started,explicit_device_bytes=allocated,observed_process_gpu_mib=observed,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,source_sha256={str(x):digest(x) for x in paths},binary_sha256=digest(gpu.library()._name),limitations=['complete self-description evaluation through capture, not the later Wf/suffix/recomputation/commit','one simulation link with 15 distinct parent states, not depth-two dynamics','coherent zero-flag physical prefix; incoherent fault and cross-level robustness execution remain open'])
    stem.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');stem.with_suffix('.progress.json').write_text(json.dumps(dict(status='complete',physical_age=c.CAPTURE_AGE,seconds=result['seconds']))+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('probes','source_sha256')},indent=2),flush=True)


if __name__=='__main__':main()
