from dataclasses import replace
import random
import unittest
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import small_holder_resident_period as gpu
from gacsca.fixed_rule import small_holder_rule as f,small_holder_core as c,small_holder_quotient as q
from gacsca.fixed_rule import small_holder_projected as r,small_holder_program as p
from gacsca.fixed_rule import small_holder_native as native,small_holder_prefix_world as reference


class ResidentPrefix(unittest.TestCase):
    def parents(self):return tuple(r.Cell(address=i*31+2,age=i*19+7,s2_head=1,s2_pc=51+i,s2_value=77+i) for i in range(3))

    def test_distinct_parent_data_retains_every_raw_controller_field(self):
        parents=self.parents()
        with gpu.World(parents) as world:
            for col,parent in enumerate(parents):
                values=world.logical_cells(tuple(col*f.Q+a for a in p.layout().info))
                raw=f.decode_cell(tuple(x.data for x in values))
                self.assertEqual(raw,r.lift(parent))
            for _ in range(3):world.step()
            self.assertEqual(world.age,3)
            self.assertLess(world.device_bytes,64*1024**2)

    def test_active_nonperiodic_write_mail_and_successive_ticks(self):
        parents=self.parents();age=1;overrides={}
        for col in range(3):
            pos=col*f.Q+100
            overrides[pos]=q.Cell(address=100,age=age,data=11+col,head=1,phase=c.WRITE,rd=100,value=91+col)
        overrides[f.Q-1]=q.Cell(address=f.Q-1,age=age,rp_target=1,rp_data=377,rp_remaining=1,rp_valid=1)
        with reference.World.encode(parents) as source:state=source.stored
        state[:,q.COL['age']]=age;stride=p.layout().computation_cells+5
        for pos,cell in overrides.items():
            col,a=divmod(pos,f.Q);row=a if a<p.layout().computation_cells else p.layout().computation_cells+a-(f.Q-5)
            state[col*stride+row]=q.encode_cell(cell)
        probes=tuple(col*f.Q+a for col in range(3) for a in (0,1,2,98,99,100,101,102,103,104,f.Q-2,f.Q-1))
        with gpu.World(parents,age=age,logical=overrides) as world,reference.World(state) as cpu:
            for _ in range(6):
                with patch.object(f,'local_step',side_effect=AssertionError('host F')),patch.object(native,'local_step',side_effect=AssertionError('host F')),patch.object(r,'local_step',side_effect=AssertionError('host upper F')):world.step()
                cpu.run(1)
                expected=tuple(r.lift(cpu.cell(*divmod(pos,f.Q))) for pos in probes)
                self.assertEqual(world.physical_cells(probes),expected)
                self.assertEqual(tuple(x.data for x in world.logical_cells((100,f.Q+100,2*f.Q+100))),(91,92,93))

    def test_clock_bulk_boundaries_signals_and_full_physical_rule(self):
        rng=random.Random(910);g=p.layout()
        for age in (0,c.RESET_AGES[1],c.RESET_AGES[2],c.VOTE_AGES[0],c.CAPTURE_AGE-1,c.WF_START-2):
            points=(0,1,2,3,4,5,g.votes[0],g.votes[1],g.info[0],100,f.Q-5,f.Q-4,f.Q-3,f.Q-2,f.Q-1)
            overrides={}
            for a in set(points)|{g.votes[i]+d for i in (0,1) for d in (-1,1,2)}:
                overrides[a]=q.Cell(address=a,age=age,data=rng.getrandbits(64),signal=rng.getrandbits(5))
            with gpu.World((self.parents()[0],),age=age,logical=overrides) as world:
                expected={}
                for a in points:
                    neighborhood=world.physical_cells(tuple((a+j)%f.Q for j in f.NEIGHBORHOOD))
                    expected[a]=native.local_step(neighborhood)
                world.step()
                self.assertEqual(world.physical_cells(points),tuple(expected[x] for x in points),age)
                if age==c.WF_START-2:
                    before=world.physical_cells(points)
                    with self.assertRaises(RuntimeError):world.step()
                    self.assertEqual(world.physical_cells(points),before)

    def test_domain_budget_and_active_capacity_failures_are_explicit(self):
        parent=self.parents()[0]
        with self.assertRaises(RuntimeError):gpu.World((parent,),device_budget=1)
        for cell in (q.Cell(address=2,age=1,f1=1),q.Cell(address=3,age=1),q.Cell(address=2,age=2),q.Cell(address=p.layout().memory_count,age=1,data=1)):
            pos=p.layout().memory_count if cell.address==p.layout().memory_count else 2
            with self.assertRaises(ValueError):gpu.World((parent,),age=1,logical={pos:cell})
        with self.assertRaises(ValueError):gpu.World((parent,),logical={i:q.Cell(address=i) for i in range(65)})
        # One row carries opposing mail, producing two separate live rows.
        # 64 well-separated sources need 128 slots after one transition.
        logical={20+i*20:q.Cell(address=20+i*20,age=1,lp_target=2,lp_data=i+1,lp_remaining=1,lp_valid=1,rp_target=2,rp_data=i+1,rp_remaining=1,rp_valid=1) for i in range(64)}
        with gpu.World((parent,),age=1,logical=logical) as world:
            before=world.logical_cells(tuple(logical))
            with self.assertRaises(RuntimeError):world.step()
            self.assertEqual(world.age,1);self.assertEqual(world.logical_cells(tuple(logical)),before)
        with self.assertRaises(ValueError):world.step()


if __name__=='__main__':unittest.main()
