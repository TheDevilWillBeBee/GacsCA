"""Complete raw local AND READ_B event for all canonical colony addresses.

This is a one-step event identity under the stated coherent controller/geometry
premise of the earlier position-event constructor, not a full instruction path.
"""
import json
from types import FunctionType

from gacsca.fixed_rule import and_holder_rule as f, and_holder_core as c
from gacsca.fixed_rule import and_holder_program as p
from gacsca.fixed_rule.wordcode_and import AND, AND_ALU
from experiments.fixed_rule import certify_compact16_holder_position_events as prior
from experiments.fixed_rule import certify_compact16_holder_clock_events as prior_clock


class Modular(prior.Modular):
    def op(self, kind, a, b):
        if kind in (AND, AND_ALU):
            return self.band(a, b)
        return super().op(kind, a, b)


def bind(function):
    namespace = dict(function.__globals__)
    namespace.update(f=f, c=c, p=p, Modular=Modular)
    result = FunctionType(function.__code__, namespace, function.__name__,
                          function.__defaults__, function.__closure__)
    result.__kwdefaults__ = function.__kwdefaults__
    return result


prepare = bind(prior.prepare)
prepare_fetch = bind(prior_clock.prepare_fetch)


def check():
    assert AND == 14 and AND_ALU == 6
    event = dict(name='read_b_AND', role='read_b', opcode=AND_ALU)
    terms, raw = prepare(event)
    description = f.self_description()
    for position in range(-4, 5):
        actual = terms.expression(
            description,
            tuple(word for delta in f.NEIGHBORHOOD
                  for word in raw(position + delta)))
        expected = raw(position, after=True)
        for (name, _), got, want in zip(f.SCHEMA, actual, expected):
            assert got == want, (position, name, terms.nodes[got], terms.nodes[want])
    return dict(passed=True, event='AND READ_B',
                canonical_base_addresses=f.Q, full_raw_output_words=9*f.FIELDS,
                descriptor_sha256=description.digest(),
                symbolic_terms=len(terms.nodes),
                premise='Coherent fivefold procedure copies, canonical geometry, '
                        'regular active clock, no incoming mail, one head at MEM '
                        'whose index matches rb and alu=6; surrounding static '
                        'metadata and Data are arbitrary.',
                limitation='One physical local step; not FETCH-to-WRITE flight '
                           'or full ROM period.')


def check_fetch():
    description = f.self_description()
    cases = []
    for last in (False, True):
        terms, prior_raw = prepare_fetch(
            dict(name=f'fetch_AND_{int(last)}', role='fetch', kind=AND,
                 last=last), (c.VOTE_AGES[0]+10, c.VOTE_AGES[0]+10))
        destination = 0 if last else 1

        def raw(position, after=False):
            values = list(prior_raw(position, after=after))
            if after:
                for offset in f.OFFSETS:
                    if position + offset == destination:
                        values[f.COL[f's{offset+2}_alu']] = terms.const(AND_ALU)
            return tuple(values)

        for position in range(-4, 5):
            actual = terms.expression(
                description,
                tuple(word for delta in f.NEIGHBORHOOD
                      for word in raw(position + delta)))
            expected = raw(position, after=True)
            for (name, _), got, want in zip(f.SCHEMA, actual, expected):
                assert got == want, (last, position, name,
                                     terms.nodes[got], terms.nodes[want])
        cases.append(dict(last=last, full_raw_output_words=9*f.FIELDS,
                          symbolic_terms=len(terms.nodes)))
    return dict(passed=True, event='AND FETCH', cases=cases,
                canonical_base_addresses=f.Q,
                full_raw_output_words=sum(row['full_raw_output_words'] for row in cases),
                descriptor_sha256=description.digest(),
                premise='Canonical geometry, regular active clock, one right-moving '
                        'head at an AND instruction whose index matches pc; '
                        'surrounding static metadata and Data arbitrary.',
                limitation='Two one-step fetch cases, not full flight or period.')


if __name__ == '__main__':
    print(json.dumps(dict(read_b=check(), fetch=check_fetch()), indent=2))
