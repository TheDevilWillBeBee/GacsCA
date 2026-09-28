"""Initialization/depth identity only; not tests of deeper physical dynamics."""
import random
import unittest
from gacsca.fixed_rule import block, block_initial, communicating as rule
from gacsca.fixed_rule.communicating_native import cells_from_array


class BlockInitialTests(unittest.TestCase):
    def test_lazy_initial_cells_match_materialized_one_level(self):
        top = (rule.Cell(bit=1), rule.Cell(head=1, phase=rule.TRANSMIT, rb=7, rd=1))
        physical = block.encode(top)
        rng = random.Random(81)
        positions = [0, block.layout().info_start, len(physical)-1]
        positions.extend(rng.randrange(len(physical)) for _ in range(100))
        for position in positions:
            self.assertEqual(block_initial.cell_at(top, 1, position),
                             cells_from_array(physical[position:position+1])[0])

    def test_depth_one_two_three_initialization_has_identical_physical_rule(self):
        top = (rule.Cell(bit=1, rp_valid=1, rp_target=9), rule.Cell(first=1, last=1, head=1))
        before = rule.identity()
        rng = random.Random(82)
        for depth in (1, 2, 3):
            parents = block_initial.physical_cells(len(top), depth-1)
            for position in (0, parents-1, rng.randrange(parents)):
                expected = block_initial.cell_at(top, depth-1, position)
                self.assertEqual(block_initial.decode_parent(top, depth, position), expected)
                self.assertEqual(len(rule.encode_cell(expected)), 177)
            self.assertEqual(block_initial.resource_estimate(len(top), depth)['fixed_rule'], before)
        self.assertEqual(rule.identity(), before)

    def test_termination_is_ordinary_quiescent_top_data(self):
        # Both bits are fixed states of the SAME rule, not a special top kernel.
        for bit in (0, 1):
            top = (rule.Cell(bit=bit),)
            self.assertEqual(rule.step_ring(top), top)
            bit_offset = sum(width for name, width in rule.SCHEMA[:5])
            address = block.layout().info_start + bit_offset
            for depth in (1, 2, 3):
                position = sum(address * block.layout().colony_cells**j for j in range(depth))
                cell = block_initial.cell_at(top, depth, position)
                self.assertEqual(cell.bit, bit)
                self.assertEqual(len(rule.encode_cell(cell)), 177)


if __name__ == '__main__':
    unittest.main()
