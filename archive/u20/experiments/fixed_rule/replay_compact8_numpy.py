"""Continuous 8Q physical replay of the encoded changed own-F circuit.

The NumPy loop reads only initialized physical gate/route rows and evolving
registers. It has no DAG, oracle, or timing lookup in its transition. Selected
whole-ring steps are compared to literal spatial_epoch8.local_step. Upper
static input words are supplied externally, so this is not closure.
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

from gacsca.fixed_rule import spatial_epoch8 as physical
from gacsca.fixed_rule import stream28_compact_vote_optimized8 as optimized
from gacsca.fixed_rule import stream28_dual_pass_optimized8 as dual_optimized
from gacsca.fixed_rule import stream28_dual_pass_optimized20 as dual_optimized20
from gacsca.fixed_rule.wordcode_and import LIT,arithmetic
from experiments.fixed_rule.build_compact8_circuit import (
    initial_cells,static_plan)
from experiments.fixed_rule.measure_stream28_spatial_capacity import (
    PROJECTED_OUTPUT_FIELDS)


def replay(periods=1,spatial_rom_center=None,dual_pass=False,
           full_dual_rom=False,typed_words=None,u20=False,
           captured_rows=None,record_output_events=False,return_rows=False,
           snapshot_ages=()):
    if periods not in (1,2):raise ValueError('one or two evaluator periods')
    if u20 and not dual_pass:
        raise ValueError('U20 candidate requires dual pass')
    if full_dual_rom and (not dual_pass or spatial_rom_center is None):
        raise ValueError('full own-ROM projection requires dual mode/address')
    started=time.perf_counter()
    plan=static_plan(dual_pass,u20)
    routes=plan['routes']
    program=routes.program
    rng=random.Random(2026092847)
    widths=(dual_optimized20 if u20 else
            dual_optimized if dual_pass else optimized).WIDTHS
    words=(tuple(rng.getrandbits(width) for width in widths)
           if typed_words is None else tuple(map(int,typed_words)))
    if (len(words)!=len(widths) or
            any(not 0<=word<1<<width
                for word,width in zip(words,widths))):
        raise ValueError('complete typed own-F input words required')
    spatial_rom_digest=None
    holder_rom_digest=None
    if spatial_rom_center is not None:
        from experiments.fixed_rule.compact8_address_rom import (
            spatial_static_digest)
        spatial_rom_digest=spatial_static_digest(dual_pass,u20)
        if full_dual_rom:
            from experiments.fixed_rule.compact8_address_rom import (
                project_all_dual_static)
            from gacsca.fixed_rule import stream28_dual_holder_rom
            holder_rom_digest=stream28_dual_holder_rom.digest()
            words=project_all_dual_static(spatial_rom_center,words,u20)
        else:
            from experiments.fixed_rule.compact8_address_rom import (
                project_spatial_static)
            words=project_spatial_static(spatial_rom_center,words,
                                         dual_pass,u20)
    input_digest=hashlib.sha256(b''.join(
        int(word).to_bytes(8,'little') for word in words)).hexdigest()
    initialized=initial_cells(words,dual_pass,u20)
    if captured_rows is not None:
        if tuple(captured_rows)!=tuple(initialized):
            raise AssertionError('literal full-rule capture differs from encoded evaluator entry')
        rows=tuple(captured_rows)
    else:rows=initialized
    q=physical.Q
    period=physical.PERIOD
    expected_outputs=program.evaluate(words)
    oracle=list(words)
    for opcode,a,b in program.operations:
        oracle.append(a if opcode==LIT else
                      arithmetic(opcode,oracle[a],oracle[b]))
    buffer_sources={edge.target_id:edge.source_id
                    for edge in routes.edges
                    if edge.target_kind=='gate' and
                       edge.target_id[0]>=len(program.operations) and
                       edge.source_kind=='raw'}
    assert len(buffer_sources)==2
    site_key={(site,slot):key for key,(site,slot,weight)
              in routes.gate_positions.items()}

    kind=np.fromiter((row.kind for row in rows),dtype=np.uint8,count=q)
    active=np.zeros(q,dtype=np.uint8)
    arg0=np.fromiter((row.arg0 for row in rows),dtype=np.uint64,count=q)
    arg1=np.fromiter((row.arg1 for row in rows),dtype=np.uint64,count=q)
    ready=np.fromiter((row.ready for row in rows),dtype=np.uint8,count=q)
    result=np.zeros(q,dtype=np.uint64)
    done=np.zeros(q,dtype=np.bool_)
    source=np.fromiter((row.source_value for row in rows),
                       dtype=np.uint64,count=q)
    address=np.arange(q,dtype=np.int32)
    gate_sites=np.flatnonzero(kind==physical.GATE)
    output_sites=np.flatnonzero(kind==physical.OUTPUT)
    op=np.zeros((q,physical.GATE_SLOTS),dtype=np.uint8)
    literal=np.zeros((q,physical.GATE_SLOTS),dtype=np.uint64)
    preload0=np.zeros((q,physical.GATE_SLOTS),dtype=np.uint64)
    preload1=np.zeros((q,physical.GATE_SLOTS),dtype=np.uint64)
    preload_ready=np.zeros((q,physical.GATE_SLOTS),dtype=np.uint8)
    base_opcodes=np.array([physical.base_opcode(code) for code in range(16)],
                          dtype=np.uint8)
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
    emissions=[0]*periods
    output_events=[]
    requested_snapshots=set(snapshot_ages)
    snapshot_states={}
    deliveries=[0]*periods
    completions=[0]*(periods+1)
    literal_steps=0
    checked_outputs=0
    literal_ticks={0,1,8191,8192,34224,34225,34226,
                   plan['output_launch'],39803,period-1}
    snapshots=[]
    output_edges=tuple(edge for edge in routes.edges
                       if edge.target_kind=='output')
    output_commit_tick=plan['output_launch']+max(
        edge.distance for edge in output_edges)
    literal_ticks.update((plan['timing']['latest_event']-1,
                          plan['timing']['latest_event'],
                          output_commit_tick-1))
    if periods==2:
        literal_ticks.update((period,period+34225,
                              period+output_commit_tick-1,2*period-1))
    first_wrap=None

    def live_fields():
        return tuple(array.copy() for array in
                     (active,arg0,arg1,ready,result,done,source,
                      mail_valid,mail_target,mail_arg,mail_gate,mail_value))

    def current_rows(age):
        return tuple(physical.replace(rows[site],age=age,
            active_slot=int(active[site]),arg0=int(arg0[site]),
            arg1=int(arg1[site]),ready=int(ready[site]),
            result=int(result[site]),done=int(done[site]),
            source_value=int(source[site]),
            mail=(physical.Packet(1,int(mail_target[site]),
                    int(mail_arg[site]),int(mail_gate[site]),
                    int(mail_value[site])) if mail_valid[site]
                  else physical.EMPTY_PACKET))
            for site in range(q))

    for t in range(period*periods):
        phase=t//period
        literal_before=current_rows(t%period) if t in literal_ticks else None
        age=(t+1)%period
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
                raise AssertionError(('invalid encoded gate switch',t,site,slot))
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
        mail_target=np.where(rightward,target_right,
                             np.where(leftward,target_left,0))
        mail_arg=np.where(rightward,arg_right,np.where(leftward,arg_left,0))
        mail_gate=np.where(rightward,gate_right,
                           np.where(leftward,gate_left,0))
        mail_value=np.where(rightward,value_right,
                            np.where(leftward,value_left,0))
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
                if record_output_events and phase==0:
                    output_events.append((int(age),int(site),value))
            else:
                bit=1<<int(mail_arg[site])
                old=int(arg1[site] if bit==2 else arg0[site])
                if ready[site]&bit and old!=value:
                    raise AssertionError(('conflicting gate input',t,site))
                if bit==2:arg1[site]=value
                else:arg0[site]=value
                ready[site]|=bit
            deliveries[phase]+=1
        mail_valid[hit]=False
        mail_target[hit]=0
        mail_arg[hit]=0
        mail_gate[hit]=0
        mail_value[hit]=0

        for site,route in launches.get(age,()):
            if mail_valid[site]:
                raise AssertionError(('mail/emission collision',t,site))
            if kind[site]==physical.SOURCE:
                value=source[site]
            elif kind[site]==physical.GATE:
                marked=(route.target_gate_slot==3 and
                        rows[site].gates[route.source_gate_slot].opcode
                        in physical.OUTPUT_BASE_OPCODE)
                if marked:value=source[site]
                elif active[site]==route.source_gate_slot and done[site]:
                    value=result[site]
                else:raise AssertionError(('source not ready',t,site))
            else:raise AssertionError(('invalid emitter kind',t,site))
            mail_valid[site]=True
            mail_target[site]=route.target
            mail_arg[site]=route.arg_slot
            mail_gate[site]=route.target_gate_slot
            mail_value[site]=value
            emissions[phase]+=1

        gate_op=op[address,active]
        normalized=base_opcodes[gate_op]
        compute=(kind==physical.GATE)&(~done)&(
            (normalized==LIT)|(compute_ready==3))
        for site in np.flatnonzero(compute):
            slot=int(active[site])
            marked=int(op[site,slot])
            opcode=physical.base_opcode(marked)
            value=(int(literal[site,slot]) if opcode==LIT else
                   arithmetic(opcode,int(arg0[site]),int(arg1[site])))
            result[site]=value
            done[site]=True
            if marked in physical.OUTPUT_BASE_OPCODE:
                source[site]=value
            key=site_key[(site,slot)]
            want=(oracle[program.inputs+key[0]]
                  if key[0]<len(program.operations) else
                  words[buffer_sources[key]])
            if value!=want:
                raise AssertionError(('wrong gate result',t,site,slot,key,
                                      value,want))
            completions[phase+int(age==0)]+=1

        if t+1==phase*period+output_commit_tick:
            for edge in output_edges:
                want=expected_outputs[PROJECTED_OUTPUT_FIELDS[edge.target_id]]
                if int(source[edge.target_site])!=want:
                    raise AssertionError(('wrong Hold output',t,edge.target_id))
                checked_outputs+=1
        if literal_before is not None:
            after=current_rows(age)
            for site in range(q):
                want=physical.local_step((literal_before[(site-1)%q],
                                          literal_before[site],
                                          literal_before[(site+1)%q]))
                if want!=after[site]:
                    raise AssertionError(('vector/literal mismatch',t,site))
                literal_steps+=1
            snapshots.append(t+1)
        if phase==0 and age in requested_snapshots:
            snapshot_states[int(age)]=current_rows(age)

        if t+1==period:first_wrap=live_fields()
        if t+1==2*period:
            if first_wrap is None or any(
                    not np.array_equal(a,b)
                    for a,b in zip(live_fields(),first_wrap)):
                raise AssertionError('spatial state differs at successive wraps')

    if (any(value!=len(routes.edges) for value in emissions) or
            any(value!=len(routes.edges) for value in deliveries) or
            any(value!=len(routes.gate_positions)
                for value in completions[:periods]) or
            checked_outputs!=119*periods):
        raise AssertionError(('incomplete physical 8Q period',emissions,
                              deliveries,completions,checked_outputs))
    report=dict(passed=True,description_sha256=program.digest(),
                dual_pass_own_rule=dual_pass,
                literal_full_rule_capture_supplied=captured_rows is not None,
                physical_output_events=output_events if record_output_events else None,
                requested_snapshot_ages=sorted(requested_snapshots),
                upper_work_period=(1<<20 if u20 else 1<<28),
                typed_input_sha256=input_digest,
                spatial_static_rom_sha256=spatial_rom_digest,
                holder_static_rom_sha256=holder_rom_digest,
                spatial_rom_center=spatial_rom_center,
                spatial_static_inputs_from_own_address=(
                    spatial_rom_center is not None),
                holder_static_inputs_from_own_address=full_dual_rom,
                physical_rule_source_sha256=hashlib.sha256(
                    Path(physical.__file__).read_bytes()).hexdigest(),
                Q=q,period=period,physical_width_bits=physical.WIDTH,
                ticks_evolved=period*periods,
                physical_site_ticks=q*period*periods,
                packet_emissions=emissions,packet_deliveries=deliveries,
                gate_completions=completions[:periods],
                next_period_initial_gate_completions=completions[periods],
                complete_periods_checked=periods,
                successive_wraps_equal=(periods==2),
                projected_output_words_checked=checked_outputs,
                literal_local_site_steps=literal_steps,
                sampled_full_ring_ticks=snapshots,
                seconds=time.perf_counter()-started,
                max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                limitation=('One or two isolated evaluator periods with all '
                            'static inputs address-derived from the provisional '
                            'dual ROM; no complete holder work period, ROM '
                            'repair, or hierarchical self-simulation.'
                            if full_dual_rom else
                            'One or two isolated evaluator periods; upper '
                            'holder static words remain externally supplied '
                            'and no complete colony self-simulation has been '
                            'replayed.'))
    if requested_snapshots-set(snapshot_states):
        raise AssertionError('requested physical evaluator snapshot missing')
    return (report,current_rows(0),snapshot_states) if return_rows else report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--periods',type=int,default=1)
    parser.add_argument('--spatial-rom-center',type=int)
    parser.add_argument('--dual-pass',action='store_true')
    parser.add_argument('--full-dual-rom',action='store_true')
    parser.add_argument('--u20',action='store_true')
    args=parser.parse_args()
    result=replay(args.periods,args.spatial_rom_center,args.dual_pass,
                  args.full_dual_rom,u20=args.u20)
    result['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    print(json.dumps(result,indent=2))
    if args.output:
        if args.output.exists():raise FileExistsError(args.output)
        args.output.write_text(json.dumps(result,indent=2)+'\n')
