"""Early and late invocations use one unchanged spatial local rule."""
from dataclasses import replace
import unittest

from gacsca.fixed_rule import spatial_epoch8 as spatial
from gacsca.fixed_rule import stream28_compact_layout as layout
from gacsca.fixed_rule import stream28_compact_vote8 as prior
from gacsca.fixed_rule import stream28_dual_pass8 as dual
from gacsca.fixed_rule import stream28_holder_projected as projected
from gacsca.fixed_rule import stream28_holder_rule as holder
from gacsca.fixed_rule import stream28_spatial_overlay8 as late
from experiments.fixed_rule.certify_stream28_dual_pass8 import check as certify
from experiments.fixed_rule.measure_stream28_spatial_capacity import check as capacity
from experiments.fixed_rule.audit_compact8_output_endpoints import check as endpoints
from experiments.fixed_rule.replay_compact8_numpy import replay


def neighborhood(site,age,source=0,output=False,value=0):
    rows=[]
    for offset in dual.NEIGHBORHOOD:
        address=(site+offset)%dual.Q
        h=holder.Cell(address=address,age=age,
                      **{f's{k}_data':source for k in range(5)})
        s=spatial.Cell(address=address,
                       kind=spatial.OUTPUT if output and offset==0 else
                            spatial.SOURCE if not output and offset==0 else
                            spatial.INERT)
        if output and offset==1:
            s=replace(s,mail=spatial.Packet(1,site,0,3,value))
        rows.append(dual.Cell(h,s))
    return tuple(rows)


class DualPassLocalTest(unittest.TestCase):
    def test_flag_bank_is_the_fixed_compact_layout(self):
        bank=layout.build().hold
        self.assertEqual(dual.EARLY_FLAG_HOLD_ADDRESSES,
                         (bank[projected.COL['f1']],
                          bank[projected.COL['f2']]))
        self.assertEqual((dual.WIDTH,dual.NEIGHBORHOOD),
                         (prior.WIDTH,prior.NEIGHBORHOOD))
        self.assertIs(dual.Cell,prior.Cell)

    def test_early_capture_uses_protected_data_and_keeps_rom_address(self):
        site=3217
        rows=neighborhood(site,dual.EARLY_CAPTURE_AGE,source=0xA5)
        out=dual.local_step(rows)
        self.assertEqual(out.evaluator.source_value,0xA5)
        self.assertEqual(out.evaluator.address,site)
        self.assertEqual(out.evaluator.age,0)
        self.assertTrue(all(getattr(out.holder,f's{k}_head')==0
                            for k in range(5)))

    def test_early_commit_only_flag_holds_and_late_pass_unchanged(self):
        for site in (*dual.EARLY_FLAG_HOLD_ADDRESSES,2497):
            rows=neighborhood(site,dual.EARLY_RUN_START,
                              source=7,output=True,value=0xBEEF)
            prior_out=prior.local_step(rows)
            out=dual.local_step(rows)
            self.assertEqual(out.evaluator.source_value,0xBEEF)
            self.assertEqual(out.evaluator.done,1)
            if site in dual.EARLY_FLAG_HOLD_ADDRESSES:
                self.assertEqual(out.holder.s2_data,0xBEEF)
            else:
                self.assertEqual(out.holder.s2_data,prior_out.holder.s2_data)
        rows=neighborhood(2497,late.RUN_START,
                          source=7,output=True,value=0xBEEF)
        self.assertEqual(dual.local_step(rows),prior.local_step(rows))
        self.assertEqual(dual.local_step(rows).holder.s2_data,0xBEEF)

    def test_early_window_ends_before_stage_five(self):
        rows=neighborhood(2496,dual.EARLY_RUN_STOP,output=True,value=11)
        self.assertEqual(dual.local_step(rows),prior.local_step(rows))
        with self.assertRaises(ValueError):dual.local_step(rows[:-1])

    def test_early_send_head_starts_from_static_first_marker(self):
        for offset in holder.OFFSETS:
            site=100-offset
            rows=list(neighborhood(site,dual.EARLY_RUN_STOP))
            center=rows[7]
            rows[7]=dual.Cell(replace(center.holder,
                         **{f'p{offset+3}_first':1}),center.evaluator)
            out=dual.local_step(tuple(rows))
            self.assertEqual(getattr(out.holder,
                                     f's{offset+2}_head'),1)
            self.assertEqual(out.evaluator,rows[7].evaluator)

    def test_complete_changed_description_and_capacity_inventory(self):
        certificate=certify()
        self.assertEqual(certificate['literal_cases'],108)
        self.assertEqual(certificate['optimized_operations'],14845)
        inventory=capacity(compact_vote=True,eight_q=True,dual_pass=True)
        self.assertEqual(inventory['static_rom_input_words'],390)
        self.assertEqual(inventory['gathered_dynamic_input_words'],761)
        self.assertEqual(inventory['gate_slot_margin_if_static_words_occupy_sites'],43)

    def test_early_and_late_hold_endpoints(self):
        result=endpoints(dual_pass=True)
        self.assertEqual(result['literal_early_holder_steps'],595)
        self.assertEqual(result['literal_fivefold_holder_steps'],595)

    def test_encoded_own_rule_circuit_continuous_one_period(self):
        result=replay(1,spatial_rom_center=3218,dual_pass=True,
                      full_dual_rom=True)
        self.assertTrue(result['passed'])
        self.assertEqual(result['description_sha256'],
                         'e594513a4dc1950c611c28a8fa851e750ced66921a40185db0665b6ac553d3c8')
        self.assertEqual(result['packet_deliveries'],[26112])
        self.assertEqual(result['gate_completions'],[14866])
        self.assertTrue(result['holder_static_inputs_from_own_address'])
        self.assertEqual(result['projected_output_words_checked'],119)


if __name__=='__main__':unittest.main()
