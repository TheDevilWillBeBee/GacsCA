"""Full terminal-memory identity: independent expressions and rejected omissions."""
from dataclasses import replace
import random
import unittest
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import retimed_holder_terminal_dag as dag,retimed_holder_terminal_reference as reference
from gacsca.fixed_rule import retimed_holder_projected as r,retimed_holder_rule as f,retimed_holder_program as p
from gacsca.fixed_rule.wordcode import Program
from experiments.fixed_rule.certify_retimed_holder_terminal_layout import certify


def random_parents(n, seed=2026092701):
    rng=random.Random(seed)
    return tuple(r.Cell(**{name:rng.getrandbits(width) for name,width in r.SCHEMA}) for _ in range(n))


class Terminal(unittest.TestCase):
    def compare(self, parents):
        a,b=dag.terminal(parents),reference.terminal(parents)
        for key in a:np.testing.assert_array_equal(a[key],b[key],err_msg=key)
        actual=np.array([f.encode_cell(r.lift(x)) for x in r.step_ring(parents)],dtype=np.uint64)
        np.testing.assert_array_equal(a['committed_bank'][:,list(p.layout().info)],actual)
        return a

    def test_random_complete_typed_state(self):
        for n in (1,3,15):
            with self.subTest(n=n):self.compare(random_parents(n))

    def test_extreme_fields_and_geometry(self):
        parents=(r.Cell(),r.Cell(**{name:(1<<width)-1 for name,width in r.SCHEMA}))
        self.compare(parents)
        for address in (0,1,f.Q-3,f.Q-1):self.compare((replace(parents[1],address=address),))

    def test_successive_controller_transitions(self):
        from experiments.fixed_rule.run_retimed_holder_cpu_periods import parents
        current=parents(15)
        for _ in range(2):
            result=self.compare(current)
            following=r.step_ring(current)
            self.assertNotEqual(current,following)
            current=following

    def test_complete_layout(self):
        result=certify()
        self.assertEqual(result['full_terminal_bank_words'],9916)
        self.assertEqual(result['all_raw_outputs'],len(f.SCHEMA))

    def test_layout_omission_and_wrong_writer_rejected(self):
        g=p.layout()
        variants=[replace(g,hold=g.hold[:-1]),replace(g,wires=g.wires[:-1])]
        ops=list(g.instructions);start,_=g.stage_ranges[4]
        ops[start]=replace(ops[start],d=0)
        variants.append(replace(g,instructions=tuple(ops)))
        for bad in variants:
            with self.assertRaises(AssertionError):certify(bad)

    def test_missing_controller_output_rejected(self):
        desc=p.compiled_description()
        bad=Program(desc.inputs,desc.operations,desc.outputs[:-1])
        with patch.object(p,'compiled_description',return_value=bad):
            with self.assertRaises(AssertionError):certify()

    def test_bounded_diagnostics(self):
        with self.assertRaises(ValueError):dag.terminal(())
        with self.assertRaises(ValueError):dag.terminal((r.Cell(),)*65)
        with self.assertRaises(ValueError):reference.terminal((r.Cell(),),max_bytes=1)


if __name__=='__main__':unittest.main()
