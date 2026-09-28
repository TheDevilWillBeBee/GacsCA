"""Independent descriptor/scalar and retained-state audit of compact GPU periods."""
import argparse
import hashlib
import json
from pathlib import Path
import time
import numpy as np
from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_core as c
from gacsca.fixed_rule import compact16_holder_projected as r, compact16_holder_program as p
from gacsca.fixed_rule import compact16_holder_records as q, compact16_holder_packed as packed
from gacsca.fixed_rule import compact16_holder_resident_period as resident
from experiments.fixed_rule.audit_small_holder_position_events import sha


def check_boundary(bank, sparse, counts, right, left, expected):
    n = len(expected); g = p.layout()
    assert bank.shape == (n, g.memory_count+5), 'incomplete Data bank'
    wanted = np.array([f.encode_cell(r.lift(cell)) for cell in expected], dtype=np.uint64)
    np.testing.assert_array_equal(bank[:, list(g.info)], wanted)
    np.testing.assert_array_equal(right, [cell.f1 for cell in expected])
    np.testing.assert_array_equal(left, [cell.f2 for cell in expected])
    assert sparse.shape == (n, resident.SLOTS, packed.WORDS) and counts.shape == (n,)
    fields = [q.COL[name] for name in resident.ACTIVE if name != 'signal']
    for col, count in enumerate(counts):
        assert 0 <= int(count) <= resident.SLOTS
        rows = packed.unpack(sparse[col, :int(count)])
        assert not np.any(rows[:, fields]), 'unconsumed controller/mail'
        addresses = list(map(int, rows[:, q.COL['address']]))
        assert len(set(addresses)) == len(addresses) and all(0 <= a < f.Q for a in addresses)
        actual = {a:int(row[q.COL['signal']]) for a, row in zip(addresses, rows) if row[q.COL['signal']]}
        signals = {a:int(left[col]) << (5-a) for a in range(1, 6)}
        signals.update({a:int(right[col]) << (f.Q-1-a) for a in range(f.Q-5, f.Q)})
        assert actual == {a:v for a,v in signals.items() if v}, 'incomplete raw Signal pattern'
    return n*f.FIELDS


def audit(path):
    path = Path(path); receipt = json.loads(path.read_text())
    assert receipt['passed'] and receipt['periods'] == 2
    assert receipt['descriptor_sha256'] == f.self_description().digest()
    assert receipt['rom_sha256'] == hashlib.sha256(p.base_rom().tobytes()).hexdigest()
    for source, digest in receipt['source_sha256'].items(): assert sha(source) == digest
    artifact = Path(receipt['artifact']); assert sha(artifact) == receipt['artifact_sha256']
    rows = []; descriptor = f.self_description()
    with np.load(artifact, allow_pickle=False) as saved:
        upper = r.cells_from_array(saved['initial_upper']); n = len(upper)
        assert n == receipt['colonies']
        for epoch in range(2):
            expected = []; changed = 0
            for col in range(n):
                neighborhood = tuple(r.lift(upper[(col+j)%n]) for j in f.NEIGHBORHOOD)
                inputs = tuple(word for cell in neighborhood for word in f.encode_cell(cell))
                raw = f.decode_cell(descriptor.evaluate(inputs))
                assert raw == f.local_step(neighborhood), 'scalar/descriptor disagreement'
                cell = r.project(raw); expected.append(cell)
                for offset in f.OFFSETS:
                    for name in ('head', *c.CONTROL):
                        field = f's{offset+2}_{name}'
                        changed += getattr(cell, field) != getattr(upper[col], field)
            checked = check_boundary(saved['boundary_banks'][epoch], saved['boundary_sparse'][epoch],
                                     saved['boundary_counts'][epoch], saved['boundary_right'][epoch],
                                     saved['boundary_left'][epoch], expected)
            if receipt['sustained_upper_arithmetic']:
                center = n//2
                if epoch == 0:
                    assert expected[center+1].s2_head and expected[center+1].s2_phase == c.WRITE
                else:
                    first = r.decode_cell(saved['initial_upper'][center])
                    value = (~(first.s2_value & first.s2_data)) & ((1 << 64)-1)
                    assert expected[center+1].s2_data == value
                    assert expected[center+2].s2_head and expected[center+2].s2_phase == c.FETCH and expected[center+2].s2_pc == 24
                assert changed > 0
            rows.append(dict(period=epoch+1, raw_Info_words_checked=checked, represented_controller_words_changed=changed))
            upper = tuple(expected)
    assert receipt['physical_ticks'] == 2*f.U == receipt['metrics']['physical_ticks']
    return dict(passed=True, execution=str(path), execution_sha256=sha(path), artifact_sha256=sha(artifact),
                periods=rows, sustained_upper_arithmetic=receipt['sustained_upper_arithmetic'],
                scope='Independent saved-state audit, not a second physical trajectory or general backend proof.')


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--execution', action='append', required=True); parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); start = time.perf_counter()
    if args.output.exists(): raise FileExistsError(args.output)
    result = dict(passed=True, cases=[audit(path) for path in args.execution], source_sha256={str(Path(__file__)):sha(__file__)}, seconds=time.perf_counter()-start)
    with args.output.open('x') as stream: stream.write(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__': main()
