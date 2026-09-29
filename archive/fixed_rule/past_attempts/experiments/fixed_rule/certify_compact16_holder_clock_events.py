"""Full raw event refinement over regular active clock intervals.

Diagnostic only. Imports earlier event formulas without altering their sources,
then replaces the physical Age fields with one interval-bounded symbolic word.
Clock overrides (reset, temporal vote, capture and commit) are deliberately
excluded from this regular-event lemma and must be composed separately.
"""
import argparse
import hashlib
import json
import resource
import time
from pathlib import Path

from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_core as c, compact16_holder_program as p
from gacsca.fixed_rule.wordcode import ADD, SHR, EQ, LT, LIT, MASK
from experiments.fixed_rule.certify_compact16_holder_position_events import cases as position_cases, prepare as position_prepare
from experiments.fixed_rule.certify_compact16_holder_scan_events import Conditional, cases as scan_cases, prepare as scan_prepare
from experiments.fixed_rule.prove_small_holder_boundary import validate


class Intervals(Conditional):
    def __init__(self, rom):
        super().__init__(rom)
        self.ranges = {}
        self.range_cache = {}

    def bounded(self, name, width, lo, hi):
        if not 0 <= lo <= hi < 1 << width:
            raise ValueError('invalid bounded variable')
        x = self.variable(name, width)
        if x in self.range_cache or x in self.ranges:
            raise ValueError('variable bounds must be declared once before use')
        self.ranges[x] = (lo, hi)
        return x

    def bounds(self, x):
        if x in self.range_cache:
            return self.range_cache[x]
        node = self.nodes[x]
        if x in self.ranges:
            result = self.ranges[x]
        elif node[0] == 'const':
            result = (node[1], node[1])
        elif node[0] == 'variable':
            result = (0, (1 << node[2]) - 1)
        elif node[0] == 'not':
            lo, hi = self.bounds(node[1])
            result = (MASK - hi, MASK - lo)
        elif node[0] == 'modadd':
            lo, hi = self.bounds(node[1])
            lo += node[2]
            hi += node[2]
            modulus = 1 << node[3]
            result = (lo % modulus, hi % modulus) if lo // modulus == hi // modulus else (0, modulus - 1)
        elif node[0] == 'op' and node[1] in (EQ, LT):
            result = (0, 1)
        elif node[0] == 'op' and node[1] == ADD:
            al, ah = self.bounds(node[2])
            bl, bh = self.bounds(node[3])
            lo, hi = al + bl, ah + bh
            modulus = 1 << 64
            result = (lo % modulus, hi % modulus) if lo // modulus == hi // modulus else (0, MASK)
        else:
            result = (0, MASK)
        self.range_cache[x] = result
        return result

    def op(self, kind, a, b):
        if kind in (EQ, LT):
            al, ah = self.bounds(a)
            bl, bh = self.bounds(b)
            if kind == EQ:
                if ah < bl or bh < al:
                    return self.const(0)
                if al == ah == bl == bh:
                    return self.const(1)
            else:
                if ah < bl:
                    return self.const(1)
                if al >= bh:
                    return self.const(0)
        return super().op(kind, a, b)


def regular_intervals():
    excluded = set(c.RESET_AGES) | set(c.VOTE_AGES) | {c.CAPTURE_AGE - 1, f.U - 1}
    result = []
    for start, stop in zip(c.RESET_AGES, c.ACTIVE_ENDS):
        at = start
        for special in sorted(x for x in excluded if start <= x < stop):
            if at < special:
                result.append((at, special - 1))
            at = special + 1
        if at < stop:
            result.append((at, stop - 1))
    return tuple(result)


def fetch_cases():
    kinds = (*c.ALU_KINDS, LIT, c.SEND, c.LOAD, c.META, c.HALT, c.IF_THIRD, c.LOOP)
    assert {op.kind for op in p.layout().instructions} <= set(kinds)
    return tuple(dict(name=f'fetch_{kind}_{int(last)}', role='fetch', kind=kind, last=last)
                 for kind in kinds for last in (False, True))


def cases():
    return (tuple(dict(event, family='position') for event in position_cases())
            + tuple(dict(event, family='scan') for event in scan_cases())
            + tuple(dict(event, family='fetch') for event in fetch_cases()))


def prepare_fetch(event, interval):
    terms, quiet = position_prepare(dict(name='quiet', role='quiet'))
    zero, one = terms.const(0), terms.const(1)
    actor = quiet(0)
    index, a, b, d = (actor[f.COL['p3_' + name]] for name in ('index', 'a', 'b', 'd'))
    old = {name: terms.variable('fetch_old_' + name, dict(c.SCHEMA)[name]) for name in c.CONTROL}
    old.update(phase=zero, direction=zero, pc=index)
    new = dict(old)
    kind = event['kind']
    if kind in c.ALU_KINDS:
        new.update(phase=terms.const(c.READ_A), ra=terms.mask(a, 32), rb=b, rd=d, alu=terms.const(kind))
    elif kind == LIT:
        new.update(phase=terms.const(c.WRITE), rd=d, value=a)
    elif kind == c.SEND:
        new.update(phase=terms.const(c.TRANSMIT), ra=terms.mask(a, 32), rb=b, rd=d)
    elif kind == c.LOAD:
        new.update(phase=terms.const(c.READ_LOAD), ra=terms.mask(a, 32))
    elif kind == c.META:
        new.update(phase=terms.const(c.READ_META), ra=terms.mask(a, 32), rb=b, value=zero)
    elif kind == c.HALT:
        new = None
    elif kind == c.IF_THIRD:
        lo, hi = interval
        if c.RESET_AGES[2] <= lo <= hi < c.ACTIVE_ENDS[2]:
            new['pc'] = terms.modular_add(index, 1, 32)
        elif hi < c.RESET_AGES[2] or lo >= c.ACTIVE_ENDS[2]:
            new = None
        else:
            raise ValueError('interval straddles IF_THIRD branch')
    elif kind == c.LOOP:
        new['pc'] = zero
    else:
        raise ValueError(kind)
    new_at = 0 if event['last'] else 1
    if new is not None:
        new['direction'] = one if event['last'] else zero

    def raw(pos, after=False):
        values = list(quiet(pos, after=after))
        for offset in f.STATIC_OFFSETS:
            if pos + offset == 0:
                values[f.COL[f'p{offset + 3}_kind']] = terms.const(kind)
                values[f.COL[f'p{offset + 3}_last']] = terms.const(int(event['last']))
        for offset in f.OFFSETS:
            site = pos + offset
            ctrl = new if after and site == new_at else old if not after and site == 0 else None
            if ctrl is not None:
                prefix = f's{offset + 2}_'
                values[f.COL[prefix + 'head']] = one
                for name, value in ctrl.items():
                    values[f.COL[prefix + name]] = value
        return tuple(values)
    return terms, raw


def prepare(event, interval):
    lo, hi = interval
    if event['family'] == 'position':
        old, old_raw = position_prepare(event)
    elif event['family'] == 'scan':
        old, old_raw = scan_prepare(event)
    elif event['family'] == 'fetch':
        old, old_raw = prepare_fetch(event, interval)
    else:
        raise ValueError(event['family'])
    terms = Intervals(p.base_rom())
    age = terms.bounded('physical_age', 32, lo, hi)
    mapping = {}

    def transfer(x):
        if x in mapping:
            return mapping[x]
        node = old.nodes[x]
        if node[0] == 'const':
            y = terms.const(node[1])
        elif node[0] == 'variable':
            y = terms.variable(node[1], node[2])
        elif node[0] == 'op':
            y = terms.op(node[1], transfer(node[2]), transfer(node[3]))
        elif node[0] == 'not':
            y = terms.inv(transfer(node[1]))
        elif node[0] == 'modadd':
            y = terms.modular_add(transfer(node[1]), node[2], node[3])
        else:
            raise ValueError(('unhandled imported term', node))
        mapping[x] = y
        return y

    for a, b in getattr(old, 'disequalities', ()):
        terms.unequal(transfer(a), transfer(b))

    def raw(pos, after=False):
        values = [transfer(x) for x in old_raw(pos, after=after)]
        values[f.COL['age']] = terms.modular_add(age, int(after), (f.U-1).bit_length())
        return tuple(values)
    return terms, raw


def certify_case(event, interval, description=None):
    desc = f.self_description() if description is None else description
    validate(desc)
    terms, raw = prepare(event, interval)
    for pos in range(-4, 5):
        actual = terms.expression(desc, tuple(w for j in f.NEIGHBORHOOD for w in raw(pos + j)))
        expected = raw(pos, after=True)
        for (name, _), a, b in zip(f.SCHEMA, actual, expected):
            if a != b:
                raise AssertionError((event['family'], event['name'], interval, pos, name, terms.nodes[a], terms.nodes[b]))
    return dict(family=event['family'], name=event['name'], interval=interval,
                passed=True, full_raw_outputs=9 * f.FIELDS, symbolic_terms=len(terms.nodes),
                disequalities=[(terms.nodes[a], terms.nodes[b]) for a, b in sorted(terms.disequalities)])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    out = Path(args.output)
    if out.exists():
        raise FileExistsError('preserve evidence')
    start = time.perf_counter()
    rows = []
    for interval in regular_intervals():
        for event in cases():
            rows.append(certify_case(event, interval))
        print(json.dumps(dict(interval=interval, completed_cases=len(rows), seconds=time.perf_counter()-start)), flush=True)
    result = dict(passed=True, cases=rows, case_count=len(rows), event_families=len(cases()),
                  intervals=regular_intervals(), regular_active_ages=sum(hi-lo+1 for lo,hi in regular_intervals()),
                  complete_raw_output_words=sum(row['full_raw_outputs'] for row in rows),
                  descriptor_sha256=f.self_description().digest(),
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  seconds=time.perf_counter()-start,
                  host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  limitation='Canonical coherent, zero flags/Signal/Wf, one head or quiet, no incoming mail. Regular active clocks only; reset/vote/capture/commit excluded. No whole-period or nested trajectory theorem.')
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'}, indent=2), flush=True)


if __name__ == '__main__':
    main()
