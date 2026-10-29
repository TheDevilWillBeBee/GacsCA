"""SP31: EXPLICIT isolated native-command revision of frozen SP30.

Keep Q1024/U475136/W842/r37, the capture layout, schedule and SF equations.
Native maintenance no longer receives private service/epoch/pressure force.
Native WF2 again comes from the actual special Info command near GF0;
private packet lifetime uses packet_valid rather than the native WF2 bit.
The private unconditional epoch birth and service machinery are retained.
This requires a new own ROM. No active or frozen prior rule is modified.
Building it does not prove noisy recovery, a higher-error map or iid memory.
"""
from dataclasses import asdict
from functools import lru_cache
from pathlib import Path
from types import FunctionType
import sys
import numpy as np
from gacsca import machine
from gacsca.netlist import Compiled,Net
import proposed_sparse_signal_reservation1024 as prior

ROOT=Path(__file__).resolve().parents[2]
for name in ('LANE_OFFSETS','logical_width','source_names','base_schema','local',
             'proposed_build','service','flag_store_cells','info_copies',
             'fivefold_fields','work_range','FIVE','FRONT','SLOTS','COMMIT_RESET_FIELDS',
             'schema','width','framed_build','previous','legacy','reserved_cells',
             'dependency_table','layout'):
    globals()[name]=getattr(prior,name)


class NativeCommand1024Params(prior.SignalReservation1024Params):
    def fam(self):return sys.modules[__name__]


def parameters():
    p=NativeCommand1024Params(**asdict(prior.parameters())).check()
    assert (p.Q,p.U,width(p),p.T_wf)==(1024,475136,842,278401)
    return p


def private_packet_cells(cells):
    # This substitution is confined to private service/detector arguments.
    # Native maintenance still reads the actual native WF2 word.
    return {j:dict(c,wf2=c['packet_valid']) for j,c in cells.items()}


def service_build(n,cells,p):
    return prior.service_build(n,private_packet_cells(cells),p)


def pulse(n,cells,p,**kwargs):
    return prior.pulse(n,private_packet_cells(cells),p,**kwargs)


@lru_cache(None)
def generated_source(p):
    source=prior.generated_source(p)
    old="        service_force=n.any([service_now['service_force'], right_epoch['force'], backward_now['signal']]),\n"
    assert source.count(old)==1
    source=source.replace(old,"        service_force=0,\n")
    old="    wf2 = n.OR(packet_birth, packet_now['wf2'])\n"
    assert source.count(old)==1
    source=source.replace(old,
        "    packet_alive = n.OR(packet_birth, packet_now['wf2'])\n"
        "    wf2 = n.all([left_end, in_wf, sim_l, n.NOT(f1_new)])\n")
    old="packet_valid=[wf2]"
    assert source.count(old)==1
    source=source.replace(old,"packet_valid=[packet_alive]")
    return source


def full_net(p,net_class=Net):
    namespace=dict(legacy.__dict__,schema=schema,width=width,previous=previous,
        dependency_table=dependency_table,service_build=service_build,pulse=pulse,
        generated_source=generated_source)
    fn=FunctionType(legacy.full_net.__code__,namespace,
        legacy.full_net.__name__,legacy.full_net.__defaults__)
    return fn(p,net_class)


@lru_cache(None)
def cached(p):
    n,_=full_net(p)
    profile={(r['field'],r['bit']):set(r['offsets']) for r in dependency_table(p)}
    live=set(n.live_nodes())
    for key,node in n.input_node.items():
        if key[0]=='x' and node in live:
            _,offset,field,bit=key
            assert offset==0 or offset in profile[field,bit],key
    return n,Compiled(n)


def sparse_locations(p,comp,supplied_layout):
    namespace=dict(legacy.__dict__,cached=cached,layout=layout,dependency_table=dependency_table)
    return FunctionType(legacy.sparse_locations.__code__,namespace)(p,comp,supplied_layout)


def compiler_input_map():
    namespace=dict(legacy.__dict__,sparse_locations=sparse_locations)
    return legacy.contextmanager(FunctionType(legacy.compiler_input_map.__wrapped__.__code__,namespace))()


def load_artifact(path=None):
    p=parameters()
    with np.load(path or ROOT/'figs/robustness/SP31_program.npz',allow_pickle=False) as saved:
        rom,locations=saved['rom'],saved['layout']
    assert np.array_equal(locations,layout(p))
    return machine.Candidate(p,rom,locations)
