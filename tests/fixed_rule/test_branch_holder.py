"""Regression and negative checks for one fixed Flag-only early branch."""
from dataclasses import replace
import hashlib
import random
import unittest

from gacsca.fixed_rule import branch_holder_rule as f, branch_holder_core as c
from gacsca.fixed_rule import branch_holder_program as p
from gacsca.fixed_rule import branch_holder_projected as r
from gacsca.fixed_rule import branch_holder_initial as initial
from gacsca.fixed_rule import and_holder_rule as previous
from experiments.fixed_rule.certify_branch_holder_rom import Checker, check, equivalence


class BranchHolder(unittest.TestCase):
    def test_fixed_rule_identity_and_resources(self):
        self.assertEqual((f.Q,f.U,f.WIDTH,f.FIELDS),(16384,1<<30,4090,154))
        self.assertEqual(f.SCHEMA,previous.SCHEMA)
        self.assertEqual(f.NEIGHBORHOOD,tuple(range(-7,8)))
        self.assertEqual(c.BRANCH_THIRD,15)
        self.assertNotIn(c.BRANCH_THIRD,(*c.ALU_KINDS,c.HALT,c.IF_THIRD))
        self.assertNotEqual(f.self_description().digest(),previous.self_description().digest())
        g=p.layout()
        self.assertEqual(g.instructions[g.branch_instruction].kind,c.BRANCH_THIRD)
        self.assertEqual(g.instructions[g.branch_instruction].a,g.signal_entry)
        self.assertLess(g.computation_cells+5,f.Q)
        self.assertTrue(g.timing_certificate()['fits'])

    def test_full_raw_local_dynamics_and_description(self):
        rng=random.Random(2026092831)
        cases=[tuple(f.Cell(**{name:rng.getrandbits(width)
                               for name,width in f.SCHEMA})
                     for _ in f.NEIGHBORHOOD) for _ in range(6)]
        for age in (*c.RESET_AGES,*c.VOTE_AGES,c.CAPTURE_AGE,f.U-1):
            cases.append(tuple(r.lift(r.Cell(address=(f.Q-7+j)%f.Q,age=age))
                               for j in f.NEIGHBORHOOD))
        for cells in cases:
            words=tuple(word for cell in cells for word in f.encode_cell(cell))
            self.assertEqual(p.compiled_description().evaluate(words),
                             f.encode_cell(f.local_step(cells)))
        self.assertEqual(equivalence()['complete_raw_outputs'],f.FIELDS)

    def test_branch_controller_moves_physically_at_both_ages(self):
        g=p.layout();pc=g.branch_instruction;at=g.memory_count+pc
        for age,target in ((c.VOTE_AGES[0]+100,g.signal_entry),
                           (c.RESET_AGES[4]+100,pc+1)):
            old=c.Cell(**dict(r.record(at),address=at,age=age,
                              head=1,phase=c.FETCH,pc=pc))
            self.assertEqual(c.advance(old)['pc'],target)
            def logical(position):
                values=dict(r.record(position%f.Q),address=position%f.Q,age=age)
                if position==at:values.update(head=1,phase=c.FETCH,pc=pc)
                return c.Cell(**values)
            for holder in range(at-1,at+4):
                neighbors=tuple(r.lift(initial.coherent_cell(logical,holder+j))
                                for j in f.NEIGHBORHOOD)
                actual=f.local_step(neighbors)
                slot=at+1-holder+2
                self.assertEqual(getattr(actual,f's{slot}_head'),1)
                self.assertEqual(getattr(actual,f's{slot}_pc'),target)
                self.assertEqual(getattr(actual,f's{slot}_phase'),c.FETCH)

    def test_rom_dynamics_and_wrong_branch_target_detected(self):
        receipt=check()
        self.assertTrue(receipt['dataflow']['early_only_flags'])
        self.assertEqual(receipt['dataflow']['complete_raw_outputs_per_colony'],f.FIELDS)
        self.assertLess(receipt['controller_path_ticks'],1<<29)
        g=p.layout();rom=p.base_rom().copy()
        rom[g.memory_count+g.branch_instruction,2]+=1
        with self.assertRaises(AssertionError):Checker(rom).check()

    def test_depth_is_initial_data_and_rom_stable(self):
        top=(r.Cell(address=7,age=19,s2_head=1,s2_phase=c.WRITE,
                    s2_pc=29,s2_value=0x1234),)
        identity=r.identity();sha=hashlib.sha256(p.base_rom().tobytes()).hexdigest()
        self.assertEqual(initial.decode_parent(top,1,0),top[0])
        self.assertEqual(initial.decode_parent(top,2,0),initial.cell_at(top,1,0))
        for depth in (1,2,3):
            self.assertEqual(initial.physical_cells(1,depth),f.Q**depth)
            self.assertEqual(r.identity(),identity)
            self.assertEqual(hashlib.sha256(p.base_rom().tobytes()).hexdigest(),sha)


if __name__=='__main__':unittest.main()
