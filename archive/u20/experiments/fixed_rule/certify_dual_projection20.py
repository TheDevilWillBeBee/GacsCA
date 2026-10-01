"""Decode the changed own-rule circuit against its address-projected rule.

All 119 evolving words, including holder controller copies and active spatial
workspace, are compared. The optional physical period runs the encoded local
evaluator; it does not replace the upper transition with a host interpreter.
"""
import argparse
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import random
import resource
import time

from gacsca.fixed_rule import spatial_epoch8 as spatial
from gacsca.fixed_rule import spatial_projected8 as spatial_projected
from gacsca.fixed_rule import stream28_dual_holder_rom as holder_rom
from gacsca.fixed_rule import stream28_dual_pass20 as physical
from gacsca.fixed_rule import stream28_dual_pass_optimized20 as optimized
from gacsca.fixed_rule import stream28_dual_projected20 as projected
from gacsca.fixed_rule import stream28_holder_projected as holder_projected
from gacsca.fixed_rule import stream28_dual_holder_rule20 as holder
from experiments.fixed_rule.compact8_address_rom import (
    holder_input_wires,project_all_dual_static,spatial_input_wires,template,
    spatial_static_digest)
from experiments.fixed_rule.measure_stream28_spatial_capacity import (
    PROJECTED_OUTPUT_FIELDS)
from experiments.fixed_rule.replay_compact8_numpy import replay


def neighborhood(center,age,seed):
    rng=random.Random(seed)
    spatial_rom=template(True,True)
    rows=[]
    for offset in physical.NEIGHBORHOOD:
        address=(center+offset)%physical.Q
        hdynamic={name:rng.getrandbits(width)
                  for name,width in holder_projected.SCHEMA}
        hdynamic.update(address=address,age=age,f1=0,f2=0)
        raw=holder.Cell(**holder_rom.holder_static_fields(address),
                        **hdynamic)
        before=spatial_projected.project(spatial_rom[address])
        sdynamic=replace(before,
            age=rng.randrange(spatial.PERIOD),
            active_slot=rng.randrange(spatial.GATE_SLOTS),
            source_value=rng.getrandbits(64),
            arg0=rng.getrandbits(64),arg1=rng.getrandbits(64),
            ready=rng.randrange(4),result=rng.getrandbits(64),
            done=rng.randrange(2),
            mail=spatial.Packet(rng.randrange(2),rng.randrange(physical.Q),
                                rng.randrange(2),rng.randrange(4),
                                rng.getrandbits(64)),
            collision=rng.randrange(2))
        rows.append(physical.Cell(
            raw,spatial_projected.lift(sdynamic,spatial_rom[address])))
    return tuple(rows)


def check(*,physical_period=False):
    started=time.perf_counter()
    program=optimized.build()
    center=3218
    ages=(physical.EARLY_CAPTURE_AGE,
          physical.EARLY_RUN_START+100,
          physical.EARLY_RUN_STOP,
          holder.RESET_AGES[4]+3,
          holder.U-1)
    checked=0
    replay_words=None
    static_wires=set(holder_input_wires())|set(spatial_input_wires())
    assert len(static_wires)==390
    for ordinal,age in enumerate(ages):
        for trial in range(8):
            rows=neighborhood(center,age,2026092900+100*ordinal+trial)
            full_words=tuple(word for row in rows
                             for word in physical.encode_cell(row))
            addressed=project_all_dual_static(center,full_words,True)
            if any(addressed[wire]!=full_words[wire]
                   for wire in static_wires):
                raise AssertionError(('ROM projection differs',age,trial))
            dynamic=tuple(projected.project(row) for row in rows)
            hstatic=tuple(row.holder for row in rows)
            sstatic=tuple(template(True,True)[(center+offset)%physical.Q]
                          for offset in physical.NEIGHBORHOOD)
            want=projected.encode_cell(projected.local_step(
                dynamic,hstatic,sstatic))
            literal=projected.encode_cell(projected.project(
                physical.local_step(rows)))
            got=program.evaluate(addressed)
            circuit=tuple(got[field] for field in PROJECTED_OUTPUT_FIELDS)
            if want!=literal or circuit!=want:
                raise AssertionError(('decoded local F differs',age,trial))
            if ordinal==1 and trial==0:replay_words=full_words
            checked+=1
    physical_result=(replay(1,center,True,True,replay_words,u20=True)
                     if physical_period else None)
    if physical_result is not None:
        if (not physical_result['passed'] or
                physical_result['projected_output_words_checked']!=119):
            raise AssertionError('coherent physical evaluator period failed')
    return dict(passed=True,decoded_local_cases=checked,
                five_distinct_work_ages=ages,
                projected_words=projected.FIELDS,
                projected_width_bits=projected.WIDTH,
                spatial_static_inputs=len(spatial_input_wires()),
                holder_static_inputs=len(holder_input_wires()),
                description_sha256=program.digest(),
                spatial_rom_sha256=spatial_static_digest(True,True),
                holder_rom_sha256=holder_rom.digest(),
                physical_period_checked=physical_period,
                physical_period_receipt=physical_result,
                max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                seconds=time.perf_counter()-started,
                limitation='Exact local projection and optionally one '
                           'isolated evaluator period; no complete colony '
                           'work period or successive upper macrosteps.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--physical',action='store_true')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result=check(physical_period=args.physical)
    result['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    print(json.dumps(result,indent=2))
    if args.output:
        if args.output.exists():raise FileExistsError(args.output)
        args.output.write_text(json.dumps(result,indent=2)+'\n')
