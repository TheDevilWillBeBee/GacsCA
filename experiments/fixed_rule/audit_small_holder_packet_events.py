"""Concrete scalar/native checks of independently specified packet events."""
import argparse
import hashlib
import json
from pathlib import Path
import random
import resource
import time

import numpy as np
from gacsca.fixed_rule import small_holder_rule as f, small_holder_native as native
from experiments.fixed_rule import certify_small_holder_packet_events as proof
from experiments.fixed_rule.audit_small_holder_position_events import evaluate, sha


def instantiate(terms, mode, rng):
    assignments = {node[1]: 0 if mode == 'zero' else (1 << node[2])-1
                   if mode == 'ones' else rng.getrandbits(node[2])
                   for node in terms.nodes if node[0] == 'variable'}
    for x, (lo, hi) in terms.ranges.items():
        assignments[terms.nodes[x][1]] = lo if mode == 'zero' else hi if mode == 'ones' else rng.randint(lo, hi)
    for a, b in terms.disequalities:
        nodes = (terms.nodes[a], terms.nodes[b])
        assert all(node[0] == 'variable' and node[2] == 32 for node in nodes)
        target = next(node for node in nodes if node[1].endswith('_incoming_target'))
        other = next(node for node in nodes if node != target)
        assignments[target[1]] = assignments[other[1]] ^ 1
    values = evaluate(terms, assignments)
    assert terms.hypotheses_hold(values)
    assert all(lo <= values[x] <= hi for x, (lo, hi) in terms.ranges.items())
    return values


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--certificate', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    out = Path(args.output)
    if out.exists():
        raise FileExistsError('preserve evidence')
    started = time.perf_counter()
    cert = json.loads(Path(args.certificate).read_text())
    assert cert['passed'] and cert['descriptor_sha256'] == f.self_description().digest()
    for path, expected in cert['source_sha256'].items():
        assert sha(path) == expected, path
    intervals = proof.clock.regular_intervals()[:1] if cert['pilot'] else proof.clock.regular_intervals()
    events = proof.cases()
    expected = {(event['name'], interval) for interval in intervals for event in events}
    assert len(cert['cases']) == cert['case_count'] == len(expected)
    assert {(row['name'], tuple(row['interval'])) for row in cert['cases']} == expected
    assert all(row['passed'] and row['full_raw_outputs'] == 9*f.FIELDS for row in cert['cases'])
    count = 0
    digest = hashlib.sha256()
    rng = random.Random(2026092604)
    for interval in intervals:
        for event in events:
            terms, raw = proof.prepare(event, interval)
            old = [tuple(raw(pos+j) for j in f.NEIGHBORHOOD) for pos in range(-4, 5)]
            wanted = [raw(pos, after=True) for pos in range(-4, 5)]
            for mode in ('zero', 'ones', 'random'):
                values = instantiate(terms, mode, rng)
                for pos, rows, expected_row in zip(range(-4, 5), old, wanted):
                    neighbors = tuple(f.decode_cell(tuple(values[x] for x in row)) for row in rows)
                    result = f.local_step(neighbors)
                    assert result == native.local_step(neighbors), (event['name'], interval, mode, pos, 'native')
                    actual = f.encode_cell(result)
                    assert actual == tuple(values[x] for x in expected_row), (event['name'], interval, mode, pos)
                    digest.update(np.array(actual, dtype=np.uint64).tobytes())
                    count += 1
        print(json.dumps(dict(interval=interval, complete_outputs=count, seconds=time.perf_counter()-started)), flush=True)
    paths = [Path(__file__), Path(proof.__file__), Path('tests/fixed_rule/test_small_holder_packet_events.py'),
             Path('experiments/fixed_rule/audit_small_holder_position_events.py')]
    result = dict(passed=True, certificate_cases=cert['case_count'],
                  complete_scalar_native_outputs=count, raw_words_per_output=f.FIELDS,
                  output_sha256=digest.hexdigest(), certificate_sha256=sha(args.certificate),
                  source_sha256={str(path): sha(path) for path in paths},
                  seconds=time.perf_counter()-started,
                  host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  limitation='Finite concrete semantics check at lower/upper/random bounded values; not packet-path composition or a whole-period/noisy hierarchical theorem.')
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
