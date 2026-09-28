import unittest
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import small_holder_rule as f,small_holder_projected as r,small_holder_program as p,small_holder_quotient as q,small_holder_native as native,small_holder_flag_profile as profile
from gacsca.fixed_rule.small_holder_prefix_world import World as Prefix
from gacsca.fixed_rule.small_holder_suffix_world import World
from gacsca.fixed_rule.wordcode import Program
from experiments.fixed_rule.prove_small_holder_flag_profile import prove

class HolderSuffix(unittest.TestCase):
    def initial(self):
        with Prefix.encode((r.Cell(),)) as world:a=world.stored
        a[:,q.COL['age']]=profile.START;a[-5:,q.COL['signal']]=[16,8,4,2,1]
        return a

    def test_all_address_and_front_symbolic_certificate(self):
        result=prove();self.assertTrue(result['passed']);self.assertEqual(len(result['cases']),4)
        self.assertTrue(all(row['descriptor_sha256']==f.self_description().digest() for row in result['cases']))

    def test_full_physical_outputs_at_wave_clock_and_commit_events(self):
        g=p.layout();front_fill=(f.Q-8+2)//3
        checkpoints=sorted(set([profile.START,f.WF_START,f.WF_START+1,f.WF_START+2,f.WF_START+front_fill-2,f.WF_START+front_fill,f.WF_END-1,f.WF_END,f.WF_END+1,f.WF_END+f.Q//2-1,(f.WF_END+f.Q),f.ACTIVE_ENDS[3]-1,f.RESET_AGES[4]-1,f.RESET_AGES[4],f.RESET_AGES[4]+100,f.ACTIVE_ENDS[4]-1,f.U-1]))
        with World(self.initial()) as world:
            for age in checkpoints:
                if age<world.age:continue
                with patch.object(Program,'evaluate',side_effect=AssertionError('host evaluator')),patch.object(f,'local_step',side_effect=AssertionError('host upper transition')):world.run(age-world.age)
                lo,hi=profile.interval(age)
                positions=sorted({a%f.Q for base in (0,lo,hi,g.info[0],g.computation_cells-1) for a in range(base-8,base+9)})
                expected={address:r.project(native.local_step(tuple(r.lift(world.cell(0,(address+j)%f.Q)) for j in range(-7,8)))) for address in positions}
                with patch.object(Program,'evaluate',side_effect=AssertionError('host evaluator')),patch.object(f,'local_step',side_effect=AssertionError('host upper transition')):world.run(1)
                for address,cell in expected.items():self.assertEqual(world.cell(0,address),cell,(age,address))
                logical=world.logical_stored
                for address in (0,g.info[0],f.Q-3):
                    index=address if address<g.computation_cells else g.computation_cells+address-f.Q+5
                    self.assertEqual(q.decode_cell(logical[index].tolist()),world.logical_cell(0,address))
            self.assertEqual(world.age,f.U)
            with self.assertRaises(RuntimeError):world.run(1)
            with self.assertRaises(ValueError):world.cell(0,0)

    def test_rejects_unsupported_signal_mail_and_initial_flags(self):
        for kind in ('left_signal','right_signal','flags','mail','age'):
            a=self.initial()
            if kind=='left_signal':a[1:6,q.COL['signal']]=[16,8,4,2,1]
            if kind=='right_signal':a[-5:,q.COL['signal']]=0
            if kind=='flags':a[3,q.COL['f1']]=1
            if kind=='mail':a[3,q.COL['lp_valid']]=1
            if kind=='age':a[:,q.COL['age']]+=1
            with self.assertRaises(ValueError):World(a)

if __name__=='__main__':unittest.main()
