"""Check entry matching for the conditional noiseless-prefix embedding.

No physical state is evolved or replaced. This joins the spatial-dependence
argument to the complete inherited banks actually used by the wider experiment.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time
import numpy as np

from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_program as p
from gacsca.fixed_rule import retimed_holder_literal_cone as cone
from gacsca.fixed_rule import retimed_holder_quotient as q, retimed_holder_resident_period as period


def sha(path):
    # Full inherited banks are multi-gigabyte files; do not read them at once.
    result = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            result.update(block)
    return result.hexdigest()


def validate_entry(entry):
    n = len(entry['bank'])
    assert entry['bank'].dtype == np.uint64
    assert entry['bank'].shape == (n, p.layout().memory_count+5)
    shapes = dict(age=(), time=(), counts=(n,), active_rows=(n, period.SLOTS, len(q.SCHEMA)),
                  flags=(n*f.Q//64, 2), signals=(n, 2))
    for key, shape in shapes.items():
        value = np.asarray(entry[key])
        assert value.shape == shape and value.dtype == np.uint64, ('complete typed entry required', key)
        assert not np.any(value), ('entry must be zero', key)


def safe_raw_colonies(selected, whole_size, radius=8):
    selected = np.asarray(selected, dtype=np.int64)
    assert np.array_equal(selected, (selected[0]+np.arange(len(selected))) % whole_size)
    return list(range(radius, len(selected)-radius))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--certificate', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    out = Path(args.output)
    if out.exists():
        raise FileExistsError(out)
    started = time.perf_counter()
    cert_path = Path(args.certificate)
    certificate = json.loads(cert_path.read_text())
    assert certificate['passed'] and certificate['initial_Signals_zero_required']
    assert certificate['complete_raw_colony_owner_offsets'] == list(range(-8, 9))
    assert certificate['descriptor_sha256'] == f.self_description().digest()
    for source, expected in {**certificate['source_sha256'], **certificate['input_sha256']}.items():
        assert sha(source) == expected, source
    burst_path = Path('figs/fixed_rule/retimed_holder_wide_burst_v1.json')
    burst = json.loads(burst_path.read_text())
    assert burst['completed'] and burst['error'] is None
    assert sha(burst_path.with_suffix('.npz')) == burst['artifact_sha256']
    base_path = Path(burst['complete_nested_checkpoint'])
    base = json.loads(base_path.read_text())
    assert sha(base_path) == burst['complete_nested_checkpoint_sha256']
    assert base['passed'] and base['case'] == 'checkpoint'
    bank_path = Path(burst['inherited_bank_source'])
    assert sha(bank_path) == burst['inherited_bank_sha256'] == base['bank_sha256'][str(bank_path)]
    assert sha(base['small_artifact']) == base['small_sha256']
    bank = np.load(bank_path, mmap_mode='r', allow_pickle=False)
    assert bank.shape == (f.Q, p.layout().memory_count+5)
    with np.load(base['small_artifact'], allow_pickle=False) as z:
        full_signals = z['step1_signals']
        assert full_signals.shape == (f.Q, 2) and not np.any(full_signals)
    with np.load(burst_path.with_suffix('.npz'), allow_pickle=False) as z:
        names = ('bank', 'active_rows', 'counts', 'flags', 'signals', 'age', 'time')
        entry = {name: z['entry_'+name] for name in names}
        validate_entry(entry)
        selected = z['selected_upper_positions']
        safe = safe_raw_colonies(selected, f.Q)
        np.testing.assert_array_equal(entry['bank'], bank[selected])
        np.testing.assert_array_equal(z['inherited_bank'], entry['bank'])
        np.testing.assert_array_equal(entry['signals'], full_signals[selected])
        upper = z['upper_context']
        assert upper.shape == (f.Q, f.FIELDS)
        for index, (_, width) in enumerate(f.SCHEMA):
            if width < 64:
                assert np.all(upper[:, index] < np.uint64(1 << width))
        normalized = upper.copy()
        cone.normalize(normalized)
        np.testing.assert_array_equal(normalized, upper)
        np.testing.assert_array_equal(bank[:, p.layout().info], upper)
        age = int(z['checkpoint_age'])
        assert certificate['late_interval'][0] <= age <= certificate['late_interval'][1]
        assert age == burst['burst_initial_age']
        assert set(range(34, 40)) <= set(safe)
        words = entry['bank'].size
    result = dict(passed=True, matched_complete_initial_bank_words=int(words),
                  full_parent_raw_words_typed_and_normalized=int(upper.size),
                  matched_entry_colonies=len(selected), complete_raw_safe_colonies=safe,
                  complete_raw_safe_upper_positions=selected[safe].tolist(),
                  burst_initial_age=age, enclosing_candidate_cuts=[35*f.Q, 39*f.Q],
                  all_initial_Signals_zero=True,
                  descriptor_sha256=f.self_description().digest(),
                  input_sha256={str(path): sha(path) for path in (cert_path, burst_path, base_path)},
                  external_bank_sha256={str(bank_path): base['bank_sha256'][str(bank_path)]},
                  source_sha256={str(path): sha(path) for path in (Path(__file__), Path(f.__file__), Path(p.__file__), Path(cone.__file__))},
                  seconds=time.perf_counter()-started,
                  host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  conclusion='For descriptor-semantics noiseless prefixes from these matching '
                             'encoded entries, all raw states in the listed 57 central colonies '
                             'agree at the burst time, by the conditional dependence argument.',
                  limitation='Entry matching plus a proof composition, not an independent '
                             'literal replay of the saved GPU prefix. The all-time noisy '
                             'boundary/collar relation after the burst remains open.')
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
