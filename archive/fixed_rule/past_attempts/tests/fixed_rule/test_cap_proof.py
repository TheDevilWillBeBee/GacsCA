from dataclasses import replace
import unittest
from gacsca.fixed_rule import repair_b_rule as f,repair_b_projected as r,repair_b_initial as initial
from experiments.fixed_rule.prove_cap_orbit import prove
from experiments.fixed_rule.prove_cap_payload import prove as payload_proof

class CapProof(unittest.TestCase):
    def test_all_ages_and_independent_neighbor_payloads(self):
        self.assertEqual(prove()['all_ages'],f.U)
        self.assertEqual(payload_proof()['maximum_payload_reset_delay'],32*f.Q)
    def test_nonzero_payload_capture_spike_is_retained(self):
        cap=replace(initial.terminal_data(age=f.CAPTURE_AGE-1)[0],data=1)
        after=r.step_ring((cap,))[0]
        self.assertEqual(after.signal,1);self.assertEqual(after.data,1)
        self.assertEqual(r.step_ring((after,))[0].signal,0)
    def test_frozen_clock_counterexample_is_detected(self):
        d=f.self_description();outputs=list(d.outputs);outputs[f.COL['age']]=5*f.FIELDS+f.COL['age']
        with self.assertRaises(AssertionError):prove(replace(d,outputs=tuple(outputs)))
    def test_missing_raw_controller_output_is_detected(self):
        d=f.self_description();outputs=list(d.outputs);outputs[f.COL['head']]=d.outputs[f.COL['f1']]
        with self.assertRaises(AssertionError):prove(replace(d,outputs=tuple(outputs)))

if __name__=='__main__':unittest.main()
