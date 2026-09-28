"""Raw-state closure and literal timing of the regenerative evaluator."""
from dataclasses import fields, replace
import random
import unittest
import numpy as np
from gacsca.fixed_rule import regenerative as rule
from gacsca.fixed_rule.regenerative_native import (
    COL, array_from_cells, cells_from_array, library, dense_step, run)


def random_cell(rng):
    return rule.Cell(**{name:rng.randrange(1 << width) for name,width in rule.SCHEMA})


class RegenerativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib=library()

    def test_complete_schema_and_description_identity(self):
        self.assertEqual(rule.WIDTH,194)
        self.assertEqual(rule.STATIC_WIDTH,69)
        self.assertEqual(tuple(f.name for f in fields(rule.Cell)),tuple(n for n,_ in rule.SCHEMA))
        self.assertEqual(rule.self_description().digest(),
                         '09dde36b30d6c3a5220540bbe782809dd1b7276387ea737553f3d9d3f944f359')
        rng=random.Random(891)
        for _ in range(50):
            c=random_cell(rng)
            self.assertEqual(rule.decode_cell(rule.encode_cell(c)),c)

    def test_complete_circuit_scalar_native_all_controller_branches(self):
        rng=random.Random(892)
        cases=[tuple(random_cell(rng) for _ in range(3)) for _ in range(200)]
        for phase in range(8):
            for kind in range(8):
                for direction in range(2):
                    for value in range(2):
                        c=rule.Cell(kind=kind,index=7,head=1,phase=phase,pc=7,
                            ra=7,rb=7,rd=7,bit=1,value=value,direction=direction,
                            first=1,last=1,a=2,b=4,d=6,address=7,
                            lp_target=7,lp_valid=1,rp_target=7,rp_bit=1,rp_cross=1,rp_valid=1)
                        cases.extend(((c,c,c),(replace(c,last=0),rule.Cell(),rule.Cell())))
        for selector in (*range(70),127,128,65535):
            for value in (0,1):
                for kind in range(8):
                    c=replace(random_cell(rng),kind=kind,head=1,phase=rule.READ_META,
                              rd=7,address=7,rb=selector,value=value,first=1,last=1)
                    cases.append((c,c,c))
        circuit=rule.self_description()
        for row in cases:
            expected=rule.local_step(*row)
            inputs=tuple(bit for cell in row for bit in rule.encode_cell(cell))
            self.assertEqual(rule.decode_cell(circuit.evaluate(inputs)),expected,row)
            self.assertEqual(cells_from_array(dense_step(array_from_cells(row),self.lib))[1],expected,row)

    def test_sparse_dense_arbitrary_raw_parity_and_locality(self):
        rng=random.Random(893)
        for n in (1,2,3,8,17):
            reference=tuple(random_cell(rng) for _ in range(n))
            sparse=dense=array_from_cells(reference)
            sparse=sparse.copy()
            for _ in range(30):
                run(sparse,1,self.lib); dense=dense_step(dense,self.lib)
                reference=rule.step_ring(reference)
                np.testing.assert_array_equal(sparse,dense)
                self.assertEqual(cells_from_array(sparse),reference)
        original=[random_cell(rng) for _ in range(15)]
        expected=rule.local_step(*original[6:9])
        for j in set(range(15))-{6,7,8}:
            changed=list(original); changed[j]=random_cell(rng)
            self.assertEqual(rule.step_ring(changed)[7],expected)
            self.assertEqual(cells_from_array(dense_step(array_from_cells(changed),self.lib))[7],expected)

    def test_meta_fixed_duration_for_all_targets_and_selectors(self):
        # Full scan reads locally, waits for the next first-site reflection,
        # then writes. The queried Address never controls instruction duration.
        q,p,h=11,8,4
        duration=1+4*q+h-p
        for target in (*range(q),q,65535):
            for selector in (*range(70),127,128,65535):
                cells=[rule.Cell(kind=rule.MEM,index=j,address=j,first=int(j==0),last=int(j==q-1),
                                 a=100+j,b=200+j,d=300+j) for j in range(q)]
                cells[p]=replace(cells[p],kind=rule.META,index=0,a=h,b=selector,head=1,rd=target)
                expected=rule.static_bit(cells[target],selector) if target<q else rule.fallback_bit(target,selector)
                cells[h]=replace(cells[h],bit=1-expected)
                state=array_from_cells(cells)
                run(state,duration-1,self.lib)
                self.assertEqual(int(state[h,COL['bit']]),1-expected)
                head=cells_from_array(state)[h]
                self.assertEqual((head.head,head.direction,head.phase,head.rd,head.value),(1,0,rule.WRITE,h,expected))
                run(state,1,self.lib)
                self.assertEqual(int(state[h,COL['bit']]),expected)
                head=cells_from_array(state)[h+1]
                self.assertEqual((head.head,head.phase,head.pc),(1,rule.FETCH,1))

    def test_clear_load_assemble_address_from_local_bit_reads(self):
        # Distinct bit pattern distinguishes bit order and accumulation.
        value=0x96B3
        cells=[rule.Cell(index=j,address=j,bit=(value>>j)&1,first=int(j==0)) for j in range(16)]
        cells.append(rule.Cell(kind=rule.CLEAR,index=0,address=16,head=1,rd=65535))
        for j in range(16):
            cells.append(rule.Cell(kind=rule.LOAD,index=j+1,a=15-j,address=17+j,last=int(j==15)))
        state=array_from_cells(cells)
        q=len(cells); phase=16; duration=0
        for i,targets in enumerate(((16,),)+tuple((17+j,15-j) for j in range(16))):
            for target in targets:
                duration+=(target-phase)%(2*q)+1; phase=(target+1)%(2*q)
        run(state,duration,self.lib)
        head=next(c for c in cells_from_array(state) if c.head)
        self.assertEqual((head.rd,head.pc,head.phase),(value,17,rule.FETCH))


if __name__=='__main__': unittest.main()
