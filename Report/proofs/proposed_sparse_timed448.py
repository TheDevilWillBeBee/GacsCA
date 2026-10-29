"""SP13: EXPLICIT timed-source and birth-guard prototype.

Add an eleven-bit packet counter to SP12, retaining Q448/U67584. Use the
J81 timed cohort. Suppress birth whenever any three-vote tagged/counter
cohort exists, including one whose translated tag is outside the packet.
General GF/NF2 islands, authentic damaged-input birth and iid unproved.
G17 and SP1--SP12 are unchanged.
"""
from contextlib import contextmanager
from dataclasses import asdict
from functools import lru_cache
import inspect
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
import proposed_timed_cohort_packet as packet


def schema(p):
    return [*base.schema(p),('packet_tag',4),('packet_valid',1),('packet_count',11)]


def width(p):
    return sum(w for _,w in schema(p))


class TimedPacket448Params(rule_g.ParamsG):
    def fam(self):
        return sys.modules[__name__]


def parameters():
    p = TimedPacket448Params(**asdict(base.parameters()))
    p.check()
    assert (p.Q,p.U,width(p)) == (448,67584,275)
    return p


@lru_cache(None)
def dependency_table(p):
    rows = [dict(row,offsets=list(row['offsets'])) for row in base.dependency_table(p)]
    for row in rows:
        if row['field']=='info':
            row['offsets'] = [j for j in range(-5,6) if j]
    used = {row['address'] for row in rows}
    available = [a for a in range(p.lo,p.hi) if a not in reserved_cells(p) and a not in used]
    extra = [('packet_tag',bit) for bit in range(4)]+[('packet_valid',0)]+[('packet_count',bit) for bit in range(11)]
    for (field,bit),address in zip(extra,available):
        rows.append(dict(field=field,bit=bit,address=address,offsets=[j for j in range(-5,6) if j]))
    assert len(rows)==width(p)
    assert [(r['field'],r['bit']) for r in rows] == [(f,b) for f,w in schema(p) for b in range(w)]
    return rows


@lru_cache(None)
def timed_build_with_witness():
    source = inspect.getsource(packet.build)
    old = '    return dict(valid=valid,wf2=valid,'
    new = '    return dict(cohort_exists=exists,valid=valid,wf2=valid,'
    assert source.count(old)==1
    source = source.replace(old,new)
    namespace = dict(packet.__dict__)
    exec(compile(source,'<SP13 exposes timed cohort witness; field equations unchanged>','exec'),namespace)
    return namespace['build'],source


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
    packet_now = packet_build(n, {j:dict(tag=cell[j]['packet_tag'], valid=cell[j]['packet_valid'][0], wf2=cell[j]['wf2'][0], count=cell[j]['packet_count']) for j in range(-5,6)})
    packet_command = 0
    for packet_A in range(1,6):
        packet_command = n.OR(packet_command, n.AND(w_eq_const(n, addr_now, packet_A), lv(3-packet_A, 'info')))
    packet_birth = n.all([w_eq_const(n, repair_age, p.age_code(p.T_wf)), packet_command, n.NOT(packet_now['cohort_exists'])])
    packet_tag = w_mux(n, packet_birth, w_add_const(n, addr_now[:4], 15), packet_now['tag'])
    packet_count = w_mux(n, packet_birth, [0]*11, packet_now['count'])
    wf2 = n.OR(packet_birth, packet_now['wf2'])"""
    assert source.count(old_wf2) == 1
    source = source.replace(old_wf2,new_wf2)
    old_outs = "wf1=[wf1], wf2=[wf2])"
    assert source.count(old_outs)==1
    source = source.replace(old_outs,"wf1=[wf1], wf2=[wf2], packet_tag=packet_tag, packet_valid=[wf2], packet_count=packet_count)")
    namespace = dict(rule_g.__dict__,maintenance=SimpleNamespace(build=proposed_build()[0]),
                     schema=schema,packet_build=timed_build_with_witness()[0],
                     OFFSETS=tuple(range(-12,13)),sparse_controls=transport.sparse_controls,
                     sparse_table=dependency_table(p))
    exec(compile(source,'<SP13 timed guarded source; explicit rule and schema change>', 'exec'),namespace)
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
    return dict(proposal='SP13',proposed_rule_change=True,active_G17_modified=False,SP5_modified=False,SP6_modified=False,SP7_modified=False,SP8_modified=False,SP9_modified=False,SP10_modified=False,SP11_modified=False,SP12_modified=False,
                Q=p.Q,U=p.U,width=width(p),radius=12,proposed_netlist_sha256=cached(p)[1].digest)


def load_artifact(path=None):
    p = parameters()
    if path is None:
        path = ROOT/'figs/robustness/SP13_program.npz'
    with np.load(path,allow_pickle=False) as artifact:
        rom,saved_layout = artifact['rom'],artifact['layout']
    assert np.array_equal(saved_layout,layout(p))
    return machine.Candidate(p,rom,saved_layout)
