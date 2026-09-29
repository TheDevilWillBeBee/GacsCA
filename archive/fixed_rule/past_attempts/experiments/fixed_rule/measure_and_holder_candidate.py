"""Reproduce bounded CPU measurements for the isolated fixed-AND ROM candidate."""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import sys
import time

from gacsca.fixed_rule import and_holder_rule as f, and_holder_core as c
from gacsca.fixed_rule import and_holder_program as p
from gacsca.fixed_rule import compact16_holder_compiler_program as old
from gacsca.fixed_rule.word_identity_and import optimize
from gacsca.fixed_rule.word_and_fusion import fuse_exclusive_and
from gacsca.fixed_rule import word_dag_order as order
from experiments.fixed_rule.certify_and_holder_rom import check
from experiments.fixed_rule.certify_and_holder_read_b import (
    check as check_and_read_b, check_fetch as check_and_fetch,
)


def cost(program):
    layout = program.layout()
    ticks = sum(layout.schedule(*span)[0] for span in layout.stage_ranges)
    ticks += layout.schedule(*layout.delivery_range)[0]
    return dict(memory_cells=layout.memory_count,
                instruction_cells=len(layout.instructions),
                core_cells=layout.computation_cells,
                controller_path_ticks=ticks,
                ROM_sha256=hashlib.sha256(program.base_rom().tobytes()).hexdigest())


def measure():
    started = time.perf_counter()
    widths = tuple(width for _ in f.NEIGHBORHOOD for _, width in f.SCHEMA)
    optimized = optimize(f.self_description(), input_widths=widths)[0]
    fused, fusion = fuse_exclusive_and(optimized)
    ordered, permutation = order.reorder(fused, reverse_outputs=True,
                                         children='original')
    assert order.verify(fused, ordered, permutation)
    assert ordered.operations == p.compiled_description().operations
    assert ordered.outputs == p.compiled_description().outputs
    assert c.AND not in (c.HALT, c.IF_THIRD, c.LIT)
    assert (dict(c.SCHEMA)['kind'], dict(c.SCHEMA)['alu']) == (4, 3)
    certificate = check()
    physical_and_events = dict(read_b=check_and_read_b(), fetch=check_and_fetch())
    current, reference = cost(p), cost(old)
    assert current['core_cells'] + 5 <= f.Q
    assert current['controller_path_ticks'] < reference['controller_path_ticks']
    source_files = [Path(module.__file__) for module in (f, c, p, order)]
    source_files += list(Path('gacsca/fixed_rule').glob('*and*.py'))
    source_files += [Path(__file__), Path('experiments/fixed_rule/certify_and_holder_rom.py'),
                     Path('experiments/fixed_rule/certify_and_holder_read_b.py'),
                     Path('tests/fixed_rule/test_and_holder_candidate.py')]
    source_files += [Path(module.__file__) for module in tuple(sys.modules.values())
                     if getattr(module, '__file__', None)
                     and '/fixed_rule/' in str(Path(module.__file__).resolve())]
    hashes = {str(path.relative_to(Path.cwd().resolve())):
              hashlib.sha256(path.read_bytes()).hexdigest()
              for path in sorted({path.resolve() for path in source_files})}
    return dict(passed=True, fixed_rule=f.identity(), fusion=fusion,
                instruction_order=dict(reverse_outputs=True,
                                       children='original',
                                       ordered_sha256=p.compiled_description().digest()),
                current=current, previous_compiler_candidate=reference,
                core_cells_saved=reference['core_cells']-current['core_cells'],
                controller_ticks_saved=reference['controller_path_ticks']-current['controller_path_ticks'],
                conditional_certificate=certificate,
                physical_and_events=physical_and_events,
                source_sha256=hashes, seconds=time.perf_counter()-started,
                host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                physical_period_executed=False, depth2_macrostep_executed=False,
                scope='Compiler and conditional symbolic own-ROM certificate, plus focused '
                      'local tests. Physical path composition and full periods remain open.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    result = measure()
    with args.output.open('x') as stream:
        stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items()
                      if key not in ('conditional_certificate', 'source_sha256', 'fixed_rule')},
                     indent=2))


if __name__ == '__main__':
    main()
