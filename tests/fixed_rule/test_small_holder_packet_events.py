import random
import unittest
from unittest.mock import patch

from gacsca.fixed_rule import small_holder_rule as f, small_holder_core as c, small_holder_native as native
from experiments.fixed_rule import certify_small_holder_packet_events as proof
from experiments.fixed_rule.audit_small_holder_packet_events import instantiate


class PacketEvents(unittest.TestCase):
    def event(self, name):
        return next(event for event in proof.cases() if event['name'] == name)

    def test_edge_and_priority_full_raw_identities(self):
        interval = proof.clock.regular_intervals()[0]
        for name in ('left_edge_hit_drop', 'right_edge_drop_hit',
                     'interior_hit_hit', 'left_edge_nonmemory_match',
                     'interior_deliver_read_a', 'interior_deliver_write',
                     'interior_deliver_send_0_7', 'interior_overwrite_send_1_7'):
            with self.subTest(name=name):
                self.assertEqual(proof.certify_case(self.event(name), interval)['full_raw_outputs'], 9*f.FIELDS)

    def test_all_clocks_cover_edge_decrement(self):
        for interval in proof.clock.regular_intervals():
            self.assertTrue(proof.certify_case(self.event('left_edge_carry_carry'), interval)['passed'])

    def test_right_delivery_wins_and_read_uses_old_data(self):
        terms, raw = proof.prepare(self.event('interior_deliver_read_a'), proof.clock.regular_intervals()[0])
        rows = [raw(j) for j in f.NEIGHBORHOOD]
        wanted = raw(0, after=True)
        values = instantiate(terms, 'random', random.Random(31))
        neighbors = tuple(f.decode_cell(tuple(values[x] for x in row)) for row in rows)
        result = f.local_step(neighbors)
        self.assertEqual(result, native.local_step(neighbors))
        self.assertEqual(f.encode_cell(result), tuple(values[x] for x in wanted))
        self.assertEqual(result.s2_data, neighbors[6].s2_rp_data)
        self.assertEqual(result.s3_value, neighbors[7].s2_data)
        self.assertEqual((result.s2_lp_valid, result.s2_rp_valid), (0, 0))

    def test_send_copies_old_data_and_overwrites_only_its_track(self):
        terms, raw = proof.prepare(self.event('interior_overwrite_send_1_7'), proof.clock.regular_intervals()[0])
        rows = [raw(j) for j in f.NEIGHBORHOOD]
        wanted = raw(0, after=True)
        values = instantiate(terms, 'random', random.Random(32))
        neighbors = tuple(f.decode_cell(tuple(values[x] for x in row)) for row in rows)
        result = f.local_step(neighbors)
        self.assertEqual(f.encode_cell(result), tuple(values[x] for x in wanted))
        self.assertEqual((result.s2_lp_data, result.s2_lp_remaining, result.s2_lp_valid),
                         (neighbors[7].s2_data, 7, 1))
        self.assertEqual(result.s2_rp_data, neighbors[6].s2_rp_data)

    def test_wrong_delivery_priority_is_rejected(self):
        original = proof.prepare
        def wrong(event, interval):
            terms, raw = original(event, interval)
            left_payload = raw(1)[f.COL['s2_lp_data']]
            def changed(pos, after=False):
                values = list(raw(pos, after=after))
                if after:
                    for delta in f.OFFSETS:
                        if pos + delta == 0:
                            values[f.COL[f's{delta+2}_data']] = left_payload
                return tuple(values)
            return terms, changed
        with patch.object(proof, 'prepare', side_effect=wrong), self.assertRaises(AssertionError):
            proof.certify_case(self.event('interior_hit_hit'), proof.clock.regular_intervals()[0])

    def test_missing_edge_decrement_is_rejected(self):
        original = proof.prepare
        def wrong(event, interval):
            terms, raw = original(event, interval)
            old_count = raw(-1)[f.COL['s2_rp_remaining']]
            def changed(pos, after=False):
                values = list(raw(pos, after=after))
                if after:
                    for delta in f.OFFSETS:
                        if pos + delta == 0:
                            values[f.COL[f's{delta+2}_rp_remaining']] = old_count
                return tuple(values)
            return terms, changed
        with patch.object(proof, 'prepare', side_effect=wrong), self.assertRaises(AssertionError):
            proof.certify_case(self.event('left_edge_absent_carry'), proof.clock.regular_intervals()[0])


if __name__ == '__main__':
    unittest.main()
