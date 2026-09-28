"""Native/scalar audit of general mail factorization, including dense deliveries."""
import argparse
import hashlib
import json
from pathlib import Path
import random
import resource
import time

import numpy as np
from gacsca.fixed_rule import small_holder_rule as f, small_holder_core as c, small_holder_native as native
from experiments.fixed_rule import certify_small_holder_mail_factorization as proof
from experiments.fixed_rule.audit_small_holder_position_events import evaluate, sha


def assignments(terms, phase, interval, address, mode, rng, tag=0):
    result = {node[1]: rng.getrandbits(node[2]) for node in terms.nodes if node[0] == 'variable'}
    result['base_address'] = address
    result['physical_age'] = interval[0] if mode == 'dense' else interval[1] if mode == 'ones' else rng.randint(*interval)
    if mode == 'ones':
        result.update({node[1]: (1 << node[2])-1 for node in terms.nodes
                       if node[0] == 'variable' and node[1] not in ('base_address', 'physical_age')})
    if mode == 'dense':
        for site in range(-16, 17):
            at = (address+site) % f.Q
            result.update({f'meta_{site}_kind': c.MEM, f'meta_{site}_index': at,
                           f'meta_{site}_first': 0, f'meta_{site}_last': 0,
                           f'proc_{site}_data': 0x3000+site})
            for channel, sign in (('lp', -1), ('rp', 1)):
                result.update({f'proc_{site}_{channel}_valid': 1,
                               f'proc_{site}_{channel}_remaining': int(at == (0 if sign < 0 else f.Q-1)),
                               f'proc_{site}_{channel}_target': (at+sign) % f.Q,
                               f'proc_{site}_{channel}_data': (0x1000 if sign < 0 else 0x2000)+site})
        if phase is not None:
            result.update(old_direction=c.RIGHT, old_ra=address, old_rb=address,
                          old_rd=tag if phase == c.TRANSMIT else address,
                          old_value=0x4000, old_alu=c.ADD)
    return result


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
    assert cert['support'] == proof.certify_support()
    intervals = proof.clock.regular_intervals()[:1] if cert['pilot'] else proof.clock.regular_intervals()
    expected = {(phase, interval) for phase in (None, *range(8)) for interval in intervals}
    assert len(cert['cases']) == cert['case_count'] == len(expected)
    assert {(row['phase'], tuple(row['interval'])) for row in cert['cases']} == expected
    assert all(row['passed'] for row in cert['cases'])
    rng = random.Random(2026092706)
    count = dense = 0
    digest = hashlib.sha256()
    for interval in intervals:
        for phase in (None, *range(8)):
            terms, raw, local = proof.prepare(phase, interval)
            holders = tuple(range(-4, 5)) if phase is not None else (0,)
            full = [tuple(raw(pos+j) for j in f.NEIGHBORHOOD) for pos in holders]
            erased = [tuple(raw(pos+j, mail=False) for j in f.NEIGHBORHOOD) for pos in holders]
            changes = [{f.COL[f's{delta+2}_{name}']: value for delta in f.OFFSETS
                        for name, value in local(pos+delta).items()} for pos in holders]
            patterns = [(0, 'dense', 0), (f.Q-1, 'dense', 15), (1, 'ones', 0),
                        (f.Q-2, 'random', 0), (f.Q//2, 'random', 0)]
            if phase == c.TRANSMIT:
                patterns.extend((17, 'dense', tag) for tag in range(16))
            for address, mode, tag in patterns:
                values = evaluate(terms, assignments(terms, phase, interval, address, mode, rng, tag))
                assert all(lo <= values[x] <= hi for x, (lo, hi) in terms.ranges.items())
                for pos, old, without, replacement in zip(holders, full, erased, changes):
                    neighbors = tuple(f.decode_cell(tuple(values[x] for x in row)) for row in old)
                    clean = tuple(f.decode_cell(tuple(values[x] for x in row)) for row in without)
                    actual = f.local_step(neighbors)
                    baseline = f.local_step(clean)
                    assert actual == native.local_step(neighbors), (phase, interval, address, mode, pos, 'full native')
                    assert baseline == native.local_step(clean), (phase, interval, address, mode, pos, 'baseline native')
                    wanted = list(f.encode_cell(baseline))
                    for index, term in replacement.items():
                        wanted[index] = values[term]
                    assert f.encode_cell(actual) == tuple(wanted), (phase, interval, address, mode, tag, pos)
                    digest.update(np.array(wanted, dtype=np.uint64).tobytes())
                    count += 1
                    dense += int(mode == 'dense')
        print(json.dumps(dict(interval=interval, full_outputs=count, seconds=time.perf_counter()-started)), flush=True)
    paths = [Path(__file__), Path(proof.__file__), Path('tests/fixed_rule/test_small_holder_mail_factorization.py'),
             Path('experiments/fixed_rule/audit_small_holder_position_events.py')]
    result = dict(passed=True, complete_scalar_native_outputs=count, mail_erased_scalar_native_outputs=count,
                  dense_delivery_outputs=dense, raw_words_per_output=f.FIELDS, output_sha256=digest.hexdigest(),
                  certificate_sha256=sha(args.certificate), source_sha256={str(path): sha(path) for path in paths},
                  seconds=time.perf_counter()-started, host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  limitation='Finite semantics audit of symbolic factorization, including dense all-site incoming mail and all SEND tags. Not a physical whole-period or nested trajectory.')
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
