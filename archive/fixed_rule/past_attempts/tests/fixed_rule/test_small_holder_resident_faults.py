"""Full projected physical faults: independent causal cones and exact rebasing."""
import random
import unittest
from contextlib import ExitStack
from dataclasses import replace
from unittest.mock import patch

from gacsca.fixed_rule import small_holder_resident_faults as faults
from gacsca.fixed_rule import small_holder_resident_gather as resident
from gacsca.fixed_rule import small_holder_projected as r, small_holder_rule as f
from gacsca.fixed_rule import small_holder_native as native, small_holder_core as c
from gacsca.fixed_rule import small_holder_quotient as q, small_holder_program as p
from gacsca.fixed_rule.wordcode import Program


def forbid_host_rule():
    stack = ExitStack()
    for owner, method in ((Program, 'evaluate'), (f, 'local_step'),
                          (r, 'local_step'), (native, 'local_step')):
        stack.enter_context(patch.object(owner, method, side_effect=AssertionError('host transition')))
    return stack


class PhysicalFaults(unittest.TestCase):
    def test_full_mutable_alphabet_matches_independent_shrinking_cones(self):
        rng = random.Random(194)
        for center in (0, f.Q - 1, p.layout().info[0]):
            logical = {center: q.Cell(address=center, age=1, head=1,
                                      phase=c.WRITE, rd=center, value=91)}
            with resident.World((r.Cell(),), age=1, logical=logical) as base, faults.World(base) as world:
                points = tuple((center + j) % f.Q for j in range(-30, 31))
                self.assertEqual(world.read(points), base.physical_cells(points))
                corrupted = r.Cell(**{name: rng.getrandbits(width) for name, width in r.SCHEMA})
                world.inject({center: corrupted})
                oracle = dict(zip(range(-30, 31), world.read(points)))
                self.assertEqual(oracle[0], r.lift(corrupted))
                for tick in range(1, 4):
                    keep = range(-30 + 7*tick, 31 - 7*tick)
                    oracle = {i: r.lift(r.project(native.local_step(tuple(oracle[i+j] for j in f.NEIGHBORHOOD)))) for i in keep}
                    with forbid_host_rule():
                        world.step()
                    self.assertEqual(world.read(tuple((center+i) % f.Q for i in keep)), tuple(oracle.values()))
                    self.assertTrue(all(r.lift(r.project(x)) == x for x in oracle.values()))

    def test_two_damaged_procedure_holders_heal_and_resume(self):
        target = p.layout().info[0]
        with resident.World((r.Cell(),), age=1) as base, resident.World((r.Cell(),), age=1) as clean, faults.World(base) as world:
            changes = {}
            for d in (-1, 1):
                cell = r.project(world.read((target+d,))[0])
                name = f's{2-d}_value'
                changes[target+d] = replace(cell, **{name: getattr(cell, name)^0xABC})
            world.inject(changes)
            with forbid_host_rule():
                result = world.advance(73)
                clean.advance(73)
            self.assertEqual(result['literal_exception_ticks'], 1)
            self.assertEqual(result['coherent_accelerated_ticks'], 72)
            self.assertEqual(world.positions, ())
            points = tuple(range(target-8, target+9))
            self.assertEqual(world.read(points), clean.physical_cells(points))

    def test_three_data_faults_rebase_without_silent_repair(self):
        target = p.layout().info[f.COL['s2_value']]
        with resident.World((r.Cell(),), age=1) as base, faults.World(base) as world:
            correct = world.read((target,))[0].s2_data
            changes = {}
            for d in (-1, 0, 1):
                cell = r.project(world.read((target+d,))[0])
                changes[target+d] = replace(cell, **{f's{2-d}_data': correct^1})
            world.inject(changes)
            with forbid_host_rule():
                world.step()
            self.assertEqual(len(world.positions), 5)
            points = tuple(range(target-8, target+9))
            before = world.read(points)
            with forbid_host_rule():
                result = world.absorb_data()
            self.assertEqual(result, {'data_cells': 1, 'exceptions': 0})
            self.assertEqual(world.read(points), before)
            self.assertEqual(world.time, 1)
            self.assertEqual(base.logical_cells((target,))[0].data, correct^1)
            self.assertEqual(world.decode()[0].s2_value, 1)

    def test_rebase_keeps_every_non_data_exception(self):
        target = p.layout().info[0]
        with resident.World((r.Cell(),), age=1) as base, faults.World(base) as world:
            changes = {}
            for d in f.OFFSETS:
                cell = r.project(world.read((target+d,))[0])
                updates = {f's{2-d}_data': cell.s2_data^7}
                if d == 0:
                    updates.update(age=37, signal=31, s2_head=1, s2_phase=c.WRITE, s2_value=123)
                changes[target+d] = replace(cell, **updates)
            # Use the same wrong logical Data in each holder.
            wrong = world.read((target,))[0].s2_data^7
            changes = {pos: replace(cell, **{f's{2-(pos-target)}_data': wrong}) for pos,cell in changes.items()}
            world.inject(changes)
            points = tuple(range(target-8, target+9))
            before = world.read(points)
            self.assertEqual(world.absorb_data(), {'data_cells': 1, 'exceptions': 1})
            self.assertEqual(world.positions, (target,))
            self.assertEqual(world.read(points), before)
            self.assertEqual(world.time, 0)

    def test_projection_contract_and_external_clock_guard(self):
        with resident.World((r.Cell(),), age=1) as base, faults.World(base) as world:
            with self.assertRaisesRegex(ValueError, 'complete projected'):
                world.inject({0: f.Cell()})
            with self.assertRaisesRegex(ValueError, 'complete projected'):
                world.inject({0: {'s2_value': 7}})
            base.step()
            with self.assertRaisesRegex(ValueError, 'outside exception owner'):
                world.step()

    def test_capacity_rejection_is_before_state_change(self):
        with resident.World((r.Cell(),), age=1) as base, faults.World(base) as world:
            changes = {}
            for start in range(0, 600, 200):
                points = tuple(i*32 for i in range(start, start+200))
                for pos, cell in zip(points, world.read(points)):
                    changes[pos] = replace(r.project(cell), signal=cell.signal^1)
            world.inject(changes)
            keys = world.positions
            before = world.read(keys[:100])
            with self.assertRaisesRegex(ValueError, 'causal frontier capacity'):
                world.step()
            self.assertEqual(world.time, 0)
            self.assertEqual(base.time, 0)
            self.assertEqual(world.positions, keys)
            self.assertEqual(world.read(keys[:100]), before)


if __name__ == '__main__':
    unittest.main()
