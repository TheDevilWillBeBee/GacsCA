"""Diagnostic snapshots of every stored canonical general-context physical field."""
import numpy as np
from . import compact16_holder_resident_general as general,compact16_holder_resident_period as period
from . import compact16_holder_packed as packed,compact16_holder_records as q,compact16_holder_rule as f


def snapshot(world):
    if type(world) is not general.World:raise TypeError('general resident world required')
    bank,stored,counts=world._core.snapshot()
    rows=np.zeros((world.colonies,period.SLOTS,len(q.SCHEMA)),dtype=np.uint64)
    for col,count in enumerate(counts):
        count=int(count)
        if count:
            positions=tuple(col*f.Q+int(row[q.COL['address']]) for row in packed.unpack(stored[col,:count]))
            rows[col,:count]=q.array_from_cells(world.logical_cells(positions))
    flags=np.zeros((world.colonies*f.Q//64,2),dtype=np.uint64) if world._flags is None else world._flags.read()
    bits=[]
    for col in range(world.colonies):
        cells=world.logical_cells((col*f.Q+3,col*f.Q+f.Q-3));bits.append((cells[0].signal>>2,cells[1].signal>>2))
    return dict(bank=bank,active_rows=rows,counts=counts,flags=flags,signals=np.array(bits,dtype=np.uint64),age=np.array(world.age,dtype=np.uint64),time=np.array(world.time,dtype=np.uint64))


def assert_equal(first,second):
    a,b=snapshot(first),snapshot(second)
    for key in a:np.testing.assert_array_equal(a[key],b[key],err_msg=key)
    return a,b
