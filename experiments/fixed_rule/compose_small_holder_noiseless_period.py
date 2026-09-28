"""Checked interfaces for the noiseless physical-period induction.

The accompanying proof explains each inductive step; this checker verifies its
finite premises, certificate coverage, timing interfaces, typing and ROM layout.
It is not a new physical executor and does not stand in for that proof text.
"""
import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import resource
import time

from gacsca.fixed_rule import small_holder_rule as f, small_holder_core as c
from gacsca.fixed_rule import small_holder_projected as r, small_holder_program as p, small_holder_period_relation as relation
from experiments.fixed_rule import certify_small_holder_mail_schedule as schedule
from experiments.fixed_rule.certify_small_holder_rom_dataflow import Terms
from experiments.fixed_rule.small_holder_guarded_bounds import GuardedBounds
from experiments.fixed_rule.audit_small_holder_position_events import sha

SOURCES={
 'schedule':'small_holder_mail_schedule_v1.json',
 'context':'small_holder_procedure_context_v1.json',
 'barriers':'small_holder_quiet_barriers_v2.json',
 'structure':'small_holder_structural_invariant_v1.json',
 'mail':'small_holder_raw_mail_factorization_v1.json',
 'mail_support':'small_holder_mail_factorization_v1.json',
 'boundary':'small_holder_signal_flag_boundaries_v1.json',
 'capture':'small_holder_signal_schedule_v2.json',
 'timed':'small_holder_timed_dataflow_v1.json',
 'queries':'small_holder_meta_query_bounds_v1.json',
 'open':'small_holder_open_dataflow_v1.json',
 'entry':'small_holder_period_relation_v1.json',
}


def load_inputs(root=Path('figs/fixed_rule')):
    loaded={name:json.loads((root/file).read_text()) for name,file in SOURCES.items()}
    for name,doc in loaded.items():
        assert doc['passed'],name
        if 'descriptor_sha256' in doc:assert doc['descriptor_sha256']==f.self_description().digest(),name
        for source,wanted in doc['source_sha256'].items():assert sha(source)==wanted,source
        for source,wanted in doc.get('input_sha256',{}).items():
            if Path(source).is_file():assert sha(source)==wanted,source
        for source,wanted in doc.get('certificate_sha256',{}).items() if isinstance(doc.get('certificate_sha256'),dict) else ():
            assert sha(source)==wanted,source
    for name in ('timed','open'):assert loaded[name]['schedule_sha256']==sha(root/SOURCES['schedule'])
    replay=json.loads(json.dumps(schedule.check(schedule.load_inputs())))
    assert replay['phases']==loaded['schedule']['phases'] and replay['trace_sha256']==loaded['schedule']['trace_sha256']
    return loaded


def output_types(description=None):
    desc=f.self_description() if description is None else description;t=Terms(p.base_rom())
    inputs=tuple(t.intern(('input',col,name,width)) for col in range(15) for name,width in f.SCHEMA)
    outputs=t.expression(desc,inputs);known=GuardedBounds(t);masks={}
    for (name,width),term in zip(f.SCHEMA,outputs):
        ones,_=known.at(term)
        assert ones<1<<width,('output exceeds fixed alphabet',name,width,ones)
        masks[name]=ones
    return dict(passed=True,raw_outputs_checked=len(masks),raw_width=f.WIDTH,projected_width=r.WIDTH,
                all_output_possible_one_masks=masks,guarded_decrements=known.refinements)


def layout():
    result=relation.layout_obligations();g=p.layout();info=set(g.info);hold=set(g.hold)
    assert not info&hold and len(info)==len(hold)==f.FIELDS
    histories={g.history(stage,neighbor,k) for stage in range(3) for neighbor in range(-7,8) for k in range(f.FIELDS)}
    for at in histories:
        row=r.record(at);assert row['kind']==c.MEM and not row['first']
        assert not row['a']&((1<<3)|(1<<4)),('late reset erases a vote operand',at)
    for at in g.votes:
        assert {at-1,at+1,at+2}<=histories
        assert 0<=at-1<at+2<f.Q
    for address in range(f.Q):
        row=r.record(address)
        if row['kind']==c.MEM and not row['first'] and row['a']&c.VOTE:assert address in g.votes
        if row['kind']==c.MEM and not row['first'] and row['a']&c.INFO:assert address in info
    # The scalar/descriptor Data operations write only MEM or a first record;
    # all fixed-ROM first records are MEM. Non-MEM initialized Data stays zero.
    assert r.record(0)['kind']==c.MEM and r.record(0)['first']==1
    return dict(result,histories_survive_both_late_resets=True,history_words=len(histories),
                all_vote_operands_inside_colony=True,Info_Hold_disjoint=True,
                vote_and_Info_marks_have_exact_layout=True)


def interfaces(loaded):
    assert (f.Q,f.U,f.FIELDS,f.WIDTH,len(r.SCHEMA),r.WIDTH,f.NEIGHBORHOOD)==(32768,4294967296,154,4090,105,2704,tuple(range(-7,8)))
    assert loaded['context']['complete_raw_words']==154 and loaded['context']['all_clock_ages']==f.U
    assert loaded['barriers']['procedure_word_identities']==90 and loaded['barriers']['all_clock_ages']==f.U
    assert loaded['barriers']['simultaneous_reset_vote_age']==c.RESET_AGES[4]==c.VOTE_AGES[1]
    assert loaded['mail_support']['support']['controller_outputs_independent_of_all_old_mail']==45
    assert len(loaded['mail']['cases'])==9 and {row['phase'] for row in loaded['mail']['cases']}=={None,*range(8)}
    assert loaded['mail']['all_clock_ages']==f.U
    assert loaded['structure']['minimum_gap']>=8
    assert loaded['boundary']['formulas']['all_clock_ages']==f.U
    assert loaded['boundary']['clearing']['total_clearing_ticks']==f.Q
    assert loaded['queries']['certified_query_bits']==15 and loaded['queries']['maximum_possible_query_mask']<f.Q
    assert loaded['timed']['commit_matches_normalized_complete_rule'] and loaded['timed']['next_reset_clears_all_nonInfo_Data']
    assert loaded['open']['source_integer_offsets']==list(range(-7,8)) and not loaded['open']['periodic_destination_used']
    assert loaded['open']['center_commit_equals_normalized_full_descriptor'] and loaded['open']['all_late_packets_zero_hop']
    assert loaded['open']['source_access_disjointness_checks']==45
    phases={row['name']:row for row in loaded['schedule']['phases']}
    order=('gather_0','gather_1','gather_2','third_evaluation','precommit_halt','final_evaluation')
    origins=(0,c.RESET_AGES[1],c.RESET_AGES[2],c.VOTE_AGES[0],c.RESET_AGES[3],c.RESET_AGES[4])
    boundaries=(*origins[1:],f.U-1);rows=[]
    timed={row['name']:row for row in loaded['timed']['phases']}
    for name,origin,next_barrier in zip(order,origins,boundaries):
        row=phases[name];assert row['origin']==origin
        assert row['head_stopped']==timed[name]['head_stopped'] and timed[name]['no_pending_packets']
        last=max(row['head_stopped'],row['packet_summary']['last_arrival'])
        assert last<row['deadline']<=next_barrier
        # Between termination and the next barrier, no unaccounted reset/vote
        # can create another head or change the Data interpretation.
        assert not any(last<=tick<next_barrier for tick in (*c.RESET_AGES,*c.VOTE_AGES,f.U-1))
        rows.append(dict(phase=name,entry_old_age=origin,quiet_from_age=last,
                         next_barrier_old_age=next_barrier,quiet_margin=next_barrier-last))
    assert loaded['capture']['latest_packet_delivery_age']<c.CAPTURE_AGE-1<c.WF_START
    assert loaded['capture']['no_SEND_during_or_after_forcing']
    assert c.WF_END+f.Q<c.RESET_AGES[4]<f.U-1
    assert all(not phases[name]['packets'] for name in ('precommit_halt','final_evaluation'))
    # The modulo-Q collision check is independent of ring length. Equal-PC
    # emissions from distinct colonies stay Q-spaced; different PCs are covered
    # by its line/lifetime exclusion. Hops count colony crossings, not ring laps.
    assert all(row['packet_summary']['same_track_collisions_excluded'] for row in phases.values())
    return dict(passed=True,phase_interfaces=rows,final_quiet_before_commit=True,
                flags_zero_before_final_evaluation=True,mail_absent_during_flag_forcing=True,
                ring_aliasing_basis='Open independent-offset identity; conservative modulo-Q collision exclusion; equal-PC packets from distinct colonies remain equally spaced; finite hop counters count every boundary crossing.',
                permitted_upper_ring_sizes='Every positive integer; infinite lattice by the same local argument.')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();loaded=load_inputs();result=interfaces(loaded);result['layout']=layout();result['typing']=output_types()
    result.update(descriptor_sha256=f.self_description().digest(),rom_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest(),
                  input_sha256={name:sha(Path('figs/fixed_rule')/file) for name,file in SOURCES.items()},
                  source_sha256={str(path):sha(path) for path in (Path(__file__),Path(relation.__file__),Path(schedule.__file__),Path('experiments/fixed_rule/small_holder_guarded_bounds.py'),Path('experiments/fixed_rule/certify_small_holder_meta_query_bounds.py'))},
                  seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  theorem_interface='For the documented noiseless induction, F^U(E(y)) is contained in E(G(y)), G=pi F iota. The companion proof must supply the induction using the checked local refinements; a green interface manifest alone is not that proof.',
                  limitation='Noisy trajectories, practical full depth-two execution, robust finite termination and original-source amplification claims are not established.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='typing'},indent=2),flush=True)


if __name__=='__main__':main()
