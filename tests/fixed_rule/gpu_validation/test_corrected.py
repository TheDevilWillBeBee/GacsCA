"""Regression for the first dense gather divergence and corrected same-F backend."""
import shutil
import unittest

import numpy as np

from gacsca.fixed_rule import stream28_dual_holder_rule20 as holder
from gacsca.fixed_rule import stream28_compact_layout as layout_module
from gacsca.fixed_rule import stream28_dual_holder_rom as rom
from gacsca.fixed_rule import stream28_dual_pass20 as physical
from gacsca.fixed_rule import stream28_dual_pass_optimized20 as old_description
from gacsca.fixed_rule.gpu_validation import dense_corrected, description
from gacsca.fixed_rule.gpu_validation.initial import initialize
from experiments.fixed_rule.compact8_address_rom import template


def oracle(raw, site):
    neighbors = tuple(physical.decode_cell(raw[(site+j)%len(raw)].tolist())
                      for j in physical.NEIGHBORHOOD)
    return np.asarray(physical.encode_cell(physical.local_step(neighbors)),
                      dtype=np.uint64)


@unittest.skipUnless(shutil.which('nvidia-smi') and
                     shutil.which('/usr/local/cuda/bin/nvcc'), 'CUDA unavailable')
class CorrectedTest(unittest.TestCase):
    def test_all_fifteen_gather_offsets_match_literal_f(self):
        raw,_ = initialize(15,20260929)
        program=description.build()
        site=7*physical.Q+layout_module.build().info[100]
        routes=[r for r in layout_module.build().routes
                if r.stage==0 and r.field==100]
        self.assertEqual(len(routes),15)
        for route in routes:
            raw[:,holder.COL['age']]=route.launch-1
            words=tuple(int(word) for j in physical.NEIGHBORHOOD
                        for word in raw[(site+j)%len(raw)])
            expected=oracle(raw,site)
            actual=np.asarray(program.evaluate(words),dtype=np.uint64)
            np.testing.assert_array_equal(actual,expected,
                err_msg=f'neighbor {route.neighbor}, launch {route.launch}')
            lane='rp' if route.neighbor<7 else 'lp'
            self.assertEqual(int(actual[holder.COL[f's2_{lane}_remaining']]),
                             abs(route.neighbor-7))

    def test_seven_hop_emission_all_421_words(self):
        raw,_ = initialize(15,20260929)
        raw[:,holder.COL['age']] = 2392
        site = 2491
        words = tuple(int(word) for j in physical.NEIGHBORHOOD
                      for word in raw[(site+j)%len(raw)])
        expected = oracle(raw,site)
        old = np.asarray(old_description.build().evaluate(words),dtype=np.uint64)
        new = np.asarray(description.build().evaluate(words),dtype=np.uint64)
        field = holder.COL['s2_rp_remaining']
        self.assertEqual(field,101)
        self.assertEqual((int(old[field]),int(new[field]),int(expected[field])),
                         (1,7,7))
        np.testing.assert_array_equal(np.flatnonzero(old != expected),[field])
        np.testing.assert_array_equal(new,expected)
        with dense_corrected.World(raw) as world:
            world.run(1)
            np.testing.assert_array_equal(world.read()[site],expected)

    def test_arbitrary_typed_all_words(self):
        rng=np.random.default_rng(202609291)
        widths=description.WIDTHS[7*physical.FIELDS:8*physical.FIELDS]
        raw=np.empty((17,physical.FIELDS),dtype=np.uint64)
        for field,width in enumerate(widths):
            high=1<<width if width<64 else np.iinfo(np.uint64).max
            raw[:,field]=rng.integers(0,high,size=17,dtype=np.uint64)
        program=description.build()
        self.assertEqual((len(program.operations),program.digest()),
                         (14830,'232fa6b96f3e2887975337ff52564e54d3a2f7fc59cbf59580e2adf8e1429f88'))
        with dense_corrected.World(raw) as world:
            for _ in range(2):
                expected=np.asarray([program.evaluate(tuple(int(word)
                    for j in physical.NEIGHBORHOOD
                    for word in raw[(site+j)%len(raw)]))
                    for site in range(len(raw))],dtype=np.uint64)
                world.run(1)
                raw=world.read()
                np.testing.assert_array_equal(raw,expected)

    def test_packet_boundary_and_active_evaluator(self):
        q=physical.Q
        raw=np.zeros((q,physical.FIELDS),dtype=np.uint64)
        raw[:,holder.COL['address']]=np.arange(q)
        raw[:,holder.COL['age']]=10000
        for offset in holder.OFFSETS:
            site=(q-1-offset)%q
            prefix=f's{offset+2}_rp_'
            for suffix,value in (('valid',1),('target',1234),
                                 ('data',0x12345678),('remaining',7)):
                raw[site,holder.COL[prefix+suffix]]=value
        with dense_corrected.World(raw) as world:
            expected={site:oracle(raw,site) for site in (q-1,0,1)}
            world.run(1)
            after=world.read()
            for site,want in expected.items():
                np.testing.assert_array_equal(after[site],want)
            self.assertEqual(int(after[0,holder.COL['s2_rp_remaining']]),6)
        evaluator=template(True,True)
        age=physical.EARLY_RUN_START+119
        raw=np.asarray([physical.encode_cell(physical.Cell(
            holder.Cell(address=site,age=age,
                        **rom.holder_static_fields(site)),evaluator[site]))
            for site in range(q)],dtype=np.uint64)
        with dense_corrected.World(raw) as world:
            for _ in range(4):
                sample=(0,1,100,2496,4096,q-1)
                expected={site:oracle(raw,site) for site in sample}
                world.run(1)
                raw=world.read()
                for site,want in expected.items():
                    np.testing.assert_array_equal(raw[site],want)


if __name__=='__main__':unittest.main()
