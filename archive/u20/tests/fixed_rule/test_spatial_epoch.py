"""Actual local gate reuse and nine-layer encoded route regression."""
from dataclasses import replace
import unittest

from gacsca.fixed_rule import spatial_epoch as s
from gacsca.fixed_rule.wordcode_and import AND,ADD
from experiments.fixed_rule.measure_spatial_epoch import check


class SpatialEpoch(unittest.TestCase):
    def test_one_fixed_rule_and_alphabet(self):
        self.assertEqual((s.Q,s.PERIOD,s.WIDTH,s.NEIGHBORHOOD),
                         (8192,32768,2334,(-1,0,1)))
        transition=s.local_step
        with self.assertRaises(ValueError):transition((s.Cell(),)*2)
        with self.assertRaises(ValueError):transition((s.Cell(),)*4)
        with self.assertRaises(ValueError):s.Cell(gates=(s.EMPTY_GATE,))
        self.assertIs(s.local_step,transition)

    def test_switch_reuses_single_dynamic_operand_pair(self):
        first=s.GateSpec(1,ADD,0,10,3,5,3)
        second=s.GateSpec(1,AND,0,11,0xf,0xa,3)
        old=s.Cell(address=5,age=8,kind=s.GATE,
                   gates=(first,second,s.EMPTY_GATE),
                   switch_ages=(10,0),arg0=3,arg1=5,ready=3,
                   result=8,done=1,routes=(
                       s.Route(1,7,0,0,0,9),
                       s.Route(1,8,1,0,1,11))+ (s.EMPTY_ROUTE,)*(s.ROUTE_SLOTS-2))
        emitted_old=s.local_step((s.Cell(),old,s.Cell()))
        self.assertEqual((emitted_old.active_slot,emitted_old.mail.value),(0,8))
        switched=s.local_step((s.Cell(age=9),emitted_old,s.Cell(age=9)))
        self.assertEqual((switched.active_slot,switched.arg0,switched.arg1,
                          switched.result,switched.done),(1,0xf,0xa,0xa,1))
        emitted_new=s.local_step((s.Cell(age=10),switched,s.Cell(age=10)))
        self.assertEqual((emitted_new.mail.target,emitted_new.mail.value),(8,0xa))
        self.assertEqual(s.local_step((s.Cell(),replace(old,age=9),s.Cell())).active_slot,1)

    def test_new_gate_can_receive_at_switch_tick(self):
        old=s.GateSpec(1,ADD,0,100,1,2,3)
        new=s.GateSpec(1,ADD,0,101,7,0,1)
        target=s.Cell(address=15,age=9,kind=s.GATE,
                      gates=(old,new,s.EMPTY_GATE),switch_ages=(10,0),
                      arg0=1,arg1=2,ready=3,result=3,done=1)
        incoming=s.Packet(1,15,1,1,5)
        first=s.local_step((s.Cell(mail=incoming),target,s.Cell()))
        self.assertEqual((first.active_slot,first.arg0,first.arg1,
                          first.ready,first.done),(1,7,5,3,0))
        second=s.local_step((s.Cell(),first,s.Cell()))
        self.assertEqual((second.done,second.result),(1,12))

    def test_work_window_wrap_returns_to_first_gate(self):
        first=s.GateSpec(1,ADD,0,100,7,0,1)
        later=s.GateSpec(1,ADD,0,101,3,4,3)
        old=s.Cell(address=15,age=s.PERIOD-1,kind=s.GATE,active_slot=1,
                   gates=(first,later,s.EMPTY_GATE),switch_ages=(10,0),
                   arg0=3,arg1=4,ready=3,result=7,done=1)
        wrapped=s.local_step((s.Cell(),old,s.Cell()))
        self.assertEqual((wrapped.age,wrapped.active_slot,wrapped.arg0,
                          wrapped.arg1,wrapped.ready,wrapped.result,
                          wrapped.done),(0,0,7,0,1,0,0))

    def test_wrap_does_not_compute_from_previous_period_ready_bits(self):
        spec=s.GateSpec(1,ADD,0,100,0,0,0)
        old=s.Cell(address=15,age=s.PERIOD-1,kind=s.GATE,
                   gates=(spec,s.EMPTY_GATE,s.EMPTY_GATE),
                   arg0=7,arg1=9,ready=3,result=16,done=1)
        wrapped=s.local_step((s.Cell(),old,s.Cell()))
        self.assertEqual((wrapped.arg0,wrapped.arg1,wrapped.ready,
                          wrapped.result,wrapped.done),(0,0,0,0,0))

    def test_packet_can_circulate_until_its_gate_slot_activates(self):
        old=s.GateSpec(1,ADD,0,100,1,2,3)
        new=s.GateSpec(1,ADD,0,101,7,0,1)
        target=s.Cell(address=15,age=8,kind=s.GATE,
                      gates=(old,new,s.EMPTY_GATE),switch_ages=(10,0),
                      arg0=1,arg1=2,ready=3,result=3,done=1)
        incoming=s.Packet(1,15,1,1,5)
        passed=s.local_step((s.Cell(mail=incoming),target,s.Cell()))
        self.assertEqual(passed.mail,incoming)
        self.assertEqual((passed.active_slot,passed.collision),(0,0))
        accepted=s.local_step((s.Cell(mail=incoming),replace(passed,mail=s.EMPTY_PACKET),s.Cell()))
        self.assertEqual((accepted.active_slot,accepted.mail,accepted.arg1,
                          accepted.ready,accepted.collision),(1,s.EMPTY_PACKET,5,3,0))

    def test_output_sink_accepts_packet_and_resets_on_period_boundary(self):
        sink=s.Cell(address=15,age=8,kind=s.OUTPUT)
        packet=s.Packet(1,15,0,2,0x1234)
        accepted=s.local_step((s.Cell(mail=packet),sink,s.Cell()))
        self.assertEqual((accepted.mail,accepted.source_value,accepted.done,
                          accepted.collision),(s.EMPTY_PACKET,0x1234,1,0))
        repeated=s.local_step((s.Cell(mail=packet),accepted,s.Cell()))
        self.assertEqual((repeated.source_value,repeated.done,repeated.collision),
                         (0x1234,1,0))
        conflicting=s.local_step((s.Cell(mail=s.Packet(1,15,0,0,7)),accepted,s.Cell()))
        self.assertEqual((conflicting.source_value,conflicting.collision),(7,1))
        wrapped=s.local_step((s.Cell(),replace(accepted,age=s.PERIOD-1),s.Cell()))
        self.assertEqual((wrapped.age,wrapped.source_value,wrapped.done),(0,0,0))
        wrong_target=s.local_step((s.Cell(mail=s.Packet(1,16,0,0,7)),sink,s.Cell()))
        self.assertEqual((wrong_target.mail.target,wrong_target.done),(16,0))

    def test_marked_output_opcode_latches_through_gate_switch(self):
        self.assertEqual(len(set(s.OUTPUT_OPCODE.values())),7)
        self.assertTrue(all(s.base_opcode(marked)==plain
                            for plain,marked in s.OUTPUT_OPCODE.items()))
        first=s.GateSpec(1,s.OUTPUT_OPCODE[ADD],0,101,3,5,3)
        second=s.GateSpec(1,AND,0,102,7,3,3)
        old=s.Cell(address=15,age=0,kind=s.GATE,
                   gates=(first,second,s.EMPTY_GATE),switch_ages=(10,0),
                   arg0=3,arg1=5,ready=3)
        latched=s.local_step((s.Cell(),old,s.Cell()))
        self.assertEqual((latched.result,latched.source_value,latched.done),(8,8,1))
        switched=s.local_step((s.Cell(),replace(latched,age=9),s.Cell()))
        self.assertEqual((switched.active_slot,switched.result,
                          switched.source_value),(1,3,8))
        wrapped=s.local_step((s.Cell(),replace(switched,age=s.PERIOD-1),s.Cell()))
        self.assertEqual((wrapped.active_slot,wrapped.source_value),(0,8))

    def test_output_packet_moves_left_using_existing_direction_tag(self):
        packet=s.Packet(1,15,0,3,0x55)
        middle=s.Cell(address=16,age=8,kind=s.INERT)
        passed=s.local_step((s.Cell(),middle,s.Cell(mail=packet)))
        self.assertEqual((passed.mail,passed.collision),(packet,0))
        sink=s.Cell(address=15,age=9,kind=s.OUTPUT)
        accepted=s.local_step((s.Cell(),sink,s.Cell(mail=passed.mail)))
        self.assertEqual((accepted.mail,accepted.source_value,
                          accepted.done,accepted.collision),
                         (s.EMPTY_PACKET,0x55,1,0))
        source=s.Cell(address=18,age=8,kind=s.SOURCE,source_value=0x55,
                      routes=(s.Route(1,15,0,3,0,9),)+
                             (s.EMPTY_ROUTE,)*(s.ROUTE_SLOTS-1))
        emitted=s.local_step((s.Cell(),source,s.Cell()))
        self.assertEqual(emitted.mail,packet)
        opposing=s.local_step((s.Cell(mail=s.Packet(1,16,0,0,3)),
                               middle,s.Cell(mail=packet)))
        self.assertEqual(opposing.collision,1)

    def test_ninth_layer_full_ring_sampled_dynamics(self):
        transition=s.local_step;width=s.WIDTH
        eight=check(False)
        result=check(True)
        self.assertTrue(eight['passed'])
        self.assertEqual(eight['evaluated_dag_prefix'],8)
        self.assertEqual(eight['first_epoch_outputs_checked'],4653)
        self.assertTrue(result['passed'])
        self.assertEqual(result['evaluated_dag_prefix'],9)
        self.assertEqual(result['first_epoch_outputs_checked'],4653)
        self.assertEqual(result['ninth_layer_outputs_checked'],371)
        self.assertEqual(result['schedule']['ninth_layer_last_completion'],20137)
        self.assertGreater(result['complete_local_steps'],s.Q)
        self.assertIs(s.local_step,transition)
        self.assertEqual(s.WIDTH,width)


if __name__=='__main__':unittest.main()
