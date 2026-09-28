from copy import deepcopy
import json
from pathlib import Path
import unittest
from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_core as c
from gacsca.fixed_rule import compact16_holder_program as p, compact16_holder_projected as r
from gacsca.fixed_rule import compact16_holder_initial as initial, compact16_holder_native as native
from experiments.fixed_rule import certify_compact16_holder_composition as composition
from experiments.fixed_rule import certify_compact16_holder_meta_paths as meta
from experiments.fixed_rule import certify_compact16_holder_instruction_paths as ordinary


class Compact16Composition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.paths = json.loads(Path('figs/fixed_rule/compact16_holder_paths_v1.json').read_text())
        cls.mail = json.loads(Path('figs/fixed_rule/compact16_holder_mail_v1.json').read_text())

    def loaded(self):
        return {'ordinary': {'rows': self.paths['ordinary_rows']},
                'meta': {'paths': self.paths['metadata_paths']},
                'dispatch': {'rows': self.paths['dispatch_rows']}}

    def test_current_rule_receipts_cover_every_phase_and_extra_leaf(self):
        for doc in (self.paths, self.mail):
            self.assertTrue(doc['passed'])
            self.assertEqual(doc['descriptor_sha256'], f.self_description().digest())
        self.assertEqual(len(self.paths['additional_leaves']), 84)
        self.assertEqual(self.mail['case_count'], 63)
        self.assertEqual(len(self.mail['packet_flight_cases']), 8)
        checked = composition.schedule(self.loaded())
        self.assertEqual(checked['trace_sha256'], self.paths['packet_schedule']['trace_sha256'])
        self.assertEqual(checked['actual_SEND_sites_checked'], 1786)

    def test_tail_lookup_uses_new_Q_for_constants_and_intervals(self):
        terms = meta.Words(p.base_rom())
        for address in (len(p.base_rom()), f.Q-6, f.Q-5, f.Q-1):
            for selector in range(7):
                self.assertEqual(terms.value(terms.lookup(terms.const(address), selector)), c.fallback(address, selector))
        tail = terms.bounded('tail', (f.Q-1).bit_length(), f.Q-5, f.Q-1)
        self.assertEqual(terms.value(terms.lookup(tail, 0)), c.MEM)
        self.assertEqual(terms.lookup(tail, 1), tail)

    def test_wrong_physical_duration_and_dispatch_are_rejected(self):
        loaded = deepcopy(self.loaded())
        loaded['ordinary']['rows'][0][3] += 1
        with self.assertRaises(AssertionError):
            composition.schedule(loaded)
        loaded = deepcopy(self.loaded())
        loaded['dispatch']['rows'][0][4] += 1
        with self.assertRaises(AssertionError):
            composition.schedule(loaded)

    def test_nonMEM_flight_requires_the_kind_hypothesis(self):
        interval = composition.clock.regular_intervals()[0]
        terms, raw = ordinary.leaf_prepare(('nonmem', 'flight_1'), interval)
        self.assertTrue(terms.disequalities)
        # Recompute without the premise. A possible matching MEM read now
        # changes the controller, so an unconditional flight identity is false.
        terms.disequalities.clear()
        actual = terms.expression(f.self_description(), tuple(w for j in f.NEIGHBORHOOD for w in raw(j)))
        self.assertNotEqual(actual, raw(0, after=True))

    def test_literal_packets_cross_both_colony_edges(self):
        payload = 0x123456789ABCDEF0
        cases = ((False, f.Q-2, 2, 1, f.Q+2),
                 (True, 1, f.Q-3, 1, -3),
                 (False, 6, 10, 0, 10))
        ticks = 8
        for leftward, source, target, hops, destination in cases:
            channel, direction = ('lp', -1) if leftward else ('rp', 1)
            def logical(at):
                values = dict(r.record(at % f.Q), address=at % f.Q, age=c.VOTE_AGES[0]+10)
                if at == source:
                    values.update({channel+'_valid': 1, channel+'_target': target,
                                   channel+'_remaining': hops, channel+'_data': payload})
                return c.Cell(**values)
            margin = 7*ticks+8
            start = source-margin
            cells = tuple(r.lift(initial.coherent_cell(logical, at))
                          for at in range(start, source+margin+1))
            for tick in range(1, ticks+1):
                before, before_start = cells, start
                # Boundary wrap of this temporary array is outside the retained
                # radius-seven cone. Crop seven outputs on each side per tick.
                cells = native.step_ring(before)[7:-7]
                start += 7
                current = source+direction*tick
                for position in {source, destination, current}:
                    index = position-before_start
                    wanted = f.local_step(before[index-7:index+8])
                    self.assertEqual(cells[position-start], wanted)
                self.assertEqual(cells[destination-start].s2_data, payload if tick >= 4 else 0)
                if tick < 4:
                    packet = cells[current-start]
                    self.assertEqual(getattr(packet, 's2_'+channel+'_valid'), 1)
                    self.assertEqual(getattr(packet, 's2_'+channel+'_data'), payload)
                else:
                    self.assertTrue(all(getattr(cell, 's2_'+channel+'_valid') == 0 for cell in cells))

    def test_literal_receive_and_WRITE_priority(self):
        at = 100
        for writing, expected in ((False, 222), (True, 333)):
            def logical(pos):
                values = dict(r.record(pos % f.Q), address=pos % f.Q, age=c.VOTE_AGES[0]+10, data=444)
                if pos == at-1:
                    values.update(rp_valid=1, rp_target=at, rp_data=222)
                if pos == at+1:
                    values.update(lp_valid=1, lp_target=at, lp_data=111)
                if pos == at and writing:
                    values.update(head=1, phase=c.WRITE, rd=at, value=333)
                return c.Cell(**values)
            cells = tuple(r.lift(initial.coherent_cell(logical, at+j)) for j in f.NEIGHBORHOOD)
            actual = native.local_step(cells)
            self.assertEqual(actual, f.local_step(cells))
            self.assertEqual(actual.s2_data, expected)


if __name__ == '__main__':
    unittest.main()
