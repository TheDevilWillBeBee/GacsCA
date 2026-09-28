import unittest
from unittest.mock import patch

from gacsca.fixed_rule import small_holder_rule as f, small_holder_native as native
from experiments.fixed_rule import certify_small_holder_packet_metadata as proof
from experiments.fixed_rule.audit_small_holder_position_events import evaluate


class PacketMetadata(unittest.TestCase):
    def event(self, name):
        return next(event for event in proof.cases() if event['name'] == name)

    def test_matching_index_never_delivers_on_any_nonMEM_kind(self):
        event = self.event('nonMEM_interior_nonmemory_nonmemory')
        terms, raw = proof.prepare(event, proof.clock.regular_intervals()[0])
        rows = [raw(j) for j in f.NEIGHBORHOOD]
        wanted = raw(0, after=True)
        assignments = {node[1]: 0 for node in terms.nodes if node[0] == 'variable'}
        assignments.update({terms.nodes[x][1]: lo for x, (lo, hi) in terms.ranges.items()})
        assignments.update(data_0=17, lp_incoming_data=23, rp_incoming_data=31)
        for kind in range(1, 16):
            assignments['transport_kind'] = kind
            values = evaluate(terms, assignments)
            neighbors = tuple(f.decode_cell(tuple(values[x] for x in row)) for row in rows)
            result = f.local_step(neighbors)
            self.assertEqual(result, native.local_step(neighbors))
            self.assertEqual(f.encode_cell(result), tuple(values[x] for x in wanted))
            self.assertEqual((result.s2_data, result.s2_lp_data, result.s2_rp_data), (17, 23, 31))
            self.assertEqual((result.s2_lp_valid, result.s2_rp_valid), (1, 1))

    def test_allowing_MEM_in_the_nonMEM_lemma_is_rejected(self):
        original = proof.prepare
        def weakened(event, interval):
            terms, raw = original(event, interval)
            kind = terms.variable('transport_kind', 4)
            terms.ranges[kind] = (0, 15)
            return terms, raw
        with patch.object(proof, 'prepare', side_effect=weakened), self.assertRaises(AssertionError):
            proof.certify_case(self.event('nonMEM_interior_nonmemory_nonmemory'), proof.clock.regular_intervals()[0])


if __name__ == '__main__':
    unittest.main()
