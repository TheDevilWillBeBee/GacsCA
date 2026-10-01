"""Fixed 8Q evaluator late-latch and fivefold Hold delivery."""
import unittest

from gacsca.fixed_rule import spatial_epoch8 as spatial
from gacsca.fixed_rule import spatial_codec8 as codec
from gacsca.fixed_rule import stream28_holder_rule as holder
from gacsca.fixed_rule import stream28_compact_vote8 as combined


class SpatialEightQ(unittest.TestCase):
    def test_late_output_route_uses_marked_value_after_gate_reuse(self):
        self.assertEqual((spatial.Q,spatial.PERIOD,spatial.WIDTH),
                         (8192,65536,2375))
        source=5000
        sink=2863
        launch=40654
        value=0x123456789abcdef0
        marked=spatial.GateSpec(1,spatial.OUTPUT_OPCODE[1])
        other=spatial.GateSpec(1,14)
        route=spatial.Route(1,sink,0,3,0,launch)
        center=spatial.Cell(address=source,age=launch-1,
                            kind=spatial.GATE,active_slot=1,
                            gates=(marked,other,spatial.EMPTY_GATE),
                            routes=(route,)+
                                   (spatial.EMPTY_ROUTE,)*
                                   (spatial.ROUTE_SLOTS-1),
                            source_value=value,result=0xdeadbeef,
                            done=0)
        self.assertEqual(codec.decode_cell(codec.encode_cell(center)),center)
        after=spatial.local_step((spatial.Cell(),center,spatial.Cell()))
        self.assertEqual(after.mail,spatial.Packet(1,sink,0,3,value))
        self.assertEqual(after.collision,0)
        self.assertEqual(after.source_value,value)

    def test_fivefold_combined_hold_commit_after_4q(self):
        sink=2863
        value=0x1020304050607080
        tick=43000
        for offset in holder.OFFSETS:
            physical_site=(sink-offset)%holder.Q
            rows=[]
            for delta in combined.NEIGHBORHOOD:
                site=(physical_site+delta)%holder.Q
                age=combined.RUN_START+tick
                raw=holder.Cell(address=site,age=age)
                spatial_cell=spatial.Cell(address=site,age=tick,
                     kind=spatial.OUTPUT if site==sink else spatial.INERT,
                     mail=(spatial.Packet(1,sink,0,3,value)
                           if site==(sink+1)%holder.Q else spatial.EMPTY_PACKET))
                rows.append(combined.Cell(raw,spatial_cell))
            after=combined.local_step(tuple(rows))
            self.assertEqual(getattr(after.holder,f's{offset+2}_data'),value)
            self.assertEqual(after.evaluator.age,tick+1)
        self.assertEqual(combined.WIDTH,holder.WIDTH+spatial.WIDTH)

    def test_8q_wrap_clears_latch(self):
        marked=spatial.GateSpec(1,spatial.OUTPUT_OPCODE[1])
        center=spatial.Cell(address=17,age=spatial.PERIOD-1,
                            kind=spatial.GATE,gates=(marked,)+
                            (spatial.EMPTY_GATE,)*2,
                            source_value=123,done=1)
        after=spatial.local_step((spatial.Cell(),center,spatial.Cell()))
        self.assertEqual((after.age,after.source_value),(0,0))
        with self.assertRaises(ValueError):spatial.local_step((center,)*2)


if __name__=='__main__':unittest.main()
