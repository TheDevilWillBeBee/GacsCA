import unittest
import numpy as np
from gacsca.fixed_rule import delivery_rule as f,delivery_program as p,delivery_projected as r
from gacsca.fixed_rule.delivery_prefix_world import World


class DeliveryPacketTimingTests(unittest.TestCase):
    def test_actual_final_packet_arrives_at_the_predicted_tick(self):
        g=p.layout();stop,rows=g.schedule(*g.delivery_range)
        gate=g.stage_ranges[4][1]-1
        gate_tick=rows[gate-g.delivery_range[0]][0]
        cert=g.timing_certificate();delta=cert['stage3_last_delivery']-(gate_tick-1)
        with World.encode((r.Cell(address=100),)) as clean:stored=clean.stored
        stored[:,r.COL['age']]=f.VOTE_AGES[0]+gate_tick-1
        stored[g.hold[f.COL['f1']],r.COL['data']]=1
        stored[g.hold[f.COL['f2']],r.COL['data']]=1
        location=g.memory_count+gate
        stored[location,r.COL['head']]=1;stored[location,r.COL['pc']]=gate
        with World(stored) as world:
            world.run(delta-1)
            self.assertEqual(world.cell(0,f.Q-1).data,0)
            self.assertEqual(world.cell(0,f.Q-2).rp_valid,1)
            world.run(1)
            self.assertEqual(world.pending,0)
            for address in (*range(1,6),*range(f.Q-5,f.Q)):self.assertEqual(world.cell(0,address).data,1)
            self.assertFalse(np.any(world.cores[:,r.COL['head']]))
            self.assertLess(world.cell(0,0).age,f.CAPTURE_AGE)

    def test_each_gather_has_no_overlapping_same_track_packet_worldlines(self):
        g=p.layout()
        for start,end in g.stage_ranges[:3]:
            stopped,rows=g.schedule(start,end);packets=[]
            for op,times in zip(g.instructions[start:end],rows):
                if op.kind!=f.SEND:continue
                direction=op.d&1;hops=op.d>>1
                distance=hops*f.Q+(op.a-op.b if direction else op.b-op.a)
                packets.append((direction,times[-1],op.a,distance))
            for k,(direction,t,source,distance) in enumerate(packets):
                line=(source+t if direction else source-t)%f.Q
                for d,u,s,other_distance in packets[k+1:]:
                    if u<t+distance and d==direction:self.assertNotEqual(line,(s+u if d else s-u)%f.Q)


if __name__=='__main__':unittest.main()
