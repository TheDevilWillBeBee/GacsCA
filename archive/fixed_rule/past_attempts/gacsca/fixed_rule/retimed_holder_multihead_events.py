"""CPU physical-event executor for a checked canonical late one-colony domain.

The alphabet, complete local evaluator and ROM are unchanged. Literal events
execute native full F followed by G projection. Transport moves all raw head
registers together and stops before any head's event or a possible interaction.
All Q logical Data words are retained, including storage outside the ROM core.
This is an execution restriction, not a depth restriction of the physical rule.
"""
import numpy as np
from . import retimed_holder_rule as f, retimed_holder_core as c
from . import retimed_holder_program as p, retimed_holder_native as native
from . import retimed_holder_literal_cone as cone

NAMES = tuple(n for n, _ in f.PROCEDURE)
COL = {name:i for i,name in enumerate(NAMES)}
CONTROL = [COL[n] for n in ('head', *c.CONTROL)]
MAIL = [i for i,n in enumerate(NAMES) if n.startswith(('lp_', 'rp_'))]
RAW_PROC = [f.COL['s2_'+n] for n in NAMES]
BARRIERS = sorted(set((*f.RESET_AGES, *f.ACTIVE_ENDS, *f.VOTE_AGES, f.CAPTURE_AGE-1, f.CAPTURE_AGE, f.WF_START-1, f.WF_END, f.U-1, f.U)))


class DomainError(ValueError):
    pass


class World:
    def __init__(self, raw, *, time=None):
        if not isinstance(raw, np.ndarray) or raw.dtype != np.uint64 or raw.shape != (f.Q, f.FIELDS):
            raise DomainError('one complete raw colony required by this executor')
        for i, (_, width) in enumerate(f.SCHEMA):
            if width < 64 and np.any(raw[:, i] >= np.uint64(1 << width)):
                raise DomainError('raw field width exceeded')
        if not np.array_equal(raw, cone.normalize(raw.copy())):
            raise DomainError('fixed metadata differs from the actual Address')
        if not np.array_equal(raw[:, f.COL['address']], np.arange(f.Q)):
            raise DomainError('canonical physical Addresses required')
        self.age = int(raw[0, f.COL['age']])
        if self.age >= f.U or np.any(raw[:, f.COL['age']] != self.age):
            raise DomainError('uniform legal physical Age required')
        self.time = self.age if time is None else time
        if type(self.time) is not int or self.time < 0 or self.time % f.U != self.age:
            raise DomainError('consistent absolute time required')
        if np.any(raw[:, [f.COL[n] for n in ('f1', 'f2', *(f'w{k}_{n}' for k in range(5) for n in ('wf1', 'wf2')))]]):
            raise DomainError('zero flags and Wf required')
        signal = raw[:, f.COL['signal']]
        for d in f.OFFSETS:
            if not np.array_equal((signal >> np.uint64(d+2)) & np.uint64(1), np.roll((signal >> np.uint64(2)) & np.uint64(1), -d)):
                raise DomainError('coherent stationary Signal copies required')
        self.words = raw[:, RAW_PROC].copy()
        for d in f.OFFSETS:
            for i,name in enumerate(NAMES):
                if not np.array_equal(raw[:, f.COL[f's{d+2}_{name}']], np.roll(self.words[:, i], -d)):
                    raise DomainError('all raw procedure copies must be coherent')
        self.base = raw.copy()
        self.rom = cone.rom()
        self.layout = p.layout()
        self.rom_rows = len(p.base_rom())
        self.native = native.library()
        self.input = np.empty((15, f.FIELDS), dtype=np.uint64)
        self.output = np.empty(f.FIELDS, dtype=np.uint64)
        self.literal_ticks = self.transport_ticks = self.quiet_ticks = self.bulk_ticks = self.local_evaluations = 0
        self.heads = self._validate_procedures()

    def _validate_procedures(self):
        if np.any(self.words[:, MAIL]):
            raise DomainError('mail is outside this transport domain')
        heads = tuple(map(int, np.flatnonzero(self.words[:, COL['head']])))
        if len(heads) > 32 or any(pos >= self.rom_rows for pos in heads):
            raise DomainError('at most 32 heads inside the ROM core required')
        occupied = set(heads)
        residues = np.flatnonzero(np.any(self.words[:, [COL[n] for n in c.CONTROL]], axis=1))
        if any(int(pos) not in occupied for pos in residues):
            raise DomainError('non-head controller residue cannot be omitted')
        return heads

    def raw(self):
        out = self.base.copy()
        out[:, f.COL['age']] = self.age
        for d in f.OFFSETS:
            for i,name in enumerate(NAMES):
                out[:, f.COL[f's{d+2}_{name}']] = np.roll(self.words[:, i], -d)
        return out

    def _head_plan(self, pos):
        row = self.words[pos]
        get = lambda name:int(row[COL[name]])
        if get('direction'):
            return pos, -1, False
        kind,index = map(int, self.rom[pos, :2])
        if get('phase') == c.FETCH and kind == c.WAIT and index == get('pc') and get('rd'):
            return get('rd'), 0, True
        target = self.rom_rows-1
        phase = get('phase')
        candidate = None
        if phase == c.FETCH and get('pc') < self.rom_rows-self.layout.memory_count-1:
            candidate = self.layout.memory_count+get('pc')
        elif phase in (c.READ_A, c.TRANSMIT, c.READ_LOAD) and get('ra') < self.layout.memory_count:
            candidate = get('ra')
        elif phase == c.READ_B and get('rb') < self.layout.memory_count:
            candidate = get('rb')
        elif phase == c.WRITE and get('rd') < self.layout.memory_count:
            candidate = get('rd')
        elif phase == c.READ_META and get('value') and get('rd') < self.rom_rows:
            candidate = get('rd')
        if candidate is not None and pos <= candidate < target:
            target = candidate
        return target-pos, 1, False

    def transport_plan(self, limit):
        plans = {pos:self._head_plan(pos) for pos in self.heads}
        amount = min([limit, *(row[0] for row in plans.values())])
        # Equal velocities preserve their relative positions, even when adjacent.
        # Different velocities use a conservative separation bound; nearby heads
        # must take literal simultaneous steps, including crossing/merging cases.
        for i,a in enumerate(self.heads):
            for b in self.heads[i+1:]:
                if plans[a][1] != plans[b][1]:
                    amount = min(amount, max(0, (b-a-2)//2))
        return amount, plans

    def _transport(self, amount, plans):
        old = {pos:self.words[pos, CONTROL].copy() for pos in self.heads}
        if self.heads:
            self.words[np.ix_(self.heads, CONTROL)] = 0
        destinations = []
        for pos, row in old.items():
            _, velocity, waiting = plans[pos]
            dest = pos+velocity*amount
            if waiting:
                row[CONTROL.index(COL['rd'])] -= np.uint64(amount)
            self.words[dest, CONTROL] = row
            destinations.append(dest)
        assert len(set(destinations)) == len(destinations)
        self.heads = tuple(sorted(destinations))
        self.age += amount
        self.time += amount
        self.transport_ticks += amount

    def literal(self):
        candidates = sorted({(pos+d) % f.Q for pos in self.heads for d in (-1, 0, 1)})
        updates = []
        for center in candidates:
            positions = (center+np.arange(-7, 8)) % f.Q
            self.input[:] = self.base[positions]
            self.input[:, f.COL['age']] = self.age
            for d in f.OFFSETS:
                self.input[:, [f.COL[f's{d+2}_{n}'] for n in NAMES]] = self.words[(positions+d) % f.Q]
            self.native.retimed_holder_local(native.pointer(self.input), native.pointer(self.output))
            assert int(self.output[f.COL['address']]) == center and int(self.output[f.COL['age']]) == (self.age+1) % f.U
            assert not np.any(self.output[[f.COL['f1'], f.COL['f2']]])
            updates.append(self.output[RAW_PROC].copy())
        for pos, row in zip(candidates, updates):
            self.words[pos] = row
        self.age = (self.age+1) % f.U
        self.time += 1
        self.literal_ticks += 1
        self.local_evaluations += len(candidates)
        # The previously checked state has no live records outside this causal
        # candidate set. Validate every changed row, retaining the full state
        # even if an unsupported packet/controller causes a domain stop.
        heads = []
        for pos, row in zip(candidates, updates):
            if any(row[i] for i in MAIL):
                raise DomainError('mail is outside this transport domain')
            if row[COL['head']]:
                if pos >= self.rom_rows:
                    raise DomainError('head left the ROM execution domain')
                heads.append(pos)
            elif any(row[COL[n]] for n in c.CONTROL):
                raise DomainError('non-head controller residue cannot be omitted')
        if len(heads) > 32:
            raise DomainError('bounded live-head capacity exceeded')
        self.heads = tuple(heads)

    def bulk(self):
        # Every physical output is executed at clock-wide events, including
        # Info commit and next-period reset; no decoder installs a successor.
        new = cone.step(self.raw())
        advanced = World(new, time=self.time+1)
        self.base, self.words, self.heads = advanced.base, advanced.words, advanced.heads
        self.age, self.time = advanced.age, advanced.time
        self.bulk_ticks += 1
        self.local_evaluations += f.Q

    def advance(self, ticks, *, event_budget=1000000):
        if type(ticks) is not int or ticks < 0 or type(event_budget) is not int or event_budget < 1:
            raise ValueError('bounded nonnegative duration and event budget required')
        stop = self.time+ticks
        events = 0
        while self.time < stop:
            if events >= event_budget:
                raise RuntimeError('event budget exhausted; exact physical state retained')
            if self.age in (*f.RESET_AGES, *f.VOTE_AGES, f.CAPTURE_AGE-1, f.WF_START-1, f.U-1):
                self.bulk(); events += 1; continue
            if f.WF_START <= self.age <= f.WF_END+f.Q:
                raise DomainError('forcing/flag interval requires another exact executor')
            amount = min(stop-self.time, min(t-self.age for t in BARRIERS if t > self.age))
            if not c.active(self.age):
                self.age += amount; self.time += amount; self.quiet_ticks += amount; continue
            jump, plans = self.transport_plan(amount)
            if jump:
                self._transport(jump, plans)
            else:
                self.literal(); events += 1
        return dict(time=self.time, age=self.age, head_positions=list(self.heads), literal_ticks=self.literal_ticks, transport_ticks=self.transport_ticks, quiet_ticks=self.quiet_ticks, bulk_ticks=self.bulk_ticks, full_local_evaluations=self.local_evaluations)
