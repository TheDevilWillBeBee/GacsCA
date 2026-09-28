"""Six physical bit faults surviving lower repair, then repaired by simulated G.

Actual packet/controller evolution performs both lower periods. A separately
evolved healthy physical reference is comparison-only and is never installed.
"""
import argparse
from contextlib import ExitStack
from dataclasses import replace
import json
from pathlib import Path
import random
import resource
import time
from unittest.mock import patch

import numpy as np

from gacsca.fixed_rule import retimed_holder_cpu_faults as overlay
from gacsca.fixed_rule import retimed_holder_cpu_general as backend,retimed_holder_cpu_events as events
from gacsca.fixed_rule import retimed_holder_cpu_gather as gather,retimed_holder_cpu_boundary as boundary
from gacsca.fixed_rule import retimed_holder_flags_cpu as flags
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_projected as r
from gacsca.fixed_rule import retimed_holder_core as c,retimed_holder_program as p
from gacsca.fixed_rule import retimed_holder_native as native,retimed_holder_period_relation as relation
from gacsca.fixed_rule.wordcode import Program
from experiments.fixed_rule import run_retimed_holder_cpu_general_periods as fixture
from experiments.fixed_rule.audit_small_holder_position_events import sha


def no_upper_transition():
    stack = ExitStack()
    for obj,name in ((Program,'evaluate'),(f,'step_ring'),(f,'local_step'),(r,'step_ring'),(r,'local_step')):
        stack.enter_context(patch.object(obj,name,side_effect=AssertionError('host represented transition forbidden during physical evolution')))
    return stack


def make(top):
    data = np.zeros((len(top),f.Q),dtype=np.uint64)
    for col,cell in enumerate(top):
        data[col,list(p.layout().info)] = f.encode_cell(r.lift(cell))
    return overlay.World(backend.World(data,np.zeros((len(top),len(events.CONTROL)),dtype=np.uint64),np.zeros(len(top),dtype=np.uint64),age=0))


def raw(cells):
    return np.array([f.encode_cell(r.lift(cell) if isinstance(cell,r.Cell) else cell) for cell in cells],dtype=np.uint64)


def equal_physical(a,b):
    assert not a.positions and not b.positions
    assert a.time == b.time and a.age == b.age
    for name in overlay.STATE:
        av,bv = getattr(a.background,name),getattr(b.background,name)
        if isinstance(av,np.ndarray):
            np.testing.assert_array_equal(av,bv,err_msg=name)
        else:
            assert av == bv,name


def run(snapshot):
    n = 15; top = fixture.parents(n); target = n//2; g = p.layout()
    dirty = list(top); triple = list(top)
    for offset in (-1,0,1):
        col = (target+offset)%n; field = f's{2-offset}_rb'
        triple[col] = replace(triple[col],**{field:getattr(triple[col],field)^1})
        if offset:
            dirty[col] = triple[col]
    dirty = tuple(dirty); triple = tuple(triple)
    healthy_next = r.step_ring(top); healthy_second = r.step_ring(healthy_next)
    assert r.step_ring(dirty) == healthy_next,'two represented rb-copy errors should repair'
    assert r.step_ring(triple) != healthy_next,'negative three-copy control must differ'
    # Warm only fixed physical compilation before disabling upper references.
    for module in (native,events,gather,boundary,backend,flags):
        module.library()
    actual,reference = make(top),make(top)
    changes = {}; defects = []
    for offset in (-1,1):
        col = (target+offset)%n; field = f's{2-offset}_rb'
        primary = col*f.Q+g.info[f.COL[field]]
        for holder in (-1,0,1):
            pos = primary+holder; name = f's{2-holder}_data'; old = r.project(actual.cell(pos))
            changes[pos] = replace(old,**{name:getattr(old,name)^1})
            defects.append(dict(position=pos,field=name,upper_colony=col,represented_field=field))
    probe = tuple(sorted({(pos+j)%actual.sites for pos in changes for j in range(-14,15)}))
    data = dict(initial=raw(top),faulty_upper_initial=raw(dirty),negative_three_copy_initial=raw(triple),
                initial_probe_positions=np.array(probe,dtype=np.uint64),initial_probe_clean=raw(actual.cell(pos) for pos in probe))
    actual.inject(changes); assert actual.decode() == dirty
    data['initial_probe_faulty'] = raw(actual.cell(pos) for pos in probe)
    metrics = []; started = time.perf_counter()
    def advance_both(target_time):
        with no_upper_transition():
            result = actual.advance(target_time-actual.time)
            reference.advance(target_time-reference.time)
        metrics.append(result)
        return result
    first = advance_both(1)
    assert first['rebased_data_cells'] == 2 and not actual.positions
    assert actual.decode() == dirty and actual.decode() != top
    data['after_first_lower_tick'] = raw(actual.decode())
    data['initial_probe_after_one_tick'] = raw(actual.cell(pos) for pos in probe)
    print(json.dumps(dict(time=actual.time,stage='wrong encoded rb values survived lower correction',metrics=first)),flush=True)
    advance_both(c.CAPTURE_AGE)
    assert actual.decode() == dirty,'Info must remain wrong until actual commit'
    hold = np.array([[actual.cell(col*f.Q+a).s2_data for a in g.hold] for col in range(n)],dtype=np.uint64)
    np.testing.assert_array_equal(hold,raw(healthy_next))
    data['Hold_after_executed_upper_repair'] = hold
    print(json.dumps(dict(time=actual.time,stage='actual evaluator Hold repaired all encoded fields',seconds=time.perf_counter()-started)),flush=True)
    # A later two-holder procedure defect while the lower controller is active.
    advance_both(c.WF_START+100)
    col = target; assert actual.background.heads[col,0]
    head = col*f.Q+int(actual.background.where[col]); rng = random.Random(2026092603)
    late = {pos:replace(r.project(actual.cell(pos)),**{f's{d+2}_{name}':rng.getrandbits(width)
             for d in f.OFFSETS for name,width in f.PROCEDURE}) for pos in (head,head+2)}
    late_probe = tuple(range(head-14,head+17))
    data['late_probe_positions'] = np.array(late_probe,dtype=np.uint64)
    data['late_probe_before'] = raw(actual.cell(pos) for pos in late_probe)
    actual.inject(late); data['late_probe_faulty'] = raw(actual.cell(pos) for pos in late_probe)
    advance_both(actual.time+1); assert not actual.positions
    data['late_probe_after_one_tick'] = raw(actual.cell(pos) for pos in late_probe)
    frames = []; validations = []
    advance_both(f.U); assert actual.decode() == healthy_next
    validations.append(relation.validate_ring(actual.cell,n,parent=lambda col:healthy_next[col]))
    frames.append(raw(actual.decode())); data['physical_boundary_1_Data'] = actual.background.data.copy()
    assert not np.array_equal(actual.background.data,reference.background.data),'wrong histories should remain distinguishable before next reset'
    advance_both(f.U+1); equal_physical(actual,reference)
    data['physical_rejoin_Data'] = actual.background.data.copy()
    data['healthy_rejoin_Data'] = reference.background.data.copy()
    print(json.dumps(dict(time=actual.time,stage='complete physical rejoin after real scratch reset',seconds=time.perf_counter()-started)),flush=True)
    advance_both(2*f.U); assert actual.decode() == healthy_second
    equal_physical(actual,reference)
    validations.append(relation.validate_ring(actual.cell,n,parent=lambda col:healthy_second[col]))
    frames.append(raw(actual.decode())); data['physical_boundary_2_Data'] = actual.background.data.copy()
    data.update(decoded=np.stack(frames),expected=np.stack([raw(healthy_next),raw(healthy_second)]),
                final_heads=actual.background.heads,final_packets=actual.background.packets,
                final_flags=actual.background.flags,final_right=actual.background.right,final_left=actual.background.left)
    np.savez_compressed(snapshot,**data)
    return dict(passed=True,colonies=n,physical_sites=actual.sites,physical_ticks=actual.time,
                initial_one_bit_faults=defects,first_lower_tick_metrics=first,
                encoded_wrong_values_survive_lower_correction=True,three_upper_copy_negative_control_differs=True,
                repaired_Hold_time=c.CAPTURE_AGE,late_procedure_fault_time=c.WF_START+100,
                late_fault_sites=list(late),late_repaired_after_one_tick=True,complete_physical_rejoin_time=f.U+1,
                period_relations=validations,advance_metrics=metrics,
                no_host_upper_transition_during_evolution=True,no_healthy_reference_installed=True,
                scope='Targeted raw physical procedure faults and executed encoded-controller replica repair across one simulation link, with a second physical period and full physical rejoin. All 15 represented neighborhood positions are distinct. No stochastic threshold, general geometry repair, amplification theorem or full upper work period at depth two.')


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--output',required=True); args = parser.parse_args()
    out = Path(args.output); snapshot = out.with_suffix('.npz')
    if out.exists() or snapshot.exists():
        raise FileExistsError('preserve evidence')
    start = time.perf_counter(); result = run(snapshot)
    modules = (overlay,backend,events,gather,boundary,flags,f,r,c,p,native,relation,fixture)
    sources = [Path(__file__),*(Path(module.__file__) for module in modules),
               *(Path(module.__file__).with_suffix('.cpp') for module in (backend,events,gather,boundary)),
               Path(flags.__file__).with_suffix('.c'),events.CUDA]
    result.update(snapshot=str(snapshot),snapshot_sha256=sha(snapshot),descriptor_sha256=f.self_description().digest(),
                  source_sha256={str(path):sha(path) for path in sources},seconds=time.perf_counter()-start,
                  host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    out.write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result,indent=2),flush=True)


if __name__ == '__main__':
    main()
