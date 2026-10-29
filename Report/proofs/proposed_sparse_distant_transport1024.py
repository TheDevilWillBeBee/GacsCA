"""SP27 EXPLICIT distance37 fast-window correction of retained SP26.

Q1024/U475136/W842/r37 and all other constants/schema remain SP26's.
Only fast-mail window12 ->37 is changed. A fresh own ROM is required;
no active rule, previous proposal or compiler is modified.
"""
from functools import lru_cache
from pathlib import Path
from types import FunctionType
import sys
import numpy as np
from gacsca import machine
import proposed_sparse_distant_short1024 as prior

ROOT=Path(__file__).resolve().parents[2]
for name in ('LANE_OFFSETS','logical_width','source_names','base_schema','previous','local',
             'proposed_build','service','reserved_cells','flag_store_cells','info_copies',
             'fivefold_fields','work_range','FIVE','FRONT','SLOTS','COMMIT_RESET_FIELDS',
             'pulse','schema','width','framed_build','service_build','dependency_table','layout'):
    globals()[name]=getattr(prior,name)

class DistantTransport1024Params(prior.DistantShort1024Params):
    def fam(self):return sys.modules[__name__]

def parameters():
    from dataclasses import asdict
    return DistantTransport1024Params(**asdict(prior.parameters())).check()

@lru_cache(None)
def generated_source(p):
    source=prior.generated_source(p)
    old='p.age_code(g * Q + 12 * (Q // 8) + 1)'
    new='p.age_code(g * Q + 37 * (Q // 8) + 1)'
    assert source.count(old)==1
    return source.replace(old,new)

def full_net(p,net_class=None):
    fn=prior.prior.full_net
    ns=dict(prior.prior.__dict__,schema=schema,width=width,
        dependency_table=dependency_table,service_build=service_build,
        generated_source=generated_source)
    build=FunctionType(fn.__code__,ns,fn.__name__,fn.__defaults__)
    return build(p) if net_class is None else build(p,net_class)

@lru_cache(None)
def cached(p):
    fn=prior.prior.cached.__wrapped__
    ns=dict(prior.prior.__dict__,full_net=full_net,dependency_table=dependency_table)
    return FunctionType(fn.__code__,ns)(p)

def sparse_locations(p,comp,supplied_layout):
    fn=prior.prior.sparse_locations
    ns=dict(prior.prior.__dict__,cached=cached,layout=layout,dependency_table=dependency_table)
    return FunctionType(fn.__code__,ns)(p,comp,supplied_layout)

def compiler_input_map():
    fn=prior.prior.compiler_input_map.__wrapped__
    ns=dict(prior.prior.__dict__,sparse_locations=sparse_locations)
    return prior.prior.contextmanager(FunctionType(fn.__code__,ns))()

def load_artifact(path=None):
    p=parameters()
    with np.load(path or ROOT/'figs/robustness/SP27_program.npz',allow_pickle=False) as z:
        rom,stored=z['rom'],z['layout']
    assert np.array_equal(stored,layout(p))
    return machine.Candidate(p,rom,stored)
