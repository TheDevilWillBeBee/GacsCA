"""Bounded synchronous GPU world with active computation and physical faults.

The large ring repeats a one-colony background; its size is not a hierarchy
claim. Every physical tick is performed by the complete fixed raw GPU rule.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import os
import subprocess
import time
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import small_holder_rule as f,small_holder_core as c
from gacsca.fixed_rule import small_holder_projected as r,small_holder_quotient as q
from gacsca.fixed_rule import small_holder_raw_packed as packed,small_holder_periodic_bounded_cuda as gpu
from gacsca.fixed_rule import small_holder_periodic_initial as init,small_holder_prefix_world as prefix
from gacsca.fixed_rule import small_holder_native as native


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def process_gpu_mib():
    text=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,used_memory','--format=csv,noheader,nounits'],text=True)
    for row in text.splitlines():
        pid,memory=(x.strip() for x in row.split(',',1))
        if pid==str(os.getpid()):return int(memory)
    return 0


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args()
    started=time.perf_counter();parent=r.Cell(address=123,age=19,s2_head=1,s2_pc=31,s2_value=778)
    bg=init.encoded_background(parent);bg[:,f.COL['age']]=1
    active=dict(data=11,head=1,phase=c.WRITE,rd=100,value=91)
    for d in f.OFFSETS:
        for name,value in active.items():bg[(100-d)%f.Q,f.COL[f's{d+2}_{name}']]=value
    # Identical coherent background in the independent physical prefix executor.
    with prefix.World.encode((parent,)) as initial:state=initial.stored
    state[:,q.COL['age']]=1
    for name,value in active.items():state[100,q.COL[name]]=value
    sites=f.Q*f.Q
    fault_sites=(100,101,sites-20,sites-19)
    faults={}
    for pos in fault_sites:
        fields=dict(zip((n for n,_ in f.SCHEMA),map(int,bg[pos%f.Q])))
        fields.update({f's{k+2}_{n}':(1<<w)-1 for k in f.OFFSETS for n,w in f.PROCEDURE})
        faults[pos]=f.Cell(**fields)
    probes=(0,1,2,98,99,100,101,102,103,f.Q-1,f.Q,f.Q+100,sites-22,sites-20,sites-19,sites-17,sites-1)
    frames=[];metrics=[];observed_gpu=[]
    with prefix.World(state) as reference,gpu.World(bg,sites,faults) as world:
        device_bytes=world.device_bytes;observed_gpu.append(process_gpu_mib())
        initial_rows=world.read(probes)
        for _ in range(8):
            with patch.object(f,'local_step',side_effect=AssertionError('host F replacement')),patch.object(native,'local_step',side_effect=AssertionError('host F replacement')),patch.object(r,'local_step',side_effect=AssertionError('host upper replacement')):
                metrics.append(world.step())
            if len(metrics) in (1,8):observed_gpu.append(process_gpu_mib())
            reference.run(1)
            got=world.read(probes);wanted=tuple(r.lift(reference.cell(0,pos%f.Q)) for pos in probes)
            assert got==wanted and not world.positions
            assert got[5].s2_data==91
            frames.append(np.array([f.encode_cell(x) for x in got],dtype=np.uint64))
        evaluations=world.local_evaluations;max_candidates=world.max_candidates
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(out.with_suffix('.npz'),initial_background_packed=packed.pack(bg),fault_positions=np.array(fault_sites,dtype=np.uint64),fault_rows=np.array([f.encode_cell(faults[x]) for x in fault_sites],dtype=np.uint64),probes=np.array(probes,dtype=np.uint64),initial_probe_rows=np.array([f.encode_cell(x) for x in initial_rows],dtype=np.uint64),frames=np.array(frames))
    paths=[Path(x.__file__) for x in (gpu,packed,init,f,c,r,q,prefix,native)]+[Path(gpu.__file__).with_suffix('.cu'),Path(__file__),Path('gacsca/fixed_rule/word_workspace_source.py'),Path('gacsca/fixed_rule/word_allocation.py')]
    result=dict(passed=True,description_sha256=f.self_description().digest(),physical_sites=sites,background_period=f.Q,physical_ticks=8,raw_fields=f.FIELDS,packed_words=packed.WORDS,explicit_device_bytes=device_bytes,observed_process_gpu_mib=observed_gpu,max_observed_process_gpu_mib=max(observed_gpu),host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,local_evaluations=evaluations,max_candidates=max_candidates,initial_exception_sites=len(fault_sites),final_exception_sites=metrics[-1]['exceptions'],active_write_result=91,complete_raw_probe_comparisons=len(probes)*8,metrics=metrics,seconds=time.perf_counter()-started,source_sha256={str(path):digest(path) for path in paths},binary_sha256=digest(gpu.library()._name),depth_two_macrostep_executed=False,limitations=['the billion-site ring repeats one encoded-colony background; this is not a depth-two initialized hierarchy','eight literal physical ticks, not a completed macrostep','only two separated pairs of procedure-holder faults, not general or cross-level noise robustness','literal background evolution still cannot cover U squared practically'])
    out.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('source_sha256','metrics')},indent=2))


if __name__=='__main__':main()
