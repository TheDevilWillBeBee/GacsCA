"""Audit real SEND continuation records and one-tick full-rule boundaries."""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time

import numpy as np
from gacsca.fixed_rule import small_holder_rule as f, small_holder_core as c
from gacsca.fixed_rule import small_holder_native as native, small_holder_quotient as q, small_holder_program as p
from experiments.fixed_rule import small_holder_send_dispatch_execution as execution
from experiments.fixed_rule.audit_small_holder_position_events import sha


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--execution', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    out = Path(args.output)
    if out.exists():
        raise FileExistsError('preserve evidence')
    started = time.perf_counter()
    stem = Path(args.execution)
    run = json.loads(stem.with_suffix('.json').read_text())
    assert run['passed'] and run['descriptor_sha256'] == f.self_description().digest()
    for path, expected in run['source_sha256'].items():
        assert sha(path) == expected, path
    assert sha(stem.with_suffix('.npz')) == run['artifact_sha256']
    pcs = execution.selected_pcs(run['pilot'])
    expected_cases = [(pc, age) for pc in pcs for age in (1, c.VOTE_AGES[0]+1)]
    assert [(case['pc'], case['age']) for case in run['cases']] == expected_cases
    assert run['physical_SEND_successors'] == len(expected_cases)*6
    assert run['packet_tags'] == sorted({p.layout().instructions[pc].d for pc in pcs})
    records = boundaries = deliveries = in_flight = 0
    digest = hashlib.sha256()
    with np.load(stem.with_suffix('.npz'), allow_pickle=False) as saved:
        assert len(saved['records']) == len(saved['indices']) == run['complete_logical_records_saved']
        for number, case in enumerate(run['cases']):
            pc, age = case['pc'], case['age']
            trace, description = execution.frames(pc, age)
            for key, expected in description.items():
                assert case[key] == expected
            assert case['checkpoint_times'] == [frame['time'] for frame in trace]
            assert all(a['time'] < b['time'] for a, b in zip(trace, trace[1:]))
            birth = next(frame for frame in trace if frame['time'] == description['birth_tick'])
            assert all(len(packets) == 1 for packets in birth['packets'])
            final = trace[-1]
            if final['time'] - birth['time'] >= description['packet_distance']:
                assert all(not packets for packets in final['packets'])
                deliveries += 6
            else:
                assert all(len(packets) == 1 for packets in final['packets'])
                in_flight += 6
            models = {frame['time']: execution.instruction.logical_model(pc, age, frame) for frame in trace}
            begin = case['records_start']
            end = begin + case['records_count']
            assert begin == records and end <= len(saved['records'])
            for row, index in zip(saved['records'][begin:end], saved['indices'][begin:end]):
                ipc, iage, elapsed, col, address = map(int, index)
                assert (ipc, iage) == (pc, age) and 0 <= col < 6 and 0 <= address < f.Q
                position = col*f.Q + address
                model = models[elapsed]
                assert tuple(map(int, row)) == q.encode_cell(model(position))
                digest.update(np.array(execution.expected_raw(model, position), dtype=np.uint64).tobytes())
                records += 1
            for before, after in zip(trace, trace[1:]):
                if after['time'] - before['time'] != 1:
                    continue
                col = number % 6
                addresses = {0, f.Q-1, p.layout().instructions[pc].b}
                for frame in (before, after):
                    if frame['head'] is not None:
                        addresses.update((frame['head'], (frame['head']-1)%f.Q, (frame['head']+1)%f.Q))
                    for address in frame['packets'][col]:
                        addresses.update((address, (address-1)%f.Q, (address+1)%f.Q))
                old, new = models[before['time']], models[after['time']]
                for address in sorted(addresses):
                    position = col*f.Q + address
                    neighbors = tuple(f.decode_cell(execution.expected_raw(old, position+j)) for j in f.NEIGHBORHOOD)
                    result = f.local_step(neighbors)
                    assert result == native.local_step(neighbors), (pc, age, before['time'], address, 'native')
                    assert f.encode_cell(result) == execution.expected_raw(new, position), (pc, age, before['time'], address)
                    boundaries += 1
    assert records == run['complete_logical_records_saved'] == run['complete_raw_probe_records_checked']
    assert digest.hexdigest() == run['raw_probe_sha256']
    paths = [Path(__file__), Path(execution.__file__), Path('tests/fixed_rule/test_small_holder_send_dispatch.py')]
    result = dict(passed=True, physical_SEND_successors=run['physical_SEND_successors'],
                  packet_tags=run['packet_tags'], packets_delivered_by_final_checkpoint=deliveries,
                  packets_still_in_flight_at_final_checkpoint=in_flight,
                  saved_complete_logical_records_checked=records, expected_raw_probe_records_rehashed=records,
                  raw_probe_sha256=digest.hexdigest(), complete_boundary_scalar_native_outputs=boundaries,
                  execution_manifest_sha256=sha(stem.with_suffix('.json')),
                  execution_artifact_sha256=sha(stem.with_suffix('.npz')),
                  source_sha256={str(path): sha(path) for path in paths},
                  seconds=time.perf_counter()-started, host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  limitation='Finite uninterrupted SEND-successor checkpoint audit, not microstep replay. Long-hop packets may remain live. No arbitrary packet trains, whole-period or nested/noisy theorem.')
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
