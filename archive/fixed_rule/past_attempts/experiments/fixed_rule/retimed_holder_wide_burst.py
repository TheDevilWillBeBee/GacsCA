"""Actual physical burst in a 73-colony inherited-bank window.

Derived from the frozen contextual burst driver, with a larger initial window.
The physical rule, hardware alphabet, evaluator and fault schedule are unchanged.
The larger upper halo does not by itself prove lower physical boundary transfer.
"""
import argparse
import json
import resource
import time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_projected as r
from gacsca.fixed_rule import retimed_holder_program as p, retimed_holder_quotient as q
from gacsca.fixed_rule import retimed_holder_resident_general as general
from gacsca.fixed_rule import retimed_holder_resident_period as period
from gacsca.fixed_rule import retimed_holder_general_faults as faults
from gacsca.fixed_rule import retimed_holder_cuda_general_snapshot as snapshots
from gacsca.fixed_rule import retimed_holder_noise_schedule as noise
from gacsca.fixed_rule import retimed_holder_live_window as live
from experiments.fixed_rule.retimed_holder_cuda_encoded_repair import forbidden, raw
from experiments.fixed_rule.run_retimed_holder_streamed_repair import sha

FIELDS = ('bank','active_rows','counts','flags','signals','age','time')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    out = Path(args.output)
    artifact = out.with_suffix('.npz')
    if out.exists() or artifact.exists():
        raise FileExistsError(out)
    started = time.perf_counter()
    fixture_path = Path('figs/fixed_rule/retimed_holder_active_evaluator_faults_v1.json')
    fixture = json.loads(fixture_path.read_text())
    assert fixture['passed'] and sha(fixture_path.with_suffix('.npz')) == fixture['artifact_sha256']
    with np.load(fixture_path.with_suffix('.npz'), allow_pickle=False) as z:
        upper = z['checkpoint_raw'].copy()
    upper_head = np.flatnonzero(upper[:, f.COL['s2_head']])
    assert len(upper_head) == 1
    upper_head = int(upper_head[0])
    center, colonies = 36, 73
    selected = (upper_head+np.arange(-36, 37)) % f.Q
    parents = tuple(r.project(f.decode_cell(upper[i])) for i in selected)
    base_path = Path('figs/fixed_rule/retimed_holder_timed_depth2_checkpoint_v1.json')
    base = json.loads(base_path.read_text())
    assert base['passed'] and base['case'] == 'checkpoint'
    bank_path = Path(base['bank_paths'][0])
    assert sha(bank_path) == base['bank_sha256'][str(bank_path)]
    bank = np.load(bank_path, mmap_mode='r', allow_pickle=False)
    inherited = np.array(bank[selected], copy=True)
    del bank
    g = p.layout()
    np.testing.assert_array_equal(inherited[:, g.info], upper[selected])
    assert sha(base['small_artifact']) == base['small_sha256']
    with np.load(base['small_artifact'], allow_pickle=False) as z:
        signals = z['step1_signals'][selected].copy()
    assert not np.any(signals)
    sampled = noise.sample(sites=f.Q, ticks=32, expected_marks=8192, seed=2026092713)
    schedule, replacements = sampled.pop('schedule'), sampled.pop('replacements')
    saved = dict(upper_context=upper, selected_upper_positions=selected, inherited_bank=inherited, inherited_signals=signals, schedule=schedule, replacements=replacements)
    def save_state(prefix, state):
        for key,value in state.items():
            saved[prefix+'_'+key] = value
    rows = []
    completed, error = False, None
    with general.World(parents, device_budget=32*1024**2) as background:
        for col in range(colonies):
            block = np.ascontiguousarray(inherited[col])
            if background._core.lib.rp_bank(background._core.handle, col, period.pointer(block)):
                raise RuntimeError('complete inherited bank upload failed')
        entry = snapshots.snapshot(background)
        np.testing.assert_array_equal(entry['bank'], inherited)
        np.testing.assert_array_equal(entry['signals'], signals)
        assert not np.any(entry['counts']) and not np.any(entry['flags'])
        save_state('entry', entry)
        with forbidden():
            prefix_metrics = background.advance(fixture['age'], extra_device_budget=32*1024**2)
        checkpoint = snapshots.snapshot(background)
        save_state('checkpoint', checkpoint)
        for col in range(center-8, center+9):
            intended = upper[(int(selected[col])+np.arange(-7, 8)) % f.Q].reshape(-1)
            np.testing.assert_array_equal(checkpoint['bank'][col, g.votes], intended)
        # Actual readback confirms complete live physical fields in the window.
        probes = sorted({center*f.Q+9565+d for d in range(-7, 8)} | {center*f.Q-2, center*f.Q-1, center*f.Q, (center+1)*f.Q})
        np.testing.assert_array_equal(live.Window(checkpoint).cells(probes), raw(background.physical_cells(probes)))
        print(json.dumps(dict(stage='actual contextual lower NAND checkpoint', colonies=colonies, upper_head=upper_head, lower_age=background.age, seconds=time.perf_counter()-started)), flush=True)
        with faults.World(background) as actual:
            peak = background.device_bytes+actual.device_bytes+32*1024**2
            assert peak < 64*1024**2
            try:
                for tick in range(1, 35):
                    with forbidden():
                        metric = actual.step()
                    state = snapshots.snapshot(background)
                    save_state(f'tick{tick}', state)
                    before = list(actual.positions)
                    indices = np.flatnonzero(schedule[:,0] == tick).tolist()
                    changes = {center*f.Q+int(schedule[i,1]):r.decode_cell(replacements[i]) for i in indices}
                    if changes:
                        actual.inject(changes)
                    positions = list(actual.positions)
                    chunks = [raw(actual.read(positions[i:i+256])) for i in range(0,len(positions),256)]
                    values = np.concatenate(chunks) if chunks else np.empty((0,f.FIELDS),dtype=np.uint64)
                    saved[f'tick{tick}_positions'] = np.array(positions,dtype=np.uint64)
                    saved[f'tick{tick}_values'] = values
                    # No injected mark is removed because it is inconvenient;
                    # all output support is recorded, including adjacent colonies.
                    row = dict(tick=tick,time=actual.time,absolute_physical_time=base['period_results'][0]['physical_time']+actual.time,mark_indices=indices,pre_noise_exception_sites=len(before),post_noise_exception_sites=len(positions),affected_lower_colonies=sorted({pos//f.Q for pos in positions}),literal_metrics=metric)
                    rows.append(row)
                    if tick % 8 == 0 or tick > 32:
                        print(json.dumps(row),flush=True)
                completed = True
            except Exception as exc:
                error = f'{type(exc).__name__}: {exc}'
            save_state('final_background', snapshots.snapshot(background))
            positions = list(actual.positions)
            chunks = [raw(actual.read(positions[i:i+256])) for i in range(0,len(positions),256)]
            saved['final_positions'] = np.array(positions,dtype=np.uint64)
            saved['final_values'] = np.concatenate(chunks) if chunks else np.empty((0,f.FIELDS),dtype=np.uint64)
    np.savez_compressed(artifact,**saved)
    sources = (Path(__file__),Path(live.__file__),Path(noise.__file__),Path(general.__file__),Path(faults.__file__),Path(f.__file__))
    result = dict(completed=completed,error=error,colonies=colonies,center_colony=center,selected_upper_positions=selected.tolist(),upper_head=upper_head,entry_physical_time=base['period_results'][0]['physical_time'],burst_initial_age=fixture['age'],noise=sampled,rows=rows,reference_prefix_metrics=prefix_metrics,fixture=str(fixture_path),fixture_sha256=sha(fixture_path),complete_nested_checkpoint=str(base_path),complete_nested_checkpoint_sha256=sha(base_path),inherited_bank_source=str(bank_path),inherited_bank_sha256=base['bank_sha256'][str(bank_path)],artifact_sha256=sha(artifact),source_sha256={str(x):sha(x) for x in sources},descriptor_sha256=f.self_description().digest(),explicit_GPU_peak_bound_bytes=peak,seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,scope='Actual lower physical burst in a 73-colony inherited-bank window encoding the actual upper NAND checkpoint. Complete seven-parent gathered inputs verified for all central 17 colonies. Window edges are not claimed equivalent to the whole Q-colony nested state; no receiving-layer repair or full noisy macrostep result yet.')
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('rows','reference_prefix_metrics')},indent=2),flush=True)
    if not completed:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
