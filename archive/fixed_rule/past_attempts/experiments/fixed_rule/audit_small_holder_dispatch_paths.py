"""Independent ROM-route and native full-state audit of saved dispatch evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import random
import resource
import time

import numpy as np
from gacsca.fixed_rule import small_holder_rule as f, small_holder_native as native
from gacsca.fixed_rule import small_holder_program as p, small_holder_core as c, small_holder_quotient as q
from gacsca.fixed_rule.wordcode import LIT
from experiments.fixed_rule import certify_small_holder_dispatch_paths as proof
from experiments.fixed_rule import small_holder_dispatch_execution as execution
from experiments.fixed_rule.audit_small_holder_position_events import evaluate, sha


def check_catalog(certificate):
    g = p.layout()
    expected = set()
    for pc, op in enumerate(g.instructions):
        if op.kind == c.HALT:
            continue
        if op.kind in c.ALU_KINDS or op.kind == LIT:
            start = op.d + 1
        elif op.kind in (c.LOAD, c.SEND, c.META):
            start = op.a + 1
        else:
            assert op.kind == c.IF_THIRD
            start = g.memory_count + pc + 1
        target = g.memory_count + pc + 1
        expected.add(('META' if op.kind == c.META else 'ordinary', pc,
                      start, pc + 1, target - start, int(op.kind == c.SEND)))
    for stage, pc in enumerate(g.entries):
        expected.add(('reset_entry', stage, 0, pc, g.memory_count + pc, 0))
    expected.add(('vote_entry', 0, 0, g.entries[4], g.memory_count + g.entries[4], 0))
    rows = {tuple(row) for row in certificate['rows']}
    assert rows == expected
    assert len(rows) == len(certificate['rows']) == certificate['route_count']
    assert sum(row[-1] for row in rows) == certificate['SEND_successors_requiring_mail_composition']
    return len(rows)


def audit_leaf():
    rng = random.Random(2026092603)
    count = 0
    for interval in proof.clock.regular_intervals():
        terms, raw = proof.leaf_prepare(True, interval)
        neighborhoods = [tuple(raw(pos + j) for j in f.NEIGHBORHOOD) for pos in range(-4, 5)]
        wanted = [raw(pos, after=True) for pos in range(-4, 5)]
        for age, mode in ((interval[0], 'zero'), (interval[1], 'ones'), (rng.randint(*interval), 'random')):
            assignments = {node[1]: 0 if mode == 'zero' else (1 << node[2]) - 1
                           if mode == 'ones' else rng.getrandbits(node[2])
                           for node in terms.nodes if node[0] == 'variable'}
            assignments['physical_age'] = age
            assignments['meta_0_index'] = assignments['old_pc']
            values = evaluate(terms, assignments)
            assert terms.hypotheses_hold(values)
            for rows, expected in zip(neighborhoods, wanted):
                neighbors = tuple(f.decode_cell(tuple(values[x] for x in row)) for row in rows)
                result = f.local_step(neighbors)
                assert result == native.local_step(neighbors)
                assert f.encode_cell(result) == tuple(values[x] for x in expected)
                count += 1
    return count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--certificate', required=True)
    parser.add_argument('--execution', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    out = Path(args.output)
    if out.exists():
        raise FileExistsError('preserve evidence')
    started = time.perf_counter()
    certificate = json.loads(Path(args.certificate).read_text())
    stem = Path(args.execution)
    run = json.loads(stem.with_suffix('.json').read_text())
    assert certificate['passed'] and run['passed']
    assert certificate['source_sha256'] == sha(proof.__file__)
    assert certificate['descriptor_sha256'] == run['descriptor_sha256'] == f.self_description().digest()
    for name, filename in proof.SOURCES.items():
        assert certificate['input_sha256'][name] == sha(Path('figs/fixed_rule') / filename)
    for path, expected in run['source_sha256'].items():
        assert sha(path) == expected, path
    assert sha(stem.with_suffix('.npz')) == run['artifact_sha256']
    catalog = check_catalog(certificate)
    leaves = audit_leaf()
    routes = {(row[0], row[1]): row for row in certificate['rows']}
    tasks = execution.tasks(run['pilot'])
    assert len(tasks) == len(run['cases'])
    records = boundaries = 0
    digest = hashlib.sha256()
    with np.load(stem.with_suffix('.npz'), allow_pickle=False) as saved:
        assert len(saved['records']) == len(saved['indices']) == run['complete_logical_records_saved']
        for number, (case, task) in enumerate(zip(run['cases'], tasks)):
            for key, expected in task.items():
                assert case[key] == expected
            initial, frames, description = execution.trajectory(task)
            for key, expected in description.items():
                assert case[key] == expected
            if case['origin'] == 'successor':
                assert p.layout().instructions[case['pc']].kind != c.SEND
                route = routes['ordinary', case['pc']]
            else:
                route = routes[case['origin'], case['stage']]
            assert tuple(route[2:5]) == (case['start_address'], case['target_pc'], case['dispatch_ticks'])
            models = [execution.instruction.logical_model(case['pc'], case['age'], frame) for frame in frames]
            begin = case['records_start']
            end = begin + case['records_count']
            assert begin == records and end <= len(saved['records'])
            for row, index in zip(saved['records'][begin:end], saved['indices'][begin:end]):
                task_number, stage, col, address = map(int, index)
                assert task_number == number and 0 <= stage < 3 and 0 <= col < 6 and 0 <= address < f.Q
                position = col * f.Q + address
                model = models[stage]
                assert tuple(map(int, row)) == q.encode_cell(model(position))
                digest.update(np.array(execution.expected_raw(model, position), dtype=np.uint64).tobytes())
                records += 1
            assert frames[2]['time'] - frames[1]['time'] == 1
            target = case['target_address']
            for address in (target - 2, target, target + 1, target + 2):
                position = (number % 6) * f.Q + address
                neighbors = tuple(f.decode_cell(execution.expected_raw(models[1], position + j)) for j in f.NEIGHBORHOOD)
                result = f.local_step(neighbors)
                assert result == native.local_step(neighbors)
                assert f.encode_cell(result) == execution.expected_raw(models[2], position), (number, address)
                boundaries += 1
    assert records == run['complete_logical_records_saved'] == run['complete_raw_probe_records_checked']
    assert digest.hexdigest() == run['raw_probe_sha256']
    paths = [Path(__file__), Path(proof.__file__), Path(execution.__file__),
             Path('tests/fixed_rule/test_small_holder_dispatch_paths.py')]
    result = dict(passed=True, actual_ROM_catalog_routes_checked=catalog,
                  matching_memory_index_full_scalar_native_outputs=leaves,
                  FETCH_boundary_full_scalar_native_outputs=boundaries,
                  saved_complete_logical_records_checked=records,
                  expected_raw_probe_records_rehashed=records, raw_probe_sha256=digest.hexdigest(),
                  certificate_sha256=sha(args.certificate),
                  execution_manifest_sha256=sha(stem.with_suffix('.json')),
                  execution_artifact_sha256=sha(stem.with_suffix('.npz')),
                  source_sha256={str(path): sha(path) for path in paths},
                  seconds=time.perf_counter()-started,
                  host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  limitation='Finite checkpoint and native semantic audit, not a full microstep replay. All dispatch contracts assume mail-free input; absence of a direct SEND predecessor does not establish that premise. No whole-period or nested/noisy theorem.')
    out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
