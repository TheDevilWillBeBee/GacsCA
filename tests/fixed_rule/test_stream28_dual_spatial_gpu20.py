"""GPU encoded spatial recurrence agrees with the literal local successor."""
import shutil
import random
import unittest

import numpy as np

from gacsca.fixed_rule import spatial_codec8 as codec
from gacsca.fixed_rule import spatial_epoch8 as spatial
from gacsca.fixed_rule import stream28_dual_pass_optimized20 as optimized
from gacsca.fixed_rule import stream28_dual_spatial_gpu20 as gpu
from experiments.fixed_rule.build_compact8_circuit import initial_cells
from experiments.fixed_rule.run_dual_spatial_gpu20 import run as run_period


@unittest.skipUnless(shutil.which('nvidia-smi') and
                     shutil.which('/usr/local/cuda/bin/nvcc'),
                     'CUDA toolchain/GPU unavailable')
class SpatialGPUFixedRuleTest(unittest.TestCase):
    def test_full_circuit_first_five_local_ticks(self):
        rows=initial_cells((0,)*len(optimized.WIDTHS),True,True)
        raw=np.array([codec.encode_cell(row) for row in rows],
                     dtype=np.uint64)
        with gpu.World(raw) as world:
            for _ in range(5):
                world.run(1)
                rows=tuple(spatial.local_step((rows[(i-1)%spatial.Q],
                                               rows[i],
                                               rows[(i+1)%spatial.Q]))
                           for i in range(spatial.Q))
            actual,events,counts=world.read()
            np.testing.assert_array_equal(
                actual,np.array([codec.encode_cell(row) for row in rows],
                                dtype=np.uint64))
            self.assertEqual(world.age,5)
            self.assertEqual(len(events),0)
            self.assertGreater(counts[1],0)

    def test_rejects_missing_raw_state_and_incoherent_age(self):
        rows=np.zeros((17,codec.FIELDS),dtype=np.uint64)
        rows[1,1]=1
        with self.assertRaises(ValueError):gpu.World(rows)
        with self.assertRaises(ValueError):gpu.World(rows[:,:-1])

    def test_arbitrary_typed_local_contexts(self):
        rng=random.Random(2026092941)
        opcodes=(0,1,2,3,4,5,6,7,8,9,10,11,12,13,14)
        for age in (0,1,8191,65535):
            rows=[]
            for i in range(17):
                gates=tuple(spatial.GateSpec(
                    valid=rng.randrange(2),opcode=rng.choice(opcodes),
                    literal=rng.getrandbits(64),wire=rng.randrange(1<<14),
                    preload0=rng.getrandbits(64),
                    preload1=rng.getrandbits(64),
                    preload_ready=rng.randrange(4)) for _ in range(3))
                routes=tuple(spatial.Route(
                    valid=rng.randrange(2),target=rng.randrange(spatial.Q),
                    arg_slot=rng.randrange(2),
                    target_gate_slot=rng.randrange(4),
                    source_gate_slot=rng.randrange(3),
                    launch=(age+1)%spatial.PERIOD)
                    if k<2 else spatial.EMPTY_ROUTE for k in range(38))
                mail=spatial.Packet(rng.randrange(2),rng.randrange(spatial.Q),
                                    rng.randrange(2),rng.randrange(4),
                                    rng.getrandbits(64))
                rows.append(spatial.Cell(
                    address=i,age=age,kind=rng.randrange(4),
                    active_slot=rng.randrange(3),
                    switch_ages=((age+1)%spatial.PERIOD,
                                 (age+1)%spatial.PERIOD),
                    gates=gates,routes=routes,
                    source_value=rng.getrandbits(64),
                    arg0=rng.getrandbits(64),arg1=rng.getrandbits(64),
                    ready=rng.randrange(4),result=rng.getrandbits(64),
                    done=rng.randrange(2),mail=mail,
                    collision=rng.randrange(2)))
            rows=tuple(rows)
            raw=np.array([codec.encode_cell(row) for row in rows],
                         dtype=np.uint64)
            with gpu.World(raw) as world:
                world.run(1)
                actual=world.read()[0]
            expected=np.array([codec.encode_cell(spatial.local_step(
                (rows[(i-1)%17],rows[i],rows[(i+1)%17])))
                for i in range(17)],dtype=np.uint64)
            np.testing.assert_array_equal(actual,expected)

    def test_complete_gpu_period_produces_all_physical_outputs(self):
        initial=initial_cells((0,)*len(optimized.WIDTHS),True,True)
        report,final,_=run_period(initial)
        self.assertEqual(report['ticks_evolved'],spatial.PERIOD)
        self.assertEqual(report['packet_deliveries'],[26101])
        self.assertEqual(report['gate_completions'],[14851])
        self.assertEqual(len(report['physical_output_events']),119)
        self.assertTrue(all(type(site) is int for _,site,_ in
                            report['physical_output_events']))
        self.assertEqual(len(final),spatial.Q)
        self.assertEqual(sum(row.kind==spatial.OUTPUT for row in final),119)
        self.assertTrue(all(not row.done for row in final
                            if row.kind==spatial.OUTPUT))


if __name__=='__main__':unittest.main()
