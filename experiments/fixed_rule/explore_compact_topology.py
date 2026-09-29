"""Try depth-ordered spatial placement of the compact-vote own-rule DAG.

This compares an optimistic dependency-time bound with the load-balanced
occupancy placement. It does not schedule packets or implement ROM lookup.
"""
import argparse
from collections import Counter,defaultdict
import hashlib
import json
from pathlib import Path

from gacsca.fixed_rule import spatial_epoch,spatial_epoch8
from gacsca.fixed_rule.wordcode_and import LIT
from experiments.fixed_rule.place_stream28_compact_gates import check as pack
from experiments.fixed_rule.measure_compact_placement_timing import bound


def check(*,include_state=False,eight_q=False,dual_pass=False,u20=False):
    facts,baseline,program,copies=pack(include_state=True,eight_q=eight_q,
                                       dual_pass=dual_pass,u20=u20)
    site_start=facts['site_start']
    site_stop=facts['site_stop_exclusive']
    capacity=site_stop-site_start
    depth=[0]*program.inputs
    for opcode,a,b in program.operations:
        depth.append(1 if opcode==LIT else 1+max(depth[a],depth[b]))
    nodes=tuple((key,weight) for key,(_,_,weight) in baseline.items())
    heavy=[(key,weight) for key,weight in nodes
           if weight==spatial_epoch.ROUTE_SLOTS]
    site_load=Counter()
    site_nodes=defaultdict(list)
    positions={}
    heavy_sites=[]
    for ordinal,(key,weight) in enumerate(heavy):
        site=site_start+ordinal*capacity//len(heavy)
        if site_load[site]:raise AssertionError('heavy reservation collision')
        site_load[site]=weight
        site_nodes[site].append(key)
        positions[key]=(site,0,weight)
        heavy_sites.append(site)
    # A 38-route gate uses an entire site's route table but leaves two gate
    # slots. Literal gates have zero routed fanout and fit those slots. Reserve
    # them here so the depth-order scan does not strand the last gate copies.
    if dual_pass:
        literal_zeros=[key for key,weight in nodes
                       if weight==0 and key not in positions and
                       key[0]<len(program.operations) and
                       program.operations[key[0]][0]==LIT]
        if len(literal_zeros)<2*len(heavy_sites):
            raise AssertionError('too few local literals for heavy sites')
        for ordinal,key in enumerate(literal_zeros[:2*len(heavy_sites)]):
            site=heavy_sites[ordinal//2]
            site_nodes[site].append(key)
            positions[key]=(site,0,0)
    cursor=site_start
    skips=0
    order=sorted((key,weight) for key,weight in nodes if key not in positions)
    order.sort(key=lambda item:(depth[program.inputs+item[0][0]]
                                if item[0][0]<len(program.operations) else
                                1,item[0]))
    for key,weight in order:
        for advance in range(capacity):
            site=site_start+(cursor-site_start+advance)%capacity
            if (len(site_nodes[site])<spatial_epoch.GATE_SLOTS and
                    site_load[site]+weight<=spatial_epoch.ROUTE_SLOTS):
                site_nodes[site].append(key)
                site_load[site]+=weight
                positions[key]=(site,0,weight)
                cursor=site_start+(site-site_start+1)%capacity
                skips+=advance
                break
        else:
            raise AssertionError(('depth-order site capacity exhausted',
                                  key,weight,len(positions)))
    for site,keys in site_nodes.items():
        keys.sort(key=lambda key:(depth[program.inputs+key[0]]
                                  if key[0]<len(program.operations) else
                                  1,key))
        for slot,key in enumerate(keys):
            weight=positions[key][2]
            positions[key]=(site,slot,weight)
    assert len(positions)==len(baseline)
    assert max(site_load.values())<=spatial_epoch.ROUTE_SLOTS
    assert max(len(keys) for keys in site_nodes.values())<=spatial_epoch.GATE_SLOTS
    period=spatial_epoch8.PERIOD if eight_q else spatial_epoch.PERIOD
    timing=bound(facts,positions,program,copies,period)
    prior=bound(facts,baseline,program,copies,period)
    summary=dict(passed=True,mode='dual_pass_u20_8q' if u20 else
                 'dual_pass_8q' if dual_pass else
                 '8q' if eight_q else '4q',
                description_sha256=program.digest(),
                site_start=site_start,site_stop_exclusive=site_stop,
                placed_gate_instances=len(positions),
                heavy_reserved=len(heavy),
                occupied_gate_sites=len(site_nodes),
                max_routes_per_site=max(site_load.values()),
                max_slots_per_site=max(map(len,site_nodes.values())),
                placement_scan_skips=skips,
                load_balanced_optimistic_output_arrival=(
                    prior['optimistic_latest_output_arrival']),
                depth_ordered_optimistic_output_arrival=(
                    timing['optimistic_latest_output_arrival']),
                depth_ordered_optimistic_gate_completion=(
                    timing['optimistic_latest_gate_completion']),
                physical_period=period,
                output_excess_over_period=max(
                    0,timing['optimistic_latest_output_arrival']-
                    period),
                limitation='Optimistic per-edge distance bound for a '
                           'dependency-ordered static placement; no packet '
                           'contention, gate-switch, static lookup, or '
                           'physical-period certificate.')
    return (summary,positions,program,copies) if include_state else summary


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
