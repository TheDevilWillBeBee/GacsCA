from dataclasses import replace
import unittest
from gacsca.fixed_rule import small_holder_rule as f, small_holder_core as c, small_holder_program as p
from gacsca.fixed_rule.wordcode import EQ
from experiments.fixed_rule.certify_small_holder_scan_events import Conditional, cases, prepare, certify_case
from experiments.fixed_rule.audit_small_holder_position_events import evaluate


class ScanEvents(unittest.TestCase):
    def test_all_conditional_full_raw_identities(self):
        events = cases()
        self.assertEqual(len(events), 43)
        for event in events:
            self.assertEqual(certify_case(event)['full_raw_outputs'], 9 * f.FIELDS)

    def test_missing_hypotheses_do_not_prove_flight_or_reflection(self):
        events = {event['name']: event for event in cases()}
        for name in ('right_flight_0', 'right_flight_3', 'right_flight_6',
                     'left_meta_fallback_0', 'meta_hit_last_0'):
            with self.assertRaises(AssertionError):
                certify_case(events[name], use_hypotheses=False)
        self.assertTrue(certify_case(events['right_flight_7'], use_hypotheses=False)['passed'])

    def test_disequality_rewrite_is_conditional_and_symmetric(self):
        t = Conditional(p.base_rom())
        x, y = t.variable('x', 2), t.variable('y', 2)
        t.unequal(x, y)
        a, b = t.op(EQ, x, y), t.op(EQ, y, x)
        for xv in range(4):
            for yv in range(4):
                values = evaluate(t, {'x': xv, 'y': yv})
                self.assertEqual(t.hypotheses_hold(values), xv != yv)
                if t.hypotheses_hold(values):
                    self.assertEqual(values[a], int(xv == yv))
                    self.assertEqual(values[b], int(yv == xv))
        with self.assertRaises(ValueError):
            t.unequal(x, x)

    def test_matching_write_is_a_concrete_counterexample_to_unqualified_flight(self):
        event = next(event for event in cases() if event['name'] == 'right_flight_3')
        t, raw = prepare(event)
        rows = tuple(raw(j) for j in f.NEIGHBORHOOD)
        want = raw(0, after=True)
        assignments = {node[1]: 0 for node in t.nodes if node[0] == 'variable'}
        assignments.update(meta_0_kind=c.MEM, meta_0_index=19, old_rd=19, old_value=23)
        values = evaluate(t, assignments)
        self.assertFalse(t.hypotheses_hold(values))
        actual = f.local_step(tuple(f.decode_cell(tuple(values[i] for i in row)) for row in rows))
        expected = tuple(values[i] for i in want)
        self.assertNotEqual(f.encode_cell(actual), expected)
        self.assertEqual(getattr(actual, 's2_data'), 23)
        self.assertEqual(expected[f.COL['s2_data']], 0)

    def test_reflection_cannot_drop_direction_or_meta_phase(self):
        desc = f.self_description()
        events = {event['name']: event for event in cases()}
        for name, field in (('right_reflect_7', 's2_direction'),
                            ('left_meta_ready', 's2_value'),
                            ('meta_hit_last_2', 's2_phase'),
                            ('left_reflect_7', 's2_phase')):
            outputs = list(desc.outputs)
            outputs[f.COL[field]] = 7 * f.FIELDS + f.COL[field]
            with self.assertRaises(AssertionError):
                certify_case(events[name], replace(desc, outputs=tuple(outputs)))


if __name__ == '__main__':
    unittest.main()
