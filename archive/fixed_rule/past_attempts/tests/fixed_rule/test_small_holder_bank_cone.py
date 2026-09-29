from unittest.mock import patch
import unittest
from gacsca.fixed_rule import small_holder_bank as bank, small_holder_bank_cone as cone
from gacsca.fixed_rule import small_holder_rule as f, small_holder_core as c, small_holder_quotient as q
from gacsca.fixed_rule import small_holder_native as native, small_holder_projected as projected


class BankCone(unittest.TestCase):
    def make(self,age=1):
        b=bank.Builder(1,age)
        b.set_logical(100,q.Cell(address=100,age=age,data=11,head=1,phase=c.WRITE,rd=100,value=91))
        b.set_logical(f.Q-1,q.Cell(address=f.Q-1,age=age,rp_target=1,rp_data=37,rp_valid=1,rp_remaining=1))
        return b

    def literal(self,s,start,count,ticks):
        values={x:s.cell(x%s.sites) for x in range(start-7*ticks,start+count+7*ticks)}
        for t in range(ticks):
            margin=7*(ticks-t-1)
            values={x:native.local_step(tuple(values[x+j] for j in f.NEIGHBORHOOD)) for x in range(start-margin,start+count+margin)}
        return tuple(values[x] for x in range(start,start+count))

    def test_successive_physical_ticks_with_active_controller_and_wrap_mail(self):
        for start in (98,f.Q-2):
            s=self.make().freeze();expected=self.literal(s,start,5,4)
            # Upper transitions and CPU physical evaluators cannot replace CUDA.
            with patch.object(f,'local_step',side_effect=AssertionError('host physical transition')),patch.object(native,'local_step',side_effect=AssertionError('host native transition')),patch.object(projected,'local_step',side_effect=AssertionError('host upper transition')):
                result=cone.run(s,start,5,4)
            self.assertEqual(result.cells,expected)
            self.assertEqual(result.local_evaluations,104)
            self.assertEqual(result.physical_ticks,4)
            if start==98:self.assertEqual(result.cells[2].s2_data,91)
            self.assertLess(result.max_device_bytes,64*1024**2)

    def test_two_damaged_procedure_holders_repair_during_active_write(self):
        clean=self.make();damaged=self.make()
        for pos in (100,101):
            damaged.set_raw_fields(pos,**{f's{k+2}_{n}':(1<<w)-1 for k in f.OFFSETS for n,w in f.PROCEDURE})
        original=damaged.freeze()
        self.assertNotEqual(original.cell(100),clean.freeze().cell(100))
        got=cone.run(original,97,9,3)
        wanted=cone.run(clean.freeze(),97,9,3)
        self.assertEqual(got.cells,wanted.cells)
        self.assertEqual(got.cells[3].s2_data,91)

    def test_rejects_uncertified_horizons(self):
        s=self.make().freeze()
        for args in ((0,f.Q,1),(0,1,-1),(-1,1,1)):
            with self.assertRaises(ValueError):cone.run(s,*args)
        result=cone.run(s,100,1,0)
        self.assertEqual(result.cells,(s.cell(100),))


if __name__=='__main__':unittest.main()
