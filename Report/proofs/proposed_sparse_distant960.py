"""SP23 EXPLICIT own-programme incorporation attempt of J125.

Change Q448->960, radius12->37, history ranks12->64, NPe65->250,
MP75->301, NP128->512, nb192->768 and corresponding word widths.
Buffered code-frame size453->965 and position width9->10 are explicit.
Joint distant refinement is unchanged in form. The resulting own ROM
and simulation/data/reliability obligations must be checked separately.
Never modifies G17, CURRENT, SP22 or the standalone J125 module.
"""
from contextlib import contextmanager
from dataclasses import asdict
from functools import lru_cache
from pathlib import Path
from types import FunctionType,SimpleNamespace
import sys
import numpy as np
from gacsca import rule_g,compiler,machine
from gacsca.netlist import Net,Compiled
import proposed_sparse_backward_fitted448 as previous
import proposed_distant_native448 as local
import check_fast_mail_proposal as transport

ROOT=Path(__file__).resolve().parents[2]
LANE_OFFSETS=(*range(-37,-22),*range(-17,0),*range(1,18),*range(23,38))
assert len(LANE_OFFSETS)==64
logical_width=FunctionType(rule_g.logical_width.__code__,dict(rule_g.__dict__,LANE_OFFSETS=LANE_OFFSETS))
source_names=FunctionType(rule_g.source_names.__code__,dict(rule_g.__dict__,LANE_OFFSETS=LANE_OFFSETS))
base_schema=FunctionType(rule_g.schema.__code__,dict(rule_g.__dict__,logical_width=logical_width))
for name in ('proposed_build','service','reserved_cells','flag_store_cells','info_copies',
             'fivefold_fields','work_range','FIVE','FRONT','SLOTS','COMMIT_RESET_FIELDS','pulse'):
    globals()[name]=getattr(previous,name)


def schema(p):
    return [*base_schema(p),('packet_tag',4),('packet_valid',1),('packet_count',11),
        ('service_valid',1),('service_position',p.PB),('service_count',11),('backward_pressure',1)]


def width(p):
    return sum(w for _,w in schema(p))


@lru_cache(None)
def framed_build(p):
    original,_=previous.service.generated_build()
    namespace=dict(original.__globals__,Q=p.Q+5,POSITION_BITS=p.PB,POSITION_MODULUS=1<<p.PB)
    return FunctionType(original.__code__,namespace,original.__name__,original.__defaults__,original.__closure__)


def service_build(n,cells,p):
    result=framed_build(p)(n,cells)
    result['service_force']=n.OR(result['service_force'],result['packet_any_cohort'])
    return result


class Distant960Params(previous.SparseBackward448Params):
    def fam(self): return sys.modules[__name__]

    @property
    def n_sources(self): return self.L+2+len(LANE_OFFSETS)+self.S+2

    def check(self):
        return FunctionType(rule_g.ParamsG.check.__code__,dict(rule_g.__dict__,LANE_OFFSETS=LANE_OFFSETS))(self)


def parameters():
    values=asdict(previous.parameters())
    values.update(q=960,k=10,m=20,nb=768,NP=512,NPe=250,MP=301,skew=(0,)*64)
    p=Distant960Params(**values);p.check()
    assert (p.Q,p.U,p.R,p.T_wf,width(p),p.n_sources,p.SB)==(960,663552,864,240193,842,136,8)
    return p


@lru_cache(None)
def dependency_table(p):
    old={(r['field'],r['bit']):r['offsets'] for r in previous.dependency_table(previous.parameters())}
    addresses=[a for a in range(p.lo,p.hi) if a not in reserved_cells(p)]
    rows=[]
    for field,w in schema(p):
        for bit in range(w):
            if field in ('addr','age'): offsets=list(LANE_OFFSETS)
            elif field in ('h1','h2'): offsets=[j for j in range(-4,5) if j]
            elif field=='service_position' and bit>=9:
                offsets=sorted(set().union(*(set(value) for (f,_),value in old.items() if f==field)))
            else: offsets=list(old[field,bit])
            rows.append(dict(field=field,bit=bit,address=addresses[len(rows)],offsets=offsets))
    assert len(rows)==width(p)==len(addresses)
    return rows


@lru_cache(None)
def generated_source(p):
    # This exact template uses p and sch at build time. Asking its legacy
    # producer to instantiate old448 dependencies at k10 is unnecessary.
    return local.generated_source(local.parameters())


def full_net(p,net_class=Net):
    namespace=dict(rule_g.__dict__,Net=net_class,OFFSETS=local.OFFSETS,
        LANE_OFFSETS=LANE_OFFSETS,logical_width=logical_width,source_names=source_names,schema=schema,
        maintenance=SimpleNamespace(build=proposed_build()[0]),service_build=lambda n,cells:service_build(n,cells,p),
        epoch_build=previous.base.starter.epoch,backward_build=pulse,distant_refinement=local.refine,
        sparse_controls=transport.sparse_controls,sparse_table=dependency_table(p))
    for name,fn in rule_g.__dict__.items():
        if isinstance(fn,FunctionType) and fn.__module__==rule_g.__name__:
            namespace[name]=FunctionType(fn.__code__,namespace,fn.__name__,fn.__defaults__,fn.__closure__)
    namespace.update(schema=schema,logical_width=logical_width,source_names=source_names)
    source=generated_source(p)
    exec(compile(source,'<EXPLICIT SP23 distant native/history64 incorporation>', 'exec'),namespace)
    return namespace['build'](p),source


@lru_cache(None)
def cached(p):
    n,_=full_net(p);profile={(r['field'],r['bit']):set(r['offsets']) for r in dependency_table(p)}
    live=set(n.live_nodes())
    for key,node in n.input_node.items():
        if key[0]=='x' and node in live:
            _,offset,field,bit=key
            assert offset==0 or offset in profile[field,bit],key
    return n,Compiled(n)


def layout(p): return np.array([r['address'] for r in dependency_table(p)],dtype=np.int64)


def sparse_locations(p,comp,supplied_layout):
    assert comp is cached(p)[1] and np.array_equal(supplied_layout,layout(p))
    rows={(r['field'],r['bit']):r for r in dependency_table(p)}
    codes={name:i for i,name in enumerate(source_names(p))}
    live=set(comp.outputs.values())
    for _,a,b in comp.gates: live.update((a,b))
    locations={}
    for key,node in comp.index.items():
        if key[0]=='x' and node in live:
            _,offset,field,bit=key;r=rows[field,bit]
            locations[node]=(r['address'],codes['info',0] if offset==0 else codes['ln',r['offsets'].index(offset)])
    assert len(set(locations.values()))==len(locations)
    return locations


@contextmanager
def compiler_input_map():
    original,original_scheduler=compiler.lane_locations,compiler.Scheduler
    namespace=dict(compiler.__dict__,lane_locations=sparse_locations,
        rule=SimpleNamespace(**dict(compiler.rule.__dict__,LANE_OFFSETS=LANE_OFFSETS)))
    constructor=FunctionType(original_scheduler.__init__.__code__,namespace,original_scheduler.__init__.__name__,original_scheduler.__init__.__defaults__)
    compiler.Scheduler=type('SP23Scheduler',(original_scheduler,),{'__init__':constructor})
    compiler.lane_locations=sparse_locations
    try: yield
    finally: compiler.lane_locations,compiler.Scheduler=original,original_scheduler


def load_artifact(path=None):
    p=parameters()
    with np.load(path or ROOT/'figs/robustness/SP23_program.npz',allow_pickle=False) as z:
        rom,stored_layout=z['rom'],z['layout']
    assert np.array_equal(stored_layout,layout(p))
    return machine.Candidate(p,rom,stored_layout)
