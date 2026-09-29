"""Conditional spatial dependence of the actual fixed-ROM noiseless prefix.

Diagnostic abstract interpretation of already certified timed memory events.
Never an evolution backend. Physical refinement and flag clearing remain explicit
premises, loaded from the existing whole-period composition.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time

from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_core as c
from gacsca.fixed_rule import retimed_holder_program as p
from experiments.fixed_rule import compose_retimed_holder_noiseless_period as composition
from experiments.fixed_rule import certify_retimed_holder_timed_dataflow as timed
from experiments.fixed_rule.run_retimed_holder_streamed_repair import sha


EMPTY = frozenset()
LOCAL = frozenset((0,))


def delivered_support(source, hops, direction):
    """Translate source-relative owners into destination-relative owners."""
    assert 0 <= hops <= 7 and direction in (c.LEFT, c.RIGHT)
    displacement = -hops if direction == c.LEFT else hops
    return frozenset(owner-displacement for owner in source)


def bounded(owners):
    assert owners <= frozenset(range(-7, 8)), ('dependence escapes seven colonies', sorted(owners))
    return owners


def field_partition():
    groups = dict(fixed_geometry=[], procedure=[], flags_and_forcing=[], signal=[])
    for name, _ in f.SCHEMA:
        if name.startswith('p') or name in ('address', 'age'):
            groups['fixed_geometry'].append(name)
        elif name.startswith('s') and name != 'signal':
            assert name.split('_', 1)[1] in dict(f.PROCEDURE)
            groups['procedure'].append(name)
        elif name in ('f1', 'f2') or name.startswith('w'):
            groups['flags_and_forcing'].append(name)
        elif name == 'signal':
            groups['signal'].append(name)
        else:
            raise AssertionError(('unaccounted raw field', name))
    assert sum(map(len, groups.values())) == f.FIELDS
    assert len(groups['procedure']) == 5 * len(f.PROCEDURE)
    return groups


def analyze(schedule, *, layout=None):
    g = p.layout() if layout is None else layout
    assert g.memory_count == p.layout().memory_count
    rom = p.base_rom()
    memory = [LOCAL if a < g.memory_count or a >= f.Q-5 else EMPTY for a in range(f.Q)]
    all_seen = LOCAL
    observations = []
    phase_order = ('gather_0', 'gather_1', 'gather_2', 'third_evaluation',
                   'precommit_halt', 'final_evaluation')
    phases = {row['name']: row for row in schedule['phases']}

    def write(address, support):
        nonlocal all_seen
        assert address < g.memory_count or f.Q-5 <= address < f.Q
        memory[address] = bounded(support)
        all_seen |= support

    def reset(stage):
        for address in range(f.Q):
            row = rom[address] if address < len(rom) else tuple(c.fallback(address, i) for i in range(7))
            if row[5] or (row[0] == c.MEM and (int(row[2]) >> stage) & 1):
                write(address, EMPTY)

    def vote():
        for address in g.votes:
            write(address, memory[address-1] | memory[address+1] | memory[address+2])

    for name in phase_order:
        phase = phases[name]
        if name.startswith('gather_'):
            reset(int(name[-1]))
        elif name == 'third_evaluation':
            vote()
        elif name == 'precommit_halt':
            reset(3)
        elif name == 'final_evaluation':
            reset(4)
            vote()
        events, _ = timed.events(phase, g)
        left = value = query = None
        controller = EMPTY
        packets = {}
        deliveries = 0
        for tick, _, pc, kind in events:
            op = g.instructions[pc]
            if kind == 'read_a':
                left = memory[op.a]
                controller |= left
            elif kind == 'read_b':
                assert left is not None
                value = left | memory[op.b]
                controller |= value
            elif kind == 'write_alu':
                assert value is not None
                write(op.d, value)
            elif kind == 'literal':
                write(op.d, EMPTY)
            elif kind == 'load':
                query = memory[op.a]
                controller |= query
            elif kind == 'metadata':
                assert query is not None
                # ROM is fixed; all data-dependent query and timing/control
                # state is conservatively attributed to the entire query.
                write(op.a, query)
            elif kind == 'send':
                assert pc not in packets
                packets[pc] = memory[op.a]
                controller |= packets[pc]
            elif kind == 'deliver':
                hops, direction = op.d >> 1, op.d & 1
                write(op.b, delivered_support(packets.pop(pc), hops, direction))
                deliveries += 1
            else:
                raise AssertionError(kind)
            bounded(controller)
        assert not packets
        assert all(memory[a] <= LOCAL for a in g.info), 'Info ceases to be local before commit'
        if name in ('precommit_halt', 'final_evaluation'):
            assert not phase['packets'], 'mail after forcing cannot be omitted'
        observations.append(dict(name=name, timed_events=len(events), deliveries=deliveries,
                                 controller_owner_offsets=sorted(controller),
                                 bank_owner_offsets=sorted(frozenset().union(*memory))))
    # All 154 represented words and every arbitrary initial scratch word were
    # included. We use unions (even for majority) and never assume equal inputs.
    assert set(g.info).isdisjoint(g.hold)
    return dict(passed=True, phases=observations, raw_field_partition=field_partition(),
                all_bank_addresses_checked=f.Q, initial_arbitrary_MEM_words=g.memory_count+5,
                initial_nonMEM_Data_zero=True, initial_Signals_zero_required=True,
                logical_owner_offsets=sorted(all_seen),
                complete_raw_colony_owner_offsets=list(range(-8, 9)),
                replica_offsets=list(f.OFFSETS),
                late_interval=[f.WF_END+f.Q, f.U-1],
                assumptions=['noiseless canonical entry relation E with all initial Signals zero',
                             'fixed ROM and coherent procedure copies',
                             'certified instruction and packet refinement',
                             'payload-independent completed instruction schedule',
                             'canonical context factorization and flag clearing'],
                conclusion='At every late precommit physical time, each complete logical '
                           'procedure and Signal depends only on initial banks within '
                           'seven colonies. Every complete raw colony depends within '
                           'eight, accounting for replicas. Geometry is fixed; flags/Wf '
                           'are zero in the stated late interval.',
                limitation='Conditional diagnostic proof composition, not a new physical '
                           'prefix run or proof for a faulty prefix. Does not establish '
                           'a persistent cut after the later burst.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    out = Path(parser.parse_args().output)
    if out.exists():
        raise FileExistsError(out)
    start = time.perf_counter()
    loaded = composition.load_inputs()
    interfaces = composition.interfaces(loaded)
    assert interfaces['flags_zero_before_final_evaluation']
    result = analyze(loaded['schedule'])
    sources = (Path(__file__), Path(composition.__file__), Path(timed.__file__),
               Path(p.__file__), Path(f.__file__), Path(c.__file__))
    result.update(descriptor_sha256=f.self_description().digest(),
                  ROM_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest(),
                  source_sha256={str(path): sha(path) for path in sources},
                  input_sha256={str(Path('figs/fixed_rule')/name): sha(Path('figs/fixed_rule')/name)
                                for name in composition.SOURCES.values()},
                  seconds=time.perf_counter()-start,
                  host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
