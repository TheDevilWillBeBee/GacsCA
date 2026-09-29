import unittest
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import repair_b_rule as f,repair_b_projected as r,repair_b_program as p
from gacsca.fixed_rule.repair_b_prefix_world import World as Prefix
from gacsca.fixed_rule.repair_b_composed_world import World
from gacsca.fixed_rule.repair_b_flags import pack_sparse
from gacsca.fixed_rule.wordcode import Program


class ComposedTests(unittest.TestCase):
    def initial(self,age):
        with Prefix.encode((r.Cell(address=100),r.Cell(address=101))) as w:a=w.stored
        g=p.layout();a[:,r.COL['age']]=age;b=a.reshape(2,g.computation_cells+5,len(r.SCHEMA))
        b[0,1:6,r.COL['signal']]=[16,8,4,2,1]
        b[1,g.computation_cells:,r.COL['signal']]=[16,8,4,2,1]
        return a

    def test_actual_nonzero_flags_controller_and_boundary_outputs_match_full_rule(self):
        a=self.initial(96*f.Q-1);g=p.layout();positions=[0,1,3,4,5,6,7,8,63,64,g.info[0],f.Q-8,f.Q-5,f.Q-3,f.Q-1]
        raw={position:3 for position in (*range(15),*range(f.Q-15,f.Q+15))}
        with World(a,flag_runs=pack_sparse(raw,2)) as w:
            for tick in range(12):
                expected={}
                for c in range(2):
                    for address in positions:
                        expected[c,address]=r.local_step(tuple(w.cell(*divmod((c*f.Q+address+j)%(2*f.Q),f.Q)) for j in range(-5,6)))
                with patch.object(Program,'evaluate',side_effect=AssertionError('host evaluator')),patch.object(f,'local_step',side_effect=AssertionError('host transition')):w.run(1)
                stored=w.stored.reshape(2,g.computation_cells+5,len(r.SCHEMA))
                for (c,address),out in expected.items():
                    self.assertEqual(w.cell(c,address),out,(tick,c,address))
                    if address<g.computation_cells or address>=f.Q-5:
                        index=address if address<g.computation_cells else g.computation_cells+address-(f.Q-5)
                        self.assertEqual(r.decode_cell(stored[c,index].tolist()),out)
            self.assertTrue(np.any(w.stored[:,r.COL['f1']]))
            self.assertTrue(np.any(w.stored[:,r.COL['f2']]))

    def test_boundary_termination_and_failed_run_invalidate_wrapper(self):
        with World(self.initial(f.U-1)) as w:
            w.run(1);self.assertEqual(w.flags.info['age'],0)
            with self.assertRaises(RuntimeError):w.run(1)
            with self.assertRaises(ValueError):w.cell(0,0)
        with self.assertRaises(ValueError):w.cell(0,0)


if __name__=='__main__':unittest.main()
