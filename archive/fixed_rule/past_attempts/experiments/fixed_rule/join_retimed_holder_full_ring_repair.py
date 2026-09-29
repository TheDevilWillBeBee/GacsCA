"""Conditional full-ring physical normalization and three-period repair join.

Uses the actual committed patch and audited physical window continuation. Full
upper steps and terminal formulas below are diagnostic comparisons, never inputs
to an evolving lower world. The full zero-scratch E entry is a comparison witness.
"""
import argparse
import json
from pathlib import Path
import resource
import time
import numpy as np

from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_core as c
from gacsca.fixed_rule import retimed_holder_projected as r, retimed_holder_program as p
from gacsca.fixed_rule import retimed_holder_literal_cone as cone
from gacsca.fixed_rule import retimed_holder_wide_inert_storage as storage
from gacsca.fixed_rule import retimed_holder_terminal_reference as terminal
from experiments.fixed_rule.audit_retimed_holder_prefix_embedding import sha


INPUTS = ('noisy_commit_embedding_v2', 'normalization_prefix_v1',
          'wide_macrostep_v1', 'wide_macrostep_audit_v1',
          'wide_next_periods_3_v2', 'wide_next_periods_audit_v1',
          'wide_reset_entry_v1', 'upper_embedding_v1',
          'inert_data_v3', 'noiseless_period_v1',
          'terminal_layout_v1', 'terminal_reference_v1')


def post_reset_words(info, retained=None):
    """Diagnostic complete logical frame expected after the literal first reset."""
    assert info.dtype == np.uint64 and info.shape == (f.FIELDS,)
    words = np.zeros((f.Q, len(storage.NAMES)), dtype=np.uint64)
    words[np.array(p.layout().info), storage.DATA] = info
    words[0, storage.NAMES.index('head')] = 1
    words[0, storage.NAMES.index('pc')] = p.layout().entries[0]
    for address, value in (retained or {}).items():
        assert address in (30960, 30961, 30962)
        words[address, storage.DATA] = value
    return words


def assert_only_metadata_changed(before, after):
    assert before.dtype == after.dtype == np.uint64
    assert before.shape == after.shape and before.ndim == 2 and before.shape[1] == f.FIELDS
    np.testing.assert_array_equal(before[:, len(f.STATIC):], after[:, len(f.STATIC):])
    np.testing.assert_array_equal(cone.normalize(before.copy()), after)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    out = Path(parser.parse_args().output)
    artifact = out.with_suffix('.npz')
    if out.exists() or artifact.exists():
        raise FileExistsError(out)
    started = time.perf_counter()
    root = Path('figs/fixed_rule')
    paths = {name: root/('retimed_holder_'+name+'.json') for name in INPUTS}
    docs = {name: json.loads(path.read_text()) for name, path in paths.items()}
    for name, doc in docs.items():
        assert doc.get('passed', doc.get('completed')) is True, name
        for source, expected in {**doc.get('source_sha256', {}), **doc.get('input_sha256', {})}.items():
            assert sha(source) == expected, source
    for name in ('noisy_commit_embedding_v2', 'wide_macrostep_v1', 'wide_next_periods_3_v2', 'upper_embedding_v1'):
        assert sha(paths[name].with_suffix('.npz')) == docs[name]['artifact_sha256']
    run = docs['wide_next_periods_3_v2']
    assert run['source_receipt_sha256'] == sha(paths['wide_macrostep_v1'])
    for name in ('wide_next_periods_audit_v1', 'wide_reset_entry_v1'):
        assert docs[name]['source_receipt_sha256'] == sha(paths['wide_next_periods_3_v2'])
        assert docs[name]['artifact_sha256'] == run['artifact_sha256']
    assert docs['wide_macrostep_audit_v1']['source_receipt_sha256'] == sha(paths['wide_macrostep_v1'])
    assert docs['noisy_commit_embedding_v2']['conditional_full_lower_ring_commit_embedding']
    assert docs['normalization_prefix_v1']['normalization_age'] == run['normalization']['age'] == 10487886
    assert run['normalization']['Info_metadata_regenerated_physically']
    assert docs['wide_next_periods_audit_v1']['exact_previous_noisy_state_verified']
    assert docs['wide_reset_entry_v1']['normalized_twin_is_exact_reset_image']
    assert docs['inert_data_v3']['selected_addresses'] == [30960, 30961, 30962]
    assert docs['inert_data_v3']['all_legal_ages'] == f.U
    assert docs['noiseless_period_v1']['typing']['all_output_possible_one_masks']

    saved = {}
    with (np.load(paths['noisy_commit_embedding_v2'].with_suffix('.npz'), allow_pickle=False) as commit,
          np.load(paths['wide_macrostep_v1'].with_suffix('.npz'), allow_pickle=False) as macro,
         np.load(paths['wide_next_periods_3_v2'].with_suffix('.npz'), allow_pickle=False) as later):
        selected = commit['selected_upper_positions']
        before = commit['full_committed_Info'].copy()
        healthy = commit['healthy_upper_successor'].copy()
        parent = cone.normalize(before.copy())
        assert_only_metadata_changed(before, parent)
        assert np.flatnonzero(np.any(before != parent, axis=1)).tolist() == [9566]
        assert np.count_nonzero(before != parent) == 16
        np.testing.assert_array_equal(before[selected[35:39]], macro['decoded_raw'][35:39])
        np.testing.assert_array_equal(parent[selected[35:39]], later['expected_normalized_info'][35:39])
        retained_positions = later['retained_positions'].copy()
        retained_values = later['retained_values'].copy()
        assert retained_positions.tolist() == [36*f.Q+a for a in (30960, 30961, 30962)]
        full_retained_positions = retained_positions+int(selected[0])*f.Q
        actual_words = macro['final_words']
        actual_signals = macro['final_signals']
        commit_index = next(i for i, row in enumerate(docs['wide_macrostep_v1']['checkpoints']) if row['time'] == f.U)
        committed_words = macro[f'checkpoint{commit_index}_words']
        committed_signals = macro[f'checkpoint{commit_index}_signals']
        np.testing.assert_array_equal(committed_words[35*f.Q:39*f.Q], commit['patch_logical_procedures'])
        np.testing.assert_array_equal(committed_signals[35*f.Q:39*f.Q], commit['patch_raw_Signals'])
        for col in range(35, 39):
            overlay = dict(zip((30960, 30961, 30962), map(int, retained_values))) if col == 36 else {}
            np.testing.assert_array_equal(actual_words[col*f.Q:(col+1)*f.Q], post_reset_words(before[selected[col]], overlay))
            sites = np.arange(col*f.Q, (col+1)*f.Q)
            actual_reset = cone.step(storage.raw_words(committed_words, committed_signals, 0,
                                                      np.arange(col*f.Q-7, (col+1)*f.Q+7)))[7:-7]
            np.testing.assert_array_equal(actual_reset, storage.raw_words(actual_words, actual_signals, 1, sites))

        # A complete full-ring E_loc comparison entry, with zero scratch. This
        # is a diagnostic preimage, not a replacement for the actual malformed
        # Info. The paired prefix physically couples only later.
        g = p.layout()
        bank = np.zeros((f.Q, g.memory_count+5), dtype=np.uint64)
        bank[:, np.array(g.info)] = parent
        full_signals = healthy[:, [f.COL['f2'], f.COL['f1']]].copy()
        entry = cone.BankImage(bank, full_signals)

        def raw_entry(sites):
            sites = np.asarray(sites, dtype=np.int64) % entry.size
            raw = entry.cells(sites)
            for pos, value in zip(full_retained_positions, retained_values):
                for delta in f.OFFSETS:
                    raw[sites == (int(pos)-delta) % entry.size, f.COL[f's{delta+2}_data']] = value
            return raw

        normalized_words = actual_words.copy()
        normalized_window = cone.normalize(macro['decoded_raw'].copy())
        for col in range(73):
            normalized_words[col*f.Q+np.array(g.info), storage.DATA] = normalized_window[col]
        reset_words_checked = 0
        for col in range(35, 39):
            global_col = int(selected[col])
            inputs = np.arange(global_col*f.Q-7, (global_col+1)*f.Q+7)
            expected = cone.step(raw_entry(inputs))[7:-7]
            actual = storage.raw_words(normalized_words, actual_signals, 1,
                                       np.arange(col*f.Q, (col+1)*f.Q))
            np.testing.assert_array_equal(expected, actual)
            reset_words_checked += expected.size
        # Everywhere outside the embedded patch, the known noiseless reset has
        # this same complete zero-scratch frame. The only paired differences
        # are 16 encoded metadata Data words, all in full colony9566.
        entry_bank_bytes = bank.nbytes
        saved['full_normalized_parent_raw'] = parent.copy()
        saved['full_healthy_parent_raw'] = healthy.copy()
        saved['full_entry_Signal_bits'] = full_signals
        saved['retained_full_positions'] = full_retained_positions
        saved['retained_values'] = retained_values
        del entry, bank, normalized_words, committed_words, actual_words

        # Diagnostic full-upper comparisons and comparison to already observed
        # decoded physical endpoints. No upper step drives a lower executor.
        rows = []
        frames = [(parent.copy(), healthy.copy())]
        for step in range(1, 4):
            parent, healthy = cone.step(parent), cone.step(healthy)
            frames.append((parent.copy(), healthy.copy()))
            safe = np.arange(7*step, 73-7*step)
            np.testing.assert_array_equal(parent[selected[safe]], later[f'period{step}_decoded'][safe])
            bad = np.flatnonzero(np.any(parent != healthy, axis=1))
            assert bad.tolist() == ([9566] if step == 1 else [])
            rows.append(dict(additional_lower_periods=step, local_physical_time=(step+1)*f.U,
                             full_upper_different_sites=bad.tolist(),
                             full_upper_different_raw_words=int(np.count_nonzero(parent != healthy)),
                             observed_window_complete_raw_matches=len(safe)*f.FIELDS))
            saved[f'period{step}_full_decoded'] = parent.copy()
            saved[f'period{step}_full_healthy'] = healthy.copy()

        # The full terminal formula uses only 15 parent records. Outside this
        # radius-seven support it cannot distinguish the period-one parents.
        positions = (9566+np.arange(-15, 16)) % f.Q
        a1, h1 = frames[1]
        actual_terminal = terminal.terminal(tuple(r.project(f.decode_cell(row)) for row in a1[positions]))
        healthy_terminal = terminal.terminal(tuple(r.project(f.decode_cell(row)) for row in h1[positions]))
        different = actual_terminal['committed_bank'] != healthy_terminal['committed_bank']
        active = np.flatnonzero(np.any(different, axis=1))
        assert active.tolist() == list(range(8, 23))
        assert int(np.count_nonzero(different)) == 660
        np.testing.assert_array_equal(actual_terminal['signals'], healthy_terminal['signals'])
        for index in active:
            col = int(positions[index])-int(selected[0])
            np.testing.assert_array_equal(actual_terminal['committed_bank'][index], later['period2_bank'][col])
        assert np.array_equal(frames[2][0], frames[2][1])
        saved['second_period_bank_difference_positions'] = positions[active]
        saved['second_period_bank_difference_counts'] = np.count_nonzero(different[active], axis=1)

    # Reuse the old independently scalar/native-checked full-upper trajectory
    # only after confirming that its complete initial and later states agree.
    with np.load(paths['upper_embedding_v1'].with_suffix('.npz'), allow_pickle=False) as previous:
        for step, (actual, reference) in enumerate(frames):
            np.testing.assert_array_equal(actual, previous[f'tick{step}_actual'])
            np.testing.assert_array_equal(reference, previous[f'tick{step}_healthy'])
    np.savez_compressed(artifact, **saved)
    result = dict(passed=True, conditional_full_ring_physical_repair_join=True,
                  full_lower_colonies=f.Q, physical_sites=f.Q*f.Q,
                  normalization_age=10487886, initial_metadata_word_differences=16,
                  full_E_comparison_bank_bytes=entry_bank_bytes,
                  native_raw_reset_words_per_comparison=reset_words_checked,
                  actual_reset_and_valid_entry_reset_checked=True,
                  existing_physical_prefix_audit_events=docs['wide_next_periods_audit_v1']['physical_normalization_trace_events'],
                  prefix_coupling_is_physical_not_host_normalization=True,
                  rows=rows, full_upper_rejoined_after_additional_periods=2,
                  full_terminal_bank_differences_after_second_period=660,
                  full_terminal_bank_difference_colonies_after_second_period=positions[active].tolist(),
                  full_banks_Signals_controllers_and_flags_rejoin_after_additional_periods=3,
                  retained_nonMEM_words=3, retained_full_positions=full_retained_positions.tolist(),
                  retained_values=retained_values.tolist(), complete_physical_erasure=False,
                  descriptor_sha256=f.self_description().digest(),
                  input_sha256={str(path): sha(path) for path in paths.values()},
                  source_sha256={str(path): sha(path) for path in (
                      Path(__file__), Path(f.__file__), Path(c.__file__), Path(r.__file__),
                      Path(p.__file__), Path(cone.__file__), Path(storage.__file__), Path(terminal.__file__))},
                  artifact_sha256=sha(artifact), seconds=time.perf_counter()-started,
                  host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  scope='Conditional full-ring composition from the physically faulted '
                        'commit through actual reset, metadata-prefix coupling and three '
                        'subsequent noiseless lower periods. Uses existing independently '
                        'audited window execution plus descriptor refinement/terminal '
                        'identities; no new literal full-ring GPU run. The three certified '
                        'nonMEM words persist. No fresh ongoing-noise, general amplification '
                        'or stochastic-threshold claim.')
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
