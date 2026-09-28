"""Host initialization and diagnostic selection of a sustained active fixture.

The preflight is upper-state diagnosis, not a physical hierarchy execution.
"""
import argparse
import hashlib
import json
from pathlib import Path
import random
from gacsca.fixed_rule import compact16_holder_core as c, compact16_holder_rule as f
from gacsca.fixed_rule import compact16_holder_projected as r, compact16_holder_initial as initial


def parents(n=31):
    if type(n) is not int or not 31 <= n <= 63 or n % 2 == 0:
        raise ValueError('odd diagnostic ring of 31 to 63 upper cells required')
    rng = random.Random(2026092771)
    data = [rng.getrandbits(64) for _ in range(n)]
    center = n//2
    def logical(position):
        at = position % n
        values = dict(r.record(at), address=at, age=c.RESET_AGES[4]+100,
                      data=data[at], f2=1)
        if at == center:
            values.update(head=1, phase=c.READ_B, pc=23, rb=at, rd=at+1,
                          value=0x123456789abcdef0, alu=c.NAND)
        return c.Cell(**values)
    return tuple(initial.coherent_cell(logical, at) for at in range(n))


def preflight(n=31):
    before = parents(n)
    def diagnostic_step(cells):
        return tuple(r.local_step(tuple(cells[(at+j)%n] for j in f.NEIGHBORHOOD)) for at in range(n))
    first = diagnostic_step(before)
    second = diagnostic_step(first)
    center = n//2
    value = (~(before[center].s2_value & before[center].s2_data)) & ((1 << 64)-1)
    assert first[center+1].s2_head == 1 and first[center+1].s2_phase == c.WRITE
    assert first[center+1].s2_value == value and first[center+1].s2_pc == 23
    assert second[center+1].s2_data == value
    assert second[center+2].s2_head == 1 and second[center+2].s2_phase == c.FETCH
    assert second[center+2].s2_pc == 24
    return dict(passed=True, upper_cells=n, lower_sites=n*f.Q,
                diagnostic_upper_steps=2, head_positions=[center, center+1, center+2],
                phases=[c.READ_B, c.WRITE, c.FETCH], computed_WRITE_value=value,
                physical_periods_executed=0,
                scope='Fixture initialization and diagnostic upper-step preflight only; '
                      'the larger compact physical run remains to be executed.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    result = preflight()
    result.update(descriptor_sha256=f.self_description().digest(),
                  source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    with args.output.open('x') as stream:
        stream.write(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
