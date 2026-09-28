"""Bounded physical GPU periods; upper transitions are diagnostics only."""
import argparse
from contextlib import ExitStack
import hashlib
import json
from pathlib import Path
import resource
import time
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import compact16_holder_resident_general as gpu
from gacsca.fixed_rule import compact16_holder_resident_period as resident
from gacsca.fixed_rule import compact16_holder_records as q, compact16_holder_packed as packed
from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_core as c
from gacsca.fixed_rule import compact16_holder_program as p, compact16_holder_projected as r
from gacsca.fixed_rule import compact16_holder_native as native
from gacsca.fixed_rule.wordcode import Program
from experiments.fixed_rule.compact16_holder_active_fixture import parents as active_parents
from experiments.fixed_rule.audit_small_holder_position_events import sha


def run(reference, artifact):
    saved = None
    if reference:
        receipt = json.loads(reference.read_text())
        assert receipt['passed'] and receipt['periods'] == 2
        assert receipt['descriptor_sha256'] == f.self_description().digest()
        assert receipt['rom_sha256'] == hashlib.sha256(p.base_rom().tobytes()).hexdigest()
        assert sha(reference.with_suffix('.npz')) == receipt['snapshot_sha256']
        saved = np.load(reference.with_suffix('.npz'), allow_pickle=False)
        parents = tuple(r.decode_cell(row) for row in saved['initial_upper'])
    else:
        parents = active_parents()
    n = len(parents)
    assert n in (3, 31)
    initial = np.array([r.encode_cell(cell) for cell in parents], dtype=np.uint64)
    g = p.layout(); timing = g.timing_certificate()
    started = time.perf_counter(); gpu_seconds = 0.; totals = {}; results = []
    banks = []; rows_saved = []; counts_saved = []; right_saved = []; left_saved = []
    with gpu.World(parents, device_budget=32*1024**2) as world:
        initialbank, _, _ = world._core.snapshot()
        known = np.zeros_like(initialbank)
        for col, cell in enumerate(parents):
            known[col, list(g.info)] = f.encode_cell(r.lift(cell))
        np.testing.assert_array_equal(initialbank, known)

        def advance(age):
            nonlocal gpu_seconds
            amount = age-world.age
            assert amount > 0
            start = time.perf_counter()
            with ExitStack() as stack:
                for module, name in ((f, 'local_step'), (r, 'local_step'),
                                     (native, 'local_step'), (Program, 'evaluate')):
                    stack.enter_context(patch.object(module, name, side_effect=AssertionError('host transition during evolution')))
                metric = world.advance(amount, extra_device_budget=32*1024**2)
            gpu_seconds += time.perf_counter()-start
            for key, value in metric.items():
                totals[key] = max(totals.get(key, 0), value) if key == 'extra_device_bytes' else totals.get(key, 0)+value

        def quiet():
            bank, rows, counts = world._core.snapshot()
            fields = [q.COL[name] for name in resident.ACTIVE if name != 'signal']
            for col, num in enumerate(counts):
                assert not np.any(packed.unpack(rows[col, :int(num)])[:, fields]), 'live controller/mail at quiet boundary'
            return bank, rows, counts

        for epoch in range(2):
            before = parents
            expected = tuple(r.local_step(tuple(before[(col+j)%n] for j in f.NEIGHBORHOOD)) for col in range(n))
            raw = np.array([f.encode_cell(r.lift(cell)) for cell in before], dtype=np.uint64)
            wanted = np.array([f.encode_cell(r.lift(cell)) for cell in expected], dtype=np.uint64)
            for stage in range(3):
                stop = c.RESET_AGES[stage]+max(timing['gathers'][stage]['head_stopped'], timing['gathers'][stage]['last_arrival'])
                advance(stop); bank, _, _ = quiet()
                for prior in range(stage+1):
                    for wire in g.gathered_inputs:
                        offset, field = wire//f.FIELDS-7, wire%f.FIELDS
                        np.testing.assert_array_equal(bank[:, g.history(prior, offset, field)], raw[(np.arange(n)+offset)%n, field])
                print(json.dumps(dict(period=epoch+1, phase='gather_'+str(stage), age=world.age, seconds=time.perf_counter()-started)), flush=True)
            advance(c.VOTE_AGES[0]+max(timing['stage3_head_stopped'], timing['stage3_last_delivery']))
            bank, _, _ = quiet()
            np.testing.assert_array_equal(bank[:, list(g.hold)], wanted)
            print(json.dumps(dict(period=epoch+1, phase='first_evaluation', age=world.age, seconds=time.perf_counter()-started)), flush=True)
            advance(c.RESET_AGES[3]+g.schedule(*g.stage_ranges[3])[0]); quiet()
            advance(c.RESET_AGES[4]+g.schedule(*g.stage_ranges[4])[0])
            bank, _, _ = quiet()
            np.testing.assert_array_equal(bank[:, list(g.hold)], wanted)
            advance(f.U)
            assert world.age == 0 and world.time == (epoch+1)*f.U
            bank, rows, counts = quiet()
            assert world._flags is None
            assert world.decode() == expected
            sides = []
            for positions in (tuple(range(1, 6)), tuple(range(f.Q-5, f.Q))):
                values = np.array([[cell.signal for cell in world.logical_cells(tuple(col*f.Q+a for a in positions))] for col in range(n)], dtype=np.uint64)
                bits = values[:, 2] >> 2
                assert np.all((bits == 0) | (bits == 1))
                np.testing.assert_array_equal(values, bits[:, None] << np.array([4, 3, 2, 1, 0], dtype=np.uint64))
                sides.append(bits)
            left, right = sides
            if saved is not None:
                full = saved['boundary_data'][epoch]
                np.testing.assert_array_equal(bank, np.concatenate((full[:, :g.memory_count], full[:, -5:]), axis=1))
                assert not np.any(full[:, g.memory_count:-5])
                np.testing.assert_array_equal(right, saved['boundary_right'][epoch])
                np.testing.assert_array_equal(left, saved['boundary_left'][epoch])
                assert not np.any(saved['boundary_flags'][epoch])
            else:
                center = n//2
                if epoch == 0:
                    assert expected[center+1].s2_head and expected[center+1].s2_phase == c.WRITE
                else:
                    value = (~(initial[center, r.COL['s2_value']] & initial[center, r.COL['s2_data']])) & np.uint64((1 << 64)-1)
                    assert expected[center+1].s2_data == int(value)
                    assert expected[center+2].s2_head and expected[center+2].s2_phase == c.FETCH and expected[center+2].s2_pc == 24
            parents = expected
            changed = sum(a != b for old, new in zip(before, expected) for a, b in zip(r.encode_cell(old), r.encode_cell(new)))
            result = dict(period=epoch+1, passed=True, age=world.age, time=world.time, changed_projected_words=changed,
                          complete_raw_decode_matches=True, boundary_data_matches_CPU=saved is not None,
                          right=right.tolist(), left=left.tolist(), gpu_seconds_so_far=gpu_seconds)
            results.append(result); banks.append(bank); rows_saved.append(rows); counts_saved.append(counts); right_saved.append(right); left_saved.append(left)
            print(json.dumps(result), flush=True)
        np.savez_compressed(artifact, initial_upper=initial, initial_bank=initialbank, boundary_banks=np.stack(banks),
                            boundary_sparse=np.stack(rows_saved), boundary_counts=np.stack(counts_saved),
                            boundary_right=np.stack(right_saved), boundary_left=np.stack(left_saved))
        explicit = world.device_bytes+totals.get('extra_device_bytes', 0)+n*f.Q//64*32+2*n
        assert explicit <= 64*1024**2
        result = dict(passed=True, colonies=n, periods=2, physical_ticks=world.time,
                      period_results=results, metrics=totals, gpu_evolution_seconds=gpu_seconds,
                      peak_explicit_device_bytes_upper_bound=explicit, host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                      seconds=time.perf_counter()-started, initial_histories_zero=True, one_retained_physical_state=True,
                      sustained_upper_arithmetic=saved is None, descriptor_sha256=f.self_description().digest(),
                      rom_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest(), artifact=str(artifact), artifact_sha256=sha(artifact),
                      reference=str(reference) if reference else None, reference_sha256=sha(reference) if reference else None,
                      source_sha256={str(Path(__file__)):sha(__file__)},
                      limitation='Two one-link coherent physical periods. Not a complete depth-two work period or noise robustness result.')
    if saved is not None: saved.close()
    return result


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--reference', type=Path); parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(); artifact = args.output.with_suffix('.npz')
    if args.output.exists() or artifact.exists(): raise FileExistsError('preserve evidence')
    result = run(args.reference, artifact)
    with args.output.open('x') as stream: stream.write(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__': main()
