import json
from pathlib import Path
import unittest
import numpy as np

from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_core as c
from gacsca.fixed_rule import retimed_holder_projected as r, retimed_holder_program as p
from experiments.fixed_rule.certify_retimed_holder_prefix_dependence import analyze, delivered_support, bounded
from experiments.fixed_rule.audit_retimed_holder_prefix_embedding import validate_entry, safe_raw_colonies


class PrefixDependence(unittest.TestCase):
    def test_actual_timed_events_and_complete_fields(self):
        schedule = json.loads(Path('figs/fixed_rule/retimed_holder_mail_schedule_v1.json').read_text())
        result = analyze(schedule)
        self.assertEqual(result['logical_owner_offsets'], list(range(-7, 8)))
        self.assertEqual(sum(len(x) for x in result['raw_field_partition'].values()), f.FIELDS)
        self.assertEqual(sum(x['deliveries'] for x in result['phases']), 6478)
        self.assertEqual(result['phases'][-1]['controller_owner_offsets'], list(range(-7, 8)))
        self.assertTrue(result['initial_Signals_zero_required'])

    def test_routes_use_unbounded_integer_colony_offsets(self):
        self.assertEqual(delivered_support(frozenset((0,)), 7, c.LEFT), frozenset((7,)))
        self.assertEqual(delivered_support(frozenset((0,)), 7, c.RIGHT), frozenset((-7,)))
        with self.assertRaisesRegex(AssertionError, 'escapes seven'):
            bounded(delivered_support(frozenset((-7, 7)), 7, c.LEFT))

    def test_initial_signal_or_controller_cannot_be_silently_omitted(self):
        entry = dict(bank=np.zeros((1, p.layout().memory_count+5), dtype=np.uint64),
                     age=np.uint64(0), time=np.uint64(0), counts=np.zeros(1, dtype=np.uint64),
                     active_rows=np.zeros((1, 64, 25), dtype=np.uint64),
                     flags=np.zeros((f.Q//64, 2), dtype=np.uint64),
                     signals=np.zeros((1, 2), dtype=np.uint64))
        validate_entry(entry)
        with self.assertRaisesRegex(AssertionError, 'complete typed entry'):
            validate_entry(dict(entry, active_rows=np.zeros((1, 64, 1), dtype=np.uint64)))
        for field in ('signals', 'active_rows', 'flags', 'counts'):
            changed = dict(entry, **{field: np.ones_like(entry[field])})
            with self.assertRaisesRegex(AssertionError, 'entry must be zero'):
                validate_entry(changed)

    def test_retained_signal_is_a_real_counterexample_to_banks_only_unrestricted_entry(self):
        def neighborhood(bit):
            return tuple(r.lift(r.Cell(address=100+d, age=f.RESET_AGES[4]+1,
                                      signal=(1 << (2-d)) if bit and -2 <= d <= 2 else 0))
                         for d in f.NEIGHBORHOOD)
        zero, one = f.local_step(neighborhood(0)), f.local_step(neighborhood(1))
        self.assertEqual(zero.signal, 0)
        self.assertEqual(one.signal, 4)
        for name, _ in f.PROCEDURE:
            for slot in range(5):
                self.assertEqual(getattr(zero, f's{slot}_{name}'), getattr(one, f's{slot}_{name}'))

    def test_raw_replica_halo_and_real_wraparound(self):
        selected = (f.Q-20+np.arange(73)) % f.Q
        self.assertEqual(safe_raw_colonies(selected, f.Q), list(range(8, 65)))
        selected[40] += 1
        with self.assertRaises(AssertionError):
            safe_raw_colonies(selected, f.Q)


if __name__ == '__main__':
    unittest.main()
