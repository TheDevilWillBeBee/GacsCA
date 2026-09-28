"""Temporal histories are voted by the full physical rule, including priorities."""
from dataclasses import replace
from functools import lru_cache
import random
import unittest
import numpy as np
from gacsca.fixed_rule import small_holder_rule as f, small_holder_core as c
from gacsca.fixed_rule import small_holder_program as p, small_holder_projected as r
from gacsca.fixed_rule import small_holder_initial as initial, small_holder_quotient as q
from gacsca.fixed_rule import small_holder_native as native, small_holder_prefix_world as executor
from gacsca.fixed_rule import holder_rule as old


class ParallelHolderVote(unittest.TestCase):
    def test_full_rule_parallel_vote_at_both_clock_entries(self):
        rng=random.Random(1019);address=p.layout().votes[17]
        for age in (*c.VOTE_AGES,c.VOTE_AGES[0]-1,c.VOTE_AGES[1]+1):
            @lru_cache(None)
            def read(pos):return q.Cell(address=(address+pos)%f.Q,age=age,data=rng.getrandbits(64))
            physical=tuple(r.lift(initial.coherent_cell(read,x)) for x in range(-7,8))
            result=f.local_step(physical);self.assertEqual(result,native.local_step(physical))
            a,b,d=(read(x).data for x in (-1,1,2));want=(a&b)|(a&d)|(b&d)
            self.assertEqual(result.s2_data,want if age in c.VOTE_AGES else read(0).data)
            if age in c.VOTE_AGES:self.assertNotEqual(result.s2_data,old.local_step(physical).s2_data)
            # The raw histories are separate cells and must not be overwritten.
            for x in (-1,1,2):
                neighbors=tuple(r.lift(initial.coherent_cell(read,x+j)) for j in range(-7,8))
                self.assertEqual(f.local_step(neighbors).s2_data,read(x).data)

    def test_vote_overrides_reset_but_not_final_maintenance_clear(self):
        address=p.layout().votes[0];age=c.VOTE_AGES[1]
        def read(x):return q.Cell(address=(address+x)%f.Q,age=age,data=0xF3)
        cells=tuple(r.lift(initial.coherent_cell(read,x)) for x in range(-7,8))
        self.assertEqual(f.local_step(cells).s2_data,0xF3) # stage-five reset would erase it
        changed=list(cells);changed[7]=replace(changed[7],address=address+11,f1=1)
        for i in (8,9,10):changed[i]=replace(changed[i],f1=1)
        out=f.local_step(tuple(changed))
        self.assertEqual(out,native.local_step(tuple(changed)))
        self.assertTrue(out.f1);self.assertNotEqual(out.address,changed[7].address)
        self.assertEqual(out.s2_data,0)

    def test_executor_vote_is_simultaneous_and_matches_physical_rule(self):
        rng=random.Random(1031);g=p.layout()
        with executor.World.encode((r.Cell(),)) as initial_world:state=initial_world.stored
        state[:,q.COL['age']]=c.VOTE_AGES[0]
        for i in range(len(state)):state[i,q.COL['data']]=rng.getrandbits(64)
        before=state.copy()
        with executor.World(state) as world:
            points=(*g.votes[:8],*g.info[:3],0)
            expected={}
            for address in points:
                neighbors=tuple(r.lift(world.cell(0,(address+j)%f.Q)) for j in range(-7,8))
                expected[address]=r.project(native.local_step(neighbors))
            world.run(1,skip_wait=False,skip_scan=False)
            after=world.stored
            a,b,d=(before[np.array(g.votes)+j,q.COL['data']] for j in (-1,1,2))
            np.testing.assert_array_equal(after[np.array(g.votes),q.COL['data']],(a&b)|(a&d)|(b&d))
            for address in points:self.assertEqual(world.cell(0,address),expected[address])

if __name__=='__main__':unittest.main()
