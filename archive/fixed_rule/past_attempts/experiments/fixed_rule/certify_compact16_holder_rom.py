"""Complete typed self-reference check for the smaller fixed Q/U candidate.

All diagnostic methods are explicitly bound to the new rule and ROM. No prior
path/clock theorem is silently transferred across the Q/U change.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import sys
import time
from types import FunctionType
from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_core as c
from gacsca.fixed_rule import compact16_holder_program as p
from gacsca.fixed_rule.wordcode import ADD, LIT
from experiments.fixed_rule.small_holder_identity_validation import StructuralTerms
from experiments.fixed_rule.certify_sparse_holder_rom import Checker as PreviousChecker


class Terms(StructuralTerms):
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
            address = self.band(source, self.const(f.Q-1))
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
    inputs = tuple(terms.variable('input_'+str(i), width)
                   for i, (_, width) in enumerate(f.SCHEMA*15))
    expected = terms.expression(original, inputs)
    actual = terms.expression(compiled, inputs)
    assert len(expected) == len(actual) == f.FIELDS
    for (name, _), got, want in zip(f.SCHEMA, actual, expected):
        assert got == want, ('complete optimized output mismatch', name)
    return dict(passed=True, complete_raw_outputs=f.FIELDS, arbitrary_typed_inputs=True,
                descriptor_sha256=original.digest(), compiled_sha256=compiled.digest())


def check():
    equality = equivalence()
    flow = Checker().check()
    g = p.layout()
    timing = g.timing_certificate()
    assert timing['fits']
    ticks = sum(g.schedule(*phase)[0] for phase in g.stage_ranges) + g.schedule(*g.delivery_range)[0]
    return dict(passed=True, equivalence=equality, dataflow=flow, timing=timing,
                Q=f.Q, U=f.U, raw_fields=f.FIELDS, raw_width=f.WIDTH,
                core_cells=g.computation_cells, memory_cells=g.memory_count,
                instructions=len(g.instructions), controller_path_ticks=ticks,
                raw_Address_bits=dict(f.SCHEMA)['address'], raw_Age_bits=dict(f.SCHEMA)['age'],
                core_to_tail_gap=f.Q-5-g.computation_cells,
                physical_descriptor_sha256=f.self_description().digest(),
                ROM_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest(),
                rule_parameters_are_actual=True, new_physical_period_executed=False,
                scope='Complete symbolic own-ROM computation and compiled-description equivalence; '
                      'physical path, packet, macrostep and noise refinements for the changed rule remain separate.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    start = time.perf_counter()
    result = check()
    result.update(seconds=time.perf_counter()-start,
                  host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    sources = {Path(__file__).resolve()}
    for module in tuple(sys.modules.values()):
        filename = getattr(module, '__file__', None)
        if filename and '/fixed_rule/' in str(Path(filename).resolve()):
            sources.add(Path(filename).resolve())
    result['source_sha256'] = {str(path.relative_to(Path.cwd())):
                              hashlib.sha256(path.read_bytes()).hexdigest()
                              for path in sorted(sources)}
    with args.output.open('x') as stream:
        stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'source_sha256'}, indent=2))


if __name__ == '__main__':
    main()
