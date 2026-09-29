"""Literal consecutive physical faults, including an interacting negative control.

Uses shrinking raw-state windows of the unchanged native physical rule. No
simulated transition, healthy replacement, or event shortcut is used here.
"""
import argparse
import json
import random
import resource
import time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_projected as r
from gacsca.fixed_rule import retimed_holder_literal_cone as cone
from gacsca.fixed_rule import retimed_holder_spacetime_domain as domain
from gacsca.fixed_rule import retimed_holder_program as p
from experiments.fixed_rule.run_retimed_holder_streamed_repair import sha

PROCEDURE = {f's{k}_{name}' for k in range(5) for name, _ in f.PROCEDURE}


def healthy_context(raw, left):
    assert np.array_equal(raw[:, f.COL['address']], np.arange(left, left+len(raw)) % f.Q)
    assert len(np.unique(raw[:, f.COL['age']])) == 1 and int(raw[0, f.COL['age']]) < f.U
    assert not np.any(raw[:, [f.COL[n] for n in ('f1', 'f2', *(f'w{k}_{n}' for k in range(5) for n in ('wf1', 'wf2')))]])
    assert np.array_equal(raw, cone.normalize(raw.copy()))
    for offset in f.OFFSETS:
        for name, _ in f.PROCEDURE:
            assert np.array_equal(raw[2:-2, f.COL[f's{offset+2}_{name}']], raw[2+offset:len(raw)-2+offset, f.COL[f's2_{name}']])
        assert np.array_equal((raw[2:-2, f.COL['signal']] >> np.uint64(offset+2)) & np.uint64(1), (raw[2+offset:len(raw)-2+offset, f.COL['signal']] >> np.uint64(2)) & np.uint64(1))


def differences(actual, healthy, left):
    diff = actual != healthy
    sites = (np.flatnonzero(np.any(diff, axis=1))+left).tolist()
    fields = [name for col, (name, _) in enumerate(f.SCHEMA) if np.any(diff[:, col])]
    return dict(sites=sites, fields=fields, raw_words=int(np.count_nonzero(diff)))


def run_case(label, initial, events, steps, saved, expect_eligible):
    positions = [pos for event in events.values() for pos in event]
    left, right = min(positions)-14*steps, max(positions)+14*steps+1
    assert right-left < f.Q and right-left <= 1024
    healthy = np.ascontiguousarray(initial(np.arange(left, right)))
    actual = healthy.copy()
    saved[label+'_initial'] = healthy.copy()
    initial_left = left
    previous = set()
    rows = []
    for tick in range(steps):
        healthy_context(healthy, left)
        prior = differences(actual, healthy, left)
        changes = events.get(tick, {})
        valid = domain.eligible(previous, changes, size=f.Q)
        if expect_eligible:
            assert valid and set(prior['sites']) <= previous and set(prior['fields']) <= PROCEDURE
        prefix = f'{label}_step{tick}'
        saved[prefix+'_positions'] = np.array(sorted(changes), dtype=np.int64)
        saved[prefix+'_replacements'] = np.array([changes[pos] for pos in sorted(changes)], dtype=np.uint64).reshape(-1, f.FIELDS)
        for pos, value in changes.items():
            actual[pos-left] = value
        saved[prefix+'_injected'] = actual.copy()
        actual = cone.step(actual)[7:-7].copy()
        healthy = cone.step(healthy)[7:-7].copy()
        left += 7
        after = differences(actual, healthy, left)
        confined = set(after['sites']) <= set(changes) and set(after['fields']) <= PROCEDURE
        if expect_eligible:
            assert confined
        saved[prefix+'_actual'] = actual.copy()
        saved[prefix+'_healthy'] = healthy.copy()
        rows.append(dict(tick=tick, left=left, current_fault_sites=sorted(changes), previous_fault_sites=sorted(previous), eligible=valid, prior=prior, after=after, output_confined_to_current_procedures=confined))
        previous = set(changes)
    rejoined = np.array_equal(actual, healthy)
    if expect_eligible:
        assert rejoined and any(row['prior']['raw_words'] for row in rows[1:len(events)])
    else:
        assert not rejoined and not rows[1]['eligible']
    return dict(label=label, initial_left=initial_left, steps=rows, fully_rejoined=rejoined, expect_eligible=expect_eligible, total_faults=len(positions))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    out = Path(args.output)
    artifact = out.with_suffix('.npz')
    if out.exists() or artifact.exists():
        raise FileExistsError(out)
    started = time.perf_counter()
    checkpoint = Path('figs/fixed_rule/retimed_holder_active_evaluator_faults_v1.npz')
    receipt = json.loads(checkpoint.with_suffix('.json').read_text())
    assert receipt['passed'] and sha(checkpoint) == receipt['artifact_sha256']
    with np.load(checkpoint, allow_pickle=False) as source:
        raw = source['checkpoint_raw'].copy()
    head = np.flatnonzero(raw[:, f.COL['s2_head']])
    assert len(head) == 1
    head = int(head[0])
    rng = random.Random(2026092712)
    def replacement(pos):
        values = {name: rng.getrandbits(width) for name, width in r.SCHEMA}
        # Wrong legal clock resets live controller outputs at the faulted holder.
        values.update(address=pos, age=0)
        return np.array(f.encode_cell(r.lift(r.Cell(**values))), dtype=np.uint64)
    saved = {}
    cases = []
    for label in ('moving_single', 'repeated_pair'):
        events = {tick: {pos: replacement(pos) for pos in ((head+tick,) if label == 'moving_single' else (head, head+1))} for tick in range(8)}
        cases.append(run_case(label, lambda positions: raw[positions % f.Q], events, 10, saved, True))
    # Two adjacent holder clocks at t=0 cause the same erroneous Data copy.
    # A new, third copy at t=1 violates only the union bound: both individual
    # external pulses satisfy the original eleven-site sparsity predicate.
    g = p.layout()
    bank = np.array([[rng.getrandbits(64) for _ in range(g.memory_count+5)]], dtype=np.uint64)
    image = cone.BankImage(bank, np.zeros((1, 2), dtype=np.uint64))
    target = 200
    def initial(positions):
        result = image.cells(positions)
        result[:, f.COL['age']] = 17
        return result
    events = {0: {}, 1: {}}
    for pos in (target-1, target):
        cell = r.project(f.decode_cell(initial(np.array([pos]))[0]))
        values = {name: getattr(cell, name) for name, _ in r.SCHEMA}
        values.update(address=g.info[0]+(pos-target), age=f.U-1)
        events[0][pos] = np.array(f.encode_cell(r.lift(r.Cell(**values))), dtype=np.uint64)
    pos = target+1
    values = {name: getattr(r.project(f.decode_cell(initial(np.array([pos]))[0])), name) for name, _ in r.SCHEMA}
    values.update(age=18, s1_data=int(bank[0, target+1]))
    events[1][pos] = np.array(f.encode_cell(r.lift(r.Cell(**values))), dtype=np.uint64)
    cases.append(run_case('three_across_two_ticks', initial, events, 4, saved, False))
    np.savez_compressed(artifact, **saved)
    sources = (Path(__file__), Path(cone.__file__), Path(domain.__file__), Path(f.__file__), Path(r.__file__))
    result = dict(passed=True, cases=cases, checkpoint=str(checkpoint), checkpoint_sha256=sha(checkpoint), artifact_sha256=sha(artifact), descriptor_sha256=f.self_description().digest(), source_sha256={str(x): sha(x) for x in sources}, seconds=time.perf_counter()-started, host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, scope='Literal physical continuing-fault experiments. Two admissible eight-tick active-controller streams and a two-tick interacting negative control. No stochastic or amplification claim.')
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'cases'}, indent=2), flush=True)


if __name__ == '__main__':
    main()
