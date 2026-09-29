"""Independent concrete semantics checks for the positional event certificate.

Diagnostics only: this does not evolve a hierarchy or replace physical steps.
"""
import argparse
import hashlib
import json
import random
import resource
import time
from pathlib import Path

import numpy as np
from gacsca.fixed_rule import small_holder_rule as f, small_holder_native as native
from gacsca.fixed_rule.wordcode import MASK, arithmetic
from experiments.fixed_rule.certify_small_holder_position_events import cases, prepare


def evaluate(terms, assignments):
    """Interpret the term syntax without using its simplifying operations."""
    values = []
    for node in terms.nodes:
        if node[0] == 'const':
            value = node[1]
        elif node[0] == 'variable':
            value = assignments[node[1]]
            if not 0 <= value < 1 << node[2]:
                raise ValueError(('variable outside declared width', node))
        elif node[0] == 'not':
            value = values[node[1]] ^ MASK
        elif node[0] == 'op':
            value = arithmetic(node[1], values[node[2]], values[node[3]])
        elif node[0] == 'modadd':
            value = (values[node[1]] + node[2]) & ((1 << node[3]) - 1)
        else:
            raise AssertionError(('unexpected symbolic primitive', node))
        values.append(value)
    return values


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def audit_events():
    rng = random.Random(2026092661)
    outputs = 0
    digest = hashlib.sha256()
    # Include both sides of the address wrap and u32/u64 overflow in controllers.
    patterns = ((0, 'zero'), (f.Q - 1, 'ones'), (1, 'random'),
                (f.Q - 2, 'random'), (f.Q // 2, 'ones'), (17, 'random'))
    for event in cases():
        terms, raw = prepare(event)
        old = [tuple(raw(pos + j) for j in f.NEIGHBORHOOD) for pos in range(-4, 5)]
        expected = [raw(pos, after=True) for pos in range(-4, 5)]
        for address, mode in patterns:
            assignments = {
                node[1]: 0 if mode == 'zero' else (1 << node[2]) - 1
                if mode == 'ones' else rng.getrandbits(node[2])
                for node in terms.nodes if node[0] == 'variable'
            }
            assignments['base_address'] = address
            values = evaluate(terms, assignments)
            for pos, rows, wanted in zip(range(-4, 5), old, expected):
                neighborhood = tuple(f.decode_cell(tuple(values[i] for i in row)) for row in rows)
                expected_values = tuple(values[i] for i in wanted)
                scalar = f.local_step(neighborhood)
                machine = native.local_step(neighborhood)
                assert scalar == machine, (event['name'], address, mode, pos, 'native')
                assert f.encode_cell(scalar) == expected_values, (event['name'], address, mode, pos)
                digest.update(np.array(expected_values, dtype=np.uint64).tobytes())
                outputs += 1
    return dict(complete_physical_outputs_checked=outputs, raw_words_per_output=f.FIELDS,
                address_patterns=patterns, output_sha256=digest.hexdigest())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--certificate', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    out = Path(args.output)
    if out.exists():
        raise FileExistsError('preserve evidence')
    start = time.perf_counter()
    certificate = json.loads(Path(args.certificate).read_text())
    checker = Path('experiments/fixed_rule/certify_small_holder_position_events.py')
    assert certificate['passed'] and certificate['source_sha256'] == sha(checker)
    assert certificate['descriptor_sha256'] == f.self_description().digest()
    assert certificate['case_count'] == len(cases())
    result = audit_events()
    paths = [Path(__file__), checker,
             Path('tests/fixed_rule/test_small_holder_position_events.py'),
             Path('experiments/fixed_rule/certify_small_holder_local_events.py'),
             Path('experiments/fixed_rule/certify_small_holder_rom_dataflow.py')]
    result.update(passed=True, certificate_sha256=sha(args.certificate),
                  source_sha256={str(path): sha(path) for path in paths},
                  seconds=time.perf_counter() - start,
                  host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  limitation='Independent finite scalar/native checks of symbolic syntax, including wrap and overflow; not an all-input or whole-period proof.')
    out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
