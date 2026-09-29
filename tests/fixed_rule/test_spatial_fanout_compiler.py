"""Static full-DAG capacity and transformed-value regressions."""
from dataclasses import replace
import random
import unittest

from gacsca.fixed_rule import spatial_epoch as physical
from gacsca.fixed_rule import spatial_fanout_compiler as compiler
from gacsca.fixed_rule import stream28_holder_program as reference
from gacsca.fixed_rule import stream28_holder_rule as raw


class SpatialFanoutCompilation(unittest.TestCase):
    def test_complete_own_dag_fits_fixed_static_slots(self):
        compiled=compiler.compile_capacity()
        self.assertTrue(compiler.validate_compilation(compiled))
        self.assertEqual(compiled.description_sha256,reference.compiled_description().digest())
        self.assertEqual((physical.Q,physical.WIDTH),(8192,2334))
        self.assertEqual((len(compiled.nodes),len(compiled.uses)),(11065,19237))
        self.assertEqual(sum(n-1 for n in compiled.copy_counts),11)
        self.assertEqual(sum(n>1 for n in compiled.copy_counts),8)
        self.assertEqual(compiled.first_eight_pinned,4653)
        self.assertLessEqual(max(compiled.site_route_counts),physical.ROUTE_SLOTS)
        self.assertLessEqual(max(compiled.raw_route_counts),physical.ROUTE_SLOTS)
        self.assertLessEqual(max(compiled.site_gate_counts),physical.GATE_SLOTS)

    def test_all_original_outputs_survive_duplication(self):
        compiled=compiler.compile_capacity()
        rng=random.Random(2026092835)
        for _ in range(2):
            words=tuple(rng.getrandbits(width) for _ in range(15)
                        for _,width in raw.SCHEMA)
            self.assertEqual(compiler.evaluate_compiled(words,compiled),
                             reference.compiled_description().evaluate(words))

    def test_wrong_route_and_slot_are_rejected(self):
        compiled=compiler.compile_capacity()
        index=next(i for i,use in enumerate(compiled.uses) if use.source_gate>=0)
        use=compiled.uses[index]
        altered=list(compiled.uses)
        altered[index]=replace(use,source_site=use.source_site+1)
        with self.assertRaisesRegex(AssertionError,'provenance changed'):
            compiler.validate_compilation(replace(compiled,uses=tuple(altered)))
        node=compiled.nodes[0]
        altered_nodes=(replace(node,slot=physical.GATE_SLOTS),)+compiled.nodes[1:]
        with self.assertRaisesRegex(AssertionError,'invalid or duplicate gate placement'):
            compiler.validate_compilation(replace(compiled,nodes=altered_nodes))


if __name__=='__main__':unittest.main()
