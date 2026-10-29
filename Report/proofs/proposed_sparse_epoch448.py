"""SP18: EXPLICIT RF-epoch-start revision, separate from SP17 and G17.

Incorporate J116's local right-mode epoch starter in a separately built
own-programme candidate. Initially retain SP17's Q448/U67584/W316,
NPe50/MP73/NP128, twelve-rank schema and commit reset. Old packet guard
and upper Flag2 command no longer control native births. General damaged
GF/Age repair, full upper map and iid reliability need further proofs.
"""
from contextlib import contextmanager
from dataclasses import asdict
from functools import lru_cache
from pathlib import Path
import sys
from types import FunctionType,SimpleNamespace

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import numpy as np
from gacsca import compiler,machine
from gacsca.netlist import Compiled
import proposed_sparse_commit_reset448 as previous
import proposed_right_epoch_starter as starter

LANE_OFFSETS=previous.LANE_OFFSETS
logical_width=previous.logical_width
source_names=previous.source_names
schema=previous.schema
width=previous.width
proposed_build=previous.proposed_build
service=previous.service
reserved_cells=previous.reserved_cells
flag_store_cells=previous.flag_store_cells
info_copies=previous.info_copies
fivefold_fields=previous.fivefold_fields
work_range=previous.work_range
FIVE,FRONT,SLOTS=previous.FIVE,previous.FRONT,previous.SLOTS
COMMIT_RESET_FIELDS=previous.COMMIT_RESET_FIELDS
dependency_table=previous.dependency_table
generated_source=starter.generated_source
full_net=starter.full_net


class Epoch448Params(previous.CommitReset448Params):
    def fam(self):
        return sys.modules[__name__]


def parameters():
    p=Epoch448Params(**asdict(previous.parameters()))
    p.check()
    assert (p.Q,p.U,width(p),p.NPe,p.MP,p.NP,p.T_wf) == (448,67584,316,50,73,128,28865)
    return p


def actual_net(p):
    return full_net(p)


@lru_cache(None)
def cached(p):
    net,_=actual_net(p)
    profile={(row['field'],row['bit']):set(row['offsets']) for row in dependency_table(p)}
    live=set(net.live_nodes())
    for key,node in net.input_node.items():
        if key[0] == 'x' and node in live:
            _,off,f,b=key
            assert off == 0 or off in profile[f,b],key
    return net,Compiled(net)


def layout(p):
    return np.array([row['address'] for row in dependency_table(p)],dtype=np.int64)


def sparse_locations(p,comp,supplied_layout):
    namespace=dict(previous.__dict__,cached=cached,layout=layout,
                   dependency_table=dependency_table,source_names=source_names)
    fn=FunctionType(previous.sparse_locations.__code__,namespace,
        previous.sparse_locations.__name__,previous.sparse_locations.__defaults__)
    return fn(p,comp,supplied_layout)


@contextmanager
def compiler_input_map():
    original,original_scheduler=compiler.lane_locations,compiler.Scheduler
    scheduler_globals=dict(compiler.__dict__,lane_locations=sparse_locations,
        rule=SimpleNamespace(**dict(compiler.rule.__dict__,LANE_OFFSETS=LANE_OFFSETS)))
    constructor=FunctionType(original_scheduler.__init__.__code__,scheduler_globals,
        original_scheduler.__init__.__name__,original_scheduler.__init__.__defaults__)
    compiler.Scheduler=type('SP18Scheduler',(original_scheduler,),{'__init__':constructor})
    compiler.lane_locations=sparse_locations
    try:
        yield
    finally:
        compiler.lane_locations,compiler.Scheduler=original,original_scheduler


def identity(p):
    return dict(proposal='SP18',proposed_rule_change=True,active_G17_modified=False,
        SP17_modified=False,SP16_modified=False,Q=p.Q,U=p.U,width=width(p),radius=12,
        proposed_netlist_sha256=cached(p)[1].digest)


def load_artifact(path=None):
    p=parameters()
    if path is None:
        path=ROOT/'figs/robustness/SP18_program.npz'
    with np.load(path,allow_pickle=False) as artifact:
        rom,saved_layout=artifact['rom'],artifact['layout']
    assert np.array_equal(saved_layout,layout(p))
    return machine.Candidate(p,rom,saved_layout)
