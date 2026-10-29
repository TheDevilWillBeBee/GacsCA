#!/usr/bin/env python3
"""Actual-gate/source support for SP4's post-gather protected-colony proof.

This certifies local dependencies, legal front ranges and courier paths.
The first-failure and unbounded trajectory argument is in ROBUSTNESS.md.
No arbitrary upper command or iid-reliability theorem is certified here.
"""
import hashlib
import inspect
import json
from pathlib import Path
import sys
from types import FunctionType

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from gacsca import rule_g
from gacsca.netlist import Net, Compiled, w_add_const_mod
from gacsca.rule import front_timing_dwell
import proposed_sparse_prefix448 as proposed
import prefix_selection as selection
import check_fast_mail_proposal as transport


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ancestors(net, node):
    visited = {node}
    stack = [node]
    while stack:
        current = stack.pop()
        edge = net.gate[current]
        if edge is None:
            continue
        for parent in edge[1:]:
            if parent not in visited:
                visited.add(parent)
                stack.append(parent)
    return {name for name, inp in net.input_node.items() if inp in visited}


def main():
    candidate = proposed.load_artifact()
    p = candidate.p
    out = ROOT / 'figs/robustness'
    net, comp = proposed.cached(p)
    assert comp.digest == candidate.comp.digest
    keys = ('laddr', 'psel', 'arrive')
    fields = ('reg', 'pend', 'pkind', 'pval', 'hold', 'scr')
    independent = []
    for name, node in net.outputs.items():
        if name[0] in keys or name[:1] == ('y',) and name[1] in fields:
            inputs = ancestors(net, node)
            assert not any(inp[0] == 'x' and inp[2] in ('mr', 'ml') for inp in inputs), name
            independent.append(name)
    assert len(independent) > 100
    radius = max(abs(name[1]) for name in comp.inputs if name[0] == 'x')
    assert radius == 12
    namespace = dict(transport.__dict__, proposed_maintenance=selection.proposed_build)
    factory = FunctionType(transport.concrete_sparse_net.__code__, namespace)
    actual, source = factory(p, proposed.dependency_table(p))
    assert Compiled(actual).digest == comp.digest
    assert p.mux_front and not p.sel_front and p.compact_front and p.computed_front
    body = inspect.getsource(rule_g._mux_front)
    assert body.count("new['reg'][i] = n.AND(any_arrive,") == 1
    assert body.count('kind_lines = [n.AND(inside, x) for x in kind_lines]') == 1
    assert 'ln[d] = ([lv(d, \'info\'), lv(d, \'hold\')]' in body
    assert "lv(d, 'h1', i)" in body and "lv(d, 'scr', i)" in body
    assert "'mr'" not in body and "'ml'" not in body
    # Evaluate actual arrival gates over every legal position/direction/
    # holder Address. Arrival is independent of raw register words.
    timing = Net()
    addr = [timing.input(('addr', bit)) for bit in range(p.k)]
    age = [timing.input(('age', bit)) for bit in range(p.m)]
    regs = {j: [timing.input(('reg', j, bit)) for bit in range(p.L)] for j in (-1, 0, 1)}
    for slot in proposed.SLOTS:
        xa = w_add_const_mod(timing, addr, slot % p.Q, p.Q)
        cell = dict(addr=xa, age=age, reg=regs[0])
        pseudo = {j: dict(reg=regs[j]) for j in (-1, 1)}
        pseudo[0] = cell
        _, _, arrive, _ = front_timing_dwell(timing, p, cell, pseudo)
        assert all(inp[0] != 'reg' for inp in ancestors(timing, arrive))
        timing.set_output(('arrive', slot), arrive)
    arrival = Compiled(timing)
    cases = 2*p.R*p.Q
    active_addresses = set()
    for begin in range(0, cases, 4096):
        number = np.arange(begin, min(cases, begin+4096), dtype=np.uint32)
        A = number % p.Q
        position = (number//p.Q) % p.R
        direction = number//(p.Q*p.R)
        packed_age = ((p.E0b+direction) << p.PB) | position
        values = {('addr', i): ((A >> i) & 1).astype(bool) for i in range(p.k)}
        values.update({('age', i): ((packed_age >> i) & 1).astype(bool) for i in range(p.m)})
        values.update({('reg', j, i): np.zeros(len(number), dtype=bool)
                       for j in (-1, 0, 1) for i in range(p.L)})
        got = arrival.evaluate(values, bool)
        for slot in proposed.SLOTS:
            expected = ((A.astype(np.int64)+slot) % p.Q)
            base = np.where(direction, p.hi-1-position.astype(np.int64), p.lo-p.H+position)
            allowed = np.isin(expected-base, np.arange(p.fronts)*p.delta)
            assert np.array_equal(got['arrive', slot], allowed)
            active_addresses.update(A[allowed].tolist())
    assert active_addresses == set(range(36, 412))
    frame = (min(active_addresses), max(active_addresses))
    support = (frame[0]-radius, frame[1]+radius)
    assert support == (24, 423) and 0 < support[0] < support[1] < p.Q-1
    table = proposed.dependency_table(p)
    last_capture = max(g*p.Q+abs(offset)*(p.Q//8)+1
                       for g in p.gathers_q for row in table for offset in row['offsets'])
    assert last_capture == 9633
    _, left_tick, right_tick = p.courier_ticks()
    paths = []
    for field, origin, target, tick in (('mr', p.hi-1, p.Q-3, right_tick),
                                        ('ml', p.lo, 3, left_tick)):
        distance = abs(origin-target)
        assert tick+1+distance == p.T_sig
        assert last_capture+1 < tick < p.T_sig < p.T_wf
        assert all(not g*p.Q+1 <= t < g*p.Q+12*(p.Q//8)+1
                   for g in p.gathers_q for t in range(tick, p.T_sig+1))
        holders = (min(origin, target)-2, max(origin, target)+2)
        assert 0 <= holders[0] <= holders[1] < p.Q
        paths.append(dict(field=field, origin=origin, target=target, load_input_tick=tick,
                          signal_input_tick=p.T_sig, source_copy_holder_range=holders,
                          unit_speed=True))
    barrier = json.loads((out / 'SP4_barrier_certificate.json').read_text())
    assert barrier['full_generated_source_sha256'] == hashlib.sha256(source.encode()).hexdigest()
    receipt = dict(
        proposal='SP4', proposed_rule_change=True, active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)), checker_sha256=digest(Path(__file__)),
        helpers_sha256=digest(ROOT / 'gacsca/netlist.py'), timing_sha256=digest(ROOT / 'gacsca/rule.py'),
        full_rule_sha256=digest(ROOT / 'gacsca/rule_g.py'),
        selection_source_sha256=digest(ROOT / 'Report/proofs/prefix_selection.py'),
        transport_checker_sha256=digest(ROOT / 'Report/proofs/check_fast_mail_proposal.py'),
        full_generated_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        front_step_source_sha256=hashlib.sha256(body.encode()).hexdigest(),
        outputs_independent_of_current_Mail=independent,
        legal_position_direction_Address_cases=cases, arrival_independent_of_raw_registers=True,
        active_register_holder_frame=frame, conservative_full_input_frame=support,
        radius=radius, copy_holder_offsets=[-2, 2],
        last_capture_input_tick=last_capture, post_gather_core_begin=last_capture+2,
        zero_flag_courier_paths=paths,
        raw_geometry_repair_updates_after_core=420,
        first_period_latest_core=p.U-1,
        maximum_geometry_repair_after_first_boundary=419,
        barrier_receipt_sha256=digest(out / 'SP4_barrier_certificate.json'),
        maintenance_receipt_sha256=digest(out / 'SP4_maintenance_certificate.json'),
        symbolic_schedule_receipt_sha256=digest(out / 'SP4_symbolic_schedule.json'),
        front_receipt_sha256=digest(out / 'SP4_front_certificate.json'),
        build_receipt_sha256=digest(out / 'SP4_program_build.json'),
        global_reliability_established=False,
        scope='local dependencies and legal-clock support for post-gather protected-colony induction; '
              'unbounded proof separate; no arbitrary upper commands or iid theorem')
    (out / 'SP4_autonomy_certificate.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(dict(independent_outputs=len(independent), legal_arrival_cases=cases,
                          register_holder_frame=frame, full_input_frame=support,
                          zero_flag_courier_paths=paths)), flush=True)


if __name__ == '__main__':
    main()
