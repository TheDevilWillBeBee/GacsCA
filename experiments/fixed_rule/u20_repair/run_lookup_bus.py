"""Execute the proposed physical one-lap lookup protocol on a closed ring."""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time

import numpy as np

from gacsca.fixed_rule import stream28_compact_layout as layout_module
from gacsca.fixed_rule import stream28_dual_holder_rule20 as holder
from gacsca.fixed_rule import stream28_dual_pass20 as physical
from gacsca.fixed_rule.u20_repair import initial,lookup_bus
from gacsca.fixed_rule.u20_repair.corrected_circuit import corrected_initial_data
from experiments.fixed_rule.compact8_address_rom import project_all_dual_static


def run(seed=20260929,upper_address=173,successor_static=False):
    started=time.monotonic()
    full,upper=initial.initialize(15,seed,random_raw=False)
    # This is a one-colony component protocol ring. It tests lookup closure;
    # no simulated macrostep claim is made from this cutout.
    raw=full[:physical.Q].copy()
    del full
    raw[lookup_bus.ADDRESS_SOURCE,holder.COL['s2_data']]=upper_address
    if successor_static:
        metadata,site_by_key=lookup_bus.successor_static_source_metadata()
    else:
        metadata,site_by_wire=lookup_bus.static_source_metadata()
        site_by_key={(wire//physical.FIELDS,wire%physical.FIELDS):site_by_wire[wire]
                     for wire in layout_module.build().static_inputs}
    bus=lookup_bus.Bus.empty(len(raw),metadata)
    assigned=list(site_by_key.values())
    if any(int(raw[site,holder.COL['s2_data']]) for site in assigned):
        raise AssertionError('upper static input was preloaded')
    before=initial.state_sha256(raw)
    checkpoints=[]
    for _ in range(2*physical.Q+2):
        age=int(raw[0,holder.COL['age']])
        bus,writes=lookup_bus.step(raw,bus)
        for d,(mask,value) in writes.items():
            raw[mask,holder.COL[f's{d+2}_data']]=value[mask]
        raw[:,holder.COL['age']]=(age+1)%physical.U
        if age in (0,physical.Q-1,physical.Q,physical.Q+1,
                   2*physical.Q-1,2*physical.Q,2*physical.Q+1):
            checkpoints.append(dict(old_age=age,
                                    state_sha256=initial.state_sha256(raw),
                                    broadcast_tokens=int(np.count_nonzero(bus.broadcast_valid)),
                                    lookup_tokens=int(np.count_nonzero(bus.packet_valid)),
                                    fetched_tokens=int(np.count_nonzero(bus.packet_fetched & bus.packet_valid))))
    # Diagnostic projection is deliberately after physical transitions.
    with corrected_initial_data():
        expected=project_all_dual_static(upper_address,
                                         (0,)*(15*physical.FIELDS),True)
    failures=[]
    for (neighbor,field),site in site_by_key.items():
        expected_value=(expected[neighbor*physical.FIELDS+field]
                        if field<physical.FIELDS else
                        int(metadata[(upper_address+neighbor-7)%physical.Q,
                                     field-physical.FIELDS]))
        for d in holder.OFFSETS:
            actual=int(raw[(site-d)%physical.Q,holder.COL[f's{d+2}_data']])
            if actual!=expected_value:
                failures.append(dict(neighbor=neighbor,field=field,
                                     site=site,copy=d,
                                     actual=actual,expected=expected_value))
    if failures:raise AssertionError(('first static lookup mismatch',failures[0]))
    return dict(upper_address=upper_address,seed=seed,
                successor_static=successor_static,
                static_words_checked=len(site_by_key),
                physical_source_sites=len(set(assigned)),
                fivefold_values_checked=len(site_by_key)*len(holder.OFFSETS),
                initial_state_sha256=before,
                final_state_sha256=initial.state_sha256(raw),
                checkpoints=checkpoints,
                duration_seconds=round(time.monotonic()-started,3),
                peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                scope='lookup-only rule; base F and own-description circuit not executed')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--seed',type=int,default=20260929)
    parser.add_argument('--upper-address',type=int,default=173)
    parser.add_argument('--successor-static',action='store_true')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    result=run(args.seed,args.upper_address,args.successor_static)
    rendered=json.dumps(result,indent=2,sort_keys=True)+'\n'
    args.output.write_text(rendered)
    print(rendered)
