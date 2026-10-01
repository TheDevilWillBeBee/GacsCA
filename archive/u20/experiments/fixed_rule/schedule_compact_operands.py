"""Event schedule of explicit compact own-rule operand packets and gates.

This deliberately excludes final leftward Hold outputs and static-ROM lookup.
Times beyond 4Q are exploratory because the current spatial local rule has a
15-bit Age and a 4Q reset. No simulated transition uses this scheduler.
"""
import argparse
from collections import Counter,defaultdict
import hashlib
import heapq
from itertools import count
import json
from pathlib import Path

from gacsca.fixed_rule import spatial_epoch
from gacsca.fixed_rule.wordcode_and import LIT
from experiments.fixed_rule import stream28_compact_routes as compiler


def schedule(deadline=8*spatial_epoch.Q,*,eight_q=False,
             dual_pass=False,u20=False,include_state=False):
    routes=compiler.build(eight_q,dual_pass,u20)
    program=routes.program
    edge_ids=tuple(i for i,e in enumerate(routes.edges)
                   if e.target_kind=='gate')
    nodes=routes.gate_positions
    site_nodes=defaultdict(list)
    for key,(site,slot,_) in nodes.items():site_nodes[site].append(key)
    for site,keys in site_nodes.items():
        keys.sort(key=lambda key:nodes[key][1])
        assert all(nodes[key][1]==slot for slot,key in enumerate(keys))
    active={site:0 for site in site_nodes}
    site_switches=defaultdict(list)
    inbound=Counter(e.target_id for e in routes.edges
                    if e.target_kind=='gate')
    emitter_edges=defaultdict(list)
    depth=[0]*program.inputs
    for opcode,a,b in program.operations:
        depth.append(1 if opcode==LIT else 1+max(depth[a],depth[b]))
    for edge_id in edge_ids:
        edge=routes.edges[edge_id]
        emitter_edges[(edge.source_kind,edge.source_id)].append(edge_id)
    for edge_list in emitter_edges.values():
        edge_list.sort(key=lambda edge_id:(
            depth[program.inputs+routes.edges[edge_id].target_id[0]]
            if routes.edges[edge_id].target_id[0]<len(program.operations)
            else 1,
            routes.edges[edge_id].target_id,
            routes.edges[edge_id].arg_slot))
    next_edge={key:0 for key in emitter_edges}
    done={}
    launched=[-1]*len(routes.edges)
    arrived=[-1]*len(routes.edges)
    phases={}
    events=[]
    sequence=count()
    def push(t,priority,kind,item):
        heapq.heappush(events,(t,priority,next(sequence),kind,item))
    def activate(key,t):
        if inbound[key]==0:push(t+1,1,'complete',key)
    for site,keys in site_nodes.items():activate(keys[0],0)
    for emitter in emitter_edges:
        if emitter[0]=='raw':push(1,3,'emit',emitter)
    completed=emitted=delivered=loops=blocked=0
    latest_event=0
    while events:
        t,_,_,kind,item=heapq.heappop(events)
        latest_event=t
        if t>=deadline:
            return dict(passed=False,deadline=deadline,
                        failed_event=(kind,str(item),t),
                        gates_completed=completed,
                        operand_packets_emitted=emitted,
                        operand_packets_delivered=delivered,
                        loops=loops,blocked_phase_attempts=blocked)
        if kind=='switch':
            site=item
            old=site_nodes[site][active[site]]
            if old not in done or next_edge.get(('gate',old),0)!=len(
                    emitter_edges.get(('gate',old),())):
                raise AssertionError(('premature gate-site switch',site,t))
            active[site]+=1
            site_switches[site].append(t)
            activate(site_nodes[site][active[site]],t)
        elif kind=='complete':
            key=item
            site=nodes[key][0]
            if site_nodes[site][active[site]]!=key or inbound[key]!=0 or key in done:
                raise AssertionError(('invalid gate completion',key,t))
            done[key]=t
            completed+=1
            emitter=('gate',key)
            if emitter in emitter_edges:push(t+1,3,'emit',emitter)
            elif active[site]+1<len(site_nodes[site]):
                push(t+1,0,'switch',site)
        elif kind=='hit':
            edge_id=item
            edge=routes.edges[edge_id]
            phase=(edge.source_site-launched[edge_id])%spatial_epoch.Q
            if phases.get(phase)!=edge_id:
                raise AssertionError(('packet phase lost',edge_id,t))
            site=edge.target_site
            target=edge.target_id
            current=site_nodes[site][active[site]]
            if current==target:
                del phases[phase]
                arrived[edge_id]=t
                delivered+=1
                inbound[target]-=1
                if inbound[target]<0:raise AssertionError('double delivery')
                if inbound[target]==0:push(t+1,1,'complete',target)
            elif active[site]<edge.target_slot:
                loops+=1
                push(t+spatial_epoch.Q,2,'hit',edge_id)
            else:
                raise AssertionError(('packet missed target slot',edge_id,t,
                                      current,target))
        elif kind=='emit':
            emitter=item
            position=next_edge[emitter]
            edges=emitter_edges[emitter]
            if position>=len(edges):raise AssertionError('empty emitter')
            edge_id=edges[position]
            edge=routes.edges[edge_id]
            site=edge.source_site
            if emitter[0]=='gate':
                gate=emitter[1]
                if (gate not in done or done[gate]>=t or
                        site_nodes[site][active[site]]!=gate):
                    raise AssertionError(('inactive source',gate,t))
            phase=(site-t)%spatial_epoch.Q
            if phase in phases:
                blocked+=1
                push(t+1,3,'emit',emitter)
                continue
            phases[phase]=edge_id
            launched[edge_id]=t
            emitted+=1
            next_edge[emitter]=position+1
            push(t+edge.distance,2,'hit',edge_id)
            if position+1<len(edges):push(t+1,3,'emit',emitter)
            elif emitter[0]=='gate' and active[site]+1<len(site_nodes[site]):
                push(t+1,0,'switch',site)
        else:raise AssertionError('unknown event')
    if (len(done)!=len(nodes) or emitted!=len(edge_ids) or
            delivered!=len(edge_ids) or phases):
        raise AssertionError(('incomplete operand schedule',len(done),
                              emitted,delivered,len(phases)))
    summary=dict(passed=True,deadline=deadline,
                description_sha256=program.digest(),
                gate_instances=len(nodes),operand_packets=len(edge_ids),
                latest_gate_completion=max(done.values()),
                latest_packet_launch=max(launched),
                latest_packet_arrival=max(arrived),
                latest_event=latest_event,
                site_switches=sum(len(keys)-1 for keys in site_nodes.values()),
                packet_target_laps=loops,
                blocked_phase_attempts=blocked,
                margin=deadline-latest_event,
                limitation='Analytical rightward operand schedule only; '
                           'output routes, static ROM lookup, physical '
                           'Age width and continuous replay unresolved.')
    return (summary,done,tuple(launched),tuple(arrived),
            dict(site_switches)) if include_state else summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--deadline',type=int,default=8*spatial_epoch.Q)
    parser.add_argument('--eight-q',action='store_true')
    parser.add_argument('--dual-pass',action='store_true')
    parser.add_argument('--u20',action='store_true')
    args=parser.parse_args()
    result=schedule(args.deadline,eight_q=args.eight_q,
                    dual_pass=args.dual_pass,u20=args.u20)
    result['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    print(json.dumps(result,indent=2))
    if args.output:
        if args.output.exists():raise FileExistsError(args.output)
        args.output.write_text(json.dumps(result,indent=2)+'\n')
