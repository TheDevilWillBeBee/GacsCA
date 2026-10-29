"""SP12: EXPLICIT tagged repair-packet prototype, not an active candidate.

Adds four packet-tag bits and a valid bit to SP11. Birth at logical
Address1..5 is allowed only at the voted T_wf clock, with tags Address-1;
retention uses the independently certified cohort module and4Q gate.
General damaged-GF birth/capture and iid reliability remain unproved.
G17 and SP1--SP11 are unchanged.
"""
from contextlib import contextmanager
from dataclasses import asdict
from functools import lru_cache
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import numpy as np
from gacsca import compiler,machine,rule_g
from gacsca.netlist import Compiled
import proposed_sparse_liveness448 as base
import check_fast_mail_proposal as transport
from proposed_sparse import (source_names,reserved_cells,flag_store_cells,
                             info_copies,logical_width,fivefold_fields,work_range,
                             LANE_OFFSETS,FIVE,FRONT,SLOTS)

from proposed_modal_clock import proposed_build
import proposed_cohort_packet as packet


def schema(p):
    return [*base.schema(p),('packet_tag',4),('packet_valid',1)]


def width(p):
    return sum(w for _,w in schema(p))


class CohortPacket448Params(rule_g.ParamsG):
    def fam(self):
        return sys.modules[__name__]


def parameters():
    p = CohortPacket448Params(**asdict(base.parameters()))
    p.check()
    assert (p.Q,p.U,width(p)) == (448,67584,264)
    return p


@lru_cache(None)
def dependency_table(p):
    rows = [dict(row,offsets=list(row['offsets'])) for row in base.dependency_table(p)]
    for row in rows:
        if row['field']=='info':
            row['offsets'] = [j for j in range(-5,6) if j]
    used = {row['address'] for row in rows}
    available = [a for a in range(p.lo,p.hi) if a not in reserved_cells(p) and a not in used]
    extra = [('packet_tag',bit) for bit in range(4)]+[('packet_valid',0)]
    for (field,bit),address in zip(extra,available):
        rows.append(dict(field=field,bit=bit,address=address,offsets=[j for j in range(-5,6) if j]))
    assert len(rows)==width(p)
    assert [(r['field'],r['bit']) for r in rows] == [(f,b) for f,w in schema(p) for b in range(w)]
    return rows


def actual_net(p):
    _,source = base.actual_net(p)
    start = p.courier_ticks()[1]
    assert start//p.R == (p.T_sig-1)//p.R
    old = '        ml = n.AND(ml, n.NOT(f1_new))'
    new = """        protected_flag2_courier = n.AND(
            w_in_range(n, age_now, p.age_code(p.courier_ticks()[1]), p.age_code(p.T_sig-1)+1),
            w_in_range(n, xaddr, 3, p.lo+1))
        ml = n.AND(ml, n.OR(n.NOT(f1_new), protected_flag2_courier))"""
    assert source.count(old) == 1
    source = source.replace(old,new)
    old_wf2 = '    wf2 = n.all([left_end, in_wf, sim_l, n.NOT(f1_new)])'
    new_wf2 = """    repair_age = [at_least(n, [cell[j]["age"][bit] for j in range(-5,6)], 6) for bit in range(p.m)]
    repair_wf = w_in_range(n, repair_age, p.age_code(p.T_wf), p.age_code(p.T_wf + 4*Q - 1) + 1)
    packet_now = packet_build(n, {j:dict(tag=cell[j]['packet_tag'], valid=cell[j]['packet_valid'][0], wf2=cell[j]['wf2'][0]) for j in range(-5,6)}, repair_wf)
    packet_command = 0
    for packet_A in range(1,6):
        packet_command = n.OR(packet_command, n.AND(w_eq_const(n, addr_now, packet_A), lv(3-packet_A, 'info')))
    packet_birth = n.AND(w_eq_const(n, repair_age, p.age_code(p.T_wf)), packet_command)
    packet_tag = w_mux(n, packet_birth, w_add_const(n, addr_now[:4], 15), packet_now['tag'])
    wf2 = n.OR(packet_birth, packet_now['wf2'])"""
    assert source.count(old_wf2) == 1
    source = source.replace(old_wf2,new_wf2)
    old_outs = "wf1=[wf1], wf2=[wf2])"
    assert source.count(old_outs)==1
    source = source.replace(old_outs,"wf1=[wf1], wf2=[wf2], packet_tag=packet_tag, packet_valid=[wf2])")
    namespace = dict(rule_g.__dict__,maintenance=SimpleNamespace(build=proposed_build()[0]),
                     schema=schema,packet_build=packet.build,
                     OFFSETS=tuple(range(-12,13)),sparse_controls=transport.sparse_controls,
                     sparse_table=dependency_table(p))
    exec(compile(source,'<SP12 tagged source; explicit rule and schema change>', 'exec'),namespace)
    return namespace['build'](p),source


@lru_cache(None)
def cached(p):
    net,_ = actual_net(p)
    profile = {(row['field'],row['bit']):set(row['offsets']) for row in dependency_table(p)}
    live = set(net.live_nodes())
    for key,node in net.input_node.items():
        if key[0] == 'x' and node in live:
            _,offset,field,bit = key
            assert offset == 0 or offset in profile[field,bit],key
    return net,Compiled(net)


def layout(p):
    return np.array([row['address'] for row in dependency_table(p)],dtype=np.int64)


def sparse_locations(p,comp,supplied_layout):
    assert comp is cached(p)[1] and np.array_equal(supplied_layout,layout(p))
    rows = {(row['field'],row['bit']):row for row in dependency_table(p)}
    codes = {name:index for index,name in enumerate(source_names(p))}
    live = set(comp.outputs.values())
    for _,a,b in comp.gates:
        live.update((a,b))
    locations = {}
    for key,node in comp.index.items():
        if key[0] != 'x' or node not in live:
            continue
        _,offset,field,bit = key
        row = rows[field,bit]
        code = codes['info',0] if offset == 0 else codes['ln',row['offsets'].index(offset)]
        locations[node] = row['address'],code
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
    return dict(proposal='SP12',proposed_rule_change=True,active_G17_modified=False,SP5_modified=False,SP6_modified=False,SP7_modified=False,SP8_modified=False,SP9_modified=False,SP10_modified=False,SP11_modified=False,
                Q=p.Q,U=p.U,width=width(p),radius=12,proposed_netlist_sha256=cached(p)[1].digest)


def load_artifact(path=None):
    p = parameters()
    if path is None:
        path = ROOT/'figs/robustness/SP12_program.npz'
    with np.load(path,allow_pickle=False) as artifact:
        rom,saved_layout = artifact['rom'],artifact['layout']
    assert np.array_equal(saved_layout,layout(p))
    return machine.Candidate(p,rom,saved_layout)
