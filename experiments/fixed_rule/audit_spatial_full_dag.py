"""Audit the complete own-rule DAG schedule against the fixed local rule.

An analytical trajectory is independently assembled from encoded static
routes and the event certificate. Whole-ring sampled steps and every packet,
gate, and switch endpoint are checked using spatial_epoch.local_step. This
is not a continuous tick-by-tick physical replay or self-reference closure.
"""
import argparse
from bisect import bisect_right
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import random
import time

from gacsca.fixed_rule import spatial_epoch as physical
from gacsca.fixed_rule import spatial_fanout_compiler as compiler
from gacsca.fixed_rule import stream28_holder_program as reference
from gacsca.fixed_rule import stream28_holder_rule as raw
from experiments.fixed_rule.explore_spatial_topology import explore
from experiments.fixed_rule.measure_spatial_epoch import gate_spec,oracle
from experiments.fixed_rule.schedule_spatial_phases import schedule


class Witness:
    def __init__(self,words,compiled,placement,timing,values,latch_outputs=False):
        program=reference.compiled_description()
        self.compiled=compiled
        self.placement=placement
        self.timing=timing
        self.values=values
        self.input_count=program.inputs
        self.output_sinks=timing.output_sinks
        self.output_wires=(tuple(wire for wire in program.outputs
                                 if wire in timing.output_sinks) if timing.output_sinks
                           else tuple(wire for wire in program.outputs
                                      if wire>=program.inputs))
        self.latch_outputs=latch_outputs
        self.output_source_sites=(
            {placement.sites[(wire-program.inputs,0)]:wire
             for wire in self.output_wires} if latch_outputs else {})
        assert len(self.output_source_sites)==(len(self.output_wires) if latch_outputs else 0)
        self.output_at_site={site:(wire,len(compiled.uses)+ordinal)
                             for ordinal,wire in enumerate(self.output_wires)
                             if (site:=self.output_sinks.get(wire)) is not None}
        self.gates={}
        for node in compiled.nodes:
            key=(node.gate_index,node.copy)
            site=placement.sites[key]
            slot=placement.slots[key]
            self.gates[(site,slot)]=key
        self.inbound=defaultdict(list)
        self.routes=defaultdict(list)
        self.source_sites=[]
        source_wires={}
        for edge,use in enumerate(compiled.uses):
            target=(use.consumer_gate,use.consumer_copy)
            source=(use.source_gate,use.source_copy)
            target_site=placement.sites[target]
            target_slot=placement.slots[target]
            if use.source_gate<0:
                source_site=use.source_site
                source_slot=0
                prior=source_wires.setdefault(source_site,use.logical_source_wire)
                assert prior==use.logical_source_wire
            else:
                source_site=placement.sites[source]
                source_slot=placement.slots[source]
            self.source_sites.append(source_site)
            self.inbound[target].append(edge)
            self.routes[source_site].append(physical.Route(
                1,target_site,use.arg_slot,target_slot,source_slot,
                timing.route_launch[edge]))
        for wire in program.outputs:
            if wire<program.inputs:
                site=reference.layout().wires[wire]
                prior=source_wires.setdefault(site,wire)
                assert prior==wire
        for ordinal,wire in enumerate(self.output_wires if timing.output_sinks else ()):
            edge=len(compiled.uses)+ordinal
            source=(wire-program.inputs,0)
            source_site=(reference.layout().wires[wire] if wire<program.inputs
                         else placement.sites[source])
            source_slot=(0 if wire<program.inputs else placement.slots[source])
            target_site=self.output_sinks[wire]
            self.source_sites.append(source_site)
            self.routes[source_site].append(physical.Route(
                1,target_site,0,
                3 if timing.summary['output_layout']=='hold_left' else 0,
                source_slot,timing.route_launch[edge]))
        rows=[physical.Cell(address=site) for site in range(physical.Q)]
        for site,wire in source_wires.items():
            rows[site]=physical.replace(rows[site],kind=physical.SOURCE,
                                        source_value=int(words[wire]))
        for sink in self.output_sinks.values():
            assert rows[sink].kind==physical.INERT
            rows[sink]=physical.replace(rows[sink],kind=physical.OUTPUT)
        for (site,slot),key in self.gates.items():
            row=rows[site]
            gates=list(row.gates)
            spec=gate_spec(program,key[0])
            if (latch_outputs and key[1]==0 and
                    program.inputs+key[0] in self.output_wires):
                spec=physical.replace(spec,
                    opcode=physical.OUTPUT_OPCODE[spec.opcode])
            gates[slot]=spec
            rows[site]=physical.replace(row,kind=physical.GATE,gates=tuple(gates))
        for site,row in enumerate(rows):
            if row.kind==physical.GATE:
                spec=row.gates[0]
                assert spec.valid
                switches=timing.site_switches.get(site,())
                assert len(switches)<=physical.GATE_SLOTS-1
                rows[site]=physical.replace(row,
                    switch_ages=tuple(switches)+(0,)*(physical.GATE_SLOTS-1-len(switches)),
                    arg0=spec.preload0,arg1=spec.preload1,ready=spec.preload_ready)
            routes=self.routes.get(site,())
            assert len(routes)<=physical.ROUTE_SLOTS
            if routes:
                rows[site]=physical.replace(rows[site],routes=tuple(routes)+
                              (physical.EMPTY_ROUTE,)*(physical.ROUTE_SLOTS-len(routes)))
        self.initial=tuple(rows)
        self.intervals=defaultdict(list)
        self.starts={}
        for edge in range(len(timing.route_launch)):
            launch=timing.route_launch[edge]
            arrival=timing.route_arrival[edge]
            assert 0<launch<arrival<physical.PERIOD
            direction=int(edge>=len(compiled.uses) and
                          timing.summary['output_layout']=='hold_left')
            phase=((self.source_sites[edge]+launch) if direction else
                   (self.source_sites[edge]-launch))%physical.Q
            self.intervals[(direction,phase)].append((launch,arrival,edge))
        for phase,intervals in self.intervals.items():
            intervals.sort()
            for (_,end,_),(start,_,_) in zip(intervals,intervals[1:]):
                assert end<=start,('phase overlap',phase,end,start)
            self.starts[phase]=tuple(start for start,_,_ in intervals)
        self.actual_done={}
        for key,scheduled in timing.gate_done.items():
            site=placement.sites[key]
            slot=placement.slots[key]
            if slot and not self.inbound[key]:
                self.actual_done[key]=timing.site_switches[site][slot-1]
            else:self.actual_done[key]=scheduled
        self._wrapped=None

    def cell_at(self,site,t):
        site%=physical.Q
        row=self.initial[site]
        updates=dict(age=t%physical.PERIOD)
        for direction,phase in ((0,(site-t)%physical.Q),(1,(site+t)%physical.Q)):
            key=(direction,phase)
            intervals=self.intervals.get(key,())
            if not intervals:continue
            position=bisect_right(self.starts[key],t)-1
            if position<0:continue
            launch,arrival,edge=intervals[position]
            if t>=arrival:continue
            if edge<len(self.compiled.uses):
                use=self.compiled.uses[edge]
                target=self.placement.sites[(use.consumer_gate,use.consumer_copy)]
                arg_slot=use.arg_slot
                gate_slot=self.placement.slots[(use.consumer_gate,use.consumer_copy)]
                wire=use.logical_source_wire
            else:
                wire=self.output_wires[edge-len(self.compiled.uses)]
                target=self.output_sinks[wire]
                arg_slot=0
                gate_slot=3 if direction else 0
            if 'mail' in updates:raise AssertionError('cross-direction mail collision')
            updates['mail']=physical.Packet(
                1,target,arg_slot,gate_slot,self.values[wire])
        if row.kind==physical.OUTPUT:
            wire,edge=self.output_at_site[site]
            if t>=self.timing.route_arrival[edge]:
                updates.update(source_value=self.values[wire],done=1)
        if row.kind==physical.GATE:
            slot=bisect_right(self.timing.site_switches.get(site,()),t)
            key=self.gates[(site,slot)]
            spec=row.gates[slot]
            arg0,arg1,ready=spec.preload0,spec.preload1,spec.preload_ready
            for edge in self.inbound[key]:
                if self.timing.route_arrival[edge]>t:continue
                use=self.compiled.uses[edge]
                value=self.values[use.logical_source_wire]
                if use.arg_slot:arg1=value
                else:arg0=value
                ready|=1<<use.arg_slot
            complete=t>=self.actual_done[key]
            updates.update(active_slot=slot,arg0=arg0,arg1=arg1,ready=ready,
                           result=self.values[self.input_count+key[0]] if complete else 0,
                           done=int(complete))
            if site in self.output_source_sites:
                wire=self.output_source_sites[site]
                if t>=self.actual_done[(wire-self.input_count,0)]:
                    updates['source_value']=self.values[wire]
        return physical.replace(row,**updates)

    def check_site_step(self,site,t):
        before=(self.cell_at(site-1,t),self.cell_at(site,t),
                self.cell_at(site+1,t))
        actual=physical.local_step(before)
        expected=self.cell_at(site,t+1)
        if actual!=expected:
            fields=[name for name in physical.Cell.__dataclass_fields__
                    if getattr(actual,name)!=getattr(expected,name)]
            raise AssertionError(('local spatial mismatch',site,t,fields))

    def snapshot(self,t):
        return tuple(self.cell_at(site,t) for site in range(physical.Q))

    def wrapped_snapshot(self):
        if self._wrapped is None:
            before=self.snapshot(physical.PERIOD-1)
            self._wrapped=tuple(physical.local_step((
                before[(site-1)%physical.Q],before[site],
                before[(site+1)%physical.Q])) for site in range(physical.Q))
            assert all(not cell.mail.valid and not cell.collision
                       for cell in self._wrapped)
            assert all(cell.active_slot==0 for cell in self._wrapped
                       if cell.kind==physical.GATE)
            assert all(not cell.done and cell.source_value==0
                       for cell in self._wrapped if cell.kind==physical.OUTPUT)
        return self._wrapped

    def periodic_cell_at(self,site,t):
        if t<physical.PERIOD:return self.cell_at(site,t)
        local=t-physical.PERIOD
        if not local:return self.wrapped_snapshot()[site%physical.Q]
        assert 0<local<physical.PERIOD
        return self.cell_at(site,local)

    def check_second_site_step(self,site,t):
        before=(self.periodic_cell_at(site-1,t),
                self.periodic_cell_at(site,t),
                self.periodic_cell_at(site+1,t))
        actual=physical.local_step(before)
        expected=self.periodic_cell_at(site,t+1)
        if actual!=expected:
            fields=[name for name in physical.Cell.__dataclass_fields__
                    if getattr(actual,name)!=getattr(expected,name)]
            raise AssertionError(('second-period local mismatch',site,t,fields))


def check(include_outputs=False,second_period=False,latch_outputs=False,
          output_layout='bank'):
    started=time.perf_counter()
    rng=random.Random(2026092836)
    program=reference.compiled_description()
    words=tuple(rng.getrandbits(width) for _ in range(15)
                for _,width in raw.SCHEMA)
    compiled=compiler.compile_capacity()
    placement=explore()
    assert not latch_outputs or include_outputs
    timing=schedule(include_outputs and not latch_outputs,output_layout)
    expected=oracle(words)
    witness=Witness(words,compiled,placement,timing,expected,latch_outputs)
    assert len(words)==program.inputs

    endpoint_count=0
    for edge,use in enumerate(compiled.uses):
        witness.check_site_step(witness.source_sites[edge],
                                timing.route_launch[edge]-1)
        witness.check_site_step(placement.sites[(use.consumer_gate,use.consumer_copy)],
                                timing.route_arrival[edge]-1)
        endpoint_count+=2
    for ordinal,wire in enumerate(witness.output_wires if timing.output_sinks else ()):
        edge=len(compiled.uses)+ordinal
        witness.check_site_step(witness.source_sites[edge],
                                timing.route_launch[edge]-1)
        witness.check_site_step(timing.output_sinks[wire],
                                timing.route_arrival[edge]-1)
        endpoint_count+=2
    for key,done_time in witness.actual_done.items():
        witness.check_site_step(placement.sites[key],done_time-1)
        endpoint_count+=1
    for site,times in timing.site_switches.items():
        for switch in times:
            witness.check_site_step(site,switch-1)
            endpoint_count+=1

    ticks={0,1,physical.Q-1,physical.Q,2*physical.Q-1,
           2*physical.Q,timing.summary['latest_packet_launch']-1,
           timing.summary['latest_packet_launch'],
           timing.summary['latest_packet_arrival']-1,
           timing.summary['latest_packet_arrival'],
           timing.summary['latest_gate_completion'],
           timing.summary['latest_output_commit']-1,
           timing.summary['latest_output_commit']}
    launches=timing.route_launch
    arrivals=timing.route_arrival
    for edge in (0,len(launches)//2,len(launches)-1):
        ticks.update((launches[edge]-1,launches[edge],
                      arrivals[edge]-1,arrivals[edge]))
    switches=sorted(t for times in timing.site_switches.values() for t in times)
    for switch in (switches[0],switches[len(switches)//2],switches[-1]):
        ticks.update((switch-1,switch))
    ticks.update(rng.randrange(timing.summary['latest_output_commit']) for _ in range(12))
    full_ring_steps=0
    checked_ticks=[]
    for t in sorted(ticks):
        before=witness.snapshot(t)
        after=witness.snapshot(t+1)
        for site in range(physical.Q):
            actual=physical.local_step((before[(site-1)%physical.Q],before[site],
                                        before[(site+1)%physical.Q]))
            if actual!=after[site]:
                fields=[name for name in physical.Cell.__dataclass_fields__
                        if getattr(actual,name)!=getattr(after[site],name)]
                raise AssertionError(('whole-ring spatial mismatch',site,t,fields))
        full_ring_steps+=physical.Q
        checked_ticks.append(t)
    output_checks=0
    if include_outputs:
        final=witness.snapshot(timing.summary['latest_output_commit'])
        layout=reference.layout()
        for wire in program.outputs:
            site=(timing.output_sinks[wire]
                  if timing.summary['output_layout']=='hold_left' else
                  layout.wires[wire] if wire<program.inputs else
                  placement.sites[(wire-program.inputs,0)] if latch_outputs else
                  timing.output_sinks[wire])
            cell=final[site]
            assert (cell.kind==physical.OUTPUT
                    if timing.summary['output_layout']=='hold_left' else
                    cell.kind==physical.SOURCE if wire<program.inputs else
                    cell.kind==physical.GATE if latch_outputs else cell.done)
            assert cell.source_value==expected[wire],('wrong decoded output',wire)
            output_checks+=1
        assert tuple(final[(placement.sites[(wire-program.inputs,0)]
                            if latch_outputs else timing.output_sinks[wire])].source_value
                     for wire in witness.output_wires)==tuple(
                         expected[wire] for wire in witness.output_wires)
    second_endpoint_count=0
    second_full_ring_steps=0
    if second_period:
        assert include_outputs
        boundary=witness.wrapped_snapshot()
        assert all(cell.kind!=physical.OUTPUT or not cell.done for cell in boundary)
        for edge,use in enumerate(compiled.uses):
            witness.check_second_site_step(witness.source_sites[edge],
                    physical.PERIOD+timing.route_launch[edge]-1)
            witness.check_second_site_step(
                    placement.sites[(use.consumer_gate,use.consumer_copy)],
                    physical.PERIOD+timing.route_arrival[edge]-1)
            second_endpoint_count+=2
        for ordinal,wire in enumerate(witness.output_wires if timing.output_sinks else ()):
            edge=len(compiled.uses)+ordinal
            witness.check_second_site_step(witness.source_sites[edge],
                    physical.PERIOD+timing.route_launch[edge]-1)
            witness.check_second_site_step(timing.output_sinks[wire],
                    physical.PERIOD+timing.route_arrival[edge]-1)
            second_endpoint_count+=2
        for key,done_time in witness.actual_done.items():
            if done_time==1 and boundary[placement.sites[key]].done:continue
            witness.check_second_site_step(placement.sites[key],
                                           physical.PERIOD+done_time-1)
            second_endpoint_count+=1
        for site,times in timing.site_switches.items():
            for switch in times:
                witness.check_second_site_step(site,physical.PERIOD+switch-1)
                second_endpoint_count+=1
        for t in (physical.PERIOD,physical.PERIOD+1,
                  physical.PERIOD+timing.summary['latest_output_commit']-1):
            for site in range(physical.Q):
                witness.check_second_site_step(site,t)
                second_full_ring_steps+=1
        last=physical.PERIOD+timing.summary['latest_output_commit']
        for wire in program.outputs:
            site=(timing.output_sinks[wire]
                  if timing.summary['output_layout']=='hold_left' else
                  reference.layout().wires[wire] if wire<program.inputs else
                  placement.sites[(wire-program.inputs,0)] if latch_outputs else
                  timing.output_sinks[wire])
            assert witness.periodic_cell_at(site,last).source_value==expected[wire]
    return dict(passed=True,description_sha256=program.digest(),
                physical_rule_width_bits=physical.WIDTH,
                gate_instances_checked=len(compiled.nodes),
                packet_launch_and_delivery_endpoints_checked=2*len(timing.route_launch),
                output_words_checked=output_checks,
                output_mode=('latch' if latch_outputs else
                             output_layout if include_outputs else 'none'),
                total_endpoint_site_steps=endpoint_count,
                sampled_full_ring_site_steps=full_ring_steps,
                second_period_endpoint_site_steps=second_endpoint_count,
                second_period_full_ring_site_steps=second_full_ring_steps,
                sampled_full_ring_ticks=checked_ticks,
                latest_gate_completion=timing.summary['latest_gate_completion'],
                latest_output_commit=timing.summary['latest_output_commit'],
                seconds=time.perf_counter()-started,
                compiler_source_sha256=hashlib.sha256(Path(compiler.__file__).read_bytes()).hexdigest(),
                topology_source_sha256=hashlib.sha256(Path(explore.__code__.co_filename).read_bytes()).hexdigest(),
                physical_rule_source_sha256=hashlib.sha256(Path(physical.__file__).read_bytes()).hexdigest(),
                schedule_source_sha256=hashlib.sha256(Path(schedule.__code__.co_filename).read_bytes()).hexdigest(),
                audit_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                limitation='Analytical witness checked at all event endpoints '
                           'and sampled whole-ring ticks; no continuous '
                           'physical replay or complete self-simulation macrostep.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--include-outputs',action='store_true')
    parser.add_argument('--latch-outputs',action='store_true')
    parser.add_argument('--output-layout',choices=('bank','hold','hold_left'),default='bank')
    parser.add_argument('--second-period',action='store_true')
    args=parser.parse_args()
    if args.second_period and not args.include_outputs:
        parser.error('--second-period requires --include-outputs')
    if args.latch_outputs and not args.include_outputs:
        parser.error('--latch-outputs requires --include-outputs')
    result=check(args.include_outputs,args.second_period,args.latch_outputs,
                 args.output_layout)
    print(json.dumps({key:value for key,value in result.items()
                      if key!='sampled_full_ring_ticks'},indent=2))
    if args.output:
        if args.output.exists():raise FileExistsError(args.output)
        args.output.write_text(json.dumps(result,indent=2)+'\n')
