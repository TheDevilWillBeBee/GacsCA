from dataclasses import replace
import random
import unittest
from gacsca.fixed_rule import clock_rule as f,canonical_flags as c


class CanonicalFlagTests(unittest.TestCase):
    def test_boundary_left_flag_patterns_and_computed_flag1_do_not_change_geometry(self):
        total=0
        for address in (*range(6),*(f.Q-j for j in range(1,7)),f.Q//2):
            for mask in range(32):
                for flag2 in (0,1):
                    for forced_f1 in (0,1):
                        for force_wf2 in (0,1):
                            row=[f.Cell(address=(address+j)%f.Q,age=f.U-1,wf1=forced_f1,wf2=force_wf2) for j in range(-5,6)]
                            row[5]=replace(row[5],f2=flag2)
                            for bit,j in enumerate(range(-1,-6,-1)):row[j+5]=replace(row[j+5],f2=(mask>>bit)&1)
                            actual=c.transition(row);expected=f.maintenance(row)
                            self.assertEqual(actual,expected)
                            self.assertEqual((actual['address'],actual['age'],actual['f1']),(address,0,forced_f1));total+=1
        self.assertEqual(total,3328)

    def test_raw_workspace_and_arbitrary_flag_patterns_match_complete_rule(self):
        rng=random.Random(2801)
        for _ in range(300):
            address=rng.choice((0,1,4,5,f.Q-1,f.Q-4,rng.randrange(f.Q)))
            age=rng.choice((0,15,72*f.Q,96*f.Q,98*f.Q-1,f.U-1))
            row=[f.Cell(**{name:rng.randrange(1<<width) for name,width in f.SCHEMA}) for _ in range(11)]
            row=tuple(replace(x,address=(address+j-5)%f.Q,age=age) for j,x in enumerate(row))
            actual=c.transition(row);full=f.local_step(row)
            self.assertEqual(actual,{name:getattr(full,name) for name in actual})

    def test_noncanonical_geometry_is_rejected_and_zero_flag_assumption_is_false(self):
        row=[f.Cell(address=100+j,age=77) for j in range(-5,6)]
        for j in (4,5,6):row[j]=replace(row[j],wf1=1)
        out=c.transition(row);self.assertEqual(out['f1'],1);self.assertEqual(out['address'],100)
        wrong=list(row);wrong[0]=replace(wrong[0],address=1)
        with self.assertRaises(ValueError):c.transition(wrong)
        wrong=list(row);wrong[0]=replace(wrong[0],age=1)
        with self.assertRaises(ValueError):c.transition(wrong)


if __name__=='__main__':unittest.main()
