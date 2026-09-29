"""Audit all compact three-history stream launches and acceptances locally."""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time
from functools import lru_cache

from gacsca.fixed_rule import stream28_holder_core as old_core
from gacsca.fixed_rule import stream28_dual_core20 as core20
from gacsca.fixed_rule import stream28_holder_initial as initial
from gacsca.fixed_rule import stream28_holder_projected as holder_projected
from gacsca.fixed_rule import stream28_holder_rule as old_holder
from gacsca.fixed_rule import stream28_dual_holder_rule20 as holder20
from gacsca.fixed_rule import spatial_epoch as old_spatial_epoch
from gacsca.fixed_rule import spatial_epoch8
from gacsca.fixed_rule import stream28_compact_layout as layout_module
from gacsca.fixed_rule import stream28_compact_vote as old_physical
from gacsca.fixed_rule import stream28_dual_pass20 as physical20
from gacsca.fixed_rule import stream28_dual_compact_vote20 as vote20


def check(*,u20=False):
    started=time.perf_counter()
    core=core20 if u20 else old_core
    holder=holder20 if u20 else old_holder
    physical=physical20 if u20 else old_physical
    spatial_epoch=spatial_epoch8 if u20 else old_spatial_epoch
    vote_marker=vote20.VOTE_SELF if u20 else physical.VOTE_SELF
    layout=layout_module.build()
    assert len(layout.gathered)==761
    assert len(layout.routes)==3*761
    sources=0
    accepts=0
    last=[0,0,0]
    phases={core.RIGHT:set(),core.LEFT:set()}
    sample_words=(0x123456789abcdef0,0xfedcba9876543210,
                  0xffff0000ffff0000)
    for route in layout.routes:
        stage=route.stage
        tick=route.launch-1
        value=sample_words[stage]^(route.wire_tag<<9)
        age=core.RESET_AGES[stage]+tick
        rows=[core.Cell(address=(route.source+j)%core.Q,age=age)
              for j in range(-5,6)]
        source=core.Cell(address=route.source,age=age,data=value,
                         **layout.metadata(route.source))
        rows[5]=source
        out=core._stream_step(tuple(rows),source,stage,tick)
        prefix='rp' if route.direction==core.RIGHT else 'lp'
        if (getattr(out,prefix+'_valid')!=1 or
                getattr(out,prefix+'_target')!=route.wire_tag or
                getattr(out,prefix+'_remaining')!=abs(route.neighbor-7) or
                getattr(out,prefix+'_data')!=value):
            raise AssertionError(('incorrect local launch',route))
        sources+=1

        target=core.Cell(address=route.target,
                         age=core.RESET_AGES[stage]+route.arrival-1,
                         data=0,**layout.metadata(route.target))
        neighbors=[core.Cell(address=(route.target+j)%core.Q,
                             age=target.age) for j in range(-5,6)]
        neighbors[5]=target
        input_prefix='rp' if route.direction==core.RIGHT else 'lp'
        index=4 if route.direction==core.RIGHT else 6
        neighbors[index]=core.Cell(address=neighbors[index].address,
                                   age=target.age,
                                   **{input_prefix+'_target':route.wire_tag,
                                      input_prefix+'_data':value,
                                      input_prefix+'_remaining':0,
                                      input_prefix+'_valid':1})
        received=core._stream_step(tuple(neighbors),target,stage,
                                   route.arrival-1)
        if received.data!=value:
            raise AssertionError(('incorrect local acceptance',route))
        accepts+=1
        last[stage]=max(last[stage],route.arrival)
        if stage==0:
            if route.phase in phases[route.direction]:
                raise AssertionError(('same-track packet phase',route))
            phases[route.direction].add(route.phase)
    # The middle stage-two history word is also its own future vote result.
    voter_sites=[layout.history(1,*wire) for wire in layout.gathered]
    assert all(layout.metadata(site)['a']&vote_marker
               for site in voter_sites)
    assert all(layout.metadata(layout.history(stage,*wire))['d']==
               core.STREAM_TAG_MARK+(stage<<core.STREAM_TAG_SHIFT)+
               wire[0]*core.STREAM_FIELDS+wire[1]
               for wire in layout.gathered for stage in range(3))

    def full_neighborhood(site,age,data_by_site,packet_by_site):
        @lru_cache(maxsize=None)
        def logical(position):
            position%=core.Q
            metadata=(layout.metadata(position)
                      if position<layout.memory_after_banks else
                      dict(kind=core.MEM,index=position,a=31))
            return core.Cell(address=position,age=age,
                             data=data_by_site.get(position,0),
                             **metadata,**packet_by_site.get(position,{}))
        rows=[]
        for offset in holder.NEIGHBORHOOD:
            position=(site+offset)%core.Q
            dynamic=initial.coherent_cell(logical,position)
            static={f'p{k+3}_{name}':getattr(logical(position+k),name)
                    for k in holder.STATIC_OFFSETS for name in core.STATIC}
            raw=holder.Cell(**static,**dict(zip(
                (name for name,_ in holder_projected.SCHEMA),
                holder_projected.encode_cell(dynamic))))
            rows.append(physical.Cell(raw,spatial_epoch.Cell(address=position)))
        return tuple(rows)

    selected=[]
    for stage in range(3):
        for direction in (core.RIGHT,core.LEFT):
            direction_rows=[row for row in layout.routes
                            if row.stage==stage and row.direction==direction]
            selected.extend((direction_rows[0],direction_rows[-1]))
    full_steps=0
    for route in selected:
        value=sample_words[route.stage]^(route.wire_tag<<9)
        age=core.RESET_AGES[route.stage]+route.launch-1
        before=full_neighborhood(route.source,age,{route.source:value},{})
        after=physical.local_step(before)
        prefix='rp' if route.direction==core.RIGHT else 'lp'
        if (getattr(after.holder,f's2_{prefix}_valid')!=1 or
                getattr(after.holder,f's2_{prefix}_target')!=route.wire_tag or
                getattr(after.holder,f's2_{prefix}_data')!=value):
            raise AssertionError(('full-F launch mismatch',route))
        full_steps+=1

        neighbor=(route.target-1 if route.direction==core.RIGHT else
                  route.target+1)%core.Q
        packet={prefix+'_target':route.wire_tag,
                prefix+'_data':value,prefix+'_remaining':0,
                prefix+'_valid':1}
        age=core.RESET_AGES[route.stage]+route.arrival-1
        before=full_neighborhood(route.target,age,{}, {neighbor:packet})
        after=physical.local_step(before)
        if after.holder.s2_data!=value:
            raise AssertionError(('full-F acceptance mismatch',route))
        full_steps+=1
    return dict(passed=True,Q=physical.Q,U=physical.U,
                gathered_projected_words=len(layout.gathered),
                static_address_rom_dependencies=len(layout.static_inputs),
                packet_paths=len(layout.routes),
                literal_local_launch_steps=sources,
                literal_local_accept_steps=accepts,
                literal_combined_endpoint_steps=full_steps,
                last_arrival_by_stage=last,
                stage_window=core.STREAM_FRAME,
                margin_to_8q=[8*physical.Q-t for t in last],
                phase_count_by_direction={
                    'right':len(phases[core.RIGHT]),
                    'left':len(phases[core.LEFT])},
                distinct_in_place_voter_sites=len(set(voter_sites)),
                memory_after_info_hold=layout.memory_after_banks,
                max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                seconds=time.perf_counter()-started,
                layout_source_sha256=hashlib.sha256(
                    Path(layout_module.__file__).read_bytes()).hexdigest(),
                limitation='Analytical full packet paths and literal core '
                           'launch/receive endpoints, with sampled combined '
                           'F endpoints; no continuous three-history '
                           'physical replay or dynamic ROM closure.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--u20',action='store_true')
    args=parser.parse_args()
    result=check(u20=args.u20)
    result['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    print(json.dumps(result,indent=2))
    if args.output:
        if args.output.exists():raise FileExistsError(args.output)
        args.output.write_text(json.dumps(result,indent=2)+'\n')
