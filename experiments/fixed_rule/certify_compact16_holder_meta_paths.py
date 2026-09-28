"""Composition of certified full-raw local events into actual fixed-ROM META paths.

Diagnostic only, never an evolution backend. A path is a finite sequence of
certified singleton events and invariant flights. Counts/positions are affine in
the query, so induction guards and duration are checked over whole query ranges.
"""
import argparse
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
import resource
import time
from pathlib import Path

import numpy as np
from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_core as c, compact16_holder_program as p
from experiments.fixed_rule import certify_compact16_holder_clock_events as clock
from experiments.fixed_rule.audit_small_holder_position_events import sha
from gacsca.fixed_rule.wordcode import ADD


@dataclass(frozen=True)
class Affine:
    q: int = 0
    k: int = 0

    def __add__(self, other):
        other = other if isinstance(other, Affine) else Affine(k=other)
        return Affine(self.q + other.q, self.k + other.k)

    def __sub__(self, other):
        other = other if isinstance(other, Affine) else Affine(k=other)
        return Affine(self.q - other.q, self.k - other.k)

    def times(self, factor):
        return Affine(self.q * factor, self.k * factor)

    def bounds(self, domain):
        values = [self.q * x + self.k for x in domain]
        return min(values), max(values)

    def word(self, terms, query):
        if self.q == 0:
            return terms.const(self.k)
        if self.q == 1:
            return terms.op(ADD, query, terms.const(self.k))
        raise ValueError('only nonnegative-position query or constant words are needed')

    def pair(self):
        return (self.q, self.k)


def nonempty_domain(count, domain):
    lo, hi = domain
    if count.q == 0:
        return domain if count.k >= 1 else None
    if count.q == 1:
        lo = max(lo, 1 - count.k)
    elif count.q == -1:
        hi = min(hi, count.k - 1)
    else:
        raise ValueError('unsupported loop count slope')
    return (lo, hi) if lo <= hi else None


class Words(clock.Intervals):
    def basic_lookup(self, address, selector):
        if selector >= len(c.STATIC):
            return self.const(0)
        value = self.value(address)
        if value is None:
            return self.intern(('rom', address, selector))
        return self.const(self.rom[value, selector] if value < len(self.rom)
                          else c.fallback(value, selector))

    def lookup(self, address, selector):
        value = self.value(address)
        if value is not None:
            return self.basic_lookup(address, selector)
        lo, hi = self.bounds(address)
        if not 0 <= lo <= hi < f.Q:
            return self.basic_lookup(address, selector)
        if lo == hi:
            return self.basic_lookup(self.const(lo), selector)
        if hi < len(self.rom):
            column = self.rom[lo:hi+1, selector]
            if selector == 1 and np.array_equal(column, np.arange(lo, hi+1, dtype=np.uint64)):
                return address
            if np.all(column == column[0]):
                return self.const(int(column[0]))
        elif lo >= len(self.rom):
            if selector == 1:
                return address
            values = {c.fallback(x, selector) for x in (lo, hi)}
            if len(values) == 1:
                return self.const(values.pop())
        return self.basic_lookup(address, selector)


EVENTS = {(event['family'], event['name']): event for event in clock.cases()}
LAST_LEFT = ('scan', 'left_flight_last')


def leaf_prepare(key, interval):
    if key != LAST_LEFT:
        return clock.prepare(EVENTS[key], interval)
    terms, original = clock.prepare(EVENTS[('scan', 'left_flight')], interval)

    def raw(pos, after=False):
        values = list(original(pos, after=after))
        for offset in f.STATIC_OFFSETS:
            if pos + offset == 0:
                values[f.COL[f'p{offset+3}_last']] = terms.const(1)
        return tuple(values)
    return terms, raw


def prove_last_left(interval):
    terms, raw = leaf_prepare(LAST_LEFT, interval)
    desc = f.self_description()
    for pos in range(-4, 5):
        actual = terms.expression(desc, tuple(w for j in f.NEIGHBORHOOD for w in raw(pos+j)))
        expected = raw(pos, after=True)
        assert actual == expected, ('last-marked left flight', interval, pos)
    return dict(interval=interval, full_raw_outputs=9*f.FIELDS, passed=True)


@lru_cache(None)
def template(key):
    terms, raw = leaf_prepare(key, clock.regular_intervals()[0])
    before = raw(0)
    destinations = [offset for offset in (-1, 0, 1)
                    if terms.value(raw(offset, after=True)[f.COL['s2_head']]) == 1]
    assert len(destinations) == 1, ('not a single-head event', key)
    shift = destinations[0]
    return terms, before, raw(shift, after=True), raw(0, after=True), shift


class MetaPath:
    def __init__(self, pc, query_domain):
        self.g = p.layout()
        self.rom = p.base_rom()
        self.t = Words(self.rom)
        self.pc = pc
        self.op = self.g.instructions[pc]
        assert self.op.kind == c.META
        self.m = self.g.memory_count + pc
        self.d = self.op.a
        self.selector = self.op.b
        self.L = len(self.rom)
        assert 0 <= self.d < self.g.memory_count <= self.m < self.L-1
        assert 0 <= self.selector < 7
        self.domain = query_domain
        lo, hi = query_domain
        self.query = self.t.const(lo) if lo == hi else self.t.bounded('query', (f.Q-1).bit_length(), lo, hi)
        self.initial = {name: self.t.variable('initial_'+name, dict(c.SCHEMA)[name]) for name in c.CONTROL}
        self.initial.update(phase=self.t.const(c.FETCH), pc=self.t.const(pc),
                            rd=self.query, direction=self.t.const(c.RIGHT))
        self.control = dict(self.initial)
        self.position = Affine(k=self.m)
        self.elapsed = Affine()
        self.steps = []
        self.writes = []

    def event(self, key, *, count=Affine(k=1), loop=False):
        assert count.bounds(self.domain)[0] >= 0, ('negative count', key, count)
        domain = nonempty_domain(count, self.domain)
        if domain is None:
            self.steps.append(dict(leaf=key, count=count.pair(), empty=True))
            return
        source, before, after, own_after, shift = template(key)
        if not loop:
            assert count == Affine(k=1)
        elif shift not in (-1, 1):
            raise AssertionError('flight must move one site')
        last = self.position + (count - 1).times(shift)
        minimum = min(self.position.bounds(domain)[0], last.bounds(domain)[0])
        maximum = max(self.position.bounds(domain)[1], last.bounds(domain)[1])
        assert 0 <= minimum <= maximum < self.L
        if loop:
            head = self.t.const(minimum) if minimum == maximum else self.t.bounded('flight_head_'+str(len(self.steps)), (f.Q-1).bit_length(), minimum, maximum)
        else:
            head = self.position.word(self.t, self.query)
        memory = self.t.variable('old_data_'+str(len(self.steps)), 64)
        mapping = {}

        def transfer(x):
            if x in mapping:
                return mapping[x]
            node = source.nodes[x]
            if node[0] == 'const':
                y = self.t.const(node[1])
            elif node[0] == 'variable':
                name = node[1]
                if name.startswith('fetch_old_'):
                    y = self.control[name[len('fetch_old_'):]]
                elif name.startswith('old_'):
                    y = self.control[name[len('old_'):]]
                elif name == 'base_address':
                    y = head
                elif name.startswith('meta_0_'):
                    y = self.t.lookup(head, c.STATIC.index(name[len('meta_0_'):]))
                elif name == 'data_0':
                    y = memory
                else:
                    raise AssertionError(('unexpected controller dependency', key, node))
            elif node[0] == 'op':
                y = self.t.op(node[1], transfer(node[2]), transfer(node[3]))
            elif node[0] == 'not':
                y = self.t.inv(transfer(node[1]))
            elif node[0] == 'modadd':
                y = self.t.modular_add(transfer(node[1]), node[2], node[3])
            else:
                raise AssertionError(node)
            mapping[x] = y
            return y

        # Instantiate the lemma's actual old controller and structural conditions.
        for name in c.CONTROL:
            got = transfer(before[f.COL['s2_'+name]])
            assert got == self.control[name], ('old controller does not match', key, name)
        for selector, name in enumerate(c.STATIC):
            got = transfer(before[f.COL['p3_'+name]])
            wanted = self.t.lookup(head, selector)
            assert got == wanted, ('ROM precondition does not hold', key, name, minimum, maximum)
        for a, b in source.disequalities:
            a, b = transfer(a), transfer(b)
            if self.t.value(self.t.op(c.EQ, a, b)) == 0:
                continue
            if {a, b} == {head, self.query} and loop:
                delta_a = (self.position - Affine(q=1)).bounds(domain)
                delta_b = (last - Affine(q=1)).bounds(domain)
                assert max(delta_a[1], delta_b[1]) < 0 or min(delta_a[0], delta_b[0]) > 0, ('search may hit', key)
            else:
                raise AssertionError(('unproved leaf hypothesis', key, self.t.nodes[a], self.t.nodes[b]))
        next_control = {name: transfer(after[f.COL['s2_'+name]]) for name in c.CONTROL}
        after_data = transfer(own_after[f.COL['s2_data']])
        if loop:
            assert next_control == self.control, ('loop changes controller', key)
            assert after_data == memory, ('loop changes Data', key)
        elif after_data != memory:
            self.writes.append((self.position, after_data))
        self.control = next_control
        self.steps.append(dict(leaf=key, start=self.position.pair(), count=count.pair(), shift=shift,
                               nonempty_query_domain=domain, head_range=(minimum,maximum)))
        self.position += count.times(shift)
        self.elapsed += count

    def left_return(self):
        # The first leftward move is on last=1; the remaining moves have last=0.
        self.event(LAST_LEFT)
        self.event(('scan','left_flight'), count=Affine(k=self.L-2), loop=True)

    def check(self):
        self.event(('fetch',f'fetch_{c.META}_0'))
        self.event(('scan','meta_unready_0'), count=Affine(k=self.L-self.m-2), loop=True)
        self.event(('scan','meta_unready_1'))
        self.left_return()
        self.event(('scan','left_meta_ready'))
        assert self.position == Affine() and self.elapsed == Affine(k=2*self.L-self.m)
        lo, hi = self.domain
        if hi < self.L-1:
            self.event(('scan',f'right_flight_{c.READ_META}'), count=Affine(q=1), loop=True)
            self.event(('position',f'meta_hit_{self.selector}'))
            self.event(('scan',f'right_flight_{c.WAIT_META}'), count=Affine(q=-1,k=self.L-2), loop=True)
            self.event(('scan',f'right_reflect_{c.WAIT_META}'))
            self.left_return()
            self.event(('scan',f'left_reflect_{c.WAIT_META}'))
        elif lo == hi == self.L-1:
            self.event(('scan',f'right_flight_{c.READ_META}'), count=Affine(k=self.L-1), loop=True)
            self.event(('scan',f'meta_hit_last_{self.selector}'))
            self.left_return()
            self.event(('scan',f'left_reflect_{c.WAIT_META}'))
        else:
            assert lo >= self.L
            self.event(('scan',f'right_flight_{c.READ_META}'), count=Affine(k=self.L-1), loop=True)
            self.event(('scan',f'right_reflect_{c.READ_META}'))
            self.left_return()
            self.event(('scan',f'left_meta_fallback_{self.selector}'))
        assert self.position == Affine() and self.elapsed == Affine(k=4*self.L-self.m)
        self.event(('scan',f'right_flight_{c.WRITE}'), count=Affine(k=self.d), loop=True)
        self.event(('position','write'))
        expected = dict(self.initial, phase=self.t.const(c.FETCH), pc=self.t.const(self.pc+1),
                        ra=self.t.const(self.d), rb=self.t.const(self.selector), rd=self.t.const(self.d),
                        value=self.t.lookup(self.query,self.selector), direction=self.t.const(c.RIGHT))
        assert self.control == expected, 'incomplete final controller'
        assert self.writes == [(Affine(k=self.d), expected['value'])], 'wrong Data effect'
        duration = 4*self.L+self.d-self.m+1
        assert self.position == Affine(k=self.d+1) and self.elapsed == Affine(k=duration)
        starts = [(lo,hi-duration+1) for lo,hi in clock.regular_intervals() if hi-lo+1 >= duration]
        assert len(starts) == len(clock.regular_intervals())
        return dict(pc=self.pc, instruction_address=self.m, destination=self.d, selector=self.selector,
                    query_domain=self.domain, duration=duration, legal_start_age_intervals=starts,
                    complete_controller_and_one_Data_write=True, steps=self.steps)


def verify_rom():
    rom=p.base_rom();g=p.layout();L=len(rom)
    assert L == g.computation_cells and 1 < g.memory_count < L < f.Q-5
    assert np.flatnonzero(rom[:,5]).tolist() == [0]
    assert np.flatnonzero(rom[:,6]).tolist() == [L-1]
    assert np.all(rom[:g.memory_count,0] == c.MEM)
    assert np.array_equal(rom[:g.memory_count,1],np.arange(g.memory_count,dtype=np.uint64))
    for pc,op in enumerate(g.instructions):
        assert tuple(map(int,rom[g.memory_count+pc,:5])) == (op.kind,pc,op.a,op.b,op.d)
    return dict(core_cells=L,memory_cells=g.memory_count,META_instructions=sum(op.kind==c.META for op in g.instructions),rom_sha256=hashlib.sha256(rom.tobytes()).hexdigest())

