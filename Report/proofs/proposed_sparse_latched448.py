"""SP7: EXPLICIT proposal with a protected physical Flag2 command relay.

SP6's Q448/U67584, schema, maintenance and ordinary sparse gathers are kept.
During the56 valid courier clocks, ML at logical Addresses3..58 ignores
Flag1 clearing. Workspace.Flag2 also ignores the computed Flag1 gate.
Workspace.Flag2 retains its own stored bit until the clock window ends.
This supplies a possible persistent physical repair source in a flagged colony;
it is not an eroder or iid theorem. G17 and SP1--SP5 are unchanged.
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
from proposed_sparse import (schema,width,source_names,reserved_cells,flag_store_cells,
                             info_copies,logical_width,fivefold_fields,work_range,
                             LANE_OFFSETS,FIVE,FRONT,SLOTS)

proposed_build = base.proposed_build


class Latched448Params(rule_g.ParamsG):
    def fam(self):
        return sys.modules[__name__]


def parameters():
    p = Latched448Params(**asdict(base.parameters()))
    p.check()
    assert (p.Q,p.U,width(p)) == (448,67584,259)
    return p


@lru_cache(None)
def dependency_table(p):
    # The original envelope is conservative for these changes: all new
    # controls use the same computed Address/Age. cached checks every live
    # x-input of the final circuit against this table rather than assuming it.
    return base.dependency_table(p)


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
    new_wf2 = '    wf2 = n.AND(in_wf, n.OR(n.AND(left_end, sim_l), c["wf2"][0]))'
    assert source.count(old_wf2) == 1
    source = source.replace(old_wf2,new_wf2)
    namespace = dict(rule_g.__dict__,maintenance=SimpleNamespace(build=proposed_build()[0]),
                     OFFSETS=tuple(range(-12,13)),sparse_controls=transport.sparse_controls,
                     sparse_table=dependency_table(p))
    exec(compile(source,'<SP7 protected Flag2 relay; explicit rule change>', 'exec'),namespace)
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
    return dict(proposal='SP7',proposed_rule_change=True,active_G17_modified=False,SP5_modified=False,SP6_modified=False,
                Q=p.Q,U=p.U,width=width(p),radius=12,proposed_netlist_sha256=cached(p)[1].digest)


def load_artifact(path=None):
    p = parameters()
    if path is None:
        path = ROOT/'figs/robustness/SP7_program.npz'
    with np.load(path,allow_pickle=False) as artifact:
        rom,saved_layout = artifact['rom'],artifact['layout']
    assert np.array_equal(saved_layout,layout(p))
    return machine.Candidate(p,rom,saved_layout)
