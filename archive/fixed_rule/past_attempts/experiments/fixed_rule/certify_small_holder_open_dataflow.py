"""Open-lattice central-colony Data identity, without periodic input aliasing.

Only the fifteen independent source columns -7..7 are needed. During gathers,
their omitted incoming mail targets are never accessed; after gathers every
SEND has zero colony hops. This is a symbolic diagnostic, not an executor.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time

from gacsca.fixed_rule import small_holder_rule as f, small_holder_core as c, small_holder_program as p
from experiments.fixed_rule import certify_small_holder_rom_dataflow as batch
from experiments.fixed_rule import certify_small_holder_mail_schedule as schedule
from experiments.fixed_rule.audit_small_holder_position_events import sha


def destination(source,direction,hops):return source+(-hops if direction else hops)


def certify(schedule_doc):
    ref=batch.Checker(p.base_rom());g=ref.g;center=7;phases={row['name']:row for row in schedule_doc['phases']}
    incoming=omitted=reads_disjoint=0;rows=[]
    for stage in range(3):
        ref.reset(stage);phase=phases[f'gather_{stage}'];targets={row[3] for row in phase['packets']}
        runs=[ref.execute(col,g.entries[stage]) for col in range(ref.n)]
        for col,run in enumerate(runs):
            assert not targets.intersection(run['accesses']),('omitted delivery can affect source program',stage,col)
            assert tuple(ref.memory[col][at] for at in g.info)==ref.normal[col]
            reads_disjoint+=1
            for arrival,wrapped_dest,target,value,direction,birth,source,address,hops in run['messages']:
                assert source==col and 1<=hops<=7
                # Use integer source labels. Never use the periodic wrapped_dest.
                dest=destination(col-center,direction,hops)
                if dest==0:
                    assert arrival<phase['deadline']-phase['origin']
                    ref.memory[center][target]=value;incoming+=1
                else:omitted+=1
        for prior in range(stage+1):
            for offset in range(-7,8):
                got=tuple(ref.memory[center][g.history(prior,offset,k)] for k in range(f.FIELDS))
                assert got==ref.normal[center+offset],('open history mismatch',stage,prior,offset)
        rows.append(dict(stage=stage,all_fifteen_source_Infos_normalized=True,
                         no_source_accesses_any_foreign_delivery_target=True,
                         central_histories_match_independent_integer_offsets=True))
    def vote():
        bank=ref.memory[center]
        for at in g.votes:
            assert 0<=at-1 and at+2<f.Q,'vote crosses a colony edge'
            a,b,d=(bank[at+j] for j in (-1,1,2));assert a==b==d;bank[at]=a
    vote()
    raw=ref.t.expression(f.self_description(),tuple(word for col in range(15) for word in ref.normal[col]))
    expected=tuple(ref.t.normalize(raw))
    third=ref.execute(center,g.entries[4],third=True)
    local_deliveries=0
    for arrival,wrapped_dest,target,value,direction,birth,source,address,hops in third['messages']:
        assert hops==0 and destination(0,direction,hops)==0
        assert arrival<phases['third_evaluation']['deadline']-phases['third_evaluation']['origin']
        ref.memory[center][target]=value;local_deliveries+=1
    bank=ref.memory[center]
    assert tuple(bank[at] for at in g.hold)==expected
    for at in range(1,6):assert bank[at]==expected[f.COL['f2']]
    for at in range(f.Q-5,f.Q):assert bank[at]==expected[f.COL['f1']]
    ref.reset(3);idle=ref.execute(center,g.entries[3]);assert not idle['messages'] and not idle['writes']
    ref.reset(4);vote();last=ref.execute(center,g.entries[4]);assert not last['messages']
    assert tuple(bank[at] for at in g.hold)==expected
    for at in g.info:
        assert at+1<f.Q,'commit crosses a colony edge'
        bank[at]=bank[at+1]
    assert tuple(bank[at] for at in g.info)==expected
    # Descriptor evaluation reads exactly the independent -7..7 normalized inputs.
    # After gathering no computation read can import another colony's evolving
    # Data: the only late packets were the ten zero-hop local deliveries.
    for phase in schedule_doc['phases']:
        if not phase['name'].startswith('gather'):
            assert all(row[4]>>1==0 for row in phase['packets'])
    return dict(passed=True,source_integer_offsets=list(range(-7,8)),periodic_destination_used=False,
                gather_rows=rows,source_access_disjointness_checks=reads_disjoint,
                central_foreign_deliveries=incoming,unobserved_deliveries_omitted=omitted,
                local_signal_deliveries=local_deliveries,complete_raw_output_words=f.FIELDS,
                center_commit_equals_normalized_full_descriptor=True,
                all_late_packets_zero_hop=True,all_votes_and_commits_inside_colony=True,
                instructions_checked=ref.instructions,symbolic_terms=len(ref.t.nodes),
                ring_extension='Translate the central integer label and substitute source input at offset j by upper cell (k+j) mod N, for every N>=1. Coincident inputs are permitted substitutions of an all-input identity. Packet geometry/collision freedom is checked separately modulo Q.',
                limitation='Open symbolic Data-flow identity. Requires the checked timed-read equivalence and physical event refinement to conclude literal physical evolution; not a full macrostep or noise theorem by itself.')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--schedule',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();doc=json.loads(Path(args.schedule).read_text());assert doc['passed']
    for source,wanted in doc['source_sha256'].items():assert sha(source)==wanted,source
    replay=json.loads(json.dumps(schedule.check(schedule.load_inputs())))
    assert replay['phases']==doc['phases'] and replay['trace_sha256']==doc['trace_sha256']
    result=certify(doc)
    result.update(descriptor_sha256=f.self_description().digest(),schedule_sha256=sha(args.schedule),
                  source_sha256={str(path):sha(path) for path in (Path(__file__),Path(batch.__file__),Path(schedule.__file__))},
                  seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
