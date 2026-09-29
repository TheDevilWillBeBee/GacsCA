from dataclasses import replace
import unittest
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_core as c
from gacsca.fixed_rule import retimed_holder_program as reference
from gacsca.fixed_rule import lowmask_holder_program as p, lowmask_holder_projected as r
from gacsca.fixed_rule import lowmask_holder_initial as initial
from gacsca.fixed_rule.wordcode import NAND, LIT, MASK
from experiments.fixed_rule.certify_lowmask_holder_rom import Checker, paths


class LowMaskHolder(unittest.TestCase):
    def test_fixed_identity_and_complete_encoding_at_three_depths(self):
        identity, rom = r.identity(), p.base_rom().tobytes()
        top = (r.Cell(**{name: (1 << width)-1 for name, width in r.SCHEMA}),)
        self.assertEqual(initial.decode_parent(top, 1, 0), top[0])
        for depth in (1, 2, 3):
            at = 0 if depth == 1 else p.layout().info[f.COL['s2_value']]
            self.assertEqual(initial.decode_parent(top, depth, at),
                             initial.cell_at(top, depth-1, at))
            self.assertEqual(r.identity(), identity)
            self.assertEqual(p.base_rom().tobytes(), rom)
        self.assertEqual(identity['width'], 2704)
        self.assertEqual(len(r.SCHEMA), 105)

    def test_no_access_beyond_fixed_neighborhood(self):
        for count in (14, 16):
            with self.assertRaises(ValueError):
                r.local_step((r.Cell(),) * count)

    def test_full_raw_self_reference(self):
        result = Checker().check()
        self.assertTrue(result['passed'])
        self.assertEqual(result['complete_raw_outputs_per_colony'], 154)
        self.assertEqual(result['colonies'], 15)

    def test_bad_constant_and_omitted_controller_output_rejected(self):
        g = p.layout()
        rom = p.base_rom().copy()
        rom[g.memory_count + g.stage_ranges[4][0], 2] = 0
        with self.assertRaisesRegex(AssertionError, 'raw Hold mismatch'):
            Checker(rom).check()
        rom = p.base_rom().copy()
        pc = g.description_instruction + len(p.compiled_description().operations) + f.COL['s2_pc']
        self.assertEqual(int(rom[g.memory_count+pc, 4]), g.hold[f.COL['s2_pc']])
        rom[g.memory_count+pc, 0:4] = (LIT, pc, 0, 0)
        with self.assertRaisesRegex(AssertionError, 'raw Hold mismatch'):
            Checker(rom).check()

    def test_initialization_precedes_every_changed_instruction(self):
        before = reference.base_rom().tobytes()
        g, old = p.layout(), reference.layout()
        start = old.description_instruction
        self.assertEqual(g.instructions[:start], old.instructions[:start])
        self.assertEqual(g.entries, old.entries)
        self.assertEqual(g.instructions[start].a, MASK)
        writes = [pc for pc, op in enumerate(g.instructions)
                  if (op.kind in (*c.ALU_KINDS, LIT) and op.d == p.MASK_ADDRESS)
                  or (op.kind == c.META and op.a == p.MASK_ADDRESS)
                  or (op.kind == c.SEND and op.b == p.MASK_ADDRESS)]
        self.assertEqual(writes, [start])
        self.assertLess(sum(paths(g)), sum(paths(old)))
        self.assertEqual(reference.base_rom().tobytes(), before)

    def test_physical_NAND_read_events_include_controller_copies(self):
        g = p.layout()
        pc = next(pc for pc, op in enumerate(g.instructions)
                  if op.kind == NAND and op.a == p.MASK_ADDRESS)
        op = g.instructions[pc]
        for phase, address, data, value, expected_phase, expected_value in (
                (c.READ_A, op.a, MASK, 123, c.READ_B, MASK),
                (c.READ_B, op.b, 0x1020304050607080, MASK, c.WRITE, 0xEFDFCFBFAF9F8F7F)):
            def logical(at):
                params = dict(r.record(at % f.Q), address=at % f.Q,
                              age=c.VOTE_AGES[0]+100, data=data if at == address else 0)
                if at == address:
                    params.update(head=1, phase=phase, pc=pc, ra=op.a, rb=op.b,
                                  rd=op.d, value=value, alu=NAND)
                return c.Cell(**params)
            for holder in range(address-1, address+4):
                neighborhood = tuple(r.lift(initial.coherent_cell(logical, holder+j))
                                     for j in f.NEIGHBORHOOD)
                actual = f.local_step(neighborhood)
                described = f.decode_cell(f.self_description().evaluate(tuple(
                    word for row in neighborhood for word in f.encode_cell(row))))
                self.assertEqual(actual, described)
                slot = address+1-holder+2
                if 0 <= slot < 5:
                    self.assertEqual(getattr(actual, f's{slot}_head'), 1)
                    self.assertEqual(getattr(actual, f's{slot}_phase'), expected_phase)
                    self.assertEqual(getattr(actual, f's{slot}_value'), expected_value)


if __name__ == '__main__':
    unittest.main()
