"""Complete live-state diagnostics must retain controllers and reject lost data."""
import unittest
import numpy as np
from gacsca.fixed_rule import retimed_holder_active_snapshot as active
from gacsca.fixed_rule import retimed_holder_quotient as q,retimed_holder_rule as f
from gacsca.fixed_rule import retimed_holder_program as p,retimed_holder_projected as r
from gacsca.fixed_rule.retimed_holder_initial import coherent_cell


def fixture():
    g=p.layout();age=f.RESET_AGES[4]+123
    bank=np.arange(g.memory_count+5,dtype=np.uint64).reshape(1,-1)
    rows=np.zeros((1,64,len(q.SCHEMA)),dtype=np.uint64)
    for i,address in enumerate((0,17,f.Q-1)):
        values={name:min((1<<width)-1,19+i) for name,width in q.SCHEMA}
        values.update(address=address,age=age,data=int(bank[0,address if address<g.memory_count else -1]),f1=0,f2=0,wf1=0,wf2=0,signal=0)
        rows[0,i]=q.encode_cell(q.Cell(**values))
    return dict(bank=bank,active_rows=rows,counts=np.array([3],dtype=np.uint64),flags=np.zeros((f.Q//64,2),dtype=np.uint64),signals=np.zeros((1,2),dtype=np.uint64),age=np.array(age,dtype=np.uint64),time=np.array(age,dtype=np.uint64))


class ActiveSnapshot(unittest.TestCase):
    def test_complete_live_fields_and_periodic_boundaries(self):
        state=fixture();logical=active.logical(state);raw=active.render(state)
        def source(pos):return q.decode_cell(logical[pos%f.Q])
        for anchor in (0,17,f.Q-1,p.layout().memory_count):
            for delta in range(-3,4):
                pos=(anchor+delta)%f.Q
                np.testing.assert_array_equal(raw[pos],f.encode_cell(r.lift(coherent_cell(source,pos))))
        for offset in f.OFFSETS:
            for name,_ in f.PROCEDURE:
                self.assertEqual(raw[17-offset,f.COL[f's{offset+2}_{name}']],logical[17,q.COL[name]])
                self.assertGreater(int(raw[17-offset,f.COL[f's{offset+2}_{name}']]),0)

    def test_incomplete_snapshot_rejected(self):
        mutations=(lambda s:s['active_rows'].__setitem__((0,0,q.COL['data']),999),
                   lambda s:s['active_rows'].__setitem__((0,1,q.COL['address']),0),
                   lambda s:s['active_rows'].__setitem__((0,0,q.COL['age']),0),
                   lambda s:s['flags'].__setitem__((0,0),1),
                   lambda s:s['counts'].__setitem__(0,2),
                   lambda s:s['signals'].__setitem__((0,0),1))
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                state=fixture();mutate(state)
                with self.assertRaises(ValueError):active.render(state)

    def test_budget_and_time_guard(self):
        state=fixture()
        with self.assertRaises(ValueError):active.render(state,max_bytes=1)
        state['time']+=np.uint64(1)
        with self.assertRaises(ValueError):active.render(state)

    def test_restore_rejects_mail_before_GPU_allocation(self):
        with self.assertRaisesRegex(ValueError,'mail-free'):active.restore(fixture())

if __name__=='__main__':unittest.main()
