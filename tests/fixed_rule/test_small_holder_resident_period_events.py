import unittest
from gacsca.fixed_rule import small_holder_resident_period as gpu
from gacsca.fixed_rule import small_holder_rule as f,small_holder_core as c,small_holder_program as p
from gacsca.fixed_rule import small_holder_projected as r,small_holder_quotient as q


class ResidentEvents(unittest.TestCase):
    def test_free_flight_opposite_mail_wait_and_overlapping_sources(self):
        parent=(r.Cell(address=17),r.Cell(address=71));age=1
        a=110
        overrides={a:q.Cell(address=a,age=age,head=1,phase=c.WRITE,rd=150,value=87),115:q.Cell(address=115,age=age,lp_target=70,lp_data=33,lp_valid=1),105:q.Cell(address=105,age=age,rp_target=160,rp_data=77,rp_valid=1),f.Q-2:q.Cell(address=f.Q-2,age=age,rp_target=3,rp_data=71,rp_remaining=1,rp_valid=1),p.layout().computation_cells+7:q.Cell(address=p.layout().computation_cells+7,age=age,rp_target=f.Q-3,rp_data=39,rp_valid=1)}
        probes=tuple(range(60,180))+tuple(range(f.Q-6,f.Q+7))
        with gpu.World(parent,age=age,logical=overrides) as fast,gpu.World(parent,age=age,logical=overrides) as slow:
            for ticks in (1,7,17,30,90):
                metrics=fast.run(ticks);slow.run(ticks,skip=False)
                self.assertEqual(fast.physical_cells(probes),slow.physical_cells(probes))
            self.assertGreater(metrics['transport_or_quiet_ticks'],0)

    def test_quiet_boundary_capture_and_nonzero_signal_fallback(self):
        for age in (c.ACTIVE_ENDS[0]-3,c.RESET_AGES[1]-3,c.VOTE_AGES[0]-3,c.CAPTURE_AGE-3):
            overrides={3:q.Cell(address=3,age=age,data=1),f.Q-3:q.Cell(address=f.Q-3,age=age,data=1)}
            with gpu.World((r.Cell(),),age=age,logical=overrides) as fast,gpu.World((r.Cell(),),age=age,logical=overrides) as slow:
                fast.run(7);slow.run(7,skip=False)
                self.assertEqual(fast.physical_cells(tuple(range(8))+tuple(range(f.Q-8,f.Q))),slow.physical_cells(tuple(range(8))+tuple(range(f.Q-8,f.Q))))
        with gpu.World((r.Cell(),),age=1,logical={100:q.Cell(address=100,age=1,signal=1)}) as world:
            metrics=world.run(1);self.assertEqual(metrics['literal_ticks'],1)


if __name__=='__main__':unittest.main()
