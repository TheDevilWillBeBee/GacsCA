"""The confined candidate is one rule; region count is configuration data."""
from dataclasses import fields, replace
import random
import unittest
import numpy as np
from gacsca.fixed_rule import confined as rule
from gacsca.fixed_rule.confined_native import (
    COL, array_from_cells, cells_from_array, library, dense_step, run)
from gacsca.fixed_rule.confined_tape import encode_evaluations, decode_evaluations


def random_cell(rng):
    return rule.Cell(**{name: rng.randrange(1 << width) for name, width in rule.SCHEMA})


def simple_colony(bit=0):
    return (rule.Cell(kind=rule.MEM, index=0, bit=bit, first=1, head=1),
            rule.Cell(kind=rule.GATE, index=0),
            rule.Cell(kind=rule.LOOP, index=1, last=1))


class ConfinedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = library()

    def test_complete_raw_encoding_includes_boundary_and_direction(self):
        self.assertEqual(rule.WIDTH, 138)
        self.assertEqual(tuple(f.name for f in fields(rule.Cell)), tuple(n for n, _ in rule.SCHEMA))
        rng = random.Random(181)
        for _ in range(30):
            cell = random_cell(rng)
            self.assertEqual(rule.decode_cell(rule.encode_cell(cell)), cell)

    def test_full_description_matches_scalar_and_native(self):
        rng = random.Random(182)
        triples = [tuple(random_cell(rng) for _ in range(3)) for _ in range(100)]
        for direction in range(2):
            for first in range(2):
                for last in range(2):
                    for phase in range(4):
                        for kind in range(4):
                            cell = rule.Cell(kind=kind, first=first, last=last, direction=direction,
                                             head=1, phase=phase, index=7, pc=7, ra=7, rb=7, rd=7,
                                             a=1, b=3, d=5, bit=1, value=1)
                            triples.append((cell, cell, cell))
        circuit = rule.self_description()
        for left, center, right in triples:
            expected = rule.local_step(left, center, right)
            bits = tuple(bit for cell in (left, center, right) for bit in rule.encode_cell(cell))
            self.assertEqual(rule.decode_cell(circuit.evaluate(bits)), expected)
            actual = dense_step(array_from_cells((left, center, right)), self.lib)
            self.assertEqual(cells_from_array(actual)[1], expected)

    def test_locality_with_arbitrary_exterior_states(self):
        rng = random.Random(183)
        cells = [random_cell(rng) for _ in range(15)]
        expected = rule.local_step(*cells[6:9])
        for index in set(range(15)) - {6, 7, 8}:
            changed = list(cells)
            changed[index] = random_cell(rng)
            self.assertEqual(rule.step_ring(changed)[7], expected)
            self.assertEqual(cells_from_array(dense_step(array_from_cells(changed), self.lib))[7], expected)

    def test_sparse_dense_parity_including_head_collisions(self):
        rng = random.Random(184)
        for n in (1, 2, 3, 7, 13):
            initial = []
            for _ in range(n):
                cell = random_cell(rng)
                if not cell.head:
                    cell = replace(cell, **dict.fromkeys(rule.CONTROL, 0))
                initial.append(cell)
            reference = tuple(initial)
            sparse, dense = array_from_cells(reference), array_from_cells(reference)
            for _ in range(40):
                run(sparse, 1, self.lib)
                dense = dense_step(dense, self.lib)
                reference = rule.step_ring(reference)
                np.testing.assert_array_equal(sparse, dense)
                self.assertEqual(cells_from_array(sparse), reference)
        invalid = array_from_cells((rule.Cell(pc=1),))
        with self.assertRaises(ValueError):
            run(invalid, 1, self.lib)

    def test_colonies_reuse_labels_without_head_leakage(self):
        joint = array_from_cells(simple_colony(0) + simple_colony(1))
        separate = [array_from_cells(simple_colony(0)), array_from_cells(simple_colony(1))]
        initial = joint.copy()
        memory_values = [set(), set()]
        for _ in range(140):
            run(joint, 1, self.lib)
            for i, state in enumerate(separate):
                run(state, 1, self.lib)
                np.testing.assert_array_equal(joint[i*3:(i+1)*3], state)
                self.assertEqual(int(state[:, COL['head']].sum()), 1)
                memory_values[i].add(int(state[0, COL['bit']]))
        self.assertEqual(memory_values, [{0, 1}, {0, 1}])
        for name in ('kind', 'index', 'a', 'b', 'd', 'first', 'last'):
            np.testing.assert_array_equal(joint[:, COL[name]], initial[:, COL[name]])

    def test_region_count_does_not_change_rule_or_local_program(self):
        before = rule.identity()
        rows = [(rule.Cell(), rule.Cell(), rule.Cell())] * 48
        large, geometry = encode_evaluations(rows)
        small, other = encode_evaluations(rows[:1])
        self.assertEqual(before, rule.identity())
        self.assertEqual(geometry, other)
        self.assertGreater(len(large), 65536)
        for name in ('kind', 'index', 'a', 'b', 'd', 'first', 'last'):
            expected = np.tile(small[:, COL[name]], 48)
            np.testing.assert_array_equal(large[:, COL[name]], expected)
        self.assertEqual(before['description_sha256'],
                         '94bd3ef17aa969a584d04a8b8dccb999f2bc8b21546cb5a90af63bd574b72bc5')

    def test_physical_self_description_in_two_colonies(self):
        # Both reflected and transmitted active heads; full raw controller output.
        left = rule.Cell(kind=rule.GATE, index=7, pc=7, head=1, a=4, b=9, d=11)
        center = rule.Cell(kind=rule.MEM, index=3, head=1, phase=rule.WRITE,
                           rd=3, pc=65535, value=1, last=1)
        right = rule.Cell(head=1, direction=rule.LEFT, phase=rule.READ_B, value=1)
        neighborhoods = ((left, center, right), (right, left, center))
        physical, geometry = encode_evaluations(neighborhoods)
        run(physical, geometry.period_ticks, self.lib)
        self.assertEqual(decode_evaluations(physical, geometry),
                         tuple(rule.local_step(*row) for row in neighborhoods))
        for base in (0, geometry.colony_cells):
            self.assertEqual(physical[base, COL['head']], 1)
            self.assertEqual(physical[base, COL['direction']], rule.RIGHT)
            self.assertEqual(physical[base, COL['pc']], 0)


if __name__ == '__main__':
    unittest.main()
