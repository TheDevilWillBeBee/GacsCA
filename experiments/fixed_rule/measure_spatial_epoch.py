"""Sample complete-ring physical steps of the fixed gate-reuse pilot.

The trajectory witness is analytic; sampled steps call the actual radius-one
transition for every physical site and compare every state field. This does
not replace a continuous tick-by-tick replay of the whole work window.
"""
import argparse
import hashlib
import json
from pathlib import Path
import random
import time

from gacsca.fixed_rule import spatial_epoch as ca
from gacsca.fixed_rule import spatial_layer1 as first_ca
from gacsca.fixed_rule import stream28_holder_program as program_module
from gacsca.fixed_rule import stream28_holder_rule as raw
from gacsca.fixed_rule.wordcode_and import LIT,arithmetic
from experiments.fixed_rule.explore_spatial_reuse import plan


def gate_spec(program,index):
    opcode,a,b=program.operations[index]
    values=[0,0];ready=0
    if opcode!=LIT:
        for slot,wire in enumerate((a,b)):
            if wire>=program.inputs and program.operations[wire-program.inputs][0]==LIT:
                values[slot]=program.operations[wire-program.inputs][1]
                ready|=1<<slot
    return ca.GateSpec(1,opcode,a if opcode==LIT else 0,
                       program.inputs+index,values[0],values[1],ready)


def initial_cells(words,spatial_plan,include_ninth=True):
    summary,first,ninth,placement,reused,new_edges=spatial_plan
    program=program_module.compiled_description()
    rom=program_module.layout()
    assert len(words)==program.inputs
    rows=[ca.Cell(address=at) for at in range(ca.Q)]
    source_wires={}
    for edge in first.edges:
        if edge.source_wire<program.inputs:
            prior=source_wires.setdefault(edge.source,edge.source_wire)
            assert prior==edge.source_wire
    if include_ninth:
        for source,_,_,_,_,_,wire,_ in new_edges:
            if wire<program.inputs:
                prior=source_wires.setdefault(source,wire)
                assert prior==wire
    for source,wire in source_wires.items():
        assert rom.wires[wire]==source
        rows[source]=ca.replace(rows[source],kind=ca.SOURCE,source_value=int(words[wire]))

    for index,address in zip(first.gate_operations,first.gate_addresses):
        spec=gate_spec(program,index)
        rows[address]=ca.replace(rows[address],kind=ca.GATE,
            gates=(spec,ca.EMPTY_GATE,ca.EMPTY_GATE),
            arg0=spec.preload0,arg1=spec.preload1,ready=spec.preload_ready)
    if include_ninth:
        for index in ninth:
            address=placement[program.inputs+index]
            spec=gate_spec(program,index)
            row=rows[address]
            if address in reused:
                assert row.kind==ca.GATE and row.gates[0].valid
                rows[address]=ca.replace(row,gates=(row.gates[0],spec,ca.EMPTY_GATE),
                                         switch_ages=(summary['reset_tick'],0))
            else:
                assert row.kind==ca.INERT
                rows[address]=ca.replace(row,kind=ca.GATE,
                    gates=(spec,ca.EMPTY_GATE,ca.EMPTY_GATE),
                    arg0=spec.preload0,arg1=spec.preload1,ready=spec.preload_ready)

    buckets={}
    for edge in first.edges:
        buckets.setdefault(edge.source,[]).append(ca.Route(1,edge.target,
                                       edge.slot,0,0,edge.launch))
    if include_ninth:
        for source,target,slot,launch,_,_,_,_ in new_edges:
            buckets.setdefault(source,[]).append(ca.Route(1,target,slot,
                                           int(target in reused),0,launch))
    for source,routes in buckets.items():
        assert len(routes)<=ca.ROUTE_SLOTS
        rows[source]=ca.replace(rows[source],routes=tuple(routes)+
                      (ca.EMPTY_ROUTE,)*(ca.ROUTE_SLOTS-len(routes)))
    return tuple(rows)


def oracle(words):
    program=program_module.compiled_description()
    values=list(map(int,words))
    for opcode,a,b in program.operations:
        values.append(a if opcode==LIT else arithmetic(opcode,values[a],values[b]))
    return values


class Snapshot:
    def __init__(self,initial,values,spatial_plan,t,include_ninth=True):
        self.t=t
        summary,first,ninth,placement,reused,new_edges=spatial_plan
        received={};live={};completion={}
        for index,tick in zip(first.gate_operations,first.gate_completion):
            completion[program_module.compiled_description().inputs+index]=tick
        ninth_arrivals={index:[] for index in ninth}
        for edge in first.edges:
            self._edge(initial,values,t,live,received,edge.source,edge.target,
                       edge.slot,0,edge.launch,edge.arrival,edge.source_wire)
        if include_ninth:
            for source,target,slot,launch,arrival,_,wire,gate_wire in new_edges:
                self._edge(initial,values,t,live,received,source,target,slot,
                           int(target in reused),launch,arrival,wire)
                ninth_arrivals[gate_wire-program_module.compiled_description().inputs].append(arrival)
            for index in ninth:
                completion[program_module.compiled_description().inputs+index]=max(
                    ninth_arrivals[index],default=0)+1
        rows=list(initial)
        for at,row in enumerate(rows):
            updates=dict(age=t%ca.PERIOD,mail=live.get(at,ca.EMPTY_PACKET))
            if row.kind==ca.GATE:
                active=int(include_ninth and at in reused and t>=summary['reset_tick'])
                spec=row.gates[active]
                arg0=received.get((at,active,0),spec.preload0)
                arg1=received.get((at,active,1),spec.preload1)
                ready=(spec.preload_ready|int((at,active,0) in received)|
                       (2*int((at,active,1) in received)))
                done=int(t>=completion[spec.wire])
                updates.update(active_slot=active,arg0=arg0,arg1=arg1,
                               ready=ready,done=done,
                               result=values[spec.wire] if done else 0)
            rows[at]=ca.replace(row,**updates)
        self.rows=tuple(rows)
        self.live=len(live)
        self.received=len(received)

    @staticmethod
    def _edge(initial,values,t,live,received,source,target,slot,target_slot,
              launch,arrival,wire):
        payload=(initial[source].source_value if initial[source].kind==ca.SOURCE
                 else values[wire])
        if t>=arrival:
            key=(target,target_slot,slot)
            assert key not in received
            received[key]=payload
        elif t>=launch:
            at=(source+t-launch)%ca.Q
            assert at not in live,('packet collision',t,at)
            live[at]=ca.Packet(1,target,slot,target_slot,payload)


def check(include_ninth=True):
    start=time.perf_counter();rng=random.Random(2026092831)
    spatial_plan=plan()
    summary,first,ninth,placement,reused,new_edges=spatial_plan
    words=tuple(rng.getrandbits(width) for _ in range(15) for _,width in raw.SCHEMA)
    initial=initial_cells(words,spatial_plan,include_ninth)
    values=oracle(words)
    final_tick=summary['ninth_layer_last_completion'] if include_ninth else first.last_completion
    ticks={0,1,first.last_arrival,first.last_completion,final_tick}
    if include_ninth:
        ticks.update((summary['first_ninth_launch']-1,summary['first_ninth_launch'],
                      summary['reset_tick']-2,summary['reset_tick']-1,
                      summary['reset_tick'],summary['reset_tick']+1,
                      summary['last_ninth_arrival']-1,
                      summary['last_ninth_arrival']))
        for edge in (new_edges[0],new_edges[len(new_edges)//2],new_edges[-1]):
            ticks.update((edge[3]-1,edge[3],edge[4]-1,edge[4]))
    ticks.update(rng.randrange(final_tick) for _ in range(12))
    checked=[]
    for tick in sorted(ticks):
        old=Snapshot(initial,values,spatial_plan,tick,include_ninth)
        nxt=Snapshot(initial,values,spatial_plan,tick+1,include_ninth)
        for at in range(ca.Q):
            actual=ca.local_step((old.rows[(at-1)%ca.Q],old.rows[at],
                                  old.rows[(at+1)%ca.Q]))
            if actual!=nxt.rows[at]:
                fields=[name for name in ca.Cell.__dataclass_fields__
                        if getattr(actual,name)!=getattr(nxt.rows[at],name)]
                raise AssertionError(('epoch local transition mismatch',tick,at,fields))
        checked.append(tick)
    before=Snapshot(initial,values,spatial_plan,first.last_completion,include_ninth)
    for index,address in zip(first.gate_operations,first.gate_addresses):
        row=before.rows[address]
        assert row.done and row.result==values[row.gates[0].wire]
    final=Snapshot(initial,values,spatial_plan,final_tick,include_ninth)
    assert final.live==0
    if include_ninth:
        for index in ninth:
            row=final.rows[placement[program_module.compiled_description().inputs+index]]
            spec=row.gates[row.active_slot]
            assert spec.wire==program_module.compiled_description().inputs+index
            assert row.done and row.result==values[spec.wire]
    assert not any(row.collision for row in final.rows)
    return dict(passed=True,rule_width_bits=ca.WIDTH,rule_radius=1,
                evaluated_dag_prefix=9 if include_ninth else 8,
                schedule=summary,first_epoch_outputs_checked=len(first.gate_operations),
                ninth_layer_outputs_checked=len(ninth) if include_ninth else 0,
                complete_local_steps=len(checked)*ca.Q,checked_ticks=checked,
                seconds=time.perf_counter()-start,
                rule_source_sha256=hashlib.sha256(Path(ca.__file__).read_bytes()).hexdigest(),
                limitation='Isolated fixed local evaluator, sampled complete-ring steps '
                           'with analytical witness, not continuous replay or own-rule closure.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--depth',type=int,choices=(8,9),default=9)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result=check(args.depth==9)
    print(json.dumps({k:v for k,v in result.items() if k!='checked_ticks'},indent=2))
    if args.output:
        if args.output.exists():raise FileExistsError(args.output)
        args.output.write_text(json.dumps(result,indent=2)+'\n')
