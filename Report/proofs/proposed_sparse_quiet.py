"""SP2: explicitly changed isolated sparse rule with quiet-majority diagnosis.

SP1's schema, transport, constants and compiler interface are retained;
J11 replaces maintenance. G17 and SP1 are unchanged. This module is not
registered in CURRENT or the manifest and proves no iid-noise threshold.
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
from gacsca import compiler, machine, rule_g
from gacsca.netlist import Compiled
import check_fast_mail_proposal as transport
import check_quiet_majority_proposal as diagnostic
import proposed_sparse as base
from proposed_sparse import (schema, width, source_names, reserved_cells,
                             flag_store_cells, info_copies, logical_width,
                             fivefold_fields, work_range, LANE_OFFSETS, FIVE, FRONT, SLOTS)


class QuietSparseParams(rule_g.ParamsG):
    def fam(self):
        return sys.modules[__name__]


def parameters():
    p = QuietSparseParams(**asdict(base.parameters()))
    p.check()
    assert (p.Q, p.U, width(p)) == (384, 55296, 259)
    return p


@lru_cache(None)
def dependency_table(p):
    # Instantiate the same conservative dependency envelope with the new
    # maintenance function in a fresh namespace. No helper globals change.
    original = inspect.getsource(transport.sparse_profile_certificate)
    start = original.index("    source = inspect.getsource(rule_g.build)")
    end = original.index("    largest = max(map(len, profile.values()))")
    body = textwrap.dedent(original[start:end])
    definition = "def envelope(p):\n" + textwrap.indent(body, "    ") + "    return profile\n"
    namespace = dict(transport.__dict__)
    namespace["proposed_maintenance"] = diagnostic.proposed_build
    exec(compile(definition, "<SP2 dependency envelope>", "exec"), namespace)
    profile = namespace["envelope"](p)
    assert max(map(len, profile.values())) <= 10
    addresses = [a for a in range(p.lo, p.hi) if a not in reserved_cells(p)]
    assert len(addresses) >= len(profile)
    rows = [dict(field=f, bit=i, address=a, offsets=sorted(offsets))
            for ((f, i), offsets), a in zip(profile.items(), addresses)]
    assert len(rows) == width(p)
    return rows


@lru_cache(None)
def cached(p):
    table = dependency_table(p)
    # Clone only the function's global bindings to select J11. The code,
    # sparse capture logic and original transport module remain unchanged.
    namespace = dict(transport.__dict__)
    namespace["proposed_maintenance"] = diagnostic.proposed_build
    factory = FunctionType(transport.concrete_sparse_net.__code__, namespace,
                           "SP2_concrete_sparse_net", transport.concrete_sparse_net.__defaults__)
    net, _ = factory(p, table)
    profile = {(row["field"], row["bit"]): set(row["offsets"]) for row in table}
    live = set(net.live_nodes())
    for name, node in net.input_node.items():
        if name[0] == "x" and node in live:
            _, off, field, bit = name
            assert off == 0 or off in profile[field, bit], name
    return net, Compiled(net)


def layout(p):
    return np.array([row["address"] for row in dependency_table(p)], dtype=np.int64)


def sparse_locations(p, comp, supplied_layout):
    assert comp is cached(p)[1] and np.array_equal(supplied_layout, layout(p))
    where = {(row["field"], row["bit"]): row for row in dependency_table(p)}
    codes = {name: code for code, name in enumerate(source_names(p))}
    live = set(comp.outputs.values())
    for _, a, b in comp.gates:
        live.update((a, b))
    locations = {}
    for name, node in comp.index.items():
        if name[0] != "x" or node not in live:
            continue
        _, offset, field, bit = name
        row = where[field, bit]
        code = codes["info", 0] if offset == 0 else codes["ln", row["offsets"].index(offset)]
        locations[node] = (row["address"], code)
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
    return dict(proposal="SP2", proposed_rule_change=True, active_G17_modified=False,
                SP1_modified=False, Q=p.Q, U=p.U, width=width(p), radius=12,
                proposed_netlist_sha256=cached(p)[1].digest)


def load_artifact(path=None):
    p = parameters()
    if path is None:
        path = ROOT / "figs/robustness/SP2_program.npz"
    with np.load(path, allow_pickle=False) as artifact:
        rom = artifact["rom"]
        saved_layout = artifact["layout"]
    assert np.array_equal(saved_layout, layout(p))
    return machine.Candidate(p, rom, saved_layout)
