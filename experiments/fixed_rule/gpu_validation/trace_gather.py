"""Trace one failed long-range gather packet across its first colony edge."""
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
from gacsca.fixed_rule.gpu_validation import dense
from gacsca.fixed_rule.gpu_validation.initial import initialize, state_sha256


def one_site_python(before, after, site):
    neighbors = tuple(physical.decode_cell(before[(site+j)%len(before)].tolist())
                      for j in physical.NEIGHBORHOOD)
    expected = np.asarray(physical.encode_cell(physical.local_step(neighbors)),
                          dtype=np.uint64)
    mismatch = np.flatnonzero(expected != after[site])
    return None if not len(mismatch) else dict(site=site, field=int(mismatch[0]),
        python=int(expected[mismatch[0]]),gpu=int(after[site,mismatch[0]]))


def run(colonies, seed, output):
    started=time.perf_counter()
    route=next(r for r in layout_module.build().routes
               if r.stage==0 and r.neighbor==0 and r.field==100)
    source_col=0
    source=source_col*physical.Q+route.source
    edge=(source_col+1)*physical.Q
    target=(source_col+7)*physical.Q+route.target
    raw,upper=initialize(colonies,seed)
    results=dict(route=route.__dict__,colonies=colonies,seed=seed,
                 initial_sha256=state_sha256(raw),observations=[])
    ages=(0,route.launch-1,route.launch,
          route.launch+edge-source-1,
          route.launch+edge-source,
          route.launch+edge-source+route.target,
          route.arrival)
    before=None;last=None
    with dense.World(raw) as world:
        for tick in ages:
            world.run(tick-world.time)
            after=world.read()
            inspect=sorted({source,source+1,edge-1,edge,edge+1,
                            edge+route.target,target})
            rows=[]
            for site in inspect:
                row=after[site]
                rows.append(dict(site=site,address=int(row[holder.COL['address']]),
                    data=int(row[holder.COL['s2_data']]),
                    rp=[dict(valid=int(row[holder.COL[f's{k}_rp_valid']]),
                             target=int(row[holder.COL[f's{k}_rp_target']]),
                             remaining=int(row[holder.COL[f's{k}_rp_remaining']]),
                             data=int(row[holder.COL[f's{k}_rp_data']]))
                        for k in range(5)]))
            parity=[]
            if last is not None and tick==last+1:
                for site in (source,edge-1,edge,edge+1,edge+route.target):
                    bad=one_site_python(before,after,site)
                    if bad:parity.append(bad)
            results['observations'].append(dict(tick=tick,sha256=state_sha256(after),
                rows=rows,python_parity_mismatches=parity,
                elapsed_seconds=time.perf_counter()-started))
            if parity:break
            before,last=after,tick
    results['seconds']=time.perf_counter()-started
    results['max_rss_kib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    results['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    output.write_text(json.dumps(results,indent=2)+'\n')
    return results


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--colonies',type=int,default=15)
    parser.add_argument('--seed',type=int,default=20260929)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():parser.error('output already exists')
    print(json.dumps(run(args.colonies,args.seed,args.output),indent=2))
