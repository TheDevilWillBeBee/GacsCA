"""Physical Info faults plus later geometry/controller/front faults in one period.

Both computed Signals are one. A separately evolved healthy physical world is
used only for comparison, never installed into the damaged world.
"""
import argparse,hashlib,json,random,resource,time
from contextlib import ExitStack
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import small_holder_resident_general as gpu,small_holder_general_faults as overlay
from gacsca.fixed_rule import small_holder_rule as f,small_holder_projected as r,small_holder_program as p,small_holder_core as c,small_holder_native as native
from gacsca.fixed_rule.wordcode import Program
from experiments.fixed_rule.small_holder_execution import initial_ring


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def raw(cells):return native.array_from_cells(tuple(r.lift(x) if isinstance(x,r.Cell) else x for x in cells))
def no_host():
    stack=ExitStack()
    for obj,name in ((Program,'evaluate'),(f,'local_step'),(r,'local_step'),(native,'local_step')):
        stack.enter_context(patch.object(obj,name,side_effect=AssertionError('host transition')))
    return stack


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();stem=Path(args.output)
    for ext in ('.json','.npz','.progress.json'):
        if stem.with_suffix(ext).exists():raise FileExistsError('preserve evidence')
    started=time.perf_counter();g=p.layout();top=tuple(replace(x,f2=1) for x in initial_ring());healthy=tuple(r.lift(r.project(x)) for x in native.step_ring(tuple(r.lift(x) for x in top)))
    assert all(x.f1==1 and x.f2==1 for x in healthy)
    data=dict(initial=raw(top),expected=raw(healthy));gpu_seconds=0.;events=[]
    with gpu.World(top) as reference,gpu.World(top) as base,overlay.World(base) as world:
        changes={};infofaults=[];wrong=list(top)
        for e in (-1,1):
            col=7+e;field=f's{2-e}_value';target=col*f.Q+g.info[f.COL[field]];wrong[col]=replace(wrong[col],**{field:getattr(wrong[col],field)^1})
            for d in (-1,0,1):
                pos=target+d;name=f's{2-d}_data';cell=r.project(world.read((pos,))[0]);changes[pos]=replace(cell,**{name:getattr(cell,name)^1});infofaults.append((pos,name))
        world.inject(changes);assert world.decode()==tuple(wrong);data['faulty_upper_initial']=raw(wrong)
        tick=time.perf_counter()
        with no_host():first=world.advance(1);reference.advance(1)
        gpu_seconds+=time.perf_counter()-tick;assert not world.positions and world.decode()==tuple(wrong)
        data['after_first_lower_tick']=raw(world.decode())
        front_age=f.WF_START+100
        def advance_both(target):
            nonlocal gpu_seconds
            while world.time<target:
                amount=min(c.T,target-world.time);tick=time.perf_counter()
                with no_host():world.advance(amount);reference.advance(amount)
                gpu_seconds+=time.perf_counter()-tick
                stem.with_suffix('.progress.json').write_text(json.dumps(dict(status='running',physical_time=world.time,gpu_run_seconds=gpu_seconds))+'\n')
        advance_both(f.CAPTURE_AGE)
        assert world.decode()==tuple(wrong)
        hold=np.array([[x.data for x in base.logical_cells(tuple(col*f.Q+a for a in g.hold))] for col in range(len(top))],dtype=np.uint64)
        np.testing.assert_array_equal(hold,raw(healthy));data['hold_after_simulated_repair']=hold
        advance_both(front_age)
        front=7*f.Q+f.Q-8-3*(front_age-f.WF_START-1);rng=random.Random(1703)
        late_positions=(7*f.Q+100,7*f.Q+101,front)
        probe=tuple(sorted({pos+d for pos in late_positions for d in range(-14,15)}))
        data['late_probe_positions']=np.array(probe,dtype=np.uint64);data['late_before_faults']=raw(world.read(probe))
        changes={pos:r.Cell(**{name:rng.getrandbits(width) for name,width in r.SCHEMA}) for pos in late_positions[:2]}
        current=r.project(world.read((front,))[0]);assert current.f1==1;changes[front]=replace(current,f1=0)
        world.inject(changes);data['late_after_faults']=raw(world.read(probe));late_changes=[]
        for pos,old,new in zip(probe,data['late_before_faults'],data['late_after_faults']):
            for (name,_),a,b in zip(f.SCHEMA,old,new):
                if a!=b:late_changes.append((pos,name,int(a),int(b)))
        tick=time.perf_counter()
        with no_host():world.step();reference.advance(1)
        gpu_seconds+=time.perf_counter()-tick;data['late_after_one_tick']=raw(world.read(probe))
        before=world.read(probe)
        with no_host():data_rebase=world.absorb_data();flag_rebase=world.absorb_flags()
        assert world.read(probe)==before
        events.append(dict(time=world.time,exceptions=len(world.positions),data_rebase=data_rebase,flag_rebase=flag_rebase))
        for _ in range(7):
            if not world.positions:break
            tick=time.perf_counter()
            with no_host():result=world.advance(1);reference.advance(1)
            gpu_seconds+=time.perf_counter()-tick;events.append(result)
        assert not world.positions
        advance_both(front_age+256)
        faulty_flags=base._flags.read();healthy_flags=reference._flags.read()
        assert np.any(faulty_flags!=healthy_flags) # coherent representation is not yet recovery
        data['delayed_flags']=faulty_flags;data['healthy_flags_same_time']=healthy_flags
        advance_both(f.WF_END+f.Q)
        assert base._flags is None and reference._flags is None
        advance_both(f.U)
        np.testing.assert_array_equal(raw(world.decode()),raw(healthy));data['decoded']=raw(world.decode())
        advance_both(f.U+1)
        np.testing.assert_array_equal(base.stored(),reference.stored())
        for col in range(len(top)):
            for begin in range(g.computation_cells,f.Q-5,256):
                positions=tuple(col*f.Q+a for a in range(begin,min(f.Q-5,begin+256)))
                assert base.logical_cells(positions)==reference.logical_cells(positions)
        assert not world.positions
        extra_bytes=world.device_bytes
    np.savez_compressed(stem.with_suffix('.npz'),**data)
    paths=[Path(__file__),Path(overlay.__file__),Path(gpu.__file__),Path('gacsca/fixed_rule/small_holder_resident_faults.py'),Path('gacsca/fixed_rule/small_holder_resident_faults.cu'),Path('gacsca/fixed_rule/small_holder_flags_gpu.py'),Path('gacsca/fixed_rule/small_holder_flags_gpu.cu')]
    result=dict(passed=True,initial_physical_one_bit_faults=infofaults,initial_rebase_metrics=first,late_fault_time=front_age,late_fault_sites=late_positions,late_changed_raw_fields=late_changes,late_repair_events=events,complete_physical_rejoin_time=f.U+1,all_decoded_fields_match=True,nonzero_flag_difference_after_256_ticks=True,physical_rule_description=f.self_description().digest(),physical_sites=len(top)*f.Q,gpu_run_seconds=gpu_seconds,seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,extra_exception_device_bytes=extra_bytes,source_sha256={str(path):sha(path) for path in paths},fault_binary_sha256=sha(overlay.library()._name),controller_binary_sha256=sha(gpu.library()._name),artifact_sha256=sha(stem.with_suffix('.npz')),scope='targeted temporally separated initial Info, later full-site and flag-front faults through one link; actual geometry/controller recovery and full physical rejoin; no stochastic threshold or nested upper work period')
    stem.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');stem.with_suffix('.progress.json').write_text(json.dumps(dict(status='complete'))+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('late_changed_raw_fields','source_sha256')},indent=2),flush=True)


if __name__=='__main__':main()
