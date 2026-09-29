"""Projection of the COMPLETE evaluator; static Address is an explicit limit."""
from dataclasses import fields,replace
import random
import unittest
import numpy as np
from gacsca.fixed_rule import addressed,addressed_block,projected as rule
from gacsca.fixed_rule.projected_native import library,dense_step,run


def random_cell(rng):
    return rule.Cell(**{name:rng.randrange(1<<width) for name,width in rule.SCHEMA})


def active_ring():
    g=addressed_block.layout()
    pc,op=next((i,op) for i,op in enumerate(g.instructions)
               if i>=2*addressed.WIDTH+2 and op.kind==addressed.GATE and op.a!=op.b and min(op.a,op.b)>1)
    return (rule.Cell(address=op.a,bit=1,head=1,phase=addressed.READ_B,
                      rb=op.a,rd=op.b,value=1,pc=pc-1),
            rule.Cell(address=op.b,bit=1),
            rule.Cell(address=g.memory_count+pc),
            rule.Cell(address=op.d,rp_target=op.a,rp_bit=0,rp_cross=1,rp_valid=1))


class ProjectedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib=library()

    def test_raw_physical_schema_has_no_program_records(self):
        self.assertEqual(rule.WIDTH,125)
        self.assertEqual(addressed.WIDTH,193)
        self.assertEqual(tuple(f.name for f in fields(rule.Cell)),tuple(n for n,_ in rule.SCHEMA))
        self.assertTrue(set(rule.STATIC).isdisjoint(rule.COL))
        self.assertFalse(rule.rom().flags.writeable)
        self.assertEqual(rule.identity()['rom_sha256'],
                         'eafb3cb1da192aef716370a821843a62864a0d30374b514e38cdae54b879c71b')
        rng=random.Random(391)
        for _ in range(50):
            cell=random_cell(rng)
            self.assertEqual(rule.decode_cell(rule.encode_cell(cell)),cell)
            self.assertEqual(rule.project(rule.lift(cell)),cell)

    def test_complete_description_and_local_commuting_relation(self):
        rng=random.Random(392)
        triples=[tuple(random_cell(rng) for _ in range(3)) for _ in range(100)]
        # Bias into actual ROM regions, including instruction and boundary rows.
        addresses=(0,1,addressed_block.layout().info_start,addressed_block.layout().memory_count,
                   len(rule.rom())-1,len(rule.rom()),65535)
        for address in addresses:
            for phase in range(8):
                c=replace(random_cell(rng),address=address,phase=phase,head=1)
                triples.append((c,c,c))
        circuit=addressed.self_description()
        for row in triples:
            lifted=tuple(rule.lift(cell) for cell in row)
            expected=addressed.local_step(*lifted)
            inputs=tuple(bit for cell in lifted for bit in addressed.encode_cell(cell))
            self.assertEqual(addressed.decode_cell(circuit.evaluate(inputs)),expected)
            projected=rule.local_step(*row)
            self.assertEqual(rule.lift(projected),expected)
            native=rule.cells_from_array(dense_step(rule.array_from_cells(row),self.lib))[1]
            self.assertEqual(native,projected)

    def test_projection_does_not_cover_address_repair_automatically(self):
        # Printed program projection needs regeneration after an Address change.
        # Preserve a concrete failed extension rather than assuming conjugacy.
        address=addressed_block.layout().memory_count
        cell=rule.Cell(address=address)
        lifted=rule.lift(cell)
        stale=replace(lifted,address=address+1)
        self.assertNotEqual(stale,rule.lift(rule.project(stale)))
        self.assertNotEqual(stale.index,rule.lift(rule.project(stale)).index)

    def test_sparse_dense_parity_and_exterior_locality(self):
        rng=random.Random(393)
        for n in (1,2,3,9):
            reference=tuple(random_cell(rng) for _ in range(n))
            sparse=rule.array_from_cells(reference)
            dense=sparse.copy()
            for _ in range(20):
                run(sparse,1,self.lib)
                dense=dense_step(dense,self.lib)
                reference=rule.step_ring(reference)
                np.testing.assert_array_equal(sparse,dense)
                self.assertEqual(rule.cells_from_array(sparse),reference)
        cells=[random_cell(rng) for _ in range(13)]
        expected=rule.local_step(*cells[5:8])
        for position in set(range(13))-{5,6,7}:
            changed=list(cells)
            changed[position]=random_cell(rng)
            self.assertEqual(rule.step_ring(changed)[6],expected)
            self.assertEqual(rule.cells_from_array(dense_step(rule.array_from_cells(changed),self.lib))[6],expected)

    def test_projection_encoding_retains_all_raw_controller_bits(self):
        reference=active_ring()
        physical=rule.encode(reference)
        self.assertEqual(rule.decode(physical),reference)
        self.assertTrue(rule.check_boundary(physical))
        changed=list(reference)
        changed[1]=replace(changed[1],pc=65535,lp_target=40000)
        other=rule.encode(changed)
        q=addressed_block.layout().colony_cells
        np.testing.assert_array_equal(physical[:q],other[:q])
        np.testing.assert_array_equal(physical[2*q:],other[2*q:])
        # Decoder refuses silently omitted/mismatched projected program fields.
        wrong=physical.copy()
        start=addressed_block.layout().info_start
        wrong[start,rule.COL['bit']]^=1  # derived opcode bit of encoded lifted cell
        with self.assertRaisesRegex(ValueError,'static program'):
            rule.decode(wrong)

    def test_two_macrosteps_with_one_compiled_projected_rule(self):
        reference=active_ring()
        physical=rule.encode(reference)
        before=rule.identity()
        values=[reference[1].bit]
        for _ in range(2):
            run(physical,addressed_block.layout().period_ticks,self.lib)
            reference=rule.step_ring(reference)
            self.assertEqual(rule.decode(physical),reference)
            self.assertTrue(rule.check_boundary(physical))
            values.append(reference[1].bit)
        self.assertEqual(values,[1,1,0])
        self.assertEqual(rule.identity(),before)


if __name__=='__main__':
    unittest.main()
