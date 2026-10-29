"""SP17: EXPLICIT commit-reset revision, separate from SP16 and G17.

Keep SP16's Q448/U67584/W316, maintenance, guard6, packet/code evolution
and twelve-rank transport. At corrected commit clock only:
 * clear native F2 and all38 WF2/packet/code output bits;
 * allow Info output primaries only at the316 encoding locations and
   the two reserved upper-flag locations.
The own-programme attempt needs NPe50/MP73 instead of SP16's46/71,
without increasing Q/U. No clock-window service suppression is introduced. General damaged-input
repair and iid reliability require new proofs; own ROM is separate.
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
from gacsca import compiler,machine,rule_g
from gacsca.netlist import Net,Compiled
import check_fast_mail_proposal as transport
import proposed_sparse_buffered448 as previous

LANE_OFFSETS = previous.LANE_OFFSETS
logical_width = previous.logical_width
source_names = previous.source_names
schema = previous.schema
width = previous.width
proposed_build = previous.proposed_build
guard = previous.guard
service = previous.service
reserved_cells = previous.reserved_cells
flag_store_cells = previous.flag_store_cells
info_copies = previous.info_copies
fivefold_fields = previous.fivefold_fields
work_range = previous.work_range
FIVE,FRONT,SLOTS = previous.FIVE,previous.FRONT,previous.SLOTS
COMMIT_RESET_FIELDS = ('f2','wf2','packet_valid','packet_tag','packet_count',
                       'service_valid','service_position','service_count')


class CommitReset448Params(previous.BufferedFrame448Params):
    def fam(self):
        return sys.modules[__name__]


def parameters():
    values=asdict(previous.parameters())
    values['NPe']=50
    values['MP']=73
    p=CommitReset448Params(**values)
    p.check()
    assert (p.Q,p.U,width(p),p.NPe,p.MP,p.NP) == (448,67584,316,50,73,128)
    return p


def dependency_table(p):
    # New gates use GF/Age nodes already required by the old full rule.
    return previous.dependency_table(p)


@lru_cache(None)
def generated_source(p):
    _,source=previous.actual_net(p)
    table=dependency_table(p)
    assert [row['address'] for row in table] == list(range(p.lo+1,p.lo+width(p)+1))
    marker="        holds = [n.AND(lv(x, 'hold', r), n.NOT(commit)) for r in range(p.NH)]\n"
    assert source.count(marker) == 1
    source=source.replace(marker,
        "        encoded_primary = n.OR(w_in_range(n, xaddr, p.lo, p.lo+sum(w for _,w in sch)+1), w_eq_const(n, xaddr, p.hi-1))\n"
        "        info = n.AND(info, n.OR(n.NOT(commit), encoded_primary))\n"+marker)
    marker="    if p.five_front:\n        for f in FRONT:\n            outs[f] = [n.AND(keep, b) for b in front_new[f]]\n"
    assert source.count(marker) == 1
    names=repr(COMMIT_RESET_FIELDS)
    source=source.replace(marker,
        f"    for reset_field in {names}:\n"
        "        outs[reset_field] = [n.AND(b, n.NOT(commit)) for b in outs[reset_field]]\n"+marker)
    return source


def full_net(p,net_class=Net,majority=None,maintenance=None,observe=False):
    source=generated_source(p)
    if observe:
        marker="    packet_birth = n.all([w_eq_const(n, repair_age, p.age_code(p.T_wf)), packet_command, n.NOT(packet_guard)])\n"
        assert source.count(marker) == 1
        source=source.replace(marker,marker+
            "    n.set_output(('proof', 'guard'), packet_guard)\n"
            "    n.set_output(('proof', 'birth'), packet_birth)\n")
    namespace=dict(rule_g.__dict__,Net=net_class,LANE_OFFSETS=LANE_OFFSETS,
        logical_width=logical_width,source_names=source_names,schema=schema,
        maintenance=SimpleNamespace(build=maintenance or proposed_build()[0]),
        service_build=service.build,packet_guard_build=guard.build,
        OFFSETS=tuple(range(-12,13)),sparse_controls=transport.sparse_controls,
        sparse_table=dependency_table(p))
    for name,fn in rule_g.__dict__.items():
        if isinstance(fn,FunctionType) and fn.__module__ == rule_g.__name__:
            namespace[name]=FunctionType(fn.__code__,namespace,fn.__name__,fn.__defaults__,fn.__closure__)
    namespace.update(logical_width=logical_width,source_names=source_names,schema=schema)
    if majority is not None:
        namespace['maj5']=majority
    exec(compile(source,'<SP17 explicit commit reset; not SP16/G17>','exec'),namespace)
    return namespace['build'](p),source


def actual_net(p):
    return full_net(p)


@lru_cache(None)
def cached(p):
    net,_=actual_net(p)
    profile={(row['field'],row['bit']):set(row['offsets']) for row in dependency_table(p)}
    live=set(net.live_nodes())
    for key,node in net.input_node.items():
        if key[0] == 'x' and node in live:
            _,off,field,bit=key
            assert off == 0 or off in profile[field,bit],key
    return net,Compiled(net)


def layout(p):
    return np.array([row['address'] for row in dependency_table(p)],dtype=np.int64)


def sparse_locations(p,comp,supplied_layout):
    assert comp is cached(p)[1] and np.array_equal(supplied_layout,layout(p))
    rows={(row['field'],row['bit']):row for row in dependency_table(p)}
    codes={name:i for i,name in enumerate(source_names(p))}
    live=set(comp.outputs.values())
    for _,a,b in comp.gates:
        live.update((a,b))
    locations={}
    for key,node in comp.index.items():
        if key[0] != 'x' or node not in live:
            continue
        _,offset,field,bit=key
        row=rows[field,bit]
        code=codes['info',0] if offset == 0 else codes['ln',row['offsets'].index(offset)]
        locations[node]=(row['address'],code)
    assert len(set(locations.values())) == len(locations)
    return locations


@contextmanager
def compiler_input_map():
    original,original_scheduler=compiler.lane_locations,compiler.Scheduler
    scheduler_globals=dict(compiler.__dict__,lane_locations=sparse_locations,
        rule=SimpleNamespace(**dict(compiler.rule.__dict__,LANE_OFFSETS=LANE_OFFSETS)))
    constructor=FunctionType(original_scheduler.__init__.__code__,scheduler_globals,
        original_scheduler.__init__.__name__,original_scheduler.__init__.__defaults__)
    compiler.Scheduler=type('SP17Scheduler',(original_scheduler,),{'__init__':constructor})
    compiler.lane_locations=sparse_locations
    try:
        yield
    finally:
        compiler.lane_locations,compiler.Scheduler=original,original_scheduler


def identity(p):
    return dict(proposal='SP17',proposed_rule_change=True,active_G17_modified=False,
        SP16_modified=False,SP15_modified=False,Q=p.Q,U=p.U,width=width(p),radius=12,
        proposed_netlist_sha256=cached(p)[1].digest)


def load_artifact(path=None):
    p=parameters()
    if path is None:
        path=ROOT/'figs/robustness/SP17_program.npz'
    with np.load(path,allow_pickle=False) as artifact:
        rom,saved_layout=artifact['rom'],artifact['layout']
    assert np.array_equal(saved_layout,layout(p))
    return machine.Candidate(p,rom,saved_layout)
