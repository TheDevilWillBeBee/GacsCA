"""Follow actual nested Info/Data paths, not only unencoded boot/padding sites."""
import unittest
from gacsca.fixed_rule import clock_rule as f,early_projected as r,early_program as p,early_initial as initial


class EarlyNestingTests(unittest.TestCase):
    def test_every_raw_word_reaches_the_bottom_of_three_initial_levels(self):
        top=(r.Cell(address=0,age=f.U-1,head=1,phase=7,pc=0xFFFFFFFF,ra=0xABCDEF01,rb=f.MASK,rd=f.MASK,value=f.MASK,alu=7,data=f.MASK,lp_valid=1,lp_target=0xFFFFFFFF,lp_data=f.MASK,lp_remaining=7,f1=1,f2=1,wf1=1,wf2=1),
             r.Cell(address=f.Q-1,data=0xFEDCBA9876543210,age=99,rp_valid=1,rp_data=f.MASK,rp_target=0xFFFFFFFF,rp_remaining=7))
        g=p.layout();identity=r.identity()
        for depth in (1,2,3):
            for t,c in enumerate(top):
                raw=f.encode_cell(r.lift(c))
                for k,word in enumerate(raw):
                    position=t*f.Q+g.info[k]
                    for _ in range(depth-1):position=position*f.Q+g.info[f.COL['data']]
                    physical=initial.cell_at(top,depth,position)
                    self.assertEqual(physical.data,word,(depth,t,k))
                    self.assertEqual(len(r.encode_cell(physical)),24)
            self.assertEqual(initial.resources(len(top),depth)['fixed_rule'],identity)


if __name__=='__main__':unittest.main()
