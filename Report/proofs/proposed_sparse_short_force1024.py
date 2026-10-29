"""SP29: EXPLICIT isolated two-Q RF-force revision of SP28.

The global force window is2048 ticks instead of4096; birth is still TF.
All other Q1024/U475136 parameters, SF equations, packet/code/pressure
fields, capture layout and own-programme architecture are retained.
This module defines its own construction namespace and compiler family.
It does not mutate SP28/G17 or claim that a programme build proves
noiseless/noisy closure, signal supply, an eroder or iid reliability.
"""
from dataclasses import asdict
from functools import lru_cache
from pathlib import Path
from types import FunctionType,SimpleNamespace
import sys

import numpy as np
from gacsca import machine
from gacsca.netlist import majority_word,w_add_const_mod,w_eq_const,w_in_range,w_add_const
import proposed_sparse_distant_transport1024 as prior

ROOT=Path(__file__).resolve().parents[2]
EPOCH_LENGTH=2048
for name in ('LANE_OFFSETS','logical_width','source_names','base_schema','local',
             'proposed_build','service','reserved_cells','flag_store_cells','info_copies',
             'fivefold_fields','work_range','FIVE','FRONT','SLOTS','COMMIT_RESET_FIELDS',
             'pulse','schema','width','framed_build','service_build','dependency_table','layout',
             'generated_source'):
    globals()[name]=getattr(prior,name)


def epoch(n,cells,p,majority=majority_word):
    adjusted=[w_add_const_mod(n,cells[j]['addr'],(-j)%p.Q,p.Q) for j in range(1,6)]
    gf,gf_exists=majority(n,adjusted,cells[0]['addr'])
    age,age_exists=majority(n,[cells[j]['age'] for j in range(1,6)],cells[0]['age'])
    pulse_at=n.all([gf_exists,age_exists,w_eq_const(n,age,p.age_code(p.T_wf))])
    force=n.all([gf_exists,age_exists,
                 w_in_range(n,age,p.age_code(p.T_wf),p.age_code(p.T_wf+EPOCH_LENGTH))])
    birth=n.AND(pulse_at,w_in_range(n,gf,1,6))
    return dict(addr=gf,age=age,force=force,birth=birth,tag=w_add_const(n,gf[:4],15))


old_previous=prior.previous
new_starter=SimpleNamespace(**dict(old_previous.base.starter.__dict__,epoch=epoch))
new_base=SimpleNamespace(**dict(old_previous.base.__dict__,starter=new_starter))
previous=SimpleNamespace(**dict(old_previous.__dict__,base=new_base))
legacy=prior.prior.prior


class ShortForce1024Params(prior.DistantTransport1024Params):
    def fam(self):
        return sys.modules[__name__]


def parameters():
    values=asdict(prior.parameters())
    values['NPe']=272
    return ShortForce1024Params(**values).check()


def full_net(p,net_class=None):
    fn=legacy.full_net
    namespace=dict(legacy.__dict__,schema=schema,width=width,previous=previous,
        dependency_table=dependency_table,service_build=service_build,
        generated_source=generated_source)
    build=FunctionType(fn.__code__,namespace,fn.__name__,fn.__defaults__)
    return build(p) if net_class is None else build(p,net_class)


@lru_cache(None)
def cached(p):
    fn=legacy.cached.__wrapped__
    namespace=dict(legacy.__dict__,full_net=full_net,dependency_table=dependency_table)
    return FunctionType(fn.__code__,namespace)(p)


def sparse_locations(p,comp,supplied_layout):
    fn=legacy.sparse_locations
    namespace=dict(legacy.__dict__,cached=cached,layout=layout,dependency_table=dependency_table)
    return FunctionType(fn.__code__,namespace)(p,comp,supplied_layout)


def compiler_input_map():
    fn=legacy.compiler_input_map.__wrapped__
    namespace=dict(legacy.__dict__,sparse_locations=sparse_locations)
    return legacy.contextmanager(FunctionType(fn.__code__,namespace))()


def load_artifact(path=None):
    p=parameters()
    with np.load(path or ROOT/'figs/robustness/SP29_program.npz',allow_pickle=False) as stored:
        rom,supplied_layout=stored['rom'],stored['layout']
    assert np.array_equal(supplied_layout,layout(p))
    return machine.Candidate(p,rom,supplied_layout)
