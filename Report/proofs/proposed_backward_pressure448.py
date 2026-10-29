"""EXPLICIT SP19 backward-pressure local transition, separate from SP18.

Add one pressure bit. A radius-six packet cohort injects it; otherwise
three right pressure bits propagate it left, using RF GF/Age/window and
stopping at GF Q-1. Force native RF in the same update. No own ROM is
provided by this module. Native reconstruction is separate from data-map,
damage confinement, self-simulation and iid reliability obligations.
"""
from dataclasses import asdict
from functools import lru_cache
from types import FunctionType,SimpleNamespace
import sys
import numpy as np
from gacsca import rule_g
from gacsca.netlist import (Net,Compiled,majority_word,w_add_const_mod,
                           w_eq_const,w_in_range,at_least)
import proposed_sparse_epoch448 as base
import proposed_packet_guard6 as detector
import check_fast_mail_proposal as transport

LANE_OFFSETS=base.LANE_OFFSETS
logical_width=base.logical_width
source_names=base.source_names
proposed_build=base.proposed_build
service=base.service
reserved_cells=base.reserved_cells
flag_store_cells=base.flag_store_cells
info_copies=base.info_copies
fivefold_fields=base.fivefold_fields
work_range=base.work_range
FIVE,FRONT,SLOTS=base.FIVE,base.FRONT,base.SLOTS
COMMIT_RESET_FIELDS=(*base.COMMIT_RESET_FIELDS,'backward_pressure')


def schema(p):
    return [*base.schema(p),('backward_pressure',1)]


def width(p):
    return sum(w for _,w in schema(p))


class BackwardPressure448Params(base.Epoch448Params):
    def fam(self):
        return sys.modules[__name__]


def parameters():
    p=BackwardPressure448Params(**asdict(base.parameters()))
    p.check()
    assert (p.Q,p.U,width(p))==(448,67584,317)
    return p


def dependency_table(p):
    rows=[dict(r,offsets=list(r['offsets'])) for r in base.dependency_table(p)]
    used={r['address'] for r in rows}
    available=[a for a in range(p.lo,p.hi) if a not in reserved_cells(p) and a not in used]
    assert available
    rows.append(dict(field='backward_pressure',bit=0,address=available[0],offsets=list(range(1,6))))
    return rows


def pulse(n,cells,p,mode=majority_word,packet_detector=detector.build):
    adjusted=[w_add_const_mod(n,cells[j]['addr'],(-j)%p.Q,p.Q) for j in range(1,6)]
    addr,exists=mode(n,adjusted,cells[0]['addr'])
    age,age_exists=mode(n,[cells[j]['age'] for j in range(1,6)],cells[0]['age'])
    packet=packet_detector(n,{j:dict(packet_tag=cells[j]['packet_tag'],
        packet_count=cells[j]['packet_count'],packet_valid=cells[j]['packet_valid'][0],
        wf2=cells[j]['wf2'][0]) for j in range(-6,7)})
    right=at_least(n,[cells[j]['backward_pressure'][0] for j in range(1,6)],3)
    window=w_in_range(n,age,p.age_code(p.T_wf),p.age_code(p.T_wf+1792)+1)
    propagate=n.AND(n.NOT(w_eq_const(n,addr,p.Q-1)),right)
    signal=n.all([exists,age_exists,window,n.OR(packet,propagate)])
    return dict(signal=signal,addr=addr,age=age,packet=packet,right=right,window=window)


@lru_cache(None)
def generated_source(p):
    source=base.generated_source(p)
    marker='    right_epoch = epoch_build(n, cell, p)\n'
    assert source.count(marker)==1
    source=source.replace(marker,marker+'    backward_now = backward_build(n, cell, p)\n')
    marker="        service_force=n.OR(service_now['service_force'], right_epoch['force']),\n"
    assert source.count(marker)==1
    source=source.replace(marker,"        service_force=n.any([service_now['service_force'], right_epoch['force'], backward_now['signal']]),\n")
    marker='    for reset_field in '
    at=source.index(marker)
    source=source[:at]+"    outs['backward_pressure'] = [n.AND(backward_now['signal'], n.NOT(commit))]\n"+source[at:]
    return source


def full_net(p,net_class=Net,majority=None,maintenance=None,symbolic=False):
    mode=majority_word
    if symbolic:
        from check_right_barrier import dominant_majority
        from check_shifted_halfline import dominant_bit
        mode=dominant_majority
        majority=majority or dominant_bit
    namespace=dict(rule_g.__dict__,Net=net_class,LANE_OFFSETS=LANE_OFFSETS,
        logical_width=logical_width,source_names=source_names,schema=schema,
        maintenance=SimpleNamespace(build=maintenance or proposed_build(symbolic=symbolic)[0]),
        service_build=service.build,epoch_build=lambda n,cells,p:base.starter.epoch(n,cells,p,mode),
        backward_build=lambda n,cells,p:pulse(n,cells,p,mode),
        OFFSETS=tuple(range(-12,13)),sparse_controls=transport.sparse_controls,sparse_table=dependency_table(p))
    for name,fn in rule_g.__dict__.items():
        if isinstance(fn,FunctionType) and fn.__module__==rule_g.__name__:
            namespace[name]=FunctionType(fn.__code__,namespace,fn.__name__,fn.__defaults__,fn.__closure__)
    namespace.update(schema=schema,logical_width=logical_width,source_names=source_names)
    if majority is not None:
        namespace['maj5']=majority
    source=generated_source(p)
    exec(compile(source,'<EXPLICIT SP19 unincorporated backward pressure>', 'exec'),namespace)
    return namespace['build'](p),source


actual_net=full_net


@lru_cache(None)
def cached(p):
    n,_=full_net(p)
    profile={(r['field'],r['bit']):set(r['offsets']) for r in dependency_table(p)}
    live=set(n.live_nodes())
    for key,node in n.input_node.items():
        if key[0]=='x' and node in live:
            _,off,f,b=key
            assert off==0 or off in profile[f,b],key
    return n,Compiled(n)


def layout(p):
    return np.asarray([r['address'] for r in dependency_table(p)],dtype=np.int64)
