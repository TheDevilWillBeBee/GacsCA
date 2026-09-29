"""Physical precommit/commit trajectories versus exact complete-state GPU endpoints."""
import argparse
from contextlib import ExitStack
import hashlib
import json
from pathlib import Path
import random
import resource
import time
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import compact16_holder_endpoint_gpu as endpoint
from gacsca.fixed_rule import compact16_holder_resident_general as physical
from gacsca.fixed_rule import compact16_holder_resident_period as resident
from gacsca.fixed_rule import compact16_holder_records as q, compact16_holder_packed as packed
from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_projected as r, compact16_holder_program as p
from gacsca.fixed_rule import compact16_holder_terminal_reference as replay, compact16_holder_terminal_dag as dag
from gacsca.fixed_rule import compact16_holder_terminal_checks as checks, compact16_holder_native as native
from gacsca.fixed_rule.wordcode import Program
from experiments.fixed_rule.audit_small_holder_position_events import sha
from experiments.fixed_rule.audit_compact16_holder_terminal import step


def guard():
    stack=ExitStack()
    for module,name in ((f,'local_step'),(r,'local_step'),(native,'local_step'),(Program,'evaluate'),(replay,'terminal'),(dag,'terminal')):
        stack.enter_context(patch.object(module,name,side_effect=AssertionError('host transition or endpoint formula during evolution')))
    return stack


def snapshot(world):
    bank,rows,counts=world._core.snapshot();unpacked=np.zeros((world.colonies,resident.SLOTS,len(q.SCHEMA)),dtype=np.uint64)
    for col,count in enumerate(counts):
        addresses=packed.unpack(rows[col,:int(count)])[:,q.COL['address']]
        cells=world.logical_cells(tuple(col*f.Q+int(a) for a in addresses))
        unpacked[col,:int(count)]=q.array_from_cells(cells)
    signals=np.array([[(world.logical_cells((col*f.Q+a,))[0].signal>>2)&1 for a in (3,f.Q-3)] for col in range(world.colonies)],dtype=np.uint64)
    assert world._flags is None
    return dict(bank=bank,signals=signals,active_rows=unpacked,counts=counts,
                flags=np.zeros((world.colonies*f.Q//64,2),dtype=np.uint64),age=np.array(world.age,dtype=np.uint64),time=np.array(world.time,dtype=np.uint64))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True,type=Path);args=parser.parse_args();artifact=args.output.with_suffix('.npz')
    if args.output.exists() or artifact.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();rng=random.Random(2026092779);n=3;g=p.layout()
    parents=tuple(r.Cell(**{name:rng.getrandbits(width) for name,width in r.SCHEMA}) for _ in range(n))
    bank=np.array([[rng.getrandbits(64) for _ in range(g.memory_count+5)] for _ in range(n)],dtype=np.uint64)
    bank[:,list(g.info)]=np.array([f.encode_cell(r.lift(cell)) for cell in parents],dtype=np.uint64)
    signals=np.array([[rng.randrange(2),rng.randrange(2)] for _ in range(n)],dtype=np.uint64)
    logical={}
    for col in range(n):
        for a in (*range(1,6),*range(f.Q-5,f.Q)):
            logical[col*f.Q+a]=q.Cell(address=a,signal=checks.signal_word(a,*signals[col]))
    saved=dict(initial_upper=r.array_from_cells(parents),initial_bank=bank,initial_signals=signals);rows=[]
    tick=time.perf_counter();endpoint.library();build_seconds=time.perf_counter()-tick
    physical_seconds=endpoint_seconds=0.;metrics={};peak=0
    with physical.World(parents,logical=logical,device_budget=32*1024**2) as actual,endpoint.World(bank,signals,device_budget=32*1024**2) as accelerated:
        # Initial physical scratch upload only. Never used between periods.
        for col in range(n):
            assert actual._core.lib.rp_bank(actual._core.handle,col,resident.pointer(np.ascontiguousarray(bank[col]))) == 0
        np.testing.assert_array_equal(actual._core.snapshot()[0],bank)
        for epoch in range(1,3):
            expected=dag.terminal(parents)
            for phase,amount,method in (('precommit',f.U-1,'precommit'),('commit',1,'commit')):
                tick=time.perf_counter()
                with guard():metric=actual.advance(amount,extra_device_budget=32*1024**2)
                physical_seconds+=time.perf_counter()-tick
                for name,value in metric.items():metrics[name]=max(metrics.get(name,0),value) if name=='extra_device_bytes' else metrics.get(name,0)+value
                tick=time.perf_counter()
                with guard():getattr(accelerated,method)()
                endpoint_seconds+=time.perf_counter()-tick
                state=snapshot(actual);fast=accelerated.snapshot()
                check=checks.check(state,expected,age=actual.age,time=actual.time)
                checks.check(fast,expected,age=actual.age,time=actual.time)
                for key in ('bank','signals','flags','age','time'):np.testing.assert_array_equal(state[key],fast[key])
                prefix=f'period{epoch}_{phase}_'
                for key,value in state.items():saved[prefix+key]=value
                row=dict(period=epoch,phase=phase,complete_state_matches=True,**check);rows.append(row)
                print(json.dumps(dict(period=epoch,phase=phase,seconds=time.perf_counter()-start)),flush=True)
            parents=step(parents)
        peak=actual.device_bytes+metrics.get('extra_device_bytes',0)+32*n*(f.Q//64)+2*n+accelerated.device_bytes
        assert peak<64*1024**2
    np.savez_compressed(artifact,**saved)
    sources=(endpoint,physical,resident,q,packed,replay,dag,checks)
    result=dict(passed=True,periods=2,colonies=n,physical_ticks=2*f.U,cases=rows,
                arbitrary_initial_scratch=True,arbitrary_typed_parents=True,physical_evolution_seconds=physical_seconds,
                endpoint_seconds=endpoint_seconds,build_seconds=build_seconds,explicit_device_buffer_bound=peak,
                descriptor_sha256=f.self_description().digest(),rom_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest(),
                artifact=str(artifact),artifact_sha256=sha(artifact),binary=str(endpoint.library()._name),binary_sha256=sha(endpoint.library()._name),
                source_sha256={str(Path(module.__file__)):sha(module.__file__) for module in sources},
                seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                scope='Four complete physical precommit/commit states compared with GPU endpoint acceleration; conditional coherent noiseless domain, no complete depth-two run or noise theorem.')
    result['source_sha256'][str(Path(__file__))]=sha(__file__)
    result['source_sha256'][str(Path(endpoint.__file__).with_suffix('.cu'))]=sha(Path(endpoint.__file__).with_suffix('.cu'))
    with args.output.open('x') as stream:stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
