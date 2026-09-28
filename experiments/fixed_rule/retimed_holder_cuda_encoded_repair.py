"""Actual GPU encoded-controller repair, compared with frozen full CPU evidence.

Two physical trajectories evolve independently: damaged and healthy. Neither
healthy states nor decoded upper transitions are installed in the damaged world.
"""
import argparse,hashlib,json,random,resource,time
from contextlib import ExitStack
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import retimed_holder_general_faults as faults,retimed_holder_resident_general as general
from gacsca.fixed_rule import retimed_holder_resident_faults as raw_faults,retimed_holder_flags_gpu as flags
from gacsca.fixed_rule import retimed_holder_cuda_general_snapshot as snapshots
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_projected as r,retimed_holder_program as p
from gacsca.fixed_rule import retimed_holder_core as c,retimed_holder_native as native,retimed_holder_quotient as q
from gacsca.fixed_rule.wordcode import Program


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def raw(cells):return np.array([f.encode_cell(r.lift(cell) if isinstance(cell,r.Cell) else cell) for cell in cells],dtype=np.uint64)
def forbidden():
    stack=ExitStack()
    for obj,name in ((Program,'evaluate'),(f,'step_ring'),(f,'local_step'),(r,'step_ring'),(r,'local_step'),(native,'local_step')):
        stack.enter_context(patch.object(obj,name,side_effect=AssertionError('host transition during GPU evolution')))
    return stack


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
    parser.add_argument('--reference',default='figs/fixed_rule/retimed_holder_cpu_encoded_repair_v2.json');args=parser.parse_args()
    out=Path(args.output);artifact=out.with_suffix('.npz');refpath=Path(args.reference)
    if out.exists() or artifact.exists():raise FileExistsError('preserve evidence')
    receipt=json.loads(refpath.read_text());assert receipt['passed']
    assert receipt['descriptor_sha256']==f.self_description().digest()
    assert sha(refpath.with_suffix('.npz'))==receipt['snapshot_sha256']
    for name,digest in receipt['source_sha256'].items():assert sha(name)==digest,name
    started=time.perf_counter();g=p.layout();metrics=[];saved={};gpu_seconds=0.
    with np.load(refpath.with_suffix('.npz'),allow_pickle=False) as old:
        top=tuple(r.project(f.decode_cell(row)) for row in old['initial']);n=len(top);assert n==15
        dirty=tuple(r.project(f.decode_cell(row)) for row in old['faulty_upper_initial'])
        healthy_next=r.step_ring(top);healthy_second=r.step_ring(healthy_next)
        triple=tuple(r.project(f.decode_cell(row)) for row in old['negative_three_copy_initial'])
        assert r.step_ring(dirty)==healthy_next and r.step_ring(triple)!=healthy_next
        for module in (flags,general,raw_faults,faults):module.library()
        with general.World(top,device_budget=32*1024**2) as background,general.World(top,device_budget=32*1024**2) as reference,faults.World(background) as actual:
            # Conservative explicit peak includes both flag arrays and one staged
            # controller batch; the two healthy/damaged advances are sequential.
            peak=(background.device_bytes+reference.device_bytes+actual.device_bytes+
                  2*(32*n*(f.Q//64)+2*n)+8*n*(g.memory_count+5+32*6+1))
            assert peak<=64*1024**2,(peak,'explicit combined device budget')
            def read(positions):return actual.read(tuple(map(int,positions)))
            def capture(name,positions):
                value=raw(read(positions));saved[name]=value
                np.testing.assert_array_equal(value,old[name],err_msg=name)
            def advance_both(target):
                nonlocal gpu_seconds
                tick=time.perf_counter()
                with forbidden():
                    row=actual.advance(target-actual.time)
                    reference.advance(target-reference.time,extra_device_budget=32*1024**2)
                gpu_seconds+=time.perf_counter()-tick;metrics.append(row)
                return row
            for name in ('initial','faulty_upper_initial','negative_three_copy_initial','initial_probe_positions','late_probe_positions'):
                saved[name]=old[name]
            capture('initial_probe_clean',old['initial_probe_positions'])
            changes={}
            for item in receipt['initial_one_bit_faults']:
                pos=item['position'];name=item['field'];cell=r.project(read((pos,))[0]);changes[pos]=replace(cell,**{name:getattr(cell,name)^1})
            actual.inject(changes);assert actual.decode()==dirty
            capture('initial_probe_faulty',old['initial_probe_positions'])
            first=advance_both(1);assert first['rebased_data_cells']==2 and not actual.positions
            assert actual.decode()==dirty and actual.decode()!=top
            saved['after_first_lower_tick']=raw(actual.decode());np.testing.assert_array_equal(saved['after_first_lower_tick'],old['after_first_lower_tick'])
            capture('initial_probe_after_one_tick',old['initial_probe_positions'])
            print(json.dumps(dict(time=actual.time,stage='wrong encoded rb survives lower correction',seconds=time.perf_counter()-started)),flush=True)
            advance_both(c.CAPTURE_AGE);assert actual.decode()==dirty
            hold=np.array([[cell.s2_data for cell in read(tuple(col*f.Q+a for a in g.hold))] for col in range(n)],dtype=np.uint64)
            np.testing.assert_array_equal(hold,old['Hold_after_executed_upper_repair']);np.testing.assert_array_equal(hold,raw(healthy_next))
            saved['Hold_after_executed_upper_repair']=hold
            print(json.dumps(dict(time=actual.time,stage='executed Hold repairs all raw outputs',seconds=time.perf_counter()-started)),flush=True)
            advance_both(c.WF_START+100);snap=snapshots.snapshot(background);target=n//2
            live=snap['active_rows'][target,:int(snap['counts'][target])];heads=live[live[:,q.COL['head']]!=0];assert len(heads)==1
            head=target*f.Q+int(heads[0,q.COL['address']]);assert [head,head+2]==receipt['late_fault_sites']
            capture('late_probe_before',old['late_probe_positions'])
            rng=random.Random(2026092603)
            late={pos:replace(r.project(read((pos,))[0]),**{f's{d+2}_{name}':rng.getrandbits(width) for d in f.OFFSETS for name,width in f.PROCEDURE}) for pos in (head,head+2)}
            actual.inject(late);capture('late_probe_faulty',old['late_probe_positions'])
            advance_both(actual.time+1);assert not actual.positions;capture('late_probe_after_one_tick',old['late_probe_positions'])
            frames=[]
            for epoch in (1,2):
                advance_both(epoch*f.U);assert not actual.positions
                assert actual.decode()==(healthy_next if epoch==1 else healthy_second)
                frames.append(raw(actual.decode()));a=snapshots.snapshot(background)
                expected=old[f'physical_boundary_{epoch}_Data'];bank=np.concatenate((expected[:,:g.memory_count],expected[:,f.Q-5:]),axis=1)
                np.testing.assert_array_equal(a['bank'],bank)
                for key,value in a.items():saved[f'boundary_{epoch}_{key}']=value
                if epoch==1:
                    b=snapshots.snapshot(reference);assert not np.array_equal(a['bank'],b['bank'])
                    saved['healthy_boundary_1_bank']=b['bank']
                    advance_both(f.U+1);a,b=snapshots.assert_equal(background,reference)
                    for key,value in a.items():saved['rejoin_actual_'+key]=value;saved['rejoin_healthy_'+key]=b[key]
                    expected=old['healthy_rejoin_Data'];bank=np.concatenate((expected[:,:g.memory_count],expected[:,f.Q-5:]),axis=1)
                    np.testing.assert_array_equal(a['bank'],bank)
                    print(json.dumps(dict(time=actual.time,stage='complete physical rejoin after actual reset',seconds=time.perf_counter()-started)),flush=True)
                else:
                    a,b=snapshots.assert_equal(background,reference)
                    for key,value in b.items():saved['healthy_boundary_2_'+key]=value
            saved['decoded']=np.stack(frames);saved['expected']=old['expected'];np.testing.assert_array_equal(saved['decoded'],old['decoded'])
            np.savez_compressed(artifact,**saved)
            modules=(faults,general,raw_faults,flags,snapshots)
            sources=[Path(__file__),*(Path(module.__file__) for module in modules),Path(raw_faults.__file__).with_suffix('.cu'),Path(flags.__file__).with_suffix('.cu')]
            result=dict(passed=True,colonies=n,physical_sites=n*f.Q,physical_ticks=actual.time,healthy_reference_ticks=reference.time,advance_metrics=metrics,first_lower_tick_metrics=first,gpu_evolution_seconds=gpu_seconds,seconds=time.perf_counter()-started,explicit_combined_peak_bound_bytes=peak,exception_device_bytes=actual.device_bytes,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,encoded_wrong_values_survive_lower_correction=True,complete_Hold_repair_time=c.CAPTURE_AGE,late_procedure_fault_time=c.WF_START+100,late_repaired_after_one_tick=True,complete_physical_rejoin_time=f.U+1,no_healthy_reference_installed=True,no_host_transition_during_GPU_evolution=True,three_copy_control_diagnostic_only=True,reference=str(refpath),reference_sha256=sha(refpath),reference_artifact_sha256=sha(refpath.with_suffix('.npz')),artifact_sha256=sha(artifact),descriptor_sha256=f.self_description().digest(),rom_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest(),source_sha256={str(path):sha(path) for path in sources},binaries={str(module.library()._name):sha(module.library()._name) for module in (faults,general,raw_faults,flags)},scope='Targeted physical and encoded-controller replica repair across one link, on two-sided Signal/flag trajectories, followed by a second lower period and full physical rejoin. No complete depth-two upper work period, stochastic threshold or general recovery theorem.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
