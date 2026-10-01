"""Exhaust every typed 9-bit packet-field selector at a real fetch event."""
import argparse
from dataclasses import replace
import json
from pathlib import Path
import random
import time

from gacsca.fixed_rule import spatial_epoch8 as spatial
from gacsca.fixed_rule import stream28_dual_core20 as core
from gacsca.fixed_rule.u20_repair import successor,successor_native,successor_optimized
from .differential import random_neighborhood


def run(seed=20260929):
    started=time.monotonic()
    base=random_neighborhood(seed,successor.Q+1,core.MEM)
    rng=random.Random(seed+1)
    gates=tuple(spatial.GateSpec(1,(slot+1)%16,rng.getrandbits(64),
                                 rng.randrange(1<<14),rng.getrandbits(64),
                                 rng.getrandbits(64),3)
                for slot in range(spatial.GATE_SLOTS))
    routes=tuple(spatial.Route(1,rng.randrange(successor.Q),slot%2,
                               slot%4,slot%spatial.GATE_SLOTS,
                               rng.randrange(spatial.PERIOD))
                 for slot in range(spatial.ROUTE_SLOTS))
    rich=replace(base[7],evaluator=replace(base[7].evaluator,
                                           gates=gates,routes=routes,
                                           mail=spatial.Packet(1,123,1,2,
                                                               rng.getrandbits(64))))
    rows=[successor.Cell(cell) for cell in base]
    rows[7]=successor.Cell(rich,lookup_enable=1,lookup_neighbor=7,
                           lookup_field=successor.base_rule.FIELDS+2,
                           lookup_address=3218,broadcast_valid=1,
                           broadcast_value=3218,packet_valid=1,
                           packet_source=1234,packet_target=5678,
                           packet_field=92,packet_fetched=1,
                           packet_value=rng.getrandbits(64))
    center_raw=successor.encode_cell(rows[7])
    program=successor_optimized.build()
    checked=0
    for field in range(1<<9):
        rows[6]=replace(rows[6],packet_valid=1,
                        packet_target=rich.holder.address,
                        packet_field=field,packet_fetched=0)
        neighborhood=tuple(rows)
        words=tuple(word for cell in neighborhood
                    for word in successor.encode_cell(cell))
        literal=successor.encode_cell(successor.local_step(neighborhood))
        expected=center_raw[field] if field<successor.FIELDS else 0
        if literal[successor.base_rule.FIELDS+11]!=expected:
            raise AssertionError(('literal packet field',field,expected,
                                  literal[successor.base_rule.FIELDS+11]))
        coded=program.evaluate(words)
        native=successor_native.evaluate(words)
        for output,(a,b,c) in enumerate(zip(literal,coded,native)):
            if a!=b or a!=c:
                raise AssertionError(dict(packet_field=field,output=output,
                                          literal=a,wordcode=b,native=c))
        checked+=successor.FIELDS
    return dict(selectors=512,valid_fields=successor.FIELDS,
                invalid_fields=512-successor.FIELDS,
                raw_outputs_checked=checked,
                wordcode_sha256=program.digest(),
                duration_seconds=round(time.monotonic()-started,3),
                scope='exhaustive packet selector for one rich typed center; full rule parity')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    receipt=run()
    rendered=json.dumps(receipt,indent=2,sort_keys=True)+'\n'
    args.output.write_text(rendered)
    print(rendered)
