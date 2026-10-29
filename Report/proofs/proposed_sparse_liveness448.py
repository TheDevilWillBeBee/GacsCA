"""SP5: EXPLICIT changed proposal, restoring Flag2 and left-clock progress.

SP4's Q448/U67584,259-bit schema, sparse transport and compiler are retained.
Maintenance is SP2's guarded radius-eight diagnostic, with its original
Flag2 geometry override, plus J54's left-Age fallback to own stored Age
when the adjusted left Address list has no majority. Neither change is
installed in G17 or SP4. No all-level repair or iid reliability is claimed.
"""
from contextlib import contextmanager
from dataclasses import asdict
from functools import lru_cache
import inspect
from pathlib import Path
import sys
import textwrap
from types import FunctionType

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from gacsca import compiler, machine, maintenance, rule_g
from gacsca.netlist import Compiled
import check_fast_mail_proposal as transport
import check_quiet_majority_proposal as quiet
from check_blank_neighbor_clock import coupled_left_clock
from check_right_barrier import dominant_majority
import proposed_sparse_prefix448 as base
from proposed_sparse import (schema, width, source_names, reserved_cells,
                             flag_store_cells, info_copies, logical_width,
                             fivefold_fields, work_range, LANE_OFFSETS, FIVE, FRONT, SLOTS)


def proposed_build(symbolic=False):
    _, source = quiet.proposed_build()
    build, source = coupled_left_clock(source)
    assert "vote_right = n.AND(exists, n.OR(n.NOT(f1), f2))" in source
    if symbolic:
        namespace = dict(maintenance.__dict__, majority_word=dominant_majority)
        exec(compile(source, '<SP5 maintenance; explicit changed proposal>', 'exec'), namespace)
        build = namespace['build']
    return build, source


class Liveness448Params(rule_g.ParamsG):
    def fam(self):
        return sys.modules[__name__]


def parameters():
    p = Liveness448Params(**asdict(base.parameters()))
    p.check()
    assert (p.Q,p.U,width(p)) == (448,67584,259)
    return p


@lru_cache(None)
def dependency_table(p):
    original = inspect.getsource(transport.sparse_profile_certificate)
    start = original.index("    source = inspect.getsource(rule_g.build)")
    end = original.index("    largest = max(map(len, profile.values()))")
    body = textwrap.dedent(original[start:end])
    definition = "def envelope(p):\n"+textwrap.indent(body,"    ")+"    return profile\n"
    namespace = dict(transport.__dict__, proposed_maintenance=proposed_build)
    exec(compile(definition,'<SP5 dependency envelope>', 'exec'),namespace)
    profile = namespace['envelope'](p)
    assert max(map(len,profile.values())) <= 10
    addresses = [a for a in range(p.lo,p.hi) if a not in reserved_cells(p)]
    assert len(addresses) >= len(profile)
    rows = [dict(field=f,bit=i,address=a,offsets=sorted(offsets))
            for ((f,i),offsets),a in zip(profile.items(),addresses)]
    assert len(rows) == width(p)
    return rows


def actual_net(p):
    namespace = dict(transport.__dict__, proposed_maintenance=proposed_build)
    factory = FunctionType(transport.concrete_sparse_net.__code__, namespace,
                           'SP5_concrete_sparse_net', transport.concrete_sparse_net.__defaults__)
    return factory(p,dependency_table(p))


@lru_cache(None)
def cached(p):
    net, _ = actual_net(p)
    profile = {(row['field'],row['bit']):set(row['offsets']) for row in dependency_table(p)}
    live = set(net.live_nodes())
    for name,node in net.input_node.items():
        if name[0] == 'x' and node in live:
            _,offset,field,bit = name
            assert offset == 0 or offset in profile[field,bit],name
    return net,Compiled(net)


def layout(p):
    return np.array([row['address'] for row in dependency_table(p)],dtype=np.int64)


def sparse_locations(p,comp,supplied_layout):
    assert comp is cached(p)[1] and np.array_equal(supplied_layout,layout(p))
    where = {(row['field'],row['bit']):row for row in dependency_table(p)}
    codes = {name:code for code,name in enumerate(source_names(p))}
    live = set(comp.outputs.values())
    for _,a,b in comp.gates:
        live.update((a,b))
    locations = {}
    for name,node in comp.index.items():
        if name[0] != 'x' or node not in live:
            continue
        _,offset,field,bit = name
        row = where[field,bit]
        code = codes['info',0] if offset == 0 else codes['ln',row['offsets'].index(offset)]
        locations[node] = (row['address'],code)
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
    return dict(proposal='SP5',proposed_rule_change=True,active_G17_modified=False,
                SP4_modified=False,Q=p.Q,U=p.U,width=width(p),radius=12,
                proposed_netlist_sha256=cached(p)[1].digest)


def load_artifact(path=None):
    p = parameters()
    if path is None:
        path = ROOT/'figs/robustness/SP5_program.npz'
    with np.load(path,allow_pickle=False) as artifact:
        rom,saved_layout = artifact['rom'],artifact['layout']
    assert np.array_equal(saved_layout,layout(p))
    return machine.Candidate(p,rom,saved_layout)
