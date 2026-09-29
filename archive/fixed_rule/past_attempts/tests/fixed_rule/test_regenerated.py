"""Projection of the COMPLETE evaluator; static Address is an explicit limit."""
from dataclasses import fields,replace
import random
import unittest
import numpy as np
from gacsca.fixed_rule import regenerative,regenerative_block,regenerated as rule
from gacsca.fixed_rule.regenerated_native import library,dense_step,run


def random_cell(rng):
    return rule.Cell(**{name:rng.randrange(1<<width) for name,width in rule.SCHEMA})


def active_ring():
    g=regenerative_block.layout()
    pc,op=next((i,op) for i,op in enumerate(g.instructions)
               if i>=2*regenerative.WIDTH+2 and op.kind==regenerative.GATE and op.a!=op.b and min(op.a,op.b)>1)
    return (rule.Cell(address=op.a,bit=1,head=1,phase=regenerative.READ_B,
                      rb=op.a,rd=op.b,value=1,pc=pc-1),
            rule.Cell(address=op.b,bit=1),
            rule.Cell(address=g.memory_count+pc),
            rule.Cell(address=op.d,rp_target=op.a,rp_bit=0,rp_cross=1,rp_valid=1))


class RegeneratedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib=library()

    def test_raw_physical_schema_has_no_program_records(self):
        self.assertEqual(rule.WIDTH,125)
        self.assertEqual(regenerative.WIDTH,194)
        self.assertEqual(tuple(f.name for f in fields(rule.Cell)),tuple(n for n,_ in rule.SCHEMA))
        self.assertTrue(set(rule.STATIC).isdisjoint(rule.COL))
        self.assertFalse(rule.rom().flags.writeable)
        self.assertEqual(rule.identity()['rom_sha256'],
                         'e2393c393706dcaf5c81f275398c4780a1c58e76dd81edc2fe946f2401f0e2fe')
        rng=random.Random(391)
        for _ in range(50):
            cell=random_cell(rng)
            self.assertEqual(rule.decode_cell(rule.encode_cell(cell)),cell)
            self.assertEqual(rule.project(rule.lift(cell)),cell)

    def test_complete_description_and_local_commuting_relation(self):
        rng=random.Random(392)
        triples=[tuple(random_cell(rng) for _ in range(3)) for _ in range(100)]
        # Bias into actual ROM regions, including instruction and boundary rows.
        addresses=(0,1,regenerative_block.layout().info_start,regenerative_block.layout().memory_count,
                   len(rule.rom())-1,len(rule.rom()),65535)
        for address in addresses:
            for phase in range(8):
                c=replace(random_cell(rng),address=address,phase=phase,head=1)
                triples.append((c,c,c))
        circuit=regenerative.self_description()
        for row in triples:
            lifted=tuple(rule.lift(cell) for cell in row)
            expected=regenerative.local_step(*lifted)
            inputs=tuple(bit for cell in lifted for bit in regenerative.encode_cell(cell))
            self.assertEqual(regenerative.decode_cell(circuit.evaluate(inputs)),expected)
            regenerated=rule.local_step(*row)
            self.assertEqual(rule.lift(regenerated),expected)
            native=rule.cells_from_array(dense_step(rule.array_from_cells(row),self.lib))[1]
            self.assertEqual(native,regenerated)

    def test_projection_does_not_cover_address_repair_automatically(self):
        # Printed program projection needs regeneration after an Address change.
        # Preserve a concrete failed extension rather than assuming conjugacy.
        address=regenerative_block.layout().memory_count
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
        q=regenerative_block.layout().colony_cells
        np.testing.assert_array_equal(physical[:q],other[:q])
        np.testing.assert_array_equal(physical[2*q:],other[2*q:])
        # Decoder refuses silently omitted/mismatched regenerated program fields.
        wrong=physical.copy()
        start=regenerative_block.layout().info_start
        wrong[start,rule.COL['bit']]^=1  # derived opcode bit of encoded lifted cell
        with self.assertRaisesRegex(ValueError,'static program'):
            rule.decode(wrong)

    def test_two_macrosteps_with_one_compiled_regenerated_rule(self):
        reference=active_ring()
        physical=rule.encode(reference)
        before=rule.identity()
        values=[reference[1].bit]
        for _ in range(2):
            run(physical,regenerative_block.layout().period_ticks,self.lib)
            reference=rule.step_ring(reference)
            self.assertEqual(rule.decode(physical),reference)
            self.assertTrue(rule.check_boundary(physical))
            values.append(reference[1].bit)
        self.assertEqual(values,[1,1,0])
        self.assertEqual(rule.identity(),before)

    def test_regeneration_after_changed_hold_address_and_corrupt_static_record(self):
        # Diagnostic stage fixture, NOT an evolved Address-repair claim. All
        # subsequent regeneration and commit use literal physical transitions.
        g=regenerative_block.layout()
        targets=(0,g.memory_count,g.colony_cells-1,65535)
        old=rule.Cell(address=g.memory_count+1,pc=57000,ra=4321,rb=6543,
                      rd=12345,phase=7,lp_target=9876,lp_valid=1,value=1)
        state=rule.encode((old,)*len(targets))
        _,rows=g.schedule()
        cut=rows[g.regeneration_instruction-1][-1]
        # Install an explicit checkpoint at the first regeneration fetch, with
        # deliberately stale output record. This tests the primitive stage only.
        p=g.memory_count+g.regeneration_instruction
        phase_start=rows[g.regeneration_instruction][0]-1
        for region,target in enumerate(targets):
            base=region*g.colony_cells
            state[base,rule.COL['head']]=0
            state[base+p,rule.COL['head']]=1
            state[base+p,rule.COL['pc']]=g.regeneration_instruction
            staged=replace(rule.lift(old),address=target)
            staged=replace(staged,kind=7,index=65535,a=65535,b=65535,d=65535,first=1,last=1)
            state[base+g.hold_start:base+g.hold_start+regenerative.WIDTH,rule.COL['bit']]=regenerative.encode_cell(staged)
        self.assertGreater(phase_start,cut)
        run(state,g.period_ticks-phase_start,self.lib)
        self.assertEqual(rule.decode(state),tuple(replace(old,address=target) for target in targets))
        self.assertTrue(rule.check_boundary(state))

    def test_self_simulates_new_metadata_controller_transition(self):
        # Four independent raw upper heads exercise READ_META and first-site
        # fallback/reflection in the self-evaluated complete description.
        g=regenerative_block.layout()
        reference=(rule.Cell(address=5,head=1,phase=regenerative.READ_META,
                             rd=5,ra=40,rb=3,value=1),
                   rule.Cell(address=0,head=1,direction=1,phase=regenerative.READ_META,
                             rd=65535,ra=99,rb=3,value=1),
                   rule.Cell(address=g.colony_cells-1,head=1,phase=regenerative.READ_META,
                             rd=g.colony_cells-1,ra=21,rb=68,value=1),
                   rule.Cell(address=0,head=1,direction=1,phase=regenerative.WAIT_META,
                             rd=13,value=1))
        expected=rule.step_ring(reference)
        self.assertNotEqual(expected,reference)
        state=rule.encode(reference)
        run(state,g.period_ticks,self.lib)
        self.assertEqual(rule.decode(state),expected)
        self.assertTrue(rule.check_boundary(state))


if __name__=='__main__':
    unittest.main()
