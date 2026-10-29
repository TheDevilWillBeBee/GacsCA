"""SP15: EXPLICIT guard6/packet-pressure/history12 proposed rule change.

G17, SP14 and all registered candidates remain unchanged. Q448/U67584
are retained for a first own-program build attempt, not a fitting claim.
Twenty extra h1/h2 copy bits implement twelve sparse history ranks.
Authentic source delivery, autonomous boundary and iid reliability remain
unproved. See ROBUSTNESS J99/J100 once their certificates are completed.
"""
from contextlib import contextmanager
from dataclasses import asdict
from functools import lru_cache
from pathlib import Path
import sys
from types import FunctionType, SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from gacsca import compiler, machine, rule_g
from gacsca.netlist import Compiled
import check_fast_mail_proposal as transport
import proposed_sparse_framed448 as previous
import proposed_packet_pressure as service
import proposed_packet_guard6 as guard
from proposed_sparse import (reserved_cells, flag_store_cells, info_copies,
    fivefold_fields, work_range, FIVE, FRONT, SLOTS)

LANE_OFFSETS = (*range(-6, 0), *range(1, 7))
logical_width = FunctionType(rule_g.logical_width.__code__,
    dict(rule_g.__dict__, LANE_OFFSETS=LANE_OFFSETS))
source_names = FunctionType(rule_g.source_names.__code__,
    dict(rule_g.__dict__, LANE_OFFSETS=LANE_OFFSETS))
base_schema = FunctionType(rule_g.schema.__code__,
    dict(rule_g.__dict__, logical_width=logical_width))
proposed_build = previous.proposed_build


def schema(p):
    return [*base_schema(p), ('packet_tag', 4), ('packet_valid', 1),
        ('packet_count', 11), ('service_valid', 1),
        ('service_position', 9), ('service_count', 11)]


def width(p):
    return sum(w for _, w in schema(p))


class GuardedPressure448Params(rule_g.ParamsG):
    def fam(self):
        return sys.modules[__name__]

    @property
    def n_sources(self):
        return self.L + 2 + len(LANE_OFFSETS) + self.S + 2

    def capture_age(self, off, g=0):
        # These are sparse rank dependencies, captured by speed-eight
        # mail; the inherited dense speed-one check is inapplicable.
        assert not any(self.skew)
        return self.gathers_q[g]*self.Q + abs(off)*(self.Q//8) + 1

    def check(self):
        return FunctionType(rule_g.ParamsG.check.__code__,
            dict(rule_g.__dict__, LANE_OFFSETS=LANE_OFFSETS))(self)


def parameters():
    values = asdict(previous.parameters())
    values['skew'] = (0,)*len(LANE_OFFSETS)
    # A longer compiler drain completed the programme, but its early
    # flags required NPe43. NPe44 supplies the mandatory spare early
    # pass; the old NP128 and MP67 still fit the same U67584.
    values['NPe'] = 44
    p = GuardedPressure448Params(**values)
    p.check()
    assert (p.Q, p.U, width(p)) == (448, 67584, 316)
    assert len(source_names(p)) == p.n_sources and p.SB == 7
    return p


@lru_cache(None)
def dependency_table(p):
    old = {(row['field'], row['bit']): row['offsets']
        for row in previous.dependency_table(previous.parameters())}
    addresses = [a for a in range(p.lo, p.hi) if a not in reserved_cells(p)]
    rows = []
    for field, w in schema(p):
        for bit in range(w):
            if field in ('h1', 'h2'):
                # All five-copy history inputs lie within four cells;
                # the live-input check below verifies this overapproximation.
                offsets = [j for j in range(-4, 5) if j]
            elif field in ('wf2', 'packet_valid', 'packet_tag', 'packet_count'):
                offsets = list(LANE_OFFSETS)
            else:
                offsets = list(old[field, bit])
            rows.append(dict(field=field, bit=bit, address=addresses[len(rows)], offsets=offsets))
    assert len(rows) == width(p) and len(rows) <= len(addresses)
    return rows


def actual_net(p):
    _, source = previous.actual_net(previous.parameters())
    old = "    packet_birth = n.all([w_eq_const(n, repair_age, p.age_code(p.T_wf)), packet_command, n.NOT(packet_now['cohort_exists'])])"
    new = """    packet_guard = packet_guard_build(n, {j:dict(
        packet_tag=cell[j]['packet_tag'], packet_valid=cell[j]['packet_valid'][0],
        packet_count=cell[j]['packet_count'], wf2=cell[j]['wf2'][0]) for j in range(-6,7)})
    packet_birth = n.all([w_eq_const(n, repair_age, p.age_code(p.T_wf)), packet_command, n.NOT(packet_guard)])"""
    assert source.count(old) == 1
    source = source.replace(old, new)
    namespace = dict(rule_g.__dict__, LANE_OFFSETS=LANE_OFFSETS,
        logical_width=logical_width, source_names=source_names, schema=schema,
        maintenance=SimpleNamespace(build=proposed_build()[0]),
        service_build=service.build, packet_guard_build=guard.build,
        OFFSETS=tuple(range(-12, 13)), sparse_controls=transport.sparse_controls,
        sparse_table=dependency_table(p))
    # Front helpers have module globals of their own. Clone them into the
    # same isolated namespace so all lane lengths use twelve ranks.
    for name, fn in rule_g.__dict__.items():
        if isinstance(fn, FunctionType) and fn.__module__ == rule_g.__name__:
            namespace[name] = FunctionType(fn.__code__, namespace, fn.__name__, fn.__defaults__, fn.__closure__)
    namespace.update(logical_width=logical_width, source_names=source_names, schema=schema)
    exec(compile(source, '<SP15 explicit guard6, packet pressure and history12>', 'exec'), namespace)
    return namespace['build'](p), source


@lru_cache(None)
def cached(p):
    net, _ = actual_net(p)
    profile = {(row['field'], row['bit']): set(row['offsets']) for row in dependency_table(p)}
    live = set(net.live_nodes())
    for key, node in net.input_node.items():
        if key[0] == 'x' and node in live:
            _, off, field, bit = key
            assert off == 0 or off in profile[field, bit], key
    return net, Compiled(net)


def layout(p):
    return np.array([row['address'] for row in dependency_table(p)], dtype=np.int64)


def sparse_locations(p, comp, supplied_layout):
    assert comp is cached(p)[1] and np.array_equal(supplied_layout, layout(p))
    rows = {(r['field'], r['bit']): r for r in dependency_table(p)}
    codes = {name: i for i, name in enumerate(source_names(p))}
    live = set(comp.outputs.values())
    for _, a, b in comp.gates:
        live.update((a, b))
    locations = {}
    for key, node in comp.index.items():
        if key[0] != 'x' or node not in live:
            continue
        _, offset, field, bit = key
        row = rows[field, bit]
        code = codes['info', 0] if offset == 0 else codes['ln', row['offsets'].index(offset)]
        locations[node] = row['address'], code
    assert len(set(locations.values())) == len(locations)
    return locations


@contextmanager
def compiler_input_map():
    original = compiler.lane_locations
    original_scheduler = compiler.Scheduler
    # The stock scheduler classifies Ln operands using a fixed ten-lane
    # global. Only this isolated constructor uses the proposed twelve.
    scheduler_globals = dict(compiler.__dict__, lane_locations=sparse_locations, rule=SimpleNamespace(
        **dict(compiler.rule.__dict__, LANE_OFFSETS=LANE_OFFSETS)))
    constructor = FunctionType(original_scheduler.__init__.__code__,
        scheduler_globals, original_scheduler.__init__.__name__,
        original_scheduler.__init__.__defaults__)
    compiler.Scheduler = type('SP15Scheduler', (original_scheduler,), {'__init__': constructor})
    compiler.lane_locations = sparse_locations
    try:
        yield
    finally:
        compiler.lane_locations = original
        compiler.Scheduler = original_scheduler


def identity(p):
    return dict(proposal='SP15', proposed_rule_change=True, active_G17_modified=False,
        SP14_modified=False, Q=p.Q, U=p.U, width=width(p), radius=12,
        proposed_netlist_sha256=cached(p)[1].digest)


def load_artifact(path=None):
    p = parameters()
    if path is None:
        path = ROOT/'figs/robustness/SP15_program.npz'
    with np.load(path, allow_pickle=False) as artifact:
        rom, saved_layout = artifact['rom'], artifact['layout']
    assert np.array_equal(saved_layout, layout(p))
    return machine.Candidate(p, rom, saved_layout)
