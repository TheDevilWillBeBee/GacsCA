"""Event-driven candidate schedule for the complete fixed-rule evaluator DAG.

The schedule enforces one dynamic gate per site, encoded site switches,
one emission per site/tick, target-slot pass-through, and collision-free
moving phases. It is an analytical compiler, not a physical CA replay.
"""
import argparse
from collections import Counter,defaultdict
from dataclasses import dataclass
import hashlib
import heapq
from itertools import count
import json
from pathlib import Path

from gacsca.fixed_rule import spatial_epoch as physical
from gacsca.fixed_rule import spatial_fanout_compiler as compiler
from gacsca.fixed_rule import stream28_holder_program as reference
from gacsca.fixed_rule.wordcode_and import LIT
from experiments.fixed_rule.explore_spatial_topology import explore


@dataclass(frozen=True)
class Schedule:
    summary:dict
    gate_done:dict
    route_launch:tuple
    route_arrival:tuple
    site_switches:dict
    output_sinks:dict


def schedule(include_outputs=False,output_layout='bank',deadline=None):
    if output_layout not in ('bank','hold','hold_left'):
        raise ValueError('output layout must be bank, hold, or hold_left')
    if deadline is None:deadline=physical.PERIOD
    compiled=compiler.compile_capacity()
    placement=explore()
    program=reference.compiled_description()
    nodes={(node.gate_index,node.copy):node for node in compiled.nodes}
    site_nodes=defaultdict(list)
    for key in nodes:site_nodes[placement.sites[key]].append(key)
    for gates in site_nodes.values():gates.sort(key=lambda key:placement.slots[key])
    active_slot={site:0 for site in site_nodes}
    switches=defaultdict(list)
    inbound=Counter((use.consumer_gate,use.consumer_copy) for use in compiled.uses)
    done={}
    phases={}
    emitter_edges=defaultdict(list)
    source_site=[]
    target_site=[]
    distance=[]
    output_sinks={}
    ordinary_edges=len(compiled.uses)
    depth=[0]*program.inputs
    for opcode,a,b in program.operations:
        depth.append(1 if opcode==LIT else 1+max(depth[a],depth[b]))
    for edge,use in enumerate(compiled.uses):
        target=(use.consumer_gate,use.consumer_copy)
        source=(use.source_gate,use.source_copy)
        src_at=(use.source_site if use.source_gate<0 else placement.sites[source])
        dst_at=placement.sites[target]
        source_site.append(src_at)
        target_site.append(dst_at)
        distance.append((dst_at-src_at)%physical.Q or physical.Q)
        emitter=('raw',src_at) if use.source_gate<0 else ('gate',source)
        emitter_edges[emitter].append(edge)
    if include_outputs and output_layout!='hold_left':
        layout=reference.layout()
        raw_sites={use.source_site for use in compiled.uses if use.source_gate<0}
        raw_sites.update(layout.wires[wire] for wire in program.outputs
                         if wire<program.inputs)
        available=(site for site in range(layout.memory_count)
                   if site not in raw_sites)
        for field,wire in enumerate(program.outputs):
            if output_layout=='bank' and wire<program.inputs:continue
            sink=(layout.hold[field] if output_layout=='hold' else next(available))
            source=(wire-program.inputs,0)
            src_at=(layout.wires[wire] if wire<program.inputs else
                    placement.sites[source])
            edge=len(source_site)
            output_sinks[wire]=sink
            source_site.append(src_at)
            target_site.append(sink)
            distance.append((sink-src_at)%physical.Q or physical.Q)
            emitter=('raw',src_at) if wire<program.inputs else ('gate',source)
            emitter_edges[emitter].append(edge)
    launched=[-1]*len(source_site)
    arrived=[-1]*len(source_site)
    for edges in emitter_edges.values():
        edges.sort(key=lambda edge:(
            (depth[program.inputs+compiled.uses[edge].consumer_gate],
             compiled.uses[edge].consumer_gate,
             compiled.uses[edge].consumer_copy,
             compiled.uses[edge].arg_slot) if edge<ordinary_edges else
            (len(depth),edge,0,0)))
    next_edge={emitter:0 for emitter in emitter_edges}

    events=[]
    sequence=count()
    def push(t,priority,kind,payload):
        heapq.heappush(events,(t,priority,next(sequence),kind,payload))
    def activate(key,t):
        if inbound[key]==0:push(t+1,1,'complete',key)
    for site,gates in site_nodes.items():activate(gates[0],0)
    for emitter in emitter_edges:
        if emitter[0]=='raw':push(1,3,'emit',emitter)
    emissions=0
    deliveries=0
    loops=0
    blocked_phase_attempts=0
    last_tick=0
    while events:
        t,_,_,kind,item=heapq.heappop(events)
        last_tick=t
        if t>=deadline:
            raise AssertionError(('missed fixed evaluator window',kind,item,t,
                                  len(done),emissions,deliveries))
        if kind=='switch':
            site=item
            old_slot=active_slot[site]
            old=site_nodes[site][old_slot]
            if old not in done or next_edge.get(('gate',old),0)!=len(emitter_edges.get(('gate',old),())):
                raise AssertionError('site switched before old result was finished')
            active_slot[site]+=1
            new=site_nodes[site][active_slot[site]]
            switches[site].append(t)
            activate(new,t)
        elif kind=='complete':
            key=item
            site=placement.sites[key]
            if site_nodes[site][active_slot[site]]!=key or inbound[key]!=0 or key in done:
                raise AssertionError(('gate completion invalid',key,t))
            done[key]=t
            emitter=('gate',key)
            if emitter in emitter_edges:
                push(t+1,3,'emit',emitter)
            elif active_slot[site]+1<len(site_nodes[site]):
                push(t+1,0,'switch',site)
        elif kind=='hit':
            edge=item
            phase=(source_site[edge]-launched[edge])%physical.Q
            if phases.get(phase)!=edge:raise AssertionError('moving packet phase lost')
            site=target_site[edge]
            if edge>=ordinary_edges:
                del phases[phase]
                arrived[edge]=t
                deliveries+=1
                continue
            use=compiled.uses[edge]
            target=(use.consumer_gate,use.consumer_copy)
            current=site_nodes[site][active_slot[site]]
            if current==target:
                del phases[phase]
                arrived[edge]=t
                deliveries+=1
                inbound[target]-=1
                if inbound[target]<0:raise AssertionError('duplicate operand delivery')
                if inbound[target]==0:push(t+1,1,'complete',target)
            elif active_slot[site]<placement.slots[target]:
                loops+=1
                push(t+physical.Q,2,'hit',edge)
            else:
                raise AssertionError(('packet missed target gate slot',edge,t,current,target))
        elif kind=='emit':
            emitter=item
            position=next_edge[emitter]
            edges=emitter_edges[emitter]
            if position>=len(edges):raise AssertionError('empty emission request')
            if emitter[0]=='gate':
                gate=emitter[1]
                site=placement.sites[gate]
                if gate not in done or done[gate]>=t or site_nodes[site][active_slot[site]]!=gate:
                    raise AssertionError(('inactive source emitted',gate,t))
            else:site=emitter[1]
            phase=(site-t)%physical.Q
            if phase in phases:
                blocked_phase_attempts+=1
                push(t+1,3,'emit',emitter)
                continue
            edge=edges[position]
            phases[phase]=edge
            launched[edge]=t
            emissions+=1
            next_edge[emitter]=position+1
            push(t+distance[edge],2,'hit',edge)
            if position+1<len(edges):
                push(t+1,3,'emit',emitter)
            elif emitter[0]=='gate' and active_slot[site]+1<len(site_nodes[site]):
                push(t+1,0,'switch',site)
        else:raise AssertionError('unknown event')

    if include_outputs and output_layout=='hold_left':
        layout=reference.layout()
        start=max(last_tick,max(done.values()))+1
        seen_phases=set()
        for field,wire in enumerate(program.outputs):
            source=(wire-program.inputs,0)
            src_at=(layout.wires[wire] if wire<program.inputs else
                    placement.sites[source])
            sink=layout.hold[field]
            phase=(src_at+start)%physical.Q
            if phase in seen_phases:
                raise AssertionError(('leftward output phase collision',field,phase))
            seen_phases.add(phase)
            output_sinks[wire]=sink
            source_site.append(src_at)
            target_site.append(sink)
            travel=(src_at-sink)%physical.Q or physical.Q
            distance.append(travel)
            launched.append(start)
            arrived.append(start+travel)
        emissions+=len(output_sinks)
        deliveries+=len(output_sinks)
        last_tick=max(last_tick,max(arrived))
        if last_tick>=deadline:
            raise AssertionError(('leftward Hold output missed deadline',last_tick,deadline))

    if (len(done)!=len(nodes) or emissions!=len(source_site) or
            deliveries!=len(source_site) or phases):
        raise AssertionError(('incomplete schedule',len(done),emissions,deliveries,len(phases)))
    if any(len(times)>physical.GATE_SLOTS-1 for times in switches.values()):
        raise AssertionError('too many encoded site switches')
    if max(launched)>=physical.PERIOD:
        raise AssertionError('launch outside encoded 15-bit work age')
    output_done=max(done[(wire-program.inputs,0)] for wire in program.outputs
                    if wire>=program.inputs)
    output_commit=max(arrived[ordinary_edges:],default=output_done)
    summary=dict(passed=True,description_sha256=program.digest(),Q=physical.Q,
                 compiler_source_sha256=hashlib.sha256(Path(compiler.__file__).read_bytes()).hexdigest(),
                 physical_rule_source_sha256=hashlib.sha256(Path(physical.__file__).read_bytes()).hexdigest(),
                 topology_source_sha256=hashlib.sha256(Path(explore.__code__.co_filename).read_bytes()).hexdigest(),
                 rule_width_bits=physical.WIDTH,
                 gate_instances=len(nodes),operand_packets=len(compiled.uses),
                 output_packets=len(output_sinks),
                 output_layout=output_layout if include_outputs else 'none',
                 gate_completions=len(done),packet_emissions=emissions,
                 packet_deliveries=deliveries,packet_target_passes=loops,
                 blocked_phase_attempts=blocked_phase_attempts,
                 encoded_site_switches=sum(map(len,switches.values())),
                 latest_gate_completion=max(done.values()),
                 latest_output_completion=output_done,
                 latest_output_commit=output_commit,
                 latest_packet_launch=max(launched),
                 latest_packet_arrival=max(arrived),
                 event_queue_last_tick=last_tick,
                 physical_period=physical.PERIOD,
                 deadline=deadline,margin=deadline-last_tick,
                 needs_stage_gating=last_tick>=physical.PERIOD,
                 limitation='Analytical healthy schedule with phase exclusion; '
                            'not a continuous physical replay or '
                            'self-reference closure.')
    return Schedule(summary,done,tuple(launched),tuple(arrived),dict(switches),
                    output_sinks)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--include-outputs',action='store_true')
    parser.add_argument('--output-layout',choices=('bank','hold','hold_left'),default='bank')
    parser.add_argument('--deadline',type=int)
    args=parser.parse_args()
    result=schedule(args.include_outputs,args.output_layout,args.deadline).summary
    result['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    print(json.dumps(result,indent=2))
    if args.output:
        if args.output.exists():raise FileExistsError(args.output)
        args.output.write_text(json.dumps(result,indent=2)+'\n')
