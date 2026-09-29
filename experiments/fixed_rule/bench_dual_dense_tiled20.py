"""Bounded literal dense CUDA throughput probe; no event skipping."""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time

import numpy as np

from gacsca.fixed_rule import stream28_dual_dense_gpu20 as reference
from gacsca.fixed_rule import stream28_dual_dense_gpu20_tiled as tiled
from gacsca.fixed_rule import stream28_dual_holder_rule20 as holder
from gacsca.fixed_rule import stream28_dual_pass20 as physical
from gacsca.fixed_rule import stream28_dual_pass_optimized20 as description
from gacsca.fixed_rule import stream28_dual_holder_rom as rom
from experiments.fixed_rule.compact8_address_rom import template


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--colonies', type=int, choices=(1, 15, 31), required=True)
    parser.add_argument('--ticks', type=int, default=20)
    parser.add_argument('--check-reference', action='store_true')
    parser.add_argument('--fixture', choices=('zero', 'active-evaluator'),
                        default='zero')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if not 1 <= args.ticks <= 1000: raise ValueError('bounded pilot only')
    n = args.colonies * physical.Q
    if args.fixture == 'zero':
        raw = np.zeros((n, physical.FIELDS), dtype=np.uint64)
        raw[:, holder.COL['address']] = np.arange(n, dtype=np.uint64) % physical.Q
    else:
        evaluator = template(True, True)
        age = physical.EARLY_RUN_START + 119
        cells = (physical.Cell(
            holder.Cell(address=site, age=age,
                        **rom.holder_static_fields(site)), evaluator[site])
            for site in range(physical.Q))
        base = np.array([physical.encode_cell(cell) for cell in cells],
                        dtype=np.uint64)
        raw = np.tile(base, (args.colonies, 1))
    if args.check_reference:
        with tiled.World(raw) as checked, reference.World(raw) as oracle:
            checked.run(1)
            oracle.run(1)
            np.testing.assert_array_equal(checked.read(), oracle.read())
    with tiled.World(raw) as world:
        world.run(1)
        started = time.perf_counter()
        world.run(args.ticks)
        run_seconds = time.perf_counter() - started
        result = dict(colonies=args.colonies, physical_sites=n,
                      fixture=args.fixture,
                      measured_ticks=args.ticks, warmup_ticks=1,
                      run_seconds=run_seconds,
                      seconds_per_tick=run_seconds / args.ticks,
                      site_transitions_per_second=n * args.ticks / run_seconds,
                      resident_device_bytes=world.device_bytes,
                      peak_init_or_read_bytes=world.peak_init_or_read_bytes,
                      checked_one_tick_against_reference=args.check_reference,
                      physical_description_sha256=description.build().digest(),
                      kernel_sha256=sha(Path(tiled.__file__).with_suffix('.cu')),
                      module_sha256=sha(tiled.__file__),
                      host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                      scope='Complete local F at every site and tick; all raw fields '
                            'resident, host timing excludes initialization/transpose; '
                            'fixture is a throughput probe, not a closed macrostep')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__': main()
