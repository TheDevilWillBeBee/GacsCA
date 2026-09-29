"""Finite-time consequence of the conditional complete prefix embedding.

Uses the actual fixed radius, complete-state intervals and shared fault marks.
No colony-local shortcut or assumption about error propagation speed is used.
"""
import argparse
import json
from pathlib import Path
import resource
import time
import numpy as np

from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_core as c
from gacsca.fixed_rule import retimed_holder_program as p
from gacsca.fixed_rule import retimed_holder_global_events as events
from experiments.fixed_rule.run_retimed_holder_streamed_repair import sha


def interior(lo, hi, ticks, *, radius=7, block=32768):
    assert 0 <= lo <= hi and ticks >= 0 and radius >= 0 and block > 0
    left, right = lo+radius*ticks, hi-radius*ticks
    if left >= right:
        return dict(physical_interval=[], complete_colonies=[])
    return dict(physical_interval=[left, right],
                complete_colonies=list(range((left+block-1)//block, right//block)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    out = Path(parser.parse_args().output)
    if out.exists():
        raise FileExistsError(out)
    start = time.perf_counter()
    root = Path('figs/fixed_rule')
    names = ('prefix_embedding_v3', 'wide_burst_v1', 'wide_recovery_v1',
             'wide_macrostep_v1', 'wide_burst_audit_v1',
             'wide_recovery_audit_v2', 'wide_macrostep_audit_v1', 'colony_cut_v2')
    paths = {name: root/('retimed_holder_'+name+'.json') for name in names}
    docs = {name: json.loads(path.read_text()) for name, path in paths.items()}
    for name, doc in docs.items():
        assert doc.get('passed', doc.get('completed')) is True, name
        for source, expected in doc.get('source_sha256', {}).items():
            assert sha(source) == expected, source
        if name in ('wide_burst_v1', 'wide_recovery_v1', 'wide_macrostep_v1'):
            assert sha(paths[name].with_suffix('.npz')) == doc['artifact_sha256'], name
    for audit, source in [('wide_burst_audit_v1', 'wide_burst_v1'),
                          ('wide_recovery_audit_v2', 'wide_recovery_v1'),
                          ('wide_macrostep_audit_v1', 'wide_macrostep_v1')]:
        assert docs[audit]['source_receipt_sha256'] == sha(paths[source])
        assert docs[audit]['artifact_sha256'] == docs[source]['artifact_sha256']
    prefix, burst = docs['prefix_embedding_v3'], docs['wide_burst_v1']
    recovery, macro = docs['wide_recovery_v1'], docs['wide_macrostep_v1']
    assert recovery['source_receipt_sha256'] == sha(paths['wide_burst_v1'])
    assert macro['source_receipt_sha256'] == sha(paths['wide_recovery_v1'])
    radius = max(abs(x) for x in f.NEIGHBORHOOD)
    assert radius == 7 and len(f.NEIGHBORHOOD) == 15
    # The complete descriptor has only the declared local inputs. The cone
    # includes every field even when geometry/ROM/controller state is corrupt.
    desc = f.self_description()
    assert desc.inputs == len(f.NEIGHBORHOOD)*f.FIELDS and len(desc.outputs) == f.FIELDS
    safe = prefix['complete_raw_safe_colonies']
    assert safe == list(range(8, 65))
    lo, hi = safe[0]*f.Q, (safe[-1]+1)*f.Q
    initial_age = burst['burst_initial_age']
    assert initial_age == prefix['burst_initial_age']
    with np.load(paths['wide_burst_v1'].with_suffix('.npz'), allow_pickle=False) as z:
        schedule = z['schedule']
        assert len(schedule) == 8404
        assert np.all((1 <= schedule[:, 0]) & (schedule[:, 0] <= 32))
        assert np.all((0 <= schedule[:, 1]) & (schedule[:, 1] < f.Q))
        assert z['replacements'].shape[0] == len(schedule)
    rows = []
    times = [('burst_end', burst['rows'][-1]['time']),
             ('recovery_end', macro['initial_time'])]
    times += [(f'macro_checkpoint_{i}', row['time']) for i, row in enumerate(macro['checkpoints'])]
    for name, physical_time in times:
        elapsed = physical_time-initial_age
        row = dict(name=name, physical_time=physical_time, elapsed_ticks=elapsed,
                   **interior(lo, hi, elapsed, radius=radius, block=f.Q))
        rows.append(row)
    assert rows[3]['elapsed_ticks'] == 116418
    assert rows[3]['complete_colonies'] == list(range(33, 40))
    assert rows[-1]['physical_interval'] == []
    # Check the cut's hypotheses at this saved checkpoint, without promoting
    # a same-time check to an all-time invariant.
    with np.load(paths['wide_macrostep_v1'].with_suffix('.npz'), allow_pickle=False) as z:
        words, signals = z['checkpoint1_words'], z['checkpoint1_signals']
        assert words.shape == (73*f.Q, len(events.NAMES))
        assert signals.shape == (73*f.Q,)
        nonzero_Signal_colonies = np.unique(np.flatnonzero(signals)//f.Q).tolist()
        assert not np.any(signals[33*f.Q:40*f.Q])
        assert nonzero_Signal_colonies == [0, 1, 2, 70, 71, 72]
        # The descriptor cut only reads a bounded collar at each boundary.
        # Its raw output sites -11..10 plus radius seven need -18..17.
        for boundary in (35*f.Q, 39*f.Q):
            assert rows[3]['physical_interval'][0] <= boundary-18
            assert boundary+18 <= rows[3]['physical_interval'][1]
        control = [events.COL[name] for name in ('head', *c.CONTROL)]
        for col in range(73):
            block = words[col*f.Q:(col+1)*f.Q]
            assert not np.any(block[:, events.MAIL])
            assert not np.any(block[len(p.base_rom()):, control])
        heads = np.flatnonzero(words[:, events.COL['head']]).tolist()
        assert heads == macro['checkpoints'][1]['heads']
    result = dict(passed=True, radius=radius, complete_fields_per_state=f.FIELDS,
                  initial_matching_physical_interval=[lo, hi],
                  shared_fault_marks=len(schedule), faulted_window_colony=burst['center_colony'],
                  corresponding_full_ring_colony=burst['selected_upper_positions'][burst['center_colony']],
                  physical_time_offset=burst['entry_physical_time'],
                  translation_in_physical_sites=burst['selected_upper_positions'][0]*f.Q,
                  checkpoints=rows, descriptor_sha256=desc.digest(),
                  checkpoint_1_candidate_cut_local_hypotheses_verified=True,
                  checkpoint_1_controllers=len(heads),
                  checkpoint_1_global_mail_zero=True,
                  checkpoint_1_central_Signals_zero=True,
                  checkpoint_1_nonzero_Signal_colonies=nonzero_Signal_colonies,
                  candidate_cut_coordinates=[35*f.Q, 39*f.Q],
                  cut_hypotheses_are_not_claimed_invariant=True,
                  input_sha256={str(path): sha(path) for path in paths.values()},
                  source_sha256={str(path): sha(path) for path in (Path(__file__), Path(f.__file__), Path(c.__file__), Path(p.__file__), Path(events.__file__))},
                  seconds=time.perf_counter()-start,
                  host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  conclusion='Conditional on the prefix embedding and physical executor '
                             'refinement, complete raw noisy states match the full lower '
                             'ring in each listed interval. Both executions use identical '
                             'translated replacement marks and no other faults.',
                  limitation='The radius-seven cone is empty before commit. This does '
                             'not embed the final faulty commit or later repair, and '
                             'does not prove the full-ring exterior stays noiseless.')
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
