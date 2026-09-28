"""Reject disappearing faults, omitted causal input, and fabricated repair."""
from dataclasses import replace
import unittest
import numpy as np

from gacsca.fixed_rule import retimed_holder_cpu_faults as overlay
from gacsca.fixed_rule import retimed_holder_cpu_general as general,retimed_holder_cpu_events as events
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_projected as r
from experiments.fixed_rule.audit_retimed_holder_cpu_encoded_repair import probe


def background():
    return general.World(np.zeros((1,f.Q),dtype=np.uint64),np.zeros((1,len(events.CONTROL)),dtype=np.uint64),
                         np.zeros(1,dtype=np.uint64),age=100)


def fixture(corrupt_holders):
    base = background(); target = 100; positions = np.arange(target-20,target+21,dtype=np.uint64)
    clean = {int(pos):base.cell(int(pos)) for pos in positions}; dirty = dict(clean)
    for d in corrupt_holders:
        pos = target+d; dirty[pos] = replace(dirty[pos],**{f's{2-d}_data':1})
    after = dict(dirty)
    for pos in positions[7:-7]:
        at = int(pos)
        after[at] = r.lift(r.project(f.local_step(tuple(dirty[at+d] for d in f.NEIGHBORHOOD))))
    raw = lambda rows:np.array([f.encode_cell(rows[int(pos)]) for pos in positions],dtype=np.uint64)
    return positions,raw(clean),raw(dirty),raw(after)


class RepairAudit(unittest.TestCase):
    def test_literal_healing_and_persistence_are_distinguished(self):
        self.assertEqual(probe(*fixture((0,)),f.Q,healed=True)['outputs_different_from_unperturbed'],0)
        self.assertGreater(probe(*fixture((-1,0,1)),f.Q,healed=False)['outputs_different_from_unperturbed'],0)

    def test_discarded_fault_or_fabricated_output_rejected(self):
        positions,clean,dirty,after = fixture((-1,0,1))
        with self.assertRaisesRegex(AssertionError,'no actual defect'):
            probe(positions,clean,clean,after,f.Q,healed=False)
        fake = after.copy(); fake[list(positions).index(100),f.COL['s2_data']] = 0
        with self.assertRaisesRegex(AssertionError,'saved faulty transition'):
            probe(positions,clean,dirty,fake,f.Q,healed=False)

    def test_missing_causal_halo_rejected(self):
        positions,clean,dirty,after = fixture((0,))
        keep = positions != 114
        with self.assertRaisesRegex(AssertionError,'missing full physical causal halo'):
            probe(positions[keep],clean[keep],dirty[keep],after[keep],f.Q,healed=True)

    def test_post_transition_capacity_rejection_restores_background(self):
        w = overlay.World(background(),capacity=3,frontier_capacity=64); target = 100
        w.inject({target+d:replace(r.project(w.cell(target+d)),**{f's{2-d}_data':1}) for d in (-1,0,1)})
        before = {pos:w.cell(pos) for pos in range(90,111)}
        with self.assertRaisesRegex(ValueError,'next exception capacity'):
            w.step()
        self.assertEqual(w.time,0); self.assertEqual(w.background.time,0)
        self.assertEqual(len(w.positions),3)
        for pos,wanted in before.items():
            self.assertEqual(w.cell(pos),wanted)


if __name__ == '__main__':
    unittest.main()
