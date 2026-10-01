"""Unskipped whole-ring ticks of the lookup successor with no upper oracle.

The lower evaluator ROM here still describes the corrected 421-word rule.
Consequently this is a combined-transition pilot, not own-rule closure.
"""
import argparse
import json
from pathlib import Path
import resource
import time

import numpy as np

from gacsca.fixed_rule import stream28_dual_holder_rule20 as holder
from gacsca.fixed_rule.u20_repair import initial,lookup_bus,successor,successor_native


def initialize(colonies,seed):
    base,upper=initial.initialize(colonies,seed,random_raw=True)
    metadata,site_by_wire=lookup_bus.successor_static_source_metadata()
    raw=np.zeros((len(base),successor.FIELDS),dtype=np.uint64)
    raw[:,:successor.base_rule.FIELDS]=base
    del base
    for col in range(colonies):
        start=col*successor.Q
        raw[start:start+successor.Q,
            successor.base_rule.FIELDS:successor.base_rule.FIELDS+3]=metadata
    for site in site_by_wire.values():
        if np.any(raw[np.arange(colonies)*successor.Q+site,
                      holder.COL['s2_data']]):
            raise AssertionError(('upper static SOURCE Data was preloaded',site))
    return raw,upper


def check_samples(before,after,sites,age):
    checks=0
    for site in sites:
        rows=tuple(successor.decode_cell(
            before[(site+j)%len(before)].tolist())
            for j in successor.NEIGHBORHOOD)
        expected=successor.encode_cell(successor.local_step(rows))
        actual=tuple(map(int,after[site]))
        for field,(got,want) in enumerate(zip(actual,expected)):
            if got!=want:
                raise AssertionError(dict(old_age=age,site=site,field=field,
                                          actual=got,literal=want,
                                          before_sha256=initial.state_sha256(before)))
        checks+=successor.FIELDS
    return checks


def run(colonies=15,ticks=2,seed=20260929):
    started=time.monotonic()
    if colonies<15 or ticks<1:
        raise ValueError('at least 15 colonies and one tick required')
    raw,upper=initialize(colonies,seed)
    first_sha=initial.state_sha256(raw)
    targets={0,1,successor.Q-1,lookup_bus.ADDRESS_SOURCE,
             lookup_bus.ADDRESS_SOURCE+1,2828,3217,
             successor.Q,2*successor.Q-1,
             (colonies//2)*successor.Q+lookup_bus.ADDRESS_SOURCE,
             len(raw)-1}
    sites=tuple(sorted(targets))
    records=[]
    for tick in range(ticks):
        step_start=time.monotonic()
        old_age=int(raw[0,holder.COL['age']])
        after=successor_native.step_ring(raw)
        checked=check_samples(raw,after,sites,old_age)
        launched=int(np.count_nonzero(after[:,successor.base_rule.FIELDS+4]))
        records.append(dict(old_age=old_age,new_age=int(after[0,holder.COL['age']]),
                            state_sha256=initial.state_sha256(after),
                            sample_sites=len(sites),raw_outputs_checked=checked,
                            broadcast_tokens=launched,
                            duration_seconds=round(time.monotonic()-step_start,3)))
        raw=after
    _,native_digest,native_path=successor_native.library()
    return dict(colonies=colonies,ticks=ticks,seed=seed,
                upper_addresses=[int(cell.holder.address) for cell in upper],
                initial_state_sha256=first_sha,final_state_sha256=initial.state_sha256(raw),
                corrected_successor_sha256=__import__(
                    'gacsca.fixed_rule.u20_repair.successor_optimized',
                    fromlist=['build']).build().digest(),
                native_source_sha256=native_digest,native_library=native_path,
                records=records,duration_seconds=round(time.monotonic()-started,3),
                peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                scope='continuous literal successor ticks, old corrected evaluator ROM; no own-rule period')


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
