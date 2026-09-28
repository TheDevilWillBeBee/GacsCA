"""Run with python -m unittest discover -s tests/fixed_rule -v."""
from dataclasses import fields, replace
import inspect
import random
import unittest
import numpy as np
from gacsca.fixed_rule.machine import (
    Cell, SCHEMA, WIDTH, MASK, MEM, GATE, LOOP, INERT, FETCH, READ_A, READ_B,
    WRITE, CONTROL, NEIGHBORHOOD, encode_cell, decode_cell, local_step,
    step_ring, self_description, identity)
from gacsca.fixed_rule.tape import (array_from_cells, cells_from_array, encode_ring,
                                   decode_ring, ring_layout, COL)
from gacsca.fixed_rule.native import library, dense_step, run


def random_cell(rng):
    return Cell(**{name: rng.randrange(1 << width) for name, width in SCHEMA})


def active_ring():
    # This represented machine actually executes NAND, writes, and restarts.
    return (Cell(kind=MEM, index=0, bit=0),
            Cell(kind=GATE, index=0, a=0, b=0, d=0, head=1),
            Cell(kind=LOOP, index=1))


class FixedRuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = library()

    def test_schema_covers_every_raw_field(self):
        self.assertEqual(tuple(f.name for f in fields(Cell)), tuple(n for n, _ in SCHEMA))
        self.assertEqual(WIDTH, 135)
        for name, width in SCHEMA:
            value = 0 if getattr(Cell(), name) else (1 << width) - 1
            cell = Cell(**{name: value})
            self.assertEqual(decode_cell(encode_cell(cell)), cell)
            self.assertNotEqual(encode_cell(cell), encode_cell(Cell()))
        with self.assertRaises(ValueError):
            decode_cell(encode_cell(Cell())[:-1])

    def test_raw_arbitrary_state_description_matches_python_and_c(self):
        rng = random.Random(123)
        cases = [(random_cell(rng), random_cell(rng)) for _ in range(100)]
        # Random 16-bit labels almost never match: force ALL control branches.
        for phase in range(4):
            for kind in range(4):
                for bit in range(2):
                    l = Cell(kind=kind, index=9, head=1, phase=phase, pc=9,
                             ra=9, rb=9, rd=9, bit=bit, value=1,
                             a=65535, b=7, d=19)
                    cases.append((l, l))
        cases.append((Cell(kind=MEM, head=1, phase=WRITE, pc=MASK), Cell()))
        for left, center in cases:
            expected = local_step(left, center)
            bits = self_description().evaluate(encode_cell(left) + encode_cell(center))
            self.assertEqual(decode_cell(bits), expected)
            actual = dense_step(array_from_cells((left, center)), self.lib)
            self.assertEqual(cells_from_array(actual)[1], expected)

    def test_radius_guard_and_exterior_perturbations(self):
        rng = random.Random(42)
        ring = tuple(random_cell(rng) for _ in range(13))
        self.assertEqual(NEIGHBORHOOD, (-1, 0))
        class Guard:
            def __getitem__(self, offset):
                if offset not in NEIGHBORHOOD:
                    raise AssertionError('outside declared neighborhood')
                return ring[6 + offset]
        guarded = Guard()
        expected = local_step(guarded[-1], guarded[0])
        for j in set(range(13)) - {5, 6}:
            changed = list(ring)
            changed[j] = random_cell(rng)
            self.assertEqual(step_ring(changed)[6], expected)
            self.assertEqual(cells_from_array(dense_step(array_from_cells(changed), self.lib))[6], expected)
        # Its public API cannot receive a ring, position, callback, or depth.
        self.assertEqual(tuple(inspect.signature(local_step).parameters), ('left', 'center'))

    def test_sparse_evolution_equals_dense_every_tick(self):
        for cells in (active_ring(), (Cell(kind=MEM, head=1, phase=WRITE, value=1),)):
            sparse, dense = array_from_cells(cells), array_from_cells(cells)
            reference = cells
            for _ in range(80):
                run(sparse, ticks=1, lib=self.lib)
                dense = dense_step(dense, self.lib)
                reference = step_ring(reference)
                np.testing.assert_array_equal(sparse, dense)
                self.assertEqual(cells_from_array(dense), reference)
        for cells in ((Cell(),), (Cell(head=1), Cell(head=1)),
                      (Cell(head=1), Cell(pc=1))):
            with self.assertRaises(ValueError):
                run(array_from_cells(cells), ticks=1, lib=self.lib)

    def test_identical_description_across_ring_sizes_without_depth_dispatch(self):
        before = identity()
        for n in (1, 2, 3, 7):
            tape, layout = encode_ring(tuple(Cell(index=i) for i in range(n)))
            self.assertEqual(layout.description_sha256, before['description_sha256'])
            self.assertEqual(tape.shape[1], len(SCHEMA))
            self.assertEqual(decode_ring(tape, layout), tuple(Cell(index=i) for i in range(n)))
        self.assertEqual(identity(), before)
        # A pinned semantic fingerprint catches a swapped depth-specific rule.
        self.assertEqual(before['description_sha256'],
                         'ce8964c17a84e955dbe4e724e8f372b2a72433af51a45bfa50e11e6baa960323')
        for callable_ in (local_step, self_description, ring_layout, run):
            self.assertNotIn('depth', inspect.signature(callable_).parameters)

    def test_autonomous_self_description_macrosteps(self):
        reference = active_ring()
        physical, layout = encode_ring(reference)
        seen_bits, seen_phases, writes = set(), set(), []
        previous_bit = reference[0].bit
        # No encode, input refill, host transitions, or reference bits are passed
        # into the running tape after initialization. Reference is diagnostic.
        for period in range(1, 27):
            metrics = run(physical, ticks=layout.period_ticks, lib=self.lib)
            self.assertEqual(metrics['completed_periods'], 1)
            self.assertEqual(metrics['physical_ticks'], layout.period_ticks)
            reference = step_ring(reference)
            actual = decode_ring(physical, layout)
            self.assertEqual(actual, reference, f'macrostep {period}')
            seen_bits.add(actual[0].bit)
            if actual[0].bit != previous_bit:
                writes.append(actual[0].bit)
            previous_bit = actual[0].bit
            seen_phases.update(c.phase for c in actual if c.head)
        self.assertEqual(seen_bits, {0, 1})
        self.assertEqual(writes, [1, 0])
        self.assertEqual(seen_phases, {FETCH, READ_A, READ_B, WRITE})

    def test_recursive_ring_encoding_cannot_masquerade_as_a_hierarchy(self):
        before = identity()
        physical, _ = encode_ring((Cell(),))
        with self.assertRaisesRegex(ValueError, 'not a hierarchy encoder'):
            encode_ring(cells_from_array(physical))
        self.assertEqual(identity(), before)

    def test_capacity_failure_is_explicit_not_a_new_kernel(self):
        with self.assertRaisesRegex(ValueError, 'not a hierarchy encoder'):
            ring_layout(100)


if __name__ == '__main__':
    unittest.main()
