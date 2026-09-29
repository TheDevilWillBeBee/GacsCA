import unittest
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import repair_b_rule as f,repair_b_projected as r,repair_b_program as p
from gacsca.fixed_rule.repair_b_prefix_world import World as Initial
from gacsca.fixed_rule.repair_b_recurrent_prefix_world import World
from gacsca.fixed_rule.wordcode import Program


class RecurrentPrefixTests(unittest.TestCase):
    def state(self,age=0):
        with Initial.encode((r.Cell(address=100,data=912),r.Cell(address=101))) as initial:a=initial.stored
        g=p.layout();a[:,r.COL['age']]=age;b=a.reshape(2,g.computation_cells+5,len(r.SCHEMA))
        b[0,1:6,r.COL['signal']]=[16,8,4,2,1];b[1,g.computation_cells:,r.COL['signal']]=[16,8,4,2,1]
        return a
    def test_carries_every_stored_word_and_matches_complete_reset_tick(self):
        a=self.state();g=p.layout()
        with World(a) as w:
            np.testing.assert_array_equal(w.stored,a)
            positions=sorted(set([*range(20),*g.info,*g.hold,g.computation_cells-1,g.computation_cells,g.computation_cells+1,f.Q-6,*range(f.Q-5,f.Q)]))
            expected={(c,x):r.local_step(tuple(w.cell(*divmod((c*f.Q+x+j)%(2*f.Q),f.Q)) for j in range(-5,6))) for c in range(2) for x in positions}
            with patch.object(Program,'evaluate',side_effect=AssertionError('host interpreter')),patch.object(f,'local_step',side_effect=AssertionError('host transition')):w.run(1)
            for (c,x),out in expected.items():self.assertEqual(w.cell(c,x),out)
            self.assertEqual(w.cell(0,3).signal,4);self.assertEqual(w.cell(1,f.Q-3).signal,4)
    def test_capture_overwrites_previous_signal_locally(self):
        a=self.state(f.CAPTURE_AGE-1);a[:,r.COL['head']]=0
        for name in f.CONTROL:a[:,r.COL[name]]=0
        g=p.layout();b=a.reshape(2,g.computation_cells+5,len(r.SCHEMA));b[:,1:6,r.COL['data']]=0;b[:,g.computation_cells:,r.COL['data']]=0
        with World(a) as w:
            w.run(1);self.assertFalse(np.any(w.stored[:,r.COL['signal']]))
    def test_incoherent_and_interior_signals_are_rejected(self):
        for index,value in ((3,0),(10,1),(0,31)):
            a=self.state();a[index,r.COL['signal']]=value
            with self.assertRaises(ValueError):World(a)


if __name__=='__main__':unittest.main()
