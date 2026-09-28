"""CPU-only evidence for evaluator self-description and Gray component execution.

python -m experiments.fixed_rule.vertical_slice --output figs/fixed_rule/vertical_slice_v1
Refuses to overwrite artifacts. This is NOT a fixed-rule Gray colony hierarchy.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time
import numpy as np
from gacsca.fixed_rule.machine import (Cell, MEM, GATE, LOOP, SCHEMA, WIDTH,
                                       encode_cell, step_ring, identity, self_description)
from gacsca.fixed_rule.tape import (encode_ring, decode_ring, encode_evaluation,
                                   decode_evaluation)
from gacsca.fixed_rule.native import library, run
from gacsca.fixed_rule import maintenance


def execute(output, steps=26):
    if steps < 26:
        raise ValueError('at least 26 steps required to witness two represented NAND writes')
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    paths = [output.with_suffix('.json'), output.with_suffix('.npz')]
    if any(path.exists() for path in paths):
        raise FileExistsError('refusing to replace existing evidence')
    root = Path(__file__).resolve().parents[2]
    sources = sorted([*root.glob('gacsca/fixed_rule/*.py'), *root.glob('gacsca/fixed_rule/*.c'),
                      *root.glob('experiments/fixed_rule/*.py'), *root.glob('tests/fixed_rule/*.py')])
    hashes = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    lib = library()
    reference = (Cell(kind=MEM, index=0), Cell(kind=GATE, index=0, head=1), Cell(kind=LOOP, index=1))
    physical, layout = encode_ring(reference)
    frames = [np.array([encode_cell(c) for c in reference], dtype=np.uint8)]
    log = []
    for period in range(1, steps + 1):
        start = time.monotonic()
        result = run(physical, ticks=layout.period_ticks, lib=lib)
        elapsed = time.monotonic() - start
        reference = step_ring(reference)  # diagnostic only; never passed into run
        decoded = decode_ring(physical, layout)
        actual_bits = np.array([encode_cell(c) for c in decoded], dtype=np.uint8)
        expected_bits = np.array([encode_cell(c) for c in reference], dtype=np.uint8)
        mismatches = int(np.count_nonzero(actual_bits != expected_bits))
        row = dict(period=period, **result, elapsed_seconds=elapsed,
                   raw_bit_mismatches=mismatches, represented_memory=decoded[0].bit)
        log.append(row)
        frames.append(actual_bits)
        if mismatches or result['completed_periods'] != 1:
            raise AssertionError(row)
    records = [dict(addr=100+j, age=maintenance.U-1, f1=0, f2=int(j == 0), wf1=0, wf2=0)
               for j in range(-5, 6)]
    component = maintenance.description()
    tape, component_layout = encode_evaluation(component, tuple(v for r in records for v in maintenance.pack(r)))
    start = time.monotonic()
    component_result = run(tape, ticks=component_layout.period_upper_bound, periods=1, lib=lib)
    component_result['elapsed_seconds'] = time.monotonic() - start
    actual = maintenance.unpack(decode_evaluation(tape, component_layout))
    expected = dict(addr=100, age=0, f1=0, f2=1, wf1=0, wf2=0)
    if actual != expected or component_result['completed_periods'] != 1:
        raise AssertionError((actual, component_result))
    component_result.update(decoded=actual, expected=expected,
                            gates=len(component.gates), physical_cells=len(tape),
                            description_sha256=component.digest())
    meta = dict(schema=1, scope='finite-ring self-description harness; NOT Gray block self-simulation',
                fixed_rule=identity(), source_sha256=hashes,
                evaluator=dict(nand_gates=len(self_description().gates), represented_cells=3,
                               physical_cells=len(physical), program_gates=len(layout.gates),
                               memory_cells=layout.memory_count,
                               period_ticks=layout.period_ticks,
                               period_tick_upper_bound=layout.period_upper_bound,
                               physical_bits=len(physical)*WIDTH,
                               array_bytes=physical.nbytes),
                periods=log, total_physical_ticks=sum(row['physical_ticks'] for row in log),
                total_execution_seconds=sum(row['elapsed_seconds'] for row in log),
                maintenance=component_result,
                hierarchy_levels_demonstrated=0,
                missing=['local block encoding and retrieval', 'Gray ProgramBit projection',
                         'combined colony/evaluator rule', 'hierarchical initialization/termination',
                         'spatial and temporal redundancy', 'simulated-layer correction',
                         'noise robustness'])
    # Exclusive writes protect historical evidence from accidental reruns.
    with paths[1].open('xb') as stream:
        np.savez_compressed(stream, frames=np.stack(frames), physical_final=physical,
                            maintenance_final=tape)
    meta['artifact_sha256'] = hashlib.sha256(paths[1].read_bytes()).hexdigest()
    with paths[0].open('x') as stream:
        json.dump(meta, stream, indent=2)
        stream.write('\n')
    print(json.dumps(dict(output=str(paths[0]), steps=steps,
                          raw_bit_mismatches=sum(row['raw_bit_mismatches'] for row in log),
                          physical_ticks=meta['total_physical_ticks'],
                          seconds=meta['total_execution_seconds'], maintenance=component_result), indent=2))
    return meta


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--steps', type=int, default=26)
    args = parser.parse_args()
    execute(args.output, args.steps)


if __name__ == '__main__':
    main()
