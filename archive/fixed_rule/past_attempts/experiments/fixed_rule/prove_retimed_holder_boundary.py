"""Exact current-rule boundary orbit and permanent Address-defect checks.

Diagnostic only: no BDD calculation is used by an evolving configuration.
The orbit quantifies normalized 31-bit clocks; defect geometry admits all
32-bit raw clocks and proves their first-step normalization explicitly.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import sys
import time

from gacsca.fixed_rule import retimed_holder_rule as f
from gacsca.fixed_rule import retimed_holder_projected as r
from gacsca.fixed_rule import retimed_holder_program as p
from gacsca.fixed_rule import retimed_holder_boundary_data as cap
from gacsca.fixed_rule.word_bdd import BDD
from gacsca.fixed_rule.wordcode import Program, NAND, ADD, SHR, EQ, LT, LIT, MASK
from gacsca.fixed_rule.word_prune import prune


def validate(description):
    if description.inputs != 15 * f.FIELDS or len(description.outputs) != f.FIELDS:
        raise ValueError('complete radius-seven raw input/output contract required')
    for i, (op, a, b) in enumerate(description.operations):
        if op == LIT:
            if type(a) is not int or not 0 <= a <= MASK:
                raise ValueError('bad literal')
        elif op not in (NAND, ADD, SHR, EQ, LT) or any(
                type(v) is not int or not 0 <= v < description.inputs + i
                for v in (a, b)):
            raise ValueError('bad operation or forward wire')
    if any(type(v) is not int or not 0 <= v < description.wires
           for v in description.outputs):
        raise ValueError('bad output wire')


def period_bits():
    bits = f.U.bit_length() - 1
    assert 1 << bits == f.U and bits <= dict(f.SCHEMA)['age']
    return bits


def prove_orbit(description=None):
    description = f.self_description() if description is None else description
    validate(description)
    bits = period_bits()
    bdd = BDD(bits)
    age = tuple(bdd.variable(i) for i in range(bits)) + (0,) * (64 - bits)
    base = r.lift(cap.cell())

    def words(clock):
        values = {name: bdd.const(getattr(base, name)) for name, _ in f.SCHEMA}
        values['age'] = clock
        head, pc = 0, bdd.const(0)
        for when, entry in cap.pulse_entries():
            hit = bdd.arithmetic(EQ, clock, bdd.const(when))[0]
            head = bdd.or_(head, hit)
            pc = tuple(bdd.ite(hit, x, y) for x, y in zip(bdd.const(entry), pc))
        values['s3_head'], values['s3_pc'] = (head,) + (0,) * 63, pc
        return tuple(values[name] for name, _ in f.SCHEMA)

    try:
        actual = bdd.evaluate(description, words(age) * 15)
        next_age = bdd.add(age, bdd.const(1))[:bits] + (0,) * (64 - bits)
        for (name, _), got, want in zip(f.SCHEMA, actual, words(next_age)):
            for bit, (x, y) in enumerate(zip(got, want)):
                if x != y:
                    raise AssertionError((name, bit, 'Age witness',
                                          bdd.witness(bdd.xor(x, y))))
        return dict(passed=True, normalized_ages=f.U,
                    raw_age_width=dict(f.SCHEMA)['age'], symbolic_age_bits=bits,
                    complete_raw_words=f.FIELDS, BDD_nodes=len(bdd.nodes),
                    pulse_entries=cap.pulse_entries(),
                    descriptor_sha256=description.digest())
    finally:
        bdd.binary.cache_clear()


def prove_defect(defect_offset, description=None):
    if defect_offset is not None and defect_offset not in range(-5, 6):
        raise ValueError('one local defect or unaffected neighborhood required')
    description = f.self_description() if description is None else description
    validate(description)
    names = ('address', 'age', 'f1', 'f2')
    program = prune(Program(description.inputs, description.operations,
                            tuple(description.outputs[f.COL[n]] for n in names)))
    used = {v for op, a, b in program.operations if op != LIT
            for v in (a, b) if v < program.inputs}
    used.update(v for v in program.outputs if v < program.inputs)
    support = sorted((v // f.FIELDS - 7, f.SCHEMA[v % f.FIELDS][0]) for v in used)
    allowed = {'address', 'age', 'f1', 'f2', 'w2_wf1', 'w2_wf2'}
    if any(not -5 <= offset <= 5 or name not in allowed for offset, name in support):
        raise AssertionError('unexpected geometry dependency')
    age_bits, address_bits = (dict(f.SCHEMA)[n] for n in ('age', 'address'))
    bdd = BDD(age_bits + address_bits + 22)
    age = tuple(bdd.variable(i) for i in range(age_bits)) + (0,) * (64 - age_bits)
    replacement = tuple(bdd.variable(age_bits + i) for i in range(address_bits))
    replacement += (0,) * (64 - address_bits)
    words = []
    for offset in f.NEIGHBORHOOD:
        values = {name: bdd.const(0) for name, _ in f.SCHEMA}
        values.update(address=replacement if offset == defect_offset else bdd.const(f.Q - 1),
                      age=age, f1=bdd.const(1), f2=bdd.const(1))
        if -5 <= offset <= 5:
            for kind in (1, 2):
                bit = bdd.variable(age_bits + address_bits + 2 * (offset + 5) + kind - 1)
                values[f'w2_wf{kind}'] = (bit,) + (0,) * 63
        words.extend(values[name] for name, _ in f.SCHEMA)
    try:
        actual = bdd.evaluate(program, tuple(words))
        bits = period_bits()
        expected = (replacement if defect_offset == 0 else bdd.const(f.Q - 1),
                    bdd.add(age, bdd.const(1))[:bits] + (0,) * (64 - bits),
                    bdd.const(1), bdd.const(1))
        for name, got, want in zip(names, actual, expected):
            for bit, (x, y) in enumerate(zip(got, want)):
                if x != y:
                    raise AssertionError((defect_offset, name, bit,
                                          bdd.witness(bdd.xor(x, y))))
        return dict(passed=True, defect_offset=defect_offset, support=support,
                    independent_bits=bdd.variables, BDD_nodes=len(bdd.nodes),
                    raw_clocks=1 << age_bits, replacement_addresses=f.Q)
    finally:
        bdd.binary.cache_clear()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    start = time.perf_counter()
    result = dict(passed=True, orbit=prove_orbit(),
                  defect_cases=[prove_defect(offset) for offset in (None, *range(-5, 6))],
                  descriptor_sha256=f.self_description().digest(),
                  ROM_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest(),
                  Q=f.Q, U=f.U, physical_width=r.WIDTH, raw_width=f.WIDTH,
                  scope='Exact descriptor-semantic noiseless terminal orbit and permanent '
                        'single-Address-defect geometry; no robust cap or new nested execution.')
    result['seconds'] = time.perf_counter() - start
    result['host_max_rss_kib'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    sources = {Path(__file__).resolve()}
    for module in tuple(sys.modules.values()):
        name = getattr(module, '__file__', None)
        if name and '/gacsca/fixed_rule/' in str(Path(name).resolve()):
            sources.add(Path(name).resolve())
    result['source_sha256'] = {str(path.relative_to(Path.cwd())):
                              hashlib.sha256(path.read_bytes()).hexdigest()
                              for path in sorted(sources)}
    with args.output.open('x') as stream:
        stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
