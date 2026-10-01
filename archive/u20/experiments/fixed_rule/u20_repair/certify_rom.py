"""Rebuild and certify the corrected evaluator ROM in process-local context."""
import argparse
import hashlib
import json
from pathlib import Path
import time

from gacsca.fixed_rule import spatial_codec8
from gacsca.fixed_rule import spatial_epoch8 as spatial
from gacsca.fixed_rule.u20_repair import corrected_circuit, description
from experiments.fixed_rule import compact8_address_rom


def certify():
    started=time.monotonic()
    with corrected_circuit.corrected_initial_data() as plan:
        rows=compact8_address_rom.template(True,True)
        routes=plan['routes']
        program=description.build()
        if routes.program.digest()!=program.digest():
            raise AssertionError('placed ROM describes a different rule')
        if len(rows)!=spatial.Q or any(row.address!=site for site,row in enumerate(rows)):
            raise AssertionError('noncanonical lower ROM addresses')
        if not plan['timing']['passed']:
            raise AssertionError('evaluator timing failure')
        if max(plan['done'].values())>=spatial.PERIOD:
            raise AssertionError('unfinished gate at capture boundary')
        if max(map(len,plan['route_rows'].values()))>spatial.ROUTE_SLOTS:
            raise AssertionError('route slot overflow')
        if max(map(len,plan['at_site'].values()))>spatial.GATE_SLOTS:
            raise AssertionError('gate slot overflow')
        sha=hashlib.sha256()
        for row in rows:
            for value in spatial_codec8.encode_cell(row):
                sha.update(int(value).to_bytes(8,'little'))
        result=dict(wordcode_sha256=program.digest(), operations=len(program.operations),
                    physical_gate_copies=len(routes.gate_positions),
                    route_edges=len(routes.edges), raw_source_sites=len(plan['raw_sources']),
                    output_sites=len(plan['sink_sites']),
                    latest_done=max(plan['done'].values()),
                    latest_event=plan['timing']['latest_event'],
                    output_launch=plan['output_launch'],
                    max_route_slots=max(map(len,plan['route_rows'].values())),
                    max_gate_slots=max(map(len,plan['at_site'].values())),
                    lower_rom_sha256=sha.hexdigest(),
                    duration_seconds=round(time.monotonic()-started,3))
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    result=certify()
    rendered=json.dumps(result,indent=2,sort_keys=True)+'\n'
    args.output.write_text(rendered)
    print(rendered)
