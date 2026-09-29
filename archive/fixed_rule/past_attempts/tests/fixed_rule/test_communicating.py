"""Complete-rule and block-simulation tests for the communicating candidate."""
from dataclasses import fields, replace
import random
import unittest
import numpy as np
from gacsca.fixed_rule import communicating as rule
from gacsca.fixed_rule.communicating_native import (
    COL, array_from_cells, cells_from_array, library, dense_step, run)
from gacsca.fixed_rule import block


def random_cell(rng):
    return rule.Cell(**{name: rng.randrange(1 << width) for name, width in rule.SCHEMA})


def active_ring():
    # The incoming packet changes bit 0 while READ_B uses its OLD value. NAND
    # writes then change bit 1 from 1->0->1 on upper steps 2 and 8.
    return (rule.Cell(kind=rule.MEM, index=0, bit=1, head=1, phase=rule.READ_B,
                      rb=0, rd=1, value=1),
            rule.Cell(kind=rule.MEM, index=1, bit=1),
            rule.Cell(kind=rule.GATE, index=1, a=0, b=1, d=1,
                      rp_target=0, rp_bit=0, rp_cross=1, rp_valid=1))


class CommunicatingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = library()

    def test_complete_raw_schema_and_identity(self):
        self.assertEqual(rule.WIDTH, 177)
        self.assertEqual(tuple(f.name for f in fields(rule.Cell)), tuple(n for n, _ in rule.SCHEMA))
        rng = random.Random(271)
        for _ in range(50):
            cell = random_cell(rng)
            self.assertEqual(rule.decode_cell(rule.encode_cell(cell)), cell)
        self.assertEqual(rule.self_description().digest(),
                         'b0dd6468dac24bba91e494821be1dc5cb746117c065ba96413dc7ea96cc63eec')

    def test_full_description_scalar_native_all_branches(self):
        rng = random.Random(272)
        cases = [tuple(random_cell(rng) for _ in range(3)) for _ in range(100)]
        for phase in range(8):
            for kind in range(4):
                for direction in range(2):
                    c = rule.Cell(kind=kind, index=7, head=1, phase=phase, pc=7,
                                  ra=7, rb=7, rd=7, bit=1, value=1, direction=direction,
                                  first=1, last=1, a=2, b=4, d=6,
                                  lp_target=7, lp_valid=1, rp_target=7, rp_bit=1, rp_cross=1, rp_valid=1)
                    cases.append((c, c, c))
        for crossed in range(2):
            for edge in range(2):
                for destination in (7, 8):
                    cases.append((rule.Cell(last=edge, rp_valid=1, rp_target=destination,
                                            rp_cross=crossed, rp_bit=1),
                                  rule.Cell(kind=rule.MEM, index=7),
                                  rule.Cell(first=edge, lp_valid=1, lp_target=destination,
                                            lp_cross=crossed, lp_bit=0)))
        circuit = rule.self_description()
        for row in cases:
            expected = rule.local_step(*row)
            inputs = tuple(bit for cell in row for bit in rule.encode_cell(cell))
            self.assertEqual(rule.decode_cell(circuit.evaluate(inputs)), expected)
            self.assertEqual(cells_from_array(dense_step(array_from_cells(row), self.lib))[1], expected)

    def test_sparse_dense_parity_arbitrary_raw_states(self):
        rng = random.Random(273)
        for n in (1, 2, 3, 8, 17):
            reference = tuple(random_cell(rng) for _ in range(n))
            sparse, dense = array_from_cells(reference), array_from_cells(reference)
            for _ in range(30):
                run(sparse, 1, self.lib)
                dense = dense_step(dense, self.lib)
                reference = rule.step_ring(reference)
                np.testing.assert_array_equal(sparse, dense)
                self.assertEqual(cells_from_array(sparse), reference)

    def test_packet_moves_one_site_and_drops_after_second_boundary(self):
        # Two length-three regions, identical local labels. Rightward packet
        # leaves the first region and deposits in the second at its index 0.
        cells = [rule.Cell(kind=rule.MEM, index=i % 3, first=int(i % 3 == 0),
                           last=int(i % 3 == 2)) for i in range(6)]
        cells[1] = replace(cells[1], rp_valid=1, rp_target=0, rp_bit=1)
        state = array_from_cells(cells)
        run(state, 1, self.lib)
        self.assertEqual(np.flatnonzero(state[:, COL['rp_valid']]).tolist(), [2])
        self.assertEqual(int(state[:, COL['bit']].sum()), 0)
        run(state, 1, self.lib)
        self.assertEqual(int(state[:, COL['rp_valid']].sum()), 0)
        self.assertEqual(np.flatnonzero(state[:, COL['bit']]).tolist(), [3])
        cells[1] = replace(cells[1], rp_cross=1, rp_target=99)
        state = array_from_cells(cells)
        run(state, 2, self.lib)
        self.assertEqual(int(state[:, COL['rp_valid']].sum()), 0)

    def test_neighborhood_excludes_all_exterior_cells(self):
        rng = random.Random(274)
        initial = [random_cell(rng) for _ in range(15)]
        expected = rule.local_step(*initial[6:9])
        for index in set(range(15)) - {6, 7, 8}:
            changed = list(initial)
            changed[index] = random_cell(rng)
            self.assertEqual(rule.step_ring(changed)[7], expected)
            self.assertEqual(cells_from_array(dense_step(array_from_cells(changed), self.lib))[7], expected)

    def test_encoder_is_block_local_and_retrieval_banks_start_empty(self):
        first = block.encode(active_ring())
        changed_upper = list(active_ring())
        changed_upper[1] = replace(changed_upper[1], bit=0, pc=65535)
        second = block.encode(changed_upper)
        g = block.layout()
        np.testing.assert_array_equal(first[:g.colony_cells], second[:g.colony_cells])
        np.testing.assert_array_equal(first[2*g.colony_cells:], second[2*g.colony_cells:])
        self.assertEqual(block.decode(first), active_ring())
        for base in range(0, len(first), g.colony_cells):
            self.assertFalse(np.any(first[base+2:base+2+rule.WIDTH, COL['bit']]))
            self.assertFalse(np.any(first[base+2+2*rule.WIDTH:base+2+3*rule.WIDTH, COL['bit']]))
        self.assertTrue(block.check_boundary(first))
        self.assertGreater(g.timing_certificate()['arrival_margin'], 0)

    def test_successive_complete_controller_macrosteps_without_host_refills(self):
        reference = active_ring()
        physical = block.encode(reference)
        g = block.layout()
        values = [reference[1].bit]
        for _ in range(8):
            run(physical, g.period_ticks, self.lib)
            reference = rule.step_ring(reference)  # oracle only, never passed into run
            self.assertEqual(block.decode(physical), reference)
            self.assertTrue(block.check_boundary(physical))
            values.append(reference[1].bit)
        self.assertEqual([i for i in range(1, len(values)) if values[i] != values[i-1]], [2, 8])
        self.assertEqual((values[0], values[2], values[8]), (1, 0, 1))

    def test_arbitrary_raw_target_two_steps_in_nonaliased_ring(self):
        rng = random.Random(275)
        reference = tuple(random_cell(rng) for _ in range(5))
        physical = block.encode(reference)
        for _ in range(2):
            run(physical, block.layout().period_ticks, self.lib)
            reference = rule.step_ring(reference)
            self.assertEqual(block.decode(physical), reference)
            self.assertTrue(block.check_boundary(physical))


if __name__ == '__main__':
    unittest.main()
