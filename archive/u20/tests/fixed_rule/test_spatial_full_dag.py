"""All own-DAG gates and packet endpoints under the fixed local evaluator."""
from dataclasses import replace
import random
import unittest

from gacsca.fixed_rule import spatial_epoch as physical
from gacsca.fixed_rule import spatial_fanout_compiler as compiler
from gacsca.fixed_rule import stream28_holder_rule as raw
from gacsca.fixed_rule import stream28_holder_program as reference
from experiments.fixed_rule.audit_spatial_full_dag import Witness,check,oracle
from experiments.fixed_rule.explore_spatial_topology import explore
from experiments.fixed_rule.schedule_spatial_phases import schedule


class FullSpatialDag(unittest.TestCase):
    def test_full_dag_local_event_audit(self):
        transition=physical.local_step;width=physical.WIDTH
        result=check()
        self.assertTrue(result['passed'])
        self.assertEqual(result['gate_instances_checked'],11065)
        self.assertEqual(result['packet_launch_and_delivery_endpoints_checked'],38474)
        self.assertEqual(result['total_endpoint_site_steps'],55872)
        self.assertLess(result['latest_gate_completion'],physical.PERIOD)
        self.assertIs(physical.local_step,transition)
        self.assertEqual(physical.WIDTH,width)

    def test_encoded_launch_tamper_breaks_literal_local_step(self):
        rng=random.Random(2026092837)
        words=tuple(rng.getrandbits(width) for _ in range(15)
                    for _,width in raw.SCHEMA)
        compiled=compiler.compile_capacity()
        placement=explore()
        timing=schedule()
        witness=Witness(words,compiled,placement,timing,oracle(words))
        edge=next(index for index,use in enumerate(compiled.uses)
                  if use.source_gate>=0)
        site=witness.source_sites[edge]
        launch=timing.route_launch[edge]
        original=witness.initial[site]
        routes=list(original.routes)
        index=next(i for i,route in enumerate(routes)
                   if route.valid and route.launch==launch)
        routes[index]=replace(routes[index],launch=launch+1)
        rows=list(witness.initial)
        rows[site]=replace(original,routes=tuple(routes))
        witness.initial=tuple(rows)
        with self.assertRaisesRegex(AssertionError,'local spatial mismatch'):
            witness.check_site_step(site,launch-1)

    def test_output_bank_commits_all_words_under_same_rule(self):
        transition=physical.local_step;width=physical.WIDTH
        timing=schedule(True)
        self.assertEqual((len(timing.output_sinks),timing.summary['output_packets']),
                         (105,105))
        self.assertLess(timing.summary['latest_output_commit'],physical.PERIOD)
        audited=check(True,True)
        self.assertEqual(audited['output_words_checked'],154)
        self.assertEqual(audited['packet_launch_and_delivery_endpoints_checked'],
                         2*(19237+105))
        self.assertGreater(audited['second_period_endpoint_site_steps'],55000)
        self.assertEqual(audited['second_period_full_ring_site_steps'],3*physical.Q)
        self.assertIs(physical.local_step,transition)
        self.assertEqual(physical.WIDTH,width)

    def test_raw_only_output_source_is_initialized_and_sink_route_is_physical(self):
        rng=random.Random(2026092838)
        words=tuple(rng.getrandbits(width) for _ in range(15)
                    for _,width in raw.SCHEMA)
        compiled=compiler.compile_capacity()
        placement=explore()
        timing=schedule(True)
        witness=Witness(words,compiled,placement,timing,oracle(words))
        program=reference.compiled_description()
        routed_raw={use.source_site for use in compiled.uses if use.source_gate<0}
        raw_only=next(wire for wire in program.outputs if wire<program.inputs
                      and reference.layout().wires[wire] not in routed_raw)
        source=witness.initial[reference.layout().wires[raw_only]]
        self.assertEqual((source.kind,source.source_value),
                         (physical.SOURCE,words[raw_only]))
        wire=next(iter(timing.output_sinks))
        edge=len(compiled.uses)+witness.output_wires.index(wire)
        site=witness.source_sites[edge]
        launch=timing.route_launch[edge]
        original=witness.initial[site]
        routes=list(original.routes)
        index=next(i for i,route in enumerate(routes)
                   if route.valid and route.launch==launch
                   and route.target==timing.output_sinks[wire])
        routes[index]=replace(routes[index],valid=0)
        rows=list(witness.initial)
        rows[site]=replace(original,routes=tuple(routes))
        witness.initial=tuple(rows)
        with self.assertRaisesRegex(AssertionError,'local spatial mismatch'):
            witness.check_site_step(site,launch-1)

    def test_latched_output_marker_is_required_for_literal_dynamics(self):
        rng=random.Random(2026092839)
        words=tuple(rng.getrandbits(width) for _ in range(15)
                    for _,width in raw.SCHEMA)
        compiled=compiler.compile_capacity()
        placement=explore()
        timing=schedule()
        witness=Witness(words,compiled,placement,timing,oracle(words),True)
        wire=next(wire for wire in reference.compiled_description().outputs
                  if wire>=reference.compiled_description().inputs)
        key=(wire-reference.compiled_description().inputs,0)
        site=placement.sites[key]
        slot=placement.slots[key]
        old=witness.initial[site]
        gates=list(old.gates)
        marked=gates[slot]
        self.assertIn(marked.opcode,physical.OUTPUT_BASE_OPCODE)
        gates[slot]=replace(marked,opcode=physical.base_opcode(marked.opcode))
        rows=list(witness.initial)
        rows[site]=replace(old,gates=tuple(gates))
        witness.initial=tuple(rows)
        with self.assertRaisesRegex(AssertionError,'local spatial mismatch'):
            witness.check_site_step(site,witness.actual_done[key]-1)

    def test_latched_outputs_complete_before_4q_boundary(self):
        result=check(True,True,True)
        self.assertEqual((result['output_mode'],result['output_words_checked']),
                         ('latch',154))
        self.assertEqual(result['packet_launch_and_delivery_endpoints_checked'],
                         2*19237)
        self.assertEqual(result['latest_output_commit'],28929)

    def test_direct_hold_output_routes_fit_one_4q_period(self):
        result=check(True,True,False,'hold_left')
        self.assertEqual((result['output_mode'],result['output_words_checked']),
                         ('hold_left',154))
        self.assertEqual(result['packet_launch_and_delivery_endpoints_checked'],
                         2*(19237+154))
        self.assertEqual(result['latest_output_commit'],31092)


if __name__=='__main__':unittest.main()
