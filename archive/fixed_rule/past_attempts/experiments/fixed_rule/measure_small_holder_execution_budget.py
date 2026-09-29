"""Exact schedule work counts; not a GPU runtime extrapolation."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import resource
import time

from gacsca.fixed_rule import small_holder_rule as f,small_holder_core as c,small_holder_program as p,small_holder_projected as r
from experiments.fixed_rule import certify_small_holder_mail_schedule as schedule
from experiments.fixed_rule.audit_small_holder_position_events import sha


def measure():
    loaded=schedule.load_inputs();checked=schedule.check(loaded);g=p.layout()
    ordinary={(row[0],row[2]):row for row in loaded['ordinary']['rows']}
    metadata={row['pc']:(row['duration'],row['destination']+1) for row in loaded['meta']['paths']}
    routes={(row[0],row[1]):row for row in loaded['dispatch']['rows']}
    rows=[]
    for phase in checked['phases']:
        head=0;travel=body=0;kinds=Counter()
        for pc in range(phase['start'],phase['end']):
            op=g.instructions[pc];kinds[op.kind]+=1
            key=phase['entry'] if pc==phase['start'] else ('META' if g.instructions[pc-1].kind==c.META else 'ordinary',pc-1)
            route=routes[key];assert tuple(route[2:4])==(head,pc);travel+=route[4]
            branch=int(op.kind==c.IF_THIRD and phase['third'])
            duration,head=metadata[pc] if op.kind==c.META else (ordinary[pc,branch][3],ordinary[pc,branch][4])
            body+=duration
        assert 1+travel+body==phase['head_stopped']-phase['origin']
        rows.append(dict(name=phase['name'],instructions=sum(kinds.values()),opcode_occurrences=dict(kinds),
                         dispatch_ticks=travel,body_ticks=body,entry_tick=1,
                         controller_path_ticks=1+travel+body))
    instructions=sum(row['instructions'] for row in rows);path_ticks=sum(row['controller_path_ticks'] for row in rows)
    dispatch=sum(row['dispatch_ticks'] for row in rows)
    assert instructions==checked['instructions_checked']
    core=len(p.base_rom());required=core+5
    min_power_Q=1<<(required-1).bit_length();min_power_U=1<<(path_ticks-1).bit_length()
    return dict(passed=True,phases=rows,instructions_per_colony_period=instructions,
                dispatch_ticks_per_period=dispatch,body_ticks_per_period=sum(row['body_ticks'] for row in rows),
                controller_path_ticks_per_period=path_ticks,outside_controller_paths_ticks=f.U-path_ticks,
                fixed_Q=f.Q,fixed_U=f.U,core_cells=core,tail_cells=5,
                minimum_Q_for_current_core_and_tail=required,minimum_power_of_two_Q=min_power_Q,
                minimum_power_of_two_U_for_current_sequential_controller_paths=min_power_U,
                two_level_single_top_cell=dict(physical_cells=f.Q**2,lower_colonies=f.Q,lower_periods=f.U,
                  physical_ticks=f.U**2,dense_projected_bytes_per_buffer=f.Q**2*r.WIDTH//8,
                  one_MEM_Data_bank_bytes=f.Q*(g.memory_count+5)*8,
                  current_per_instruction_strategy_occurrences=instructions*f.Q*f.U),
                limitation='Exact operation/clock/storage arithmetic for the frozen schedule. Not a measured full-ring GPU time, not a lower bound on every possible accelerator or alternative fixed construction. Outside-controller ticks include live packet flight and flag dynamics, not just idle time.')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();result=measure()
    result.update(descriptor_sha256=f.self_description().digest(),rom_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest(),
                  source_sha256={str(path):sha(path) for path in (Path(__file__),Path(schedule.__file__),Path(p.__file__))},
                  seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
