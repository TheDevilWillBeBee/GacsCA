"""Full-word parity, radius and initialized-ring regressions."""
import hashlib
from pathlib import Path
import shutil
import unittest

import numpy as np

from gacsca.fixed_rule import stream28_dual_pass20 as physical
from gacsca.fixed_rule import stream28_dual_pass_optimized20 as description
from gacsca.fixed_rule import stream28_dual_holder_rule20 as holder
from gacsca.fixed_rule.gpu_validation import dense
from gacsca.fixed_rule.gpu_validation.initial import initialize, decode_info


def literal_ring(raw):
    # The raw typed alphabet admits route slot 3, whereas the Python Route
    # dataclass enforces the narrower semantic subset {0,1,2}. WordCode F
    # is defined on every typed raw neighborhood and is the oracle here.
    program = description.build()
    return np.asarray([program.evaluate(tuple(int(word) for delta in
        physical.NEIGHBORHOOD for word in raw[(site+delta)%len(raw)]))
        for site in range(len(raw))], dtype=np.uint64)


@unittest.skipUnless(shutil.which('nvidia-smi') and
                     shutil.which('/usr/local/cuda/bin/nvcc'), 'CUDA unavailable')
class DenseTest(unittest.TestCase):
    def test_arbitrary_typed_all_421_words_two_ticks(self):
        rng = np.random.default_rng(129923)
        widths = description.WIDTHS[7*physical.FIELDS:8*physical.FIELDS]
        raw = np.empty((17, physical.FIELDS), dtype=np.uint64)
        for field, width in enumerate(widths):
            high = 1 << width if width < 64 else np.iinfo(np.uint64).max
            raw[:, field] = rng.integers(0, high, size=17, dtype=np.uint64)
        with dense.World(raw) as world:
            for _ in range(2):
                expected = literal_ring(raw)
                world.run(1)
                raw = world.read()
                np.testing.assert_array_equal(raw, expected)

    def test_radius_seven_excludes_eighth_neighbor(self):
        raw = np.zeros((17, physical.FIELDS), dtype=np.uint64)
        raw[8, holder.COL['address']] = 123
        changed = raw.copy()
        changed[8, holder.COL['address']] = 456
        with dense.World(raw) as baseline, dense.World(changed) as variant:
            baseline.run(1)
            variant.run(1)
            np.testing.assert_array_equal(baseline.read()[0], variant.read()[0])

    def test_initializer_and_dense_boundary_wrap(self):
        raw, upper = initialize(15, 20260929)
        self.assertEqual(len(raw), 15*physical.Q)
        self.assertEqual(len(decode_info(raw)), 15)
        self.assertGreater(len({row.holder.s2_data for row in upper}), 1)
        with dense.World(raw) as world:
            expected = literal_ring_samples(raw, (0, 1, physical.Q-1,
                                                  len(raw)-1))
            world.run(1)
            after = world.read()
            for site, words in expected.items():
                np.testing.assert_array_equal(after[site], words)

    def test_fivefold_packet_crosses_colony_boundary(self):
        n = physical.Q
        raw = np.zeros((n, physical.FIELDS), dtype=np.uint64)
        raw[:, holder.COL['address']] = np.arange(n)
        raw[:, holder.COL['age']] = 10000
        for offset in holder.OFFSETS:
            site = (n-1-offset)%n
            prefix = f's{offset+2}_rp_'
            raw[site, holder.COL[prefix+'valid']] = 1
            raw[site, holder.COL[prefix+'target']] = 1234
            raw[site, holder.COL[prefix+'data']] = 0x12345678
            raw[site, holder.COL[prefix+'remaining']] = 1
        with dense.World(raw) as world:
            expected = literal_ring_samples(raw, (n-1, 0, 1))
            world.run(1)
            after = world.read()
            for site, words in expected.items():
                np.testing.assert_array_equal(after[site], words)
            self.assertEqual(int(after[0, holder.COL['s2_rp_valid']]), 1)
            self.assertEqual(int(after[0, holder.COL['s2_rp_data']]), 0x12345678)

    def test_rule_identity_and_no_event_interface(self):
        self.assertEqual(description.build().digest(),
                         '16bf88a1d4ff5496cd3b61a1200f8a809db1438472a9191fded26de3a0786257')
        self.assertEqual((physical.FIELDS, physical.WIDTH,
                          len(physical.NEIGHBORHOOD)), (421, 6465, 15))
        source = Path(dense.__file__).read_text()+Path(dense.__file__).with_suffix('.cu').read_text()
        self.assertIn('fr_run', source)
        self.assertIn('fixed_local', source)
        self.assertNotIn('upper_step', source)
        self.assertNotIn('event_skip', source)


def literal_ring_samples(raw, sites):
    result = {}
    for site in sites:
        neighbors = tuple(physical.decode_cell(raw[(site+delta)%len(raw)].tolist())
                          for delta in physical.NEIGHBORHOOD)
        result[site] = np.asarray(physical.encode_cell(
            physical.local_step(neighbors)), dtype=np.uint64)
    return result


if __name__ == '__main__':
    unittest.main()
