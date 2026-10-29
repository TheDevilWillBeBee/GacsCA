"""SP21 own-ROM interface for the EXPLICIT J121 backward-pressure rule.

Keep J121's local equations; EXPLICITLY change NPe50 to NPe70/MP83.
All other primitive parameters are unchanged; the epoch moves to T_wf35905.
This module only provides isolated compiler/candidate bindings. Building
an own programme does not establish damage confinement or iid reliability.
G17, CURRENT, SP18 and the J121 local source are unchanged.
"""
from contextlib import contextmanager
from dataclasses import asdict
from functools import lru_cache
from pathlib import Path
from types import FunctionType,SimpleNamespace
import sys
import numpy as np
from gacsca import compiler,machine
from gacsca.netlist import Compiled
import proposed_backward_pressure448 as local
import proposed_sparse_epoch448 as previous

ROOT=Path(__file__).resolve().parents[2]
base=local.base
detector=local.detector
for _name in ('LANE_OFFSETS','logical_width','source_names','schema','width',
              'proposed_build','service','reserved_cells','flag_store_cells',
              'info_copies','fivefold_fields','work_range','FIVE','FRONT','SLOTS',
              'COMMIT_RESET_FIELDS','dependency_table','generated_source','full_net',
              'actual_net','layout','pulse'):
    globals()[_name]=getattr(local,_name)


class SparseBackward448Params(local.BackwardPressure448Params):
    def fam(self):
        return sys.modules[__name__]


def parameters():
    values=asdict(local.parameters())
    values['NPe']=70
    values['MP']=83
    p=SparseBackward448Params(**values)
    p.check()
    assert asdict(p)==dict(asdict(local.parameters()),NPe=70,MP=83)
    assert (p.Q,p.U,p.T_wf,width(p))==(448,67584,35905,317)
    return p


@lru_cache(None)
def cached(p):
    n,_=actual_net(p)
    comp=Compiled(n)
    assert comp.digest==local.cached(p)[1].digest
    return n,comp


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
    compiler.Scheduler=type('SP21Scheduler',(original_scheduler,),{'__init__':constructor})
    compiler.lane_locations=sparse_locations
    try:
        yield
    finally:
        compiler.lane_locations,compiler.Scheduler=original,original_scheduler


def identity(p):
    return dict(proposal='SP21',proposed_rule_change=True,active_G17_modified=False,
        SP18_modified=False,J121_local_module_modified=False,NPe_change=[50,70],MP_change=[73,83],Q=p.Q,U=p.U,
        width=width(p),radius=12,proposed_netlist_sha256=cached(p)[1].digest)


def load_artifact(path=None):
    p=parameters()
    if path is None:
        path=ROOT/'figs/robustness/SP21_program.npz'
    with np.load(path,allow_pickle=False) as artifact:
        rom,saved_layout=artifact['rom'],artifact['layout']
    assert np.array_equal(saved_layout,layout(p))
    return machine.Candidate(p,rom,saved_layout)
