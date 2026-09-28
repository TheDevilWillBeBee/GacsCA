"""Independent artifact audit of two successive resident GPU work periods.

This validates complete decoded controller states and committed physical
snapshots. Continuity of the GPU allocation is recorded by the execution driver;
snapshots alone cannot prove how the intervening trajectory was obtained.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time

import numpy as np

from gacsca.fixed_rule import small_holder_rule as f
from gacsca.fixed_rule import small_holder_projected as r
from gacsca.fixed_rule import small_holder_quotient as q
from gacsca.fixed_rule import small_holder_program as p
from gacsca.fixed_rule import small_holder_native as native
from gacsca.fixed_rule import small_holder_resident_period as gpu
from gacsca.fixed_rule import small_holder_prefix_description


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def audit(stem):
    started = time.perf_counter()
    manifest = json.loads(stem.with_suffix('.json').read_text())
    description = f.self_description()
    assert manifest['passed']
    assert manifest['physical_rule_description'] == description.digest()
    assert manifest['successive_periods'] == 2
    for path, wanted in manifest['source_sha256'].items():
        assert digest(path) == wanted, path
    assert digest(gpu.library()._name) == manifest['binary_sha256']
    assert digest(stem.with_suffix('.npz')) == manifest['artifact_sha256']
    metrics = manifest['metrics']
    assert metrics['physical_ticks'] == manifest['physical_ticks'] == 2*f.U
    assert metrics['physical_ticks'] == metrics['literal_ticks'] + metrics['transport_or_quiet_ticks']
    assert metrics['literal_ticks'] > 0 and metrics['logical_evaluations'] > 0
    periods = []
    with np.load(stem.with_suffix('.npz'), allow_pickle=False) as archive:
        raw = tuple(r.lift(x) for x in r.cells_from_array(archive['initial_top']))
        n = len(raw)
        g = p.layout()
        assert manifest['physical_sites'] == n*f.Q
        decoded = archive['decoded']
        assert decoded.shape == (2, n, f.FIELDS)
        np.testing.assert_array_equal(decoded, archive['expected'])
        addresses = np.array([*range(g.computation_cells), *range(f.Q-5, f.Q)], dtype=np.uint64)
        for period, key in enumerate(('first_stored', 'second_stored')):
            scalar = f.step_ring(raw)
            assert scalar == native.step_ring(raw)
            described = tuple(f.decode_cell(description.evaluate(tuple(
                word for j in f.NEIGHBORHOOD
                for word in f.encode_cell(raw[(i+j) % n])
            ))) for i in range(n))
            assert described == scalar
            projected = tuple(r.lift(r.project(x)) for x in scalar)
            expected = native.array_from_cells(projected)
            np.testing.assert_array_equal(decoded[period], expected)
            changes = sum(getattr(old, name) != getattr(new, name)
                          for old, new in zip(raw, projected)
                          for name, _ in r.SCHEMA if name.startswith('s'))
            assert changes > 0
            evidence = manifest['periods'][period]
            assert evidence['raw_controller_changes'] == changes
            flat = archive[key]
            assert flat.shape == (n*(g.computation_cells+5), len(q.SCHEMA))
            assert flat.dtype == np.uint64
            assert hashlib.sha256(flat.tobytes()).hexdigest() == evidence['stored_sha256']
            stored = flat.reshape(n, g.computation_cells+5, len(q.SCHEMA))
            np.testing.assert_array_equal(stored[:, np.array(g.info), q.COL['data']], expected)
            np.testing.assert_array_equal(stored[:, np.array(g.hold), q.COL['data']], expected)
            old_raw = native.array_from_cells(raw)
            neighborhoods = np.stack([old_raw[(np.arange(n)+j) % n]
                                      for j in f.NEIGHBORHOOD], axis=1).reshape(n, -1)
            for stage in range(3):
                history = tuple(g.history(stage, j, k)
                                for j in f.NEIGHBORHOOD for k in range(f.FIELDS))
                np.testing.assert_array_equal(stored[:, np.array(history), q.COL['data']], neighborhoods)
            np.testing.assert_array_equal(stored[:, np.array(g.votes), q.COL['data']], neighborhoods)
            signals = np.zeros((n, g.computation_cells+5), dtype=np.uint64)
            weights = np.array([16, 8, 4, 2, 1], dtype=np.uint64)
            signals[:, 1:6] = expected[:, f.COL['f2'], None]*weights
            signals[:, -5:] = expected[:, f.COL['f1'], None]*weights
            np.testing.assert_array_equal(stored[:, :, q.COL['signal']], signals)
            assert bool(np.any(signals)) == evidence['old_signals_carried']
            assert not np.any(stored[:, :, [q.COL[x] for x in ('age', 'f1', 'f2', 'wf1', 'wf2')]])
            for part in stored:
                np.testing.assert_array_equal(part[:, q.COL['address']], addresses)
                for name, width in q.SCHEMA:
                    if width < 64:
                        assert np.all(part[:, q.COL[name]] < 1 << width), name
            # The execution driver compared every omitted gap cell with the
            # CPU reference. Reconstruct its canonical committed gap here.
            gap = np.zeros((f.Q-5-g.computation_cells, len(q.SCHEMA)), dtype=np.uint64)
            gap[:, q.COL['address']] = np.arange(g.computation_cells, f.Q-5)
            gaps = hashlib.sha256()
            for _ in range(n):
                gaps.update(gap.tobytes())
            assert gaps.hexdigest() == evidence['gap_sha256']
            periods.append(dict(period=period+1, raw_controller_changes=changes,
                                all_raw_decoded_fields_match=True,
                                all_histories_votes_info_hold_match=True,
                                complete_stored_and_gap_hashes_match=True,
                                carried_signals_match=True))
            raw = projected
            del stored, flat
    assert int(decoded[0, 7, f.COL['s2_data']]) == 0x123456789ABCDEF0
    return dict(passed=True, periods=periods,
                scalar_native_complete_description_agree=True,
                physical_ticks=2*f.U, coherent_sites_checked_per_commit=n*f.Q,
                description_sha256=description.digest(),
                controller_description_sha256=small_holder_prefix_description.build().digest(),
                rom_bytes_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest(),
                source_files_checked=len(manifest['source_sha256']),
                manifest_sha256=digest(stem.with_suffix('.json')),
                artifact_sha256=digest(stem.with_suffix('.npz')),
                audit_source_sha256=digest(__file__),
                seconds=time.perf_counter()-started,
                host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                limitations=[
                    'Two periods at one simulation link; not two nested hierarchy levels.',
                    'Continuous allocation and no host upper transition during advance are execution-driver checks; snapshots alone cannot prove trajectory provenance.',
                    'Canonical coherent domain with restricted suffix Signals; no noisy amplification claim.'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists():
        raise FileExistsError('preserve prior audit')
    result = audit(Path(args.input))
    output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
