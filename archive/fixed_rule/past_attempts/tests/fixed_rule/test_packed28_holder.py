"""Executable checks for the physical Q8192 packed self-ROM candidate."""
from dataclasses import replace
import hashlib
import random
import tempfile
import unittest
from pathlib import Path

from gacsca.fixed_rule import packed28_holder_core as c
from gacsca.fixed_rule import packed28_holder_initial as initial
from gacsca.fixed_rule import packed28_holder_program as p
from gacsca.fixed_rule import packed28_holder_projected as r
from gacsca.fixed_rule import packed28_holder_rule as f
from experiments.fixed_rule.certify_packed28_holder_rom import Checker, check
from experiments.fixed_rule.run_packed28_holder_cpu_general_periods import run


class Packed28Holder(unittest.TestCase):
    def test_fixed_geometry_and_self_description(self):
        g=p.layout();rom=p.base_rom()
        self.assertEqual((f.Q,f.U,f.WIDTH,f.FIELDS),(8192,1<<28,4090,154))
        self.assertEqual(f.NEIGHBORHOOD,tuple(range(-7,8)))
        self.assertEqual(f.self_description().inputs,15*f.FIELDS)
        self.assertEqual(len(rom),g.computation_cells)
        self.assertEqual((len(g.instructions),len(g.packed.rows)),(10606,4213))
        self.assertLess(g.computation_cells+5,f.Q)
        self.assertTrue(g.timing_certificate()['fits'])
        self.assertEqual(g.packed.decode(),g.instructions)
        self.assertTrue(any(row.kind==c.PACK3 for row in g.packed.rows))
        identity=r.identity();digest=f.self_description().digest()
        rom_digest=hashlib.sha256(rom.tobytes()).hexdigest()
        for depth in (1,2,3):
            self.assertEqual(initial.physical_cells(1,depth),f.Q**depth)
            self.assertEqual(r.identity(),identity)
            self.assertEqual(f.self_description().digest(),digest)
            self.assertEqual(hashlib.sha256(p.base_rom().tobytes()).hexdigest(),rom_digest)

    def test_full_raw_description_including_invalid_controller_states(self):
        rng=random.Random(2026092819)
        for _ in range(12):
            cells=tuple(f.Cell(**{name:rng.getrandbits(width)
                                  for name,width in f.SCHEMA})
                        for _ in f.NEIGHBORHOOD)
            for cell in cells:
                self.assertEqual(f.decode_cell(f.encode_cell(cell)),cell)
            words=tuple(word for cell in cells for word in f.encode_cell(cell))
            self.assertEqual(f.self_description().evaluate(words),
                             f.encode_cell(f.local_step(cells)))
        with self.assertRaises(ValueError):f.local_step(tuple(c.Cell() for _ in range(14)))
        with self.assertRaises(ValueError):f.local_step(tuple(c.Cell() for _ in range(16)))

    def test_packed_slots_are_literal_local_fetches(self):
        g=p.layout();row=next(row for row in g.packed.rows if row.kind==c.PACK3 and row.count==3)
        for slot in range(3):
            pc=row.micro_pc+slot;at=g.physical_position(pc);op=g.instructions[pc]
            self.assertEqual(int(p.base_rom()[at,0]),c.PACK3)
            def logical(position):
                values=dict(r.record(position%f.Q),address=position%f.Q,
                            age=c.RESET_AGES[4]+100)
                if position==at:values.update(head=1,phase=c.FETCH,pc=pc)
                return c.Cell(**values)
            neighbors=tuple(r.lift(initial.coherent_cell(logical,at+1+j))
                            for j in f.NEIGHBORHOOD)
            actual=f.local_step(neighbors)
            self.assertEqual(p.compiled_description().evaluate(
                tuple(word for cell in neighbors for word in f.encode_cell(cell))),
                f.encode_cell(actual))
            self.assertEqual((actual.s2_head,actual.s2_phase,actual.s2_pc),
                             (1,c.READ_A,pc))
            self.assertEqual((actual.s2_ra,actual.s2_rb,actual.s2_rd),
                             (op.a,op.b,op.d))

    def test_own_physical_rom_dataflow_and_tamper(self):
        receipt=check()
        self.assertEqual(receipt['dataflow']['complete_raw_outputs_per_colony'],f.FIELDS)
        self.assertEqual(receipt['dataflow']['colonies'],15)
        self.assertLess(receipt['controller_path_ticks'],f.U)
        g=p.layout();rom=p.base_rom().copy()
        row=next(row for row in g.packed.rows if row.kind==c.PACK3 and row.count==3)
        rom[g.physical_position(row.micro_pc),2]^=1<<28
        with self.assertRaises(AssertionError):Checker(rom).check()

    def test_complete_physical_period_changes_decoded_upper_state(self):
        with tempfile.TemporaryDirectory() as temporary:
            receipt=run(1,1,Path(temporary)/'period.npz')
        self.assertTrue(receipt['passed'])
        self.assertEqual(receipt['physical_ticks'],f.U)
        self.assertGreater(receipt['period_results'][0]['changed_projected_words'],0)
        self.assertEqual(receipt['period_results'][0]['full_entry_relation']['validated_sites'],f.Q)
        self.assertEqual(receipt['metrics']['packets_dropped'],0)


if __name__=='__main__':unittest.main()
