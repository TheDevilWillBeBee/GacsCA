import os
"""General flags plus full physical faults, checked by independent local cones."""
from contextlib import ExitStack
from dataclasses import replace
import random
import unittest
from unittest.mock import patch
from gacsca.fixed_rule import retimed_holder_general_faults as faults,retimed_holder_resident_general as general
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_projected as r,retimed_holder_native as native,retimed_holder_quotient as q,retimed_holder_program as p
from gacsca.fixed_rule.wordcode import Program


def signals(age):
    out={}
    for col,(right,left) in enumerate(((1,1),(0,1),(1,0))):
        for a in range(1,6):out[col*f.Q+a]=q.Cell(address=a,age=age,signal=left<<(5-a))
        for a in range(f.Q-5,f.Q):out[col*f.Q+a]=q.Cell(address=a,age=age,signal=right<<(f.Q-1-a))
    return out


def no_host_rule():
    stack=ExitStack()
    for obj,name in ((Program,'evaluate'),(f,'local_step'),(r,'local_step'),(native,'local_step')):
        stack.enter_context(patch.object(obj,name,side_effect=AssertionError('host transition')))
    return stack


@unittest.skipUnless(os.environ.get('FIXED_RULE_GPU_TESTS')=='1','explicit bounded GPU invocation required')
class GeneralPhysicalFaults(unittest.TestCase):
    def test_complete_random_faults_match_full_cones_across_flag_lifecycle(self):
        rng=random.Random(902);start=f.WF_START-2
        for age in (f.WF_START-1,f.WF_START+2,f.WF_START+f.Q//2,f.WF_END-1,f.WF_END+f.Q-1):
            with general.World((r.Cell(),)*3,age=start,logical=signals(start)) as base:
                base.advance(age-start)
                with faults.World(base) as world:
                    center=f.Q;points=tuple(center+i for i in range(-30,31))
                    self.assertEqual(world.read(points),base.physical_cells(points))
                    world.inject({center:r.Cell(**{name:rng.getrandbits(width) for name,width in r.SCHEMA})})
                    oracle=dict(zip(range(-30,31),world.read(points)))
                    for tick in range(1,4):
                        keep=range(-30+7*tick,31-7*tick)
                        oracle={i:r.lift(r.project(native.local_step(tuple(oracle[i+j] for j in f.NEIGHBORHOOD)))) for i in keep}
                        with no_host_rule():world.step()
                        self.assertEqual(world.read(tuple(center+i for i in keep)),tuple(oracle.values()),(age,tick))

    def test_interior_geometry_and_all_procedure_faults_rejoin_during_forcing(self):
        rng=random.Random(903);start=f.WF_START-2
        with general.World((r.Cell(),)*3,age=start,logical=signals(start)) as base:
            base.advance(f.WF_START+100-start)
            with faults.World(base) as world:
                changes={}
                for pos in (100,101):
                    original=r.project(world.read((pos,))[0]);updates={name:rng.getrandbits(width) for name,width in r.SCHEMA}
                    updates.update(address=original.address+1000,age=27)
                    changes[pos]=replace(original,**updates)
                world.inject(changes)
                # Two arbitrary complete physical sites are a genuine fault pair.
                for _ in range(4):
                    with no_host_rule():world.step()
                    if not world.positions:break
                self.assertFalse(world.positions)
                self.assertEqual(world.read(tuple(range(90,112))),base.physical_cells(tuple(range(90,112))))

    def test_wrong_data_rebase_retains_actual_nonzero_flags(self):
        start=f.WF_START-2
        with general.World((r.Cell(),)*3,age=start,logical=signals(start)) as base:
            base.advance(f.WF_END-start)
            with faults.World(base) as world:
                target=p.layout().info[f.COL['s2_value']]
                correct=world.read((target,))[0].s2_data;changes={}
                for d in (-1,0,1):
                    original=r.project(world.read((target+d,))[0]);changes[target+d]=replace(original,**{f's{2-d}_data':correct^1})
                world.inject(changes)
                with no_host_rule():world.step()
                points=tuple(range(target-8,target+9));before=world.read(points)
                self.assertTrue(any(x.f2 for x in before))
                with no_host_rule():result=world.absorb_data()
                self.assertEqual(result,dict(data_cells=1,exceptions=0));self.assertEqual(world.read(points),before)
                self.assertEqual(world.decode()[0].s2_value,1)

    def test_flag_rebase_rejects_inconsistent_wf_then_preserves_complete_state(self):
        start=f.WF_START-2
        with general.World((r.Cell(),)*3,age=start,logical=signals(start)) as base:
            base.advance(f.WF_START+2-start)
            with faults.World(base) as world:
                before=r.project(world.read((2,))[0]);self.assertEqual((before.f1,before.w2_wf2),(0,1))
                world.inject({2:replace(before,f1=1)})
                self.assertEqual(world.absorb_flags(),dict(flag_fields=0,exceptions=1))
                changes={}
                for d in f.OFFSETS:
                    cell=r.project(world.read((2+d,))[0]);changes[2+d]=replace(cell,**{f'w{2-d}_wf2':0})
                world.inject(changes);points=tuple(range(12));before=world.read(points)
                with no_host_rule():result=world.absorb_flags()
                self.assertEqual(result,dict(flag_fields=1,exceptions=0))
                self.assertEqual(world.read(points),before);self.assertEqual(base.physical_cells((2,))[0].f1,1)

    def test_packed_atomic_flag_updates_and_late_rebase_guard(self):
        start=f.WF_START-2
        with general.World((r.Cell(),)*3,age=start,logical=signals(start)) as base:
            base.advance(f.WF_START+2-start)
            with faults.World(base) as world:
                points=tuple(range(64));before=world.read(points)
                world.inject({pos:replace(r.project(cell),f2=cell.f2^1) for pos,cell in zip(points,before)})
                wanted=world.read(points);result=world.absorb_flags()
                self.assertEqual(result,dict(flag_fields=64,exceptions=0));self.assertEqual(world.read(points),wanted)
                world.advance(f.WF_END+1-base.age)
                cell=r.project(world.read((100,))[0]);world.inject({100:replace(cell,f2=cell.f2^1)})
                wanted=world.read((100,));self.assertEqual(world.absorb_flags(),dict(flag_fields=0,exceptions=1));self.assertEqual(world.read((100,)),wanted)

    def test_accelerated_wrong_front_matches_literal_exception_evolution(self):
        import numpy as np
        start=f.WF_START-2;age=f.WF_START+100;front=f.Q-8-3*(age-f.WF_START-1)
        with general.World((r.Cell(),)*3,age=start,logical=signals(start)) as a,general.World((r.Cell(),)*3,age=start,logical=signals(start)) as b:
            a.advance(age-start);b.advance(age-start)
            with faults.World(a) as fast,faults.World(b) as slow:
                for world in (fast,slow):
                    cell=r.project(world.read((front,))[0]);self.assertEqual(cell.f1,1);world.inject({front:replace(cell,f1=0)})
                with no_host_rule():
                    result=fast.advance(256);slow.advance(256,absorb_flags=False)
                self.assertEqual(result['rebased_flag_fields'],1);self.assertEqual(result['literal_exception_ticks'],1)
                self.assertTrue(slow.positions);self.assertFalse(fast.positions)
                actual=b._flags.read()
                for pos,cell in zip(slow.positions,slow.read(slow.positions)):
                    word,bit=divmod(pos,64)
                    for field,value in enumerate((cell.f1,cell.f2)):
                        actual[word,field]=np.uint64((int(actual[word,field])&~(1<<bit))|(value<<bit))
                np.testing.assert_array_equal(a._flags.read(),actual)
                points=tuple(sorted({(pos+d)%(3*f.Q) for pos in slow.positions for d in range(-7,8)}))
                self.assertEqual(fast.read(points),slow.read(points))
                self.assertTrue(np.any(a._flags.read()!=b._flags.read())) # empty exceptions is not recovery

    def test_clock_and_type_guards(self):
        from gacsca.fixed_rule import retimed_holder_resident_gather as old
        with old.World((r.Cell(),)) as reference:
            with self.assertRaisesRegex(ValueError,'general-Signal'):faults.World(reference)
        with general.World((r.Cell(),)) as base,faults.World(base) as world:
            base.advance(1)
            with self.assertRaisesRegex(ValueError,'outside exception owner'):world.read((0,))


if __name__=='__main__':unittest.main()
