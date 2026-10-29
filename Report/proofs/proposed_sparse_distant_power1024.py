"""SP24 EXPLICIT power-of-two/longer-schedule revision of failed SP23.

Q960->1024, nb768->1536, NP512->1024, NPe250->550, MP301->601,
Age20->21, code position10->11/frame965->1029, U1425408/W844.
Radius37 and64 ranks retained; every previous proposal remains unchanged.
Own programme/encoding/native/data/higher-error proofs remain separate.
"""
from dataclasses import asdict
from functools import lru_cache
from pathlib import Path
from types import FunctionType
import sys
import numpy as np
from gacsca import machine
import proposed_sparse_distant960 as prior

ROOT=Path(__file__).resolve().parents[2]
for name in ('LANE_OFFSETS','logical_width','source_names','base_schema','previous','local',
             'proposed_build','service','reserved_cells','flag_store_cells','info_copies',
             'fivefold_fields','work_range','FIVE','FRONT','SLOTS','COMMIT_RESET_FIELDS',
             'pulse','generated_source'):
    globals()[name]=getattr(prior,name)


class DistantPower1024Params(prior.Distant960Params):
    def fam(self): return sys.modules[__name__]


def parameters():
    values=asdict(prior.parameters())
    values.update(q=1024,m=21,nb=1536,NP=1024,NPe=550,MP=601)
    p=DistantPower1024Params(**values);p.check()
    assert (p.Q,p.R,p.U,width(p),p.T_wf)==(1024,928,1425408,844,536385)
    return p


def schema(p):
    return [(field,11 if field=='service_position' else bits) for field,bits in prior.schema(p)]


def width(p): return sum(bits for _,bits in schema(p))


@lru_cache(None)
def framed_build(p):
    original=prior.framed_build(p)
    namespace=dict(original.__globals__,Q=p.Q+5,POSITION_BITS=11,POSITION_MODULUS=2048)
    return FunctionType(original.__code__,namespace,original.__name__,original.__defaults__,original.__closure__)


def service_build(n,cells,p):
    result=framed_build(p)(n,cells)
    result['service_force']=n.OR(result['service_force'],result['packet_any_cohort'])
    return result


@lru_cache(None)
def dependency_table(p):
    old={(r['field'],r['bit']):r['offsets'] for r in previous.dependency_table(previous.parameters())}
    addresses=[a for a in range(p.lo,p.hi) if a not in reserved_cells(p)]
    rows=[]
    for field,bits in schema(p):
        for bit in range(bits):
            if field in ('addr','age'): offsets=list(LANE_OFFSETS)
            elif field in ('h1','h2'): offsets=[j for j in range(-4,5) if j]
            elif field=='service_position' and bit>=9:
                offsets=sorted(set().union(*(set(value) for (f,_),value in old.items() if f==field)))
            else: offsets=list(old[field,bit])
            rows.append(dict(field=field,bit=bit,address=addresses[len(rows)],offsets=offsets))
    assert len(rows)==width(p)<=len(addresses)
    return rows


def full_net(p,net_class=None):
    namespace=dict(prior.__dict__,schema=schema,width=width,dependency_table=dependency_table,
        service_build=service_build,generated_source=generated_source)
    fn=FunctionType(prior.full_net.__code__,namespace,prior.full_net.__name__,prior.full_net.__defaults__)
    return fn(p) if net_class is None else fn(p,net_class)


@lru_cache(None)
def cached(p):
    namespace=dict(prior.__dict__,full_net=full_net,dependency_table=dependency_table)
    return FunctionType(prior.cached.__wrapped__.__code__,namespace)(p)


def layout(p): return np.array([r['address'] for r in dependency_table(p)],dtype=np.int64)


def sparse_locations(p,comp,supplied_layout):
    namespace=dict(prior.__dict__,cached=cached,layout=layout,dependency_table=dependency_table)
    return FunctionType(prior.sparse_locations.__code__,namespace)(p,comp,supplied_layout)


def compiler_input_map():
    namespace=dict(prior.__dict__,sparse_locations=sparse_locations)
    generator=FunctionType(prior.compiler_input_map.__wrapped__.__code__,namespace)
    return prior.contextmanager(generator)()


def load_artifact(path=None):
    p=parameters()
    with np.load(path or ROOT/'figs/robustness/SP24_program.npz',allow_pickle=False) as z:
        rom,stored_layout=z['rom'],z['layout']
    assert np.array_equal(stored_layout,layout(p))
    return machine.Candidate(p,rom,stored_layout)
