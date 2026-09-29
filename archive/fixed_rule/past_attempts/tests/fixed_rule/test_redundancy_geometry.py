"""Indistinguishability witness for naive redundant instantaneous voting."""
import unittest
from gacsca.fixed_rule import serial_vote_clock_description as described,serial_vote_rule as f
from gacsca.fixed_rule.wordcode import LIT

class RedundancyGeometry(unittest.TestCase):
    def test_current_radius_two_vote_requires_radius_six_after_precorrection(self):
        def damaged(value):
            primary={1:0,3:1,4:value}
            holders={x:[primary.get(x+d,0) for d in range(-2,3)] for x in range(-8,9)}
            # In either world only two physical holders have one bad backup bit.
            for x in ((4,5) if value==0 else (2,3)):holders[x][4-x+2]^=1
            return holders
        zero,one=damaged(0),damaged(1)
        self.assertEqual([zero[x] for x in range(-5,6)],[one[x] for x in range(-5,6)])
        def decode(holders,target):return int(sum(holders[target+e][2-e] for e in range(-2,3))>=3)
        def wanted(holders):return int(sum(decode(holders,a) for a in (1,3,4))>=2)
        self.assertEqual(wanted(zero),0);self.assertEqual(wanted(one),1)
        self.assertNotEqual(zero[6],one[6])
        # The backup at physical x=0 for logical x+2 must differ, but its entire
        # permitted radius-five input is identical. No such one-tick map exists.

    def test_serial_clock_healthy_procedure_uses_only_radius_one_inputs(self):
        d=described.build(healthy_domain=True);pending=list(d.outputs);seen=set();inputs=set()
        while pending:
            w=pending.pop()
            if w in seen:continue
            seen.add(w)
            if w<d.inputs:inputs.add(w);continue
            op,a,b=d.operations[w-d.inputs]
            if op!=LIT:pending.extend((a,b))
        self.assertTrue(inputs);self.assertTrue(all(f.FIELDS<=w<4*f.FIELDS for w in inputs))
        # Signal/maintenance remain separately radius five; this support claim
        # concerns healthy controller/data/mail procedures, not the whole rule.

if __name__=='__main__':unittest.main()
