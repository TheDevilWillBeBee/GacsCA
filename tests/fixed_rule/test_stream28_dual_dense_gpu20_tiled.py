"""Parity of the coalesced dense backend with the complete fixed physical F."""
import shutil
import unittest

import numpy as np

from gacsca.fixed_rule import stream28_dual_dense_gpu20 as reference
from gacsca.fixed_rule import stream28_dual_dense_gpu20_tiled as tiled
from gacsca.fixed_rule import stream28_dual_holder_rule20 as holder
from gacsca.fixed_rule import stream28_dual_pass20 as physical
from gacsca.fixed_rule import stream28_dual_pass_optimized20 as description
from gacsca.fixed_rule import stream28_dual_holder_rom as rom
from experiments.fixed_rule.compact8_address_rom import template


@unittest.skipUnless(shutil.which('nvidia-smi') and
                     shutil.which('/usr/local/cuda/bin/nvcc'),
                     'CUDA toolchain/GPU unavailable')
class TiledDenseTest(unittest.TestCase):
    def test_arbitrary_typed_state_across_two_ticks(self):
        rng = np.random.default_rng(20260929)
        widths = description.WIDTHS[7 * physical.FIELDS:8 * physical.FIELDS]
        raw = np.empty((17, physical.FIELDS), dtype=np.uint64)
        for field, width in enumerate(widths):
            high = (1 << width) if width < 64 else np.iinfo(np.uint64).max
            raw[:, field] = rng.integers(0, high, size=17,
                                         dtype=np.uint64)
        with tiled.World(raw) as world, reference.World(raw) as expected:
            self.assertEqual(world.sites, 17)
            for _ in range(2):
                world.run(1)
                expected.run(1)
                np.testing.assert_array_equal(world.read(), expected.read())

    def test_colony_wide_successive_ticks_against_reference(self):
        n = physical.Q
        raw = np.zeros((n, physical.FIELDS), dtype=np.uint64)
        raw[:, holder.COL['address']] = np.arange(n, dtype=np.uint64)
        with tiled.World(raw) as actual, reference.World(raw) as expected:
            actual.run(3)
            expected.run(3)
            np.testing.assert_array_equal(actual.read(), expected.read())

    def test_fivefold_packet_flight_across_thirty_two_literal_ticks(self):
        n = physical.Q
        origin = 100
        raw = np.zeros((n, physical.FIELDS), dtype=np.uint64)
        raw[:, holder.COL['address']] = np.arange(n, dtype=np.uint64)
        raw[:, holder.COL['age']] = 10000
        for offset in holder.OFFSETS:
            site = origin - offset
            prefix = f's{offset + 2}_rp_'
            raw[site, holder.COL[prefix + 'valid']] = 1
            raw[site, holder.COL[prefix + 'target']] = 0xCAFE
            raw[site, holder.COL[prefix + 'data']] = 0x12345678
            raw[site, holder.COL[prefix + 'remaining']] = 0
        with tiled.World(raw) as actual, reference.World(raw) as expected:
            actual.run(32)
            expected.run(32)
            result = actual.read()
            np.testing.assert_array_equal(result, expected.read())
            self.assertEqual(int(result[origin + 32,
                                        holder.COL['s2_rp_valid']]), 1)
            self.assertEqual(int(result[origin + 32,
                                        holder.COL['s2_rp_data']]), 0x12345678)

    def test_active_encoded_evaluator_sixteen_ticks(self):
        evaluator = template(True, True)
        age = physical.EARLY_RUN_START + 119
        cells = (physical.Cell(
            holder.Cell(address=site, age=age,
                        **rom.holder_static_fields(site)),
            evaluator[site]) for site in range(physical.Q))
        raw = np.array([physical.encode_cell(cell) for cell in cells],
                       dtype=np.uint64)
        with tiled.World(raw) as actual, reference.World(raw) as expected:
            actual.run(16)
            expected.run(16)
            np.testing.assert_array_equal(actual.read(), expected.read())


if __name__ == '__main__': unittest.main()
