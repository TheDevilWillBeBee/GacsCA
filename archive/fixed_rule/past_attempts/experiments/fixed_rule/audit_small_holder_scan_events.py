"""Independent concrete audit of conditional scanner identities."""
import argparse
import hashlib
import json
import random
import resource
import time
from pathlib import Path

import numpy as np
from gacsca.fixed_rule import small_holder_rule as f, small_holder_native as native
from gacsca.fixed_rule.wordcode import MASK
from experiments.fixed_rule.certify_small_holder_scan_events import cases, prepare
from experiments.fixed_rule.audit_small_holder_position_events import evaluate, sha


def satisfy(terms, assignments):
    """Repair finite audit samples, never proof assumptions or evolving states."""
    for _ in range(8):
        values = evaluate(terms, assignments)
        if terms.hypotheses_hold(values):
            return values
        for a, b in sorted(terms.disequalities):
            if values[a] != values[b]:
                continue
            choices = [(x, y) for x, y in ((a, b), (b, a))
                       if terms.nodes[x][0] == 'variable' and terms.nodes[x][1] != 'base_address']
            choices.sort(key=lambda pair: not terms.nodes[pair[0]][1].startswith('old_'))
            if not choices:
                raise AssertionError('cannot construct audit sample')
            x, y = choices[0]
            _, name, width = terms.nodes[x]
            assignments[name] = (values[y] + 1) & ((1 << width) - 1)
    raise AssertionError('audit sample did not satisfy explicit hypotheses')


def audit_events():
    rng = random.Random(2026092671)
    count = 0
    digest = hashlib.sha256()
    patterns = ((0, 'zero', f.Q - 6), (f.Q - 1, 'ones', f.Q - 5),
                (1, 'random', f.Q - 1), (f.Q - 2, 'random', f.Q),
                (f.Q // 2, 'ones', 0), (17, 'random', MASK))
    for event in cases():
        terms, raw = prepare(event)
        old = [tuple(raw(pos + j) for j in f.NEIGHBORHOOD) for pos in range(-4, 5)]
        expected = [raw(pos, after=True) for pos in range(-4, 5)]
        for address, mode, query in patterns:
            assignments = {node[1]: 0 if mode == 'zero' else (1 << node[2]) - 1
                           if mode == 'ones' else rng.getrandbits(node[2])
                           for node in terms.nodes if node[0] == 'variable'}
            assignments.update(base_address=address, old_rd=query)
            values = satisfy(terms, assignments)
            assert terms.hypotheses_hold(values)
            for pos, rows, wanted in zip(range(-4, 5), old, expected):
                neighborhood = tuple(f.decode_cell(tuple(values[i] for i in row)) for row in rows)
                scalar = f.local_step(neighborhood)
                machine = native.local_step(neighborhood)
                assert scalar == machine, (event['name'], address, mode, pos, 'native')
                wanted_values = tuple(values[i] for i in wanted)
                assert f.encode_cell(scalar) == wanted_values, (event['name'], address, mode, pos)
                digest.update(np.array(wanted_values, dtype=np.uint64).tobytes())
                count += 1
    return dict(complete_physical_outputs_checked=count, raw_words_per_output=f.FIELDS,
                all_concrete_hypotheses_checked=True, address_and_fallback_patterns=patterns,
                output_sha256=digest.hexdigest())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--certificate', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    out = Path(args.output)
    if out.exists():
        raise FileExistsError('preserve evidence')
    start = time.perf_counter()
    checker = Path('experiments/fixed_rule/certify_small_holder_scan_events.py')
    certificate = json.loads(Path(args.certificate).read_text())
    assert certificate['passed'] and certificate['source_sha256'] == sha(checker)
    assert certificate['descriptor_sha256'] == f.self_description().digest()
    assert certificate['case_count'] == len(cases())
    result = audit_events()
    paths = [Path(__file__), checker,
             Path('tests/fixed_rule/test_small_holder_scan_events.py'),
             Path('experiments/fixed_rule/audit_small_holder_position_events.py'),
             Path('experiments/fixed_rule/certify_small_holder_position_events.py'),
             Path('experiments/fixed_rule/certify_small_holder_local_events.py'),
             Path('experiments/fixed_rule/certify_small_holder_rom_dataflow.py')]
    result.update(passed=True, certificate_sha256=sha(args.certificate),
                  source_sha256={str(path): sha(path) for path in paths},
                  seconds=time.perf_counter() - start,
                  host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  limitation='Finite independent scalar/native checks with each explicit hypothesis checked; no scan trajectory, clock-interval or whole-period theorem.')
    out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
