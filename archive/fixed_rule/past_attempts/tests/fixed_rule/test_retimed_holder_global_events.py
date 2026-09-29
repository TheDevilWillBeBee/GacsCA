import unittest
import numpy as np
from gacsca.fixed_rule import retimed_holder_global_events as events
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_core as c
from gacsca.fixed_rule import retimed_holder_literal_cone as cone, retimed_holder_program as p
from tests.fixed_rule.test_retimed_holder_multihead_events import fixture


def ring(heads,age=None):
    rows = [fixture(h) for h in heads]
    raw = np.concatenate(rows)
    words = raw[:,events.RAW_PROC].copy()
    for d in f.OFFSETS:
        raw[:,[f.COL[f's{d+2}_{n}'] for n in events.NAMES]] = np.roll(words,-d,axis=0)
    if age is not None:
        raw[:,f.COL['age']] = age
    return raw


def world(raw):
    return events.World(lambda pos:raw[pos%len(raw)],size=len(raw),time=int(raw[0,f.COL['age']]))


class GlobalEvents(unittest.TestCase):
    def test_second_colony_relative_targets_and_full_controller(self):
        raw = ring([{200:dict(pc=4000000,rb=2**63+17)}, {200:dict(pc=4000001,ra=91),201:dict(pc=4000002,rd=2**60)}])
        w = world(raw)
        w.advance(32)
        for center in (200,f.Q+200):
            left,right = center-14*32,center+14*32+2
            expected = raw[np.arange(left,right)%len(raw)].copy()
            for _ in range(32):
                expected = cone.step(expected)[7:-7].copy()
                left += 7
            np.testing.assert_array_equal(w.cells(np.arange(left,left+len(expected))),expected)
        self.assertEqual(w.heads,(232,f.Q+232,f.Q+233))
        self.assertEqual(w.transport_ticks,32)

    def test_global_boundary_copies_use_neighbor_data(self):
        raw = ring([{},{}])
        words = raw[:,events.RAW_PROC].copy()
        words[f.Q-1,events.COL['data']] = 17
        words[2*f.Q-1,events.COL['data']] = 91
        for d in f.OFFSETS:
            raw[:,[f.COL[f's{d+2}_{n}'] for n in events.NAMES]] = np.roll(words,-d,axis=0)
        w = world(raw)
        self.assertEqual(int(w.cells([f.Q])[0,f.COL['s1_data']]),17)
        self.assertEqual(int(w.cells([0])[0,f.COL['s1_data']]),91)
        raw[f.Q,f.COL['s1_data']] = 91
        with self.assertRaisesRegex(events.DomainError,'coherent global'):
            world(raw)

    def test_reflection_at_each_first_marker_matches_native(self):
        raw = ring([{0:dict(pc=4000000,direction=1)}, {0:dict(phase=c.READ_META,pc=8,ra=200,rb=1,rd=2**60,value=1,direction=1)}])
        w = world(raw)
        expected = cone.step(raw)
        w.advance(1)
        for start in (0,f.Q):
            np.testing.assert_array_equal(w.cells(np.arange(start,start+f.Q)),expected[start:start+f.Q])

    def test_commit_reset_all_sites_and_unused_data(self):
        raw = ring([{200:dict(pc=4000000)}, {201:dict(pc=4000001)}],f.U-1)
        words = raw[:,events.RAW_PROC].copy()
        g = p.layout()
        for col in range(2):
            words[col*f.Q+np.array(g.info)+1,events.COL['data']] = np.arange(f.FIELDS)+1000*col
        for d in f.OFFSETS:
            raw[:,[f.COL[f's{d+2}_{n}'] for n in events.NAMES]] = np.roll(words,-d,axis=0)
        w = world(raw)
        for _ in range(2):
            raw = cone.step(raw)
            w.advance(1)
            for start in (0,f.Q):
                np.testing.assert_array_equal(w.cells(np.arange(start,start+f.Q)),raw[start:start+f.Q])
        self.assertEqual(w.heads,(0,f.Q))
        self.assertEqual(int(w.words[f.Q+30000,events.COL['data']]),0xDEADBEEF01234567)

    def test_omitted_controller_residue_rejected(self):
        raw = ring([{},{}])
        for d in f.OFFSETS:
            raw[f.Q+400-d,f.COL[f's{d+2}_rb']] = 99
        with self.assertRaisesRegex(events.DomainError,'residue'):
            world(raw)


if __name__ == '__main__':
    unittest.main()
