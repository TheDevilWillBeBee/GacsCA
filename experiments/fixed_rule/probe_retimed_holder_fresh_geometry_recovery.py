"""Bounded literal continuation of the saved nine-mark fresh-fault experiment."""
import argparse
import json
from pathlib import Path
import resource
import time
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f
from gacsca.fixed_rule import retimed_holder_literal_cone as cone
from experiments.fixed_rule.audit_retimed_holder_prefix_embedding import sha


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    parser.add_argument('--ticks', type=int, default=128)
    args = parser.parse_args()
    if not 8 <= args.ticks <= 512:
        raise ValueError('bounded literal duration required')
    out = Path(args.output)
    artifact = out.with_suffix('.npz')
    if out.exists() or artifact.exists():
        raise FileExistsError(out)
    started = time.perf_counter()
    root = Path('figs/fixed_rule')
    oldpath = root/'retimed_holder_wide_next_periods_3_v2.json'
    path = root/'retimed_holder_residual_reactivation_audit_v3.json'
    for receipt in (oldpath, path):
        doc = json.loads(receipt.read_text())
        assert doc.get('passed', doc.get('completed')) is True
        assert sha(receipt.with_suffix('.npz')) == doc['artifact_sha256']
    with np.load(oldpath.with_suffix('.npz'), allow_pickle=False) as old:
        anchor = int(old['retained_positions'][0])
        radius = 14*args.ticks+5
        positions = np.arange(anchor-radius, anchor+radius+1)
        reference = cone.BankImage(old['period3_bank'], old['period3_signals']).cells(positions)
        actual = reference.copy()
        for pos, value in zip(old['retained_positions'], old['retained_values']):
            for d in f.OFFSETS:
                actual[positions+d == pos, f.COL[f's{d+2}_data']] = value
    with np.load(path.with_suffix('.npz'), allow_pickle=False) as previous:
        marks = [(int(t), int(pos), row.copy()) for t,pos,row in zip(previous['fault_times'], previous['fault_positions'], previous['fault_replacements'])]
        expected = {key:previous[key] for key in previous.files if key.startswith('tick')}
    saved, observations = {}, []
    target_ticks = {1, 2, 3, 4, 5, 8, 16, 32, 64, 128, 256, 512, args.ticks}
    evaluated = 0
    for tick in range(args.ticks):
        for t,pos,row in marks:
            if t == tick:
                actual[pos-positions[0]] = row
        actual = cone.step(actual)[7:-7].copy()
        reference = cone.step(reference)[7:-7].copy()
        positions = positions[7:-7]
        evaluated += actual.size+reference.size
        if tick < 5:
            idx = expected[f'tick{tick+1}_positions']-positions[0]
            np.testing.assert_array_equal(actual[idx], expected[f'tick{tick+1}_actual'])
            np.testing.assert_array_equal(reference[idx], expected[f'tick{tick+1}_fault_free'])
        diff = actual != reference
        indices = np.flatnonzero(np.any(diff, axis=1))
        assert np.all(np.abs(positions[indices]-anchor) <= 5+7*(tick+1))
        if tick+1 in target_ticks or not len(indices):
            counts = np.count_nonzero(diff, axis=0)
            row = dict(tick=tick+1, different_sites=len(indices), different_raw_words=int(counts.sum()),
                       support_offsets=(positions[indices]-anchor).tolist(),
                       fields={name:int(counts[j]) for j,(name,_) in enumerate(f.SCHEMA) if counts[j]},
                       seconds=time.perf_counter()-started)
            observations.append(row)
            print(json.dumps({k:v for k,v in row.items() if k != 'support_offsets'}), flush=True)
        if not len(indices):
            break
    saved.update(final_actual=actual, final_reference=reference, final_positions=positions)
    np.savez_compressed(artifact, **saved)
    result = dict(passed=True, elapsed_ticks=tick+1, requested_ticks=args.ticks,
                  fully_rejoined=not len(indices), observations=observations,
                  retained_native_output_words=evaluated, exact_saved_five_tick_prefix_matched=True,
                  descriptor_sha256=f.self_description().digest(),
                  input_sha256={str(x):sha(x) for x in (oldpath,path)},
                  source_sha256={str(x):sha(x) for x in (Path(__file__),Path(f.__file__),Path(cone.__file__))},
                  artifact_sha256=sha(artifact), seconds=time.perf_counter()-started,
                  host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  scope='Bounded literal full-rule continuation of actual saved replacements '
                        'and residuals versus the fault-free trajectory. Full-ring interpretation '
                        'uses the previous conditional endpoint relation and ordinary locality; '
                        'new suffix has not yet been independently scalar audited.')
    with out.open('x') as stream:
        stream.write(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'observations'},indent=2),flush=True)


if __name__ == '__main__':
    main()
