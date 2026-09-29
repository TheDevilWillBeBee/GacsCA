from dataclasses import replace
import unittest
import numpy as np
from gacsca.fixed_rule import small_holder_reset_encoding as reset
from gacsca.fixed_rule import small_holder_projected as r, small_holder_rule as f
from gacsca.fixed_rule import small_holder_quotient as q, small_holder_program as p
from gacsca.fixed_rule import small_holder_native as native
from experiments.fixed_rule.prove_small_holder_reset_encoding import prove


class ResetEncoding(unittest.TestCase):
    def test_complete_raw_reset_certificate(self):
        result=prove();self.assertTrue(result['passed']);self.assertEqual(result['complete_raw_outputs'],154)
        self.assertEqual(result['arbitrary_complete_static_records'],7)

    def test_info_controller_and_signal_are_all_present(self):
        parent=r.Cell(address=30000,age=987,s2_head=1,s2_phase=3,s2_rd=321,s2_value=(1<<64)-1,f1=1,f2=1)
        encoded=reset.Encoding((parent,))
        words=tuple(encoded.logical(a).data for a in p.layout().info)
        self.assertEqual(words,f.encode_cell(r.lift(parent)))
        self.assertEqual(encoded.logical(0).head,1)
        self.assertEqual(encoded.logical(0).pc,p.layout().entries[0])
        self.assertEqual(encoded.logical(3).signal,4)
        self.assertEqual(encoded.logical(f.Q-3).signal,4)
        self.assertNotEqual(encoded.physical(0),replace(encoded.physical(0),s2_head=0))
        self.assertNotEqual(encoded.physical(3),replace(encoded.physical(3),signal=0))

    def test_reset_relation_at_rom_and_colony_boundaries(self):
        parents=(r.Cell(f1=1),r.Cell(f2=1,s2_value=123),r.Cell(f1=1,f2=1))
        encoded=reset.Encoding(parents)
        selected=(0,1,2,7,p.layout().info[0],p.layout().info[-1],p.layout().memory_count-1,p.layout().memory_count,p.layout().computation_cells-1,f.Q-6,f.Q-5,f.Q-1,f.Q,f.Q+3)
        from gacsca.fixed_rule.small_holder_initial import coherent_cell
        def old(pos):
            cell=q.decode_cell(encoded.array((pos,),age=0)[0]);a=pos%f.Q
            if (a<p.layout().memory_count or a>=f.Q-5) and a not in encoded.info:cell=replace(cell,data=0xDEAD1234)
            return cell
        for pos in selected:
            neighborhood=tuple(r.lift(coherent_cell(old,pos+j)) for j in f.NEIGHBORHOOD)
            actual=native.local_step(neighborhood)
            self.assertEqual(actual,encoded.physical(pos))

    def test_missing_controller_and_signal_fail_complete_verifier(self):
        model=reset.Encoding((r.Cell(f1=1,f2=1),))
        class Fake:
            colonies=1;age=1
            def logical_cells(self,positions):
                rows=model.array(positions)
                for i,pos in enumerate(positions):
                    if pos==0:rows[i,q.COL['head']]=0
                return q.cells_from_array(rows)
        with self.assertRaises(AssertionError):model.verify(Fake())
        class LostSignal(Fake):
            def logical_cells(self,positions):
                rows=model.array(positions);rows[:,q.COL['signal']]=0
                return q.cells_from_array(rows)
        with self.assertRaises(AssertionError):model.verify(LostSignal())

if __name__=='__main__':unittest.main()
