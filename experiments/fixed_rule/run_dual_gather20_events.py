"""Three complete clean gather dataflows under the fixed U20 controller.

Packet motion between literal source/receiver local steps is skipped only
after checking unique direction/phase on the physical periodic ring. This
does not yet evolve the full holder/evaluator rule across a work period.
"""
import argparse
import hashlib
import json
from pathlib import Path
import random
import resource
import time

import numpy as np

from gacsca.fixed_rule import stream28_compact_layout as layout_module
from gacsca.fixed_rule import stream28_dual_core20 as core
from gacsca.fixed_rule import stream28_dual_holder_rom as rom
from gacsca.fixed_rule import stream28_dual_projected20 as projected
from gacsca.fixed_rule import stream28_holder_projected as holder_projected
from gacsca.fixed_rule import spatial_projected8 as spatial_projected


def check(*,colonies=3,seed=2026092901,parents=None,
          initial_data=None,return_data=False):
    if not 1<=colonies<=15:raise ValueError('one to fifteen colonies required')
    started=time.perf_counter()
    layout=layout_module.build()
    assert len(layout.gathered)==761 and len(layout.routes)==2283
    rng=random.Random(seed)
    widths=(tuple(width for _,width in holder_projected.SCHEMA)+
            spatial_projected.WIDTHS)
    assert len(widths)==len(layout.info)
    parents=(tuple(tuple(rng.getrandbits(width) for width in widths)
                   for _ in range(colonies)) if parents is None else
             tuple(tuple(map(int,row)) for row in parents))
    if (len(parents)!=colonies or any(len(row)!=len(widths) or
            any(not 0<=value<1<<width
                for value,width in zip(row,widths)) for row in parents)):
        raise ValueError('complete typed projected parent states required')
    size=colonies*core.Q
    data=np.zeros(size,dtype=np.uint64)
    for col,words in enumerate(parents):
        data[col*core.Q+np.array(layout.info)]=words
    for physical,value in (initial_data or {}).items():
        if not 0<=physical<size or not 0<=value<1<<64:
            raise ValueError('initial Data outside physical ring/word')
        if physical%core.Q in layout.info and int(data[physical])!=value:
            raise ValueError('initial Data conflicts with parent Info')
        data[physical]=value
    routes_by_stage=[tuple(row for row in layout.routes if row.stage==stage)
                     for stage in range(3)]
    counts=[]

    def neighborhood(position,age,incoming=None):
        rows=[]
        for offset in core.NEIGHBORHOOD:
            physical=(position+offset)%size
            address=physical%core.Q
            values=dict(zip(core.STATIC,rom.record(address)))
            if incoming is not None and physical==incoming[0]:
                values.update(incoming[1])
            rows.append(core.Cell(**values,address=address,age=age,
                                  data=int(data[physical])))
        return tuple(rows)

    for stage,routes in enumerate(routes_by_stage):
        reset=core.RESET_AGES[stage]
        # Each history bank's reset mask is checked against its actual ROM;
        # earlier completed banks must remain available for the vote.
        cleared=retained=0
        for wire in layout.gathered:
            for bank in range(3):
                site=layout.history(bank,*wire)
                mask=(rom.record(site)[core.STATIC.index('a')]>>stage)&1
                if mask:
                    data[site::core.Q]=0
                    cleared+=colonies
                else:retained+=colonies
        for col,words in enumerate(parents):
            actual=tuple(int(data[col*core.Q+site]) for site in layout.info)
            if actual!=words:
                raise AssertionError(('Info changed at reset',stage,col))

        phases={core.LEFT:set(),core.RIGHT:set()}
        source_steps=receiver_steps=0
        latest_arrival=0
        for route in routes:
            offset=route.neighbor-7
            prefix='rp' if route.direction==core.RIGHT else 'lp'
            incoming_prefix=prefix
            for target_col in range(colonies):
                source_col=(target_col+offset)%colonies
                source=source_col*core.Q+route.source
                target=target_col*core.Q+route.target
                phase=(source+route.launch if route.direction==core.LEFT else
                       source-route.launch)%size
                if phase in phases[route.direction]:
                    raise AssertionError(('same-track phase collision',stage,
                                          target_col,route))
                phases[route.direction].add(phase)
                # Run the literal clock rule at the actual source Data word.
                before=neighborhood(source,reset+route.launch-1)
                emitted=core._clock_step(before)
                packet={name:getattr(emitted,prefix+'_'+name)
                        for name in ('target','data','remaining','valid')}
                value=parents[source_col][route.field]
                if packet!=dict(target=route.wire_tag,data=value,
                                remaining=abs(offset),valid=1):
                    raise AssertionError(('wrong physical source emission',
                                          stage,target_col,route,packet,value))
                source_steps+=1
                distance=route.arrival-route.launch
                sign=1 if route.direction==core.RIGHT else -1
                if (not 0<distance<core.STREAM_FRAME or
                        (source+sign*distance)%size!=target):
                    raise AssertionError(('invalid packet flight',stage,
                                          target_col,route,distance))
                boundary_crossings=abs(
                    (source+sign*distance)//core.Q-source//core.Q)
                if boundary_crossings!=packet['remaining']:
                    raise AssertionError(('packet countdown disagrees with '
                                          'physical colony crossings',stage,
                                          target_col,route,boundary_crossings,
                                          packet['remaining']))
                carrier=(target-1 if route.direction==core.RIGHT else
                         target+1)%size
                arrived=dict(packet,remaining=0)
                incoming={incoming_prefix+'_'+name:word
                          for name,word in arrived.items()}
                received=core._clock_step(neighborhood(
                    target,reset+route.arrival-1,(carrier,incoming)))
                if received.data!=value or getattr(received,prefix+'_valid'):
                    raise AssertionError(('wrong physical receiver',stage,
                                          target_col,route,received.data,value))
                data[target]=received.data
                receiver_steps+=1
                latest_arrival=max(latest_arrival,route.arrival)
        for target_col in range(colonies):
            for route in routes:
                source_col=(target_col+route.neighbor-7)%colonies
                actual=int(data[target_col*core.Q+route.target])
                expected=parents[source_col][route.field]
                if actual!=expected:
                    raise AssertionError(('history word mismatch',stage,
                                          target_col,route,actual,expected))
        counts.append(dict(stage=stage,source_steps=source_steps,
                           receiver_steps=receiver_steps,
                           boundary_crossings_checked=source_steps,
                           distinct_direction_phases=sum(map(len,phases.values())),
                           cleared_history_words=cleared,
                           retained_history_words=retained,
                           last_arrival=latest_arrival))
    result=dict(passed=True,colonies=colonies,Q=core.Q,U=core.U,
                stages=counts,
                complete_history_words_checked=colonies*3*len(layout.gathered),
                packet_boundary_crossings_checked=sum(
                    row['boundary_crossings_checked'] for row in counts),
                info_words_preserved=colonies*3*len(layout.info),
                input_sha256=hashlib.sha256(np.array(parents,dtype=np.uint64)
                                            .tobytes()).hexdigest(),
                max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                seconds=time.perf_counter()-started,
                limitation='Composed clean core packet endpoints with '
                           'collision-free analytical flight; not a continuous '
                           'full-holder/evaluator U-period or fault test.')
    return (result,data,parents) if return_data else result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--colonies',type=int,default=3)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result=check(colonies=args.colonies)
    result['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    print(json.dumps(result,indent=2))
    if args.output:
        if args.output.exists():raise FileExistsError(args.output)
        args.output.write_text(json.dumps(result,indent=2)+'\n')
