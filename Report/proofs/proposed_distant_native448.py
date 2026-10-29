"""EXPLICIT unincorporated native-input revision of SP22; no own ROM.

For logical offsets -5..5, refine the GF/Age pair using four disjoint
five-cell blocks centered at -30,-10,10,30 relative to that offset.
Each block uses whole-word 3/5; a joint 3/4 quorum of existing block
values replaces the raw pair. Otherwise keep the raw pair. Substitute
these pairs throughout SP22's physical equations, including its copy
keep/front tests. Other state fields and SP22 constants stay unchanged.
Radius is explicitly increased from12 to37. The old twelve-rank
capture layout and own programme do not cover these equations.
"""
from functools import lru_cache
from types import FunctionType,SimpleNamespace
from gacsca import rule_g
from gacsca.netlist import (Net,Compiled,majority_word,at_least,w_eq,
                           w_mux,w_add_const_mod)
import proposed_sparse_backward_fitted448 as previous
import check_fast_mail_proposal as transport

CENTERS=(-30,-10,10,30)
REFINED=tuple(range(-5,6))
OFFSETS=tuple(range(-37,38))
parameters=previous.parameters
schema=previous.schema
width=previous.width


def block_quorum(n,values,default):
    """Joint whole-word 3/4 of four existing block results."""
    assert len(values)==4
    bitwise=[at_least(n,[word[b] for word,_ in values],3)
             for b in range(len(default))]
    exists=at_least(n,[n.AND(valid,w_eq(n,word,bitwise))
                       for word,valid in values],3)
    return w_mux(n,exists,bitwise,default),exists


def refine_one(n,cells,p,j,mode=majority_word,quorum=block_quorum):
    raw=[*cells[j]['addr'],*cells[j]['age']]
    blocks=[]
    for center in CENTERS:
        words=[]
        for u in range(-2,3):
            displacement=center+u
            c=cells[j+displacement]
            adjusted=w_add_const_mod(n,c['addr'],(-displacement)%p.Q,p.Q)
            words.append([*adjusted,*c['age']])
        blocks.append(mode(n,words,raw))
    pair,exists=quorum(n,blocks,raw)
    return dict(addr=pair[:p.k],age=pair[p.k:]),exists


def refine(n,cells,p,mode=majority_word,quorum=block_quorum):
    return {j:refine_one(n,cells,p,j,mode,quorum)[0] for j in REFINED}


@lru_cache(None)
def generated_source(p):
    source=previous.generated_source(p)
    marker="    I = [n.input(('I', i)) for i in range(p.IW)]\n"
    assert source.count(marker)==1
    extra="""    native_refined = distant_refinement(n, cell, p)
    cell = {j: dict(value, **native_refined[j]) if j in native_refined else value
            for j, value in cell.items()}
"""
    return source.replace(marker,extra+marker)


def full_net(p,net_class=Net):
    namespace=dict(rule_g.__dict__,Net=net_class,OFFSETS=OFFSETS,
        LANE_OFFSETS=previous.LANE_OFFSETS,logical_width=previous.logical_width,
        source_names=previous.source_names,schema=schema,
        maintenance=SimpleNamespace(build=previous.proposed_build()[0]),
        service_build=previous.service.build,
        epoch_build=previous.base.starter.epoch,backward_build=previous.pulse,
        distant_refinement=refine,sparse_controls=transport.sparse_controls,
        sparse_table=previous.dependency_table(p))
    for name,fn in rule_g.__dict__.items():
        if isinstance(fn,FunctionType) and fn.__module__==rule_g.__name__:
            namespace[name]=FunctionType(fn.__code__,namespace,fn.__name__,fn.__defaults__,fn.__closure__)
    namespace.update(schema=schema,logical_width=previous.logical_width,
                     source_names=previous.source_names)
    source=generated_source(p)
    exec(compile(source,'<EXPLICIT distant native input revision; no own ROM>','exec'),namespace)
    return namespace['build'](p),source


@lru_cache(None)
def cached(p):
    n,source=full_net(p)
    return n,Compiled(n),source
