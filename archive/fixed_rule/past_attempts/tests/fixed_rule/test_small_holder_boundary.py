from dataclasses import replace
import unittest
from gacsca.fixed_rule import small_holder_rule as f,small_holder_projected as r,small_holder_native as native,small_holder_boundary as cap
from experiments.fixed_rule.prove_small_holder_boundary import prove

class HolderBoundary(unittest.TestCase):
    def test_all_clock_full_controller_orbit(self):
        proof=prove();self.assertTrue(proof['passed']);self.assertEqual(proof['all_ages'],1<<32);self.assertEqual(proof['complete_raw_words'],154)
    def test_required_backup_pulses_and_wrap_match_native(self):
        ages={0,f.U-1}
        for age,pc in cap.pulse_entries():ages.update((age-1,age,age+1))
        for age in sorted(ages):
            old=r.lift(cap.cell(age));self.assertEqual(r.project(native.local_step((old,)*15)),cap.cell((age+1)%f.U))
        old=r.lift(cap.cell(0));actual=r.project(native.local_step((old,)*15))
        self.assertNotEqual(actual,replace(cap.cell(0),age=1))
        self.assertEqual(actual.s3_head,1)
    def test_missing_raw_fields_or_forward_wires_are_rejected(self):
        d=f.self_description()
        for bad in (replace(d,outputs=d.outputs[:-1]),replace(d,inputs=d.inputs-1),replace(d,operations=((1,d.inputs+1,0),)+d.operations[1:])):
            with self.assertRaises(ValueError):prove(bad)

if __name__=='__main__':unittest.main()
