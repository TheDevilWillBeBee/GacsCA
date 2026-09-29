"""Audit saved complete-period states against scalar F and its word descriptor.

This reads execution snapshots only. It neither runs the event backend nor
recreates the physical trajectory with host-side simulated transitions.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time

import numpy as np

from gacsca.fixed_rule import retimed_holder_rule as f
from gacsca.fixed_rule import retimed_holder_core as c
from gacsca.fixed_rule import retimed_holder_projected as r
from gacsca.fixed_rule import retimed_holder_program as p
from experiments.fixed_rule.audit_small_holder_position_events import sha


def check_boundary(data, right, expected):
    """Check every Info word, retained Signal bit, and non-MEM Data word."""
    n = len(expected)
    assert data.shape == (n, f.Q), 'incomplete physical Data snapshot'
    assert right.shape == (n,), 'incomplete physical Signal snapshot'
    raw = np.array([f.encode_cell(r.lift(cell)) for cell in expected], dtype=np.uint64)
    assert np.array_equal(data[:, list(p.layout().info)], raw), 'complete raw Info mismatch'
    assert np.array_equal(right, [cell.f1 for cell in expected]), 'captured right Signal mismatch'
    assert all(cell.f2 == 0 for cell in expected), 'outside supported left-zero Signal domain'
    nonmem = np.array([r.record(a)['kind'] != c.MEM for a in range(f.Q)])
    assert not np.any(data[:, nonmem]), 'non-MEM physical Data is nonzero'
    return n * f.FIELDS


def audit(path):
    receipt = json.loads(Path(path).read_text())
    assert receipt['passed']
    for source, wanted in receipt['source_sha256'].items():
        assert sha(source) == wanted, source
    assert receipt['descriptor_sha256'] == f.self_description().digest()
    assert receipt['rom_sha256'] == hashlib.sha256(p.base_rom().tobytes()).hexdigest()
    snapshot = Path(receipt['snapshot'])
    assert sha(snapshot) == receipt['snapshot_sha256'], 'snapshot hash mismatch'
    n, periods = receipt['colonies'], receipt['periods']
    descriptor = f.self_description()
    rows = []
    total_changed = 0
    with np.load(snapshot, allow_pickle=False) as saved:
        assert saved['initial_upper'].shape == (n, len(r.SCHEMA))
        upper = r.cells_from_array(saved['initial_upper'])
        assert saved['boundary_data'].shape == (periods, n, f.Q)
        assert saved['boundary_right'].shape == (periods, n)
        assert saved['boundary_age'].shape == (periods,)
        assert not np.any(saved['boundary_age'])
        assert saved['final_heads'].shape == (n, 1 + len(c.CONTROL))
        assert not np.any(saved['final_heads']), 'raw final controller not empty'
        assert saved['final_packets'].shape == (0, 5), 'raw final mail not empty'
        for epoch in range(periods):
            expected = []
            changed = 0
            for col in range(n):
                neighborhood = tuple(r.lift(upper[(col+j) % n]) for j in f.NEIGHBORHOOD)
                inputs = tuple(word for cell in neighborhood for word in f.encode_cell(cell))
                raw = f.decode_cell(descriptor.evaluate(inputs))
                assert raw == f.local_step(neighborhood), ('scalar/descriptor disagreement', epoch, col)
                cell = r.project(raw)
                expected.append(cell)
                for delta in f.OFFSETS:
                    for name in ('head', *c.CONTROL):
                        field = f's{delta+2}_{name}'
                        changed += getattr(cell, field) != getattr(upper[col], field)
            expected = tuple(expected)
            checked = check_boundary(saved['boundary_data'][epoch], saved['boundary_right'][epoch], expected)
            digest = hashlib.sha256(r.array_from_cells(expected).tobytes()).hexdigest()
            assert digest == receipt['period_results'][epoch]['decoded_sha256']
            rows.append(dict(period=epoch+1, complete_raw_words_checked=checked,
                             represented_controller_words_changed=changed,
                             retained_right_signals=saved['boundary_right'][epoch].tolist(),
                             decoded_sha256=digest))
            total_changed += changed
            upper = expected
    assert total_changed > 0, 'fixture did not exercise represented controllers'
    assert receipt['physical_ticks'] == periods * f.U
    return dict(passed=True, execution=str(path), execution_sha256=sha(path),
                snapshot_sha256=sha(snapshot), colonies=n, periods=periods,
                period_results=rows, scalar_and_descriptor_agree=True,
                saved_complete_Info_matches=True, saved_final_controller_and_mail_empty=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--execution', action='append', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    out = Path(args.output)
    if out.exists():
        raise FileExistsError('preserve evidence')
    started = time.perf_counter()
    rows = [audit(path) for path in args.execution]
    result = dict(passed=True, cases=rows,
                  source_sha256={str(path): sha(path) for path in
                                 (Path(__file__), *(Path(module.__file__) for module in (f, c, r, p)))},
                  seconds=time.perf_counter()-started,
                  host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  limitation='Saved boundary-state audit, not an independent physical execution or a general backend-equivalence proof. No full upper work period at depth two or noise claim.')
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
