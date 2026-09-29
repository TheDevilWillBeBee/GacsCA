"""Lossless early snapshot views and flag attachment; no physical transitions."""
import numpy as np
from . import retimed_holder_rule as f,retimed_holder_quotient as q
from . import retimed_holder_wide_inert_storage as storage
from . import retimed_holder_contextual_flags as existing
from . import retimed_holder_early_flags_gpu as early,retimed_holder_resident_period as period


class View:
    def __init__(self,state,positions=(),values=None):
        if not 0<=int(state['age'])<32768:raise ValueError('early snapshot required')
        self.planes=state['flags'];n=len(state['bank'])
        if self.planes.dtype!=np.uint64 or self.planes.shape!=(n*f.Q//64,2):raise ValueError('complete flag planes required')
        rows=state['active_rows'].copy()
        for col,count in enumerate(state['counts']):
            part=rows[col,:int(count)];pos=col*f.Q+part[:,q.COL['address']].astype(np.int64)
            bits=(self.planes[pos//64] >> (pos%64).astype(np.uint64)[:,None])&np.uint64(1)
            np.testing.assert_array_equal(part[:,[q.COL['f1'],q.COL['f2']]],bits)
            part[:,[q.COL['f1'],q.COL['f2']]]=0
        self.base=storage.View(dict(state,active_rows=rows,flags=np.zeros_like(self.planes)),np.array([],dtype=np.int64),np.array([],dtype=np.uint64))
        self.size=self.base.size;self.positions=np.asarray(positions,dtype=np.int64)
        self.values=np.empty((0,f.FIELDS),dtype=np.uint64) if values is None else values
        if self.positions.ndim!=1 or self.values.dtype!=np.uint64 or self.values.shape!=(len(self.positions),f.FIELDS) or np.any(self.positions<0) or np.any(self.positions>=self.size) or np.any(np.diff(self.positions)<=0):raise ValueError('complete sorted exception records required')

    def cells(self,positions):
        positions=np.asarray(positions,dtype=np.int64)%self.size
        raw=self.base.cells(positions)
        raw[:,[f.COL['f1'],f.COL['f2']]]=(self.planes[positions//64] >> (positions%64).astype(np.uint64)[:,None])&np.uint64(1)
        indices=np.searchsorted(self.positions,positions);valid=np.flatnonzero(indices<len(self.positions))
        valid=valid[self.positions[indices[valid]]==positions[valid]]
        raw[valid]=self.values[indices[valid]]
        return raw


def attach(actual):
    actual._check();background=actual.reference
    if background._flags is not None:raise ValueError('already has flag storage')
    state,positions,values=existing.capture(actual);before=View(state,positions,values)
    planes=np.zeros_like(state['flags'])
    for col in range(len(state['bank'])):
        sites=np.arange(col*f.Q,(col+1)*f.Q);raw=before.cells(sites)
        assert np.array_equal(raw[:,f.COL['address']],sites%f.Q)
        assert np.all(raw[:,f.COL['age']]==background.age)
        assert not np.any(raw[:,[f.COL[f'w{k}_{name}'] for k in range(5) for name in ('wf1','wf2')]])
        for k,name in enumerate(('f1','f2')):
            bits=raw[:,f.COL[name]].reshape(-1,64)
            planes[col*f.Q//64:(col+1)*f.Q//64,k]=np.bitwise_or.reduce(bits << np.arange(64,dtype=np.uint64),axis=1)
    background._flags=early.World(tuple(map(int,state['signals'][:,1])),tuple(map(int,state['signals'][:,0])),age=background.age,initial=planes)
    background._snapshot=None;actual._check()
    if len(positions):
        different=np.empty(len(positions),dtype=np.uint64)
        if actual.lib.rf_normalize(actual.background.handle,actual.handle,period.pointer(different)):raise RuntimeError('early flag normalization failed')
        selected=np.flatnonzero(different).astype(np.uint64)
        if actual.lib.rf_commit(actual.handle,period.pointer(selected),len(selected)):raise RuntimeError('early flag compaction failed')
        actual._positions=actual._positions[selected.astype(np.intp)]
    after=View(*existing.capture(actual))
    for col in range(len(state['bank'])):
        sites=np.arange(col*f.Q,(col+1)*f.Q)
        np.testing.assert_array_equal(before.cells(sites),after.cells(sites))
    return dict(physical_transitions=0,complete_raw_words_verified=before.size*f.FIELDS,
                exceptions_before=len(positions),exceptions_after=len(actual.positions),
                flag1_bits=sum(int(x).bit_count() for x in planes[:,0]),
                flag2_bits=sum(int(x).bit_count() for x in planes[:,1]),
                device_flag_bytes=background._flags.device_bytes)
