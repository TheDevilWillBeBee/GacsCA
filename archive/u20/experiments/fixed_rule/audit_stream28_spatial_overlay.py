"""Literal local handoff from stream28 voted Data to spatial Hold output.

The fixture is a healthy coherent stage-five slice, not a physical execution
of the preceding 82-million-tick stages. The local transition itself is the
candidate combined fixed rule; host logic only initializes and diagnoses.
"""
import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import random
import time

from gacsca.fixed_rule import spatial_epoch as spatial
from gacsca.fixed_rule import spatial_fanout_compiler as compiler
from gacsca.fixed_rule import stream28_holder_core as core
from gacsca.fixed_rule import stream28_holder_initial as initial
from gacsca.fixed_rule import stream28_holder_program as reference
from gacsca.fixed_rule import stream28_holder_projected as projected
from gacsca.fixed_rule import stream28_holder_rule as holder
from gacsca.fixed_rule import stream28_spatial_overlay as combined
from experiments.fixed_rule.audit_spatial_full_dag import Witness,oracle
from experiments.fixed_rule.explore_spatial_topology import explore
from experiments.fixed_rule.schedule_spatial_phases import schedule


class Fixture:
    def __init__(self):
        program=reference.compiled_description()
        rng=random.Random(2026092836)
        self.words=tuple(rng.getrandbits(width) for _ in range(15)
                         for _,width in holder.SCHEMA)
        self.values=oracle(self.words)
        self.compiled=compiler.compile_capacity()
        self.placement=explore()
        self.timing=schedule(True,'hold_left')
        self.witness=Witness(self.words,self.compiled,self.placement,
                             self.timing,self.values)
        self.program=program
        self.layout=reference.layout()
        self.sources={site:int(cell.source_value)
                      for site,cell in enumerate(self.witness.initial)
                      if cell.kind==spatial.SOURCE}
        self.outputs={site:(wire,self.timing.route_arrival[len(self.compiled.uses)+field])
                      for field,wire in enumerate(program.outputs)
                      for site in (self.layout.hold[field],)}
        assert len(self.outputs)==holder.FIELDS
        assert set(self.sources).isdisjoint(self.outputs)

    def base_cell(self,site,age,t):
        site%=holder.Q
        @lru_cache(maxsize=None)
        def logical(address):
            address%=holder.Q
            data=self.sources.get(address,0)
            if address in self.outputs:
                wire,arrival=self.outputs[address]
                data=self.values[wire] if t>=arrival else 0
            elif address in self.layout.info:
                field=self.layout.info.index(address)
                data=self.words[7*holder.FIELDS+field]
            return core.Cell(**projected.record(address),address=address,
                             age=age,data=int(data))
        return projected.lift(initial.coherent_cell(logical,site))

    def neighborhood(self,site,age,t,capture=False):
        rows=[]
        for delta in combined.NEIGHBORHOOD:
            address=(site+delta)%holder.Q
            base=self.base_cell(address,age,t)
            spatial_cell=(self.witness.initial[address] if capture else
                          self.witness.cell_at(address,t))
            if capture and spatial_cell.kind==spatial.SOURCE:
                spatial_cell=spatial.replace(spatial_cell,source_value=0)
            rows.append(combined.Cell(base,spatial_cell))
        return tuple(rows)


def check():
    started=time.perf_counter()
    fixture=Fixture()
    transition=combined.local_step
    upper_neighborhood=tuple(holder.decode_cell(
        fixture.words[j*holder.FIELDS:(j+1)*holder.FIELDS])
        for j in range(15))
    scalar_upper=holder.local_step(upper_neighborhood)
    decoded_info=tuple(fixture.values[wire]
                       for wire in fixture.program.outputs)
    assert decoded_info==holder.encode_cell(scalar_upper)
    assert (combined.WIDTH,combined.NEIGHBORHOOD)==(
        holder.WIDTH+spatial.WIDTH,holder.NEIGHBORHOOD)
    with_bad_size=False
    try:transition(fixture.neighborhood(0,combined.CAPTURE_AGE,0,True)[:-1])
    except ValueError:with_bad_size=True
    assert with_bad_size

    source_site=next(site for site in fixture.sources
                     if fixture.sources[site]!=0)
    captured=transition(fixture.neighborhood(
        source_site,combined.CAPTURE_AGE,0,True))
    assert captured.evaluator.kind==spatial.SOURCE
    assert captured.evaluator.source_value==fixture.sources[source_site]
    assert captured.evaluator.age==0
    assert captured.holder.s2_head==0
    source_captures=0
    for site,value in fixture.sources.items():
        after=transition(fixture.neighborhood(
            site,combined.CAPTURE_AGE,0,True))
        if (after.evaluator.source_value!=value or
                after.evaluator.kind!=spatial.SOURCE or
                after.evaluator.age!=0):
            raise AssertionError(('wrong corrected source capture',site))
        source_captures+=1

    first=transition(fixture.neighborhood(0,holder.RESET_AGES[4],0,True))
    assert all(getattr(first.holder,f's{slot}_head')==0 for slot in range(5))

    gate_output=next((field,wire) for field,wire in enumerate(fixture.program.outputs)
                     if wire>=fixture.program.inputs and fixture.values[wire]!=0)
    field,wire=gate_output
    sink=fixture.layout.hold[field]
    arrival=fixture.timing.route_arrival[len(fixture.compiled.uses)+field]
    assert arrival<spatial.PERIOD
    assert fixture.witness.cell_at(sink,arrival-1).done==0
    replica_sites=[]
    for offset in range(-2,3):
        physical_site=(sink-offset)%holder.Q
        after=transition(fixture.neighborhood(
            physical_site,combined.RUN_START+arrival-1,arrival-1))
        assert getattr(after.holder,f's{offset+2}_data')==fixture.values[wire]
        assert after.holder.age==combined.RUN_START+arrival
        replica_sites.append(physical_site)
        if offset==0:
            assert after.evaluator.done==1
            assert after.evaluator.source_value==fixture.values[wire]

    raw_output=next((field,wire) for field,wire in enumerate(fixture.program.outputs)
                    if wire<fixture.program.inputs and fixture.values[wire]!=0)
    raw_field,raw_wire=raw_output
    raw_sink=fixture.layout.hold[raw_field]
    raw_arrival=fixture.timing.route_arrival[len(fixture.compiled.uses)+raw_field]
    raw_after=transition(fixture.neighborhood(
        raw_sink,combined.RUN_START+raw_arrival-1,raw_arrival-1))
    assert raw_after.holder.s2_data==fixture.values[raw_wire]
    assert raw_after.evaluator.done==1
    local_commit_steps=0
    for output_field,output_wire in enumerate(fixture.program.outputs):
        output_site=fixture.layout.hold[output_field]
        output_arrival=fixture.timing.route_arrival[
            len(fixture.compiled.uses)+output_field]
        for offset in range(-2,3):
            physical_site=(output_site-offset)%holder.Q
            after=transition(fixture.neighborhood(
                physical_site,combined.RUN_START+output_arrival-1,
                output_arrival-1))
            if getattr(after.holder,f's{offset+2}_data')!=fixture.values[output_wire]:
                raise AssertionError(('wrong fivefold Hold field',output_field,offset))
            if offset==0:
                assert after.evaluator.done==1
                assert after.evaluator.source_value==fixture.values[output_wire]
            local_commit_steps+=1
    info_commit_steps=0
    for output_field,output_wire in enumerate(fixture.program.outputs):
        info_site=fixture.layout.info[output_field]
        for offset in range(-2,3):
            physical_site=(info_site-offset)%holder.Q
            after=transition(fixture.neighborhood(
                physical_site,holder.U-1,
                fixture.timing.summary['latest_output_commit']))
            if getattr(after.holder,f's{offset+2}_data')!=fixture.values[output_wire]:
                raise AssertionError(('wrong fivefold Info commit',output_field,offset))
            if after.holder.age!=0:
                raise AssertionError(('work-period age failed to wrap',output_field,offset))
            info_commit_steps+=1
    assert transition is combined.local_step
    return dict(passed=True,description_sha256=fixture.program.digest(),
                combined_width_bits=combined.WIDTH,radius=7,
                source_capture_site=source_site,
                source_sites_captured=source_captures,
                gate_output_field=field,gate_output_sink=sink,
                gate_output_arrival=arrival,
                five_replicas_committed=replica_sites,
                raw_output_field=raw_field,raw_output_arrival=raw_arrival,
                all_hold_sites=len(fixture.outputs),
                complete_raw_upper_fields_checked=len(decoded_info),
                literal_fivefold_hold_commit_steps=local_commit_steps,
                literal_fivefold_info_commit_steps=info_commit_steps,
                evaluator_packet_count=len(fixture.timing.route_launch),
                seconds=time.perf_counter()-started,
                combined_rule_source_sha256=hashlib.sha256(
                    Path(combined.__file__).read_bytes()).hexdigest(),
                limitation='Literal local source capture and fivefold Hold '
                           'handoff on a coherent stage-five fixture; no '
                           'closed self-description or integrated full period.')


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
