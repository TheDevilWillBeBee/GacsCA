"""Finite-radius Address broadcast and one-lap static-word retrieval prototype.

This is an explicit alphabet extension of the U20 rule, not a certificate of
the old 421-word rule or an integrated own-rule evaluator. Each source sends
one token per period. Tokens advance one physical site per tick; distinct
source sites preserve spacing and therefore do not collide on the ring.
"""
from dataclasses import dataclass
import numpy as np

from .. import stream28_compact_layout as layout_module
from .. import spatial_codec8
from .. import stream28_dual_holder_rule20 as holder
from .. import stream28_dual_pass20 as physical
from .. import stream28_holder_projected as projected_holder
from experiments.fixed_rule.build_compact8_circuit import static_plan
from .corrected_circuit import corrected_initial_data


Q=physical.Q
ADDRESS_SOURCE=layout_module.build().info[projected_holder.COL['address']]
EVOLVING_BUS=('address_register','broadcast_valid','broadcast_value',
              'packet_valid','packet_source','packet_target','packet_field',
              'packet_fetched','packet_value')
OWN_FIELDS=physical.FIELDS+3+len(EVOLVING_BUS)


def static_source_metadata():
    """Immutable lower metadata chosen only by the physical source site."""
    with corrected_initial_data():
        plan=static_plan(True,True)
        wires=tuple(layout_module.build().static_inputs)
    site_by_wire={wire:site for site,wire in plan['raw_sources'].items()}
    # Seven unused static inputs were removed by the compiler. Reserve exactly
    # the seven vacant positions in the otherwise contiguous SOURCE interval.
    source_sites=set(site_by_wire.values())
    free=[site for site in range(2828,3218) if site not in source_sites
          and site not in plan['at_site'] and site not in plan['sink_sites']]
    missing=[wire for wire in wires if wire not in site_by_wire]
    if len(free)!=7 or len(missing)!=7:
        raise AssertionError(('static SOURCE geometry changed',len(free),len(missing)))
    site_by_wire.update(zip(missing,free))
    table=np.zeros((Q,3),dtype=np.int32)
    for wire in wires:
        neighbor,field=divmod(wire,physical.FIELDS)
        site=site_by_wire[wire]
        table[site]=(1,neighbor,field)
    if int(np.count_nonzero(table[:,0]==1))!=390:
        raise AssertionError('not all 390 static fields assigned')
    return table,site_by_wire


def successor_static_source_metadata():
    """Provisional 393-source lookup table for this rule's own static inputs.

    The three added sites overlap the predecessor evaluator gate bank. This
    table certifies the lookup component, not an integrated own-rule ROM.
    """
    from . import successor_optimized
    from ..wordcode_and import LIT
    program=successor_optimized.build()
    old_table,old_sites=static_source_metadata()
    predecessor={(wire//physical.FIELDS,wire%physical.FIELDS):old_sites[wire]
                 for wire in layout_module.build().static_inputs}
    spatial_dynamic={1,3,*range(spatial_codec8.FIELDS-12,
                                spatial_codec8.FIELDS)}
    static_fields=set(range(len(holder.STATIC)))
    static_fields.update(holder.FIELDS+field
                         for field in range(spatial_codec8.FIELDS)
                         if field not in spatial_dynamic)
    static_fields.update(range(physical.FIELDS,physical.FIELDS+3))
    used={wire for opcode,a,b in program.operations if opcode!=LIT
          for wire in (a,b) if wire<program.inputs}
    used.update(wire for wire in program.outputs if wire<program.inputs)
    requested=tuple(sorted((wire//OWN_FIELDS,wire%OWN_FIELDS)
                           for wire in used if wire%OWN_FIELDS in static_fields))
    if len(requested)!=393:
        raise AssertionError(('own static dependency count changed',len(requested)))
    missing=set(predecessor)-set(requested)
    new=tuple(key for key in requested if key not in predecessor)
    if missing or len(new)!=3 or any(field<physical.FIELDS for _,field in new):
        raise AssertionError(('own static dependency classification changed',
                              missing,new))
    site_by_key={key:predecessor[key] for key in requested if key in predecessor}
    site_by_key.update(zip(new,(3218,3219,3220)))
    table=np.copy(old_table)
    for key in new:
        site=site_by_key[key]
        table[site]=(1,*key)
    if len(set(site_by_key.values()))!=393:
        raise AssertionError('static source site collision')
    return table,site_by_key


@dataclass
class Bus:
    address_register:np.ndarray
    broadcast_valid:np.ndarray
    broadcast_value:np.ndarray
    packet_valid:np.ndarray
    packet_source:np.ndarray
    packet_target:np.ndarray
    packet_field:np.ndarray
    packet_fetched:np.ndarray
    packet_value:np.ndarray
    metadata:np.ndarray

    @classmethod
    def empty(cls,n,metadata):
        if n%Q:raise ValueError('whole physical colonies required')
        return cls(np.zeros(n,np.uint16),np.zeros(n,np.bool_),
                   np.zeros(n,np.uint16),np.zeros(n,np.bool_),
                   np.zeros(n,np.uint16),np.zeros(n,np.uint16),
                   np.zeros(n,np.uint16),np.zeros(n,np.bool_),
                   np.zeros(n,np.uint64),np.tile(metadata,(n//Q,1)))


def step(raw,bus):
    """One synchronous radius-three bus transition, using only local ROM.

    `raw` is the previous complete lower state. Returned writes are fivefold
    Data assignments for the simultaneous physical base-rule transition.
    The physical Age word supplies phase; no host tick selects a rule.
    """
    n=len(raw)
    if raw.shape not in ((n,physical.FIELDS),(n,OWN_FIELDS)) or n%Q:
        raise ValueError('complete lower raw ring required')
    age=raw[:,holder.COL['age']]
    address=raw[:,holder.COL['address']].astype(np.uint16)
    new=Bus(*(np.copy(getattr(bus,name)) for name in
              ('address_register','broadcast_valid','broadcast_value',
               'packet_valid','packet_source','packet_target','packet_field',
               'packet_fetched','packet_value','metadata')))
    writes={}
    first=age==0
    launch=first & (address==ADDRESS_SOURCE)
    new.broadcast_valid[first]=launch[first]
    if np.any(launch):
        new.broadcast_value[launch]=(raw[launch,holder.COL['s2_data']] &
                                     np.uint64(Q-1)).astype(np.uint16)
        new.address_register[launch]=new.broadcast_value[launch]
    new.packet_valid[first]=False
    broadcast=(age>0)&(age<Q)
    if np.any(broadcast):
        shifted_valid=np.roll(bus.broadcast_valid,1)
        shifted_value=np.roll(bus.broadcast_value,1)
        new.broadcast_valid[broadcast]=shifted_valid[broadcast]
        new.broadcast_value[broadcast]=shifted_value[broadcast]
        received=broadcast & new.broadcast_valid
        new.address_register[received]=new.broadcast_value[received]
    request=age==Q
    if np.any(request):
        new.broadcast_valid[request]=False
        enabled=request & (bus.metadata[:,0]==1)
        new.packet_valid[request]=enabled[request]
        new.packet_source[request]=address[request]
        new.packet_target[request]=(bus.address_register[request].astype(np.int32)+
                                    bus.metadata[request,1]-7)%Q
        new.packet_field[request]=bus.metadata[request,2]
        new.packet_fetched[request]=False
        new.packet_value[request]=0
    flight=(age>Q)&(age<=2*Q)
    if np.any(flight):
        for name in ('packet_valid','packet_source','packet_target',
                     'packet_field','packet_fetched','packet_value'):
            shifted=np.roll(getattr(bus,name),1)
            getattr(new,name)[flight]=shifted[flight]
        match=(flight & new.packet_valid & (~new.packet_fetched) &
               (new.packet_target==address))
        if np.any(match):
            at=np.flatnonzero(match)
            legal=at[new.packet_field[at]<raw.shape[1]]
            extra=at[(new.packet_field[at]>=raw.shape[1]) &
                     (new.packet_field[at]<OWN_FIELDS)]
            illegal=at[new.packet_field[at]>=OWN_FIELDS]
            new.packet_value[legal]=raw[legal,new.packet_field[legal]]
            if extra.size:
                if raw.shape[1]!=physical.FIELDS:
                    raise AssertionError('unexpected full successor field gap')
                for site in extra:
                    field=int(new.packet_field[site])-physical.FIELDS
                    new.packet_value[site]=(bus.metadata[site,field]
                        if field<3 else
                        getattr(bus,EVOLVING_BUS[field-3])[site])
            new.packet_value[illegal]=0
            new.packet_fetched[at]=True
    commit=age==2*Q+1
    if np.any(commit):
        # The packet reached its physical source at the previous tick. Its
        # fetched value is now visible to all five nearby holders.
        for d in holder.OFFSETS:
            src=np.roll(bus.packet_source,-d)
            valid=np.roll(bus.packet_valid & bus.packet_fetched,-d)
            at=commit & valid & (src==(address.astype(np.int32)+d)%Q)
            writes[d]=(at,np.roll(bus.packet_value,-d))
        new.packet_valid[commit]=False
    return new,writes


def advance_lookup_only(raw,bus):
    """Standalone local lookup dynamics for protocol tests; no F claim."""
    next_bus,writes=step(raw,bus)
    out=raw.copy()
    for d,(mask,value) in writes.items():
        out[mask,holder.COL[f's{d+2}_data']]=value[mask]
    out[:,holder.COL['age']]=(out[:,holder.COL['age']]+1)%physical.U
    return out,next_bus
