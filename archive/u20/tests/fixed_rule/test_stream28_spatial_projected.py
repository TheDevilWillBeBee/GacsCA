"""Complete projected controller/evaluator state and fixed-ROM dependency."""
from dataclasses import replace
import unittest

from gacsca.fixed_rule import stream28_spatial_projected as projected
from gacsca.fixed_rule import stream28_spatial_overlay as physical
from experiments.fixed_rule.audit_stream28_spatial_overlay import Fixture


class StreamSpatialProjected(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.fixture=Fixture()

    def test_all_evolving_fields_roundtrip(self):
        self.assertEqual((projected.WIDTH,projected.FIELDS),(3062,119))
        full=self.fixture.neighborhood(2863,physical.RUN_START+30000,30000)[7]
        dynamic=projected.project(full)
        words=projected.encode_cell(dynamic)
        self.assertEqual(len(words),119)
        self.assertEqual(projected.decode_cell(words),dynamic)
        self.assertEqual(projected.lift(dynamic,
                         self.fixture.witness.initial[2863]),full)
        with self.assertRaises(ValueError):projected.decode_cell(words[:-1])

    def test_projected_local_step_matches_full_fixed_rule(self):
        field=49
        sink=self.fixture.layout.hold[field]
        arrival=self.fixture.timing.route_arrival[
            len(self.fixture.compiled.uses)+field]
        full=self.fixture.neighborhood(sink,physical.RUN_START+arrival-1,
                                       arrival-1)
        dynamic=tuple(projected.project(cell) for cell in full)
        static=tuple(self.fixture.witness.initial[(sink+delta)%physical.Q]
                     for delta in physical.NEIGHBORHOOD)
        result=projected.local_step(dynamic,static)
        self.assertEqual(result,projected.project(physical.local_step(full)))
        self.assertEqual(result.holder.s2_data,
                         self.fixture.values[self.fixture.program.outputs[field]])
        with self.assertRaises(ValueError):projected.local_step(dynamic[:-1],static)


if __name__=='__main__':unittest.main()
