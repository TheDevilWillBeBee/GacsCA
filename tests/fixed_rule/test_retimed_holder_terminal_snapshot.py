"""Reject erased scratch, controller and distributed Signal state."""
import unittest
import numpy as np
from gacsca.fixed_rule import retimed_holder_terminal_dag as dag,retimed_holder_terminal_checks as check
from gacsca.fixed_rule import retimed_holder_projected as r,retimed_holder_rule as f,retimed_holder_program as p,retimed_holder_quotient as q


class Snapshot(unittest.TestCase):
    def fixture(self):
        expected=dag.terminal((r.Cell(),));expected['signals'][0]=1
        rows=np.zeros((1,64,len(q.SCHEMA)),dtype=np.uint64)
        for i,a in enumerate((*range(1,6),*range(f.Q-5,f.Q))):
            rows[0,i,q.COL['address']]=a
            rows[0,i,q.COL['signal']]=check.signal_word(a,1,1)
            if a<p.layout().memory_count:rows[0,i,q.COL['data']]=expected['committed_bank'][0,a]
        state=dict(bank=expected['committed_bank'].copy(),active_rows=rows,counts=np.array([10],dtype=np.uint64),flags=np.zeros((f.Q//64,2),dtype=np.uint64),signals=expected['signals'].copy(),age=np.array(0),time=np.array(f.U))
        return expected,state

    def test_complete_synthetic_snapshot(self):
        expected,state=self.fixture();check.check(state,expected,age=0,time=f.U)

    def test_changed_scratch_and_hidden_controller_rejected(self):
        for name in ('scratch','controller','signal_replica','flag','missing_row'):
            expected,state=self.fixture()
            if name=='scratch':state['bank'][0,p.layout().memory_count-1]^=np.uint64(1)
            elif name=='controller':state['active_rows'][0,0,q.COL['rb']]=1
            elif name=='signal_replica':state['active_rows'][0,0,q.COL['signal']]=0
            elif name=='flag':state['flags'][0,1]=1
            else:state['counts'][0]=9;state['active_rows'][0,9]=0
            with self.assertRaises(AssertionError,msg=name):check.check(state,expected,age=0,time=f.U)

    def test_distributed_signal_pattern_is_literal_fixed_point(self):
        for left in (0,1):
            for right in (0,1):
                for a in (*range(13),*range(f.Q-13,f.Q),f.Q//2):
                    neighbors=tuple(r.Cell(address=(a+d)%f.Q,age=f.U-2,signal=check.signal_word((a+d)%f.Q,left,right)) for d in f.NEIGHBORHOOD)
                    self.assertEqual(r.local_step(neighbors).signal,check.signal_word(a,left,right))


if __name__=='__main__':unittest.main()
