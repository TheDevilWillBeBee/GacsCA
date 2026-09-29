"""Exact projected 8Q controller, evaluator and static-ROM dependencies."""
from dataclasses import replace
import unittest

from gacsca.fixed_rule import stream28_compact_projected8 as projected
from gacsca.fixed_rule import stream28_compact_vote8 as physical
from experiments.fixed_rule.certify_stream28_compact_vote8 import vote_neighborhood


class CompactProjectedEightQ(unittest.TestCase):
    def test_full_projected_roundtrip_and_static_vote_dependency(self):
        voter=2863
        rows=vote_neighborhood(voter,voter,(0,0xffffffffffffffff,0),
                               60000000)
        dynamic=tuple(projected.project(row) for row in rows)
        holder_static=tuple(row.holder for row in rows)
        spatial_static=tuple(row.evaluator for row in rows)
        self.assertEqual((projected.WIDTH,projected.FIELDS),(3063,119))
        self.assertEqual(projected.decode_cell(projected.encode_cell(dynamic[7])),
                         dynamic[7])
        self.assertEqual(projected.lift(dynamic[7],holder_static[7],
                                        spatial_static[7]),rows[7])
        result=projected.local_step(dynamic,holder_static,spatial_static)
        self.assertEqual(result,projected.project(physical.local_step(rows)))
        self.assertEqual(result.holder.s2_data,0)

        cleared=list(holder_static)
        cleared[7]=replace(cleared[7],p3_a=0)
        without_marker=projected.local_step(dynamic,tuple(cleared),
                                            spatial_static)
        self.assertNotEqual(result.holder.s2_data,
                            without_marker.holder.s2_data)
        with self.assertRaises(ValueError):
            projected.local_step(dynamic[:-1],holder_static,spatial_static)


if __name__=='__main__':unittest.main()
