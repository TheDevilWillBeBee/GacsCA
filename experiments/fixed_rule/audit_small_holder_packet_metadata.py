"""Independent finite native audit for non-MEM packet transport identities."""
import argparse
import hashlib
import json
from pathlib import Path
import random
import resource
import time

import numpy as np
from gacsca.fixed_rule import small_holder_rule as f, small_holder_native as native
from experiments.fixed_rule import certify_small_holder_packet_metadata as proof
from experiments.fixed_rule.audit_small_holder_packet_events import instantiate
from experiments.fixed_rule.audit_small_holder_position_events import sha


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
    assert cert['passed'] and not cert['pilot']
    assert cert['descriptor_sha256'] == f.self_description().digest()
    for path, expected in cert['source_sha256'].items():
        assert sha(path) == expected, path
    events = proof.cases()
    intervals = proof.clock.regular_intervals()
    assert len(cert['cases']) == cert['case_count'] == len(events)*len(intervals)
    assert {(row['name'], tuple(row['interval'])) for row in cert['cases']} == {(event['name'], interval) for event in events for interval in intervals}
    assert all(row['passed'] and row['full_raw_outputs'] == 9*f.FIELDS for row in cert['cases'])
    rng = random.Random(2026092605)
    count = 0
    digest = hashlib.sha256()
    for interval in intervals:
        for event in events:
            terms, raw = proof.prepare(event, interval)
            old = [tuple(raw(pos+j) for j in f.NEIGHBORHOOD) for pos in range(-4, 5)]
            wanted = [raw(pos, after=True) for pos in range(-4, 5)]
            for mode in ('zero', 'ones', 'random'):
                values = instantiate(terms, mode, rng)
                for pos, rows, expected in zip(range(-4, 5), old, wanted):
                    neighbors = tuple(f.decode_cell(tuple(values[x] for x in row)) for row in rows)
                    result = f.local_step(neighbors)
                    assert result == native.local_step(neighbors), (event['name'], interval, mode, pos, 'native')
                    actual = f.encode_cell(result)
                    assert actual == tuple(values[x] for x in expected), (event['name'], interval, mode, pos)
                    digest.update(np.array(actual, dtype=np.uint64).tobytes())
                    count += 1
    paths = [Path(__file__), Path(proof.__file__), Path('experiments/fixed_rule/audit_small_holder_packet_events.py'),
             Path('tests/fixed_rule/test_small_holder_packet_metadata.py')]
    result = dict(passed=True, certificate_cases=cert['case_count'], complete_scalar_native_outputs=count,
                  raw_words_per_output=f.FIELDS, output_sha256=digest.hexdigest(),
                  certificate_sha256=sha(args.certificate),
                  source_sha256={str(path): sha(path) for path in paths},
                  seconds=time.perf_counter()-started, host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  limitation='Finite local native/scalar audit, not a composed packet-path, whole-period or noisy hierarchy execution.')
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
