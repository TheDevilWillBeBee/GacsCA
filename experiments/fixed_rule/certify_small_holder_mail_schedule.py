"""Join fixed-ROM instruction timing and packet noninterference obligations.

This is a conditional schedule certificate, never an execution backend. The
factorization/flight leaves and initial canonical empty-mail invariant remain
explicit premises; reset/Signal/flag closure is not inferred here.
"""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import resource
import time

from gacsca.fixed_rule import small_holder_rule as f, small_holder_core as c, small_holder_program as p
from gacsca.fixed_rule.wordcode import LIT
from experiments.fixed_rule import certify_small_holder_dispatch_paths as dispatch
from experiments.fixed_rule import certify_small_holder_mail_factorization as factor
from experiments.fixed_rule import prove_small_holder_packet_flight as flight
from experiments.fixed_rule.audit_small_holder_position_events import sha

SOURCES={
 'factor':'small_holder_mail_factorization_v1.json',
 'factor_audit':'small_holder_mail_factorization_audit_v1.json',
 'flight':'small_holder_packet_flight_proof_v1.json',
 'dispatch':'small_holder_dispatch_paths_v1.json',
 'dispatch_audit':'small_holder_dispatch_paths_pilot_audit_v1.json',
 'ordinary':'small_holder_instruction_paths_v1.json',
 'meta':'small_holder_meta_paths_v2.json',
}


def load_inputs():
    dispatch.inputs()
    loaded={key:json.loads((Path('figs/fixed_rule')/name).read_text()) for key,name in SOURCES.items()}
    for key,doc in loaded.items():
        assert doc['passed'],key
        if 'descriptor_sha256' in doc:assert doc['descriptor_sha256']==f.self_description().digest(),key
        hashes=doc.get('source_sha256')
        if isinstance(hashes,dict):
            for path,wanted in hashes.items():assert sha(path)==wanted,path
    assert loaded['dispatch']['source_sha256']==sha(dispatch.__file__)
    for key in ('factor','dispatch'):
        assert loaded[key+'_audit']['certificate_sha256']==sha(Path('figs/fixed_rule')/SOURCES[key])
    assert not loaded['factor']['pilot']
    assert {(row['phase'],tuple(row['interval'])) for row in loaded['factor']['cases']} == {(phase,interval) for phase in (None,*range(8)) for interval in factor.clock.regular_intervals()}
    replay=[flight.prove_case(hops) for hops in range(8)]
    assert replay==loaded['flight']['cases'],'packet induction replay changed'
    return loaded


def verify_geometry(rom=None):
    rom=p.base_rom() if rom is None else rom
    assert rom.shape==p.base_rom().shape
    memory=[]
    for address in range(f.Q):
        record=rom[address] if address<len(rom) else tuple(c.fallback(address,k) for k in range(7))
        if int(record[0])==c.MEM:
            assert int(record[1])==address,('MEM index is not its canonical Address',address)
            memory.append(address)
    expected=set(range(p.layout().memory_count))|set(range(f.Q-5,f.Q))
    assert set(memory)==expected,'actual MEM geometry changed'
    return expected


def verify_packets(packets, accesses):
    lines=defaultdict(list);targets=set()
    for row in packets:
        pc,birth,source,target,tag,distance,arrival=row
        hops,direction=tag>>1,tag&1
        assert 0<=tag<=15 and distance==hops*f.Q+(source-target if direction else target-source)>0
        assert arrival==birth+distance
        assert target not in targets,('duplicate phase destination',target)
        targets.add(target)
        # Conservative: exclude even simultaneous reads, though these see old Data.
        assert all(tick<arrival for tick in accesses.get(target,())),('controller access at/after delivery',pc,target,arrival)
        line=(source+(birth if direction else -birth))%f.Q
        lines[direction,line].append((birth,arrival,pc))
    for key, intervals in lines.items():
        intervals.sort()
        assert all(a[1]<=b[0] for a,b in zip(intervals,intervals[1:])),('same-track overwrite',key)
    return dict(packets=len(packets),unique_destinations=len(targets),space_time_lines=len(lines),
                last_arrival=max((row[-1] for row in packets),default=0),
                same_track_collisions_excluded=True,all_destination_accesses_before_delivery=True)


def phases():
    g=p.layout()
    result=[dict(name=f'gather_{stage}',start=start,end=end,origin=c.RESET_AGES[stage],
                 entry=('reset_entry',stage),third=False,deadline=(c.VOTE_AGES[0] if stage==2 else c.ACTIVE_ENDS[stage]))
            for stage,(start,end) in enumerate(g.stage_ranges[:3])]
    result.append(dict(name='precommit_halt',start=g.stage_ranges[3][0],end=g.stage_ranges[3][1],origin=c.RESET_AGES[3],entry=('reset_entry',3),third=False,deadline=c.ACTIVE_ENDS[3]))
    result.append(dict(name='third_evaluation',start=g.delivery_range[0],end=g.delivery_range[1],origin=c.VOTE_AGES[0],entry=('vote_entry',0),third=True,deadline=c.CAPTURE_AGE-1))
    result.append(dict(name='final_evaluation',start=g.stage_ranges[4][0],end=g.stage_ranges[4][1],origin=c.RESET_AGES[4],entry=('reset_entry',4),third=False,deadline=c.ACTIVE_ENDS[4]))
    return tuple(result)


def check(loaded,rom=None):
    g=p.layout();memory=verify_geometry(rom)
    ordinary={(row[0],row[2]):row for row in loaded['ordinary']['rows']}
    metadata={}
    for row in loaded['meta']['paths']:
        value=(row['duration'],row['destination']+1)
        assert row['pc'] not in metadata or metadata[row['pc']]==value
        metadata[row['pc']]=value
    routes={(row[0],row[1]):row for row in loaded['dispatch']['rows']}
    result=[];seen_send=set();trace_hash=hashlib.sha256();instructions=0
    for phase in phases():
        # Time is absolute physical Age of the current state. First state is
        # immediately after the reset/vote tick; producing it is a separate premise.
        age=phase['origin']+1;head=0;accesses=defaultdict(list);packets=[];rows=[]
        scheduled,independent=g.schedule(phase['start'],phase['end'])
        for pc in range(phase['start'],phase['end']):
            op=g.instructions[pc]
            key=phase['entry'] if pc==phase['start'] else ('META' if g.instructions[pc-1].kind==c.META else 'ordinary',pc-1)
            route=routes[key];assert tuple(route[2:4])==(head,pc)
            dispatch_ticks=route[4];assert dispatch_ticks==g.memory_count+pc-head>=0
            fetch_age=age+dispatch_ticks
            branch=int(op.kind==c.IF_THIRD and phase['third'])
            duration,new_head=metadata[pc] if op.kind==c.META else (ordinary[pc,branch][3],ordinary[pc,branch][4])
            end_age=fetch_age+duration
            assert any(lo<=age<=end_age-1<=hi for lo,hi in factor.clock.regular_intervals()),('path crosses an excluded clock',phase['name'],pc,age,end_age)
            times=tuple(phase['origin']+tick for tick in independent[pc-phase['start']])
            assert times[-1]==end_age,('independent schedule differs',phase['name'],pc)
            if op.kind in c.ALU_KINDS:targets=(op.a,op.b,op.d)
            elif op.kind==LIT:targets=(op.d,)
            elif op.kind in (c.LOAD,c.SEND):targets=(op.a,)
            elif op.kind==c.META:targets=(op.a,)
            else:targets=()
            access_times=(end_age,) if op.kind==c.META else times[1:]
            assert len(targets)==len(access_times)
            for target,tick in zip(targets,access_times):
                assert target in memory
                accesses[target].append(tick)
            if op.kind==c.SEND:
                assert op.b in memory and 0<=op.d<=15
                hops,direction=op.d>>1,op.d&1
                distance=hops*f.Q+(op.a-op.b if direction else op.b-op.a)
                arrival=end_age+distance
                assert distance>0
                assert any(lo<=end_age<=arrival-1<=hi for lo,hi in factor.clock.regular_intervals()),('packet crosses an excluded clock',phase['name'],pc)
                packets.append((pc,end_age,op.a,op.b,op.d,distance,arrival));seen_send.add(pc)
            rows.append((pc,age,dispatch_ticks,fetch_age,duration,end_age,new_head))
            trace_hash.update(json.dumps((phase['name'],rows[-1]),separators=(',',':')).encode())
            age,head=end_age,new_head;instructions+=1
            if head<0:assert pc==phase['end']-1,'early halt'
        assert head<0 and age==phase['origin']+scheduled
        packet_result=verify_packets(packets,accesses)
        assert max(age,packet_result['last_arrival'])<phase['deadline'],('phase exceeds deadline',phase['name'])
        result.append(dict(phase,head_stopped=age,packet_summary=packet_result,
                           margin=phase['deadline']-max(age,packet_result['last_arrival']),
                           instruction_count=len(rows),accessed_addresses=len(accesses),packets=packets,
                           first_instruction=rows[0],last_instruction=rows[-1]))
    assert seen_send=={pc for pc,op in enumerate(g.instructions) if op.kind==c.SEND}
    return dict(passed=True,phases=result,instructions_checked=instructions,actual_SEND_sites_checked=len(seen_send),
                MEM_addresses=len(memory),trace_sha256=trace_hash.hexdigest(),
                conditional_join='Given canonical coherent zero-flag/Signal/Wf entry, empty initial mail, stated one-head geometry and regular-clock invariance, the checked timing, unique MEM indices, receive induction and collision/access guards support the actual fixed-ROM packet paths. Reset/Signal/flag closure and global induction are not established by this catalog.')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    started=time.perf_counter();loaded=load_inputs();result=check(loaded)
    paths=[Path(__file__),Path(factor.__file__),Path(flight.__file__),Path(p.__file__)]
    result.update(descriptor_sha256=f.self_description().digest(),rom_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest(),
                  source_sha256={str(path):sha(path) for path in paths},input_sha256={key:sha(Path('figs/fixed_rule')/name) for key,name in SOURCES.items()},
                  seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  limitation='Static conditional composition check, not physical execution or a closed whole-period/nested/noisy simulation proof. Signal/flag/reset invariants and formal head/mail induction remain separate.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='phases'},indent=2),flush=True)


if __name__=='__main__':main()
