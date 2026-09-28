"""Successive physical periods from Info-only initialization, mixed-right Signal scope.

Every boundary calls complete F at every physical site. Controller events use F;
packets retain actual emitted payloads. Upper stepping is diagnostic comparison
only. Physical right Signals and their flag profiles are retained; nonzero left Signals reject.
"""
import argparse
import hashlib
import json
from pathlib import Path
import random
import resource
import time
import numpy as np
from gacsca.fixed_rule import retimed_holder_cpu_boundary as boundary,retimed_holder_flag_profile as profile
from gacsca.fixed_rule import retimed_holder_cpu_profile as backend,retimed_holder_cpu_gather as gather,retimed_holder_cpu_events as events
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_core as c,retimed_holder_program as p
from gacsca.fixed_rule import retimed_holder_projected as r,retimed_holder_initial as initial,retimed_holder_period_relation as relation,retimed_holder_native as native
from experiments.fixed_rule.audit_small_holder_position_events import sha


def parents(n):
    rng=random.Random(2026092671);values=[rng.getrandbits(64) for _ in range(n)]
    def logical(pos):
        at=pos%n;record=dict(r.record(at),address=at,age=c.RESET_AGES[4]+100,data=values[at])
        if at==n//2:record.update(head=1,phase=c.READ_B,pc=23,rb=at,rd=(at+1)%n,value=0x123456789abcdef0,alu=c.NAND)
        return c.Cell(**record)
    return tuple(initial.coherent_cell(logical,col) for col in range(n))


def run(n,periods,snapshot_path):
    if not 1<=n<=15 or not 1<=periods<=3:raise ValueError('bounded CPU reference run required')
    upper=parents(n);initial_upper=np.array([r.encode_cell(cell) for cell in upper],dtype=np.uint64)
    g=p.layout();timing=g.timing_certificate();data=np.zeros((n,f.Q),dtype=np.uint64)
    for col,cell in enumerate(upper):data[col,list(g.info)]=f.encode_cell(r.lift(cell))
    world=backend.World(data,np.zeros((n,len(events.CONTROL)),dtype=np.uint64),np.zeros(n,dtype=np.uint64),age=0)
    records=[];saved=[];saved_right=[];totals={};started=time.perf_counter()
    def account(row):
        for name,value in row.items():totals[name]=totals.get(name,0)+value
    def quiet(to_age):account(world.quiet_advance(to_age-world.age))
    def boundary():account(world.step())
    def compute(to_age):account(world.advance(to_age-world.age))
    def empty():assert not np.any(world.heads) and not len(world.packets),'nonquiet physical phase boundary'
    for epoch in range(periods):
        before=upper;expected=r.step_ring(before);raw=tuple(f.encode_cell(r.lift(cell)) for cell in before)
        phases=[];period_start=time.perf_counter();assert world.age==0
        for stage in range(3):
            quiet(c.RESET_AGES[stage]);boundary()
            stop=c.RESET_AGES[stage]+max(timing['gathers'][stage]['head_stopped'],timing['gathers'][stage]['last_arrival'])
            compute(stop);empty()
            for col in range(n):
                for prior in range(stage+1):
                    for offset in range(-7,8):
                        actual=tuple(int(world.data[col,g.history(prior,offset,k)]) for k in range(f.FIELDS))
                        assert actual==raw[(col+offset)%n],('executed history mismatch',epoch,stage,col,prior,offset)
            phases.append(dict(name='gather_'+str(stage),age=world.age,actual_histories_checked=n*(stage+1)*15*f.FIELDS))
            print(json.dumps(dict(period=epoch+1,phase=phases[-1]['name'],age=world.age,seconds=time.perf_counter()-started)),flush=True)
        quiet(c.VOTE_AGES[0]);boundary()
        stop=c.VOTE_AGES[0]+max(timing['stage3_head_stopped'],timing['stage3_last_delivery'])
        compute(stop);empty()
        for col,cell in enumerate(expected):assert tuple(map(int,world.data[col,list(g.hold)]))==f.encode_cell(r.lift(cell))
        phases.append(dict(name='first_evaluation',age=world.age))
        quiet(c.CAPTURE_AGE-1);boundary()
        quiet(c.RESET_AGES[3]);boundary()
        compute(c.RESET_AGES[3]+g.schedule(*g.stage_ranges[3])[0]);empty()
        quiet(c.RESET_AGES[4]);boundary()
        compute(c.RESET_AGES[4]+g.schedule(*g.stage_ranges[4])[0]);empty()
        phases.append(dict(name='final_evaluation',age=world.age))
        quiet(f.U-1);boundary();empty()
        upper=tuple(relation.decode_colony(world.cell,n,col) for col in range(n))
        assert upper==expected,'committed decoded upper transition mismatch'
        check=relation.validate_ring(world.cell,n,parent=lambda col:expected[col])
        changed=sum(a!=b for old,new in zip(before,upper) for a,b in zip(r.encode_cell(old),r.encode_cell(new)))
        assert world.time==(epoch+1)*f.U and world.age==0
        record=dict(period=epoch+1,passed=True,phases=phases,full_entry_relation=check,changed_projected_words=changed,
                    decoded_sha256=hashlib.sha256(np.array([r.encode_cell(cell) for cell in upper],dtype=np.uint64).tobytes()).hexdigest(),
                    seconds=time.perf_counter()-period_start)
        records.append(record);saved.append(world.data.copy());saved_right.append(world.right.copy())
        print(json.dumps(dict(period=epoch+1,complete=True,seconds=time.perf_counter()-started,changed_projected_words=changed)),flush=True)
    np.savez_compressed(snapshot_path,initial_upper=initial_upper,boundary_data=np.stack(saved),boundary_age=np.zeros(periods,dtype=np.uint64),
                        boundary_right=np.stack(saved_right),final_heads=world.heads,final_where=world.where,final_packets=world.packets)
    return dict(passed=True,colonies=n,periods=periods,physical_ticks=world.time,period_results=records,metrics=totals,
                initial_histories_zero=True,no_host_replacement_of_upper_transitions=True,no_between_period_reinitialization=True,
                complete_raw_words_per_decoded_cell=f.FIELDS,snapshot=str(snapshot_path),snapshot_sha256=sha(snapshot_path),
                limitation='Executed one-link periods on canonical coherent mixed-right/left-zero Signal trajectories with actual flag evolution. Unsupported left Signals and controller/packet interactions reject. No complete upper work period at depth two or noise robustness is established.')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--colonies',type=int,default=1);parser.add_argument('--periods',type=int,default=2);parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output);snapshot=out.with_suffix('.npz')
    if out.exists() or snapshot.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();result=run(args.colonies,args.periods,snapshot)
    modules=(backend,boundary,profile,gather,events,f,c,p,r,relation,native)
    sources=[Path(__file__),*(Path(module.__file__) for module in modules),*(Path(module.__file__).with_suffix('.cpp') for module in (backend,boundary,gather,events)),events.CUDA]
    result.update(descriptor_sha256=f.self_description().digest(),rom_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest(),
                  source_sha256={str(path):sha(path) for path in sources},seconds=time.perf_counter()-start,
                  host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__':main()
