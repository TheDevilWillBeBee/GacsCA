"""Independent scalar sparse-procedure and integer-flag recovery replay.

Sparse omission is restricted to the checked active, reset/vote/commit-free,
mail-free interval. Head/control/mail propagation has radius one there; all
other procedure outputs are unchanged Data and zero controls. Every live
candidate executes the scalar core rule, including full raw controller fields.
"""
import argparse
import itertools
import json
import resource
import time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_core as c
from gacsca.fixed_rule import retimed_holder_active_snapshot as active
from gacsca.fixed_rule import retimed_holder_literal_cone as cone
from experiments.fixed_rule.run_retimed_holder_streamed_repair import sha

FIELDS = ('bank', 'active_rows', 'counts', 'flags', 'signals', 'age', 'time')
NAMES = tuple(n for n, _ in f.PROCEDURE)
DATA = NAMES.index('data')
OTHER = [i for i,n in enumerate(NAMES) if n != 'data']
MAIL = [i for i,n in enumerate(NAMES) if n.startswith(('lp_', 'rp_'))]


class SparseProcedures:
    def __init__(self, raw):
        self.words = np.array(raw[:, [f.COL['s2_'+n] for n in NAMES]], copy=True)
        self.base = raw.copy()
        for d in f.OFFSETS:
            for i, name in enumerate(NAMES):
                np.testing.assert_array_equal(raw[:, f.COL[f's{d+2}_{name}']], np.roll(self.words[:, i], -d))
        assert not np.any(self.words[:, MAIL])
        self.live = set(map(int, np.flatnonzero(np.any(self.words[:, OTHER], axis=1))))
        self.rom = cone.rom()
        self.evaluations = 0

    def step(self, age):
        assert c.active(age) and age not in (*f.RESET_AGES, *f.VOTE_AGES, f.U-1)
        candidates = sorted({(pos+d) % f.Q for pos in self.live for d in (-1, 0, 1)})
        cache = {}
        def cell(pos):
            pos %= f.Q
            if pos not in cache:
                values = dict(zip(c.STATIC, map(int, self.rom[pos])))
                values.update(zip(NAMES, map(int, self.words[pos])))
                cache[pos] = c.Cell(address=pos, age=age, **values)
            return cache[pos]
        outputs = []
        for pos in candidates:
            result = c._clock_step(tuple(cell(pos+d) for d in range(-5, 6)))
            row = tuple(getattr(result, n) for n in NAMES)
            assert not any(row[i] for i in MAIL), 'mail-free sparse replay domain ended'
            outputs.append(row)
        self.live = set()
        for pos, row in zip(candidates, outputs):
            self.words[pos] = row
            if any(row[i] for i in OTHER):
                self.live.add(pos)
        self.evaluations += len(candidates)

    def render(self, age, flag1):
        result = self.base.copy()
        result[:, f.COL['age']] = age
        result[:, f.COL['f1']] = np.unpackbits(np.frombuffer(flag1.to_bytes(f.Q//8, 'little'), dtype=np.uint8), bitorder='little')
        result[:, f.COL['f2']] = 0
        for d in f.OFFSETS:
            for i, name in enumerate(NAMES):
                result[:, f.COL[f's{d+2}_{name}']] = np.roll(self.words[:, i], -d)
        return result


def flag_step(value):
    # Right-neighbor flags outside this single colony are excluded. Flag2 is
    # initially zero and stays zero without forcing, for every Flag1 pattern.
    neighbors = [value >> d for d in range(1, 6)]
    two = three = 0
    for i,j in itertools.combinations(range(5), 2):
        two |= neighbors[i] & neighbors[j]
    for i,j,k in itertools.combinations(range(5), 3):
        three |= neighbors[i] & neighbors[j] & neighbors[k]
    return three | (value & two)


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
    assert receipt['completed'] and receipt['error'] is None
    assert sha(path.with_suffix('.npz')) == receipt['artifact_sha256']
    assert sha(receipt['source_receipt']) == receipt['source_receipt_sha256']
    for source, digest in receipt['source_sha256'].items():
        assert sha(source) == digest, source
    targets = {row['tick']:row for row in receipt['observations']}
    dense_outputs = 0
    clear_tick = None
    with np.load(path.with_suffix('.npz'), allow_pickle=False) as saved:
        initial = {k:saved['initial_'+k] for k in FIELDS}
        healthy_raw = active.render(initial)
        actual_raw = healthy_raw.copy()
        actual_raw[saved['initial_positions']] = saved['initial_values']
        np.testing.assert_array_equal(actual_raw, saved['before_attach'])
        np.testing.assert_array_equal(actual_raw, saved['after_attach'])
        assert receipt['attachment']['physical_transitions'] == 0
        assert receipt['attachment']['complete_raw_words_verified'] == f.Q*f.FIELDS
        assert not np.any(actual_raw[:, [f.COL['f2'], *(f.COL[f'w{k}_{n}'] for k in range(5) for n in ('wf1', 'wf2'))]])
        age = int(initial['age'])
        assert f.WF_END+f.Q < age and age+receipt['elapsed_physical_ticks'] < min(a for a in (*f.RESET_AGES, *f.VOTE_AGES, f.U) if a > age)
        np.testing.assert_array_equal(actual_raw[:, f.COL['address']], np.arange(f.Q))
        np.testing.assert_array_equal(actual_raw[:, f.COL['signal']], healthy_raw[:, f.COL['signal']])
        # Canonical fixed metadata, uniform age and stationary coherent Signals.
        np.testing.assert_array_equal(actual_raw, cone.normalize(actual_raw.copy()))
        assert np.all(actual_raw[:, f.COL['age']] == age)
        actual, healthy = SparseProcedures(actual_raw), SparseProcedures(healthy_raw)
        flag1 = int.from_bytes(np.packbits(actual_raw[:, f.COL['f1']].astype(np.uint8), bitorder='little').tobytes(), 'little')
        dense_actual, dense_healthy = actual_raw, healthy_raw
        checks = []
        for tick in range(receipt['elapsed_physical_ticks']+1):
            if tick:
                actual.step(age+tick-1)
                healthy.step(age+tick-1)
                flag1 = flag_step(flag1)
                if not flag1 and clear_tick is None:
                    clear_tick = tick
                if tick <= 8:
                    dense_actual, dense_healthy = cone.step(dense_actual), cone.step(dense_healthy)
                    dense_outputs += 2*f.Q
                    np.testing.assert_array_equal(actual.render(age+tick, flag1), dense_actual)
                    np.testing.assert_array_equal(healthy.render(age+tick, 0), dense_healthy)
            if tick in targets:
                observed = targets[tick]
                expected_actual, expected_healthy = actual.render(age+tick, flag1), healthy.render(age+tick, 0)
                prefix = f'observe{tick}'
                snapshot = {k:saved[prefix+'_healthy_'+k] for k in FIELDS}
                np.testing.assert_array_equal(active.render(snapshot), expected_healthy)
                reconstructed = expected_healthy.copy()
                reconstructed[saved[prefix+'_positions']] = saved[prefix+'_values']
                np.testing.assert_array_equal(reconstructed, expected_actual)
                diff = expected_actual != expected_healthy
                positions = np.flatnonzero(np.any(diff, axis=1))
                np.testing.assert_array_equal(positions, saved[prefix+'_positions'])
                assert len(positions) == observed['discrepant_sites']
                assert np.count_nonzero(diff) == observed['discrepant_words']
                assert observed['actual_flag1_sites'] == flag1.bit_count() and observed['actual_flag2_sites'] == 0
                check = dict(tick=tick, discrepant_sites=len(positions), raw_words=int(np.count_nonzero(diff)), flag1_sites=flag1.bit_count())
                checks.append(check)
                print(json.dumps(dict(check, seconds=time.perf_counter()-started)), flush=True)
    sources = (Path(__file__), Path(c.__file__), Path(f.__file__), Path(cone.__file__), Path(active.__file__))
    result = dict(passed=True, all_quiet_physical_ticks_replayed=receipt['elapsed_physical_ticks'], scalar_core_candidate_evaluations=actual.evaluations+healthy.evaluations, complete_native_prefix_output_states=dense_outputs, complete_native_prefix_output_words=dense_outputs*f.FIELDS, independently_verified_observations=checks, independently_computed_first_flag_clear_tick=clear_tick, all_mail_outputs_zero=True, source_receipt_sha256=sha(path), artifact_sha256=receipt['artifact_sha256'], source_sha256={str(p):sha(p) for p in sources}, seconds=time.perf_counter()-started, host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, scope='Every quiet tick independently replays scalar logical procedures and exact integer Flag1 recurrence in the checked canonical/coherent/mail-free event-free domain. Complete raw-state equality at all saved observations. First eight ticks additionally replay both full physical lattices with native G. No general arbitrary-state sparse-replay claim or decoded macrostep assertion.')
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'independently_verified_observations'}, indent=2), flush=True)


if __name__ == '__main__':
    main()
