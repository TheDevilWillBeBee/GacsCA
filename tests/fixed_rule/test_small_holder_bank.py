from dataclasses import replace
from functools import lru_cache
import random
import unittest
import numpy as np
from gacsca.fixed_rule import small_holder_bank as bank
from gacsca.fixed_rule import small_holder_bank_cuda as gpu
from gacsca.fixed_rule import small_holder_rule as f, small_holder_quotient as q
from gacsca.fixed_rule import small_holder_program as p, small_holder_native as native
from gacsca.fixed_rule import small_holder_core as c


class CompactBank(unittest.TestCase):
    def test_every_logical_and_raw_field_lossless_including_nonmemory_data(self):
        rng=random.Random(392)
        b=bank.Builder(2,17)
        positions=(0,100,p.layout().memory_count+13,f.Q-1,f.Q+7)
        cells={position:q.Cell(**{n:rng.getrandbits(w) for n,w in q.SCHEMA}) for position in positions}
        for pos,cell in cells.items(): b.set_logical(pos,cell)
        raw={n:rng.getrandbits(w) for n,w in f.SCHEMA}
        b.set_raw_fields(f.Q-2,**raw)
        s=b.freeze()
        for pos,cell in cells.items(): self.assertEqual(s.logical_cell(pos),cell)
        self.assertEqual(s.cell(f.Q-2),f.Cell(**raw))
        # Zero overrides must not fall back to nonzero bank data or metadata.
        b.set_raw_fields(100,s2_data=0,p3_a=0)
        self.assertEqual(b.freeze().cell(100).s2_data,0)
        b.data[0,100]^=np.uint64(77)
        self.assertEqual(s.logical_cell(100),cells[100])
        self.assertLess(s.storage_bytes,200000)
        self.assertFalse(s.data.flags.writeable)

    def test_rejects_malformed_and_overbudget_representations(self):
        with self.assertRaises(ValueError):bank.Builder(10000)
        b=bank.Builder(1);s=b.freeze()
        for keys,values in (([2,2],[0,0]),([2,1],[0,0]),([s.sites*f.FIELDS],[0]),([f.COL['age']],[f.U])):
            with self.assertRaises(ValueError):replace(s,raw_keys=np.array(keys,dtype=np.uint64),raw_values=np.array(values,dtype=np.uint64))
        with self.assertRaises(ValueError):b.set_logical(0,q.Cell().__dict__)
        with self.assertRaises(ValueError):b.set_raw_fields(0,missing_field=0)
        with self.assertRaises(ValueError):b.set_raw_fields(0,s2_head=2)
        with self.assertRaises(ValueError):b.set_raw_fields(f.Q,s2_head=1)
        with self.assertRaises(ValueError):s.cell(-1)

    def test_resident_reconstruction_and_full_rule_at_faults_and_clock_boundaries(self):
        rng=random.Random(402)
        positions=(0,1,2,97,100,103,p.layout().votes[3],p.layout().memory_count+5,f.Q-2,f.Q-1,f.Q,f.Q+3)
        ages=(0,f.VOTE_AGES[0],f.CAPTURE_AGE-1,f.WF_START,f.U-1)
        for age in ages:
            b=bank.Builder(2,age)
            for pos in positions:
                # Include flags/Wf, noncanonical clocks/addresses, arbitrary mail.
                fields={n:rng.getrandbits(w) for n,w in q.SCHEMA}
                b.set_logical(pos,q.Cell(**fields))
            for pos in (1,100,f.Q-1):
                b.set_raw_fields(pos,**{n:rng.getrandbits(w) for n,w in f.SCHEMA})
            s=b.freeze()
            read=lru_cache(None)(s.cell)
            with gpu.Resident(s) as world:
                self.assertLess(world.device_bytes,64*1024**2)
                got=world.evaluate(positions,reconstruct=True)
                expected=np.array([f.encode_cell(read(pos)) for pos in positions],dtype=np.uint64)
                np.testing.assert_array_equal(got,expected)
                new=world.evaluate(positions)
                for pos,row in zip(positions,new):
                    neighbors=tuple(read((pos+j)%s.sites) for j in f.NEIGHBORHOOD)
                    want=f.local_step(neighbors)
                    self.assertEqual(f.decode_cell(row.tolist()),want,(age,pos))
                    self.assertEqual(native.local_step(neighbors),want,(age,pos))
                # Both evaluation and reconstruction leave the resident input intact.
                np.testing.assert_array_equal(world.evaluate(positions,reconstruct=True),expected)
                with self.assertRaises(ValueError):world.evaluate([s.sites])
                with self.assertRaises(ValueError):world.evaluate([0]*257)
            with self.assertRaises(ValueError):world.evaluate([0])

    def test_active_write_and_broken_backup_are_not_dropped(self):
        b=bank.Builder(1,1)
        b.set_logical(100,q.Cell(address=100,age=1,data=11,head=1,phase=c.WRITE,rd=100,value=91))
        # A damaged physical holder carries independent control and metadata.
        b.set_raw_fields(102,s0_data=12345,s0_value=444,p1_a=555)
        s=b.freeze()
        with gpu.Resident(s) as world:
            positions=(98,99,100,101,102)
            out=world.evaluate(positions)
        for pos,row in zip(positions,out):
            want=native.local_step(tuple(s.cell((pos+j)%s.sites) for j in f.NEIGHBORHOOD))
            self.assertEqual(f.decode_cell(row.tolist()),want)
        self.assertEqual(int(out[2,f.COL['s2_data']]),91)
        self.assertNotEqual(int(out[2,f.COL['s2_head']]),s.cell(100).s2_head)
        self.assertEqual(s.cell(102).p1_a,555)


if __name__=='__main__':unittest.main()
