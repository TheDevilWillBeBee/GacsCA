from dataclasses import replace
import unittest
from experiments.fixed_rule.check_cap_proof_contract import checked,candidate,serial

class ProofContract(unittest.TestCase):
    def test_both_complete_rules(self):
        for checker in (candidate,serial):self.assertTrue(checked(checker)['passed'])
    def test_missing_or_extra_raw_output_is_rejected(self):
        for checker in (candidate,serial):
            d=checker.f.self_description()
            for outputs in (d.outputs[:-1],d.outputs+(d.outputs[0],)):
                with self.assertRaises(ValueError):checked(checker,replace(d,outputs=outputs))
    def test_forward_reference_and_unknown_instruction_are_rejected(self):
        d=candidate.f.self_description()
        for row in ((999,0,0),(1,d.wires,0)):
            with self.assertRaises(ValueError):checked(candidate,replace(d,operations=(row,*d.operations[1:])))

if __name__=='__main__':unittest.main()
