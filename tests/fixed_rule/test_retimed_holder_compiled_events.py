import unittest
import numpy as np

from gacsca.fixed_rule import retimed_holder_compiled_events as compiled
from gacsca.fixed_rule import retimed_holder_global_events as original
from gacsca.fixed_rule import retimed_holder_literal_cone as cone
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_core as c
from tests.fixed_rule.test_retimed_holder_global_events import ring


def world(raw, implementation=compiled):
    return implementation.World(lambda pos:raw[pos%len(raw)],size=len(raw),time=int(raw[0,f.COL['age']]))


class CompiledEvents(unittest.TestCase):
    def test_collision_and_reflection_match_complete_native_outputs(self):
        raw = ring([{200:dict(pc=4000000,rb=2**63+17),202:dict(pc=4000001,direction=1)},
                    {0:dict(phase=c.READ_META,pc=8,ra=200,rb=1,rd=2**60,value=1,direction=1)}])
        w = world(raw)
        for _ in range(4):
            raw = cone.step(raw)
            w.advance(1)
            for start in (0,f.Q):
                np.testing.assert_array_equal(w.cells(np.arange(start,start+f.Q)),raw[start:start+f.Q])

    def test_transport_and_events_match_previous_trace_and_all_words(self):
        raw = ring([{0:dict(pc=4000000,direction=1)},
                    {200:dict(pc=4000001,ra=91),201:dict(pc=4000002,rd=2**60)}])
        actual,expected = world(raw),world(raw,original)
        for ticks in (1,32,1000):
            self.assertEqual(actual.advance(ticks),expected.advance(ticks))
            np.testing.assert_array_equal(actual.words,expected.words)
            np.testing.assert_array_equal(actual.signals,expected.signals)
            self.assertEqual(actual.trace,expected.trace)

    def test_complete_commit_reset_keeps_nonmem_data(self):
        raw = ring([{200:dict(pc=4000000)},{201:dict(pc=4000001)}],f.U-1)
        w = world(raw)
        for _ in range(2):
            raw = cone.step(raw);w.advance(1)
            for start in (0,f.Q):
                np.testing.assert_array_equal(w.cells(np.arange(start,start+f.Q)),raw[start:start+f.Q])
        self.assertEqual(w.heads,(0,f.Q))
        self.assertEqual(int(w.words[f.Q+30000,original.COL['data']]),0xDEADBEEF01234567)

    def test_omitted_controller_and_wrong_neighbor_copy_rejected(self):
        raw = ring([{},{}])
        raw[f.Q,f.COL['s1_data']] ^= np.uint64(1)
        with self.assertRaisesRegex(original.DomainError,'coherent global'):
            world(raw)
        raw = ring([{},{}])
        for d in f.OFFSETS:
            raw[f.Q+400-d,f.COL[f's{d+2}_rb']] = 99
        with self.assertRaisesRegex(original.DomainError,'residue'):
            world(raw)

    def test_transactional_literal_budget_retains_valid_state(self):
        raw = ring([{0:dict(pc=4000000,direction=1)},{}])
        actual,expected = world(raw),world(raw,original)
        with self.assertRaises(original.DomainError):
            actual.advance(100000,event_budget=1)
        self.assertGreater(actual.time,int(raw[0,f.COL['age']]))
        expected.advance(actual.time-int(raw[0,f.COL['age']]))
        np.testing.assert_array_equal(actual.words,expected.words)
        self.assertEqual(actual.heads,expected.heads)


if __name__ == '__main__':
    unittest.main()
