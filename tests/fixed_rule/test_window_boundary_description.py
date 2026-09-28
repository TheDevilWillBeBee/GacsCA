"""Exact constant/word-edge cases that sparse random raw tests rarely hit."""
from dataclasses import replace
import unittest
from gacsca.fixed_rule import window_rule as f
from gacsca.fixed_rule.window_core import array_from_cells,cells_from_array,dense_step,library


class WindowBoundaryDescriptionTests(unittest.TestCase):
    def test_colony_boundaries_and_32_bit_carries_in_complete_description(self):
        circuit=f.self_description();lib=library();cases=[]
        for address in (0,1,f.COLONY_CELLS-1,f.COLONY_CELLS,f.MASK):
            for crossed in (0,1):
                left=f.Cell(address=address,rp_valid=1,rp_cross=crossed,rp_bit=1,rp_target=f.MASK)
                right=f.Cell(address=address,lp_valid=1,lp_cross=crossed,lp_bit=0,lp_target=f.MASK)
                for kind in (f.MEM,f.PADDING_KIND):
                    cases.append((left,f.Cell(kind=kind,index=f.MASK,bit=1),right))
        for pc in (65535,0x7FFFFFFF,f.MASK):
            for kind,phase in ((f.CLEAR,f.FETCH),(f.WAIT,f.FETCH),(f.MEM,f.WRITE),(f.MEM,f.READ_LOAD)):
                for value in (0,f.MASK):
                    c=f.Cell(kind=kind,index=pc,head=1,phase=phase,pc=pc,ra=pc,
                             rd=pc if phase==f.WRITE else value,bit=1,value=1,last=1)
                    cases.append((c,c,c))
        for triple in cases:
            expected=f.local_step(*triple)
            described=f.decode_cell(circuit.evaluate(tuple(bit for c in triple for bit in f.encode_cell(c))))
            self.assertEqual(described,expected,triple)
            self.assertEqual(cells_from_array(dense_step(array_from_cells(triple),lib))[1],expected,triple)


if __name__=='__main__':unittest.main()
