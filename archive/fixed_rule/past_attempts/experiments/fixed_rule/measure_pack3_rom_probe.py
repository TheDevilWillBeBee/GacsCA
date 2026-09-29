"""Exact layout/path arithmetic for a proposed fixed three-ALU ROM encoding.

This is an architectural upper-bound probe, not a new physical CA or a
self-reference certificate. The decoder's own F/ROM cost is not yet included.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time

from gacsca.fixed_rule import gather29_holder_program as p
from gacsca.fixed_rule import gather29_holder_core as c
from gacsca.fixed_rule import gather29_holder_rule as f
from gacsca.fixed_rule import pack3_rom
from gacsca.fixed_rule.wordcode_and import LIT


def schedule(g,packed,pcs,stage=None):
    core=g.memory_count+len(packed.rows)+1
    cycle=2*core;phase=0;ticks=1;rows=[]
    for pc in pcs:
        op=g.instructions[pc]
        physical=g.memory_count+packed.physical_of_pc[pc]
        targets=(physical,)
        if op.kind in c.ALU_KINDS:
            d=op.d
            if stage is not None and d&c.PHASE_MARK:
                d=(d&~c.PHASE_MARK)+c.GATHER_OFFSETS[stage]
            targets+=(op.a,op.b,d)
        elif op.kind==LIT:targets+=(op.d,)
        elif op.kind in (c.SEND,c.LOAD):targets+=(op.a,)
        times=[]
        for target in targets:
            ticks+=(target-phase)%cycle+1;phase=(target+1)%cycle;times.append(ticks)
        if op.kind==c.META:
            ticks+=4*core+op.a-physical;phase=op.a+1;times.append(ticks)
        rows.append(tuple(times))
    return ticks,tuple(rows)


def measure():
    start=time.perf_counter();g=p.layout();packed=pack3_rom.pack(g.instructions)
    core=g.memory_count+len(packed.rows)+1
    assert packed.decode()==g.instructions
    counts={}
    for row in packed.rows:counts[row.count]=counts.get(row.count,0)+1
    paths=[];gather_margins=[]
    for stage,(first,last) in enumerate(g.stage_ranges[:3]):
        pcs=tuple(range(first,last));ticks,rows=schedule(g,packed,pcs,stage)
        arrival=0
        for pc,times in zip(pcs,rows):
            op=g.instructions[pc]
            if op.kind!=c.SEND:continue
            target=(op.b&~c.PHASE_MARK)+c.GATHER_OFFSETS[stage]
            hops,direction=op.d>>1,op.d&1
            distance=hops*f.Q+(op.a-target if direction==c.LEFT else target-op.a)
            arrival=max(arrival,times[-1]+distance)
        deadline=(c.VOTE_AGES[0] if stage==2 else c.ACTIVE_ENDS[stage])-c.RESET_AGES[stage]
        paths.append(ticks)
        gather_margins.append(deadline-max(ticks,arrival))
    for first,last in g.stage_ranges[3:]:
        paths.append(schedule(g,packed,range(first,last))[0])
    early_pcs=tuple(range(g.stage_ranges[4][0],g.branch_instruction+1))
    early_pcs+=tuple(range(g.signal_entry,len(g.instructions)))
    early_ticks,early_rows=schedule(g,packed,early_pcs)
    last=0
    for pc,times in zip(early_pcs,early_rows):
        op=g.instructions[pc]
        if op.kind==c.SEND:
            last=max(last,times[-1]+(op.a-op.b if op.d&1 else op.b-op.a))
    return dict(passed=True,physical_decoder_implemented=False,
                self_reference_closed=False,full_period_executed=False,
                original_instruction_cells=len(g.instructions),
                packed_physical_instruction_cells=len(packed.rows),
                packed_row_counts=counts,
                memory_cells=g.memory_count,original_core_cells=g.computation_cells,
                projected_core_cells_before_decoder_cost=core,
                projected_Q8192_slack_before_decoder_cost=8192-core-5,
                original_controller_path_ticks=357637146,
                projected_controller_path_ticks=sum(paths)+early_ticks,
                gather_margins=gather_margins,
                early_capture_margin=c.CAPTURE_AGE-c.VOTE_AGES[0]-last,
                stage3_stop_margin=c.ACTIVE_ENDS[2]-c.VOTE_AGES[0]-early_ticks,
                final_evaluation_margin=c.ACTIVE_ENDS[4]-c.RESET_AGES[4]-paths[-1],
                physical_rule_sha256=f.self_description().digest(),
                source_sha256={str(path):hashlib.sha256(path.read_bytes()).hexdigest()
                               for path in (Path(__file__),Path(pack3_rom.__file__),
                                            Path(p.__file__),Path(c.__file__))},
                seconds=time.perf_counter()-start,
                host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();result=measure()
    with args.output.open('x') as stream:stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='source_sha256'},indent=2))


if __name__=='__main__':main()
