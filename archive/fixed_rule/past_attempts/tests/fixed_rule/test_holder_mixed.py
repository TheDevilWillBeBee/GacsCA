import unittest
import numpy as np
from gacsca.fixed_rule import holder_rule as f,holder_projected as r,holder_program as p,holder_quotient as q,holder_native as native,holder_flag_profile as profile
from gacsca.fixed_rule.holder_prefix_world import World as Prefix
from gacsca.fixed_rule.holder_suffix_mixed import World
from gacsca.fixed_rule.holder_omp_suffix_mixed import World as Parallel
from gacsca.fixed_rule.holder_omp_prefix_world import World as ParallelPrefix
from experiments.fixed_rule.prove_holder_mixed_profile import prove

class MixedSuffix(unittest.TestCase):
    def state(self):
        with Prefix.encode(tuple(r.Cell(address=100+i) for i in range(4))) as world:a=world.stored
        a[:,q.COL['age']]=profile.START;rows=a.reshape(4,p.layout().computation_cells+5,len(q.SCHEMA))
        for index in (1,3):rows[index,-5:,q.COL['signal']]=[16,8,4,2,1]
        return a
    def test_mixed_signals_exact_symbolic_front_proof(self):
        proof=prove();self.assertTrue(proof['passed']);self.assertTrue(all(case['independent_colony_signals']==3 for case in proof['cases']))
    def test_mixed_suffix_and_parallel_kernel_match_full_native_at_boundaries(self):
        state=self.state();g=p.layout()
        with World(state) as serial,Parallel(state) as parallel:
            for age in (profile.START,96*f.Q+1,96*f.Q+12,98*f.Q-1,98*f.Q+17,99*f.Q,112*f.Q,f.U-1):
                serial.run(age-serial.age);parallel.run(age-parallel.age)
                np.testing.assert_array_equal(serial.logical_stored,parallel.logical_stored)
                lo,hi=profile.interval(age);positions=sorted({a%f.Q for base in (0,lo,hi,g.info[0]) for a in range(base-7,base+8)})
                expected={}
                for colony in range(4):
                    for address in positions:
                        raw=tuple(r.lift(serial.cell(*divmod((colony*f.Q+address+j)%(4*f.Q),f.Q))) for j in range(-7,8))
                        expected[colony,address]=r.project(native.local_step(raw))
                serial.run(1);parallel.run(1)
                for key,value in expected.items():self.assertEqual(serial.cell(*key),value);self.assertEqual(parallel.cell(*key),value)
    def test_parallel_prefix_state_and_counters_match_serial(self):
        from gacsca.fixed_rule.holder_recurrent_prefix_world import World as Serial
        with Serial.encode(tuple(r.Cell(address=i) for i in range(7))) as serial:state=serial.stored
        with Serial(state) as serial,ParallelPrefix(state) as parallel:
            for ticks in (1,100,1000000):
                self.assertEqual(serial.run(ticks),parallel.run(ticks));np.testing.assert_array_equal(serial.stored,parallel.stored)

if __name__=='__main__':unittest.main()
