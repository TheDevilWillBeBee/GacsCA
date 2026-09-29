"""Conditional full-raw scanner identities with explicit disequality hypotheses.

Proof diagnostic only. It does not simulate upper transitions or evolve cells.
The clock is one stated active instant; flags, Signal, Wf and incoming mail are
zero. Every assumption is a word disequality recorded for independent checking.
"""
import argparse
import hashlib
import json
import resource
import time
from pathlib import Path

from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_core as c, compact16_holder_program as p
from gacsca.fixed_rule.wordcode import EQ, LT, ADD
from experiments.fixed_rule.certify_compact16_holder_position_events import Modular
from experiments.fixed_rule.prove_small_holder_boundary import validate


class Conditional(Modular):
    def __init__(self, rom):
        super().__init__(rom)
        self.disequalities = set()

    def unequal(self, a, b):
        pair = tuple(sorted((a, b)))
        known = super().op(EQ, a, b)
        if self.value(known) == 1:
            raise ValueError('contradictory disequality')
        self.disequalities.add(pair)

    def op(self, kind, a, b):
        if kind == EQ and tuple(sorted((a, b))) in self.disequalities:
            return self.const(0)
        return super().op(kind, a, b)

    def hypotheses_hold(self, values):
        return all(values[a] != values[b] for a, b in self.disequalities)


def cases():
    result = [dict(name=f'{role}_{phase}', role=role, phase=phase)
              for role in ('right_flight', 'right_reflect') for phase in range(8)]
    result += [dict(name='left_flight', role='left_flight')]
    result += [dict(name=f'left_reflect_{phase}', role='left_reflect', phase=phase)
               for phase in range(8) if phase != c.READ_META]
    result += [dict(name='left_meta_ready', role='left_meta_ready')]
    result += [dict(name=f'left_meta_fallback_{selector}', role='left_meta_fallback', selector=selector)
               for selector in range(8)]
    result += [dict(name=f'meta_hit_last_{selector}', role='meta_hit_last', selector=selector)
               for selector in range(8)]
    result += [dict(name=f'meta_unready_{int(last)}', role='meta_unready', last=last)
               for last in (False, True)]
    return tuple(result)


def prepare(event, *, use_hypotheses=True):
    t = Conditional(p.base_rom())
    zero, one = t.const(0), t.const(1)
    address = t.variable('base_address', (f.Q-1).bit_length())
    age = c.VOTE_AGES[0] + 10
    widths = dict(c.SCHEMA)
    metadata = {pos: {name: t.variable(f'meta_{pos}_{name}', widths[name]) for name in c.STATIC}
                for pos in range(-16, 17)}
    data = {pos: t.variable(f'data_{pos}', 64) for pos in range(-16, 17)}
    old = {name: t.variable('old_' + name, widths[name]) for name in c.CONTROL}
    old['direction'] = zero
    metadata[0]['last'] = zero
    index = metadata[0]['index']
    role = event['role']
    new_at = 1

    def neq(a, b):
        if use_hypotheses:
            t.unequal(a, b)

    if role in ('right_flight', 'right_reflect'):
        phase = event['phase']
        old['phase'] = t.const(phase)
        if phase == c.FETCH:
            neq(old['pc'], index)
        elif phase in (c.READ_A, c.TRANSMIT, c.READ_LOAD):
            neq(old['ra'], index)
        elif phase == c.READ_B:
            neq(old['rb'], index)
        elif phase == c.WRITE:
            neq(old['rd'], index)
        elif phase == c.READ_META:
            neq(old['rd'], address)
        new = dict(old)
        if role == 'right_reflect':
            metadata[0]['last'] = one
            new['direction'] = one
            new_at = 0
    elif role == 'left_flight':
        old['direction'] = one
        metadata[0]['first'] = zero
        new = dict(old)
        new_at = -1
    elif role in ('left_reflect', 'left_meta_ready', 'left_meta_fallback'):
        old['direction'] = one
        metadata[0]['first'] = one
        new_at = 0
        if role == 'left_reflect':
            old['phase'] = t.const(event['phase'])
            new = dict(old, direction=zero)
            if event['phase'] == c.WAIT_META:
                new['phase'] = t.const(c.WRITE)
        elif role == 'left_meta_ready':
            old.update(phase=t.const(c.READ_META), value=zero)
            new = dict(old, direction=zero, value=one)
        else:
            selector = event['selector']
            old.update(phase=t.const(c.READ_META), rb=t.const(selector))
            neq(old['value'], zero)
            # c.fallback expressed independently, including selector >= 7 -> 0.
            tail = t.op(EQ, t.op(LT, old['rd'], t.const(f.Q - 5)), zero)
            tail_mask = t.op(ADD, t.inv(tail), one)
            if selector == 0:
                fallback = t.band(t.inv(tail_mask), t.const(c.LOOP))
            elif selector == 1:
                fallback = old['rd']
            elif selector == 2:
                fallback = t.band(tail_mask, t.const(31))
            else:
                fallback = zero
            new = dict(old, direction=zero, phase=t.const(c.WRITE), value=fallback, rd=old['ra'])
    elif role == 'meta_hit_last':
        selector = event['selector']
        old.update(phase=t.const(c.READ_META), rd=address, rb=t.const(selector))
        neq(old['value'], zero)
        metadata[0]['last'] = one
        new = dict(old, phase=t.const(c.WAIT_META), rd=old['ra'], direction=one,
                   value=metadata[0][c.STATIC[selector]] if selector < 7 else zero)
        new_at = 0
    elif role == 'meta_unready':
        old.update(phase=t.const(c.READ_META), value=zero)
        new = dict(old)
        if event['last']:
            metadata[0]['last'] = one
            new['direction'] = one
            new_at = 0
    else:
        raise ValueError(role)

    def raw(pos, after=False):
        values = {name: zero for name, _ in f.SCHEMA}
        for delta in f.STATIC_OFFSETS:
            for name, value in metadata[pos + delta].items():
                values[f'p{delta + 3}_{name}'] = value
        values.update(address=t.modular_add(address, pos, (f.Q-1).bit_length()), age=t.const(age + int(after)))
        for delta in f.OFFSETS:
            site = pos + delta
            prefix = f's{delta + 2}_'
            values[prefix + 'data'] = data[site]
            controller = new if after and site == new_at else old if not after and site == 0 else None
            if controller is not None:
                values[prefix + 'head'] = one
                for name, value in controller.items():
                    values[prefix + name] = value
        return tuple(values[name] for name, _ in f.SCHEMA)

    return t, raw


def certify_case(event, description=None, *, use_hypotheses=True):
    desc = f.self_description() if description is None else description
    validate(desc)
    terms, raw = prepare(event, use_hypotheses=use_hypotheses)
    for pos in range(-4, 5):
        actual = terms.expression(desc, tuple(w for j in f.NEIGHBORHOOD for w in raw(pos + j)))
        expected = raw(pos, after=True)
        for (name, _), a, b in zip(f.SCHEMA, actual, expected):
            if a != b:
                raise AssertionError((event['name'], pos, name, terms.nodes[a], terms.nodes[b]))
    return dict(name=event['name'], passed=True, full_raw_outputs=9 * f.FIELDS,
                disequalities=[(terms.nodes[a], terms.nodes[b]) for a, b in sorted(terms.disequalities)],
                symbolic_terms=len(terms.nodes))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    out = Path(args.output)
    if out.exists():
        raise FileExistsError('preserve evidence')
    start = time.perf_counter()
    rows = [certify_case(event) for event in cases()]
    result = dict(passed=True, cases=rows, case_count=len(rows),
                  complete_raw_output_words=sum(row['full_raw_outputs'] for row in rows),
                  all_base_addresses=f.Q, event_age=c.VOTE_AGES[0] + 10,
                  descriptor_sha256=f.self_description().digest(),
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  seconds=time.perf_counter() - start,
                  host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  scope='All width-bounded assignments satisfying the recorded word disequalities, canonical geometry, coherent arbitrary metadata/Data and specified controllers; full raw F.',
                  limitation='One active Age, zero flags/Signal/Wf, no incoming mail, one head. Conditional local identities, not composed scan/period or noisy hierarchical execution.')
    out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
