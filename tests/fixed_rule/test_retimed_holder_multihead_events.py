import unittest
import numpy as np
from gacsca.fixed_rule import retimed_holder_multihead_events as events
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_core as c
from gacsca.fixed_rule import retimed_holder_program as p, retimed_holder_literal_cone as cone


def fixture(heads):
    g = p.layout()
    image = cone.BankImage(np.zeros((1, g.memory_count+5), dtype=np.uint64), np.zeros((1, 2), dtype=np.uint64))
    raw = image.cells(np.arange(f.Q))
    raw[:, f.COL['age']] = f.RESET_AGES[4]+10000000
    logical = np.zeros((f.Q, len(events.NAMES)), dtype=np.uint64)
    logical[30000, events.COL['data']] = 0xDEADBEEF01234567
    for pos, values in heads.items():
        logical[pos, events.COL['head']] = 1
        for name, value in values.items():
            logical[pos, events.COL[name]] = value
    for d in f.OFFSETS:
        for index,name in enumerate(events.NAMES):
            raw[:, f.COL[f's{d+2}_{name}']] = np.roll(logical[:, index], -d)
    return raw


def literal_window(raw, lo, hi, ticks):
    left = lo-14*ticks
    current = raw[np.arange(left, hi+14*ticks+1) % f.Q].copy()
    for _ in range(ticks):
        current = cone.step(current)[7:-7].copy()
        left += 7
    return left, current


class MultiheadEvents(unittest.TestCase):
    def compare(self, heads, ticks):
        raw = fixture(heads)
        world = events.World(raw)
        left, expected = literal_window(raw, min(heads), max(heads), ticks)
        world.advance(ticks)
        np.testing.assert_array_equal(world.raw()[np.arange(left, left+len(expected)) % f.Q], expected)
        self.assertEqual(int(world.words[30000, events.COL['data']]), 0xDEADBEEF01234567)
        return world

    def test_adjacent_parallel_heads_transport_all_registers(self):
        common = dict(phase=c.FETCH, pc=4000000, ra=123, rb=2**63+71, rd=2**60, value=73, alu=c.NAND)
        w = self.compare({200:common, 201:dict(common, pc=4000001, value=911)}, 64)
        self.assertEqual(w.transport_ticks, 64)
        self.assertEqual(w.literal_ticks, 0)
        self.assertEqual(w.heads, (264, 265))

    def test_opposed_heads_force_literal_interaction(self):
        heads = {200:dict(pc=4000000), 210:dict(pc=4000001, direction=1)}
        w = self.compare(heads, 12)
        self.assertGreater(w.literal_ticks, 0)
        self.assertLess(len(w.heads), 2)

    def test_left_metadata_fallback_and_head_interaction(self):
        self.compare({0:dict(phase=c.READ_META, pc=8, ra=200, rb=1, rd=2**60+7, value=1, direction=1), 20:dict(pc=4000000, direction=1)}, 12)

    def test_raw_controller_residue_is_not_dropped(self):
        raw = fixture({200:dict(pc=4000000)})
        for d in f.OFFSETS:
            raw[400-d, f.COL[f's{d+2}_rb']] = 99
        with self.assertRaisesRegex(events.DomainError, 'residue'):
            events.World(raw)

    def test_head_outside_executor_domain_rejected(self):
        with self.assertRaisesRegex(events.DomainError, 'inside the ROM'):
            events.World(fixture({30000:dict(pc=4000000)}))

    def test_incoherent_backup_is_not_projected_away(self):
        raw = fixture({200:dict(pc=4000000)})
        raw[100, f.COL['s0_data']] = 1
        with self.assertRaisesRegex(events.DomainError, 'coherent'):
            events.World(raw)


if __name__ == '__main__':
    unittest.main()
