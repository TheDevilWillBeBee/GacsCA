from dataclasses import replace
import unittest

from gacsca.fixed_rule import small_holder_rule as f, small_holder_core as c, small_holder_program as p
from gacsca.fixed_rule import small_holder_native as native
from gacsca.fixed_rule.wordcode import ADD, EQ, LT, MASK
from experiments.fixed_rule.certify_small_holder_clock_events import Intervals, cases, prepare, certify_case, regular_intervals
from experiments.fixed_rule.audit_small_holder_position_events import evaluate


class ClockEvents(unittest.TestCase):
    def test_partition_covers_exactly_regular_active_clocks(self):
        intervals = regular_intervals()
        excluded = set(c.RESET_AGES) | set(c.VOTE_AGES) | {c.CAPTURE_AGE - 1, f.U - 1}
        self.assertEqual(len(intervals), 7)
        self.assertTrue(all(a[1] < b[0] for a, b in zip(intervals, intervals[1:])))
        cuts = {0, f.U - 1, *c.RESET_AGES, *c.ACTIVE_ENDS, *c.VOTE_AGES, c.CAPTURE_AGE - 1}
        probes = {x + d for x in cuts for d in (-1, 0, 1) if 0 <= x + d < f.U}
        probes.update((lo + hi) // 2 for lo, hi in intervals)
        for age in probes:
            self.assertEqual(any(lo <= age <= hi for lo, hi in intervals), c.active(age) and age not in excluded)
        expected = sum(hi - lo for lo, hi in zip(c.RESET_AGES, c.ACTIVE_ENDS))
        expected -= sum(c.active(age) for age in excluded)
        self.assertEqual(sum(hi - lo + 1 for lo, hi in intervals), expected)
        self.assertTrue(any(lo <= c.CAPTURE_AGE <= hi for lo, hi in intervals))

    def test_interval_comparison_rewrites_exhaustive_small_domains(self):
        for width in (1, 2, 3):
            ranges = [(lo, hi) for lo in range(1 << width) for hi in range(lo, 1 << width)]
            for xl, xh in ranges:
                for yl, yh in ranges:
                    terms = Intervals(p.base_rom())
                    x = terms.bounded('x', width, xl, xh)
                    y = terms.bounded('y', width, yl, yh)
                    eq, lt, gt = terms.op(EQ, x, y), terms.op(LT, x, y), terms.op(LT, y, x)
                    for xv in range(xl, xh + 1):
                        for yv in range(yl, yh + 1):
                            values = evaluate(terms, {'x': xv, 'y': yv})
                            self.assertEqual(values[eq], int(xv == yv))
                            self.assertEqual(values[lt], int(xv < yv))
                            self.assertEqual(values[gt], int(yv < xv))

    def test_range_propagation_with_wrap_and_complement(self):
        ranges = ((0, 0), (0, 7), (3, 15), (MASK - 3, MASK), (0, MASK))
        for lo, hi in ranges:
            terms = Intervals(p.base_rom())
            x = terms.bounded('x', 64, lo, hi)
            nodes = [x, terms.inv(x)]
            for delta in (-1, 0, 1, 3, MASK):
                added = terms.op(ADD, x, terms.const(delta))
                nodes.append(added)
                for width in (0, 1, 15, 32, 64):
                    nodes.append(terms.modular_add(added, delta, width))
            for value in {lo, hi, (lo + hi) // 2}:
                values = evaluate(terms, {'x': value})
                for node in nodes:
                    a, b = terms.bounds(node)
                    self.assertLessEqual(a, values[node])
                    self.assertLessEqual(values[node], b)
            with self.assertRaises(ValueError):
                terms.bounded('x', 64, lo, hi)
        with self.assertRaises(ValueError):
            Intervals(p.base_rom()).bounded('bad', 3, 0, 8)

    def test_fetch_all_used_kinds_and_branch_clocks(self):
        events = [event for event in cases() if event['family'] == 'fetch']
        self.assertEqual({op.kind for op in p.layout().instructions} - {event['kind'] for event in events}, set())
        for interval in (regular_intervals()[0], regular_intervals()[3]):
            for event in events:
                self.assertEqual(certify_case(event, interval)['full_raw_outputs'], 9 * f.FIELDS)

    def test_capture_predecessor_is_a_real_counterexample(self):
        event = next(event for event in cases() if event['family'] == 'position' and event['name'] == 'quiet')
        interval = (c.CAPTURE_AGE - 1, c.CAPTURE_AGE - 1)
        with self.assertRaises(AssertionError):
            certify_case(event, interval)
        terms, raw = prepare(event, interval)
        rows = tuple(raw(j) for j in f.NEIGHBORHOOD)
        wanted = raw(0, after=True)
        assignments = {node[1]: 0 for node in terms.nodes if node[0] == 'variable'}
        assignments.update(physical_age=c.CAPTURE_AGE-1, base_address=3, data_0=1)
        values = evaluate(terms, assignments)
        neighbors = tuple(f.decode_cell(tuple(values[i] for i in row)) for row in rows)
        scalar = f.local_step(neighbors)
        self.assertEqual(scalar, native.local_step(neighbors))
        self.assertEqual(scalar.signal, 4)
        self.assertEqual(values[wanted[f.COL['signal']]], 0)
        self.assertEqual(scalar.age, c.CAPTURE_AGE)

    def test_general_fetch_cannot_omit_loaded_operand(self):
        event = next(event for event in cases() if event['family'] == 'fetch' and event['kind'] == c.META and not event['last'])
        desc = f.self_description()
        outputs = list(desc.outputs)
        outputs[f.COL['s2_rb']] = 7 * f.FIELDS + f.COL['s2_rb']
        with self.assertRaises(AssertionError):
            certify_case(event, regular_intervals()[3], replace(desc, outputs=tuple(outputs)))


if __name__ == '__main__':
    unittest.main()
