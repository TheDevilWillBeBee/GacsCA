"""Explicit operand/output packets for the compact own-rule spatial DAG.

Compiled at initialization from one depth-independent WordCode description.
This is a route inventory; physical packet launch times are certified by a
separate scheduler, and the static upper-ROM lookup is still unresolved.
"""
from collections import Counter,defaultdict
from dataclasses import dataclass
from functools import lru_cache

from gacsca.fixed_rule import spatial_codec,spatial_epoch
from gacsca.fixed_rule import stream28_holder_rule as holder
from gacsca.fixed_rule import stream28_compact_layout as layout_module
from gacsca.fixed_rule.wordcode_and import LIT
from experiments.fixed_rule.measure_stream28_spatial_capacity import (
    PROJECTED_OUTPUT_FIELDS,SPATIAL_DYNAMIC_FIELDS)
from experiments.fixed_rule.explore_compact_topology import check as topology


@dataclass(frozen=True)
class Edge:
    source_kind:str
    source_id:object
    target_kind:str
    target_id:object
    arg_slot:int
    source_site:int
    target_site:int
    target_slot:int
    direction:int
    distance:int


@dataclass(frozen=True)
class Routes:
    edges:tuple
    gate_positions:dict
    program:object
    copies:tuple
    node_inputs:dict


@lru_cache(maxsize=8)
def build(eight_q=False,dual_pass=False,u20=False):
    facts,positions,program,copies=topology(
        include_state=True,eight_q=eight_q,dual_pass=dual_pass,u20=u20)
    layout=layout_module.build()
    n=program.inputs
    stride=holder.FIELDS+spatial_codec.FIELDS
    static_sites={wire:facts['site_start']-len(layout.static_inputs)+rank
                  for rank,wire in enumerate(layout.static_inputs)}
    dynamic_rank={item:rank for rank,item in enumerate(layout.gathered)}

    def raw_site(wire):
        if wire in static_sites:return static_sites[wire]
        neighbor,field=divmod(wire,stride)
        if field<holder.FIELDS:
            if field<len(holder.STATIC):raise AssertionError('missing static input')
            projected=field-len(holder.STATIC)
        else:
            field-=holder.FIELDS
            if field not in SPATIAL_DYNAMIC_FIELDS:
                raise AssertionError('missing spatial static input')
            projected=(len(holder.SCHEMA)-len(holder.STATIC)+
                       SPATIAL_DYNAMIC_FIELDS.index(field))
        return 8+3*dynamic_rank[(neighbor,projected)]+1

    def routed(wire):
        return wire<n or program.operations[wire-n][0]!=LIT

    depth=[0]*n
    for opcode,a,b in program.operations:
        depth.append(1 if opcode==LIT else 1+max(depth[a],depth[b]))
    consumers=defaultdict(list)
    inputs=defaultdict(list)
    for index,(opcode,a,b) in enumerate(program.operations):
        if opcode==LIT:continue
        for copy in range(copies[index]):
            for arg,wire in enumerate((a,b)):
                if routed(wire):
                    consumers[wire].append(('gate',(index,copy),arg))
    for field,full_field in enumerate(PROJECTED_OUTPUT_FIELDS):
        consumers[program.outputs[full_field]].append(('output',field,0))
    for uses in consumers.values():
        uses.sort(key=lambda item:(depth[n+item[1][0]],item[1],item[2])
                  if item[0]=='gate' else (max(depth)+1,item[1],0))

    edges=[]
    raw_buffers=0
    for wire,uses in sorted(consumers.items()):
        if wire<n:
            site=raw_site(wire)
            direct=uses[:37] if len(uses)>spatial_epoch.ROUTE_SLOTS else uses
            buffered=uses[37:] if len(uses)>spatial_epoch.ROUTE_SLOTS else ()
            if buffered:
                buffer_key=(len(program.operations)+raw_buffers,0)
                raw_buffers+=1
                if (raw_buffers>(2 if eight_q else 1) or
                        len(buffered)>spatial_epoch.ROUTE_SLOTS):
                    raise AssertionError('unsupported raw source buffer demand')
                direct=list(direct)+[('gate',buffer_key,0)]
            sources=[('raw',wire,site,use) for use in direct]
            sources.extend(('gate',buffer_key,positions[buffer_key][0],use)
                           for use in buffered)
        else:
            index=wire-n
            if len(uses)>copies[index]*spatial_epoch.ROUTE_SLOTS:
                raise AssertionError('insufficient gate copies')
            sources=[('gate',(index,ordinal//spatial_epoch.ROUTE_SLOTS),
                      positions[(index,ordinal//spatial_epoch.ROUTE_SLOTS)][0],
                      use)
                     for ordinal,use in enumerate(uses)]
        for source_kind,source_id,source_site,use in sources:
            target_kind,target_id,arg=use
            if target_kind=='gate':
                target_site,target_slot=positions[target_id][:2]
                direction=0
                distance=(target_site-source_site)%spatial_epoch.Q or spatial_epoch.Q
                inputs[target_id].append(len(edges))
            else:
                target_site=layout.hold[target_id]
                target_slot=3
                direction=1
                distance=(source_site-target_site)%spatial_epoch.Q or spatial_epoch.Q
            edges.append(Edge(source_kind,source_id,target_kind,target_id,arg,
                              source_site,target_site,target_slot,direction,
                              distance))
    assert raw_buffers==(2 if eight_q else 1)
    assert len([edge for edge in edges if edge.target_kind=='output'])==119
    gate_load=Counter(edge.source_id for edge in edges
                      if edge.source_kind=='gate')
    assert max(gate_load.values())<=38
    return Routes(tuple(edges),positions,program,copies,dict(inputs))
