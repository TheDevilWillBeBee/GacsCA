import unittest
import numpy as np
from gacsca.fixed_rule import clock_rule as f,early_program as p,early_projected as r
from gacsca.fixed_rule.early_world import World


class EarlyConvergenceTests(unittest.TestCase):
    def test_complete_physical_state_converges_after_program_only_corruption(self):
        g=p.layout();top=tuple(r.Cell(address=address,data=f.MASK,age=f.U-1,head=1,phase=7,pc=0xFFFFFFFF,rd=f.MASK,lp_valid=1,lp_data=f.MASK,f1=1,wf2=1)
            for address in (0,g.memory_count+g.description_instruction,g.computation_cells-1,f.Q-1))
        clean=r.encode_cores(top);damaged=clean.copy()
        for base in range(0,len(damaged),g.computation_cells):
            for name in f.STATIC:damaged[base+g.info[f.COL[name]],r.COL['data']]^=np.uint64((1<<dict(f.SCHEMA)[name])-1)
        with World(clean) as reference,World(damaged) as actual:
            reference.run(p.repair_ticks());actual.run(p.repair_ticks())
            np.testing.assert_array_equal(actual.cores,reference.cores)
            self.assertEqual(actual.pending,0);self.assertEqual(reference.pending,0)
            for colony in range(4):
                for address in (g.computation_cells,g.computation_cells+1,f.Q//2,f.Q-1):self.assertEqual(actual.cell(colony,address),reference.cell(colony,address))


if __name__=='__main__':unittest.main()
