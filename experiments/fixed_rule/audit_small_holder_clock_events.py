"""Concrete full-rule audit of interval and symbolic-FETCH event identities."""
import argparse
import gc
import hashlib
import json
import random
import resource
import time
from pathlib import Path

import numpy as np
from gacsca.fixed_rule import small_holder_rule as f, small_holder_native as native
from experiments.fixed_rule.certify_small_holder_clock_events import cases, prepare, regular_intervals
from experiments.fixed_rule.audit_small_holder_position_events import sha
from experiments.fixed_rule.audit_small_holder_scan_events import satisfy


def audit():
    rng = random.Random(2026092681)
    count = 0
    digest = hashlib.sha256()
    for interval in regular_intervals():
        lo, hi = interval
        for event in cases():
            terms, raw = prepare(event, interval)
            old = [tuple(raw(pos + j) for j in f.NEIGHBORHOOD) for pos in range(-4, 5)]
            expected = [raw(pos, after=True) for pos in range(-4, 5)]
            patterns = ((lo, 0, 'zero'), (hi, f.Q - 1, 'ones'),
                        (rng.randint(lo, hi), rng.randrange(f.Q), 'random'))
            for age, address, mode in patterns:
                assignments = {node[1]: 0 if mode == 'zero' else (1 << node[2]) - 1
                               if mode == 'ones' else rng.getrandbits(node[2])
                               for node in terms.nodes if node[0] == 'variable'}
                assignments.update(physical_age=age, base_address=address)
                values = satisfy(terms, assignments)
                assert terms.hypotheses_hold(values)
                assert all(a <= values[x] <= b for x, (a, b) in terms.ranges.items())
                for pos, rows, wanted in zip(range(-4, 5), old, expected):
                    neighborhood = tuple(f.decode_cell(tuple(values[i] for i in row)) for row in rows)
                    scalar = f.local_step(neighborhood)
                    machine = native.local_step(neighborhood)
                    assert scalar == machine, (event['family'], event['name'], age, address, pos, 'native')
                    want = tuple(values[i] for i in wanted)
                    assert f.encode_cell(scalar) == want, (event['family'], event['name'], age, address, pos)
                    digest.update(np.array(want, dtype=np.uint64).tobytes())
                    count += 1
        gc.collect()
        print(json.dumps(dict(interval=interval, complete_outputs=count)), flush=True)
    return dict(complete_physical_outputs_checked=count, raw_words_per_output=f.FIELDS,
                all_disequalities_and_interval_bounds_checked=True,
                concrete_clock_patterns=['interval first Age', 'interval last Age', 'seeded random interior Age'],
                word_patterns=['zero', 'width-limited ones', 'seeded random'], output_sha256=digest.hexdigest())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--certificate', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    out = Path(args.output)
    if out.exists():
        raise FileExistsError('preserve evidence')
    start = time.perf_counter()
    checker = Path('experiments/fixed_rule/certify_small_holder_clock_events.py')
    certificate = json.loads(Path(args.certificate).read_text())
    assert certificate['passed'] and certificate['source_sha256'] == sha(checker)
    assert certificate['descriptor_sha256'] == f.self_description().digest()
    assert certificate['event_families'] == len(cases())
    assert certificate['intervals'] == [list(interval) for interval in regular_intervals()]
    assert certificate['case_count'] == len(cases()) * len(regular_intervals())
    result = audit()
    paths = [Path(__file__), checker, Path(f.__file__), Path(native.__file__),
             Path('tests/fixed_rule/test_small_holder_clock_events.py'),
             Path('experiments/fixed_rule/certify_small_holder_position_events.py'),
             Path('experiments/fixed_rule/certify_small_holder_scan_events.py'),
             Path('experiments/fixed_rule/certify_small_holder_local_events.py'),
             Path('experiments/fixed_rule/certify_small_holder_rom_dataflow.py'),
             Path('experiments/fixed_rule/audit_small_holder_position_events.py'),
             Path('experiments/fixed_rule/audit_small_holder_scan_events.py')]
    result.update(passed=True, certificate_sha256=sha(args.certificate),
                  source_sha256={str(path): sha(path) for path in paths},
                  seconds=time.perf_counter()-start,
                  host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  limitation='Finite independent scalar/native audit of each interval/event family at two clock endpoints and one random Age; no full-period or nested trajectory execution.')
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
