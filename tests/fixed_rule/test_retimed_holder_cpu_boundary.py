"""Full boundary streaming, old-state voting, wrap, and quiet guards."""
import unittest
import numpy as np
from gacsca.fixed_rule import retimed_holder_cpu_boundary as b,retimed_holder_cpu_events as e
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_core as c,retimed_holder_program as p,retimed_holder_native as native


def world(age):
    data=np.zeros((1,f.Q),dtype=np.uint64)
    data[0,:p.layout().memory_count]=np.arange(p.layout().memory_count,dtype=np.uint64)+17
    return b.World(data,np.zeros((1,len(e.CONTROL)),dtype=np.uint64),[0],age=age)


class Boundaries(unittest.TestCase):
    def test_reset_vote_and_commit_match_complete_literal_outputs(self):
        g=p.layout()
        for age in (0,c.VOTE_AGES[0],c.RESET_AGES[4],f.U-1):
            w=world(age);centers=(0,g.info[f.COL['s2_pc']],g.votes[0],len(p.base_rom())-1,f.Q-1)
            expected={pos:native.local_step(tuple(w.cell(pos+j) for j in f.NEIGHBORHOOD)) for pos in centers}
            result=w.step()
            self.assertEqual(result['full_raw_evaluations'],f.Q)
            for pos,wanted in expected.items():self.assertEqual(w.cell(pos),wanted,(age,pos))
            self.assertEqual(w.age,(age+1)%f.U)

    def test_nonzero_capture_rejected_without_clearing(self):
        w=world(c.CAPTURE_AGE-1);w.data[0,1:6]=1
        before=(w.data.copy(),w.heads.copy(),w.where.copy(),w.age,w.time)
        with self.assertRaisesRegex(RuntimeError,'rejected \\(-21\\)'):w.step()
        for actual,wanted in zip((w.data,w.heads,w.where),before[:3]):np.testing.assert_array_equal(actual,wanted)
        self.assertEqual((w.age,w.time),before[3:])

    def test_quiet_window_matches_literal_and_rejects_bulk_or_live_head(self):
        w=world(c.WF_END-1);centers=(0,73,f.Q-3)
        expected={pos:native.local_step(tuple(w.cell(pos+j) for j in f.NEIGHBORHOOD)) for pos in centers}
        w.quiet_advance(1)
        for pos,wanted in expected.items():self.assertEqual(w.cell(pos),wanted)
        for age in (*c.RESET_AGES,*c.VOTE_AGES,c.CAPTURE_AGE-1,f.U-1):
            w=world(age)
            with self.assertRaisesRegex(ValueError,'physical boundary'):w.quiet_advance(1)
        w=world(100);w.heads[0,0]=1
        with self.assertRaisesRegex(ValueError,'zero heads'):w.quiet_advance(1)

if __name__=='__main__':unittest.main()
