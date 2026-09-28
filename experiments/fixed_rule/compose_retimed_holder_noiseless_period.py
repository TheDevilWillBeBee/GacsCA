"""Finite interfaces for the retimed noiseless whole-period induction.

The companion RETIMED_NOISELESS_MACROSTEP report supplies the induction. This
checker is diagnostic only and is never used to replace a physical transition.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_core as c,retimed_holder_projected as r,retimed_holder_program as p,retimed_holder_period_relation as relation
from experiments.fixed_rule import certify_retimed_holder_mail_schedule as schedule
from experiments.fixed_rule import certify_retimed_holder_local_transfer as local
from experiments.fixed_rule.certify_small_holder_rom_dataflow import Terms
from experiments.fixed_rule.small_holder_guarded_bounds import GuardedBounds
from experiments.fixed_rule.audit_small_holder_position_events import sha

SOURCES={'transfer':'retimed_holder_local_transfer_v1.json','rom':'retimed_holder_rom_v1.json',
         'schedule':'retimed_holder_mail_schedule_v1.json','boundary':'retimed_holder_signal_flag_boundaries_v1.json',
         'capture':'retimed_holder_signal_schedule_v1.json','timed':'retimed_holder_timed_dataflow_v1.json',
         'queries':'retimed_holder_meta_query_bounds_v2.json','open':'retimed_holder_open_dataflow_v1.json',
         'entry':'retimed_holder_period_relation_v1.json'}

def load_inputs(root=Path('figs/fixed_rule')):
    loaded={name:json.loads((root/file).read_text()) for name,file in SOURCES.items()}
    for name,doc in loaded.items():
        assert doc['passed'],name
        for key in ('descriptor_sha256','physical_descriptor_sha256'):
            if key in doc:assert doc[key]==f.self_description().digest(),name
        for source,wanted in {**doc['source_sha256'],**doc.get('input_sha256',{})}.items():
            assert Path(source).is_file() and sha(source)==wanted,source
    for name in ('timed','open'):assert loaded[name]['schedule_sha256']==sha(root/SOURCES['schedule'])
    replay=json.loads(json.dumps(schedule.check(schedule.load_inputs())))
    assert replay['phases']==loaded['schedule']['phases'] and replay['trace_sha256']==loaded['schedule']['trace_sha256']
    # Check the transferred premise domains again; full clock identities were
    # replayed when producing the hashed transfer manifest.
    replay=local.validate_premises(local.load_inputs())
    assert all(loaded['transfer'][key]==value for key,value in replay.items())
    expected_rom=hashlib.sha256(p.base_rom().tobytes()).hexdigest()
    assert all(loaded[key]['rom_sha256']==expected_rom for key in ('transfer','rom','schedule'))
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
    assert (f.Q,f.U,f.FIELDS,f.WIDTH,len(r.SCHEMA),r.WIDTH,f.NEIGHBORHOOD)==(32768,2147483648,154,4090,105,2704,tuple(range(-7,8)))
    transfer=loaded['transfer']
    assert transfer['canonical_structural_domain_preserved']
    assert transfer['legal_new_ages']==f.U and transfer['complete_non_Age_outputs']==153
    assert transfer['clock_intervals']==22
    assert transfer['geometry']['core_cells']==len(p.base_rom())
    assert transfer['geometry']['minimum_gap_to_next_colony_core']>=8
    assert transfer['spatial_support']['maximum_head_controller_logical_radius']<=1
    assert transfer['spatial_support']['static_fields_preserved']==49
    assert len(transfer['local_lemmas'])==6
    assert loaded['rom']['all_fixed_ROM_fields_typed']
    assert loaded['rom']['equivalence']['complete_raw_outputs']==154
    assert loaded['entry']['represented_raw_fields']==154 and loaded['entry']['represented_projected_fields']==105
    assert loaded['entry']['nonzero_initial_scratch'] and loaded['entry']['nonzero_retained_Signals']
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
    start=time.perf_counter();result=interfaces(load_inputs());result['layout']=layout();result['typing']=output_types()
    result.update(descriptor_sha256=f.self_description().digest(),rom_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest(),
                  input_sha256={str(Path('figs/fixed_rule')/file):sha(Path('figs/fixed_rule')/file) for file in SOURCES.values()},
                  source_sha256={str(path):sha(path) for path in (Path(__file__),Path(relation.__file__),Path(schedule.__file__),Path(local.__file__),Path('experiments/fixed_rule/certify_small_holder_rom_dataflow.py'),Path('experiments/fixed_rule/small_holder_guarded_bounds.py'))},
                  seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  theorem_interface='For the companion noiseless descriptor-semantics induction, F^U(E(y)) is contained in E(G(y)), G=pi F iota, for the retimed fixed rule and own ROM. Green interface checks alone are not the inductive proof.',
                  limitation='Not a new U-tick physical trace or backend equivalence certificate. No general noise theorem, practical complete depth-two run or robust finite-cap repair follows.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='typing'},indent=2),flush=True)

if __name__=='__main__':main()
