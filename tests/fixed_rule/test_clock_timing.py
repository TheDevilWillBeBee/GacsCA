import unittest
import numpy as np
from gacsca.fixed_rule import clock_rule as f,clock_program as p,clock_projected as r,clock_initial
from gacsca.fixed_rule.clock_world import World


class ClockTimingTests(unittest.TestCase):
    def test_first_gather_halt_and_final_arrival_are_measured_at_exact_ticks(self):
        g=p.layout();timing=g.timing_certificate()['gathers'][0]
        with World.encode((r.Cell(address=100,wf2=1),)) as world:
            world.run(timing['head_stopped']-1)
            self.assertEqual(int(world.cores[:,r.COL['head']].sum()),1)
            world.run(1);self.assertEqual(int(world.cores[:,r.COL['head']].sum()),0)
            world.run(timing['last_arrival']-world.time-1)
            target=g.history(0,-5,f.COL['wf2'])
            self.assertEqual(world.cell(0,target).data,0)
            world.run(1);self.assertEqual(world.cell(0,target).data,1)
            self.assertEqual(world.pending,0)

    def test_evaluation_halt_and_padding_metadata_fallback_use_measured_budget(self):
        g=p.layout();top=clock_initial.terminal_data(age=7);expected=r.step_ring(top);core=r.encode_cores(top)
        raw=f.encode_cell(r.lift(top[0]));core[:,r.COL['age']]=112*f.Q
        for history in range(3):
            for neighbor in range(-5,6):core[[g.history(history,neighbor,k) for k in range(f.FIELDS)],r.COL['data']]=raw
        ticks=g.timing_certificate()['evaluation_ticks']
        with World(core) as world:
            world.run(ticks-1);self.assertEqual(int(world.cores[:,r.COL['head']].sum()),1)
            world.run(1);self.assertEqual(int(world.cores[:,r.COL['head']].sum()),0)
            world.run(16*f.Q-world.time)
            self.assertEqual(world.decode(),expected);self.assertTrue(world.check_boundary())


if __name__=='__main__':unittest.main()
