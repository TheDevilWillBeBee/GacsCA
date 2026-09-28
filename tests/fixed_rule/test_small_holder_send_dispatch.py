import unittest

from gacsca.fixed_rule import small_holder_core as c, small_holder_program as p, small_holder_rule as f
from experiments.fixed_rule import small_holder_send_dispatch_execution as execution


class SendDispatch(unittest.TestCase):
    def test_selection_retains_all_sixteen_packet_tags(self):
        pcs = execution.selected_pcs()
        self.assertEqual({p.layout().instructions[pc].d for pc in pcs}, set(range(16)))
        for pc in pcs:
            trace, details = execution.frames(pc, 1)
            birth = next(frame for frame in trace if frame['time'] == details['birth_tick'])
            self.assertTrue(all(len(row) == 1 for row in birth['packets']))
            self.assertEqual(trace[-1]['time'], details['birth_tick'] + details['dispatch_ticks'] + 1)
            self.assertTrue(all(a['time'] < b['time'] for a, b in zip(trace, trace[1:])))

    def test_delivered_and_live_packet_states_are_distinguished(self):
        pcs = execution.selected_pcs(True)
        for tag in (1, 15):
            pc = next(pc for pc in pcs if p.layout().instructions[pc].d == tag)
            op = p.layout().instructions[pc]
            trace, details = execution.frames(pc, c.VOTE_AGES[0]+1)
            final = trace[-1]
            if tag == 1:
                self.assertTrue(all(not row for row in final['packets']))
                self.assertEqual([row[op.b] for row in final['data']], [row[op.a] for row in trace[0]['data']])
            else:
                self.assertTrue(all(len(row) == 1 for row in final['packets']))
                dt = final['time'] - details['birth_tick']
                self.assertLess(dt, op.a+1)
                for row in final['packets']:
                    self.assertEqual(next(iter(row)), (op.a-dt)%f.Q)
                    self.assertEqual(next(iter(row.values()))['lp_remaining'], 7)


if __name__ == '__main__':
    unittest.main()
