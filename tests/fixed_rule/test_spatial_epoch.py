"""Actual local gate reuse and nine-layer encoded route regression."""
from dataclasses import replace
import unittest

from gacsca.fixed_rule import spatial_epoch as s
from gacsca.fixed_rule.wordcode_and import AND,ADD
from experiments.fixed_rule.measure_spatial_epoch import check


class SpatialEpoch(unittest.TestCase):
    def test_one_fixed_rule_and_alphabet(self):
        self.assertEqual((s.Q,s.PERIOD,s.WIDTH,s.NEIGHBORHOOD),
                         (8192,65536,2375,(-1,0,1)))
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
