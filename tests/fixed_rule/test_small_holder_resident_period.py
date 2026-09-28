import unittest
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import small_holder_resident_period as gpu,small_holder_prefix_world as oldprefix
from gacsca.fixed_rule import small_holder_rule as f,small_holder_quotient as q,small_holder_projected as r,small_holder_program as p,small_holder_native as native,small_holder_flag_profile as profile
from experiments.fixed_rule.prove_small_holder_flag_profile import prove


class ResidentPeriod(unittest.TestCase):
    def state(self,age,right=1,colonies=1):
        with oldprefix.World.encode((r.Cell(),)*colonies) as old:a=old.stored
        g=p.layout();rows=g.computation_cells+5;addresses=[*range(g.computation_cells),*range(f.Q-5,f.Q)]
        for part in a.reshape(colonies,rows,len(q.SCHEMA)):
            part[:,q.COL['age']]=age;part[-5:,q.COL['signal']]=np.array([16,8,4,2,1])*right
            if age>=profile.START:part[:,[q.COL[x] for x in ('f1','f2','wf1','wf2')]]=np.array([profile.bits(age,x) for x in addresses])*right
        return a

    def test_existing_full_rule_flag_certificate_still_matches(self):
        result=prove();self.assertTrue(result['passed'])
        self.assertTrue(all(x['descriptor_sha256']==f.self_description().digest() for x in result['cases']))

    def test_stationary_signals_and_flag_wave_match_full_physical_rule(self):
        ages=(profile.START,f.WF_START,f.WF_START+1,f.WF_START+5000,f.WF_END-1,f.WF_END,f.WF_END+1,f.WF_END+f.Q//2-1,f.RESET_AGES[4]-1,f.RESET_AGES[4])
        for right in (0,1):
            for age in ages:
                with gpu.World.from_stored(self.state(age,right)) as world:
                    lo,hi=profile.interval(age)
                    points=tuple(sorted({a%f.Q for center in (0,lo,hi,p.layout().info[0]) for a in range(center-3,center+4)}))
                    expected=tuple(native.local_step(world.physical_cells(tuple((a+j)%f.Q for j in f.NEIGHBORHOOD))) for a in points)
                    world.step();self.assertEqual(world.physical_cells(points),expected,(right,age))
        with gpu.World.from_stored(self.state(f.CAPTURE_AGE,1)) as world:
            before=world.logical_cells(tuple(range(f.Q-5,f.Q)))
            metrics=world.run(profile.START-world.age)
            self.assertGreater(metrics['transport_or_quiet_ticks'],1000000)
            after=world.logical_cells(tuple(range(f.Q-5,f.Q)))
            self.assertEqual([x.signal for x in before],[x.signal for x in after])

    def test_commit_preserves_every_raw_parent_field_and_restarts(self):
        target=r.Cell(address=27,age=117,s2_head=1,s2_phase=3,s2_pc=53,s2_rd=101,s2_value=987654,s0_rp_valid=1,s0_rp_data=4567)
        state=self.state(f.U-1);g=p.layout()
        state[np.array(g.hold),q.COL['data']]=f.encode_cell(r.lift(target))
        with gpu.World.from_stored(state) as world:
            with patch.object(f,'local_step',side_effect=AssertionError('host upper transition')):world.run(1)
            self.assertEqual(world.age,0);self.assertEqual(world.time,1)
            self.assertEqual(world.decode(),(target,))
            self.assertEqual([x.signal for x in world.logical_cells(tuple(range(f.Q-5,f.Q)))],[16,8,4,2,1])
            points=(0,1,2,g.info[0],g.info[-1],f.Q-1)
            expected=tuple(native.local_step(world.physical_cells(tuple((a+j)%f.Q for j in f.NEIGHBORHOOD))) for a in points)
            world.step();self.assertEqual(world.physical_cells(points),expected)
            self.assertEqual(world.decode(),(target,))

    def test_suffix_domain_and_computed_mail_rejections_are_atomic(self):
        for kind in ('left','missing_right_copy','mail','flags','mixed'):
            a=self.state(profile.START,colonies=2 if kind=='mixed' else 1)
            if kind=='left':a[1:6,q.COL['signal']]=[16,8,4,2,1]
            if kind=='missing_right_copy':a[-3,q.COL['signal']]=0
            if kind=='mail':a[100,q.COL['lp_valid']]=1
            if kind=='flags':a[3,q.COL['f1']]=1
            if kind=='mixed':a[-5:,q.COL['signal']]=0
            with self.assertRaises(ValueError):gpu.World.from_stored(a)
        a=self.state(f.WF_START+10)
        a[100,q.COL['head']]=1;a[100,q.COL['phase']]=4;a[100,q.COL['ra']]=100;a[100,q.COL['rb']]=101
        with gpu.World.from_stored(a) as world:
            before=world.physical_cells((99,100,101))
            with self.assertRaises(RuntimeError):world.step()
            self.assertEqual(world.age,f.WF_START+10);self.assertEqual(world.physical_cells((99,100,101)),before)


if __name__=='__main__':unittest.main()
