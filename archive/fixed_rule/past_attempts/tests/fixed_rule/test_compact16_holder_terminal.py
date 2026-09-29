"""Complete-memory and raw-controller obligations for compact endpoints."""
from dataclasses import replace
import json
from pathlib import Path
import unittest
import numpy as np
from gacsca.fixed_rule import compact16_holder_program as p, compact16_holder_rule as f
from gacsca.fixed_rule import compact16_holder_projected as r, compact16_holder_core as c
from gacsca.fixed_rule import compact16_holder_terminal_dag as dag, compact16_holder_terminal_reference as replay
from gacsca.fixed_rule import compact16_holder_terminal_image as image, compact16_holder_native as native
from gacsca.fixed_rule import compact16_holder_terminal_checks as checks
from experiments.fixed_rule.certify_compact16_holder_terminal_layout import certify
from experiments.fixed_rule.audit_compact16_holder_terminal import witness


class Terminal(unittest.TestCase):
    def test_partition_and_sparse_metadata(self):
        result=certify()
        self.assertEqual(sum(result['complete_memory_categories'].values()),3447)
        self.assertEqual(result['metadata_queries'],98)
        self.assertEqual(result['complete_memory_categories']['history'],2067)

    def test_changed_mask_controller_and_allocation_rejected(self):
        g=p.layout();start,end=g.stage_ranges[4]
        code=list(g.instructions);code[start]=replace(code[start],a=0)
        with self.assertRaises(AssertionError):certify(replace(g,instructions=tuple(code)))
        target=g.hold[f.COL['s2_pc']]
        at=next(i for i in range(start,end) if g.instructions[i].kind in c.ALU_KINDS and g.instructions[i].d==target)
        code=list(g.instructions);code[at]=replace(code[at],d=target+2)
        with self.assertRaises(AssertionError):certify(replace(g,instructions=tuple(code)))
        wires=list(g.wires);wires[p.compiled_description().inputs]+=1
        with self.assertRaises(AssertionError):certify(replace(g,wires=tuple(wires)))

    def test_equal_decodes_do_not_erase_scratch(self):
        result=witness()
        self.assertTrue(result['equal_decoded_outputs'])
        self.assertEqual(result['different_retained_bank_words'],28)

    def test_complete_physical_commit(self):
        parent=r.Cell(address=f.Q+17,age=0xffffffff,s2_head=1,s2_pc=39,s2_value=123)
        expected=dag.terminal((parent,));actual=replay.terminal((parent,))
        for key in expected:np.testing.assert_array_equal(actual[key],expected[key])
        before=image.Image(expected,precommit=True);after=image.Image(expected,precommit=False)
        selected={0,1,3,5,f.Q-5,f.Q-3,f.Q-1,p.layout().memory_count-1,p.layout().computation_cells-1}
        selected.update(p.layout().info);selected.update(p.layout().hold)
        for at in sorted(selected):
            neighborhood=tuple(r.lift(before.cell(at+j)) for j in f.NEIGHBORHOOD)
            self.assertEqual(native.local_step(neighborhood),r.lift(after.cell(at)),at)

    def test_saved_physical_endpoints_and_mutations(self):
        path=Path('figs/fixed_rule/compact16_holder_endpoint_v1.npz')
        with np.load(path,allow_pickle=False) as saved:
            parents=r.cells_from_array(saved['initial_upper'])
            expected=dag.terminal(parents)
            state={key[len('period1_precommit_'):]:saved[key].copy() for key in saved.files if key.startswith('period1_precommit_')}
            checks.check(state,expected,age=f.U-1,time=f.U-1)
            state['bank'][0,p.MASK_ADDRESS]^=np.uint64(1)
            with self.assertRaises(AssertionError):checks.check(state,expected,age=f.U-1,time=f.U-1)


if __name__=='__main__':unittest.main()
