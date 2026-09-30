import unittest
from dataclasses import replace

import numpy as np

from gacsca.fixed_rule import spatial_epoch8 as spatial
from gacsca.fixed_rule import stream28_dual_core20 as core
from gacsca.fixed_rule import stream28_dual_holder_rom as rom
from gacsca.fixed_rule import stream28_dual_holder_rule20 as holder
from gacsca.fixed_rule import stream28_dual_pass20 as base
from gacsca.fixed_rule.u20_repair import lookup_bus,successor,successor_optimized,successor_native


class ProtocolTest(unittest.TestCase):
    def test_raw_codec_radius_and_fixed_identity(self):
        self.assertEqual((successor.Q,successor.U,successor.WIDTH,
                          successor.FIELDS),(8192,1<<20,6609,433))
        names={name for name,_ in holder.SCHEMA}
        self.assertIn('s4_rp_remaining',names)
        self.assertIn('s0_phase',names)
        self.assertIn('w4_wf2',names)
        cell=successor.Cell(base.Cell(holder.Cell(),spatial.Cell()))
        self.assertEqual(successor.decode_cell(successor.encode_cell(cell)),cell)
        with self.assertRaises(ValueError):successor.decode_cell((0,)*432)
        with self.assertRaises(ValueError):successor.local_step((cell,)*14)
        with self.assertRaises(ValueError):successor.local_step((cell,)*16)
        self.assertEqual(successor_optimized.build().inputs,15*433)
        self.assertEqual(len(successor_optimized.build().outputs),433)

    def test_local_lookup_phase_uses_each_sites_age(self):
        raw=np.zeros((base.Q,base.FIELDS),dtype=np.uint64)
        raw[:,holder.COL['address']]=np.arange(base.Q)
        raw[:,holder.COL['age']]=77
        raw[100,holder.COL['age']]=base.Q
        meta=np.zeros((base.Q,3),dtype=np.int32)
        meta[100]=(1,7,holder.COL['p3_kind'])
        bus=lookup_bus.Bus.empty(base.Q,meta)
        bus.address_register[100]=321
        new,_=lookup_bus.step(raw,bus)
        self.assertEqual(int(new.packet_valid[100]),1)
        self.assertEqual(int(new.packet_target[100]),321)
        self.assertEqual(int(np.count_nonzero(new.packet_valid)),1)

    def test_source_word_is_read_at_physical_target(self):
        raw=np.zeros((base.Q,base.FIELDS),dtype=np.uint64)
        raw[:,holder.COL['address']]=np.arange(base.Q)
        raw[:,holder.COL['age']]=base.Q+1
        raw[101,holder.COL['p3_kind']]=13
        bus=lookup_bus.Bus.empty(base.Q,np.zeros((base.Q,3),dtype=np.int32))
        bus.packet_valid[100]=True
        bus.packet_target[100]=101
        bus.packet_field[100]=holder.COL['p3_kind']
        new,_=lookup_bus.step(raw,bus)
        self.assertEqual(int(new.packet_value[101]),13)
        self.assertEqual(int(new.packet_fetched[101]),1)
        raw[111,holder.COL['p3_kind']]=9
        changed,_=lookup_bus.step(raw,bus)
        self.assertEqual(int(changed.packet_value[101]),13)

    def test_successor_packet_reads_its_own_static_metadata(self):
        center=3218
        for field,expected in ((base.FIELDS,1),
                               (base.FIELDS+1,7),
                               (base.FIELDS+2,423)):
            rows=[]
            for j in base.NEIGHBORHOOD:
                address=(center+j)%base.Q
                rows.append(successor.Cell(
                    base.Cell(holder.Cell(address=address,age=base.Q+1),
                              spatial.Cell(address=address)),
                    lookup_enable=int(j==0),
                    lookup_neighbor=7 if j==0 else 0,
                    lookup_field=423 if j==0 else 0,
                    packet_valid=int(j==-1),
                    packet_target=center if j==-1 else 0,
                    packet_field=field if j==-1 else 0))
            neighborhood=tuple(rows)
            literal=successor.encode_cell(successor.local_step(neighborhood))
            words=tuple(word for cell in neighborhood
                        for word in successor.encode_cell(cell))
            self.assertEqual(literal[base.FIELDS+11],expected)
            self.assertEqual(successor_optimized.build().evaluate(words),literal)
            self.assertEqual(successor_native.evaluate(words),literal)

    def test_fivefold_write_is_part_of_the_same_literal_and_native_rule(self):
        source=3000
        value=0xDEADBEEF12345678
        program=successor_optimized.build()
        for d in holder.OFFSETS:
            center=(source-d)%base.Q
            rows=[]
            for j in base.NEIGHBORHOOD:
                address=(center+j)%base.Q
                h=holder.Cell(address=address,age=2*base.Q+1,
                              **rom.holder_static_fields(address))
                rows.append(successor.Cell(base.Cell(h,spatial.Cell(address=address)),
                                           packet_valid=int(address==source),
                                           packet_source=source,
                                           packet_fetched=int(address==source),
                                           packet_value=value if address==source else 0))
            neighborhood=tuple(rows)
            literal=successor.encode_cell(successor.local_step(neighborhood))
            words=tuple(word for cell in neighborhood
                        for word in successor.encode_cell(cell))
            self.assertEqual(program.evaluate(words),literal)
            self.assertEqual(successor_native.evaluate(words),literal)
            self.assertEqual(literal[holder.COL[f's{d+2}_data']],value)

    def test_vectorized_bus_matches_literal_successor_locally(self):
        center=lookup_bus.ADDRESS_SOURCE
        names=('lookup_address','broadcast_valid','broadcast_value',
               'packet_valid','packet_source','packet_target','packet_field',
               'packet_fetched','packet_value')
        for age in (0,1,base.Q,base.Q+1,2*base.Q,2*base.Q+1):
            raw=np.zeros((base.Q,base.FIELDS),dtype=np.uint64)
            raw[:,holder.COL['address']]=np.arange(base.Q)
            raw[:,holder.COL['age']]=age
            raw[center,holder.COL['s2_data']]=173
            raw[center,holder.COL['p3_kind']]=13
            meta=np.zeros((base.Q,3),dtype=np.int32)
            meta[center]=(1,7,holder.COL['p3_kind'])
            bus=lookup_bus.Bus.empty(base.Q,meta)
            bus.address_register[center]=173
            bus.broadcast_valid[center-1]=True
            bus.broadcast_value[center-1]=4093
            bus.packet_valid[center-1]=True
            bus.packet_target[center-1]=center
            bus.packet_field[center-1]=holder.COL['p3_kind']
            bus.packet_valid[center]=True
            bus.packet_source[center]=center
            bus.packet_fetched[center]=True
            bus.packet_value[center]=0xDEADBEEF
            advanced,writes=lookup_bus.step(raw,bus)
            cells=[]
            for j in base.NEIGHBORHOOD:
                site=(center+j)%base.Q
                fields={name:int(getattr(bus,'address_register' if name=='lookup_address' else name)[site])
                        for name in names}
                fields.update(lookup_enable=int(meta[site,0]),
                              lookup_neighbor=int(meta[site,1]),
                              lookup_field=int(meta[site,2]))
                cells.append(successor.Cell(base.decode_cell(raw[site].tolist()),
                                            **fields))
            result=successor.local_step(tuple(cells))
            for name in names:
                self.assertEqual(getattr(result,name),int(getattr(advanced,'address_register' if name=='lookup_address' else name)[center]),
                                 msg=f'age={age} field={name}')
            if age==2*base.Q+1:
                mask,value=writes[0]
                self.assertTrue(mask[center])
                self.assertEqual(result.base.holder.s2_data,int(value[center]))

    def test_broadcast_masks_full_width_info_word(self):
        center=lookup_bus.ADDRESS_SOURCE
        raw=np.zeros((base.Q,base.FIELDS),dtype=np.uint64)
        raw[:,holder.COL['address']]=np.arange(base.Q)
        raw[center,holder.COL['s2_data']]=0xDEADBEEF1234A173
        bus=lookup_bus.Bus.empty(base.Q,np.zeros((base.Q,3),dtype=np.int32))
        advanced,_=lookup_bus.step(raw,bus)
        expected=0xDEADBEEF1234A173 & (base.Q-1)
        self.assertEqual(int(advanced.broadcast_value[center]),expected)
        self.assertEqual(int(advanced.address_register[center]),expected)
        rows=[]
        for j in base.NEIGHBORHOOD:
            site=(center+j)%base.Q
            rows.append(successor.Cell(base.decode_cell(raw[site].tolist())))
        literal=successor.local_step(tuple(rows))
        self.assertEqual(literal.broadcast_value,expected)
        self.assertEqual(literal.lookup_address,expected)

    def test_unrepaired_static_damage(self):
        rows=[]
        for j in base.NEIGHBORHOOD:
            address=(100+j)%base.Q
            h=holder.Cell(address=address,age=100,
                          **rom.holder_static_fields(address))
            rows.append(base.Cell(h,spatial.Cell(address=address)))
        center=rows[7]
        rows[7]=replace(center,holder=replace(center.holder,p3_kind=15))
        after=base.local_step(tuple(rows))
        self.assertEqual(after.holder.p3_kind,15)


class FidelityTest(unittest.TestCase):
    def test_candidate_b_flag2_erases_where_printed_condition_persists(self):
        rows=tuple(core.Cell(address=(3+j)%core.Q,age=0,f2=int(j==0))
                   for j in core.NEIGHBORHOOD)
        # Gray p. 21 prints erasure for Flag1=0 only if there is no zero in
        # L(x)&C(x). Here the left neighbors are zero, so the printed bit
        # persists; the candidate-B explicit erosion clears it.
        self.assertEqual(core.maintenance(rows)['f2'],0)
        self.assertTrue(any(row.f2==0 for row in rows[:5]))

    def test_signal_uses_data_bit_at_capture(self):
        rows=tuple(holder.Cell(address=(3+j)%holder.Q,
                               age=holder.CAPTURE_AGE-1,
                               **rom.holder_static_fields((3+j)%holder.Q),
                               **{f's{k}_data':1 for k in range(5)})
                   for j in holder.NEIGHBORHOOD)
        after=holder.local_step(rows)
        self.assertEqual((after.age,after.signal,after.f1,after.f2),
                         (holder.CAPTURE_AGE,4,0,0))


if __name__=='__main__':unittest.main()
