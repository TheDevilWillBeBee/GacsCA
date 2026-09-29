"""Fixed-rule, complete-controller checks for the experimental AND ROM."""
from dataclasses import replace
import hashlib
import random
import unittest

from gacsca.fixed_rule import and_holder_core as c, and_holder_rule as f
from gacsca.fixed_rule import and_holder_program as p
from gacsca.fixed_rule import and_holder_projected as r
from gacsca.fixed_rule import and_holder_initial as initial
from gacsca.fixed_rule.wordcode_and import AND, AND_ALU, LIT, MASK
from gacsca.fixed_rule.word_and_fusion import fuse_exclusive_and
from gacsca.fixed_rule import word_dag_order as order
from gacsca.fixed_rule.word_identity_and import optimize
from experiments.fixed_rule.certify_and_holder_rom import Checker, equivalence
from experiments.fixed_rule.certify_and_holder_read_b import (
    check as check_and_read_b, check_fetch as check_and_fetch,
)


class AndHolderCandidate(unittest.TestCase):
    def test_opcode_is_distinct_and_rule_alphabet_fixed(self):
        self.assertEqual(AND, 14)
        self.assertEqual(AND_ALU, 6)
        self.assertNotIn(AND, (c.HALT, c.IF_THIRD, c.LIT, c.MEM))
        self.assertEqual(c.ALU_KINDS, (c.NAND, c.ADD, c.SHR, c.EQ, c.LT, AND))
        self.assertEqual((f.Q, f.U, f.WIDTH, f.FIELDS), (16384, 1 << 30, 4090, 154))
        self.assertEqual((r.WIDTH, len(r.SCHEMA)), (2704, 105))
        self.assertEqual(r.SCHEMA, f.SCHEMA[len(f.STATIC):])
        self.assertEqual(r.Cell.__module__, r.__name__)
        self.assertEqual(f.NEIGHBORHOOD, tuple(range(-7, 8)))
        self.assertEqual(dict(c.SCHEMA)['kind'], 4)
        self.assertEqual(dict(c.SCHEMA)['alu'], 3)

    def test_fusion_preserves_every_raw_output(self):
        widths = tuple(width for _ in f.NEIGHBORHOOD for _, width in f.SCHEMA)
        optimized = optimize(f.self_description(), input_widths=widths)[0]
        fused, proof = fuse_exclusive_and(optimized)
        ordered, permutation = order.reorder(fused, reverse_outputs=True,
                                             children='original')
        self.assertTrue(order.verify(fused, ordered, permutation))
        self.assertEqual(ordered.operations, p.compiled_description().operations)
        self.assertEqual(ordered.outputs, p.compiled_description().outputs)
        self.assertGreater(proof['exclusive_cones'], 1000)
        self.assertEqual(proof['operations_before'] - proof['operations_after'],
                         proof['exclusive_cones'])
        self.assertEqual(len(ordered.outputs), f.FIELDS)
        self.assertEqual(equivalence()['complete_raw_outputs'], f.FIELDS)
        compiled = p.compiled_description()
        corrupt = list(compiled.outputs)
        corrupt[f.COL['s2_pc']] = next(compiled.inputs + i for i, (kind, a, b)
                                       in enumerate(compiled.operations)
                                       if kind == LIT and a == 0)
        with self.assertRaisesRegex(AssertionError, 's2_pc'):
            equivalence(replace(compiled, outputs=tuple(corrupt)))

    def test_actual_local_dynamics_matches_complete_descriptor(self):
        rng = random.Random(2026092814)
        cases = [tuple(f.Cell(**{name: rng.getrandbits(width)
                                 for name, width in f.SCHEMA})
                       for _ in f.NEIGHBORHOOD) for _ in range(8)]
        for age in (*c.RESET_AGES, *c.VOTE_AGES, c.CAPTURE_AGE, f.U - 1):
            cases.append(tuple(r.lift(r.Cell(address=(j + f.Q - 7) % (2*f.Q),
                                                age=age)) for j in range(15)))
        for neighbors in cases:
            raw = tuple(word for cell in neighbors for word in f.encode_cell(cell))
            self.assertEqual(p.compiled_description().evaluate(raw),
                             f.encode_cell(f.local_step(neighbors)))

    def test_physical_and_fetch_and_read_b(self):
        layout = p.layout()
        pc = next(i for i, op in enumerate(layout.instructions)
                  if op.kind == AND and 7 < op.b < f.Q - 8)
        instruction = layout.instructions[pc]
        fetched = c.advance(c.Cell(kind=AND, index=pc, pc=pc,
                                   a=instruction.a, b=instruction.b,
                                   d=instruction.d, phase=c.FETCH))
        self.assertEqual(fetched['phase'], c.READ_A)
        self.assertEqual(fetched['alu'], AND_ALU)
        self.assertEqual(fetched['rb'], instruction.b)
        payload = 0x1020304050607080
        operand = 0xFF00FF00FF00FF00

        def logical(at):
            row = dict(r.record(at % f.Q), address=at % f.Q,
                       age=c.VOTE_AGES[0] + 100,
                       data=payload if at == instruction.b else 0)
            if at == instruction.b:
                row.update(head=1, phase=c.READ_B, pc=pc,
                           ra=instruction.a, rb=instruction.b,
                           rd=instruction.d, value=operand, alu=AND_ALU)
            return c.Cell(**row)

        for holder in range(instruction.b - 1, instruction.b + 4):
            neighbors = tuple(r.lift(initial.coherent_cell(logical, holder + j))
                              for j in f.NEIGHBORHOOD)
            actual = f.local_step(neighbors)
            slot = instruction.b + 1 - holder + 2
            self.assertEqual(getattr(actual, f's{slot}_head'), 1)
            self.assertEqual(getattr(actual, f's{slot}_phase'), c.WRITE)
            self.assertEqual(getattr(actual, f's{slot}_value'), operand & payload)

    def test_locality_depth_data_and_fixed_own_rom(self):
        top = (r.Cell(address=19, age=50, s2_head=1, s2_phase=c.WRITE,
                      s2_pc=39, s2_value=MASK),)
        rule = r.identity()
        rom = hashlib.sha256(p.base_rom().tobytes()).hexdigest()
        self.assertEqual(len(p.layout().info), f.FIELDS)
        self.assertEqual(len(p.layout().hold), f.FIELDS)
        self.assertEqual(initial.decode_parent(top, 1, 0), top[0])
        self.assertEqual(initial.decode_parent(top, 2, 0),
                         initial.cell_at(top, 1, 0))
        for depth in (1, 2, 3):
            self.assertEqual(initial.physical_cells(1, depth), f.Q ** depth)
            self.assertEqual(r.identity(), rule)
            self.assertEqual(hashlib.sha256(p.base_rom().tobytes()).hexdigest(), rom)
        raw = [f.Cell() for _ in range(31)]
        before = f.step_ring(raw)[15]
        raw[23] = f.Cell(s2_data=MASK, address=99, age=31)
        self.assertEqual(f.step_ring(raw)[15], before)
        with self.assertRaises(ValueError):
            f.local_step(tuple(raw[:14]))

    def test_own_rom_executes_all_controller_fields(self):
        result = Checker().check()
        self.assertEqual(result['complete_raw_outputs_per_colony'], f.FIELDS)
        self.assertTrue(result['all_controller_outputs_checked'])
        self.assertGreater(result['instructions_checked'], 300000)
        self.assertTrue(p.layout().timing_certificate()['fits'])
        self.assertTrue(any(op.kind == AND for op in p.layout().instructions))

    def test_full_raw_and_read_b_event(self):
        event = check_and_read_b()
        self.assertEqual(event['full_raw_output_words'], 9*f.FIELDS)
        self.assertEqual(event['canonical_base_addresses'], f.Q)

    def test_full_raw_and_fetch_event(self):
        event = check_and_fetch()
        self.assertEqual(event['full_raw_output_words'], 18*f.FIELDS)
        self.assertEqual(event['canonical_base_addresses'], f.Q)


if __name__ == '__main__':
    unittest.main()
