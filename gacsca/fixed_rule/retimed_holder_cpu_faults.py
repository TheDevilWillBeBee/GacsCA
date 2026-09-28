"""Bounded literal projected-G exceptions over the canonical CPU reference.

G=pi F iota is fixed at every physical site, including faulty geometry. All 105
mutable words are stored; metadata is normalized by the same fixed ROM at every
tick. Background acceleration is used only outside the exact defect light cone.
Coherent Data absorption is an equality-preserving representation change, never
a transition, correction, or replacement by a healthy/upper reference.
"""
from functools import lru_cache
import numpy as np

from . import retimed_holder_cpu_general as general, retimed_holder_cpu_events as events
from . import retimed_holder_rule as f, retimed_holder_projected as r
from . import retimed_holder_core as c, retimed_holder_native as native
from . import retimed_holder_program as p


STATE = ('data','heads','where','packets','flags','left','right','age','time')
BOUNDARIES = frozenset((*c.RESET_AGES,*c.VOTE_AGES,c.CAPTURE_AGE-1,f.U-1))


class World:
    def __init__(self, background, *, capacity=1024, frontier_capacity=4096):
        if type(background) is not general.World:
            raise TypeError('the retimed general-context physical reference is required')
        if type(capacity) is not int or type(frontier_capacity) is not int or not 1<=capacity<=frontier_capacity<=4096:
            raise ValueError('bounded exception/frontier capacities required')
        self.background = background; self.sites = background.n*f.Q
        self.capacity = capacity; self.frontier_capacity = frontier_capacity
        self.exceptions = {}; self._time = background.time

    @property
    def time(self):
        return self._time

    @property
    def age(self):
        return self.background.age

    @property
    def positions(self):
        return tuple(sorted(self.exceptions))

    def _check(self):
        if self.background.time != self.time:
            raise ValueError('background advanced outside exception owner')

    def cell(self, position):
        self._check(); position %= self.sites
        if position in self.exceptions:
            return r.lift(self.exceptions[position])
        return self.background.cell(position)

    def inject(self, replacements):
        """External simultaneous replacements, not a physical transition."""
        self._check(); replacements = dict(replacements)
        if any(type(pos) is not int or not 0<=pos<self.sites or not isinstance(cell,r.Cell)
               for pos,cell in replacements.items()):
            raise ValueError('in-ring complete projected physical replacements required')
        changed = dict(self.exceptions)
        for pos,cell in replacements.items():
            if cell == r.project(self.background.cell(pos)):
                changed.pop(pos,None)
            else:
                changed[pos] = cell
        if len(changed)>self.capacity:
            raise ValueError('exception capacity exceeded before injection')
        self.exceptions = changed

    def _background(self, ticks):
        """Advance only physical fields, splitting at actual clock predicates."""
        remaining = ticks; calls = 0
        while remaining:
            age = self.background.age
            if age in BOUNDARIES:
                row = self.background.step(); amount = 1
            else:
                interval = next(((lo,hi) for lo,hi in events.regular_intervals() if lo<=age<=hi),None)
                if interval is not None:
                    amount = min(remaining,interval[1]-age+1)
                    row = self.background.advance(amount)
                else:
                    stop = min(at for at in BOUNDARIES if at>age)
                    amount = min(remaining,stop-age)
                    row = self.background.quiet_advance(amount)
            calls += row['full_raw_evaluations']; remaining -= amount
        return calls

    def step(self):
        self._check()
        if not self.exceptions:
            calls = self._background(1); self._time = self.background.time
            return dict(physical_ticks=1,candidates=0,exceptions=0,exception_F_calls=0,background_F_calls=calls)
        affected = sorted({(pos-delta)%self.sites for pos in self.exceptions for delta in f.NEIGHBORHOOD})
        if len(affected)>self.frontier_capacity:
            raise ValueError('causal frontier capacity exceeded before state change')
        # Only fixed-radius physical G transitions evolve the actual exceptions.
        read = lru_cache(maxsize=256)(self.cell)
        try:
            actual = {pos:r.project(native.local_step(tuple(read(pos+d) for d in f.NEIGHBORHOOD)))
                      for pos in affected}
        finally:
            read.cache_clear()
        old = tuple(getattr(self.background,name) for name in STATE)
        try:
            calls = self._background(1)
            changed = {pos:cell for pos,cell in actual.items() if cell != r.project(self.background.cell(pos))}
            if len(changed)>self.capacity:
                raise ValueError('next exception capacity exceeded')
        except BaseException:
            for name,value in zip(STATE,old):
                setattr(self.background,name,value)
            raise
        self.exceptions = changed; self._time = self.background.time
        return dict(physical_ticks=1,candidates=len(affected),exceptions=len(changed),
                    exception_F_calls=len(affected),background_F_calls=calls)

    def absorb_data(self):
        """Rebase only equal copies of actual MEM Data, retaining wrong values."""
        self._check()
        if not self.exceptions:
            return dict(data_cells=0,exceptions=0)
        actual = dict(self.exceptions); targets = sorted({(pos+d)%self.sites for pos in actual for d in f.OFFSETS})
        updates = []
        for primary in targets:
            col,address = divmod(primary,f.Q)
            if r.record(address)['kind'] != c.MEM:
                continue
            holders = tuple((primary+d)%self.sites for d in f.OFFSETS)
            values = tuple(getattr(self.cell(pos),f's{2-d}_data') for d,pos in zip(f.OFFSETS,holders))
            if len(set(values)) == 1 and values[0] != int(self.background.data[col,address]):
                if not all(pos in actual for pos in holders):
                    raise AssertionError('rebase would alter an unrepresented physical holder')
                updates.append((col,address,values[0]))
        if not updates:
            return dict(data_cells=0,exceptions=len(actual))
        old_data = self.background.data; data = old_data.copy()
        for col,address,value in updates:
            data[col,address] = value
        self.background.data = data
        try:
            changed = {pos:cell for pos,cell in actual.items() if cell != r.project(self.background.cell(pos))}
            self.exceptions = changed
            assert all(r.project(self.cell(pos)) == cell for pos,cell in actual.items()), 'rebase changed actual physical state'
        except BaseException:
            self.background.data = old_data; self.exceptions = actual
            raise
        return dict(data_cells=len(updates),exceptions=len(changed))

    def advance(self, ticks, *, absorb_data=True, literal_budget=4096):
        self._check()
        if type(ticks) is not int or ticks<0 or type(literal_budget) is not int or not 1<=literal_budget<=100000:
            raise ValueError('nonnegative duration and bounded literal budget required')
        stop = self.time+ticks; literal = fast = rebased = calls = 0
        while self.time<stop:
            if self.exceptions:
                if literal>=literal_budget:
                    raise RuntimeError('literal defect budget exhausted; exact current state retained')
                calls += self.step()['exception_F_calls']; literal += 1
                if absorb_data:
                    rebased += self.absorb_data()['data_cells']
            else:
                amount = stop-self.time
                try:
                    self._background(amount)
                finally:
                    self._time = self.background.time
                fast += amount
        return dict(time=self.time,literal_exception_ticks=literal,coherent_accelerated_ticks=fast,
                    rebased_data_cells=rebased,exception_F_calls=calls,exceptions=len(self.exceptions))

    def decode(self):
        self._check(); result = []
        for col in range(self.background.n):
            raw = f.decode_cell(tuple(self.cell(col*f.Q+a).s2_data for a in p.layout().info))
            value = r.project(raw)
            if r.lift(value) != raw:
                raise ValueError('decoded metadata is not normalized from represented Address')
            result.append(value)
        return tuple(result)
