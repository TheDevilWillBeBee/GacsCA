"""Conditional full raw self-ROM certificate for the fixed AND evaluator.

The checker executes the ROM's instruction data flow symbolically.  It assumes
each physical instruction and packet has the effect and timing specified by
the local controller; separate physical path tests are still required.
"""
from types import FunctionType

from gacsca.fixed_rule import and_holder_rule as f, and_holder_core as c
from gacsca.fixed_rule import and_holder_program as p
from gacsca.fixed_rule.wordcode_and import ADD, AND
from experiments.fixed_rule.certify_compact16_holder_rom import (
    Terms as PreviousTerms, Checker as PreviousChecker,
)


class Terms(PreviousTerms):
    def op(self, kind, a, b):
        if kind == AND:
            return self.band(a, b)
        return super().op(kind, a, b)

    def lookup(self, address, selector):
        if selector >= len(c.STATIC):
            return self.const(0)
        value = self.value(address)
        if value is None:
            return self.intern(('rom', address, selector))
        return self.const(self.rom[value, selector] if value < len(self.rom)
                          else c.fallback(value, selector))

    def normalize(self, raw):
        result = list(raw)
        for offset in f.STATIC_OFFSETS:
            source = raw[f.COL['address']]
            if offset:
                source = self.op(ADD, source, self.const(offset))
            address = self.band(source, self.const(f.Q - 1))
            for selector, name in enumerate(c.STATIC):
                result[f.COL[f'p{offset+3}_{name}']] = self.lookup(address, selector)
        return result


def bind(function):
    namespace = dict(function.__globals__)
    namespace.update(f=f, c=c, p=p, Terms=Terms)
    result = FunctionType(function.__code__, namespace, function.__name__,
                          function.__defaults__, function.__closure__)
    result.__kwdefaults__ = function.__kwdefaults__
    return result


class Checker(PreviousChecker):
    __init__ = bind(PreviousChecker.__init__)
    reset = bind(PreviousChecker.reset)
    mem = bind(PreviousChecker.mem)
    execute = bind(PreviousChecker.execute)
    deliver = bind(PreviousChecker.deliver)
    vote = bind(PreviousChecker.vote)
    check = bind(PreviousChecker.check)


def equivalence(description=None):
    original = f.self_description()
    compiled = p.compiled_description() if description is None else description
    terms = Terms(p.base_rom())
    inputs = tuple(terms.variable('input_' + str(i), width)
                   for i, (_, width) in enumerate(f.SCHEMA * 15))
    expected = terms.expression(original, inputs)
    actual = terms.expression(compiled, inputs)
    assert len(expected) == len(actual) == f.FIELDS
    for (name, _), got, want in zip(f.SCHEMA, actual, expected):
        assert got == want, ('complete optimized output mismatch', name)
    return dict(passed=True, complete_raw_outputs=f.FIELDS,
                arbitrary_typed_inputs=True,
                descriptor_sha256=original.digest(),
                compiled_sha256=compiled.digest(),
                symbolic_terms=len(terms.nodes))


def check():
    equal = equivalence()
    flow = Checker().check()
    layout = p.layout()
    timing = layout.timing_certificate()
    assert timing['fits']
    path_ticks = sum(layout.schedule(*phase)[0] for phase in layout.stage_ranges)
    path_ticks += layout.schedule(*layout.delivery_range)[0]
    return dict(passed=True, equivalence=equal, dataflow=flow,
                timing=timing, Q=f.Q, U=f.U, fields=f.FIELDS, width=f.WIDTH,
                core_cells=layout.computation_cells,
                instructions=len(layout.instructions),
                controller_path_ticks=path_ticks,
                scope='Conditional full raw symbolic own-ROM data flow; '
                      'not a physical macrostep or noise theorem.')


if __name__ == '__main__':
    import json
    print(json.dumps(check(), indent=2))
