"""SP16: explicit buffered-code-frame CA proposal, separate from SP15/G17.

Use J103's tag+6/code-limit453 service with SP15's guard6 and twelve
history ranks. The raw schema and proposed Q448/U67584 are unchanged.
The first NPe44 build required45 early passes; explicit NPe46 supplies
the mandatory spare pass. This changes its signal/birth clocks too.
Its first NPe46/MP67 build missed one match key; MP69 then stalled in
post-match scheduling. MP71 is the next isolated legal-pass attempt.
Every adjustment remains an explicitly proposed change.
An own programme and full incorporation/encoding certificates are
required; no iid reliability theorem is supplied by defining this rule.
"""
from contextlib import contextmanager
from dataclasses import asdict
from functools import lru_cache
from pathlib import Path
import sys
from types import FunctionType,SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import numpy as np
from gacsca import compiler,machine
from gacsca.netlist import Compiled
import proposed_sparse_guarded_pressure448 as previous
import proposed_buffered_framed_service as service

LANE_OFFSETS = previous.LANE_OFFSETS
logical_width = previous.logical_width
source_names = previous.source_names
schema = previous.schema
width = previous.width
proposed_build = previous.proposed_build
guard = previous.guard
reserved_cells = previous.reserved_cells
flag_store_cells = previous.flag_store_cells
info_copies = previous.info_copies
fivefold_fields = previous.fivefold_fields
work_range = previous.work_range
FIVE,FRONT,SLOTS = previous.FIVE,previous.FRONT,previous.SLOTS


class BufferedFrame448Params(previous.GuardedPressure448Params):
    def fam(self):
        return sys.modules[__name__]


def parameters():
    values = asdict(previous.parameters())
    values['NPe'] = 46
    values['MP'] = 71
    p = BufferedFrame448Params(**values)
    p.check()
    assert (p.Q,p.U,width(p)) == (448,67584,316)
    return p


def dependency_table(p):
    # No added input offset: only packet-to-code arithmetic/range changes.
    return previous.dependency_table(p)


def actual_net(p):
    # Reconstruct SP15's literal full rule with the separately changed
    # module in its isolated namespace. Do not mutate previous globals.
    namespace = dict(previous.__dict__,service=service,schema=schema,
        logical_width=logical_width,source_names=source_names,
        dependency_table=dependency_table,proposed_build=proposed_build,guard=guard)
    fn = FunctionType(previous.actual_net.__code__,namespace,
        previous.actual_net.__name__,previous.actual_net.__defaults__)
    return fn(p)


@lru_cache(None)
def cached(p):
    net,_ = actual_net(p)
    profile = {(row['field'],row['bit']):set(row['offsets']) for row in dependency_table(p)}
    live = set(net.live_nodes())
    for key,node in net.input_node.items():
        if key[0] == 'x' and node in live:
            _,off,field,bit = key
            assert off == 0 or off in profile[field,bit],key
    return net,Compiled(net)


def layout(p):
    return np.array([row['address'] for row in dependency_table(p)],dtype=np.int64)


def sparse_locations(p,comp,supplied_layout):
    namespace = dict(previous.__dict__,cached=cached,layout=layout,
        dependency_table=dependency_table,source_names=source_names)
    fn = FunctionType(previous.sparse_locations.__code__,namespace,
        previous.sparse_locations.__name__,previous.sparse_locations.__defaults__)
    return fn(p,comp,supplied_layout)


@contextmanager
def compiler_input_map():
    original,original_scheduler = compiler.lane_locations,compiler.Scheduler
    scheduler_globals = dict(compiler.__dict__,lane_locations=sparse_locations,
        rule=SimpleNamespace(**dict(compiler.rule.__dict__,LANE_OFFSETS=LANE_OFFSETS)))
    constructor = FunctionType(original_scheduler.__init__.__code__,scheduler_globals,
        original_scheduler.__init__.__name__,original_scheduler.__init__.__defaults__)
    compiler.Scheduler = type('SP16Scheduler',(original_scheduler,),{'__init__':constructor})
    compiler.lane_locations = sparse_locations
    try:
        yield
    finally:
        compiler.lane_locations,compiler.Scheduler = original,original_scheduler


def identity(p):
    return dict(proposal='SP16',proposed_rule_change=True,active_G17_modified=False,
        SP15_modified=False,SP14_modified=False,Q=p.Q,U=p.U,width=width(p),radius=12,
        proposed_netlist_sha256=cached(p)[1].digest)


def load_artifact(path=None):
    p = parameters()
    if path is None:
        path = ROOT/'figs/robustness/SP16_program.npz'
    with np.load(path,allow_pickle=False) as artifact:
        rom,saved_layout = artifact['rom'],artifact['layout']
    assert np.array_equal(saved_layout,layout(p))
    return machine.Candidate(p,rom,saved_layout)
