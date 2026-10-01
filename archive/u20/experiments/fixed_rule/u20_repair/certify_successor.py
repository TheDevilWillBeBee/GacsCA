"""Boundary/random all-field parity for the extended lookup successor."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import random
import time

from gacsca.fixed_rule.u20_repair import successor,successor_optimized,successor_native
from .differential import random_neighborhood


AGES=(0,1,8191,8192,8193,16383,16384,16385,16386,393217,
      720897,successor.U-1)


def run(seed=20260929,rounds=96):
    start=time.monotonic()
    rng=random.Random(seed)
    program=successor_optimized.build()
    count=Counter()
    for case in range(rounds):
        age=AGES[case%len(AGES)]
        base=random_neighborhood(seed+case,age,case%16)
        neighborhood=[]
        for raw in base:
            fields={name:rng.getrandbits(width)
                    for name,width in successor.BUS_SCHEMA}
            neighborhood.append(successor.Cell(raw,**fields))
        neighborhood=tuple(neighborhood)
        words=tuple(word for cell in neighborhood
                    for word in successor.encode_cell(cell))
        literal=successor.encode_cell(successor.local_step(neighborhood))
        wordcode=program.evaluate(words)
        native=successor_native.evaluate(words)
        for field,(a,b,c) in enumerate(zip(literal,wordcode,native)):
            if a!=b or a!=c:
                raise AssertionError(dict(case=case,age=age,field=field,
                                          literal=a,wordcode=b,native=c,
                                          input_sha256=hashlib.sha256(
                                              b''.join(int(v).to_bytes(8,'little')
                                                       for v in words)).hexdigest()))
        count[age]+=1
    _,native_digest,native_path=successor_native.library()
    return dict(cases=rounds,raw_outputs_checked=rounds*successor.FIELDS,
                age_coverage={str(k):v for k,v in sorted(count.items())},
                optimized_description_sha256=program.digest(),
                optimized_operations=len(program.operations),
                native_source_sha256=native_digest,native_library=native_path,
                duration_seconds=round(time.monotonic()-start,3),
                scope='local successor parity; self-ROM placement and U trajectory open')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--rounds',type=int,default=96)
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    result=run(rounds=args.rounds)
    rendered=json.dumps(result,indent=2,sort_keys=True)+'\n'
    args.output.write_text(rendered)
    print(rendered)
