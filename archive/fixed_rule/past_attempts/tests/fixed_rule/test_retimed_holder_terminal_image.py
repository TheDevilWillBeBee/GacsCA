"""Literal local commit of complete formula images; raw controller preserved."""
import unittest
from gacsca.fixed_rule import retimed_holder_terminal_dag as dag,retimed_holder_terminal_image as image
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_projected as r,retimed_holder_program as p
from experiments.fixed_rule.run_retimed_holder_cpu_periods import parents


class Image(unittest.TestCase):
    def test_literal_commit_at_all_layout_interfaces(self):
        expected=dag.terminal(parents(15));before=image.Image(expected,precommit=True);after=image.Image(expected,precommit=False);g=p.layout()
        addresses={0,1,2,3,4,5,6,f.Q//2,g.computation_cells-1,g.computation_cells,f.Q-6,f.Q-5,f.Q-3,f.Q-1}
        for at in (g.info[0],g.info[-1],g.hold[-1],g.memory_count-6,g.memory_count):addresses.update(at+d for d in range(-2,3))
        for col in (0,7,14):
            for a in addresses:
                pos=col*f.Q+a
                actual=r.local_step(tuple(before.cell(pos+d) for d in f.NEIGHBORHOOD))
                self.assertEqual(actual,after.cell(pos),(col,a))

    def test_full_raw_info_includes_active_controller(self):
        top=parents(15);expected=dag.terminal(top);before=image.Image(expected,precommit=True)
        for col,parent in enumerate(top):
            decoded=f.decode_cell(tuple(before.cell(col*f.Q+a).s2_data for a in p.layout().info))
            self.assertEqual(decoded,r.lift(parent))
        self.assertTrue(any(getattr(parent,name) for parent in top for name,_ in r.SCHEMA if name.endswith('_head')))


if __name__=='__main__':unittest.main()
