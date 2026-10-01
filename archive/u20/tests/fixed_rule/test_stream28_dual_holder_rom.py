"""The compact holder table gives a real local SEND instruction path."""
from dataclasses import replace
import unittest

from gacsca.fixed_rule import spatial_epoch8 as spatial
from gacsca.fixed_rule import stream28_dual_holder_rom as rom
from gacsca.fixed_rule import stream28_dual_pass8 as dual
from gacsca.fixed_rule import stream28_compact_layout as compact_layout
from gacsca.fixed_rule import stream28_holder_core as core
from gacsca.fixed_rule import stream28_holder_rule as holder
from experiments.fixed_rule.build_compact8_circuit import initial_cells,static_plan
from experiments.fixed_rule.compact8_address_rom import (
    holder_input_wires,project_all_dual_static,spatial_input_wires)
from gacsca.fixed_rule import stream28_dual_pass_optimized8 as optimized


def core_neighborhood(site,age,head_site=None,pc=0):
    rows=[]
    for offset in core.NEIGHBORHOOD:
        address=(site+offset)%core.Q
        static=dict(zip(core.STATIC,rom.record(address)))
        rows.append(core.Cell(**static,address=address,age=age,
                   head=int(address==head_site),pc=pc if address==head_site else 0))
    return tuple(rows)


def replicated_holder_neighborhood(site,age,head_site,pc):
    rows=[]
    for offset in holder.NEIGHBORHOOD:
        address=(site+offset)%core.Q
        copies={}
        for d in holder.OFFSETS:
            target=(address+d)%core.Q
            logical=core.Cell(**dict(zip(core.STATIC,rom.record(target))),
                              address=target,age=age,
                              head=int(target==head_site),
                              pc=pc if target==head_site else 0)
            copies.update({f's{d+2}_{name}':getattr(logical,name)
                           for name,_ in holder.PROCEDURE})
        rows.append(holder.Cell(**rom.holder_static_fields(address),
                                **copies,address=address,age=age))
    return tuple(rows)


class DualHolderROMTest(unittest.TestCase):
    def test_one_canonical_short_program_and_stage_halts(self):
        first=dict(zip(core.STATIC,rom.record(0)))
        self.assertEqual((first['kind'],first['first']),
                         (core.MEM,1))
        for stage in range(5):
            self.assertEqual(core.entry(core.Cell(**first),stage),
                             rom.HALT_PC)
        for pc in range(10):
            row=dict(zip(core.STATIC,
                         rom.record(rom.INSTRUCTION_START+pc)))
            self.assertEqual((row['kind'],row['index']),
                             (core.SEND,pc))
            self.assertEqual(row['a'],rom.FLAG2_HOLD if pc<5 else
                             rom.FLAG1_HOLD)
            self.assertEqual(row['b'],pc+1 if pc<5 else
                             core.Q-5+pc-5)
            self.assertEqual(row['d'],core.LEFT if pc<5 else core.RIGHT)
        last=dict(zip(core.STATIC,rom.record(rom.LAST_SITE)))
        self.assertEqual((last['kind'],last['index'],last['last']),
                         (core.HALT,rom.HALT_PC,1))
        self.assertEqual(len(holder_input_wires()),49)
        self.assertEqual(len(spatial_input_wires()),341)

    def test_info_data_survives_all_three_gather_resets(self):
        site=compact_layout.build().info[0]
        self.assertEqual(dict(zip(core.STATIC,rom.record(site)))['a'],
                         core.INFO)
        for age in core.RESET_AGES[:3]:
            rows=list(core_neighborhood(site,age))
            rows[5]=replace(rows[5],data=0x123456789ABCDEF0)
            result=core._clock_step(tuple(rows))
            self.assertEqual(result.data,0x123456789ABCDEF0)

    def test_literal_head_fetches_each_send_and_halt(self):
        age=dual.EARLY_RUN_STOP+100
        for pc in range(10):
            instruction=rom.INSTRUCTION_START+pc
            out=core._word_step(core_neighborhood(
                instruction+1,age,head_site=instruction,pc=pc))
            self.assertEqual((out.head,out.phase,out.ra,out.rb,out.rd),
                (1,core.TRANSMIT,
                 rom.FLAG2_HOLD if pc<5 else rom.FLAG1_HOLD,
                 pc+1 if pc<5 else core.Q-5+pc-5,
                 core.LEFT if pc<5 else core.RIGHT))
        stopped=core._clock_step(core_neighborhood(
            rom.LAST_SITE,age,head_site=rom.LAST_SITE,pc=rom.HALT_PC))
        self.assertEqual(stopped.head,0)

    def test_fivefold_holder_copies_fetch_the_same_send(self):
        age=dual.EARLY_RUN_STOP+100
        for pc in (0,9):
            instruction=rom.INSTRUCTION_START+pc
            target=instruction+1
            for d in holder.OFFSETS:
                physical_site=target-d
                rows=replicated_holder_neighborhood(
                    physical_site,age,instruction,pc)
                out=holder.local_step(rows)
                self.assertEqual(getattr(out,f's{d+2}_head'),1)
                self.assertEqual(getattr(out,f's{d+2}_phase'),
                                 core.TRANSMIT)
                self.assertEqual(getattr(out,f's{d+2}_ra'),
                                 rom.FLAG2_HOLD if pc<5 else rom.FLAG1_HOLD)

    def test_all_static_inputs_are_derived_from_own_address_table(self):
        words=(0,)*len(optimized.WIDTHS)
        wires=set(holder_input_wires())|set(spatial_input_wires())
        self.assertEqual(len(wires),390)
        for center in (0,3218,rom.INSTRUCTION_START,rom.LAST_SITE):
            projected=project_all_dual_static(center,words)
            for wire in holder_input_wires():
                neighbor,field=divmod(wire,dual.FIELDS)
                site=(center+neighbor-7)%dual.Q
                name=holder.SCHEMA[field][0]
                self.assertEqual(projected[wire],
                                 rom.holder_static_fields(site)[name])
            physical=initial_cells(projected,True)
            for site,wire in static_plan(True)['raw_sources'].items():
                if wire in wires:
                    self.assertEqual(physical[site].source_value,
                                     projected[wire])
            self.assertTrue(all(projected[wire]==0 for wire in
                                range(len(projected)) if wire not in wires))

    def test_early_trigger_uses_real_first_rom_at_all_five_replicas(self):
        for offset in holder.OFFSETS:
            site=(-offset)%dual.Q
            rows=[]
            for delta in dual.NEIGHBORHOOD:
                address=(site+delta)%dual.Q
                h=holder.Cell(**rom.holder_static_fields(address),
                              address=address,age=dual.EARLY_RUN_STOP)
                rows.append(dual.Cell(h,spatial.Cell(address=address)))
            out=dual.local_step(tuple(rows))
            self.assertEqual(getattr(out.holder,
                                     f's{offset+2}_head'),1)


if __name__=='__main__':unittest.main()
