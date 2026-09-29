"""Pack compact-vote own-F gate copies into the remaining fixed spatial sites.

This proves only static gate/route-table occupancy under an assumed one-site
store for each address-indexed static input word. Operand paths, gate epochs,
packet phases, own-ROM lookup, and temporal correctness remain unchecked.
"""
import argparse
from collections import Counter
import hashlib
import heapq
import json
from math import ceil
from pathlib import Path

from gacsca.fixed_rule import spatial_epoch
from gacsca.fixed_rule import stream28_compact_vote_optimized as optimized
from gacsca.fixed_rule import stream28_compact_vote_optimized8 as optimized8
from gacsca.fixed_rule import stream28_dual_pass_optimized8 as dual_optimized8
from gacsca.fixed_rule import stream28_dual_pass_optimized20 as dual_optimized20
from gacsca.fixed_rule.wordcode_and import LIT
from experiments.fixed_rule.measure_stream28_spatial_capacity import check as inventory
from experiments.fixed_rule.measure_stream28_spatial_capacity import PROJECTED_OUTPUT_FIELDS


def check(*,include_state=False,eight_q=False,dual_pass=False,u20=False):
    facts=inventory(compact_vote=True,eight_q=eight_q,
                    dual_pass=dual_pass,u20=u20)
    program=(dual_optimized20 if u20 else
             dual_optimized8 if dual_pass else
             optimized8 if eight_q else optimized).build()
    limit=spatial_epoch.ROUTE_SLOTS
    n=program.inputs
    def routed(wire):
        return wire<n or program.operations[wire-n][0]!=LIT
    demand=Counter()
    for opcode,a,b in program.operations:
        if opcode!=LIT:
            for wire in (a,b):
                if routed(wire):demand[wire]+=1
    for field in PROJECTED_OUTPUT_FIELDS:
        demand[program.outputs[field]]+=1
    copies=[1]*len(program.operations)
    for index in range(len(copies)-1,-1,-1):
        wire=n+index
        copies[index]=max(1,ceil(demand[wire]/limit))
        opcode,a,b=program.operations[index]
        if opcode!=LIT:
            for operand in (a,b):
                if routed(operand):demand[operand]+=copies[index]-1
    assert sum(copies)==facts['fanout_gate_copies']

    buffers=[]
    for wire in range(n):
        if demand[wire]<=limit:continue
        # One identity AND gate with a locally preloaded all-ones operand:
        # the raw site sends 37 original uses plus one buffer input packet.
        # The buffer emits the remaining uses without changing the word.
        assert demand[wire]<=2*limit-1
        buffers.append((wire,demand[wire]-limit+1))
    assert len(buffers)==(2 if eight_q else 1)
    assert all(demand[wire]<=limit or wire in {item[0] for item in buffers}
               for wire in range(n))

    site_start=(facts['memory_recipe_words']+
                facts['static_rom_input_words'])
    site_stop=spatial_epoch.Q-5
    gate_sites=site_stop-site_start
    assert gate_sites>0
    nodes=[(index,copy,min(limit,max(0,demand[n+index]-copy*limit)))
           for index in range(len(copies)) for copy in range(copies[index])]
    nodes.extend((len(copies)+i,0,load) for i,(_,load) in enumerate(buffers))
    nodes.sort(key=lambda row:(-row[2],row[0],row[1]))
    heap=[(0,0,site) for site in range(site_start,site_stop)]
    heapq.heapify(heap)
    occupied={}
    for index,copy,weight in nodes:
        skipped=[]
        while heap:
            route_load,slots,site=heapq.heappop(heap)
            if (slots<spatial_epoch.GATE_SLOTS and
                    route_load+weight<=limit):
                occupied[(index,copy)]=(site,slots,weight)
                heapq.heappush(heap,(route_load+weight,slots+1,site))
                break
            skipped.append((route_load,slots,site))
        else:
            raise AssertionError(('gate/route site packing failed',
                                  index,copy,weight,len(occupied)))
        for candidate in skipped:heapq.heappush(heap,candidate)
    site_routes=Counter()
    site_slots=Counter()
    for site,slot,weight in occupied.values():
        site_routes[site]+=weight
        site_slots[site]+=1
    assert len(occupied)==sum(copies)+len(buffers)
    assert max(site_routes.values())<=limit
    assert max(site_slots.values())<=spatial_epoch.GATE_SLOTS
    assert all(site_start<=site<site_stop for site in site_routes)
    assert len({(site,slot) for site,slot,_ in occupied.values()})==len(occupied)
    summary=dict(passed=True,mode='dual_pass_u20_8q' if u20 else
                 'dual_pass_8q' if dual_pass else
                 '8q' if eight_q else '4q',
                description_sha256=program.digest(),
                Q=spatial_epoch.Q,site_start=site_start,
                site_stop_exclusive=site_stop,available_gate_sites=gate_sites,
                logical_operations=len(program.operations),
                fanout_copies=sum(copies),raw_input_buffers=buffers,
                placed_gate_instances=len(occupied),
                occupied_gate_sites=len(site_slots),
                unused_gate_sites=gate_sites-len(site_slots),
                vacant_gate_slots=gate_sites*spatial_epoch.GATE_SLOTS-
                                  len(occupied),
                max_routes_per_gate_site=max(site_routes.values()),
                max_gate_slots_per_site=max(site_slots.values()),
                total_gate_source_routes=sum(site_routes.values()),
                output_routes=len(PROJECTED_OUTPUT_FIELDS),
                limitation='Static site occupancy only, with one site per '
                           'address-indexed static word; no actual static '
                           'ROM lookup, packet paths or own-rule timing.')
    return (summary,occupied,program,tuple(copies)) if include_state else summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--eight-q',action='store_true')
    parser.add_argument('--dual-pass',action='store_true')
    parser.add_argument('--u20',action='store_true')
    args=parser.parse_args()
    result=check(eight_q=args.eight_q,dual_pass=args.dual_pass,
                 u20=args.u20)
    result['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    print(json.dumps(result,indent=2))
    if args.output:
        if args.output.exists():raise FileExistsError(args.output)
        args.output.write_text(json.dumps(result,indent=2)+'\n')
