"""Bounded fault-capable bank/CUDA physical execution evidence and resources."""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time
import numpy as np
from gacsca.fixed_rule import small_holder_bank as bank, small_holder_bank_cuda as gpu
from gacsca.fixed_rule import small_holder_bank_cone as cone, small_holder_rule as f
from gacsca.fixed_rule import small_holder_quotient as q, small_holder_core as c
from gacsca.fixed_rule import small_holder_native as native, small_holder_projected as projected


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args()
    started=time.perf_counter();clean=bank.Builder(1,1);damaged=bank.Builder(1,1)
    for b in (clean,damaged):
        b.set_logical(100,q.Cell(address=100,age=1,data=11,head=1,phase=c.WRITE,rd=100,value=91))
        b.set_logical(f.Q-1,q.Cell(address=f.Q-1,age=1,rp_target=1,rp_data=37,rp_valid=1,rp_remaining=1))
    for pos in (100,101):damaged.set_raw_fields(pos,**{f's{k+2}_{n}':(1<<w)-1 for k in f.OFFSETS for n,w in f.PROCEDURE})
    before=damaged.freeze();positions=tuple(range(94,109))+(f.Q-2,f.Q-1,0,1,2)
    with gpu.Resident(before) as resident:
        reconstructed=resident.evaluate(positions,reconstruct=True)
        after=resident.evaluate(positions);device=resident.device_bytes
    old=np.array([f.encode_cell(before.cell(pos)) for pos in positions],dtype=np.uint64)
    expected=np.array([f.encode_cell(native.local_step(tuple(before.cell((pos+j)%before.sites) for j in f.NEIGHBORHOOD))) for pos in positions],dtype=np.uint64)
    assert np.array_equal(old,reconstructed) and np.array_equal(after,expected)
    repaired=cone.run(before,97,9,3);reference=cone.run(clean.freeze(),97,9,3)
    assert repaired.cells==reference.cells and repaired.cells[3].s2_data==91
    output=Path(args.output);output.parent.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(output.with_suffix('.npz'),data=before.data,logical_keys=before.logical_keys,logical_values=before.logical_values,raw_keys=before.raw_keys,raw_values=before.raw_values,positions=np.array(positions,dtype=np.uint64),old=old,new=after,expected=expected,repaired=np.array([f.encode_cell(x) for x in repaired.cells],dtype=np.uint64))
    modules=(bank,gpu,cone,f,q,c,projected,native)
    sources=[Path(x.__file__) for x in modules]+[Path(gpu.__file__).with_suffix('.cu'),Path(__file__)]
    result=dict(passed=True,rule=f.identity(),storage_bytes=before.storage_bytes,explicit_device_bytes=device,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,local_reconstruction_checks=len(positions),local_transition_checks=len(positions),literal_gpu_ticks=repaired.physical_ticks,cone_evaluations_each=repaired.local_evaluations,two_damaged_procedure_holders_repaired=True,active_write_result=repaired.cells[3].s2_data,final_storage_bytes=repaired.final_storage_bytes,max_cone_device_bytes=repaired.max_device_bytes,seconds=time.perf_counter()-started,source_sha256={str(x):hashlib.sha256(x.read_bytes()).hexdigest() for x in sources},binary_sha256=hashlib.sha256(Path(gpu.library()._name).read_bytes()).hexdigest(),limitations=['bounded snapshots and literal shrinking physical windows, not a whole-colony resident commit executor','arbitrary raw exceptions represented; repair experiment damages only two procedure holders','no full depth-two macrostep or stochastic/cross-level robustness measurement'])
    output.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('rule','source_sha256')},indent=2))


if __name__=='__main__':main()
