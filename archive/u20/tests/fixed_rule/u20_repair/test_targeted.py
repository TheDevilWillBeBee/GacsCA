"""Regress actual branch witnesses and the whole-ring native entry point."""
import unittest

import numpy as np

from experiments.fixed_rule.u20_repair.targeted_parity import run
from experiments.fixed_rule.u20_repair.certify_packet_mux import run as packet_mux_run
from gacsca.fixed_rule import spatial_epoch8 as spatial
from gacsca.fixed_rule import stream28_dual_holder_rule20 as holder
from gacsca.fixed_rule import stream28_dual_pass20 as base
from gacsca.fixed_rule.u20_repair import successor,successor_native


class TargetedParityTest(unittest.TestCase):
    def test_all_packet_field_selectors(self):
        receipt=packet_mux_run()
        self.assertEqual((receipt['selectors'],receipt['valid_fields'],
                          receipt['invalid_fields']),(512,433,79))
        self.assertEqual(receipt['raw_outputs_checked'],512*433)

    def test_real_opcode_route_and_boundary_branches(self):
        receipt=run()
        self.assertEqual(receipt['cases'],55)
        self.assertEqual(receipt['raw_outputs_checked'],55*base.FIELDS)
        self.assertEqual(len(receipt['executed_opcode_branches']),9)
        self.assertEqual(len(receipt['executed_route_offsets']),14)
        self.assertEqual(len(receipt['coherent_boundary_ages']),32)

    def test_native_ring_preserves_every_successor_field(self):
        n=17
        raw=np.zeros((n,successor.FIELDS),dtype=np.uint64)
        raw[:,holder.COL['address']]=np.arange(n)
        raw[:,holder.COL['age']]=1000
        raw[:,successor.base_rule.FIELDS+3]=np.arange(n)+173
        raw[:,successor.base_rule.FIELDS+8]=np.arange(n)+47
        raw[:,successor.base_rule.FIELDS+11]=0xABC00000+np.arange(n)
        actual=successor_native.step_ring(raw)
        self.assertEqual(actual.shape,raw.shape)
        for site in range(n):
            rows=tuple(successor.decode_cell(raw[(site+j)%n].tolist())
                       for j in successor.NEIGHBORHOOD)
            self.assertEqual(tuple(map(int,actual[site])),
                             successor.encode_cell(successor.local_step(rows)))


if __name__=='__main__':unittest.main()
