"""Uninterrupted all-fields dense U20 trajectory with read-only checkpoints."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import time

import numpy as np

from gacsca.fixed_rule import spatial_codec8
from gacsca.fixed_rule import stream28_compact_layout as layout_module
from gacsca.fixed_rule import stream28_dual_holder_rule20 as holder
from gacsca.fixed_rule import stream28_dual_pass20 as physical
from gacsca.fixed_rule import stream28_dual_pass_optimized20 as description
from gacsca.fixed_rule import stream28_dual_projected20 as projected
from gacsca.fixed_rule.gpu_validation import dense
from gacsca.fixed_rule.gpu_validation.initial import (
    decode_info, expected_upper_step, initialize, state_sha256)
from experiments.fixed_rule.build_compact8_circuit import initial_cells
from experiments.fixed_rule.compact8_address_rom import project_all_dual_static


def boundaries():
    ages = [0, 1, 2, 131072, 262144, 393216, 393217, 393218,
            438343, 458754, 630680, 630685, 647168,
            655360, 688128, 704512, 720896, 720897, 720898,
            766023, 786434, physical.U-1, physical.U, physical.U+1]
    ages += [65515, 196586, 327657]
    return sorted({v for age in ages for v in (age-1, age, age+1)
                   if v >= 0})


def sampled_parity(before, after, sites):
    for site in sites:
        neighbors = tuple(physical.decode_cell(
            before[(site+delta)%len(before)].tolist())
            for delta in physical.NEIGHBORHOOD)
        expected = np.asarray(physical.encode_cell(
            physical.local_step(neighbors)), dtype=np.uint64)
        got = after[site]
        different = np.flatnonzero(expected != got)
        if len(different):
            field = int(different[0])
            raise AssertionError(('raw local parity', site, field,
                                  int(expected[field]), int(got[field])))


def checkpoint(raw, tick, initial_static, initial_sources, upper, predictions,
               initial_info, captured_centers):
    q = physical.Q
    age = raw[:, holder.COL['age']]
    address = raw[:, holder.COL['address']]
    if not np.all(age == tick%physical.U):
        index = int(np.flatnonzero(age != tick%physical.U)[0])
        raise AssertionError(('Age', tick, index, int(age[index])))
    if not np.array_equal(address, np.arange(len(raw))%q):
        index = int(np.flatnonzero(address != np.arange(len(raw))%q)[0])
        raise AssertionError(('Address', tick, index, int(address[index])))
    if not np.array_equal(raw[:, initial_static], initial_sources):
        bad = np.argwhere(raw[:, initial_static] != initial_sources)[0]
        raise AssertionError(('static ROM', tick, int(bad[0]),
                              int(initial_static[int(bad[1])])))
    decoded = decode_info(raw)
    decoded_sha = hashlib.sha256(np.asarray(decoded, dtype=np.uint64).tobytes()).hexdigest()
    prior_period = min(tick//physical.U, len(predictions))
    completed_gather = {65515:0, 196586:1, 327657:2}
    relative = tick%physical.U
    checked_history = 0
    for arrival, stage in completed_gather.items():
        if relative not in (arrival, arrival+1):
            continue
        col = len(upper)//2
        bank = layout_module.build()
        parent = initial_info if prior_period == 0 else predictions[prior_period]
        for neighbor, field in bank.gathered:
            site = bank.history(stage, neighbor, field)
            actual = int(raw[col*q+site, holder.COL['s2_data']])
            want = int(parent[(col+neighbor-7)%len(upper)][field])
            if actual != want:
                raise AssertionError(('gather history',tick,stage,col,site,
                                      neighbor,field,actual,want))
            checked_history += 1
    if tick%physical.U == 0 and tick:
        expected_info = predictions[prior_period]
    else:
        expected_info = initial_info if prior_period == 0 else predictions[prior_period]
    safe_prior = range(7*prior_period, len(upper)-7*prior_period)
    for col in safe_prior:
        if decoded[col] != expected_info[col]:
            field = next(i for i,(a,b) in enumerate(zip(decoded[col],expected_info[col]))
                         if a != b)
            raise AssertionError(('Info before/after commit', tick, col, field,
                                  decoded[col][field], expected_info[col][field]))
    if tick%physical.U == physical.U-1:
        hold_sites = np.asarray(layout_module.build().hold)
        for col in range(7*(prior_period+1),len(upper)-7*(prior_period+1)):
            hold = tuple(map(int, raw[col*q+hold_sites,
                                      holder.COL['s2_data']]))
            want = predictions[prior_period+1][col]
            if hold != want:
                field = next(i for i,(a,b) in enumerate(zip(hold,want)) if a != b)
                raise AssertionError(('Hold before Info commit',tick,col,field,
                                      hold[field],want[field]))
    if tick%physical.U in (physical.EARLY_RUN_START,
                            holder.RESET_AGES[4]+2):
        center = len(upper)//2
        expected_spatial = captured_centers[prior_period]
        actual = raw[center*q:(center+1)*q, holder.FIELDS:]
        if not np.array_equal(actual, expected_spatial):
            site,field = map(int,np.argwhere(actual != expected_spatial)[0])
            raise AssertionError(('evaluator capture',tick,center,site,field,
                                  int(actual[site,field]),
                                  int(expected_spatial[site,field])))
    # Work-boundary Info is the complete 119-word represented state.
    mismatches = []
    period = tick//physical.U
    if tick%physical.U in (0, 1) and period and period in predictions:
        expected = predictions[period]
        safe = range(7*period, len(upper)-7*period)
        for col in safe:
            for field, (actual, want) in enumerate(zip(decoded[col], expected[col])):
                if actual != want:
                    mismatches.append((col, field, actual, want))
                    break
        if mismatches:
            raise AssertionError(('decoded upper F', tick, mismatches[:8]))
    sample = [0, 1, 7, q-1, q, (len(upper)//2)*q+2496,
              (len(upper)//2)*q+2498, len(raw)-1]
    return dict(tick=tick, age=tick%physical.U, state_sha256=state_sha256(raw),
                decoded_info_sha256=decoded_sha,
                gathered_history_words_checked=checked_history,
                sample={str(i):[int(v) for v in raw[i]] for i in sample},
                flag1_sites=int(np.count_nonzero(raw[:, holder.COL['f1']])),
                flag2_sites=int(np.count_nonzero(raw[:, holder.COL['f2']])),
                head_copies=int(sum(np.count_nonzero(raw[:, holder.COL[f's{k}_head']])
                                    for k in range(5))),
                mail_copies=int(sum(np.count_nonzero(raw[:, holder.COL[f's{k}_{lane}_valid']])
                                    for k in range(5) for lane in ('lp','rp'))),
                decoded_centers_checked=max(0, len(upper)-14*period)
                if tick%physical.U in (0,1) and period in predictions else 0)


def write_json(path, data):
    temp = path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(data, indent=2)+'\n')
    os.replace(temp, path)


def run(colonies, periods, stop_tick, seed, output, snapshots=False):
    started = time.perf_counter()
    raw, upper = initialize(colonies, seed)
    initial_hash = state_sha256(raw)
    initial_static = [holder.COL[name] for name, _ in holder.STATIC]
    spatial_dynamic = {1, 3, *range(spatial_codec8.FIELDS-12,
                                    spatial_codec8.FIELDS)}
    initial_static += [holder.FIELDS+i for i in range(spatial_codec8.FIELDS)
                       if i not in spatial_dynamic]
    initial_static = np.asarray(initial_static)
    initial_sources = raw[:, initial_static].copy()
    predictions = {}
    predicted = upper
    initial_info = tuple(projected.encode_cell(projected.project(cell))
                         for cell in upper)
    center = colonies//2
    states_at_start = [upper]
    for period in range(1, periods+1):
        predicted = expected_upper_step(predicted)
        states_at_start.append(predicted)
        predictions[period] = tuple(projected.encode_cell(projected.project(cell))
                                    for cell in predicted)
    captured_centers = {}
    for period, states in enumerate(states_at_start[:-1]):
        upper_words = tuple(word for offset in physical.NEIGHBORHOOD
                            for word in physical.encode_cell(
                                states[(center+offset)%colonies]))
        addressed = project_all_dual_static(states[center].holder.address,
                                            upper_words, True)
        captured_centers[period] = np.asarray(
            [spatial_codec8.encode_cell(row)
             for row in initial_cells(addressed,True,True)],dtype=np.uint64)
    source = Path(dense.__file__).with_suffix('.cu')
    receipt = dict(status='running', physical_rule='stream28_dual_pass20.local_step',
                   q=physical.Q, u=physical.U, radius=7, fields=physical.FIELDS,
                   width_bits=physical.WIDTH,
                   description_sha256=description.build().digest(),
                   backend_python_sha256=hashlib.sha256(Path(dense.__file__).read_bytes()).hexdigest(),
                   backend_cuda_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                   runner_python_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   initializer_python_sha256=hashlib.sha256(Path(__import__(
                       'gacsca.fixed_rule.gpu_validation.initial',
                       fromlist=['__file__']).__file__).read_bytes()).hexdigest(),
                   initial_state_sha256=initial_hash, colonies=colonies,
                   upper_seed=seed, periods=periods, target_tick=stop_tick,
                   checkpoints=[], limitation='Upper geometry seam; only centers with full radius-seven causal cone are compared.')
    write_json(output, receipt)
    sites = sorted({0, 6, 7, physical.Q-1, physical.Q,
                    (colonies//2)*physical.Q+2496,
                    (colonies//2)*physical.Q+2498,
                    len(raw)-1})
    schedule = [base+t for base in range(0, periods*physical.U, physical.U)
                for t in boundaries() if base+t <= stop_tick]
    schedule += [p*physical.U for p in range(1,periods+1)
                 if p*physical.U<=stop_tick]
    schedule = sorted(set(schedule+[stop_tick]))
    last_raw = None
    last_tick = None
    try:
        with dense.World(raw) as world:
            receipt['device_bytes'] = world.device_bytes
            receipt['host_raw_bytes'] = raw.nbytes
            receipt['host_static_reference_bytes'] = initial_sources.nbytes
            for tick in schedule:
                run_start = time.perf_counter()
                world.run(tick-world.time)
                run_seconds = time.perf_counter()-run_start
                read_start = time.perf_counter()
                current = world.read()
                read_seconds = time.perf_counter()-read_start
                try:
                    if last_tick is not None and tick == last_tick+1:
                        sampled_parity(last_raw, current, sites)
                    entry = checkpoint(current, tick, initial_static,
                                       initial_sources, upper, predictions,
                                       initial_info, captured_centers)
                except Exception:
                    np.save(output.with_name(output.stem+f'_divergence_t{tick}.npy'), current)
                    raise
                entry.update(run_seconds=run_seconds,
                             read_seconds=read_seconds,
                             elapsed_seconds=time.perf_counter()-started,
                             max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
                receipt['checkpoints'].append(entry)
                receipt['last_tick'] = tick
                if snapshots and tick%physical.U == 0:
                    np.save(output.with_name(output.stem+f'_t{tick}.npy'),current)
                write_json(output, receipt)
                last_raw, last_tick = current, tick
    except Exception as exc:
        receipt.update(status='failed', error=repr(exc),
                       seconds=time.perf_counter()-started)
        write_json(output, receipt)
        raise
    receipt.update(status='completed',seconds=time.perf_counter()-started,
                   max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                   measured_seconds_per_tick=(time.perf_counter()-started)/max(1,stop_tick))
    write_json(output, receipt)
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--colonies', type=int, default=31)
    parser.add_argument('--periods', type=int, default=1)
    parser.add_argument('--stop-tick', type=int)
    parser.add_argument('--seed', type=int, default=20260929)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--snapshots', action='store_true')
    args = parser.parse_args()
    if args.output.exists():
        parser.error('output already exists; receipts are immutable')
    if args.periods not in (1,2) or not 0 <= (args.stop_tick or args.periods*physical.U) <= args.periods*physical.U:
        parser.error('one or two bounded periods required')
    print(json.dumps(run(args.colonies,args.periods,
                         args.stop_tick if args.stop_tick is not None else args.periods*physical.U,
                         args.seed,args.output,args.snapshots),indent=2))
