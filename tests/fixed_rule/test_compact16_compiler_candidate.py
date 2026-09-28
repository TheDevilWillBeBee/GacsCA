"""Meaningful mutation checks for the isolated fixed-ROM compiler candidate."""
from dataclasses import replace
import random
import unittest
from gacsca.fixed_rule import compact16_holder_rule as f,compact16_holder_program as old
from gacsca.fixed_rule import compact16_holder_compiler_program as candidate
from gacsca.fixed_rule import word_boolean_cuts as cuts,word_dag_order as order
from experiments.fixed_rule.certify_compact16_holder_compiler_rom_v2 import Checker


class CompilerCandidate(unittest.TestCase):
    def test_all_raw_fields_match_actual_local_rule(self):
        rng=random.Random(202609280101)
        description=candidate.compiled_description()
        cases=[]
        for _ in range(6):
            cases.append(tuple(f.Cell(**{name:rng.getrandbits(width) for name,width in f.SCHEMA}) for _ in f.NEIGHBORHOOD))
        for age in (0,f.U-1,2*f.U-1):
            cases.append(tuple(f.Cell(age=age,address=(j+f.Q-7)%(2*f.Q)) for j in range(15)))
        for cells in cases:
            words=tuple(word for cell in cells for word in f.encode_cell(cell))
            self.assertEqual(description.evaluate(words),f.encode_cell(f.local_step(cells)))

    def test_rule_identity_and_complete_controller(self):
        description,proof,permutation=candidate.proof()
        optimized=cuts.optimize(old.compiled_description())[0]
        self.assertEqual(cuts.verify(old.compiled_description(),optimized,proof)['complete_outputs'],f.FIELDS)
        self.assertTrue(order.verify(optimized,description,permutation))
        self.assertEqual(candidate.RESULT_CAPACITY,270)
        self.assertEqual((f.Q,f.U,f.WIDTH,len(f.SCHEMA)),(16384,1<<30,4090,154))
        self.assertEqual(candidate.layout().description_sha256,description.digest())
        self.assertEqual(len(candidate.layout().info),154)
        self.assertEqual(len(candidate.layout().hold),154)
        self.assertEqual(len(candidate.base_rom()),candidate.layout().computation_cells)
        self.assertEqual(Checker().check()['complete_raw_outputs_per_colony'],154)

    def test_mutations_of_output_and_boolean_proof_fail(self):
        description,proof,permutation=candidate.proof()
        optimized=cuts.optimize(old.compiled_description())[0]
        wrong=list(description.outputs);wrong[f.COL['s2_pc']]=wrong[f.COL['s2_phase']]
        with self.assertRaises(AssertionError):order.verify(optimized,replace(description,outputs=tuple(wrong)),permutation)
        invalid=dict(proof);entries=list(invalid['rewrites']);entries[0]=dict(entries[0],truth=entries[0]['truth']^1)
        invalid['rewrites']=tuple(entries)
        with self.assertRaises(AssertionError):cuts.verify(old.compiled_description(),optimized,invalid)


if __name__=='__main__':unittest.main()
