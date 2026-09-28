"""Bounded layout search for one fixed AND self-description.

Only ROM compilation order and scratch capacity vary.  The physical F,
alphabet, Q, U, and complete output mapping stay unchanged.
"""
import argparse
import json
from pathlib import Path
import resource
import time

from gacsca.fixed_rule import and_holder_program as p
from gacsca.fixed_rule import word_dag_order as order


def costs(layout):
    path = sum(layout.schedule(*span)[0] for span in layout.stage_ranges)
    path += layout.schedule(*layout.delivery_range)[0]
    return dict(core_cells=layout.computation_cells,
                memory_cells=layout.memory_count,
                instruction_cells=len(layout.instructions),
                controller_path_ticks=path,
                timing_fits=layout.timing_certificate()['fits'])


def search():
    start = time.perf_counter()
    original_description = p.compiled_description
    original_capacity = p.RESULT_CAPACITY
    base = original_description()
    rows = []
    try:
        for reverse in (False, True):
            for children in ('original', 'reverse', 'deep_first', 'shallow_first'):
                description, permutation = order.reorder(
                    base, reverse_outputs=reverse, children=children)
                assert order.verify(base, description, permutation)
                for capacity in (256, 270, 288, 320, 352, 384, 416):
                    p.compiled_description = lambda d=description: d
                    p.RESULT_CAPACITY = capacity
                    p.layout.cache_clear()
                    row = dict(reverse_outputs=reverse, children=children,
                               capacity=capacity, description_sha256=description.digest())
                    try:
                        row.update(costs(p.layout()), fits=True)
                    except (ValueError, AssertionError) as error:
                        row.update(fits=False, error=repr(error))
                    rows.append(row)
    finally:
        p.compiled_description = original_description
        p.RESULT_CAPACITY = original_capacity
        p.layout.cache_clear()
    accepted = [row for row in rows if row['fits'] and row['timing_fits']]
    best_time = min(accepted, key=lambda row: (row['controller_path_ticks'], row['core_cells']))
    best_space = min(accepted, key=lambda row: (row['core_cells'], row['controller_path_ticks']))
    return dict(passed=True, original_description_sha256=base.digest(),
                baseline=costs(p.layout()), best_time=best_time,
                best_space=best_space, trials=rows,
                seconds=time.perf_counter() - start,
                host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                scope='Exact dependency-order verification and deterministic fixed-ROM cost; '
                      'not physical execution or a lower Q/U certificate.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    result = search()
    with args.output.open('x') as stream:
        stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items() if key != 'trials'},
                     indent=2))


if __name__ == '__main__':
    main()
