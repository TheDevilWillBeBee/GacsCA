"""Bounded metadata-only cost study; hypothetical sizes are not new rules."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import resource
import time
from gacsca.fixed_rule import holder_rule as f, holder_program as p, holder_projected as projected
from gacsca.fixed_rule import parallel_vote_probe as probe


def study():
    start_time=time.monotonic();g=p.layout();d=f.self_description()
    start,end=g.stage_ranges[4];ticks,rows=g.schedule(start,end)
    cuts=(start,g.description_instruction,g.description_instruction+len(d.operations),end)
    groups=[];previous=1
    for name,a,b in zip(('serial_temporal_vote','complete_rule_descriptor','output_and_metadata'),cuts,cuts[1:]):
        last=rows[b-start-1][-1]
        groups.append(dict(name=name,instructions=b-a,ticks=last-previous,
                           fraction_of_evaluation=(last-previous)/ticks,
                           scheduled_accesses=sum(len(row) for row in rows[a-start:b-start]),
                           opcode_counts=dict(Counter(op.kind for op in g.instructions[a:b]))))
        previous=last
    assert 1+sum(row['ticks'] for row in groups)==ticks==g.timing_certificate()['evaluation_ticks']
    # Full projected physical state includes every backup, unlike the coherent quotient.
    state_bytes=((projected.WIDTH+63)//64)*8
    sizes=[]
    for q in (8192,65536,1<<20,f.Q):
        u=128*q
        sizes.append(dict(Q=q,illustrative_U_128Q=u,
                          two_level_cells_per_top_cell=q*q,
                          double_buffer_full_state_bytes_per_top_cell=2*state_bytes*q*q,
                          two_level_ticks_per_top_step_at_illustrative_U=u*u,
                          fits_current_core_storage=q>=g.computation_cells,
                          has_audited_one_link_holder_fixture_at_this_Q=(q==f.Q),
                          verified_two_level_dynamics=False))
    return dict(kind='cost_study_not_replacement_rule',baseline_rule_identity=f.identity(),
                complete_core_cells=g.computation_cells,memory_cells=g.memory_count,
                rom_instruction_cells=len(g.instructions),evaluation_ticks=ticks,groups=groups,
                parallel_vote_primitive=dict(support=probe.SUPPORT,outputs=5,
                    descriptor_operations=len(probe.description().operations),
                    descriptor_sha256=probe.description().digest(),
                    integrated_into_rule=False,complete_self_reference_established=False),
                hypothetical_sizes=sizes,physical_bytes_per_cell_64bit_packed=state_bytes,
                dense_estimates_exclude_neighbor_guard_cells=True,
                elapsed_seconds=time.monotonic()-start_time,
                host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)


def execute(path):
    path=Path(path)
    if path.exists():raise FileExistsError('preserve evidence')
    result=study();root=Path(__file__).resolve().parents[2]
    sources=[Path(__file__),root/'gacsca/fixed_rule/parallel_vote_probe.py',
             root/'tests/fixed_rule/test_parallel_vote_probe.py',
             root/'gacsca/fixed_rule/holder_program.py',root/'gacsca/fixed_rule/holder_rule.py',
             root/'gacsca/fixed_rule/holder_description.py',root/'gacsca/fixed_rule/holder_core.py']
    result['source_sha256']={str(x.relative_to(root)):hashlib.sha256(x.read_bytes()).hexdigest() for x in sources}
    path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('baseline_rule_identity','source_sha256')},indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True)
    execute(parser.parse_args().output)
