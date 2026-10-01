"""Continuous CPU transitions from oracle-free initial state; no event skips."""
import argparse
import json
from pathlib import Path
import resource
import time

import numpy as np

from gacsca.fixed_rule import stream28_dual_holder_rule20 as holder
from gacsca.fixed_rule import stream28_dual_pass20 as physical
from gacsca.fixed_rule.u20_repair import initial,native


def run(colonies,ticks,seed):
    started=time.monotonic()
    raw,upper=initial.initialize(colonies,seed)
    checkpoints=[dict(tick=0,state_sha256=initial.state_sha256(raw),
                      decoded_sha256=__import__('hashlib').sha256(
                          np.asarray(initial.decode_info(raw),dtype=np.uint64)
                          .tobytes()).hexdigest())]
    previous=raw
    for tick in range(1,ticks+1):
        before=time.monotonic()
        raw=native.step_ring(previous)
        for site in (0,1,7,physical.Q-1,len(raw)//2,len(raw)-1):
            neighborhood=tuple(physical.decode_cell(
                previous[(site+j)%len(previous)].tolist())
                for j in physical.NEIGHBORHOOD)
            expected=physical.encode_cell(physical.local_step(neighborhood))
            actual=tuple(map(int,raw[site]))
            if expected!=actual:
                field=next(i for i,(a,b) in enumerate(zip(expected,actual)) if a!=b)
                raise AssertionError(dict(tick=tick,old_age=int(previous[site,holder.COL['age']]),
                                          site=site,field=field,literal=expected[field],native=actual[field]))
        checkpoints.append(dict(tick=tick,state_sha256=initial.state_sha256(raw),
                                elapsed_seconds=round(time.monotonic()-before,3),
                                decoded_sha256=__import__('hashlib').sha256(
                                    np.asarray(initial.decode_info(raw),dtype=np.uint64)
                                    .tobytes()).hexdigest(),
                                age_zero=int(raw[0,holder.COL['age']])))
        previous=raw
    _,digest,path=native.library()
    return dict(colonies=colonies,sites=len(raw),ticks=ticks,seed=seed,
                lower_source_policy='upper static SOURCE Data zero; no upper-Address projection',
                wordcode_sha256=native.description.build().digest(),
                native_source_sha256=digest,native_library=path,
                checkpoints=checkpoints,
                duration_seconds=round(time.monotonic()-started,3),
                peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--colonies',type=int,default=15)
    parser.add_argument('--ticks',type=int,default=2)
    parser.add_argument('--seed',type=int,default=20260929)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    receipt=run(args.colonies,args.ticks,args.seed)
    rendered=json.dumps(receipt,indent=2,sort_keys=True)+'\n'
    args.output.write_text(rendered)
    print(rendered)
