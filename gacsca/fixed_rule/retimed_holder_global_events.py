"""Physical event scheduling on a complete bounded multi-colony ring.

Uses the unchanged native local rule and the guarded transport algorithm from
multihead_events. All neighbors and procedure copies address the global ring.
The allocation bound is an executor restriction, not a hierarchy parameter.
"""
import numpy as np
from . import retimed_holder_multihead_events as single
from . import retimed_holder_rule as f, retimed_holder_core as c
from . import retimed_holder_program as p, retimed_holder_native as native
from . import retimed_holder_literal_cone as cone

NAMES, COL, CONTROL, MAIL, RAW_PROC = single.NAMES, single.COL, single.CONTROL, single.MAIL, single.RAW_PROC
DomainError = single.DomainError


class World(single.World):
    def __init__(self, cells, *, size, time):
        if type(size) is not int or size % f.Q or not f.Q <= size <= 128*f.Q:
            raise DomainError('bounded complete colony ring required')
        if type(time) is not int or time < 0:
            raise DomainError('nonnegative physical time required')
        self.size, self.time, self.age = size, time, time % f.U
        self.rom, self.layout = cone.rom(), p.layout()
        self.rom_rows = len(p.base_rom())
        self.template = np.zeros((f.Q,f.FIELDS),dtype=np.uint64)
        self.template[:,f.COL['address']] = np.arange(f.Q)
        cone.normalize(self.template)
        self.words = np.empty((size,len(NAMES)),dtype=np.uint64)
        self.signals = np.empty(size,dtype=np.uint64)
        for start in range(0,size,f.Q):
            sites = np.arange(start,start+f.Q)
            raw = cells(sites)
            if raw.dtype != np.uint64 or raw.shape != (f.Q,f.FIELDS):
                raise DomainError('every complete raw physical field required')
            for i,(_,width) in enumerate(f.SCHEMA):
                if width < 64 and np.any(raw[:,i] >= np.uint64(1 << width)):
                    raise DomainError('raw field width exceeded')
            self.words[sites] = raw[:,RAW_PROC]
            self.signals[sites] = raw[:,f.COL['signal']]
        for d in f.OFFSETS:
            if not np.array_equal((self.signals >> np.uint64(d+2)) & np.uint64(1),np.roll((self.signals >> np.uint64(2)) & np.uint64(1),-d)):
                raise DomainError('coherent stationary Signal copies required')
        # Reconstruction equality checks all raw metadata, geometry, flags,
        # Wf and controller copies against the actual global neighborhood.
        for start in range(0,size,f.Q):
            sites = np.arange(start,start+f.Q)
            if not np.array_equal(cells(sites),self.cells(sites)):
                raise DomainError('canonical geometry and coherent global raw copies required')
        self.native = native.library()
        self.output = np.empty(f.FIELDS,dtype=np.uint64)
        self.literal_ticks = self.transport_ticks = self.quiet_ticks = self.bulk_ticks = self.local_evaluations = 0
        self.heads = self._validate_procedures()
        self.trace = []

    def cells(self, sites, *, words=None, signals=None, age=None):
        sites = np.asarray(sites,dtype=np.int64)
        if sites.ndim != 1 or len(sites) > 65536:
            raise DomainError('bounded physical read required')
        sites = sites % self.size
        words = self.words if words is None else words
        signals = self.signals if signals is None else signals
        age = self.age if age is None else age
        raw = self.template[sites % f.Q].copy()
        raw[:,f.COL['age']] = age
        raw[:,f.COL['signal']] = signals[sites]
        for d in f.OFFSETS:
            raw[:,[f.COL[f's{d+2}_{n}'] for n in NAMES]] = words[(sites+d)%self.size]
        return raw

    def raw(self):
        raise DomainError('use bounded cells() to read the complete global state')

    def _validate_procedures(self):
        if np.any(self.words[:,MAIL]):
            raise DomainError('mail is outside this transport domain')
        heads = tuple(map(int,np.flatnonzero(self.words[:,COL['head']])))
        if len(heads) > 32*(self.size//f.Q) or any(pos % f.Q >= self.rom_rows for pos in heads):
            raise DomainError('bounded heads inside each ROM core required')
        residues = np.flatnonzero(np.any(self.words[:,[COL[n] for n in c.CONTROL]],axis=1))
        occupied = set(heads)
        if any(int(pos) not in occupied for pos in residues):
            raise DomainError('non-head controller residue cannot be omitted')
        return heads

    def _head_plan(self, pos):
        row, address = self.words[pos],pos % f.Q
        get = lambda name:int(row[COL[name]])
        if get('direction'):
            return address,-1,False
        kind,index = map(int,self.rom[address,:2])
        if get('phase') == c.FETCH and kind == c.WAIT and index == get('pc') and get('rd'):
            return get('rd'),0,True
        target,candidate = self.rom_rows-1,None
        phase = get('phase')
        if phase == c.FETCH and get('pc') < self.rom_rows-self.layout.memory_count-1:
            candidate = self.layout.memory_count+get('pc')
        elif phase in (c.READ_A,c.TRANSMIT,c.READ_LOAD) and get('ra') < self.layout.memory_count:
            candidate = get('ra')
        elif phase == c.READ_B and get('rb') < self.layout.memory_count:
            candidate = get('rb')
        elif phase == c.WRITE and get('rd') < self.layout.memory_count:
            candidate = get('rd')
        elif phase == c.READ_META and get('value') and get('rd') < self.rom_rows:
            candidate = get('rd')
        if candidate is not None and address <= candidate < target:
            target = candidate
        return target-address,1,False

    def _transport(self, amount, plans):
        before = self.time
        super()._transport(amount,plans)
        self.trace.append((0,before,amount))

    def literal(self):
        before = self.time
        candidates = sorted({(pos+d)%self.size for pos in self.heads for d in (-1,0,1)})
        updates = []
        for center in candidates:
            inputs = self.cells(center+np.arange(-7,8))
            self.native.retimed_holder_local(native.pointer(inputs),native.pointer(self.output))
            assert int(self.output[f.COL['address']]) == center % f.Q
            assert int(self.output[f.COL['age']]) == (self.age+1)%f.U
            assert not np.any(self.output[[f.COL['f1'],f.COL['f2']]])
            updates.append(self.output[RAW_PROC].copy())
        heads = []
        for pos,row in zip(candidates,updates):
            self.words[pos] = row
        self.age,self.time = (self.age+1)%f.U,self.time+1
        self.literal_ticks += 1
        self.local_evaluations += len(candidates)
        for pos,row in zip(candidates,updates):
            if any(row[i] for i in MAIL):
                raise DomainError('mail is outside this transport domain')
            if row[COL['head']]:
                if pos % f.Q >= self.rom_rows:
                    raise DomainError('head left closed ROM domain')
                heads.append(pos)
            elif any(row[COL[n]] for n in c.CONTROL):
                raise DomainError('non-head controller residue cannot be omitted')
        if len(heads) > 32*(self.size//f.Q):
            raise DomainError('bounded head capacity exceeded')
        self.heads = tuple(heads)
        self.trace.append((1,before,1))

    def bulk(self):
        # Read every block from the same OLD global state, including its true
        # radius-seven halo; only after all outputs exist can state advance.
        before = self.time
        raw = np.empty((self.size,f.FIELDS),dtype=np.uint64)
        for start in range(0,self.size,f.Q):
            raw[start:start+f.Q] = cone.step(self.cells(np.arange(start-7,start+f.Q+7)))[7:-7]
        words,signals = raw[:,RAW_PROC].copy(),raw[:,f.COL['signal']].copy()
        age = (self.age+1)%f.U
        for start in range(0,self.size,f.Q):
            sites = np.arange(start,start+f.Q)
            if not np.array_equal(raw[sites],self.cells(sites,words=words,signals=signals,age=age)):
                raise DomainError('clock output left canonical coherent execution domain')
        self.words,self.signals,self.age,self.time = words,signals,age,self.time+1
        self.heads = self._validate_procedures()
        self.bulk_ticks += 1
        self.local_evaluations += self.size
        self.trace.append((2,before,1))
