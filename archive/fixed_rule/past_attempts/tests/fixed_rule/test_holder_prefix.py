from dataclasses import replace
from functools import lru_cache
import random
import unittest
import numpy as np
from gacsca.fixed_rule import holder_rule as f,holder_core as c,holder_projected as r,holder_program as p,holder_initial as initial,holder_native as native,holder_quotient as q,holder_prefix_world as executor

class HolderPrefix(unittest.TestCase):
    def test_complete_physical_conjugacy_on_prefix_domain(self):
        rng=random.Random(291)
        for age in (0,1,16*f.Q,32*f.Q,72*f.Q,c.CAPTURE_AGE-1,c.CAPTURE_AGE,96*f.Q-2):
            for base in (0,p.layout().info[0],p.layout().computation_cells-1,f.Q-3):
                @lru_cache(None)
                def read(pos):
                    return q.Cell(**{n:rng.getrandbits(w) for n,w in q.SCHEMA if n not in ('address','age','f1','f2','wf1','wf2')},address=(base+pos)%f.Q,age=age)
                physical=tuple(r.lift(initial.coherent_cell(read,pos)) for pos in range(-7,8))
                new={}
                for pos in range(-2,3):
                    inputs=np.array([c.encode_cell(q.lift(read(pos+j))) for j in range(-5,6)],dtype=np.uint64);output=np.empty(c.FIELDS,dtype=np.uint64)
                    executor.library().ww_prefix_local(executor.pointer(inputs),executor.pointer(output))
                    new[pos]=q.project(c.decode_cell(output.tolist()))
                expected=initial.coherent_cell(new.__getitem__,0)
                self.assertEqual(r.project(native.local_step(physical)),expected,(age,base))

    def state(self,age=1):
        with executor.World.encode((r.Cell(),r.Cell())) as world:state=world.stored
        state[:,q.COL['age']]=age
        return state

    def test_ballistic_head_packet_crossings_and_deliveries(self):
        g=p.layout();rows=g.computation_cells+5
        for age in (1,72*f.Q-2,16*f.Q-3):
            state=self.state(age)
            # Simultaneous same-track packets, opposite-track crossings, a head
            # whose source overlaps another packet's destination, and a WRITE.
            records={100:dict(head=1,phase=c.WRITE,rd=140,value=0x123),120:dict(lp_target=70,lp_data=17,lp_remaining=0,lp_valid=1),105:dict(rp_target=170,rp_data=19,rp_remaining=0,rp_valid=1),115:dict(rp_target=190,rp_data=23,rp_remaining=0,rp_valid=1),rows-2:dict(lp_target=f.Q-5,lp_data=29,lp_remaining=0,lp_valid=1),rows:dict(lp_target=10,lp_data=31,lp_remaining=1,lp_valid=1),g.computation_cells-2:dict(rp_target=300,rp_data=37,rp_remaining=1,rp_valid=1)}
            for pos,fields in records.items():
                for name,value in fields.items():state[pos,q.COL[name]]=value
            with executor.World(state) as fast,executor.World(state) as slow:
                for ticks in (1,2,7,40,60):
                    fast.run(ticks);slow.run(ticks,skip_wait=False,skip_scan=False)
                    np.testing.assert_array_equal(fast.stored,slow.stored)
                    self.assertEqual(fast.pending,slow.pending)
                    for address in (0,100,140,170,f.Q-5,f.Q-1,g.computation_cells,g.computation_cells+20,g.computation_cells+fast.time-2):
                        self.assertEqual(fast.cell(0,address),slow.cell(0,address))

    def test_literal_executor_step_matches_complete_physical_rule(self):
        g=p.layout();state=self.state(c.CAPTURE_AGE-1)
        for address in (2,3,4,100,g.computation_cells-1):state[address,q.COL['data']]=1
        state[100,q.COL['head']]=1;state[100,q.COL['phase']]=c.TRANSMIT;state[100,q.COL['ra']]=100;state[100,q.COL['rb']]=105
        with executor.World(state) as world:
            for _ in range(3):
                points=(0,1,2,3,4,5,99,100,101,102,103,104,105,g.computation_cells-1,g.computation_cells,f.Q-3,f.Q-1)
                expected={}
                for address in points:
                    cells=[]
                    for j in range(-7,8):
                        colony,a=divmod(address+j,f.Q);cells.append(r.lift(world.cell(colony%world.colonies,a)))
                    expected[address]=r.project(native.local_step(tuple(cells)))
                world.run(1)
                for address in points:self.assertEqual(world.cell(0,address),expected[address],(world.time,address))

    def test_long_gap_flight_and_exact_arrival(self):
        g=p.layout();state=self.state();start=g.computation_cells-1;target=f.Q-3
        for name,value in dict(rp_valid=1,rp_target=target,rp_data=93).items():state[start,q.COL[name]]=value
        with executor.World(state) as world:
            world.run(100)
            self.assertEqual(world.cell(0,start+100).s2_rp_data,93)
            for d in f.OFFSETS:self.assertEqual(getattr(world.cell(0,start+100-d),f's{d+2}_rp_data'),93)
            world.run(target-start-101)
            cells=[]
            for j in range(-7,8):
                colony,a=divmod(target+j,f.Q);cells.append(r.lift(world.cell(colony,a)))
            expected=r.project(native.local_step(tuple(cells)))
            world.run(1)
            self.assertEqual(world.cell(0,target),expected)
            self.assertEqual(world.cell(0,target).s2_data,93)
            self.assertEqual(world.pending,0)

    def test_executor_rejects_domain_violations(self):
        for field in ('f1','f2','wf1','wf2','signal','address'):
            state=self.state();state[3,q.COL[field]]^=1
            with self.assertRaises(ValueError):executor.World(state)
        with executor.World.encode((r.Cell(),)) as world:
            with self.assertRaises(RuntimeError):world.run(96*f.Q)

if __name__=='__main__':unittest.main()
