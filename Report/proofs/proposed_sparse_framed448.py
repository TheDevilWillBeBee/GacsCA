"""SP14: EXPLICIT framed-service prototype, separate from every earlier CA.

Wire J87's minimum-counter packet and 21-bit coded flag into SP13's
own-program framework, at Q448/U67584/W296. Birth still uses the existing
canonical command/clock plus cohort guard. Authentic damaged-input birth,
autonomous right boundary, full upper map and iid threshold are unproved.
G17 and SP1--SP13 are unchanged.
"""
from contextlib import contextmanager
from dataclasses import asdict
from functools import lru_cache
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from gacsca import compiler, machine, rule_g
from gacsca.netlist import Compiled
import check_fast_mail_proposal as transport
import proposed_sparse_timed448 as previous
import proposed_framed_service as service
from proposed_sparse import (source_names, reserved_cells, flag_store_cells,
                             info_copies, logical_width, fivefold_fields,
                             work_range, LANE_OFFSETS, FIVE, FRONT, SLOTS)

proposed_build = service.maintenance_build


def schema(p):
    return [*previous.schema(p), ('service_valid', 1),
            ('service_position', 9), ('service_count', 11)]


def width(p):
    return sum(w for _, w in schema(p))


class Framed448Params(rule_g.ParamsG):
    def fam(self):
        return sys.modules[__name__]


def parameters():
    p = Framed448Params(**asdict(previous.parameters()))
    p.check()
    assert (p.Q, p.U, width(p)) == (448, 67584, 296)
    return p


@lru_cache(None)
def dependency_table(p):
    rows = [dict(row, offsets=list(row['offsets'])) for row in previous.dependency_table(p)]
    used = {row['address'] for row in rows}
    available = [a for a in range(p.lo, p.hi) if a not in reserved_cells(p) and a not in used]
    extra = [('service_valid', 0)] + [('service_position', bit) for bit in range(9)] + [('service_count', bit) for bit in range(11)]
    assert len(available) >= len(extra)
    for (field, bit), address in zip(extra, available):
        rows.append(dict(field=field, bit=bit, address=address,
                         offsets=[j for j in range(-5, 6) if j]))
    assert len(rows) == width(p)
    assert [(r['field'], r['bit']) for r in rows] == [(f, b) for f, w in schema(p) for b in range(w)]
    return rows


def actual_net(p):
    _, source = previous.actual_net(p)
    marker = '    # ------------------------------------------------------------ local structure\n'
    insert = """    service_now = service_build(n, {j:dict(
        packet_tag=cell[j]['packet_tag'], packet_valid=cell[j]['packet_valid'][0],
        packet_count=cell[j]['packet_count'], wf2=cell[j]['wf2'][0],
        flag_valid=cell[j]['service_valid'][0], flag_position=cell[j]['service_position'],
        flag_count=cell[j]['service_count']) for j in range(-5,6)})
"""
    assert source.count(marker) == 1
    source = source.replace(marker, marker + insert)
    old = '        **(dict(Q=Q, nb=p.nb, radix=p.R, pos_bits=p.PB) if p.exact else {}))'
    new = '        service_force=service_now[\'service_force\'],\n' + old
    assert source.count(old) == 1
    source = source.replace(old, new)
    old = "    packet_now = packet_build(n, {j:dict(tag=cell[j]['packet_tag'], valid=cell[j]['packet_valid'][0], wf2=cell[j]['wf2'][0], count=cell[j]['packet_count']) for j in range(-5,6)})"
    new = "    packet_now = dict(tag=service_now['packet_tag'], valid=service_now['packet_valid'], wf2=service_now['wf2'], count=service_now['packet_count'], cohort_exists=service_now['packet_any_cohort'])"
    assert source.count(old) == 1
    source = source.replace(old, new)
    old = 'packet_valid=[wf2], packet_count=packet_count)'
    new = "packet_valid=[wf2], packet_count=packet_count, service_valid=[service_now['flag_valid']], service_position=service_now['flag_position'], service_count=service_now['flag_count'])"
    assert source.count(old) == 1
    source = source.replace(old, new)
    namespace = dict(rule_g.__dict__, maintenance=SimpleNamespace(build=proposed_build()[0]),
                     schema=schema, service_build=service.build,
                     OFFSETS=tuple(range(-12, 13)), sparse_controls=transport.sparse_controls,
                     sparse_table=dependency_table(p))
    exec(compile(source, '<SP14 explicit framed service and state change>', 'exec'), namespace)
    return namespace['build'](p), source


@lru_cache(None)
def cached(p):
    net, _ = actual_net(p)
    profile = {(row['field'], row['bit']): set(row['offsets']) for row in dependency_table(p)}
    live = set(net.live_nodes())
    for key, node in net.input_node.items():
        if key[0] == 'x' and node in live:
            _, offset, field, bit = key
            assert offset == 0 or offset in profile[field, bit], key
    return net, Compiled(net)


def layout(p):
    return np.array([row['address'] for row in dependency_table(p)], dtype=np.int64)


def sparse_locations(p, comp, supplied_layout):
    assert comp is cached(p)[1] and np.array_equal(supplied_layout, layout(p))
    rows = {(row['field'], row['bit']): row for row in dependency_table(p)}
    codes = {name: index for index, name in enumerate(source_names(p))}
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
    compiler.lane_locations = sparse_locations
    try:
        yield
    finally:
        compiler.lane_locations = original


def identity(p):
    return dict(proposal='SP14', proposed_rule_change=True, active_G17_modified=False,
                SP13_modified=False, Q=p.Q, U=p.U, width=width(p), radius=12,
                proposed_netlist_sha256=cached(p)[1].digest)


def load_artifact(path=None):
    p = parameters()
    if path is None:
        path = ROOT / 'figs/robustness/SP14_program.npz'
    with np.load(path, allow_pickle=False) as artifact:
        rom, saved_layout = artifact['rom'], artifact['layout']
    assert np.array_equal(saved_layout, layout(p))
    return machine.Candidate(p, rom, saved_layout)
