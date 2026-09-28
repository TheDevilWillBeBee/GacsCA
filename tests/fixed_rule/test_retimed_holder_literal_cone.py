"""Shrinking windows must agree with full-ring physical evolution."""
import unittest
from dataclasses import replace
import numpy as np
from gacsca.fixed_rule import retimed_holder_literal_cone as cone,retimed_holder_rule as f,retimed_holder_projected as r,retimed_holder_program as p
from gacsca.fixed_rule import retimed_holder_endpoint_image_array as vector


class LiteralCone(unittest.TestCase):
    def test_complete_image_accessor(self):
        g=p.layout();bank=np.arange(2*(g.memory_count+5),dtype=np.uint64).reshape(2,-1);signals=np.array([[1,0],[0,1]],dtype=np.uint64)
        image=cone.BankImage(bank,signals);expected=vector.render(bank,signals,0)
        positions=np.array([-7,-1,0,1,3,5,g.memory_count-1,g.memory_count,f.Q-5,f.Q-1,f.Q,f.Q+3,2*f.Q+1])
        np.testing.assert_array_equal(image.cells(positions),expected[positions%image.size])

    def test_shrinking_cone_matches_complete_ring(self):
        size=521;cells=tuple(r.Cell(address=i%f.Q,age=99,s2_data=i+1) for i in range(size))
        base=np.array([f.encode_cell(r.lift(x)) for x in cells],dtype=np.uint64)
        changes={-1:replace(cells[-1],address=17,age=f.U-1,s2_rb=123,signal=31),0:replace(cells[0],s0_head=1,s0_phase=3)}
        result=cone.evolve(lambda positions:base[positions%size],changes,size=size,ticks=4)
        actual=base.copy();healthy=base.copy()
        for pos,cell in changes.items():actual[pos%size]=f.encode_cell(r.lift(cell))
        for _ in range(result['ticks']):actual=cone.step(actual);healthy=cone.step(healthy)
        positions=(np.arange(len(result['actual']))+result['left'])%size
        np.testing.assert_array_equal(result['actual'],actual[positions]);np.testing.assert_array_equal(result['healthy'],healthy[positions])
        self.assertEqual(result['rejoined'],np.array_equal(actual,healthy))

    def test_raw_controller_fields_are_retained(self):
        size=521;base=np.array([f.encode_cell(r.lift(r.Cell(address=i,age=99))) for i in range(size)],dtype=np.uint64)
        changes={}
        for pos in (199,200,201):
            prefix=f's{2-(pos-200)}_'
            changes[pos]=r.Cell(address=pos,age=99,**{prefix+'rb':123,prefix+'head':1,prefix+'phase':2,prefix+'pc':1})
        result=cone.evolve(lambda positions:base[positions%size],changes,size=size,ticks=1)
        self.assertFalse(result['rejoined']);self.assertTrue(any(name.endswith('_rb') for name in result['trace'][0]['fields']))

    def test_invalid_domains_reject_before_evolution(self):
        with self.assertRaises(ValueError):cone.evolve(lambda x:None,{0:r.Cell()},size=100,ticks=12)
        with self.assertRaises(ValueError):cone.evolve(lambda x:None,{0:r.Cell()},size=1000,ticks=12,max_cells=1)

if __name__=='__main__':unittest.main()
