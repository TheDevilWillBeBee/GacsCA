"""Static capacity compiler for the complete fixed-rule evaluator DAG.

This is host initialization and diagnostics, not an evolving transition. It
duplicates eight high-fanout computations, assigns each operand use to an
equivalent copy, and places every gate within the *already fixed* three gate
slots and 38 route slots of spatial_epoch. It proves static capacity only:
no epoch times, packet launch times, or self-reference closure are inferred.
"""
from collections import Counter,defaultdict
from dataclasses import dataclass
from functools import lru_cache
import heapq
from math import ceil

from . import spatial_epoch as hardware
from . import spatial_layer1 as previous
from . import stream28_holder_program as reference
from .wordcode_and import LIT,arithmetic


@dataclass(frozen=True)
class Node:
    gate_index:int
    copy:int
    site:int
    slot:int
    route_count:int


@dataclass(frozen=True)
class Use:
    consumer_gate:int
    consumer_copy:int
    arg_slot:int
    logical_source_wire:int
    source_gate:int  # -1 means an encoded raw memory source
    source_copy:int
    source_site:int
    target_site:int
    target_slot:int


@dataclass(frozen=True)
class Compilation:
    description_sha256:str
    nodes:tuple
    uses:tuple
    copy_counts:tuple
    site_gate_counts:tuple
    site_route_counts:tuple
    raw_route_counts:tuple
    first_eight_pinned:int


def _is_routed(program,wire):
    return wire<program.inputs or program.operations[wire-program.inputs][0]!=LIT


@lru_cache(maxsize=1)
def compile_capacity():
    program=reference.compiled_description()
    layout=reference.layout()
    first=previous.layout(8,'earliest')
    limit=hardware.ROUTE_SLOTS
    memory=layout.memory_count
    gate_sites=hardware.Q-5-memory
    assert gate_sites>0

    # A clone of an operation adds one use of each of its nonliteral inputs.
    # Reverse topological order closes this increased demand in one pass.
    demand=Counter()
    for opcode,a,b in program.operations:
        if opcode==LIT:continue
        for wire in (a,b):
            if _is_routed(program,wire):demand[wire]+=1
    copies=[1]*len(program.operations)
    for index in range(len(program.operations)-1,-1,-1):
        wire=program.inputs+index
        copies[index]=max(1,ceil(demand[wire]/limit))
        opcode,a,b=program.operations[index]
        for operand in (a,b) if opcode!=LIT else ():
            if _is_routed(program,operand):demand[operand]+=copies[index]-1
    raw_routes=tuple(demand[index] for index in range(program.inputs))
    if max(raw_routes)>limit:
        raise AssertionError('raw source needs an encoded buffer gate')

    # Consumers are ordered by dependency layer, then topological index.
    # The original producer serves the early prefix where possible.
    depth=[0]*program.inputs
    for opcode,a,b in program.operations:
        depth.append(1 if opcode==LIT else 1+max(depth[a],depth[b]))
    consumers=defaultdict(list)
    for index,(opcode,a,b) in enumerate(program.operations):
        if opcode==LIT:continue
        for copy in range(copies[index]):
            for arg_slot,wire in enumerate((a,b)):
                if _is_routed(program,wire):
                    consumers[wire].append((index,copy,arg_slot))
    for occurrences in consumers.values():
        occurrences.sort(key=lambda item:(depth[program.inputs+item[0]],item))
    if any(len(consumers[wire])!=count for wire,count in demand.items()):
        raise AssertionError('clone input demand not closed')
    assigned={}
    source_load=Counter()
    for wire,occurrences in consumers.items():
        if wire<program.inputs:continue
        for ordinal,consumer in enumerate(occurrences):
            source=(wire-program.inputs,ordinal//limit)
            if source[1]>=copies[source[0]]:raise AssertionError('insufficient copies')
            assigned[consumer]=source
            source_load[source]+=1
    if max(source_load.values(),default=0)>limit:
        raise AssertionError('copy fanout remains over capacity')

    # Preserve the already physically audited original first-eight gates.
    site_load=[0]*gate_sites
    site_slots=[0]*gate_sites
    placed={}
    for index,address in zip(first.gate_operations,first.gate_addresses):
        local=address-memory
        assert 0<=local<gate_sites and site_slots[local]==0
        node=(index,0)
        placed[node]=(address,0)
        site_load[local]=source_load[node]
        site_slots[local]=1
    heap=[(site_load[j],site_slots[j],j) for j in range(gate_sites)]
    heapq.heapify(heap)
    remaining=[(index,copy) for index in range(len(program.operations))
               for copy in range(copies[index]) if (index,copy) not in placed]
    remaining.sort(key=lambda node:(-source_load[node],node))
    for node in remaining:
        weight=source_load[node]
        skipped=[]
        while heap:
            current,slots,local=heapq.heappop(heap)
            if slots<hardware.GATE_SLOTS and current+weight<=limit:
                placed[node]=(memory+local,slots)
                site_load[local]=current+weight
                site_slots[local]=slots+1
                heapq.heappush(heap,(site_load[local],site_slots[local],local))
                break
            skipped.append((current,slots,local))
        else:
            raise AssertionError(('fixed gate/route placement exhausted',node,weight))
        for candidate in skipped:heapq.heappush(heap,candidate)

    nodes=tuple(Node(index,copy,*placed[(index,copy)],source_load[(index,copy)])
                for index in range(len(program.operations))
                for copy in range(copies[index]))
    uses=[]
    for wire,occurrences in consumers.items():
        for consumer in occurrences:
            target_site,target_slot=placed[consumer[:2]]
            if wire<program.inputs:
                source_gate,source_copy=-1,0
                source_site=layout.wires[wire]
                if source_site is None:raise AssertionError('missing raw input placement')
            else:
                source_gate,source_copy=assigned[consumer]
                source_site=placed[(source_gate,source_copy)][0]
            uses.append(Use(*consumer,wire,source_gate,source_copy,
                            source_site,target_site,target_slot))
    uses.sort(key=lambda use:(use.consumer_gate,use.consumer_copy,use.arg_slot))
    result=Compilation(program.digest(),nodes,tuple(uses),tuple(copies),
                       tuple(site_slots),tuple(site_load),raw_routes,
                       len(first.gate_operations))
    assert len(nodes)==sum(copies)
    assert sum(raw_routes)+sum(site_load)==len(uses)
    assert max(site_slots)<=hardware.GATE_SLOTS
    assert max(site_load)<=limit
    assert max(raw_routes)<=limit
    validate_compilation(result)
    return result


def validate_compilation(compiled):
    """Independent static checker for gate slots, routes and provenance."""
    program=reference.compiled_description()
    layout=reference.layout()
    first=previous.layout(8,'earliest')
    if compiled.description_sha256!=program.digest():
        raise AssertionError('description identity changed')
    memory=layout.memory_count
    gate_sites=hardware.Q-5-memory
    if len(compiled.copy_counts)!=len(program.operations):
        raise AssertionError('missing logical gate copy counts')
    nodes={}
    occupied=set()
    for node in compiled.nodes:
        key=(node.gate_index,node.copy)
        place=(node.site,node.slot)
        if (key in nodes or place in occupied or
                not 0<=node.gate_index<len(program.operations) or
                not 0<=node.copy<compiled.copy_counts[node.gate_index] or
                not memory<=node.site<hardware.Q-5 or
                not 0<=node.slot<hardware.GATE_SLOTS):
            raise AssertionError('invalid or duplicate gate placement')
        nodes[key]=node
        occupied.add(place)
    if len(nodes)!=sum(compiled.copy_counts):
        raise AssertionError('not all gate copies are present')
    for index,address in zip(first.gate_operations,first.gate_addresses):
        if nodes[(index,0)].site!=address or nodes[(index,0)].slot!=0:
            raise AssertionError('audited first-eight placement changed')
    uses={}
    site_load=Counter()
    raw_load=Counter()
    raw_site_wires=defaultdict(set)
    node_load=Counter()
    for use in compiled.uses:
        key=(use.consumer_gate,use.consumer_copy,use.arg_slot)
        target=nodes.get(key[:2])
        if key in uses or target is None or use.arg_slot not in (0,1):
            raise AssertionError('invalid or duplicate operand use')
        opcode,a,b=program.operations[use.consumer_gate]
        actual_wire=(a,b)[use.arg_slot]
        if (opcode==LIT or not _is_routed(program,actual_wire) or
                use.logical_source_wire!=actual_wire):
            raise AssertionError('operand provenance changed')
        if (use.target_site,use.target_slot)!=(target.site,target.slot):
            raise AssertionError('operand destination moved')
        if actual_wire<program.inputs:
            if (use.source_gate,use.source_copy,use.source_site)!=(-1,0,layout.wires[actual_wire]):
                raise AssertionError('raw source provenance changed')
            raw_load[actual_wire]+=1
            raw_site_wires[use.source_site].add(actual_wire)
        else:
            source=nodes.get((use.source_gate,use.source_copy))
            if (source is None or use.source_gate!=actual_wire-program.inputs or
                    use.source_site!=source.site):
                raise AssertionError('gate source provenance changed')
            site_load[source.site-memory]+=1
            node_load[(source.gate_index,source.copy)]+=1
        uses[key]=use
    for node in compiled.nodes:
        opcode,a,b=program.operations[node.gate_index]
        if opcode==LIT:continue
        for slot,wire in enumerate((a,b)):
            if _is_routed(program,wire) and (node.gate_index,node.copy,slot) not in uses:
                raise AssertionError('missing routed operand')
    for edge in first.edges:
        use=uses.get((edge.gate_wire-program.inputs,0,edge.slot))
        if (use is None or use.source_site!=edge.source or
                use.target_site!=edge.target or use.source_copy!=0 or
                use.logical_source_wire!=edge.source_wire):
            raise AssertionError('audited first-eight operand route changed')
    if any(len(wires)>1 for wires in raw_site_wires.values()):
        raise AssertionError('one raw source site carries multiple wires')
    if (tuple(raw_load[index] for index in range(program.inputs))!=compiled.raw_route_counts or
            tuple(site_load[index] for index in range(gate_sites))!=compiled.site_route_counts or
            any(node_load[(node.gate_index,node.copy)]!=node.route_count
                for node in compiled.nodes)):
        raise AssertionError('route load count changed')
    slots=Counter(node.site-memory for node in compiled.nodes)
    if tuple(slots[index] for index in range(gate_sites))!=compiled.site_gate_counts:
        raise AssertionError('gate slot count changed')
    if (max(slots.values())>hardware.GATE_SLOTS or
            max(site_load.values(),default=0)>hardware.ROUTE_SLOTS or
            max((sum(raw_load[wire] for wire in wires)
                 for wires in raw_site_wires.values()),default=0)>hardware.ROUTE_SLOTS):
        raise AssertionError('fixed physical capacity exceeded')
    return True


def evaluate_compiled(words,compilation=None):
    """Diagnostic oracle: verify every transformed gate and its output."""
    compiled=compilation or compile_capacity()
    program=reference.compiled_description()
    if len(words)!=program.inputs:raise ValueError('complete raw input required')
    if compiled.description_sha256!=program.digest():
        raise AssertionError('wrong source rule description')
    validate_compilation(compiled)
    expected=list(map(int,words))
    for opcode,a,b in program.operations:
        expected.append(a if opcode==LIT else arithmetic(opcode,expected[a],expected[b]))
    incoming={(use.consumer_gate,use.consumer_copy,use.arg_slot):use
              for use in compiled.uses}
    actual={}
    for node in compiled.nodes:
        opcode,a,b=program.operations[node.gate_index]
        if opcode==LIT:
            value=a
        else:
            args=[]
            for slot,wire in enumerate((a,b)):
                if not _is_routed(program,wire):
                    args.append(program.operations[wire-program.inputs][1])
                    continue
                use=incoming[(node.gate_index,node.copy,slot)]
                if use.logical_source_wire!=wire:
                    raise AssertionError('operand wire relabeled')
                args.append(words[wire] if use.source_gate<0 else
                            actual[(use.source_gate,use.source_copy)])
            value=arithmetic(opcode,*args)
        if value!=expected[program.inputs+node.gate_index]:
            raise AssertionError(('cloned gate diverged',node.gate_index,node.copy))
        actual[(node.gate_index,node.copy)]=value
    return tuple(actual[(wire-program.inputs,0)] if wire>=program.inputs
                 else words[wire] for wire in program.outputs)
