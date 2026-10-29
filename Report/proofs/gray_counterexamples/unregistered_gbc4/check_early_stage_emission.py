"""Exact prepared execution of GBC1's issued early stage-correction path.

No whole physical period/own beta/Gray theorem is inferred. Stable banks,
correct lower control and no active wipes are execution premises here.
"""
from dataclasses import asdict
from hashlib import sha256, shake_256
from pathlib import Path
import argparse
import json
import time
import compact_completion_rule as b
from complete_branch_emitter import emit_early_stage_programme


def case_cells(phi, flag1=0, gf_fault=False):
    cells = {}
    for j in b.LANES:
        fields = {f: tuple(int.from_bytes(shake_256(f'GBC1-stage:{phi}:{j}:{f}:{q}'.encode()).digest((w+7)//8), 'little') & ((1 << w)-1)
                           for q in range(5)) for f, w in b.FIELDS}
        cells[j] = b.Cell(addr=(100+j+(37 if gf_fault and j == 0 else 0)) % b.Q,
                          age=(phi-1) % b.U, f1=flag1, **fields)
    return cells


def execute(cells, beta):
    encoded = {j: b.encode_cell(c) for j, c in cells.items()}
    desired = b.encode_cell(b.total_rule(cells, beta))
    native = b.native_at(cells, 0)
    assert 0 <= native['age'] < b.COLLECT
    def tape(address):
        assert 0 <= address < b.Q
        if not b.PRIMARY_START <= address < b.PRIMARY_START+b.FRAME_BITS:
            return 0
        bit = address-b.PRIMARY_START
        return sum(encoded[j][bit] << lane for lane, j in enumerate(b.LANES))
    p, position = b.Packet(p=1), b.PRIMARY_START
    writes, trace = {}, []
    for tick in range(1, 65535):
        position += (1 if p.move == 1 else -1 if p.move == 2 else 0)
        p, bit = b.cpu(p, position, {d: tape(position+d) for d in range(-4, 5)}, beta)
        assert p.mode != b.ERROR, (tick, position, p)
        if bit is not None:
            writes[position] = bit
        trace.append((tick, position, b.pack(p), bit))
        if p.mode == b.HALT:
            break
    else:
        raise AssertionError('specified stage path missed the current late deadline')
    actual = tuple(writes.get(a, 0) for a in range(b.PRIMARY_START, b.PRIMARY_START+b.FRAME_BITS))
    wrong = [i for i, (x, y) in enumerate(zip(actual, desired)) if x != y]
    assert not wrong, (native, wrong[:30])
    assert len(writes) == b.FRAME_BITS
    return {'input_cells': {str(j): asdict(c) for j, c in cells.items()},
            'computed_native': native, 'updates': tick, 'unique_output_columns': len(writes),
            'output_bits': ''.join(map(str, actual)), 'desired_upper_output': asdict(b.total_rule(cells, beta)),
            'trace_sha256': sha256(json.dumps(trace).encode()).hexdigest(), 'wrong_raw_bits': wrong}


def run():
    t0 = time.monotonic()
    beta, listing, bits = emit_early_stage_programme()
    cases = []
    for phi in (0, 1, b.Q+1, b.Q+2, 8*b.Q+2, 16*b.Q-1, 16*b.Q,
                32*b.Q, 32*b.Q+1, 40*b.Q+2, 64*b.Q, 64*b.Q+1, 72*b.Q+2):
        for flag1 in (0, 1):
            cases.append({'phi': phi, 'flag1': flag1, 'gf_fault': False,
                          **execute(case_cells(phi, flag1), beta)})
    cases.append({'phi': b.Q+2, 'flag1': 1, 'gf_fault': True,
                  **execute(case_cells(b.Q+2, 1, True), beta)})
    return {'passed': True, 'scope': 'prepared early computed-Age path; later own stages unfinished',
            'Q': b.Q, 'U': b.U, 'lambda': b.LAMBDA, 'c': b.ERROR_SEPARATION,
            'K': b.FRAME_BITS, 'Head_bits': b.HEAD_BITS,
            'programme_bits': bits, 'instructions': len(listing), 'listing': listing,
            'beta_sha256': sha256(bytes(beta)).hexdigest(), 'cases': cases,
            'maximum_selected_updates': max(c['updates'] for c in cases),
            'full_own_beta': False, 'universal_full_deadline': False,
            'physical_period': False, 'gray_refutation': False, 'iid_failure': False,
            'shorter_U': False, 'elapsed_seconds': time.monotonic()-t0}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    r = run()
    args.output.write_text(json.dumps(r, indent=2)+'\n')
    print(json.dumps({k: v for k, v in r.items() if k not in ('listing', 'cases')}, indent=2))
