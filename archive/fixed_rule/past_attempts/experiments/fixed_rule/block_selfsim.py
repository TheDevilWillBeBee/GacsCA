"""Literal CPU block-self-simulation of the communicating computation substrate.

This is NOT yet a Gray/Gács maintenance/repair rule or projected ProgramBit rule.
All host reference transitions are diagnostic; only fm_local evolves the tape.
"""
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import tarfile
import time
import numpy as np
from gacsca.fixed_rule import communicating as rule, block
from gacsca.fixed_rule.block_initial import resource_estimate
from gacsca.fixed_rule.communicating_native import library, run, COL


def initial_ring():
    return (rule.Cell(kind=rule.MEM, index=0, bit=1, head=1, phase=rule.READ_B,
                      rb=0, rd=1, value=1),
            rule.Cell(kind=rule.MEM, index=1, bit=1),
            rule.Cell(kind=rule.GATE, index=1, a=0, b=1, d=1,
                      rp_target=0, rp_bit=0, rp_cross=1, rp_valid=1))


def execute(output, steps=8):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    paths = [output.with_suffix(suffix) for suffix in ('.json', '.npz', '.tar.gz')]
    if any(p.exists() for p in paths):
        raise FileExistsError('refusing to overwrite evidence')
    if steps < 8:
        raise ValueError('at least eight steps required for both represented NAND writes')
    root = Path(__file__).resolve().parents[2]
    sources = sorted([*root.glob('gacsca/fixed_rule/*.py'), *root.glob('gacsca/fixed_rule/*.c'),
                      *root.glob('tests/fixed_rule/*.py'), *root.glob('experiments/fixed_rule/*.py')])
    hashes = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    reference = initial_ring()
    physical = block.encode(reference)
    geometry = block.layout()
    lib = library()
    frames = [np.array([rule.encode_cell(cell) for cell in reference], dtype=np.uint8)]
    rows = []
    packet_probe = None
    first_send_time = geometry.schedule()[1][0][-1]
    for period in range(1, steps+1):
        started = time.monotonic()
        if period == 1:
            early = run(physical, first_send_time, lib)
            packet_probe = physical.copy()
            if not np.any(packet_probe[:, COL['lp_valid']]):
                raise AssertionError('local SEND did not produce a physical packet')
            metrics = run(physical, geometry.period_ticks-first_send_time, lib)
            metrics['physical_ticks'] += early['physical_ticks']
            metrics['local_evaluations'] += early['local_evaluations']
        else:
            metrics = run(physical, geometry.period_ticks, lib)
        elapsed = time.monotonic()-started
        actual = block.decode(physical)
        reference = rule.step_ring(reference)
        actual_bits = np.array([rule.encode_cell(cell) for cell in actual], dtype=np.uint8)
        expected_bits = np.array([rule.encode_cell(cell) for cell in reference], dtype=np.uint8)
        mismatches = int(np.count_nonzero(actual_bits != expected_bits))
        boundary = block.check_boundary(physical)
        row = dict(period=period, **metrics, elapsed_seconds=elapsed,
                   raw_bit_mismatches=mismatches, admissible_boundary=boundary,
                   represented_memory=actual[1].bit)
        rows.append(row)
        frames.append(actual_bits)
        print(json.dumps(row), flush=True)
        if mismatches or not boundary:
            raise AssertionError(row)
    with tarfile.open(paths[2], 'x:gz') as archive:
        for name in hashes:
            archive.add(root/name, arcname=name)
    with paths[1].open('xb') as stream:
        np.savez_compressed(stream, frames=np.stack(frames), physical_final=physical,
                            first_send_physical=packet_probe)
    data = dict(schema=1, scope='one-link noiseless block self-simulation of full communicating evaluator; NOT Gray/Gacs repair',
                fixed_rule=rule.identity(), colonies=3, colony_cells=geometry.colony_cells,
                physical_cells=len(physical), memory_records=geometry.memory_count,
                instructions=len(geometry.instructions), description_gates=len(rule.self_description().gates),
                timing=geometry.timing_certificate(), first_send_time=first_send_time,
                periods=rows, total_ticks=sum(row['physical_ticks'] for row in rows),
                total_seconds=sum(row['elapsed_seconds'] for row in rows),
                executed_computing_substrate_links=1, executed_gray_gacs_hierarchy_levels=0,
                initialization_only_depth_estimates=[resource_estimate(1,depth) for depth in (1,2,3)],
                source_sha256=hashes,
                artifact_sha256=hashlib.sha256(paths[1].read_bytes()).hexdigest(),
                source_archive_sha256=hashlib.sha256(paths[2].read_bytes()).hexdigest())
    with paths[0].open('x') as stream:
        json.dump(data,stream,indent=2)
        stream.write('\n')
    return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--steps', type=int, default=8)
    args = parser.parse_args()
    execute(args.output,args.steps)
