"""CPU evidence for independent, locally bounded evaluator regions.

This intentionally records the missing-feedback witness: a second evaluation of
unchanged input snapshots repeats F(x), rather than producing F(F(x)). No claim of
block self-simulation is made until local retrieval and commit are implemented.
"""
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import tarfile
import time
import numpy as np
from gacsca.fixed_rule import confined as rule
from gacsca.fixed_rule.confined_native import library, run, COL
from gacsca.fixed_rule.confined_tape import encode_evaluations, decode_evaluations


def execute(output):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    paths = [output.with_suffix(suffix) for suffix in ('.json', '.npz', '.tar.gz')]
    if any(path.exists() for path in paths):
        raise FileExistsError('existing evidence must be preserved')
    upper = (rule.Cell(kind=rule.MEM, index=0, head=1, phase=rule.WRITE, rd=0, value=1, first=1),
             rule.Cell(kind=rule.GATE, index=0), rule.Cell(kind=rule.LOOP, index=1, last=1))
    neighborhoods = tuple((upper[i-1], cell, upper[(i+1) % len(upper)]) for i, cell in enumerate(upper))
    physical, geometry = encode_evaluations(neighborhoods)
    first = rule.step_ring(upper)
    second = rule.step_ring(first)
    frames, logs = [], []
    lib = library()
    for cycle in range(2):
        started = time.monotonic()
        metrics = run(physical, geometry.period_ticks, lib)
        metrics['elapsed_seconds'] = time.monotonic() - started
        actual = decode_evaluations(physical, geometry)
        if actual != first:
            raise AssertionError('physical complete-controller evaluation failed')
        metrics['raw_snapshot_transition_mismatches'] = 0
        logs.append(metrics)
        frames.append(np.array([rule.encode_cell(cell) for cell in actual], dtype=np.uint8))
    assert first != second, 'missing-feedback witness became vacuous'
    root = Path(__file__).resolve().parents[2]
    sources = sorted([*root.glob('gacsca/fixed_rule/*.py'), *root.glob('gacsca/fixed_rule/*.c'),
                      *root.glob('tests/fixed_rule/*.py'), *root.glob('experiments/fixed_rule/*.py')])
    hashes = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    with tarfile.open(paths[2], 'x:gz') as archive:
        for name in hashes:
            archive.add(root/name, arcname=name)
    with paths[1].open('xb') as stream:
        np.savez_compressed(stream, decoded_cycles=np.stack(frames), physical_final=physical,
                            input_ring=np.array([rule.encode_cell(cell) for cell in upper], dtype=np.uint8),
                            expected_second=np.array([rule.encode_cell(cell) for cell in second], dtype=np.uint8))
    data = dict(schema=1, scope='confined local evaluation regions; input snapshots; no retrieval/commit',
                fixed_rule=rule.identity(), colonies=3, colony_cells=geometry.colony_cells,
                physical_cells=len(physical), memory_records_per_colony=geometry.memory_count,
                description_gates=len(geometry.gates), period_ticks=geometry.period_ticks,
                cycles=logs, missing_feedback_witness=True,
                second_cycle_vs_second_transition_raw_bit_mismatches=int(np.count_nonzero(
                    frames[1] != np.array([rule.encode_cell(cell) for cell in second], dtype=np.uint8))),
                hierarchy_levels_demonstrated=0, source_sha256=hashes,
                artifact_sha256=hashlib.sha256(paths[1].read_bytes()).hexdigest(),
                source_archive_sha256=hashlib.sha256(paths[2].read_bytes()).hexdigest())
    with paths[0].open('x') as stream:
        json.dump(data, stream, indent=2)
        stream.write('\n')
    print(json.dumps({name: data[name] for name in (
        'colonies', 'colony_cells', 'description_gates', 'period_ticks', 'cycles',
        'second_cycle_vs_second_transition_raw_bit_mismatches', 'hierarchy_levels_demonstrated')}, indent=2))
    return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    execute(parser.parse_args().output)
