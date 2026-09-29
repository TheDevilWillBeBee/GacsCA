"""Regression gates for the single retimed Q8192/U2^20 candidate.

These tests deliberately do not label evaluator periods as upper macrosteps.
"""
import unittest

from gacsca.fixed_rule import spatial_epoch8 as evaluator
from gacsca.fixed_rule import stream28_compact_layout as layout
from gacsca.fixed_rule import stream28_dual_pass8 as old
from gacsca.fixed_rule import stream28_dual_pass20 as current
from gacsca.fixed_rule import stream28_dual_pass_optimized8 as old_program
from gacsca.fixed_rule import stream28_dual_pass_optimized20 as program
from gacsca.fixed_rule import stream28_dual_holder_rule20 as holder
from gacsca.fixed_rule import stream28_dual_core20 as core
from gacsca.fixed_rule import stream28_dual_holder_rom as rom
from gacsca.fixed_rule import stream28_holder_rule as old_holder
from gacsca.fixed_rule.wordcode_and import LIT
from experiments.fixed_rule.audit_compact8_output_endpoints import check as endpoints
from experiments.fixed_rule.audit_dual_clock20 import check as clock
from experiments.fixed_rule.certify_dual_projection20 import check as projection
from experiments.fixed_rule.certify_stream28_dual_pass20 import check as certify
from experiments.fixed_rule.measure_stream28_spatial_capacity import check as capacity


def used_inputs(selected):
    compiled=selected.build()
    result={wire for opcode,a,b in compiled.operations if opcode!=LIT
            for wire in (a,b) if wire<compiled.inputs}
    result.update(wire for wire in compiled.outputs if wire<compiled.inputs)
    return result


class FixedU20DualPassTest(unittest.TestCase):
    def test_fixed_alphabet_neighborhood_and_complete_input_layout(self):
        self.assertEqual((current.Q,current.U,current.WIDTH),
                         (8192,1<<20,6465))
        self.assertEqual(current.NEIGHBORHOOD,tuple(range(-7,8)))
        self.assertEqual(evaluator.PERIOD,8*current.Q)
        self.assertEqual((holder.STATIC,holder.SCHEMA),
                         (old_holder.STATIC,old_holder.SCHEMA))
        self.assertEqual(current.WIDTH,old.WIDTH)
        self.assertEqual(current.FIELDS,old.FIELDS)
        used=used_inputs(program)
        self.assertEqual(used,used_inputs(old_program))
        self.assertEqual(len(used),1151)
        self.assertEqual(len(used.intersection(layout.build().static_inputs)),390)
        self.assertEqual(len(used-set(layout.build().static_inputs)),761)

    def test_complete_physical_F_and_capacity(self):
        certificate=certify()
        self.assertTrue(certificate['passed'])
        self.assertEqual(certificate['literal_cases'],108)
        self.assertEqual(certificate['optimized_operations'],14830)
        self.assertEqual(certificate['optimized_description_sha256'],
                         '16bf88a1d4ff5496cd3b61a1200f8a809db1438472a9191fded26de3a0786257')
        inventory=capacity(compact_vote=True,eight_q=True,dual_pass=True,
                           u20=True)
        self.assertEqual(inventory['static_rom_input_words'],390)
        self.assertEqual(inventory['gathered_dynamic_input_words'],761)
        # The inventory precedes two required raw-source buffer instances.
        self.assertEqual(inventory['gate_slot_margin_if_static_words_occupy_sites'],58)

    def test_info_survives_gathers_and_commits_final_hold(self):
        site=layout.build().info[0]
        hold=site+1
        for age in core.RESET_AGES[:3]:
            rows=[]
            for offset in core.NEIGHBORHOOD:
                address=(site+offset)%core.Q
                raw=core.Cell(**dict(zip(core.STATIC,rom.record(address))),
                              address=address,age=age,
                              data=37 if address==site else 0)
                rows.append(raw)
            self.assertEqual(core._clock_step(tuple(rows)).data,37)
        logical={site:11,hold:97}
        rows=[]
        for offset in current.NEIGHBORHOOD:
            address=(site+offset)%current.Q
            copies={}
            for backup in holder.OFFSETS:
                source=(address+backup)%current.Q
                copies[f's{backup+2}_data']=logical.get(source,0)
            rows.append(current.Cell(
                holder.Cell(**rom.holder_static_fields(address),
                            address=address,age=current.U-1,**copies),
                evaluator.Cell(address=address)))
        out=current.local_step(tuple(rows))
        self.assertEqual(out.holder.s2_data,97)
        self.assertEqual(out.holder.age,0)

    def test_gather_two_pass_send_and_commit_deadlines(self):
        result=clock()
        self.assertEqual(result['U'],128*result['Q'])
        self.assertGreaterEqual(result['send_margin_to_stage3_end'],16000)
        self.assertLess(result['final_last_hold'],result['final_run_stop'])
        literal=endpoints(dual_pass=True,u20=True)
        self.assertEqual(literal['literal_early_holder_steps'],595)
        self.assertEqual(literal['literal_fivefold_holder_steps'],595)

    def test_decoded_own_rule_dynamics_from_encoded_rom(self):
        result=projection(physical_period=True)
        self.assertEqual(result['decoded_local_cases'],40)
        self.assertEqual(result['projected_words'],119)
        self.assertEqual(result['spatial_static_inputs'],341)
        self.assertEqual(result['holder_static_inputs'],49)
        self.assertEqual(result['physical_period_receipt']
                         ['projected_output_words_checked'],119)


if __name__=='__main__':unittest.main()
