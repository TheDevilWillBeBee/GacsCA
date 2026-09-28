"""Reject violations of the spatial premises used in the global proof join."""
import json
from pathlib import Path
import tempfile
import unittest

from gacsca.fixed_rule import small_holder_rule as f
from gacsca.fixed_rule.wordcode import Program
from experiments.fixed_rule.join_small_holder_structural_invariant import support,join


class StructuralInvariant(unittest.TestCase):
    def test_distant_head_dependency_rejected(self):
        desc=f.self_description();outputs=list(desc.outputs)
        outputs[f.COL['s2_data']]=(7+2)*f.FIELDS+f.COL['s2_head']
        mutant=Program(desc.inputs,desc.operations,tuple(outputs))
        with self.assertRaisesRegex(AssertionError,'logical support exceeds one'):support(mutant)

    def test_mutable_metadata_rejected(self):
        desc=f.self_description();outputs=list(desc.outputs)
        outputs[f.COL['p3_first']]=7*f.FIELDS+f.COL['s2_head']
        mutant=Program(desc.inputs,desc.operations,tuple(outputs))
        with self.assertRaisesRegex(AssertionError,'static metadata changed'):support(mutant)

    def test_missing_controller_phase_rejected(self):
        root=Path(__file__).resolve().parents[2]
        h=root/'figs/fixed_rule/small_holder_head_invariant_v1.json'
        image=root/'figs/fixed_rule/small_holder_procedure_image_v1.json'
        data=json.loads(h.read_text());data['cases']=data['cases'][:-1]
        with tempfile.TemporaryDirectory(prefix='fixed_rule_head_join_') as directory:
            damaged=Path(directory)/'missing_phase.json';damaged.write_text(json.dumps(data))
            with self.assertRaises(AssertionError):join(damaged,image)


if __name__=='__main__':unittest.main()
