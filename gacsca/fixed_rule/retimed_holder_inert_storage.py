"""Exact retained-Data representation for the audited next-period state.

The descriptor certificate proves the overlay is constant and independent of
all other physical outputs under canonical geometry. GPU evolution uses the
existing fixed rule; initialization uploads actual banks, including malformed
encoded metadata. No transition or Info normalization runs on the host.
"""
import hashlib
import json
from pathlib import Path
import numpy as np
from . import retimed_holder_rule as f,retimed_holder_quotient as q
from . import retimed_holder_projected as r,retimed_holder_program as p
from . import retimed_holder_resident_general as general,retimed_holder_resident_period as period
from . import retimed_holder_cuda_general_snapshot as snapshots
from . import retimed_holder_active_snapshot as active
from . import retimed_holder_literal_cone as cone

NAMES = tuple(n for n,_ in f.PROCEDURE)
DATA = NAMES.index('data')
CERTIFICATE = Path('figs/fixed_rule/retimed_holder_inert_data_v3.json')


def certificate():
    result = json.loads(CERTIFICATE.read_text())
    assert result['passed'] and result['descriptor_sha256'] == f.self_description().digest()
    assert result['selected_addresses'] == [30960,30961,30962]
    assert result['all_legal_ages'] == f.U and result['unchanged_Data_copies'] == 15
    for path,digest in result['source_sha256'].items():
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == digest,path
    return result


def raw_words(words,signals,age,sites):
    """Bounded read-only canonical coherent raw encoding of every procedure."""
    sites = np.asarray(sites,dtype=np.int64)
    if sites.ndim != 1 or len(sites)>65536:
        raise ValueError('bounded physical read required')
    sites = sites % len(words)
    result = np.zeros((len(sites),f.FIELDS),dtype=np.uint64)
    result[:,f.COL['address']] = sites % f.Q
    result[:,f.COL['age']] = age
    result[:,f.COL['signal']] = signals[sites]
    cone.normalize(result)
    for d in f.OFFSETS:
        result[:,[f.COL[f's{d+2}_{n}'] for n in NAMES]] = words[(sites+d)%len(words)]
    return result


class View:
    """Complete unflagged diagnostic view; no call is an evolution operation."""
    def __init__(self,state,positions,values):
        logical = active.logical(state,max_bytes=2*1024**3)
        self.words = logical[:,[q.COL[n] for n in NAMES]].copy()
        self.signals = logical[:,q.COL['signal']].copy()
        self.age,self.size = int(state['age']),len(logical)
        self.words[positions,DATA] = values
    def cells(self,sites):
        return raw_words(self.words,self.signals,self.age,sites)


class World:
    def __init__(self,words,signals,*,time,device_budget=32*1024**2):
        proof = certificate()
        if not isinstance(words,np.ndarray) or words.dtype!=np.uint64 or words.ndim!=2 or words.shape[1]!=len(NAMES) or len(words)%f.Q or not f.Q<=len(words)<=128*f.Q:
            raise ValueError('bounded complete procedure words required')
        if not isinstance(signals,np.ndarray) or signals.dtype!=np.uint64 or signals.shape!=(len(words),) or np.any(signals>=32):
            raise ValueError('complete typed Signal words required')
        if type(time) is not int or time<0 or time%f.U!=1:
            raise ValueError('actual post-reset Age-one entry required')
        for i,(_,width) in enumerate(f.PROCEDURE):
            if width<64 and np.any(words[:,i]>=np.uint64(1<<width)):
                raise ValueError('procedure field outside fixed alphabet')
        g = p.layout()
        n,age = len(words)//f.Q,time%f.U
        address = np.arange(len(words))%f.Q
        outside = (address>=g.memory_count)&(address<f.Q-5)&(words[:,DATA]!=0)
        self.positions = np.flatnonzero(outside)
        if not set((self.positions%f.Q).tolist())<=set(proof['selected_addresses']):
            raise ValueError('uncertified out-of-bank Data cannot be dropped')
        self.values = words[self.positions,DATA].copy()
        self.positions.flags.writeable = self.values.flags.writeable = False
        bank = np.empty((n,g.memory_count+5),dtype=np.uint64)
        records = np.zeros((n,period.SLOTS,len(q.SCHEMA)),dtype=np.uint64)
        counts = np.zeros(n,dtype=np.uint64)
        bits = np.empty((n,2),dtype=np.uint64)
        sparse = {}
        control = [i for i,name in enumerate(NAMES) if name!='data']
        for col in range(n):
            begin = col*f.Q
            part = words[begin:begin+f.Q]
            bank[col] = np.concatenate((part[:g.memory_count,DATA],part[-5:,DATA]))
            live = np.flatnonzero(np.any(part[:,control],axis=1)|(signals[begin:begin+f.Q]!=0))
            if len(live)>period.SLOTS:
                raise ValueError('bounded resident active-record capacity exceeded')
            counts[col] = len(live)
            for index,a in enumerate(live):
                row = records[col,index]
                row[q.COL['address']],row[q.COL['age']] = a,age
                row[q.COL['signal']] = signals[begin+a]
                row[[q.COL[name] for name in NAMES]] = part[a]
                if g.memory_count<=a<f.Q-5:
                    row[q.COL['data']] = 0
                sparse[begin+int(a)] = q.decode_cell(row)
            bits[col] = ((signals[begin+3]>>np.uint64(2))&np.uint64(1),(signals[begin+f.Q-3]>>np.uint64(2))&np.uint64(1))
        expected = dict(bank=bank,active_rows=records,counts=counts,flags=np.zeros((n*f.Q//64,2),dtype=np.uint64),signals=bits,age=np.array(age,dtype=np.uint64),time=np.array(time,dtype=np.uint64))
        # Independent existing snapshot validator checks complete record widths,
        # canonical geometry, Data consistency and every localized Signal bit.
        represented = View(expected,self.positions,self.values)
        for start in range(0,len(words),f.Q):
            sites = np.arange(start,start+f.Q)
            np.testing.assert_array_equal(represented.cells(sites),raw_words(words,signals,age,sites))
        self.reference = general.World((r.Cell(),)*n,age=age,logical=sparse,device_budget=device_budget)
        try:
            for col in range(n):
                data = np.ascontiguousarray(bank[col])
                if self.reference._core.lib.rp_bank(self.reference._core.handle,col,period.pointer(data)):
                    raise RuntimeError('complete actual bank upload failed')
            self.reference._core.time = time
            restored = snapshots.snapshot(self.reference)
            for key in expected:
                np.testing.assert_array_equal(restored[key],expected[key],err_msg=key)
            actual = View(restored,self.positions,self.values)
            for start in range(0,len(words),f.Q):
                sites = np.arange(start,start+f.Q)
                np.testing.assert_array_equal(actual.cells(sites),raw_words(words,signals,age,sites))
            self.initialization = dict(physical_transitions=0,complete_raw_words_verified=len(words)*f.FIELDS,retained_positions=self.positions.tolist(),retained_values=self.values.tolist(),actual_encoded_metadata_uploaded_without_normalization=True)
        except BaseException:
            self.reference.close()
            raise

    @property
    def time(self):return self.reference.time
    @property
    def age(self):return self.reference.age
    @property
    def device_bytes(self):return self.reference.device_bytes
    def close(self):self.reference.close()
    def __enter__(self):return self
    def __exit__(self,*args):self.close()
    def advance(self,ticks,**kwargs):return self.reference.advance(ticks,**kwargs)
    def snapshot(self):return snapshots.snapshot(self.reference)
    def view(self):return View(self.snapshot(),self.positions,self.values)
