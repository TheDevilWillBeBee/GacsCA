"""Literal continuation of the actual repaired endpoint under nine fresh marks.

Checks all retained scalar/native outputs. Pair coupling concerns old residue;
the third, fault-free trajectory separately exposes remaining fresh damage.
"""
import argparse
import json
from pathlib import Path
import resource
import time
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_core as c
from gacsca.fixed_rule import retimed_holder_projected as r
from gacsca.fixed_rule import retimed_holder_literal_cone as cone
from gacsca.fixed_rule import retimed_holder_wide_inert_storage as storage
from experiments.fixed_rule.audit_retimed_holder_prefix_embedding import sha
from experiments.fixed_rule.audit_retimed_holder_residual_noise import scalar_at


def continue_pair(actual, comparison, positions, anchor, *, controller=True, geometry=True,
                  verify_scalar=False, ticks=5):
    if ticks != 5 or len(positions) != 147 or not np.array_equal(positions, np.arange(anchor-72, anchor+75)):
        raise ValueError('exact five-tick causal window required')
    if actual.dtype != np.uint64 or comparison.dtype != np.uint64 or actual.shape != comparison.shape or actual.shape != (147, f.FIELDS):
        raise ValueError('complete raw paired states required')
    actual, comparison = actual.copy(), comparison.copy()
    untouched = comparison.copy()
    initial_mask = np.any(actual != comparison, axis=1)
    assert np.flatnonzero(initial_mask).size == 7
    assert np.array_equal(positions[initial_mask], np.arange(anchor-2, anchor+5))
    arrays = dict(initial_actual=actual.copy(), initial_comparison=comparison.copy(), initial_positions=positions.copy())
    rows, marks = [], []
    scalar_words = native_words = 0
    for tick in range(ticks):
        offsets = (-3, -2, -1) if tick == 1 and controller else (-5, -4, -3, 3, 4, 5) if tick == 2 and geometry else ()
        for offset in offsets:
            site = anchor+offset
            index = site-positions[0]
            replacement = comparison[index:index+1].copy()
            if tick == 1:
                slot = -1-offset+2
                replacement[0, f.COL[f's{slot}_head']] = 1
                replacement[0, f.COL[f's{slot}_phase']] = c.READ_A
                replacement[0, f.COL[f's{slot}_ra']] = 65
            else:
                replacement[0, f.COL['address']] = 64+offset
                cone.normalize(replacement)
            assert np.array_equal(replacement, cone.normalize(replacement.copy()))
            actual[index] = comparison[index] = replacement[0]
            marks.append((tick, int(site), replacement[0].copy()))
        before = (actual, comparison, untouched)
        after = tuple(cone.step(world)[7:-7].copy() for world in before)
        if verify_scalar:
            for source, target in zip(before, after):
                for index in range(7, len(source)-7):
                    np.testing.assert_array_equal(scalar_at(source, index), target[index-7])
                    scalar_words += f.FIELDS
        actual, comparison, untouched = after
        positions = positions[7:-7]
        native_words += sum(world.size for world in after)
        delta = actual != comparison
        at = positions[np.any(delta, axis=1)]
        assert np.all((at >= anchor-2-7*(tick+1)) & (at <= anchor+4+7*(tick+1)))
        counts = np.count_nonzero(delta, axis=0)
        controller_fields = [j for j,(name,_) in enumerate(f.SCHEMA)
                             if name.startswith(tuple(f's{k}_' for k in range(5))) and name.split('_', 1)[1] in ('head', *c.CONTROL)]
        rows.append(dict(tick=tick+1, paired_different_sites=len(at),
                         paired_different_raw_words=int(np.count_nonzero(delta)),
                         fields={name:int(counts[j]) for j,(name,_) in enumerate(f.SCHEMA) if counts[j]},
                         differing_controller_words=int(np.count_nonzero(delta[:,controller_fields])),
                         actual_vs_fault_free_raw_words=int(np.count_nonzero(actual != untouched)),
                         comparison_vs_fault_free_raw_words=int(np.count_nonzero(comparison != untouched))))
        arrays[f'tick{tick+1}_actual'] = actual.copy()
        arrays[f'tick{tick+1}_comparison'] = comparison.copy()
        arrays[f'tick{tick+1}_fault_free'] = untouched.copy()
        arrays[f'tick{tick+1}_positions'] = positions.copy()
    arrays['fault_times'] = np.array([x[0] for x in marks], dtype=np.int64)
    arrays['fault_positions'] = np.array([x[1] for x in marks], dtype=np.int64)
    arrays['fault_replacements'] = np.array([x[2] for x in marks], dtype=np.uint64).reshape(-1, f.FIELDS)
    return dict(trace=rows, fresh_full_state_marks=len(marks), scalar_raw_output_words=scalar_words,
                retained_native_output_words=native_words,
                paired_rejoined=not np.any(actual != comparison),
                fault_free_rejoined=not np.any(actual != untouched)), arrays


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    out = Path(parser.parse_args().output)
    artifact = out.with_suffix('.npz')
    if out.exists() or artifact.exists():
        raise FileExistsError(out)
    started = time.perf_counter()
    root = Path('figs/fixed_rule')
    paths = [root/('retimed_holder_'+name+'.json') for name in
             ('wide_next_periods_3_v2', 'wide_next_periods_audit_v1', 'full_ring_repair_v1')]
    docs = [json.loads(path.read_text()) for path in paths]
    for doc in docs:
        assert doc.get('passed', doc.get('completed')) is True
        for source, digest in {**doc.get('source_sha256', {}), **doc.get('input_sha256', {})}.items():
            assert sha(source) == digest, source
    assert sha(paths[0].with_suffix('.npz')) == docs[0]['artifact_sha256']
    assert docs[1]['source_receipt_sha256'] == sha(paths[0])
    assert docs[2]['conditional_full_ring_physical_repair_join']
    with np.load(paths[0].with_suffix('.npz'), allow_pickle=False) as old:
        state = {name:old['period3_'+name] for name in ('bank', 'active_rows', 'counts', 'flags', 'signals', 'age', 'time')}
        assert int(state['age']) == 0 and int(state['time']) == 4*f.U
        assert not np.any(state['flags'])
        retained_positions, retained_values = old['retained_positions'], old['retained_values']
        anchor = int(retained_positions[0])
        assert retained_positions.tolist() == [36*f.Q+a for a in (30960,30961,30962)]
        assert retained_values.tolist() == docs[2]['retained_values']
        positions = np.arange(anchor-72, anchor+75)
        # Independent complete snapshot accessor, including all active fields.
        view = storage.View(state, retained_positions, retained_values)
        actual = view.cells(positions)
        comparison = cone.BankImage(state['bank'], state['signals']).cells(positions)
        expected = comparison.copy()
        for pos, value in zip(retained_positions, retained_values):
            for d in f.OFFSETS:
                expected[positions+d == pos, f.COL[f's{d+2}_data']] = value
        np.testing.assert_array_equal(actual, expected)
        del view
    result, arrays = continue_pair(actual, comparison, positions, anchor, verify_scalar=True)
    assert result['fresh_full_state_marks'] == 9
    assert result['trace'][3]['fields']['s4_value'] == 1
    assert result['trace'][3]['differing_controller_words'] == 1
    assert result['paired_rejoined'] and not result['fault_free_rejoined']
    index = int(np.flatnonzero(arrays['tick4_positions'] == anchor)[0])
    value = int(arrays['tick4_actual'][index, f.COL['s4_value']])
    assert value == int(retained_values[1])
    assert arrays['tick4_comparison'][index, f.COL['s4_value']] == 0
    # The pilot stored array aliases: its tick1/tick2 snapshots were mutated
    # by the following fresh replacements. Reconstruct precisely that aliasing
    # for provenance, while the accepted snapshots above are immutable copies.
    pilot_path = root/'retimed_holder_residual_reactivation_pilot_v1.npz'
    with np.load(pilot_path, allow_pickle=False) as pilot:
        for tick in range(1, 6):
            indices = arrays[f'tick{tick}_positions']-pilot[f'tick{tick}_positions'][0]
            for name in ('actual', 'comparison'):
                expected_pilot = arrays[f'tick{tick}_{name}'].copy()
                for mark in np.flatnonzero(arrays['fault_times'] == tick):
                    at = int(arrays['fault_positions'][mark]-arrays[f'tick{tick}_positions'][0])
                    expected_pilot[at] = arrays['fault_replacements'][mark]
                np.testing.assert_array_equal(expected_pilot, pilot[f'tick{tick}_{name}'][indices])
    np.savez_compressed(artifact, **arrays)
    source_paths = (Path(__file__), Path(f.__file__), Path(c.__file__), Path(r.__file__),
                    Path(cone.__file__), Path(storage.__file__),
                    Path('experiments/fixed_rule/audit_retimed_holder_residual_noise.py'))
    result.update(passed=True, observed_residual_value_activated=True, activated_value=value,
                  activation_tick=4, paired_rejoin_tick=5, full_ring_initial_relation_conditional=True,
                  pilot_early_snapshot_aliasing_identified=True, accepted_snapshots_are_copies=True,
                  initial_local_physical_time=4*f.U, full_ring_anchor=docs[2]['retained_full_positions'][0],
                  descriptor_sha256=f.self_description().digest(),
                  input_sha256={str(path):sha(path) for path in (*paths, pilot_path)},
                  source_sha256={str(path):sha(path) for path in source_paths},
                  artifact_sha256=sha(artifact), seconds=time.perf_counter()-started,
                  host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  scope='Exact five-tick complete-rule continuation from the saved repaired '
                        'endpoint under nine identical paired full-state marks. An actual '
                        'retained even-valued word enters a controller before complete paired '
                        'coupling at tick five. Fresh damage remains versus a fault-free third '
                        'trajectory; no complete fresh-fault repair or threshold claim.')
    with out.open('x') as stream:
        stream.write(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
