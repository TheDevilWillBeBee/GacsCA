from dataclasses import replace
import random
import unittest
from gacsca.fixed_rule import clock_rule as f,canonical_clock_native as native
from gacsca.fixed_rule.canonical_clock_description import build


class CanonicalClockTests(unittest.TestCase):
    def test_complete_clock_outputs_with_arbitrary_flags_at_all_boundary_ages(self):
        rng=random.Random(2802);program=build();lib=native.library();total=0
        ages={0,1,15,f.U-1}
        for age in (*f.RESET_AGES,*f.ACTIVE_ENDS,*f.VOTE_AGES,98*f.Q):ages.update(((age-1)%f.U,age,(age+1)%f.U))
        for age in ages:
            for address in (0,1,4,5,f.Q//2,f.Q-5,f.Q-1):
                row=[f.Cell(**{n:rng.randrange(1<<w) for n,w in f.SCHEMA}) for _ in range(11)]
                row=tuple(replace(c,address=(address+j-5)%f.Q,age=age) for j,c in enumerate(row))
                expected=f.local_step(row)
                self.assertEqual(native.local_step(row,lib),expected)
                self.assertEqual(f.decode_cell(program.evaluate(tuple(v for c in row for v in f.encode_cell(c)))),expected)
                total+=1
        self.assertGreater(total,200)

    def test_noncanonical_domains_are_rejected(self):
        row=tuple(f.Cell(address=100+j,age=1) for j in range(-5,6))
        for name,value in (('address',12345),('age',2)):
            bad=list(row);bad[0]=replace(bad[0],**{name:value})
            with self.assertRaises(ValueError):native.local_step(bad)
        with self.assertRaises(ValueError):native.dense_step(native.array_from_cells(row))


if __name__=='__main__':unittest.main()
