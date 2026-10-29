"""SP30: EXPLICIT isolated repair-signal reservation revision of SP29.

Keep Q1024/U475136/state width842/radius37/two-Q force and every
primitive parameter of SP29. Reserve opposite-phase signal aliases509
and515 from normal encoding. Move only h2:77 and h2:83 to901 and902.
At commit keep exactly the relocated normal frame and the existing
two early-flag Hold locations58/965; all other Info groups are zero.
No G17, CURRENT, SP29, compiler or retained programme is modified.
Compilation/interface proofs do not establish noisy recovery or iid.
"""
from dataclasses import asdict
from functools import lru_cache
from pathlib import Path
from types import FunctionType
import sys
import numpy as np
from gacsca import machine
import proposed_sparse_short_force1024 as prior

ROOT=Path(__file__).resolve().parents[2]
for name in ('LANE_OFFSETS','logical_width','source_names','base_schema','local',
             'proposed_build','service','flag_store_cells','info_copies',
             'fivefold_fields','work_range','FIVE','FRONT','SLOTS','COMMIT_RESET_FIELDS',
             'pulse','schema','width','framed_build','service_build','previous','legacy'):
    globals()[name]=getattr(prior,name)
SIGNAL_ALIASES=(509,515)
RELOCATIONS={509:901,515:902}


class SignalReservation1024Params(prior.ShortForce1024Params):
    def fam(self):return sys.modules[__name__]


def parameters():
    p=SignalReservation1024Params(**asdict(prior.parameters())).check()
    assert (p.Q,p.U,width(p),p.T_wf)==(1024,475136,842,278401)
    return p


def reserved_cells(p):return tuple(sorted(set(prior.reserved_cells(p))|set(SIGNAL_ALIASES)))


@lru_cache(None)
def dependency_table(p):
    rows=[dict(row,address=RELOCATIONS.get(row['address'],row['address'])) for row in prior.dependency_table(p)]
    assert [(r['field'],r['bit'],r['address']) for r in rows if r['address'] in RELOCATIONS.values()]==[
        ('h2',77,901),('h2',83,902)]
    assert len(rows)==width(p)==len({r['address'] for r in rows})
    assert not set(SIGNAL_ALIASES)&{r['address'] for r in rows}
    assert all(p.lo<r['address']<p.hi-1 for r in rows)
    return rows


@lru_cache(None)
def generated_source(p):
    source=prior.generated_source(p)
    old="        encoded_primary = n.OR(w_in_range(n, xaddr, p.lo, p.lo+sum(w for _,w in sch)+1), w_eq_const(n, xaddr, p.hi-1))\n"
    assert source.count(old)==1
    new=("        old_frame = n.all([w_in_range(n, xaddr, p.lo, p.lo+sum(w for _,w in sch)+1),\n"
         "                           n.NOT(w_eq_const(n, xaddr, 509)), n.NOT(w_eq_const(n, xaddr, 515))])\n"
         "        encoded_primary = n.any([old_frame, w_eq_const(n, xaddr, 901),\n"
         "                                 w_eq_const(n, xaddr, 902), w_eq_const(n, xaddr, p.hi-1)])\n")
    return source.replace(old,new)


def full_net(p,net_class=None):
    fn=legacy.full_net
    namespace=dict(legacy.__dict__,schema=schema,width=width,previous=previous,
        dependency_table=dependency_table,service_build=service_build,generated_source=generated_source)
    build=FunctionType(fn.__code__,namespace,fn.__name__,fn.__defaults__)
    return build(p) if net_class is None else build(p,net_class)


@lru_cache(None)
def cached(p):
    namespace=dict(legacy.__dict__,full_net=full_net,dependency_table=dependency_table)
    return FunctionType(legacy.cached.__wrapped__.__code__,namespace)(p)


def layout(p):return np.array([r['address'] for r in dependency_table(p)],dtype=np.int64)


def sparse_locations(p,comp,supplied_layout):
    namespace=dict(legacy.__dict__,cached=cached,layout=layout,dependency_table=dependency_table)
    return FunctionType(legacy.sparse_locations.__code__,namespace)(p,comp,supplied_layout)


def compiler_input_map():
    namespace=dict(legacy.__dict__,sparse_locations=sparse_locations)
    return legacy.contextmanager(FunctionType(legacy.compiler_input_map.__wrapped__.__code__,namespace))()


def load_artifact(path=None):
    p=parameters()
    with np.load(path or ROOT/'figs/robustness/SP30_program.npz',allow_pickle=False) as saved:
        rom,locations=saved['rom'],saved['layout']
    assert np.array_equal(locations,layout(p))
    return machine.Candidate(p,rom,locations)
