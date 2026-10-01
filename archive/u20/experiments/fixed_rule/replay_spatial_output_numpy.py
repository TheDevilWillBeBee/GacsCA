"""Continuously replay the encoded spatial evaluator with dense NumPy mail.

The replay evolves all 8192 physical sites at every tick. Static descriptions
come from the encoded initial cells; the loop never reads the compiled DAG or
analytical timing. The analytical witness and own-F oracle are diagnostics.
This is an independent equivalent implementation, not a call to the literal
Python local_step at every site/tick, and not an integrated self-simulator.
"""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import random
import resource
import time

import numpy as np

from gacsca.fixed_rule import spatial_epoch as physical
from gacsca.fixed_rule import spatial_fanout_compiler as compiler
from gacsca.fixed_rule import stream28_holder_program as reference
from gacsca.fixed_rule import stream28_holder_rule as raw
from gacsca.fixed_rule.wordcode_and import LIT,arithmetic
from experiments.fixed_rule.audit_spatial_full_dag import Witness,oracle
from experiments.fixed_rule.explore_spatial_topology import explore
from experiments.fixed_rule.schedule_spatial_phases import schedule


def replay(periods=2,steps=None,latch_outputs=False,output_layout='bank'):
    started=time.perf_counter()
    program=reference.compiled_description()
    rng=random.Random(2026092836)
    words=tuple(rng.getrandbits(width) for _ in range(15)
                for _,width in raw.SCHEMA)
    compiled=compiler.compile_capacity()
    placement=explore()
    timing=schedule(not latch_outputs,output_layout)
    values=oracle(words)
    witness=Witness(words,compiled,placement,timing,values,latch_outputs)
    rows=witness.initial
    q=physical.Q
    period=physical.PERIOD
    total=steps if steps is not None else periods*period
    assert 0<total<=2*period

    kind=np.fromiter((c.kind for c in rows),dtype=np.uint8,count=q)
    active=np.fromiter((c.active_slot for c in rows),dtype=np.uint8,count=q)
    arg0=np.fromiter((c.arg0 for c in rows),dtype=np.uint64,count=q)
    arg1=np.fromiter((c.arg1 for c in rows),dtype=np.uint64,count=q)
    ready=np.fromiter((c.ready for c in rows),dtype=np.uint8,count=q)
    result=np.fromiter((c.result for c in rows),dtype=np.uint64,count=q)
    done=np.fromiter((c.done for c in rows),dtype=np.bool_,count=q)
    source=np.fromiter((c.source_value for c in rows),dtype=np.uint64,count=q)
    address=np.arange(q,dtype=np.int32)
    gate_sites=np.flatnonzero(kind==physical.GATE)
    output_sites=np.flatnonzero(kind==physical.OUTPUT)
    op=np.zeros((q,physical.GATE_SLOTS),dtype=np.uint8)
    literal=np.zeros((q,physical.GATE_SLOTS),dtype=np.uint64)
    preload0=np.zeros((q,physical.GATE_SLOTS),dtype=np.uint64)
    preload1=np.zeros((q,physical.GATE_SLOTS),dtype=np.uint64)
    preload_ready=np.zeros((q,physical.GATE_SLOTS),dtype=np.uint8)
    base_opcodes=np.array([physical.base_opcode(opcode)
                           for opcode in range(16)],dtype=np.uint8)
    switches=defaultdict(list)
    launches=defaultdict(list)
    for site,row in enumerate(rows):
        if row.kind==physical.GATE:
            for slot,spec in enumerate(row.gates):
                op[site,slot]=spec.opcode
                literal[site,slot]=spec.literal
                preload0[site,slot]=spec.preload0
                preload1[site,slot]=spec.preload1
                preload_ready[site,slot]=spec.preload_ready
            for slot,age in enumerate(row.switch_ages):
                if age:switches[age].append((site,slot))
        for route in row.routes:
            if route.valid:launches[route.launch].append((site,route))

    mail_valid=np.zeros(q,dtype=np.bool_)
    mail_target=np.zeros(q,dtype=np.int32)
    mail_arg=np.zeros(q,dtype=np.uint8)
    mail_gate=np.zeros(q,dtype=np.uint8)
    mail_value=np.zeros(q,dtype=np.uint64)
    expected_emissions=len(timing.route_launch)
    emission_counts=[0,0]
    delivery_counts=[0,0]
    completion_counts=[0,0,0]
    snapshots={1,physical.Q-1,physical.Q,20137,28929,32100,
               period-1,period,period+1,period+physical.Q,
               period+28929,period+32100,2*period-1}
    snapshots={t for t in snapshots if t<=total}
    checked=[]
    at_first_wrap=None
    output_words_checked=0
    output_commit_tick=timing.summary['latest_output_commit']
    literal_ticks={0,q-1,timing.summary['latest_output_commit']-1,
                   period-1,period,2*period-1}
    literal_steps=0

    def live_fields():
        return tuple(array.copy() for array in
                     (active,arg0,arg1,ready,result,done,source,
                      mail_valid,mail_target,mail_arg,mail_gate,mail_value))

    def check_snapshot(t):
        for site in range(q):
            expected=witness.periodic_cell_at(site,t)
            actual_mail=(physical.Packet(1,int(mail_target[site]),int(mail_arg[site]),
                                         int(mail_gate[site]),int(mail_value[site]))
                         if mail_valid[site] else physical.EMPTY_PACKET)
            fields=(int(active[site]),int(arg0[site]),int(arg1[site]),
                    int(ready[site]),int(result[site]),int(done[site]),
                    int(source[site]),actual_mail)
            want=(expected.active_slot,expected.arg0,expected.arg1,
                  expected.ready,expected.result,expected.done,
                  expected.source_value,expected.mail)
            if fields!=want:
                raise AssertionError(('continuous replay mismatch',t,site,fields,want))
        checked.append(t)

    def literal_snapshot(t):
        return tuple(physical.replace(rows[site],age=t%period,
                    active_slot=int(active[site]),arg0=int(arg0[site]),
                    arg1=int(arg1[site]),ready=int(ready[site]),
                    result=int(result[site]),done=int(done[site]),
                    source_value=int(source[site]),
                    mail=(physical.Packet(1,int(mail_target[site]),
                            int(mail_arg[site]),int(mail_gate[site]),
                            int(mail_value[site])) if mail_valid[site]
                            else physical.EMPTY_PACKET)) for site in range(q))

    for t in range(total):
        before_literal=literal_snapshot(t) if t in literal_ticks else None
        age=(t+1)%period
        phase=t//period
        if age==0:
            active[gate_sites]=0
            arg0[gate_sites]=preload0[gate_sites,0]
            arg1[gate_sites]=preload1[gate_sites,0]
            ready[gate_sites]=preload_ready[gate_sites,0]
            result[gate_sites]=0
            done[gate_sites]=False
            source[gate_sites]=0
            source[output_sites]=0
            done[output_sites]=False
        for site,slot in switches.get(age,()):
            if active[site]!=slot or not rows[site].gates[slot+1].valid:
                raise AssertionError(('invalid encoded switch',t,site,slot))
            active[site]=slot+1
            arg0[site]=preload0[site,slot+1]
            arg1[site]=preload1[site,slot+1]
            ready[site]=preload_ready[site,slot+1]
            result[site]=0
            done[site]=False
        compute_ready=ready.copy()
        rightward=np.roll(mail_valid & (mail_gate!=3),1)
        leftward=np.roll(mail_valid & (mail_gate==3),-1)
        if np.any(rightward & leftward):
            raise AssertionError(('opposing mail collision',t))
        target_right=np.roll(mail_target,1)
        target_left=np.roll(mail_target,-1)
        arg_right=np.roll(mail_arg,1)
        arg_left=np.roll(mail_arg,-1)
        gate_right=np.roll(mail_gate,1)
        gate_left=np.roll(mail_gate,-1)
        value_right=np.roll(mail_value,1)
        value_left=np.roll(mail_value,-1)
        mail_valid=rightward|leftward
        mail_target=np.where(rightward,target_right,np.where(leftward,target_left,0))
        mail_arg=np.where(rightward,arg_right,np.where(leftward,arg_left,0))
        mail_gate=np.where(rightward,gate_right,np.where(leftward,gate_left,0))
        mail_value=np.where(rightward,value_right,np.where(leftward,value_left,0))
        hit=mail_valid & (mail_target==address) & (
            ((kind==physical.GATE)&(mail_gate==active)) |
            (kind==physical.OUTPUT))
        for site in np.flatnonzero(hit):
            value=int(mail_value[site])
            if kind[site]==physical.OUTPUT:
                if done[site] and int(source[site])!=value:
                    raise AssertionError(('conflicting output',t,site))
                source[site]=value
                done[site]=True
            else:
                bit=1<<int(mail_arg[site])
                old=int(arg1[site] if bit==2 else arg0[site])
                if ready[site]&bit and old!=value:
                    raise AssertionError(('conflicting operand',t,site))
                if bit==2:arg1[site]=value
                else:arg0[site]=value
                ready[site]|=bit
            delivery_counts[phase]+=1
        mail_valid[hit]=False
        mail_target[hit]=0
        mail_arg[hit]=0
        mail_gate[hit]=0
        mail_value[hit]=0

        for site,route in launches.get(age,()):
            if mail_valid[site]:raise AssertionError(('mail/emission collision',t,site))
            if kind[site]==physical.SOURCE:
                value=source[site]
            elif (kind[site]==physical.GATE and
                  active[site]==route.source_gate_slot and done[site]):
                value=result[site]
            else:raise AssertionError(('source not ready',t,site,route))
            mail_valid[site]=True
            mail_target[site]=route.target
            mail_arg[site]=route.arg_slot
            mail_gate[site]=route.target_gate_slot
            mail_value[site]=value
            emission_counts[phase]+=1

        gate_op=op[address,active]
        normalized_op=base_opcodes[gate_op]
        compute=(kind==physical.GATE)&(~done)&(
            (normalized_op==LIT)|(compute_ready==3))
        for site in np.flatnonzero(compute):
            slot=int(active[site])
            marked_opcode=int(op[site,slot])
            opcode=physical.base_opcode(marked_opcode)
            value=(int(literal[site,slot]) if opcode==LIT else
                   arithmetic(opcode,int(arg0[site]),int(arg1[site])))
            result[site]=value
            done[site]=True
            if marked_opcode in physical.OUTPUT_BASE_OPCODE:
                source[site]=value
            key=witness.gates[(site,slot)]
            if value!=values[program.inputs+key[0]]:
                raise AssertionError(('wrong gate result',t,site,slot,key))
            completion_counts[(t+1)//period]+=1
        now=t+1
        if now in (output_commit_tick,period+output_commit_tick):
            for wire in program.outputs:
                site=(timing.output_sinks[wire]
                      if timing.summary['output_layout']=='hold_left' else
                      reference.layout().wires[wire] if wire<program.inputs else
                      placement.sites[(wire-program.inputs,0)] if latch_outputs else
                      timing.output_sinks[wire])
                if int(source[site])!=values[wire]:
                    raise AssertionError(('wrong physical output',now,wire,site))
                output_words_checked+=1
        if before_literal is not None:
            after_literal=literal_snapshot(now)
            for site in range(q):
                actual=physical.local_step((before_literal[(site-1)%q],
                                            before_literal[site],
                                            before_literal[(site+1)%q]))
                if actual!=after_literal[site]:
                    raise AssertionError(('vector/literal mismatch',t,site))
                literal_steps+=1
        if now in snapshots:check_snapshot(now)
        if now==period:at_first_wrap=live_fields()
        if now==2*period:
            if at_first_wrap is None:raise AssertionError('missing first wrap')
            if any(not np.array_equal(a,b) for a,b in zip(live_fields(),at_first_wrap)):
                raise AssertionError('physical state did not return at second wrap')

    complete_periods=total//period
    for i in range(complete_periods):
        if (emission_counts[i]!=expected_emissions or
                delivery_counts[i]!=expected_emissions or
                completion_counts[i]!=len(compiled.nodes)):
            raise AssertionError(('incomplete physical period',i,
                                  emission_counts[i],delivery_counts[i],
                                  completion_counts[i]))
    return dict(passed=True,description_sha256=program.digest(),
                physical_rule_source_sha256=hashlib.sha256(
                    Path(physical.__file__).read_bytes()).hexdigest(),
                Q=q,period=period,cell_width_bits=physical.WIDTH,
                ticks_evolved=total,physical_site_ticks=q*total,
                packet_emissions=emission_counts,packet_deliveries=delivery_counts,
                gate_completions=completion_counts[:2],
                next_period_initial_completions=completion_counts[2],
                complete_periods_checked=complete_periods,
                output_mode='latch' if latch_outputs else output_layout,
                output_words_checked=output_words_checked,
                literal_local_site_steps=literal_steps,
                sampled_full_state_ticks=checked,
                max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                seconds=time.perf_counter()-started,
                compiler_source_sha256=hashlib.sha256(
                    Path(compiler.__file__).read_bytes()).hexdigest(),
                topology_source_sha256=hashlib.sha256(
                    Path(explore.__code__.co_filename).read_bytes()).hexdigest(),
                schedule_source_sha256=hashlib.sha256(
                    Path(schedule.__code__.co_filename).read_bytes()).hexdigest(),
                initializer_source_sha256=hashlib.sha256(
                    Path(Witness.__init__.__code__.co_filename).read_bytes()).hexdigest(),
                limitation='Independent continuous vectorized replay of the '
                           'isolated evaluator, with literal-rule sampled '
                           'checks; no integrated self-simulation macrostep.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--periods',type=int,default=2)
    parser.add_argument('--ticks',type=int)
    parser.add_argument('--latch-outputs',action='store_true')
    parser.add_argument('--output-layout',choices=('bank','hold','hold_left'),default='bank')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result=replay(args.periods,args.ticks,args.latch_outputs,args.output_layout)
    result['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    print(json.dumps(result,indent=2))
    if args.output:
        if args.output.exists():raise FileExistsError(args.output)
        args.output.write_text(json.dumps(result,indent=2)+'\n')
