"""Check literal and WordCode transitions for the fixed 8Q vote successor."""
import argparse
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import random
import resource
import time

from gacsca.fixed_rule import spatial_epoch8 as spatial_epoch
from gacsca.fixed_rule import stream28_holder_rule as holder
from gacsca.fixed_rule import stream28_compact_vote8 as physical
from gacsca.fixed_rule import stream28_compact_vote_description8 as full
from gacsca.fixed_rule import stream28_compact_vote_optimized8 as optimized


def vote_neighborhood(physical_site,voter,values,age):
    history={(voter-1)%holder.Q:values[0],voter%holder.Q:values[1],
             (voter+1)%holder.Q:values[2]}
    rows=[]
    for delta in physical.NEIGHBORHOOD:
        site=(physical_site+delta)%holder.Q
        static={f'p{offset+3}_kind':0 for offset in range(-3,4)}
        static.update({f'p{offset+3}_a':
                       physical.VOTE_SELF if
                       (site+offset)%holder.Q==voter else 0
                       for offset in range(-3,4)})
        copies={f's{offset+2}_data':history.get((site+offset)%holder.Q,0)
                for offset in holder.OFFSETS}
        raw=holder.Cell(address=site,age=age,**static,**copies)
        rows.append(physical.Cell(raw,spatial_epoch.Cell(address=site)))
    return tuple(rows)


def check():
    started=time.perf_counter()
    rng=random.Random(2026092844)
    original=full.build()
    simplified=optimized.build()
    assert (original.inputs,len(original.outputs))==(
        15*physical.FIELDS,physical.FIELDS)
    checks=0
    marked=0
    faulty=0

    def verify(before,expected_vote=None):
        nonlocal checks
        expected=physical.encode_cell(physical.local_step(before))
        words=tuple(word for row in before for word in
                    physical.encode_cell(row))
        for label,program in (('full',original),('optimized',simplified)):
            got=program.evaluate(words)
            if got!=expected:
                mismatch=[(i,a,b) for i,(a,b) in enumerate(zip(got,expected))
                          if a!=b]
                raise AssertionError((label,checks,mismatch[:8]))
        if expected_vote is not None:
            offset=(before[7].holder.address-voter)%holder.Q
            if offset>2:offset-=holder.Q
            assert getattr(physical.decode_cell(expected).holder,
                           f's{2-offset}_data')==expected_vote
        checks+=1

    valuesets=[(rng.getrandbits(64),rng.getrandbits(64),
                rng.getrandbits(64)) for _ in range(4)]
    voter=2863
    for values in valuesets:
        expected=physical.majority3(*values)
        for age in holder.VOTE_AGES:
            for offset in holder.OFFSETS:
                site=(voter-offset)%holder.Q
                before=vote_neighborhood(site,voter,values,age)
                verify(before,expected)
                marked+=1
                if age==holder.VOTE_AGES[0]:
                    rows=list(before)
                    for target in (voter-1,voter,voter+1):
                        physical_index=(target-site)%holder.Q
                        if physical_index>7:physical_index-=holder.Q
                        row_index=7+physical_index
                        row=rows[row_index]
                        rows[row_index]=replace(row,holder=replace(
                            row.holder,s2_data=row.holder.s2_data^((1<<64)-1)))
                    verify(tuple(rows),expected)
                    faulty+=1

    for _ in range(35):
        site=rng.randrange(holder.Q)
        tick=rng.randrange(spatial_epoch.PERIOD)
        rows=tuple(physical.Cell(
            holder.Cell(address=(site+delta)%holder.Q,
                        age=physical.RUN_START+tick),
            spatial_epoch.Cell(address=(site+delta)%holder.Q,age=tick))
            for delta in physical.NEIGHBORHOOD)
        verify(rows)

    source=5000
    sink=2863
    tick=40653
    value=0x123456789abcdef0
    gate=spatial_epoch.GateSpec(1,spatial_epoch.OUTPUT_OPCODE[1])
    route=spatial_epoch.Route(1,sink,0,3,0,tick+1)
    rows=[]
    for delta in physical.NEIGHBORHOOD:
        site=(source+delta)%holder.Q
        spatial=spatial_epoch.Cell(address=site,age=tick)
        if site==source:
            spatial=replace(spatial,kind=spatial_epoch.GATE,
                  active_slot=1,
                  gates=(gate,spatial_epoch.GateSpec(1,14),
                         spatial_epoch.EMPTY_GATE),
                  routes=(route,)+
                         (spatial_epoch.EMPTY_ROUTE,)*
                         (spatial_epoch.ROUTE_SLOTS-1),
                  source_value=value,done=0)
        rows.append(physical.Cell(holder.Cell(address=site,
                    age=physical.RUN_START+tick),spatial))
    verify(tuple(rows))

    assert marked==40 and faulty==20
    return dict(passed=True,full_description_sha256=original.digest(),
                optimized_description_sha256=simplified.digest(),
                full_operations=len(original.operations),
                optimized_operations=len(simplified.operations),
                literal_local_cases=checks,marked_vote_cases=marked,
                single_fault_per_input_cases=faulty,
                plain_8q_cases=35,late_output_cases=1,
                max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                seconds=time.perf_counter()-started,
                physical_source_sha256=hashlib.sha256(
                    Path(physical.__file__).read_bytes()).hexdigest(),
                limitation='Local vote and exact explicit-input own-F only; '
                           'no three-slot initialized ROM, spatial routing '
                           'schedule, or decoded macrostep.')


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
