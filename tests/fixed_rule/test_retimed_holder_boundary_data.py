from dataclasses import replace
import unittest

from gacsca.fixed_rule import retimed_holder_rule as f
from gacsca.fixed_rule import retimed_holder_projected as r
from gacsca.fixed_rule import retimed_holder_boundary_data as cap
from experiments.fixed_rule.prove_retimed_holder_boundary import prove_orbit, prove_defect


class RetimedBoundaryData(unittest.TestCase):
    def test_complete_orbit_all_normalized_clocks(self):
        proof = prove_orbit()
        self.assertEqual(proof['normalized_ages'], f.U)
        self.assertEqual(proof['symbolic_age_bits'], 31)
        self.assertEqual(proof['raw_age_width'], 32)
        self.assertEqual(proof['complete_raw_words'], f.FIELDS)

    def test_scalar_pulses_and_wrap(self):
        ages = {0, f.U - 1, f.WF_START - 1, f.WF_END - 1, f.CAPTURE_AGE - 1}
        for when, _ in cap.pulse_entries():
            ages.update((when - 1, when, when + 1))
        for age in sorted(ages):
            self.assertEqual(r.local_step((cap.cell(age),) * 15), cap.cell((age + 1) % f.U))
        self.assertEqual(cap.cell(1).s3_head, 1)
        self.assertNotEqual(cap.cell(1), replace(cap.cell(), age=1))
        for bad in (-1, f.U, True):
            with self.assertRaises(ValueError):
                cap.cell(bad)

    def test_incomplete_neighborhood_or_outputs_rejected(self):
        description = f.self_description()
        for bad in (replace(description, inputs=description.inputs - 1),
                    replace(description, outputs=description.outputs[:-1])):
            with self.assertRaises(ValueError):
                prove_orbit(bad)

    def test_frozen_clock_and_missing_controller_pulse_rejected(self):
        description = f.self_description()
        for name in ('age', 's3_head', 's3_pc'):
            outputs = list(description.outputs)
            outputs[f.COL[name]] = 7 * f.FIELDS + f.COL[name]
            with self.assertRaises(AssertionError):
                prove_orbit(replace(description, outputs=tuple(outputs)))

    def test_defect_all_offsets_and_raw_clock_normalization(self):
        for offset in (None, *range(-5, 6)):
            proof = prove_defect(offset)
            self.assertTrue(proof['passed'])
            self.assertEqual(proof['raw_clocks'], 1 << 32)
            self.assertEqual(proof['independent_bits'], 69)

    def test_healthy_orbit_does_not_establish_defect_result(self):
        description = f.self_description()
        outputs = list(description.outputs)
        # A neighbor with the healthy Address can conceal the defect in an
        # undamaged-orbit check, but violates preservation at the damaged site.
        outputs[f.COL['address']] = 6 * f.FIELDS + f.COL['address']
        changed = replace(description, outputs=tuple(outputs))
        self.assertTrue(prove_orbit(changed)['passed'])
        with self.assertRaises(AssertionError):
            prove_defect(0, changed)


if __name__ == '__main__':
    unittest.main()
