"""Audit a fixed local streaming gather against the packed rule's inputs.

The schedule certificate covers every required wire in all three stages.
Selected full packet paths are advanced one physical local_step at a time;
their omitted concurrent packets are covered by the distinct-phase
collision argument, not by a full-ring physical run.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time

from gacsca.fixed_rule import stream_gather as s
from gacsca.fixed_rule import packed28_holder_program as p


def trace_packet(number,stage,*,colonies=15):
    layout=p.layout();neighbor,field=divmod(number,s.FIELDS);offset=neighbor-7
    source=layout.info[field];target=layout.history(stage,offset,field)
    direction=s.direction(offset);launch=s.launch_time(source,offset,field)
    source_col=7;destination_col=(source_col-offset)%colonies
    position=source_col*s.Q+source
    destination=destination_col*s.Q+target
    value=(0x9E3779B97F4A7C15*(field+1))&((1<<64)-1)
    words=[0]*s.FIELDS;words[field]=value
    total=colonies*s.Q

    def at(global_pos,age,packet=None):
        cell=s.initial_cell(global_pos%s.Q,words)
        update=dict(age=age)
        if packet is not None:update['right' if direction==1 else 'left']=packet
        return s.replace(cell,**update)

    age=stage*s.FRAME+launch-1
    emitted=s.local_step(tuple(at(position+j,age) for j in (-1,0,1)))
    packet=emitted.right if direction==1 else emitted.left
    assert packet==s.Packet(1,number,abs(offset),stage,value)
    assert not emitted.collision
    age+=1
    distance=0
    while packet.valid:
        next_position=(position+direction)%total
        neighbors=tuple(at(next_position+j,age,packet if
                           (next_position+j)%total==position else None)
                        for j in (-1,0,1))
        output=s.local_step(neighbors)
        assert not output.collision,(number,stage,age,next_position)
        packet=output.right if direction==1 else output.left
        position=next_position;age+=1;distance+=1
        if not packet.valid:
            assert position==destination,(number,stage,position,destination)
            assert output.history_valid and output.history_value==value
        assert distance<=8*s.Q,(number,stage,'undelivered')
    assert age-stage*s.FRAME==s.arrival_time(source,target,offset,field)
    return dict(wire=number,stage=stage,offset=offset,source=source,target=target,
                launch=launch,arrival=age-stage*s.FRAME,distance=distance)


def check():
    started=time.perf_counter();certificate=s.schedule_certificate()
    layout=p.layout();by_offset={}
    for number in layout.gathered_inputs:
        offset=number//s.FIELDS-7
        by_offset.setdefault(offset,number)
    # Both directions and all seven hop counts, including local transport.
    traced=[trace_packet(by_offset[offset],stage)
            for offset in s.OFFSETS for stage in (0,2)]
    assert certificate['last_delivery']<8*s.Q
    return dict(passed=True,certificate={k:v for k,v in certificate.items() if k!='rows'},
                local_physical_traces=traced,trace_count=len(traced),
                rule_source_sha256=hashlib.sha256(Path(s.__file__).read_bytes()).hexdigest(),
                current_input_set_sha256=hashlib.sha256(str(layout.gathered_inputs).encode()).hexdigest(),
                seconds=time.perf_counter()-started,
                limitation='Candidate gather component only: isolated packet paths plus '
                           'collision-phase certificate, not a full concurrent physical '
                           'period or a self-reference-closed replacement rule.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError('preserve earlier evidence')
    result=check();args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='local_physical_traces'},indent=2))


if __name__=='__main__':main()
