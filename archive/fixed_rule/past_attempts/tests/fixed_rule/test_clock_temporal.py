"""Actual local stage-five computation from three initialized history records.

History corruption is an isolated protocol fixture, not a spatial noise law or
an assertion that the preceding gathers were executed in these tests.
"""
from dataclasses import replace
import unittest
import numpy as np
from gacsca.fixed_rule import clock_rule as f,clock_projected as r,clock_program as p
from gacsca.fixed_rule.clock_world import World


class ClockTemporalTests(unittest.TestCase):
    def test_one_bad_history_corrects_two_bad_histories_change_full_output(self):
        g=p.layout();top=[r.Cell(address=100+i,age=1) for i in range(11)]
        top[5]=replace(top[5],data=f.MASK,head=1,phase=f.READ_B,rb=105,rd=106,value=f.MASK,alu=f.NAND)
        top=tuple(top);raw=tuple(f.encode_cell(r.lift(c)) for c in top)
        good=r.step_ring(top);changed=list(top);changed[5]=replace(changed[5],data=f.MASK^1);bad=r.step_ring(tuple(changed))
        self.assertNotEqual(good,bad)
        results=[]
        for histories in ((0,),(1,),(2,),(0,1)):
            core=r.encode_cores(top);core[:,r.COL['age']]=112*f.Q
            for colony in range(11):
                for history in range(3):
                    for neighbor in range(-5,6):
                        source=(colony+neighbor)%11
                        addresses=[colony*g.computation_cells+g.history(history,neighbor,k) for k in range(f.FIELDS)]
                        core[addresses,r.COL['data']]=raw[source]
                        if source==5 and history in histories:
                            core[colony*g.computation_cells+g.history(history,neighbor,f.COL['data']),r.COL['data']]^=np.uint64(1)
            with World(core) as world:
                metrics=world.run(16*f.Q)
                actual=world.decode();self.assertEqual(actual,good if len(histories)==1 else bad,histories)
                self.assertTrue(world.check_boundary());self.assertEqual(world.pending,0)
                self.assertGreater(metrics['scan_ticks_skipped'],40000000)
                results.append(actual)
        self.assertEqual(results[0],results[1]);self.assertEqual(results[1],results[2]);self.assertNotEqual(results[2],results[3])


if __name__=='__main__':unittest.main()
