"""Audit an initial descriptor prefix through one fixed local evaluator.

An analytical trajectory is used only as an independent witness and to
select sampled times. At each sampled time every Q physical cell is advanced
by the actual radius-one rule and compared field-for-field with the witness.
"""
import argparse
import hashlib
import json
from pathlib import Path
import random
import time

from gacsca.fixed_rule import spatial_layer1 as s
from gacsca.fixed_rule import stream28_holder_program as p
from gacsca.fixed_rule import stream28_holder_rule as f


class Snapshot:
    def __init__(self,initial,expected,t,max_depth=1,phase_policy='earliest'):
        self.t=t;self.placement=s.layout(max_depth,phase_policy);self.rows=list(initial)
        live={};received={}
        for edge in self.placement.edges:
            payload=(initial[edge.source].source_value if initial[edge.source].kind==s.SOURCE
                     else expected[edge.source_wire])
            if t>=edge.arrival:
                key=edge.target,edge.slot
                assert key not in received
                received[key]=payload
            elif t>=edge.launch:
                at=edge.source+t-edge.launch
                assert at not in live,('same-lane collision',t,at)
                live[at]=s.Packet(1,edge.target,edge.slot,payload)
        completion=dict(zip(self.placement.gate_addresses,self.placement.gate_completion))
        for at,row in enumerate(self.rows):
            updates=dict(age=t%s.PERIOD,mail=live.get(at,s.EMPTY_PACKET))
            if row.kind==s.GATE:
                updates.update(arg0=received.get((at,0),row.arg0),
                               arg1=received.get((at,1),row.arg1),
                               ready=row.ready|int((at,0) in received)|
                                     (2*int((at,1) in received)))
                if t>=completion[at]:
                    updates.update(result=expected[row.gate_wire],done=1)
            self.rows[at]=s.replace(row,**updates)
        self.rows=tuple(self.rows)
        self.live=len(live)
        self.received=len(received)


def check(max_depth=1,phase_policy='earliest'):
    started=time.perf_counter();rng=random.Random(2026092831)
    program=p.compiled_description()
    words=tuple(rng.getrandbits(width) for _ in range(15) for _,width in f.SCHEMA)
    assert len(words)==program.inputs
    initial=s.initial_cells(words,max_depth,phase_policy)
    expected=s.expected_prefix(words,max_depth,phase_policy)
    certificate=s.schedule_certificate(max_depth,phase_policy)
    g=s.layout(max_depth,phase_policy)
    representatives=(g.edges[0],g.edges[len(g.edges)//2],g.edges[-1],
                     max(g.edges,key=lambda edge:edge.arrival))
    ticks={0,1,s.Q//4,s.Q//2,s.Q-1,s.Q,
           g.last_arrival-1,g.last_arrival,g.last_completion}
    for edge in representatives:
        ticks.update((edge.launch-1,edge.launch,edge.arrival-1,edge.arrival))
    ticks.update(rng.randrange(g.last_completion) for _ in range(10))
    checked=[]
    for t in sorted(ticks):
        old=Snapshot(initial,expected,t,max_depth,phase_policy)
        new=Snapshot(initial,expected,t+1,max_depth,phase_policy)
        for at in range(s.Q):
            actual=s.local_step((old.rows[(at-1)%s.Q],old.rows[at],old.rows[(at+1)%s.Q]))
            if actual!=new.rows[at]:
                fields=[name for name in s.Cell.__dataclass_fields__
                        if getattr(actual,name)!=getattr(new.rows[at],name)]
                raise AssertionError(('spatial local transition mismatch',t,at,fields))
        checked.append(dict(tick=t,complete_sites=s.Q,
                            live_packets=old.live,received_operands=old.received))
    final=Snapshot(initial,expected,g.last_completion,max_depth,phase_policy)
    assert final.live==0 and final.received==len(g.edges)
    for index,address in zip(g.gate_operations,g.gate_addresses):
        cell=final.rows[address]
        assert cell.done and cell.result==expected[cell.gate_wire],('incomplete gate',index,address)
    assert not any(cell.collision for cell in final.rows)
    return dict(passed=True,schedule=certificate,
                evaluated_prefix_outputs_checked=len(expected),
                complete_local_steps=len(checked)*s.Q,
                checked_ticks=checked,seconds=time.perf_counter()-started,
                rule_source_sha256=hashlib.sha256(Path(s.__file__).read_bytes()).hexdigest(),
                limitation='Initial descriptor dependency prefix only; witness-based '
                           'sampled whole-ring steps, no complete 8Q tick replay, '
                           'later-layer routing, or self-description closure.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--depth',type=int,default=1)
    parser.add_argument('--policy',choices=('earliest','ordinal'),default='earliest')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result=check(args.depth,args.policy)
    path=args.output or Path(f'figs/fixed_rule/spatial_layer{args.depth}_{args.policy}_v1.json')
    if path.exists():raise FileExistsError(path)
    path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:value for key,value in result.items() if key!='checked_ticks'},indent=2))
