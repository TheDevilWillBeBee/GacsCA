import random
import unittest
from gacsca.fixed_rule import clock_rule as f,clock_native
from gacsca.fixed_rule.canonical_flag_world import FlagProjection,local_step,NAMES


class CanonicalFlagWorldTests(unittest.TestCase):
    def test_sparse_physical_projection_matches_complete_local_kernel(self):
        rng=random.Random(2803)
        for age in (0,96*f.Q+1,98*f.Q-2,f.U-1):
            states={p:rng.randrange(16) for p in (*range(10),*range(f.Q-10,f.Q),*range(100,110))}
            world=FlagProjection(states,age=age)
            for _ in range(8):
                positions=sorted({(p+j)%f.Q for p in world.states for j in range(-5,6)}|{f.Q//2})
                # Audit all potentially changing cells against the complete rule.
                expected={}
                for position in positions:
                    out=clock_native.local_step(tuple(world.record(position+j) for j in range(-5,6)))
                    bits=sum(getattr(out,name)<<k for k,name in enumerate(NAMES))
                    if bits:expected[position]=bits
                world.step();self.assertEqual(world.states,expected)

    def test_printed_flag2_persistence_and_zero_background_are_retained(self):
        for age in (0,95*f.Q,112*f.Q,f.U-1):
            world=FlagProjection({100:2},age=age).run(32)
            self.assertEqual(world.states,{100:2})
        for address in (0,1,4,f.Q-1):
            for age in (*f.RESET_AGES,96*f.Q-1,98*f.Q-1,f.U-1):self.assertEqual(local_step((0,)*11,address,age),0)

    def test_workspace_flag_seed_produces_a_local_wave_with_canonical_geometry(self):
        world=FlagProjection({p:4 for p in range(f.Q-5,f.Q)},age=96*f.Q+1)
        for _ in range(64):world.step()
        active=[p for p,v in world.states.items() if v&1]
        self.assertGreater(len(active),100)
        self.assertTrue(all(f.Q-5-5*64<=p<f.Q for p in active))
        self.assertEqual(world.record(min(active)).address,min(active))
        self.assertEqual(world.age,96*f.Q+65)
        self.assertEqual(world.at(f.Q//2),0)


if __name__=='__main__':unittest.main()
