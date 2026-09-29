import random
import unittest

from gacsca.fixed_rule import small_holder_rule as f, small_holder_core as c, small_holder_native as native, small_holder_program as p
from gacsca.fixed_rule.wordcode import NAND, MASK
from experiments.fixed_rule import certify_small_holder_clock_mail_factorization as proof
from experiments.fixed_rule.audit_small_holder_position_events import evaluate


def concrete(age, address=100, overrides=None, positions=(0,)):
    terms, raw, _ = proof.prepare(None)
    rows = {pos: tuple(raw(pos+j) for j in f.NEIGHBORHOOD) for pos in positions}
    assignments = {node[1]: 0 for node in terms.nodes if node[0] == 'variable'}
    assignments.update(physical_age=age, base_address=address)
    for site in range(-16, 17):
        assignments[f'meta_{site}_index'] = (address+site) % f.Q
    assignments.update(overrides or {})
    values = evaluate(terms, assignments)
    result = {}
    for pos, neighborhood in rows.items():
        cells = tuple(f.decode_cell(tuple(values[x] for x in row)) for row in neighborhood)
        actual = f.local_step(cells)
        assert actual == native.local_step(cells)
        result[pos] = actual
    return result


class ClockMailFactorization(unittest.TestCase):
    def test_word_mux_identity_and_complement_guard(self):
        terms = proof.ClockTerms(p.base_rom())
        value = terms.variable('value', 64)
        mask = terms.variable('mask', 64)
        other = terms.variable('other', 64)
        joined = terms.op(NAND, terms.op(NAND, mask, value), terms.op(NAND, terms.inv(mask), value))
        wrong = terms.op(NAND, terms.op(NAND, mask, value), terms.op(NAND, other, value))
        self.assertEqual(joined, value)
        self.assertNotEqual(wrong, value)
        rng = random.Random(2026092801)
        for _ in range(40):
            assignment = dict(value=rng.getrandbits(64), mask=rng.getrandbits(64), other=rng.getrandbits(64))
            values = evaluate(terms, assignment)
            self.assertEqual(values[wrong], (assignment['mask'] & assignment['value']) | (assignment['other'] & assignment['value']))

    def test_all_ages_in_every_controller_phase(self):
        for phase in (None, *range(8)):
            result = proof.certify_case(phase)
            self.assertEqual(result['all_clock_ages'], 1 << 32)
            self.assertTrue(result['canonical_geometry_preserved'])

    def test_reset_keeps_unmarked_same_tick_delivery(self):
        incoming = {
            'proc_0_data': 7, 'proc_-1_rp_target': 100, 'proc_-1_rp_data': 55,
            'proc_-1_rp_remaining': 0, 'proc_-1_rp_valid': 1}
        ordinary = concrete(0, overrides=incoming)[0]
        marked = concrete(0, overrides=dict(incoming, meta_0_a=1))[0]
        self.assertEqual((ordinary.s2_data, ordinary.s2_rp_valid), (55, 0))
        self.assertEqual(marked.s2_data, 0)

    def test_rest_retains_invalid_packet_words(self):
        out = concrete(c.ACTIVE_ENDS[0], overrides={
            'proc_0_rp_target': 17, 'proc_0_rp_data': 99, 'proc_0_rp_remaining': 7,
            'proc_0_rp_valid': 0})[0]
        self.assertEqual((out.s2_rp_target, out.s2_rp_data, out.s2_rp_remaining, out.s2_rp_valid), (17, 99, 7, 0))

    def test_computed_Flag1_clears_mail_after_delivery(self):
        out = concrete(1, overrides={
            'physical_1_f1': 1, 'physical_2_f1': 1, 'physical_3_f1': 1,
            'proc_-1_rp_target': 100, 'proc_-1_rp_data': 55, 'proc_-1_rp_valid': 1,
            'proc_1_lp_target': 33, 'proc_1_lp_remaining': 1, 'proc_1_lp_valid': 1})[0]
        self.assertEqual((out.address, out.age, out.f1), (100, 2, 1))
        self.assertEqual(out.s2_data, 55)
        self.assertTrue(all(getattr(out, f's{d+2}_{name}') == 0 for d in f.OFFSETS for name in proof.regular.MAIL))

    def test_flag_gradient_can_break_mail_replica_coherence(self):
        outputs = concrete(1, overrides={
            'physical_1_f1': 1, 'physical_2_f1': 1, 'physical_3_f1': 1,
            'proc_-1_rp_target': 33, 'proc_-1_rp_remaining': 1, 'proc_-1_rp_valid': 1}, positions=tuple(f.OFFSETS))
        copies = [getattr(outputs[pos], f's{2-pos}_rp_valid') for pos in f.OFFSETS]
        self.assertEqual(set(copies), {0, 1})

    def test_vote_and_commit_override_incoming_Data(self):
        voted = concrete(c.VOTE_AGES[0], overrides={
            'meta_0_a': c.VOTE, 'proc_-1_data': 0x0F, 'proc_1_data': 0x33, 'proc_2_data': 0x55,
            'proc_-1_rp_target': 100, 'proc_-1_rp_data': MASK, 'proc_-1_rp_valid': 1})[0]
        self.assertEqual(voted.s2_data, 0x17)
        committed = concrete(f.U-1, overrides={'meta_0_a': c.INFO, 'proc_0_data': 7, 'proc_1_data': 0x123})[0]
        self.assertEqual((committed.s2_data, committed.age), (0x123, 0))

    def test_capture_reads_old_Data_before_delivery(self):
        for old, incoming in ((0, 1), (1, 0)):
            out = concrete(c.CAPTURE_AGE-1, address=3, overrides={
                'proc_0_data': old, 'proc_-1_rp_target': 3, 'proc_-1_rp_data': incoming,
                'proc_-1_rp_valid': 1})[0]
            self.assertEqual((out.s2_data, out.signal), (incoming, old << 2))


if __name__ == '__main__':
    unittest.main()
