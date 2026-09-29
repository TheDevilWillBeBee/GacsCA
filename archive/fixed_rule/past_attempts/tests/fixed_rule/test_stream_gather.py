"""Local dynamics and schedule checks for the experimental stream gather."""
from dataclasses import replace
import unittest

from gacsca.fixed_rule import stream_gather as s
from gacsca.fixed_rule import stream_gather_overlay as overlay
from gacsca.fixed_rule import packed28_holder_program as p
from experiments.fixed_rule.measure_stream_gather import trace_packet
from experiments.fixed_rule.audit_stream_gather_concurrent import check as concurrent_check


class StreamGather(unittest.TestCase):
    def test_fixed_local_alphabet_and_radius(self):
        self.assertEqual((s.Q,s.FRAME,s.PERIOD),(8192,16*8192,64*8192))
        self.assertEqual(s.local_step((s.Cell(),)*3).age,1)
        for width in (0,1,2,4):
            with self.assertRaises(ValueError):s.local_step((s.Cell(),)*width)
        with self.assertRaises(ValueError):s.Packet(1,s.WIRE_LIMIT,0,0,0)
        with self.assertRaises(ValueError):s.Cell(emit_mask=1)

    def test_all_encoded_wires_have_distinct_trajectories_and_fit(self):
        result=s.schedule_certificate();layout=p.layout()
        self.assertEqual((result['required_words'],result['packets_per_colony']),
                         (len(layout.gathered_inputs),3*len(layout.gathered_inputs)))
        self.assertEqual((result['local_words'],result['nonlocal_words']),(97,592))
        self.assertEqual(result['phase_counts'],{'1':293,'-1':396})
        self.assertLess(result['last_delivery'],8*s.Q)
        self.assertEqual(result['maximum_emissions_per_Info_site'],15)
        self.assertEqual(len({(row[0],row[1]) for row in result['rows']}),3*689)

    def test_boundary_crossing_and_target_acceptance_are_local(self):
        number=s.wire(-1,3);payload=0xA5A5F0F012345678
        source=replace(s.Cell(address=s.Q-1),
                       right=s.Packet(1,number,1,0,payload))
        receiver=s.Cell(address=0,accept_wire=number,accept_stage=0)
        out=s.local_step((source,receiver,s.Cell(address=1)))
        self.assertEqual((out.history_valid,out.history_value,out.right.valid,out.collision),
                         (1,payload,0,0))
        other=s.local_step((source,replace(receiver,accept_wire=number+1),s.Cell(address=1)))
        self.assertEqual((other.right.valid,other.right.hops,other.history_valid),(1,0,0))
        left_source=replace(s.Cell(address=0),left=s.Packet(1,s.wire(1,3),1,0,payload))
        left_target=s.Cell(address=s.Q-1,accept_wire=s.wire(1,3),accept_stage=0)
        out=s.local_step((s.Cell(address=s.Q-2),left_target,left_source))
        self.assertEqual((out.history_valid,out.history_value,out.left.valid),(1,payload,0))

    def test_encoded_source_emits_without_host_packet_creation(self):
        layout=p.layout();number=next(w for w in layout.gathered_inputs if w//s.FIELDS-7==-7)
        offset,field=-7,number%s.FIELDS;source=layout.info[field]
        words=[0]*s.FIELDS;words[field]=0xDEADBEEFDEADBEEF
        at=s.initial_cell(source,words)
        launch=s.launch_time(source,offset,field)
        center=replace(at,age=2*s.FRAME+launch-1)
        left=replace(s.initial_cell(source-1,words),age=center.age)
        right=replace(s.initial_cell(source+1,words),age=center.age)
        out=s.local_step((left,center,right))
        self.assertEqual(out.right,s.Packet(1,number,7,2,words[field]))
        self.assertEqual(out.age,center.age+1)

    def test_static_stream_metadata_fits_existing_rom_fields(self):
        rom=overlay.trial_rom();layout=p.layout()
        masks,accepts,sources=s.static_layout()
        self.assertEqual(overlay.footprint()['widened_physical_fields'],0)
        self.assertEqual(len(rom),layout.computation_cells)
        for address,field in sources.items():
            self.assertEqual(int(rom[address,overlay.MASK_SELECTOR]),masks[field])
        for address,want in accepts.items():
            self.assertEqual(overlay.decode_accept(rom[address,overlay.ACCEPT_SELECTOR]),want)
        packet=s.Packet(1,s.wire(-7,3),7,2,0x123456789abcdef0)
        self.assertEqual(overlay.decode_existing_mail(**overlay.encode_existing_mail(packet),
                                                      age=2*s.FRAME+19),packet)
        with self.assertRaises(ValueError):
            overlay.decode_existing_mail(**overlay.encode_existing_mail(packet),
                                         age=3*s.FRAME)

    def test_representative_complete_physical_paths(self):
        layout=p.layout()
        for offset in (0,-1,1,-7,7):
            number=next(w for w in layout.gathered_inputs if w//s.FIELDS-7==offset)
            receipt=trace_packet(number,2)
            self.assertEqual(receipt['offset'],offset)
            self.assertLess(receipt['arrival'],s.FRAME)

    def test_concurrent_stage_boundary_steps(self):
        receipt=concurrent_check((s.FRAME-1,2*s.FRAME-1,3*s.FRAME-1))
        self.assertTrue(receipt['passed'])
        self.assertEqual(receipt['complete_local_site_steps'],3*15*s.Q)
        self.assertEqual([row['delivered_history_sites'] for row in receipt['checked_ticks']],
                         [15*689,2*15*689,3*15*689])


if __name__=='__main__':unittest.main()
