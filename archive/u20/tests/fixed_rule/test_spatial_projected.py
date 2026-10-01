"""ProgramBit-style static projection keeps all evolving evaluator state."""
from dataclasses import replace
import random
import unittest

from gacsca.fixed_rule import spatial_epoch as physical
from gacsca.fixed_rule import spatial_fanout_compiler as compiler
from gacsca.fixed_rule import spatial_projected as projected
from gacsca.fixed_rule import stream28_holder_rule as raw
from experiments.fixed_rule.audit_spatial_full_dag import Witness,oracle
from experiments.fixed_rule.explore_spatial_topology import explore
from experiments.fixed_rule.schedule_spatial_phases import schedule


class SpatialProjected(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rng=random.Random(2026092836)
        words=tuple(rng.getrandbits(width) for _ in range(15)
                    for _,width in raw.SCHEMA)
        cls.compiled=compiler.compile_capacity()
        cls.timing=schedule(True,'hold_left')
        cls.witness=Witness(words,cls.compiled,explore(),cls.timing,oracle(words))

    def test_projection_roundtrip_retains_all_dynamic_fields(self):
        self.assertEqual((projected.WIDTH,physical.WIDTH-projected.WIDTH),
                         (358,1976))
        state=self.witness.cell_at(self.timing.output_sinks[
            next(iter(self.timing.output_sinks))],
            self.timing.summary['latest_output_commit'])
        dynamic=projected.project(state)
        self.assertEqual(projected.decode_cell(projected.encode_cell(dynamic)),dynamic)
        self.assertEqual(projected.lift(dynamic,self.witness.initial[state.address]),state)
        with self.assertRaises(ValueError):projected.decode_cell(
            projected.encode_cell(dynamic)[:-1])

    def test_local_projection_uses_fixed_static_route_data(self):
        edge=len(self.compiled.uses)
        site=self.witness.source_sites[edge]
        t=self.timing.route_launch[edge]-1
        addresses=((site-1)%physical.Q,site,(site+1)%physical.Q)
        dynamics=tuple(projected.project(self.witness.cell_at(at,t))
                       for at in addresses)
        static=tuple(self.witness.initial[at] for at in addresses)
        expected=projected.project(physical.local_step(tuple(
            self.witness.cell_at(at,t) for at in addresses)))
        self.assertEqual(projected.local_step(dynamics,static),expected)
        routes=list(static[1].routes)
        route_index=next(i for i,route in enumerate(routes)
                         if route.valid and route.launch==t+1 and
                         route.target_gate_slot==3)
        routes[route_index]=replace(routes[route_index],valid=0)
        damaged=list(static)
        damaged[1]=replace(static[1],routes=tuple(routes))
        self.assertNotEqual(projected.local_step(dynamics,tuple(damaged)),expected)
        with self.assertRaises(ValueError):projected.local_step(dynamics[:2],static)


if __name__=='__main__':unittest.main()
