"""Candidate full-DAG local-mail timing with gate lifetimes and ring laps.

This schedules every gate and packet under site gate order, one outgoing
packet per site/tick, and pass-through at an inactive target gate slot. It
audits same-lane phase conflicts afterward; conflicts make the candidate
invalid until launch times are adjusted. It is not a physical CA replay.
"""
import argparse
from collections import Counter,defaultdict,deque
import hashlib
import json
from pathlib import Path

from gacsca.fixed_rule import spatial_epoch as physical
from gacsca.fixed_rule import spatial_fanout_compiler as compiler
from gacsca.fixed_rule import stream28_holder_program as reference
from gacsca.fixed_rule.wordcode_and import LIT
from experiments.fixed_rule.explore_spatial_topology import explore


def analyze():
    compiled=compiler.compile_capacity()
    placement=explore()
    program=reference.compiled_description()
    keys=[(node.gate_index,node.copy) for node in compiled.nodes]
    node_index={key:index for index,key in enumerate(keys)}
    N=len(keys);M=len(compiled.uses);V=2*N+2*M
    adjacency=[[] for _ in range(V)]
    indegree=[0]*V
    times=[0]*V
    distance=[0]*M
    target_index=[0]*M
    source_site=[0]*M
    depth=[0]*program.inputs
    for opcode,a,b in program.operations:
        depth.append(1 if opcode==LIT else 1+max(depth[a],depth[b]))
    def A(index):return index
    def C(index):return N+index
    def L(edge):return 2*N+edge
    def T(edge):return 2*N+M+edge
    def link(source,target,delay):
        adjacency[source].append((target,delay))
        indegree[target]+=1

    for index in range(N):link(A(index),C(index),1)
    by_site=defaultdict(list)
    for key in keys:by_site[placement.sites[key]].append(key)
    next_node={}
    for nodes in by_site.values():
        nodes.sort(key=lambda key:placement.slots[key])
        for old,new in zip(nodes,nodes[1:]):
            link(C(node_index[old]),A(node_index[new]),1)
            next_node[old]=node_index[new]

    emitters=defaultdict(list)
    for edge,use in enumerate(compiled.uses):
        target=(use.consumer_gate,use.consumer_copy)
        source=(use.source_gate,use.source_copy)
        target_at=placement.sites[target]
        source_at=(use.source_site if use.source_gate<0 else placement.sites[source])
        distance[edge]=(target_at-source_at)%physical.Q or physical.Q
        source_site[edge]=source_at
        target_index[edge]=node_index[target]
        link(A(node_index[target]),T(edge),0)
        link(L(edge),T(edge),0)
        link(T(edge),C(node_index[target]),1)
        if use.source_gate<0:
            times[L(edge)]=1
            emitter=('raw',source_at)
        else:
            link(C(node_index[source]),L(edge),1)
            if source in next_node:
                link(L(edge),A(next_node[source]),1)
            emitter=('gate',source)
        emitters[emitter].append(edge)

    # Local hardware emits at most one outgoing packet in each tick.
    for edges in emitters.values():
        edges.sort(key=lambda edge:(
            depth[program.inputs+compiled.uses[edge].consumer_gate],
            compiled.uses[edge].consumer_gate,
            compiled.uses[edge].consumer_copy,
            compiled.uses[edge].arg_slot))
        for earlier,later in zip(edges,edges[1:]):link(L(earlier),L(later),1)

    queue=deque(index for index,count in enumerate(indegree) if count==0)
    visited=0
    lap_histogram=Counter()
    while queue:
        event=queue.popleft();visited+=1
        if event>=2*N+M:
            edge=event-(2*N+M)
            nominal=times[L(edge)]+distance[edge]
            active_at=times[A(target_index[edge])]
            laps=max(0,(active_at-nominal+physical.Q-1)//physical.Q)
            times[event]=nominal+laps*physical.Q
            lap_histogram[laps]+=1
        for successor,delay in adjacency[event]:
            times[successor]=max(times[successor],times[event]+delay)
            indegree[successor]-=1
            if indegree[successor]==0:queue.append(successor)
    if visited!=V:raise AssertionError('event precedence cycle')

    phase_intervals=defaultdict(list)
    for edge in range(M):
        launch=times[L(edge)]
        arrival=times[T(edge)]
        phase=(source_site[edge]-launch)%physical.Q
        phase_intervals[phase].append((launch,arrival,edge))
    conflicts=[]
    for phase,intervals in phase_intervals.items():
        intervals.sort()
        latest_end=-1;latest_edge=-1
        for launch,arrival,edge in intervals:
            if launch<latest_end:
                conflicts.append((phase,latest_edge,edge,launch,latest_end))
            if arrival>latest_end:latest_end,latest_edge=arrival,edge
    output_keys=[(wire-program.inputs,0) for wire in program.outputs
                 if wire>=program.inputs]
    return dict(description_sha256=program.digest(),Q=physical.Q,
                rule_width_bits=physical.WIDTH,
                event_graph_nodes=V,
                precedence_arcs=sum(map(len,adjacency)),
                gate_instances=N,operand_packets=M,
                one_packet_per_emitter_tick=True,
                latest_gate_completion=max(times[N:2*N]),
                latest_output_completion=max(times[C(node_index[key])]
                                             for key in output_keys),
                latest_launch=max(times[2*N:2*N+M]),
                latest_arrival=max(times[2*N+M:]),
                ring_lap_histogram={str(key):value
                                    for key,value in sorted(lap_histogram.items())},
                moving_phase_conflicts=len(conflicts),
                first_phase_conflicts=conflicts[:10],
                deadline=physical.PERIOD,
                limitation='Candidate event schedule only. Any moving phase '
                           'conflicts make it invalid; no literal physical '
                           'full-DAG steps or self-reference closure.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result=analyze()
    result['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    print(json.dumps(result,indent=2))
    if args.output:
        if args.output.exists():raise FileExistsError(args.output)
        args.output.write_text(json.dumps(result,indent=2)+'\n')
