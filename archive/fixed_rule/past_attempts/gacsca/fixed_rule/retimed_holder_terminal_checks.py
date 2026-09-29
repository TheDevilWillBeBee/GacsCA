"""Read-only checks of every stored terminal physical degree of freedom."""
import numpy as np
from . import retimed_holder_rule as f,retimed_holder_program as p,retimed_holder_quotient as q


def signal_word(address,left,right):
    # Bit k at physical a represents the Signal primary at a+k-2.
    if 1<=address<=5:return int(left)<<(5-address)
    if f.Q-5<=address<f.Q:return int(right)<<(f.Q-1-address)
    return 0


def check(snapshot,expected,*,age,time):
    """Check canonical resident reconstruction, including every live controller.

    The backend domain already supplies coherent replicas, derived static ROM,
    canonical geometry and zero non-MEM Data. These are representation premises,
    not deductions from an incomplete snapshot of a general physical world.
    """
    bank=expected['precommit_bank' if age==f.U-1 else 'committed_bank']
    assert age in (0,f.U-1)
    n=len(bank);assert bank.shape==(n,p.layout().memory_count+5)
    np.testing.assert_array_equal(snapshot['bank'],bank,err_msg='all terminal Data')
    np.testing.assert_array_equal(snapshot['signals'],expected['signals'],err_msg='terminal Signals')
    assert snapshot['flags'].shape==(n*f.Q//64,2) and not np.any(snapshot['flags'])
    assert int(snapshot['age'])==age and int(snapshot['time'])==time
    rows=snapshot['active_rows'];counts=snapshot['counts']
    assert rows.shape==(n,64,len(q.SCHEMA)) and counts.shape==(n,)
    for col,count in enumerate(counts):
        count=int(count);assert 0<=count<=64
        assert not np.any(rows[col,count:]),'nonzero unused diagnostic rows'
        found=set()
        for row in rows[col,:count]:
            a=int(row[q.COL['address']]);assert 0<=a<f.Q and a not in found
            found.add(a);wanted=np.zeros(len(q.SCHEMA),dtype=np.uint64)
            wanted[q.COL['address']]=a;wanted[q.COL['age']]=age
            if a<p.layout().memory_count:wanted[q.COL['data']]=bank[col,a]
            elif a>=f.Q-5:wanted[q.COL['data']]=bank[col,p.layout().memory_count+a-(f.Q-5)]
            wanted[q.COL['signal']]=signal_word(a,*expected['signals'][col])
            np.testing.assert_array_equal(row,wanted,err_msg='complete controller/mail/Wf state')
        for a in (*range(1,6),*range(f.Q-5,f.Q)):
            if signal_word(a,*expected['signals'][col]):assert a in found,'missing physical Signal replica'
    return dict(bank_words=int(bank.size),complete_logical_fields=len(q.SCHEMA),raw_fields=len(f.SCHEMA),physical_sites=n*f.Q,age=age,time=time)
