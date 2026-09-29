from dataclasses import replace
import random
import unittest
from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_core as c
from gacsca.fixed_rule import compact16_holder_program as p, compact16_holder_projected as r
from gacsca.fixed_rule import compact16_holder_initial as initial, compact16_holder_native as native
from gacsca.fixed_rule import retimed_holder_rule as previous
from gacsca.fixed_rule.wordcode import LIT, NAND
from experiments.fixed_rule.certify_compact16_holder_rom import Checker, equivalence


class Compact16Holder(unittest.TestCase):
    def compare(self, neighborhood):
        scalar = f.local_step(neighborhood)
        described = f.decode_cell(f.self_description().evaluate(tuple(
            word for cell in neighborhood for word in f.encode_cell(cell))))
        self.assertEqual(scalar, described)
        self.assertEqual(scalar, native.local_step(neighborhood))
        return scalar

    def test_fixed_full_alphabet_and_three_depths(self):
        self.assertEqual(f.SCHEMA, previous.SCHEMA)
        self.assertEqual(f.WIDTH, 4090)
        self.assertEqual(r.WIDTH, 2704)
        self.assertEqual((f.Q, f.U), (1 << 14, 1 << 30))
        values = {name: (1 << width)-1 for name, width in r.SCHEMA}
        values.update(address=f.Q+37, age=3*f.U+9)
        top = (r.Cell(**values),)
        identity = r.identity()
        self.assertEqual(initial.decode_parent(top, 1, 0), top[0])
        for depth in (1, 2, 3):
            at = 0 if depth == 1 else p.layout().info[f.COL['s2_value']]
            self.assertEqual(initial.decode_parent(top, depth, at), initial.cell_at(top, depth-1, at))
            self.assertEqual(initial.physical_cells(1, depth), f.Q ** depth)
            self.assertEqual(r.identity(), identity)
        for length in (14, 16):
            with self.assertRaises(ValueError):
                r.local_step((top[0],) * length)

    def test_self_description_and_complete_own_ROM(self):
        self.assertTrue(equivalence()['passed'])
        self.assertEqual(Checker().check()['complete_raw_outputs_per_colony'], 154)
        description = p.compiled_description()
        zero = next(description.inputs+i for i, (op, a, b) in enumerate(description.operations)
                    if op == LIT and a == 0)
        outputs = list(description.outputs)
        outputs[f.COL['s2_pc']] = zero
        with self.assertRaisesRegex(AssertionError, 's2_pc'):
            equivalence(replace(description, outputs=tuple(outputs)))

    def test_zero_offset_Address_must_be_masked(self):
        high = r.lift(r.Cell(address=f.Q+37))
        for offset in f.STATIC_OFFSETS:
            for name, value in r.record((37+offset) % f.Q).items():
                self.assertEqual(getattr(high, f'p{offset+3}_{name}'), value)
        g = p.layout()
        own_kind = g.wires[7*f.FIELDS+f.COL['p3_kind']]
        pc = next(pc for pc in range(*g.stage_ranges[4])
                  if g.instructions[pc].kind == c.META and g.instructions[pc].a == own_kind)
        self.assertEqual(g.instructions[pc-1].kind, c.LOAD)
        rom = p.base_rom().copy()
        rom[g.memory_count+pc-1, 2] = g.wires[7*f.FIELDS+f.COL['address']]
        with self.assertRaises(AssertionError):
            Checker(rom).check()

    def test_scalar_descriptor_native_full_raw_boundary_and_random_cases(self):
        rng = random.Random(202609270016)
        for _ in range(24):
            cells = tuple(f.Cell(**{name: rng.getrandbits(width) for name, width in f.SCHEMA})
                          for j in f.NEIGHBORHOOD)
            self.compare(cells)
        ages = {0, f.U-1, f.U, 2*f.U-1, 3*f.U, 4*f.U-1,
                c.CAPTURE_AGE-1, c.WF_START-1, c.WF_END-1,
                *c.RESET_AGES, *c.VOTE_AGES, *c.ACTIVE_ENDS}
        for age in sorted(ages):
            for base in (0, f.Q-1, f.Q, 2*f.Q-1):
                cells = tuple(r.lift(r.Cell(address=(base+j) % (2*f.Q), age=age))
                              for j in f.NEIGHBORHOOD)
                self.compare(cells)
        for age in (f.U-1, f.U, 2*f.U-1, 3*f.U, 4*f.U-1):
            cells = (r.lift(r.Cell(address=f.Q+37, age=age, f1=1, f2=1)),) * 15
            result = self.compare(cells)
            self.assertEqual(result.age, (age+1) % f.U)

    def test_using_alphabet_width_as_Q_modulus_is_detected(self):
        description = f.self_description()
        bad = replace(description, operations=tuple(
            (op, 2*f.Q-1 if op == LIT and a == f.Q-1 else a, b)
            for op, a, b in description.operations))
        cells = tuple(r.lift(r.Cell(address=(f.Q-1+j) % f.Q, age=19))
                      for j in f.NEIGHBORHOOD)
        words = tuple(word for cell in cells for word in f.encode_cell(cell))
        self.assertNotEqual(bad.evaluate(words), f.encode_cell(f.local_step(cells)))

    def test_literal_active_controller_copies(self):
        g = p.layout()
        pc = next(pc for pc, op in enumerate(g.instructions) if op.kind == NAND and op.a == 6)
        op = g.instructions[pc]
        mask, payload = (1 << 64)-1, 0x1020304050607080
        def logical(at):
            values = dict(r.record(at % f.Q), address=at % f.Q, age=c.VOTE_AGES[0]+100,
                          data=payload if at == op.b else 0)
            if at == op.b:
                values.update(head=1, phase=c.READ_B, pc=pc, ra=op.a, rb=op.b,
                              rd=op.d, value=mask, alu=NAND)
            return c.Cell(**values)
        for holder in range(op.b-1, op.b+4):
            neighborhood = tuple(r.lift(initial.coherent_cell(logical, holder+j)) for j in f.NEIGHBORHOOD)
            actual = self.compare(neighborhood)
            slot = op.b+1-holder+2
            self.assertEqual(getattr(actual, f's{slot}_head'), 1)
            self.assertEqual(getattr(actual, f's{slot}_phase'), c.WRITE)
            self.assertEqual(getattr(actual, f's{slot}_value'), mask ^ payload)


if __name__ == '__main__':
    unittest.main()
