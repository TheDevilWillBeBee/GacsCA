"""Encode the changed 8Q own-F DAG into the fixed spatial local alphabet.

The 390 upper static words are supplied by the caller. This is a diagnostic
one-macrostep initialization, not a self-referential address lookup or a
depth-dependent physical transition.
"""
from collections import Counter,defaultdict
from dataclasses import replace
from functools import lru_cache

from gacsca.fixed_rule import spatial_epoch8 as physical
from gacsca.fixed_rule.wordcode_and import LIT,AND,MASK
from experiments.fixed_rule import stream28_compact_routes as compiler
from experiments.fixed_rule.schedule_compact_operands import schedule


@lru_cache(maxsize=3)
def static_plan(dual_pass=False,u20=False):
    routes=compiler.build(True,dual_pass,u20)
    timing,done,launches,arrivals,switches=schedule(
        physical.PERIOD,eight_q=True,dual_pass=dual_pass,u20=u20,
        include_state=True)
    assert timing['passed']
    output_launch=timing['latest_event']+1
    assert output_launch<physical.PERIOD
    program=routes.program
    at_site=defaultdict(list)
    for key,(site,slot,weight) in routes.gate_positions.items():
        at_site[site].append((slot,key))
    output_sources={edge.source_id for edge in routes.edges
                    if edge.target_kind=='output'}
    assert len(output_sources)==119
    raw_sources={}
    sink_sites=set()
    route_rows=defaultdict(list)
    for edge_id,edge in enumerate(routes.edges):
        if edge.source_kind=='raw':
            old=raw_sources.setdefault(edge.source_site,edge.source_id)
            if old!=edge.source_id:
                raise AssertionError('two raw words share a physical source')
        if edge.target_kind=='output':
            sink_sites.add(edge.target_site)
            launch=output_launch
        else:launch=launches[edge_id]
        if launch<0 or launch>=physical.PERIOD:
            raise AssertionError(('encoded route launch out of 8Q',edge_id))
        route_rows[edge.source_site].append(physical.Route(
            1,edge.target_site,edge.arg_slot,edge.target_slot,
            routes.gate_positions[edge.source_id][1]
            if edge.source_kind=='gate' else 0,launch))
    assert len(sink_sites)==119
    assert all(len(rows)<=physical.ROUTE_SLOTS
               for rows in route_rows.values())
    assert not (set(raw_sources)&set(at_site) or set(raw_sources)&sink_sites
                or set(at_site)&sink_sites)
    return dict(routes=routes,timing=timing,done=done,
                launches=launches,arrivals=arrivals,switches=switches,
                at_site=dict(at_site),output_sources=output_sources,
                raw_sources=raw_sources,sink_sites=sink_sites,
                route_rows=dict(route_rows),output_launch=output_launch)


def initial_cells(words,dual_pass=False,u20=False):
    plan=static_plan(dual_pass,u20)
    program=plan['routes'].program
    if len(words)!=program.inputs or any(not 0<=int(value)<1<<64
                                        for value in words):
        raise ValueError('all 6315 typed full-rule input words required')
    rows=[physical.Cell(address=site) for site in range(physical.Q)]
    for site,wire in plan['raw_sources'].items():
        rows[site]=replace(rows[site],kind=physical.SOURCE,
                           source_value=int(words[wire]))
    for site in plan['sink_sites']:
        rows[site]=replace(rows[site],kind=physical.OUTPUT)
    for site,slot_keys in plan['at_site'].items():
        gate_specs=list(physical.EMPTY_GATES)
        for slot,key in slot_keys:
            index,copy=key
            if index in (len(program.operations),
                         len(program.operations)+1):
                opcode=AND
                literal=0
                preload0=0
                preload1=MASK
                preload_ready=2
            else:
                opcode,a,b=program.operations[index]
                literal=a if opcode==LIT else 0
                preload=[0,0]
                ready=0
                if opcode!=LIT:
                    for arg,wire in enumerate((a,b)):
                        if (wire>=program.inputs and
                                program.operations[wire-program.inputs][0]==LIT):
                            preload[arg]=program.operations[wire-program.inputs][1]
                            ready|=1<<arg
                preload0,preload1=preload
                preload_ready=ready
                if key in plan['output_sources']:
                    opcode=physical.OUTPUT_OPCODE[opcode]
            gate_specs[slot]=physical.GateSpec(
                1,opcode,literal,index&((1<<14)-1),
                preload0,preload1,preload_ready)
        ages=tuple(plan['switches'].get(site,()))
        if len(ages)!=len(slot_keys)-1:
            raise AssertionError(('wrong encoded site switches',site,ages))
        ages=ages+(0,)*(physical.GATE_SLOTS-1-len(ages))
        first=gate_specs[0]
        rows[site]=replace(rows[site],kind=physical.GATE,
                           gates=tuple(gate_specs),switch_ages=ages,
                           arg0=first.preload0,arg1=first.preload1,
                           ready=first.preload_ready)
    for site,routes in plan['route_rows'].items():
        rows[site]=replace(rows[site],routes=tuple(routes)+
                           (physical.EMPTY_ROUTE,)*
                           (physical.ROUTE_SLOTS-len(routes)))
    return tuple(rows)
