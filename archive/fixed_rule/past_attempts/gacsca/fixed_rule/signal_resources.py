"""Compile a proposed instruction transcript for resource accounting only.

No ROM/projected rule/initializer/executor is claimed here. The transcript
omits upper-flag delivery, buffer metadata and stage-three-only branch; its
cost is a necessary baseline, not a certificate for the final signal system.
Reuse Layout.schedule because the signal candidate's raw controller is exactly
clock_rule's and Q/U are unchanged; do not use its old timing_certificate.
"""
from . import signal_rule as r
from .clock_program import Layout,Instruction,RESERVED,HISTORY_OFFSETS
from .wordcode import LIT,ADD


def transcript():
    f=r.base;desc=r.self_description()
    votes=tuple(RESERVED+4*i+1 for i in range(desc.inputs))
    start_info=RESERVED+4*desc.inputs
    info=tuple(start_info+2*i for i in range(r.FIELDS));hold=tuple(i+1 for i in info)
    wire_base=start_info+2*r.FIELDS
    wires=votes+tuple(wire_base+i for i in range(len(desc.operations)))
    temp=wire_base+len(desc.operations);memory=temp+1
    ops=[];entries=[];ranges=[]
    for stage in range(3):
        start=len(ops);entries.append(start)
        if stage==0:
            for selector,name in enumerate(r.STATIC):
                ops.extend((Instruction(f.LOAD,info[r.COL['address']],0,0),Instruction(f.META,info[r.COL[name]],selector,0)))
        ops.append(Instruction(LIT,0,0,temp))
        for i,source in enumerate(info):ops.append(Instruction(ADD,source,temp,RESERVED+4*(5*r.FIELDS+i)+HISTORY_OFFSETS[stage]))
        for hops in range(1,6):
            for field,source in enumerate(info):
                for direction,neighbor in ((f.LEFT,hops),(f.RIGHT,-hops)):
                    target=RESERVED+4*((5+neighbor)*r.FIELDS+field)+HISTORY_OFFSETS[stage]
                    ops.append(Instruction(f.SEND,source,target,(hops<<1)|direction))
        ops.append(Instruction(f.HALT,0,0,0));ranges.append((start,len(ops)))
    entries.append(len(ops));ops.append(Instruction(f.HALT,0,0,0));ranges.append((entries[3],len(ops)))
    entries.append(len(ops));start=len(ops)
    for i,(kind,a,b) in enumerate(desc.operations):
        ops.append(Instruction(kind,a if kind==LIT else wires[a],0 if kind==LIT else wires[b],wires[desc.inputs+i]))
    zero=next(wires[desc.inputs+i] for i,(kind,a,_) in enumerate(desc.operations) if kind==LIT and a==0)
    for target,out in zip(hold,desc.outputs):ops.append(Instruction(ADD,wires[out],zero,target))
    for selector,name in enumerate(r.STATIC):
        ops.extend((Instruction(f.LOAD,hold[r.COL['address']],0,0),Instruction(f.META,hold[r.COL[name]],selector,0)))
    ops.append(Instruction(f.HALT,0,0,0));ranges.append((start,len(ops)))
    return Layout(memory,tuple(ops),tuple(entries),info,hold,votes,wires,tuple(ranges),desc.digest())


def measure():
    g=transcript();f=r.base;gathers=[]
    for stage,(start,end) in enumerate(g.stage_ranges[:3]):
        stopped,rows=g.schedule(start,end);arrival=0
        for op,times in zip(g.instructions[start:end],rows):
            if op.kind==f.SEND:
                hops,direction=op.d>>1,op.d&1
                distance=hops*r.Q+(op.a-op.b if direction==f.LEFT else op.b-op.a)
                arrival=max(arrival,times[-1]+distance)
        gathers.append(dict(stage=stage+1,head_stopped=stopped,last_arrival=arrival))
    evaluation,_=g.schedule(*g.stage_ranges[4])
    # These bound only a delivery appended AFTER this evaluation transcript,
    # not a design that sends flags before evaluation finishes. No extra
    # instruction fetch/load/send is included, and the
    # current core length would grow if the missing delivery were compiled.
    right_distance=r.Q-5-g.hold[r.COL['f1']]
    return dict(scope=__doc__,rule=r.identity(),operations=len(r.self_description().operations),
                core_cells=g.computation_cells,memory_cells=g.memory_count,instructions=len(g.instructions),
                early_repair_ticks=g.schedule(0,2*len(r.STATIC))[0],gathers=gathers,
                evaluation_ticks=evaluation,evaluation_budget=8*r.Q,evaluation_margin=8*r.Q-evaluation,
                stage3_vote_72Q_earliest_evaluation_end=72*r.Q+evaluation,
                proposed_capture_computed_age=r.CAPTURE_AGE,
                stage3_vote_72Q_postevaluation_delivery_bound=72*r.Q+evaluation+right_distance,
                stage3_vote_70Q_gather_margin=6*r.Q-gathers[2]['last_arrival'],
                stage3_vote_70Q_delivery_margin=r.CAPTURE_AGE-(70*r.Q+evaluation+right_distance))
