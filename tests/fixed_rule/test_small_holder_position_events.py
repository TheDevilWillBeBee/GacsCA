from dataclasses import replace
import random
import unittest

from gacsca.fixed_rule import small_holder_rule as f, small_holder_program as p
from gacsca.fixed_rule.wordcode import ADD, EQ, MASK, LIT
from experiments.fixed_rule.certify_small_holder_position_events import Modular, cases, certify_case
from experiments.fixed_rule.audit_small_holder_position_events import evaluate


class PositionEvents(unittest.TestCase):
    def test_all_position_identities_include_complete_raw_output(self):
        events = cases()
        self.assertEqual(len(events), 49)
        for event in events:
            result = certify_case(event)
            self.assertEqual(result['all_base_addresses'], 32768)
            self.assertEqual(result['full_raw_outputs'], 9 * f.FIELDS)

    def test_modular_rewrites_exhaustive_small_widths(self):
        for width in range(1, 6):
            t = Modular(p.base_rom())
            x = t.variable('x', width)
            mask = (1 << width) - 1
            formulas = []
            for delta in range(-2 * (mask + 1), 2 * (mask + 1) + 1):
                explicit = t.mask(t.op(ADD, x, t.const(delta)), width)
                normalized = t.modular_add(x, delta, width)
                self.assertEqual(explicit, normalized)
                composed = t.modular_add(normalized, -delta, width)
                self.assertEqual(composed, x)
                formulas.append((delta, normalized, t.op(EQ, x, normalized)))
            for value in range(mask + 1):
                values = evaluate(t, {'x': value})
                for delta, node, equal in formulas:
                    expected = (value + delta) & mask
                    self.assertEqual(values[node], expected)
                    self.assertEqual(values[equal], int(value == expected))

    def test_masks_and_overflow_at_machine_widths(self):
        rng = random.Random(2026092662)
        for width in (0, 1, 15, 32, 63, 64):
            t = Modular(p.base_rom())
            x = t.variable('x', 64)
            mask = (1 << width) - 1
            formulas = []
            for delta in (0, 1, -1, MASK, 1 << 63, -(1 << 63), 1 << 64):
                formula = t.mask(t.op(ADD, x, t.const(delta)), width)
                normalized = t.modular_add(x, delta, width)
                nested = t.modular_add(normalized, 3, width)
                formulas.append((delta, formula, normalized, nested))
            for value in (0, 1, MASK, MASK - 1, 1 << 63, *[rng.getrandbits(64) for _ in range(16)]):
                values = evaluate(t, {'x': value})
                for delta, formula, normalized, nested in formulas:
                    self.assertEqual(values[formula], (value + delta) & mask)
                    self.assertEqual(values[normalized], (value + delta) & mask)
                    self.assertEqual(values[nested], (value + delta + 3) & mask)

    def test_lost_controller_geometry_and_packet_outputs_fail(self):
        desc = f.self_description()
        events = {event['name']: event for event in cases()}
        for event, field in (('write', 's2_pc'), ('read_b_2', 's2_value'),
                             ('left_flight', 's1_direction'), ('quiet', 'address')):
            outputs = list(desc.outputs)
            # An address copied from the wrong neighbor must fail even at wrap.
            outputs[f.COL[field]] = (8 if field == 'address' else 7) * f.FIELDS + f.COL[field]
            with self.assertRaises(AssertionError):
                certify_case(events[event], replace(desc, outputs=tuple(outputs)))
        zero = next(desc.inputs + i for i, (kind, a, _) in enumerate(desc.operations)
                    if kind == LIT and a == 0)
        outputs = list(desc.outputs)
        outputs[f.COL['s2_rp_valid']] = zero
        with self.assertRaises(AssertionError):
            certify_case(events['send_0_7'], replace(desc, outputs=tuple(outputs)))
        with self.assertRaises(ValueError):
            certify_case(events['quiet'], replace(desc, outputs=desc.outputs[:-1]))


if __name__ == '__main__':
    unittest.main()
