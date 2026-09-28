"""Read-only physical schedule accounting; no new candidate or speedup claim."""
from collections import Counter
import json
from pathlib import Path
from gacsca.fixed_rule import compact16_holder_program as p, compact16_holder_core as c
from gacsca.fixed_rule import compact16_holder_rule as f
from gacsca.fixed_rule.wordcode import LIT
from experiments.fixed_rule.run_compact16_holder_streamed_depth2 import sha


def main():
    output=Path('figs/fixed_rule/compact16_holder_cost_profile_v1.json')
    if output.exists():raise FileExistsError(output)
    g=p.layout();names={getattr(c,k):k for k in ('NAND','ADD','SHR','EQ','LT','LIT','SEND','LOAD','META','HALT','IF_THIRD')}
    phases=[]
    for label,(start,end) in zip(('gather1','gather2','gather3','unused_halt','evaluation'),g.stage_ranges):
        if label=='unused_halt':continue
        ticks,rows=g.schedule(start,end);categories=Counter();operations=Counter();previous=1
        for op,times in zip(g.instructions[start:end],rows):
            categories[names[op.kind]]+=times[-1]-previous;operations[names[op.kind]]+=1;previous=times[-1]
        assert sum(categories.values())+1==ticks
        phases.append(dict(phase=label,ticks=ticks,instructions=end-start,ticks_by_opcode=dict(categories),opcode_counts=dict(operations)))
    third,_=g.schedule(*g.delivery_range)
    controller_total=sum(row['ticks'] for row in phases[:3])+third+phases[-1]['ticks']
    operation_counts=Counter(names[op] for op,_,_ in p.compiled_description().operations)
    evaluation=phases[-1]
    # A necessary space target with the current MEM layout, not a candidate:
    # leave at least today's 25-cell gap and five tail cells.
    instructions_at_Q8192=8192-g.memory_count-1-25-5
    result=dict(descriptor_sha256=f.self_description().digest(),Q=f.Q,U=f.U,
                physical_core=g.computation_cells,memory_cells=g.memory_count,instructions=len(g.instructions),
                instruction_fraction_of_core=len(g.instructions)/g.computation_cells,
                descriptor_operations=len(p.compiled_description().operations),descriptor_opcode_counts=dict(operation_counts),
                history_cells=3*len(g.gathered_inputs),vote_cells=len(g.votes),raw_info_and_hold_cells=len(g.info)+len(g.hold),
                static_input_cells=len(g.regenerated_inputs),scratch_capacity=p.RESULT_CAPACITY,
                phases=phases,evaluation_plus_signal_delivery_ticks=third,controller_path_ticks_per_period=controller_total,
                evaluation_and_signal_delivery_fraction=(third+evaluation['ticks'])/controller_total,
                maximum_possible_clock_savings_if_only_slack_removed=1-controller_total/f.U,
                minimum_controller_path_reduction_to_fit_U_2pow29=1-(1<<29)/controller_total,
                Q8192_instruction_budget_with_current_memory_and_gap=instructions_at_Q8192,
                Q8192_required_instruction_removal=len(g.instructions)-instructions_at_Q8192,
                timing_certificate=g.timing_certificate(),
                source_sha256={str(Path(__file__)):sha(__file__),str(Path(p.__file__)):sha(p.__file__)},
                scope='Exact existing deterministic head-path counts; slack figures are optimistic necessary bounds excluding additional delivery/flag/barrier constraints. No optimized rule has been implemented by this profile.')
    with output.open('x') as stream:stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
