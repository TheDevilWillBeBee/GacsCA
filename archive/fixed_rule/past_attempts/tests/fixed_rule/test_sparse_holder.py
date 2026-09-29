import unittest
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_core as c
from gacsca.fixed_rule import sparse_holder_program as p, sparse_holder_projected as r
from gacsca.fixed_rule import sparse_holder_initial as initial
from gacsca.fixed_rule.wordcode import NAND
from experiments.fixed_rule.certify_sparse_holder_rom import Checker


class SparseHolder(unittest.TestCase):
    def test_complete_self_reference_with_unused_raw_inputs_unrestricted(self):
        result = Checker().check()
        self.assertTrue(result['passed'])
        self.assertEqual(result['complete_encoded_fields'], 154)
        self.assertEqual(result['complete_raw_outputs_per_colony'], 154)
        self.assertTrue(result['all_controller_outputs_checked'])

    def test_fixed_identity_and_every_controller_field_at_three_depths(self):
        identity = r.identity()
        top = (r.Cell(**{name: (1 << width)-1 for name, width in r.SCHEMA}),)
        self.assertEqual(initial.decode_parent(top, 1, 0), top[0])
        for depth in (1, 2, 3):
            at = 0 if depth == 1 else p.layout().info[f.COL['s2_value']]
            self.assertEqual(initial.decode_parent(top, depth, at), initial.cell_at(top, depth-1, at))
            self.assertEqual(r.identity(), identity)
        self.assertEqual(identity['width'], 2704)
        self.assertEqual(len(r.SCHEMA), 105)
        for count in (14, 16):
            with self.assertRaises(ValueError):
                r.local_step((top[0],) * count)

    def test_all_used_inputs_have_histories_or_explicit_ROM_regeneration(self):
        g = p.layout()
        self.assertEqual(set(g.required_inputs), set(g.gathered_inputs) | set(g.regenerated_inputs))
        self.assertFalse(set(g.gathered_inputs) & set(g.regenerated_inputs))
        self.assertEqual(len(g.gathered_inputs), 689)
        self.assertEqual(len(g.regenerated_inputs), 49)
        self.assertEqual(len(g.info), len(g.hold))
        self.assertEqual(len(g.info), f.FIELDS)
        addresses = {g.history(stage, wire//f.FIELDS-7, wire % f.FIELDS)
                     for stage in range(3) for wire in g.gathered_inputs}
        self.assertEqual(len(addresses), 3*689)
        self.assertFalse(addresses & set(g.votes))
        with self.assertRaises(KeyError):
            g.history(0, 0, f.COL['p3_kind'])
        with self.assertRaises(KeyError):
            g.history(0, -7, f.COL['s2_pc'])
        widths = dict(c.SCHEMA)
        for col, name in enumerate(c.STATIC):
            self.assertTrue(all(int(value) < 1 << widths[name] for value in p.base_rom()[:, col]))

    def test_wrong_controller_retrieval_and_own_metadata_rejected(self):
        g = p.layout()
        target = g.history(0, 1, f.COL['s2_pc'])
        pc = next(pc for pc, op in enumerate(g.instructions)
                  if op.kind == c.SEND and op.b == target)
        rom = p.base_rom().copy()
        rom[g.memory_count+pc, 2] = g.info[f.COL['s2_value']]
        with self.assertRaisesRegex(AssertionError, 'gathered history mismatch'):
            Checker(rom).check()
        pc = next(pc for pc in range(*g.stage_ranges[4]) if g.instructions[pc].kind == c.META)
        rom = p.base_rom().copy()
        rom[g.memory_count+pc, 3] = 7
        with self.assertRaises(AssertionError):
            Checker(rom).check()

    def test_omitted_raw_controller_output_is_rejected(self):
        g = p.layout()
        target = g.hold[f.COL['s2_pc']]
        pc = next(pc for pc in range(g.description_instruction+len(p.compiled_description().operations),
                                    g.stage_ranges[4][1])
                  if g.instructions[pc].kind in c.ALU_KINDS and g.instructions[pc].d == target)
        rom = p.base_rom().copy()
        # Keep a valid data-copy operation, but copy a different raw field.
        rom[g.memory_count+pc, 2] = g.wires[7*f.FIELDS+f.COL['s2_value']]
        with self.assertRaisesRegex(AssertionError, 'raw Hold mismatch'):
            Checker(rom).check()

    def test_active_physical_read_updates_all_controller_copies(self):
        g = p.layout()
        pc = next(pc for pc, op in enumerate(g.instructions) if op.kind == NAND and op.a == 6)
        op = g.instructions[pc]
        payload, mask = 0x1020304050607080, (1 << 64)-1
        def logical(at):
            values = dict(r.record(at % f.Q), address=at % f.Q, age=c.VOTE_AGES[0]+100,
                          data=payload if at == op.b else 0)
            if at == op.b:
                values.update(head=1, phase=c.READ_B, pc=pc, ra=op.a, rb=op.b,
                              rd=op.d, value=mask, alu=NAND)
            return c.Cell(**values)
        for holder in range(op.b-1, op.b+4):
            neighborhood = tuple(r.lift(initial.coherent_cell(logical, holder+j)) for j in f.NEIGHBORHOOD)
            actual = f.local_step(neighborhood)
            described = f.decode_cell(f.self_description().evaluate(tuple(
                word for row in neighborhood for word in f.encode_cell(row))))
            self.assertEqual(actual, described)
            slot = op.b+1-holder+2
            self.assertEqual(getattr(actual, f's{slot}_head'), 1)
            self.assertEqual(getattr(actual, f's{slot}_phase'), c.WRITE)
            self.assertEqual(getattr(actual, f's{slot}_value'), mask ^ payload)


if __name__ == '__main__':
    unittest.main()
