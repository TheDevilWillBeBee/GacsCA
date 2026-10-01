"""Actual local transport and computation in the spatial evaluator pilot."""
from dataclasses import replace
import random
import unittest

from gacsca.fixed_rule import spatial_layer1 as s
from gacsca.fixed_rule import stream28_holder_program as p
from gacsca.fixed_rule import stream28_holder_rule as f
from gacsca.fixed_rule.wordcode_and import LIT,arithmetic
from experiments.fixed_rule.measure_spatial_layer1 import check


class SpatialLayerOne(unittest.TestCase):
    def test_fixed_rule_and_schedule(self):
        placement=s.layout();certificate=s.schedule_certificate()
        self.assertEqual((s.Q,s.WIDTH,s.NEIGHBORHOOD),(8192,1630,(-1,0,1)))
        self.assertEqual((len(placement.gate_operations),len(placement.edges)),(1020,1876))
        self.assertEqual(len({edge.phase for edge in placement.edges}),1876)
        self.assertLessEqual(placement.max_routes_per_source,s.ROUTE_SLOTS)
        self.assertLess(placement.last_completion,8*s.Q)
        self.assertEqual(placement.description_sha256,p.compiled_description().digest())
        with self.assertRaises(ValueError):s.local_step((s.Cell(),)*2)
        with self.assertRaises(ValueError):s.local_step((s.Cell(),)*4)
        with self.assertRaises(ValueError):s.Cell(routes=(s.EMPTY_ROUTE,)*7)

    def test_encoded_emit_receive_and_gate_execution(self):
        rng=random.Random(2026092831)
        words=tuple(rng.getrandbits(width) for _ in range(15) for _,width in f.SCHEMA)
        cells=s.initial_cells(words);placement=s.layout();edge=placement.edges[0]
        source=cells[edge.source]
        old=replace(source,age=edge.launch-1)
        emitted=s.local_step((replace(cells[edge.source-1],age=old.age),old,
                              replace(cells[edge.source+1],age=old.age)))
        self.assertEqual(emitted.mail,
                         s.Packet(1,edge.target,edge.slot,int(words[edge.source_wire])))
        gate=cells[edge.target]
        left=replace(cells[edge.target-1],age=edge.arrival-1,mail=emitted.mail)
        entered=s.local_step((left,replace(gate,age=edge.arrival-1),
                              replace(cells[edge.target+1],age=edge.arrival-1)))
        self.assertEqual(entered.ready,1<<edge.slot)
        self.assertEqual(entered.arg1 if edge.slot else entered.arg0,
                         int(words[edge.source_wire]))
        self.assertEqual(entered.mail,s.EMPTY_PACKET)
        complete=replace(gate,age=10,ready=3,arg0=0x1234,arg1=0x5678)
        evaluated=s.local_step((cells[edge.target-1],complete,cells[edge.target+1]))
        self.assertEqual((evaluated.done,evaluated.result),
                         (1,arithmetic(gate.opcode,0x1234,0x5678)))
        literal=next(cells[address] for address in placement.gate_addresses
                     if cells[address].opcode==LIT)
        self.assertEqual(s.local_step((s.Cell(),literal,s.Cell())).result,literal.literal)

    def test_complete_first_layer_with_sampled_full_ring_steps(self):
        result=check()
        self.assertTrue(result['passed'])
        self.assertEqual(result['evaluated_prefix_outputs_checked'],1020)
        self.assertGreaterEqual(result['complete_local_steps'],s.Q)

    def test_same_rule_executes_two_layer_prefix(self):
        transition=s.local_step;width=s.WIDTH
        result=check(2)
        self.assertTrue(result['passed'])
        self.assertEqual(result['evaluated_prefix_outputs_checked'],1794)
        self.assertEqual(result['schedule']['local_constant_operands'],336)
        self.assertIs(s.local_step,transition)
        self.assertEqual(s.WIDTH,width)

    def test_encoded_phase_schedule_reaches_eight_layers(self):
        transition=s.local_step;width=s.WIDTH
        result=check(8)
        self.assertTrue(result['passed'])
        self.assertEqual(result['evaluated_prefix_outputs_checked'],4653)
        self.assertEqual(result['schedule']['operand_packets'],7680)
        self.assertEqual(result['schedule']['last_completion'],12672)
        self.assertLess(result['schedule']['last_completion'],8*s.Q)
        with self.assertRaisesRegex(AssertionError,'launch exceeds fixed Age alphabet'):
            s.layout(8,'ordinal')
        self.assertIs(s.local_step,transition)
        self.assertEqual(s.WIDTH,width)


if __name__=='__main__':unittest.main()
