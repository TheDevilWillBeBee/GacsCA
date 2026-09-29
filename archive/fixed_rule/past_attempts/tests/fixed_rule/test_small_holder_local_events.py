from dataclasses import replace
import unittest
from gacsca.fixed_rule import small_holder_rule as f,small_holder_program as p
from gacsca.fixed_rule.wordcode import NAND,MASK,LIT
from experiments.fixed_rule.certify_small_holder_local_events import Algebra,cases,certify_case


class LocalEvents(unittest.TestCase):
    def test_all_stated_full_raw_event_identities(self):
        events=cases();self.assertEqual(len(events),67)
        for event in events:self.assertTrue(certify_case(event)['passed'])

    def test_arithmetic_and_stale_controller_mutations_are_detected(self):
        desc=f.self_description();events={x['name']:x for x in cases()}
        for name,field in (('read_b_2','s2_value'),('write','s2_pc'),('write','s2_alu')):
            outputs=list(desc.outputs);outputs[f.COL[field]]=7*f.FIELDS+f.COL[field]
            with self.assertRaises(AssertionError):certify_case(events[name],replace(desc,outputs=tuple(outputs)))
        with self.assertRaises(ValueError):certify_case(events['load'],replace(desc,outputs=desc.outputs[:-1]))

    def test_emitted_packet_cannot_be_omitted(self):
        desc=f.self_description();event=next(x for x in cases() if x['name']=='send_0_7')
        zero=next(desc.inputs+i for i,(op,a,b) in enumerate(desc.operations) if op==LIT and a==0)
        outputs=list(desc.outputs);outputs[f.COL['s2_rp_valid']]=zero
        with self.assertRaises(AssertionError):certify_case(event,replace(desc,outputs=tuple(outputs)))

    def test_added_bitwise_rewrites_are_valid(self):
        a=Algebra(p.base_rom());x=a.variable('x',64)
        self.assertEqual(a.inv(a.inv(x)),x)
        self.assertEqual(a.band(x,x),x)
        self.assertEqual(a.op(NAND,x,a.const(MASK)),a.inv(x))
        self.assertEqual(a.value(a.op(NAND,x,a.const(0))),MASK)
        for value in (0,1,63,64,0x123456789ABCDEF0,MASK):
            self.assertEqual(a.value(a.inv(a.const(value))),value^MASK)
            self.assertEqual(a.value(a.op(NAND,a.const(value),a.const(value))),value^MASK)

if __name__=='__main__':unittest.main()
