"""Independent vector reconstruction matches all raw fields of scalar images."""
import unittest
import numpy as np
from gacsca.fixed_rule import retimed_holder_endpoint_image_array as vector,retimed_holder_terminal_image as scalar,retimed_holder_terminal_dag as dag
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_projected as r,retimed_holder_program as p
from experiments.fixed_rule.run_retimed_holder_cpu_periods import parents


class ImageArray(unittest.TestCase):
    def test_full_raw_reconstruction_at_all_interfaces(self):
        terminal=dag.terminal(parents(3));g=p.layout()
        for precommit in (False,True):
            key='precommit_bank' if precommit else 'committed_bank';age=f.U-1 if precommit else 0
            actual=vector.render(terminal[key],terminal['signals'],age)
            expected=scalar.Image(terminal,precommit=precommit)
            for col in range(3):
                for anchor in (0,g.info[0],g.info[-1],g.memory_count,g.computation_cells,f.Q-3):
                    for offset in range(-3,4):
                        pos=(col*f.Q+anchor+offset)%expected.size
                        np.testing.assert_array_equal(actual[pos],f.encode_cell(r.lift(expected.cell(pos))))

    def test_resource_and_domain_guards(self):
        terminal=dag.terminal((r.Cell(),));bank=terminal['committed_bank'];signals=terminal['signals']
        with self.assertRaises(ValueError):vector.render(bank,signals,1)
        with self.assertRaises(ValueError):vector.render(bank,signals,0,max_bytes=1)
        with self.assertRaises(ValueError):vector.render(bank,signals+2,0)


if __name__=='__main__':unittest.main()
