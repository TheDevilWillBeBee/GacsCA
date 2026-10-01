"""Topology-aware static placement and optimistic local-routing bound.

The bound allows every packet to launch one tick after its source becomes
ready, with no packet contention or gate-switch delay. It is therefore a
necessary timing check, not a physical execution or a deadline certificate.
"""
import argparse
from collections import Counter,defaultdict,deque
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

from gacsca.fixed_rule import spatial_epoch as physical
from gacsca.fixed_rule import spatial_fanout_compiler as compiler
from gacsca.fixed_rule import spatial_layer1 as first_physical
from gacsca.fixed_rule import stream28_holder_program as reference
from gacsca.fixed_rule.wordcode_and import LIT


@dataclass(frozen=True)
class Plan:
    summary:dict
    sites:dict
    slots:dict
    ready:dict


def explore():
    compiled=compiler.compile_capacity()
    program=reference.compiled_description()
    first=first_physical.layout(8,'earliest')
    memory=reference.layout().memory_count
    capacity=physical.Q-5-memory
    depth=[0]*program.inputs
    for opcode,a,b in program.operations:
        depth.append(1 if opcode==LIT else 1+max(depth[a],depth[b]))
    by_key={(node.gate_index,node.copy):node for node in compiled.nodes}
    sites={}
    pinned=set()
    site_load=[0]*capacity
    site_nodes=defaultdict(list)
    for index,address in zip(first.gate_operations,first.gate_addresses):
        key=(index,0)
        local=address-memory
        sites[key]=address
        pinned.add(key)
        site_load[local]=by_key[key].route_count
        site_nodes[address].append(key)
    order=sorted((key for key in by_key if key not in pinned),
                 key=lambda key:(depth[program.inputs+key[0]],key))
    rank={key:index for index,key in enumerate(order)}

    # A 38-route node requires a site with zero existing route load. Keep
    # those scarce sites for the ten unpinned high-fanout instances before
    # placing the smaller outputs in dependency-layer order.
    reserved=0
    for key in order:
        if by_key[key].route_count<physical.ROUTE_SLOTS:continue
        ideal=(len(first.gate_operations)+rank[key])%capacity
        candidates=(local for local in range(capacity)
                    if site_load[local]==0 and
                    len(site_nodes[memory+local])<physical.GATE_SLOTS)
        local=min(candidates,key=lambda at:(at-ideal)%capacity)
        address=memory+local
        sites[key]=address
        site_load[local]=by_key[key].route_count
        site_nodes[address].append(key)
        reserved+=1

    cursor=len(first.gate_operations)
    skipped=0
    for key in order:
        if key in sites:continue
        weight=by_key[key].route_count
        for advance in range(capacity):
            local=(cursor+advance)%capacity
            address=memory+local
            if (len(site_nodes[address])<physical.GATE_SLOTS and
                    site_load[local]+weight<=physical.ROUTE_SLOTS):
                sites[key]=address
                site_load[local]+=weight
                site_nodes[address].append(key)
                cursor=(local+1)%capacity
                skipped+=advance
                break
        else:raise AssertionError(('topology placement exhausted',key,weight))

    # Gate descriptors can be ordered by depth independently of their
    # physical-site placement. Preserve every audited first-eight gate in
    # slot zero; sort any later descriptors at its site by depth.
    slots={}
    pinned_inversions=[]
    for address,nodes in site_nodes.items():
        first_key=next((key for key in nodes if key in pinned),None)
        rest=sorted((key for key in nodes if key!=first_key),
                    key=lambda key:(depth[program.inputs+key[0]],key))
        if first_key is not None:
            for key in rest:
                if depth[program.inputs+key[0]]<depth[program.inputs+first_key[0]]:
                    pinned_inversions.append((address,first_key,key))
            nodes[:]=[first_key]+rest
        else:nodes[:]=rest
        for slot,key in enumerate(nodes):slots[key]=slot

    incoming=defaultdict(list)
    for use in compiled.uses:incoming[(use.consumer_gate,use.consumer_copy)].append(use)
    ready={};best_parent={};lengths=[]
    for node in compiled.nodes:
        key=(node.gate_index,node.copy)
        opcode,a,b=program.operations[node.gate_index]
        if opcode==LIT:
            ready[key]=1
            continue
        arrivals=[]
        for use in incoming[key]:
            source=(use.source_gate,use.source_copy)
            source_site=(use.source_site if use.source_gate<0 else sites[source])
            distance=(sites[key]-source_site)%physical.Q or physical.Q
            lengths.append(distance)
            source_ready=0 if use.source_gate<0 else ready[source]
            arrivals.append((source_ready+distance+2,source,distance))
        if arrivals:
            arrival=max(arrivals)
            ready[key]=arrival[0]
            best_parent[key]=arrival[1:]
        else:ready[key]=1

    # A static site order must be consistent with logical dependencies.
    indegree=Counter({key:0 for key in by_key})
    children=defaultdict(list)
    for use in compiled.uses:
        if use.source_gate<0:continue
        source=(use.source_gate,use.source_copy)
        target=(use.consumer_gate,use.consumer_copy)
        children[source].append(target)
        indegree[target]+=1
    for nodes in site_nodes.values():
        for source,target in zip(nodes,nodes[1:]):
            children[source].append(target)
            indegree[target]+=1
    queue=deque(key for key,count in indegree.items() if count==0)
    visited=0
    while queue:
        source=queue.popleft();visited+=1
        for target in children[source]:
            indegree[target]-=1
            if indegree[target]==0:queue.append(target)
    acyclic=(visited==len(by_key))

    output_keys=[(wire-program.inputs,0) for wire in program.outputs
                 if wire>=program.inputs]
    last=max(output_keys,key=lambda key:ready[key])
    baseline_ready={}
    for node in compiled.nodes:
        key=(node.gate_index,node.copy)
        opcode,a,b=program.operations[node.gate_index]
        if opcode==LIT:
            baseline_ready[key]=1
            continue
        arrivals=[]
        for use in incoming[key]:
            source=(use.source_gate,use.source_copy)
            source_ready=0 if use.source_gate<0 else baseline_ready[source]
            distance=(use.target_site-use.source_site)%physical.Q or physical.Q
            arrivals.append(source_ready+distance+2)
        baseline_ready[key]=max(arrivals,default=1)
    baseline_output=max(baseline_ready[key] for key in output_keys)
    critical=[];critical_distance=0
    while last in best_parent:
        critical.append(last)
        parent,distance=best_parent[last]
        critical_distance+=distance
        if parent[0]<0:break
        last=parent
    critical.reverse()
    site_load_actual=Counter()
    for node in compiled.nodes:site_load_actual[sites[(node.gate_index,node.copy)]]+=node.route_count
    assert max(site_load_actual.values())<=physical.ROUTE_SLOTS
    assert max(len(nodes) for nodes in site_nodes.values())<=physical.GATE_SLOTS
    assert all(sites[(index,0)]==address and slots[(index,0)]==0
               for index,address in zip(first.gate_operations,first.gate_addresses))
    summary=dict(description_sha256=program.digest(),Q=physical.Q,
                 compiler_source_sha256=hashlib.sha256(Path(compiler.__file__).read_bytes()).hexdigest(),
                 physical_rule_source_sha256=hashlib.sha256(Path(physical.__file__).read_bytes()).hexdigest(),
                 rule_width_bits=physical.WIDTH,
                 gate_instances=len(compiled.nodes),routed_uses=len(compiled.uses),
                 first_eight_sites_pinned=len(pinned),
                 reserved_high_fanout_sites=reserved,
                 max_gate_slots_per_site=max(len(nodes) for nodes in site_nodes.values()),
                 max_routes_per_site=max(site_load_actual.values()),
                 pinned_slot_depth_inversions=len(pinned_inversions),
                 site_order_and_dag_acyclic=acyclic,
                 optimistic_latest_gate_completion=max(ready.values()),
                 optimistic_latest_output_completion=ready[max(output_keys,key=lambda key:ready[key])],
                 load_balanced_optimistic_output_completion=baseline_output,
                 optimistic_output_speedup=baseline_output/ready[max(output_keys,key=lambda key:ready[key])],
                 mean_route_distance=sum(lengths)/len(lengths),
                 critical_chain_gate_count=len(critical),
                 critical_chain_route_distance=critical_distance,
                 critical_chain_gate_indices=[index for index,_ in critical],
                 placement_scan_skips=skipped,
                 limitation='Optimistic route-time lower bound; no per-site '
                            'switch, source-result lifetime, packet phase '
                            'or complete physical macrostep schedule.')
    return Plan(summary,sites,slots,ready)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result=explore().summary
    result['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    print(json.dumps(result,indent=2))
    if args.output:
        if args.output.exists():raise FileExistsError(args.output)
        args.output.write_text(json.dumps(result,indent=2)+'\n')
