from dataclasses import replace
import random
import unittest
from gacsca.fixed_rule import small_holder_rule as f, small_holder_projected as r
from gacsca.fixed_rule import small_holder_native as native, small_holder_boundary as cap
from gacsca.fixed_rule.wordcode import LIT
from experiments.fixed_rule.prove_small_holder_cap_defect import prove, prove_case


class CapDefect(unittest.TestCase):
    def test_all_addresses_clocks_and_workspace_flags(self):
        result=prove()
        self.assertTrue(result['passed']);self.assertEqual(len(result['cases']),12)
        self.assertEqual(result['all_ages'],1<<32)
        self.assertEqual(result['all_replacement_addresses'],1<<15)
        self.assertTrue(all(x['independent_bits']==69 for x in result['cases']))

    def test_mutations_and_incomplete_description_are_detected(self):
        desc=f.self_description()
        with self.assertRaises(ValueError):prove_case(0,replace(desc,outputs=desc.outputs[:-1]))
        outputs=list(desc.outputs);outputs[f.COL['age']]=7*f.FIELDS+f.COL['age']
        with self.assertRaises(AssertionError):prove_case(0,replace(desc,outputs=tuple(outputs)))
        # A constant cap Address passes an undamaged cap orbit but falsifies the
        # persistent-defect theorem. This distinguishes the two claims.
        outputs=list(desc.outputs);outputs[f.COL['address']]=desc.wires
        changed=replace(desc,operations=desc.operations+((LIT,f.Q-1,0),),outputs=tuple(outputs))
        with self.assertRaises(AssertionError):prove_case(0,changed)

    def test_arbitrary_other_raw_fields_match_scalar_and_native(self):
        rng=random.Random(76543)
        for age in (0,15,f.VOTE_AGES[0],f.WF_START,f.U-1):
            cells=[]
            for i in range(17):
                fields={name:rng.getrandbits(width) for name,width in r.SCHEMA}
                fields.update(address=1234 if i==8 else f.Q-1,age=age,f1=1,f2=1)
                cells.append(r.lift(r.Cell(**fields)))
            actual=native.step_ring(tuple(cells))
            for i,cell in enumerate(actual):
                self.assertEqual((cell.address,cell.age,cell.f1,cell.f2),(1234 if i==8 else f.Q-1,(age+1)%f.U,1,1))
            for i in (3,8,13):
                self.assertEqual(actual[i],f.local_step(tuple(cells[(i+j)%17] for j in f.NEIGHBORHOOD)))

    def test_one_bit_cap_fault_remains_through_controller_pulses(self):
        for start in (0,f.VOTE_AGES[0]-1,f.RESET_AGES[4]-1,f.U-2):
            cells=[r.lift(cap.cell(start)) for _ in range(17)]
            cells[8]=r.lift(replace(cap.cell(start),address=f.Q-2))
            for dt in range(12):
                cells=native.step_ring(tuple(cells))
                self.assertEqual([x.address for x in cells],[f.Q-1]*8+[f.Q-2]+[f.Q-1]*8)
                self.assertTrue(all(x.age==(start+dt+1)%f.U and x.f1==x.f2==1 for x in cells))

if __name__=='__main__':unittest.main()
