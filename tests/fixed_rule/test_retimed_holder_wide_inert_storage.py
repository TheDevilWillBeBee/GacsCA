import unittest
import numpy as np
from gacsca.fixed_rule import retimed_holder_wide_inert_storage as wide
from gacsca.fixed_rule import retimed_holder_inert_storage as previous


def snapshot(n):
    f,q,p,period=wide.f,wide.q,wide.p,wide.period
    bank=np.zeros((n,p.layout().memory_count+5),dtype=np.uint64)
    rows=np.zeros((n,period.SLOTS,len(q.SCHEMA)),dtype=np.uint64)
    rows[:,0,q.COL['age']]=1
    rows[:,0,q.COL['head']]=1
    rows[:,0,q.COL['rb']]=np.arange(n,dtype=np.uint64)+np.uint64(2**63)
    return dict(bank=bank,active_rows=rows,counts=np.ones(n,dtype=np.uint64),
                flags=np.zeros((n*f.Q//64,2),dtype=np.uint64),signals=np.zeros((n,2),dtype=np.uint64),
                age=np.array(1,dtype=np.uint64),time=np.array(f.U+1,dtype=np.uint64))


class WideStorage(unittest.TestCase):
    def test_tiled_view_matches_complete_previous_view(self):
        state=snapshot(5)
        positions=np.array([4*wide.f.Q+30960],dtype=np.int64)
        values=np.array([2**64-1],dtype=np.uint64)
        a,b=wide.View(state,positions,values),previous.View(state,positions,values)
        np.testing.assert_array_equal(a.words,b.words)
        np.testing.assert_array_equal(a.signals,b.signals)
        for start in range(0,5*wide.f.Q,wide.f.Q):
            sites=np.arange(start,start+wide.f.Q)
            np.testing.assert_array_equal(a.cells(sites),b.cells(sites))

    def test_all_73_colonies_and_global_replica_boundaries(self):
        state=snapshot(73)
        positions=np.array([36*wide.f.Q+30960],dtype=np.int64)
        values=np.array([0xDEADBEEF01234567],dtype=np.uint64)
        view=wide.View(state,positions,values)
        self.assertEqual(view.size,73*wide.f.Q)
        for col in (0,3,4,36,71,72):
            sites=np.array([col*wide.f.Q-1,col*wide.f.Q,col*wide.f.Q+1])
            cells=view.cells(sites)
            for k,site in enumerate(sites):
                for offset in wide.f.OFFSETS:
                    owner=(int(site)+offset)%view.size
                    wanted=2**63+owner//wide.f.Q if owner%wide.f.Q==0 else 0
                    self.assertEqual(int(cells[k,wide.f.COL[f's{offset+2}_rb']]),wanted)
        self.assertEqual(int(view.words[int(positions[0]),wide.DATA]),int(values[0]))

    def test_truncated_global_state_and_late_tile_flags_rejected(self):
        state=snapshot(5);empty=np.empty(0,dtype=np.int64);values=np.empty(0,dtype=np.uint64)
        with self.assertRaisesRegex(ValueError,'complete typed global'):
            wide.View(dict(state,active_rows=state['active_rows'][:,:,:-1]),empty,values)
        state['flags'][-1,0]=1
        with self.assertRaisesRegex(ValueError,'zero-flag'):
            wide.View(state,empty,values)


if __name__=='__main__':unittest.main()
