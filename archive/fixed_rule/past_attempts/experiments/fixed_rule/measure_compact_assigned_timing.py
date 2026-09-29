"""Optimistic timing of explicit producer-copy routes for the compact DAG."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from gacsca.fixed_rule import spatial_epoch
from experiments.fixed_rule import stream28_compact_routes as compiler


def check():
    routes=compiler.build()
    program=routes.program
    buffer_key=(len(program.operations),0)
    completed={}
    buffer_in=routes.node_inputs[buffer_key]
    assert len(buffer_in)==1
    assert routes.edges[buffer_in[0]].source_kind=='raw'
    completed[buffer_key]=routes.edges[buffer_in[0]].distance+1
    latest_gate=(0,None)
    for index in range(len(program.operations)):
        for copy in range(routes.copies[index]):
            key=(index,copy)
            arrivals=[]
            for edge_index in routes.node_inputs.get(key,()):
                edge=routes.edges[edge_index]
                source_time=(completed[edge.source_id]
                             if edge.source_kind=='gate' else 0)
                arrivals.append(source_time+edge.distance)
            done=max(arrivals,default=0)+1
            completed[key]=done
            if done>latest_gate[0]:latest_gate=(done,key)
    output_arrivals={}
    for edge in routes.edges:
        if edge.target_kind!='output':continue
        source_time=(completed[edge.source_id]
                     if edge.source_kind=='gate' else 0)
        output_arrivals[edge.target_id]=source_time+edge.distance
    assert len(output_arrivals)==119
    latest_output=max(output_arrivals.items(),key=lambda item:item[1])
    site_load=Counter()
    for edge in routes.edges:site_load[edge.source_site]+=1
    assert max(site_load.values())<=spatial_epoch.ROUTE_SLOTS
    expected_gate_load=Counter()
    for site,slot,weight in routes.gate_positions.values():
        expected_gate_load[site]+=weight
    assert all(site_load[site]==weight for site,weight in
               expected_gate_load.items())
    return dict(passed=True,description_sha256=program.digest(),
                explicit_packet_routes=len(routes.edges),
                output_packet_routes=len(output_arrivals),
                gate_instances=len(routes.gate_positions),
                latest_assigned_gate_completion=latest_gate[0],
                latest_gate_key=latest_gate[1],
                latest_assigned_output_arrival=latest_output[1],
                latest_output_field=latest_output[0],
                physical_period=spatial_epoch.PERIOD,
                gate_excess_over_4q=max(0,latest_gate[0]-spatial_epoch.PERIOD),
                output_excess_over_4q=max(0,latest_output[1]-spatial_epoch.PERIOD),
                max_source_routes_per_site=max(site_load.values()),
                limitation='Optimistic actual-copy distance bound; no '
                           'phase contention, site switch times, output '
                           'mail conflicts, or static ROM lookup.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result=check()
    result['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    print(json.dumps(result,indent=2))
    if args.output:
        if args.output.exists():raise FileExistsError(args.output)
        args.output.write_text(json.dumps(result,indent=2)+'\n')
