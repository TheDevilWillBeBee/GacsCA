import unittest
from unittest.mock import patch
from gacsca.fixed_rule import small_holder_rule as f,small_holder_core as c,small_holder_program as p,small_holder_native as native
from experiments.fixed_rule import certify_small_holder_dispatch_paths as dispatch
from experiments.fixed_rule.audit_small_holder_position_events import evaluate


class DispatchPaths(unittest.TestCase):
    def test_memory_FETCH_leaf_all_regular_clocks(self):
        for interval in dispatch.clock.regular_intervals():
            self.assertEqual(dispatch.prove_memory_leaf(interval)['full_raw_outputs'],9*f.FIELDS)

    def test_matching_memory_index_preserves_stale_controller(self):
        terms,raw=dispatch.leaf_prepare(True,dispatch.clock.regular_intervals()[0])
        rows=tuple(raw(j) for j in f.NEIGHBORHOOD);wanted=raw(0,after=True)
        assignments={node[1]:0 for node in terms.nodes if node[0]=='variable'}
        assignments.update(physical_age=1,base_address=19,meta_0_index=19,old_pc=19,old_rd=55,old_value=77,data_0=23)
        values=evaluate(terms,assignments)
        neighbors=tuple(f.decode_cell(tuple(values[x] for x in row)) for row in rows)
        result=f.local_step(neighbors);self.assertEqual(result,native.local_step(neighbors))
        self.assertEqual(f.encode_cell(result),tuple(values[x] for x in wanted))
        self.assertEqual((result.s3_head,result.s3_pc,result.s3_rd,result.s3_value),(1,19,55,77))
        self.assertEqual(result.s2_data,23)

    def test_old_index_disequality_cannot_replace_memory_leaf(self):
        original=dispatch.template
        with patch.object(dispatch,'template',side_effect=lambda memory:original(False)),self.assertRaises(AssertionError):
            dispatch.DispatchPath(0,0).check()

    def test_overshooting_matching_instruction_is_rejected(self):
        g=p.layout();path=dispatch.DispatchPath(g.memory_count,3)
        with self.assertRaises(AssertionError):path.flight(g.memory_count+4,False)

    def test_zero_distance_and_full_entry_routes(self):
        g=p.layout()
        for pc in g.entries:
            zero=dispatch.DispatchPath(g.memory_count+pc,pc).check()
            self.assertEqual(zero['duration'],0);self.assertTrue(zero['zero_duration_needs_no_clock_step'])
            row=dispatch.DispatchPath(0,pc).check();self.assertEqual(row['duration'],g.memory_count+pc)

    def test_all_successors_accounted_for_without_erasing_SEND_mail(self):
        rows=dispatch.routes(dispatch.inputs());g=p.layout()
        successors=[row for row in rows if row['origin'] in ('ordinary','META')]
        self.assertEqual(len(successors),len(g.instructions)-sum(op.kind==c.HALT for op in g.instructions))
        self.assertEqual(sum(row['requires_mail_composition'] for row in rows),sum(op.kind==c.SEND for op in g.instructions))
        self.assertEqual(sum(row['origin']=='reset_entry' for row in rows),5)
        self.assertEqual(sum(row['origin']=='vote_entry' for row in rows),1)


if __name__=='__main__':unittest.main()
