"""Independent collision replay and invalid-PC flight proof for this trajectory.

Replays scalar local procedures until exactly one FETCH head remains and its PC
matches no metadata index in its closed ROM interval. Its remaining flight is a
proved reflection cycle, with no instruction, Data write or packet operation.
Commit/reset are independently constructed and checked with scalar full-G probes.
"""
import argparse
import json
import resource
import time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_core as c
from gacsca.fixed_rule import retimed_holder_program as p, retimed_holder_projected as r
from gacsca.fixed_rule import retimed_holder_literal_cone as cone
from experiments.fixed_rule.audit_retimed_holder_burst_recovery import SparseProcedures, NAMES
from experiments.fixed_rule.run_retimed_holder_streamed_repair import sha

COL = {n:i for i,n in enumerate(NAMES)}


def scalar_outputs(before, after, positions):
    for pos in positions:
        cells = tuple(f.decode_cell(before[(pos+d) % f.Q]) for d in f.NEIGHBORHOOD)
        expected = f.encode_cell(r.lift(r.project(f.local_step(cells))))
        np.testing.assert_array_equal(after[pos], expected)
    return len(positions)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    path, out = Path(args.input), Path(args.output)
    if out.exists():
        raise FileExistsError(out)
    started = time.perf_counter()
    receipt = json.loads(path.read_text())
    assert receipt['completed'] and receipt['error'] is None and receipt['pilot_ticks'] is None
    artifact = path.with_suffix('.npz')
    assert sha(artifact) == receipt['artifact_sha256']
    for name,digest in receipt['source_sha256'].items():
        assert sha(name) == digest, name
    source_path = Path(receipt['source_receipt'])
    source = json.loads(source_path.read_text())
    assert sha(source_path) == receipt['source_receipt_sha256']
    assert sha(source_path.with_suffix('.npz')) == receipt['source_artifact_sha256']
    scalar_count = 0
    with np.load(artifact, allow_pickle=False) as saved, np.load(source_path.with_suffix('.npz'), allow_pickle=False) as original:
        from gacsca.fixed_rule import retimed_holder_late_flags as late
        fields = ('bank', 'active_rows', 'counts', 'flags', 'signals', 'age', 'time')
        state = {k:original['final_background_'+k] for k in fields}
        initial = late.render(state)
        initial[original['final_exception_positions']] = original['final_exception_values']
        np.testing.assert_array_equal(initial, saved['initial'])
        actual = SparseProcedures(initial)
        clock = receipt['initial_time']
        rom = cone.rom()
        length = len(p.base_rom())
        targets = {row['time']:i for i,row in enumerate(receipt['checkpoints'])}
        transitions = []
        previous_heads = None
        # This bound is an audit resource, not a physical limit or fallback.
        for tick in range(65537):
            heads = sorted(pos for pos in actual.live if actual.words[pos, COL['head']])
            if len(heads) != previous_heads:
                transitions.append(dict(time=clock, head_positions=heads))
                previous_heads = len(heads)
            if clock in targets:
                np.testing.assert_array_equal(actual.render(clock % f.U, 0), saved[f'checkpoint{targets[clock]}'])
            if len(heads) == 1:
                pos = heads[0]
                row = actual.words[pos]
                if int(row[COL['phase']]) == c.FETCH and not np.any(rom[:length, 1] == row[COL['pc']]):
                    break
            if tick == 65536:
                raise RuntimeError('bounded scalar collision prefix did not reach the claimed invariant')
            actual.step(clock % f.U)
            clock += 1
            if tick and tick % 2048 == 0:
                print(json.dumps(dict(stage='scalar collision replay', ticks=tick, head_count=len(heads), seconds=time.perf_counter()-started)), flush=True)
        collapse_time, invalid_pc = clock, int(actual.words[pos, COL['pc']])
        assert pos < length and actual.words[pos, COL['phase']] == c.FETCH
        assert not np.any(actual.words[:, [COL[n] for n in NAMES if n.startswith(('lp_', 'rp_'))]])
        # The closed physical ROM interval has exactly one first and last marker.
        assert list(np.flatnonzero(rom[:, c.STATIC.index('first')])) == [0]
        assert list(np.flatnonzero(rom[:, c.STATIC.index('last')])) == [length-1]
        assert invalid_pc > int(np.max(rom[:length, c.STATIC.index('index')]))
        assert clock < f.ACTIVE_ENDS[4]
        control_indices = [COL[n] for n in ('head', *c.CONTROL)]
        def flight(until):
            nonlocal clock, pos
            assert clock <= until <= f.ACTIVE_ENDS[4]
            words = actual.words[pos, control_indices].copy()
            direction = int(actual.words[pos, COL['direction']])
            phase = pos if not direction else 2*length-1-pos
            phase = (phase+(until-clock)) % (2*length)
            new_pos = phase if phase < length else 2*length-1-phase
            words[control_indices.index(COL['direction'])] = int(phase >= length)
            actual.words[pos, control_indices] = 0
            actual.words[new_pos, control_indices] = words
            pos, clock, actual.live = new_pos, until, {new_pos}
        for row in receipt['checkpoints']:
            target = row['time']
            if target < clock:
                continue
            if target <= f.ACTIVE_ENDS[4]:
                flight(target)
            elif target == f.U-1:
                assert clock == f.ACTIVE_ENDS[4] and not c.active(clock)
                clock = target  # every procedure word freezes in this inactive interval
            elif target == f.U:
                assert clock == f.U-1
                before = actual.render(f.U-1, 0)
                old_data = actual.words[:, COL['data']].copy()
                selected = (rom[:, 0] == c.MEM) & (rom[:, c.STATIC.index('first')] == 0) & ((rom[:, c.STATIC.index('a')] & c.INFO) != 0)
                addresses = np.flatnonzero(selected)
                actual.words[addresses, COL['data']] = old_data[(addresses+1) % f.Q]
                clock = target
                after = actual.render(0, 0)
                probe = sorted({(int(a)+d) % f.Q for a in addresses for d in f.OFFSETS} | {0, f.Q-1, pos})
                scalar_count += scalar_outputs(before, after, probe)
            elif target == f.U+1:
                assert clock == f.U and actual.words[pos, COL['phase']] == c.FETCH
                before = actual.render(0, 0)
                first = rom[:, c.STATIC.index('first')] != 0
                erase = first | ((rom[:, 0] == c.MEM) & ((rom[:, c.STATIC.index('a')] & 1) != 0))
                actual.words[:, [COL[n] for n in NAMES if n != 'data']] = 0
                actual.words[erase, COL['data']] = 0
                actual.words[first, COL['head']] = 1
                actual.words[first, COL['pc']] = rom[first, c.STATIC.index('a')] & np.uint64(0xFFFFFFFF)
                actual.live = set(map(int, np.flatnonzero(first)))
                clock = target
                after = actual.render(1, 0)
                # All potentially changed physical sites, not a sample of them.
                changed = np.flatnonzero(erase)
                probe = sorted({(int(a)+d) % f.Q for a in changed for d in f.OFFSETS} | {(pos+d) % f.Q for d in f.OFFSETS})
                scalar_count += scalar_outputs(before, after, probe)
            else:
                raise AssertionError(('unreviewed checkpoint', target))
            np.testing.assert_array_equal(actual.render(clock % f.U, 0), saved[f'checkpoint{targets[target]}'])
            print(json.dumps(dict(stage='complete checkpoint verified', time=target, seconds=time.perf_counter()-started)), flush=True)
        np.testing.assert_array_equal(actual.render(1, 0), saved['final'])
        committed = saved[f'checkpoint{targets[f.U]}']
        decoded = f.decode_cell(committed[list(p.layout().info), f.COL['s2_data']])
        expected = f.decode_cell(saved['healthy_decoded_words'])
        raw_differences = int(np.count_nonzero(np.array(f.encode_cell(decoded)) != np.array(f.encode_cell(expected))))
        projected_differences = sum(getattr(decoded,n) != getattr(expected,n) for n,_ in r.SCHEMA)
        assert raw_differences == 48 and projected_differences > 0
    sources = (Path(__file__), Path('experiments/fixed_rule/audit_retimed_holder_burst_recovery.py'), Path(c.__file__), Path(f.__file__), Path(p.__file__))
    result = dict(passed=True, exact_recovery_endpoint_bound=True, scalar_collision_prefix_ticks=collapse_time-receipt['initial_time'], scalar_core_candidate_evaluations=actual.evaluations, head_count_transitions=transitions, single_invalid_FETCH_head_time=collapse_time, invalid_pc=invalid_pc, closed_ROM_rows=length, analytic_reflection_period=2*length, complete_raw_checkpoints_verified=len(receipt['checkpoints']), scalar_complete_G_commit_reset_outputs=scalar_count, decoded_raw_word_differences=raw_differences, decoded_projected_word_differences=projected_differences, next_reset_single_head_restored=True, source_receipt_sha256=sha(path), artifact_sha256=receipt['artifact_sha256'], source_sha256={str(x):sha(x) for x in sources}, seconds=time.perf_counter()-started, host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, scope='Specific noisy trajectory independently verified: every collision-prefix tick by scalar procedures, then a checked no-instruction reflection invariant, exact quiet hold and independently constructed commit/reset with full scalar G checks on every potentially changed site. No general multihead scheduler proof or noise threshold.')
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
