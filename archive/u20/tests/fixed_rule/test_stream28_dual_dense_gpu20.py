"""CUDA backend executes the complete fixed raw successor, not an upper oracle."""
import shutil
import unittest

import numpy as np

from gacsca.fixed_rule import spatial_epoch8 as spatial
from gacsca.fixed_rule import stream28_dual_dense_gpu20 as gpu
from gacsca.fixed_rule import stream28_dual_holder_rule20 as holder
from gacsca.fixed_rule import stream28_dual_holder_rom as rom
from gacsca.fixed_rule import stream28_dual_native20 as native
from gacsca.fixed_rule import stream28_dual_pass20 as physical
from experiments.fixed_rule.compact8_address_rom import template


@unittest.skipUnless(shutil.which('nvidia-smi') and
                     shutil.which('/usr/local/cuda/bin/nvcc'),
                     'CUDA toolchain/GPU unavailable')
class LiteralGPUFixedRuleTest(unittest.TestCase):
    def test_complete_raw_ring_through_successive_ticks(self):
        cells=tuple(physical.Cell(
            holder.Cell(address=i,age=holder.RESET_AGES[2]-2,
                        **{f's{k}_data':i*19+k for k in range(5)}),
            spatial.Cell(address=i,kind=spatial.SOURCE,
                         source_value=i*7)) for i in range(17))
        raw=np.array([physical.encode_cell(row) for row in cells],
                     dtype=np.uint64)
        with gpu.World(raw) as world:
            self.assertEqual(world.sites,17)
            for ticks in (1,1,3):
                world.run(ticks)
                for _ in range(ticks):cells=native.step_ring(cells)
                expected=np.array([physical.encode_cell(row)
                                   for row in cells],dtype=np.uint64)
                np.testing.assert_array_equal(world.read(),expected)
            self.assertEqual(world.time,5)

    def test_complete_canonical_colony_at_active_evaluator_age(self):
        evaluator=template(True,True)
        age=physical.EARLY_RUN_START+119
        cells=tuple(physical.Cell(
            holder.Cell(address=i,age=age,
                        **rom.holder_static_fields(i),
                        **{f's{k}_data':i*19+k for k in range(5)}),
            evaluator[i]) for i in range(physical.Q))
        raw=np.array([physical.encode_cell(row) for row in cells],
                     dtype=np.uint64)
        with gpu.World(raw) as world:
            for _ in range(2):
                world.run(1)
                cells=native.step_ring(cells)
            np.testing.assert_array_equal(
                world.read(),
                np.array([physical.encode_cell(row) for row in cells],
                         dtype=np.uint64))

    def test_packet_travels_between_checked_event_endpoints(self):
        origin=100
        evaluator=template(True,True)
        cells=[]
        for site in range(physical.Q):
            copies={}
            for offset in holder.OFFSETS:
                if (site+offset)%physical.Q==origin:
                    prefix=f's{offset+2}_rp_'
                    copies.update({prefix+'valid':1,prefix+'target':0xCAFE,
                                   prefix+'data':0x12345678,
                                   prefix+'remaining':0})
            cells.append(physical.Cell(
                holder.Cell(address=site,age=10000,
                            **rom.holder_static_fields(site),**copies),
                evaluator[site]))
        cells=tuple(cells)
        raw=np.array([physical.encode_cell(row) for row in cells],
                     dtype=np.uint64)
        with gpu.World(raw) as world:
            world.run(4)
            for _ in range(4):cells=native.step_ring(cells)
            np.testing.assert_array_equal(
                world.read(),
                np.array([physical.encode_cell(row) for row in cells],
                         dtype=np.uint64))
            world.run(28)
            actual=world.read()
            self.assertEqual(int(actual[origin+32,
                                        holder.COL['s2_rp_valid']]),1)
            self.assertEqual(int(actual[origin+32,
                                        holder.COL['s2_rp_data']]),0x12345678)
            self.assertEqual(int(actual[:,holder.COL['s2_rp_valid']].sum()),1)


if __name__=='__main__':unittest.main()
