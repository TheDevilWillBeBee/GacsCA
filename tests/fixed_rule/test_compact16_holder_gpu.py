import os
import unittest
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import compact16_holder_resident_general as gpu
from gacsca.fixed_rule import compact16_holder_resident_gather as gather
from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_core as c
from gacsca.fixed_rule import compact16_holder_program as p, compact16_holder_projected as r
from gacsca.fixed_rule import compact16_holder_records as q, compact16_holder_native as native
from gacsca.fixed_rule import compact16_holder_flags_cpu as cpu_flags, compact16_holder_flags_gpu as flags
from gacsca.fixed_rule.wordcode import Program


def signal_rows(age, right, left):
    rows = {}
    for col, (a, b) in enumerate(zip(right, left)):
        for address in range(1, 6):
            rows[col*f.Q+address] = q.Cell(address=address, age=age, signal=b << (5-address))
        for address in range(f.Q-5, f.Q):
            rows[col*f.Q+address] = q.Cell(address=address, age=age, signal=a << (f.Q-1-address))
    return rows


def literal_next(world, positions):
    size = world.colonies*f.Q
    return tuple(native.local_step(world.physical_cells(tuple((pos+j)%size for j in f.NEIGHBORHOOD)))
                 for pos in positions)


@unittest.skipUnless(os.environ.get('FIXED_RULE_GPU_TESTS') == '1', 'bounded explicit GPU invocation required')
class CompactGPU(unittest.TestCase):
    def test_complete_Info_and_physical_WRITE_mail_dynamics(self):
        parents = tuple(r.Cell(address=17+i, age=123+i, s2_head=1, s2_pc=91+i,
                               s0_rb=(1 << 63)+i) for i in range(3))
        logical = {col*f.Q+100: q.Cell(address=100, age=1, data=11+col, head=1,
                                      phase=c.WRITE, rd=100, value=91+col) for col in range(3)}
        logical[f.Q-1] = q.Cell(address=f.Q-1, age=1, rp_target=1, rp_data=377, rp_remaining=1, rp_valid=1)
        points = tuple(col*f.Q+a for col in range(3) for a in (0, 1, 2, 98, 100, 102, 104, f.Q-2, f.Q-1))
        with gpu.World(parents, age=1, logical=logical, device_budget=32*1024**2) as world:
            self.assertEqual(world.decode(), parents)
            for _ in range(6):
                expected = literal_next(world, points)
                with patch.object(f, 'local_step', side_effect=AssertionError('host F')), patch.object(r, 'local_step', side_effect=AssertionError('host upper')), patch.object(Program, 'evaluate', side_effect=AssertionError('host evaluator')):
                    world.step()
                self.assertEqual(world.physical_cells(points), expected)
            self.assertEqual(tuple(x.data for x in world.logical_cells((100, f.Q+100, 2*f.Q+100))), (91, 92, 93))
            self.assertEqual(world.logical_cells((f.Q+1,))[0].data, 377)

    def test_all_clock_bulk_boundaries_match_full_raw_F(self):
        g = p.layout()
        rng = np.random.default_rng(719)
        ages = (0, c.RESET_AGES[1], c.RESET_AGES[2], c.VOTE_AGES[0], c.CAPTURE_AGE-1)
        for age in ages:
            points = (0, 1, 3, 5, g.votes[0], g.votes[1], g.info[0], f.Q-5, f.Q-3, f.Q-1)
            addresses = set(points) | {g.votes[i]+d for i in (0, 1) for d in (-1, 1, 2)}
            logical = {a: q.Cell(address=a, age=age, data=int(rng.integers(0, 1 << 63))) for a in addresses}
            # Capture requires equal low bits in each five-holder buffer group.
            if age == c.CAPTURE_AGE-1:
                for a in (*range(1, 6), *range(f.Q-5, f.Q)):
                    logical[a] = q.Cell(address=a, age=age, data=1)
            with gpu.World((r.Cell(),), age=age, logical=logical, device_budget=32*1024**2) as world:
                expected = literal_next(world, points)
                world.step()
                self.assertEqual(world.physical_cells(points), expected, age)

    def test_both_Signals_forcing_and_active_controller(self):
        age = c.WF_START-2
        logical = signal_rows(age, (1, 0, 1), (1, 1, 0))
        logical[100] = q.Cell(address=100, age=age, head=1, phase=c.WRITE, rd=100, value=99)
        with gpu.World((r.Cell(),)*3, age=age, logical=logical, device_budget=32*1024**2) as world:
            for offset in (0, 1, 2, 3, 19, f.Q//2, 2*f.Q+2, 3*f.Q+2):
                world.advance(offset-world.time)
                points = tuple(sorted({(col*f.Q+a)%(3*f.Q) for col in range(3)
                                       for a in (*range(-3, 9), 98, 100, 102)}))
                expected = literal_next(world, points)
                world.step()
                self.assertEqual(world.physical_cells(points), expected)
            self.assertIsNone(world._flags)

    def test_arbitrary_packed_flags_match_CPU_recurrence(self):
        rng = np.random.default_rng(813)
        initial = rng.integers(0, 2**64, size=(3*f.Q//64, 2), dtype=np.uint64)
        runs = [(i+1, int(a), int(b)) for i, (a, b) in enumerate(initial)]
        for age in (c.WF_START-1, c.WF_END-2):
            with flags.World((1, 0, 1), (1, 1, 0), age=age, initial=initial) as a, cpu_flags.World((1, 0, 1), (1, 1, 0), age=age, runs=runs) as b:
                for ticks in (1, 7, 19):
                    a.run(ticks)
                    b.run(ticks, skip_fixed=False)
                    expected = np.empty_like(initial)
                    start = 0
                    for end, one, two in b.runs:
                        expected[start:int(end)] = (one, two)
                        start = int(end)
                    np.testing.assert_array_equal(a.read(), expected)

    def test_protected_target_access_is_atomic(self):
        g = p.layout()
        target = next(g.history(0, w//f.FIELDS-7, w%f.FIELDS) for w in g.gathered_inputs if w//f.FIELDS != 7)
        logical = {target: q.Cell(address=target, age=100, head=1, phase=c.READ_A, ra=target)}
        with gather.World((r.Cell(),), age=100, logical=logical, device_budget=32*1024**2) as world:
            before = world.snapshot()
            with self.assertRaises(RuntimeError):
                world.batch(1, extra_device_budget=32*1024**2)
            for got, want in zip(world.snapshot(), before):
                np.testing.assert_array_equal(got, want)
            self.assertEqual(world.age, 100)


if __name__ == '__main__':
    unittest.main()
