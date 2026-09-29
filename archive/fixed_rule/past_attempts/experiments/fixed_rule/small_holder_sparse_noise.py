"""Whole-period independent physical replacement-noise pilot, without resampling."""
import argparse,hashlib,json,resource,time,traceback
from dataclasses import replace
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import small_holder_noise as noise,small_holder_resident_general as gpu,small_holder_general_faults as overlay
from gacsca.fixed_rule import small_holder_rule as f,small_holder_projected as r,small_holder_program as p,small_holder_core as c,small_holder_native as native
from experiments.fixed_rule.small_holder_execution import initial_ring
from experiments.fixed_rule.small_holder_temporal_repair import no_host,raw


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def decoded_raw(world):
    return np.array([[cell.s2_data for cell in world.read(tuple(col*f.Q+a for a in p.layout().info))] for col in range(world.background.colonies)],dtype=np.uint64)
def physical_equal(world,base,reference):
    keys=world.positions
    for start in range(0,len(keys),256):
        part=keys[start:start+256]
        if world.read(part)!=reference.physical_cells(part):return False
    same=np.array_equal(base.stored(),reference.stored());g=p.layout()
    if same:
        for col in range(base.colonies):
            for start in range(g.computation_cells,f.Q-5,256):
                positions=tuple(col*f.Q+a for a in range(start,min(f.Q-5,start+256)))
                if base.logical_cells(positions)!=reference.logical_cells(positions):same=False;break
            if not same:break
    if same:return True
    if not keys:return False
    # Rare cancellation case: a differing reference can be corrected by exceptions.
    for start in range(0,world.sites,256):
        positions=tuple(range(start,min(world.sites,start+256)))
        if world.read(positions)!=reference.physical_cells(positions):return False
    return True


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);parser.add_argument('--seed',type=int,required=True);parser.add_argument('--periods',type=int,default=2);parser.add_argument('--rate-exponent',type=int,default=44);parser.add_argument('--max-events',type=int,default=2048);args=parser.parse_args();stem=Path(args.output)
    for ext in ('.json','.npz','.noise.npz','.progress.json','.events.jsonl'):
        if stem.with_suffix(ext).exists():raise FileExistsError('preserve evidence')
    if not 1<=args.periods<=8:raise ValueError('bounded pilot period count required')
    top=tuple(replace(x,f2=1) for x in initial_ring());sites=len(top)*f.Q;horizon=args.periods*f.U
    started=time.perf_counter()
    try:schedule=noise.generate(sites,horizon,args.seed,args.rate_exponent,max_events=args.max_events)
    except noise.EventLimit as exc:
        stem.with_suffix('.json').write_text(json.dumps(dict(execution_complete=False,resource_rejected=True,seed=args.seed,drawn_events=exc.count,limit=exc.limit,resampled=False),indent=2)+'\n');raise
    np.savez_compressed(stem.with_suffix('.noise.npz'),times=schedule.times,positions=schedule.positions,replacements=schedule.replacements)
    selected=set(map(int,np.linspace(0,len(schedule.times)-1,min(8,len(schedule.times)),dtype=int)))
    frames=[];expected_frames=[];checks=[];probes=[];event_records=[];gpu_seconds=0.;processed=0;completed=False;final_equal=None;error=None
    totals=dict(literal_exception_ticks=0,coherent_accelerated_ticks=0,rebased_data_cells=0,rebased_flag_fields=0);max_exceptions=0
    wanted=tuple(r.lift(x) for x in top);final_time=0;pending=None
    with stem.with_suffix('.events.jsonl').open('x') as log:
        with gpu.World(top) as reference,gpu.World(top) as base,overlay.World(base) as world:
            def advance_plain(target):
                nonlocal gpu_seconds,max_exceptions
                while world.time<target:
                    amount=min(c.T,target-world.time);tick=time.perf_counter()
                    with no_host():metrics=world.advance(amount);reference.advance(amount)
                    gpu_seconds+=time.perf_counter()-tick
                    for key in totals:totals[key]+=metrics[key]
                    max_exceptions=max(max_exceptions,len(world.positions))
                    stem.with_suffix('.progress.json').write_text(json.dumps(dict(status='running',physical_time=world.time,processed_events=processed,total_events=len(schedule.times),gpu_run_seconds=gpu_seconds))+'\n')
            def advance_to(target):
                nonlocal pending
                if pending is not None and pending['time']+1<=target:
                    advance_plain(pending['time']+1);pending['after_local_before_noise']=raw(world.read(pending['positions']));probes.append(pending);pending=None
                advance_plain(target)
            try:
                event=0;boundary=1
                while event<len(schedule.times) or boundary<=args.periods:
                    next_event=int(schedule.times[event]) if event<len(schedule.times) else horizon+1
                    next_boundary=boundary*f.U if boundary<=args.periods else horizon+1
                    target=min(next_event,next_boundary);advance_to(target)
                    if target==next_event:
                        end=event+1
                        while end<len(schedule.times) and int(schedule.times[end])==target:end+=1
                        indices=range(event,end);chosen=next((i for i in indices if i in selected),None)
                        if chosen is not None:
                            center=int(schedule.positions[chosen]);positions=tuple((center+d)%sites for d in range(-14,15))
                            pending=dict(event_index=chosen,time=target,positions=positions,before_noise=raw(world.read(positions)))
                        replacements={int(schedule.positions[i]):r.decode_cell(schedule.replacements[i].tolist()) for i in indices}
                        world.inject(replacements)
                        points=tuple(replacements)
                        for start in range(0,len(points),256):
                            part=points[start:start+256];assert world.read(part)==tuple(r.lift(replacements[pos]) for pos in part)
                        if pending is not None:pending['after_noise']=raw(world.read(pending['positions']))
                        record=dict(time=target,first_event=event,count=end-event,positions=list(points),exceptions_after_injection=len(world.positions))
                        max_exceptions=max(max_exceptions,len(world.positions));event_records.append(record);log.write(json.dumps(record)+'\n');log.flush();processed=end;event=end
                    if target==next_boundary:
                        wanted=tuple(r.lift(r.project(x)) for x in native.step_ring(wanted));expected=raw(wanted)
                        np.testing.assert_array_equal(raw(reference.decode()),expected)
                        actual=decoded_raw(world);frames.append(actual);expected_frames.append(expected)
                        try:valid=all(r.lift(r.project(f.decode_cell(row.tolist())))==f.decode_cell(row.tolist()) for row in actual)
                        except ValueError:valid=False
                        check=dict(period=boundary,time=target,equal_to_healthy=bool(np.array_equal(actual,expected)),different_raw_words=int(np.count_nonzero(actual!=expected)),valid_projected_encoding=valid,exceptions=len(world.positions));checks.append(check);print(json.dumps(check),flush=True);boundary+=1
                advance_to(horizon+8);final_equal=physical_equal(world,base,reference);completed=True
            except Exception as exc:
                error=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc())
            finally:final_time=world.time
    arrays=dict(initial=raw(top),decoded=np.array(frames,dtype=np.uint64).reshape(-1,len(top),f.FIELDS),expected=np.array(expected_frames,dtype=np.uint64).reshape(-1,len(top),f.FIELDS),probe_event_indices=np.array([x['event_index'] for x in probes],dtype=np.uint64),probe_times=np.array([x['time'] for x in probes],dtype=np.uint64),probe_positions=np.array([x['positions'] for x in probes],dtype=np.uint64).reshape(-1,29))
    for name in ('before_noise','after_noise','after_local_before_noise'):arrays['probe_'+name]=np.array([x[name] for x in probes],dtype=np.uint64).reshape(-1,29,f.FIELDS)
    np.savez_compressed(stem.with_suffix('.npz'),**arrays)
    paths=[Path(__file__),Path(noise.__file__),Path(overlay.__file__),Path(gpu.__file__),Path('experiments/fixed_rule/small_holder_temporal_repair.py')]
    forcing_events=sum(f.WF_START-1<=int(t)%f.U<=f.WF_END+f.Q for t in schedule.times)
    result=dict(execution_complete=completed,error=error,noise=schedule.metadata(),noise_archive_sha256=sha(stem.with_suffix('.noise.npz')),processed_events=processed,resampled=False,observations=checks,all_decoded_equal_to_healthy=all(x['equal_to_healthy'] for x in checks) and len(checks)==args.periods,final_physical_equal_to_healthy=final_equal,final_time=final_time,noise_free_settling_ticks=8,forcing_or_clearing_events=forcing_events,noise_groups=len(event_records),simultaneous_groups=sum(x['count']>1 for x in event_records),max_observed_exceptions=max_exceptions,advance_metrics=totals,local_transition_probes=len(probes),gpu_advance_seconds_including_reference=gpu_seconds,seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,physical_descriptor_sha256=f.self_description().digest(),source_sha256={str(path):sha(path) for path in paths},fault_binary_sha256=sha(overlay.library()._name),controller_binary_sha256=sha(gpu.library()._name),artifact_sha256=sha(stem.with_suffix('.npz')),event_log_sha256=sha(stem.with_suffix('.events.jsonl')),scope='very-low-rate independent uniform whole-cell replacements over complete physical work periods, one simulation link; fixed predetermined seed, no conditioning on success; no threshold or cross-level amplification claim')
    stem.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');stem.with_suffix('.progress.json').write_text(json.dumps(dict(status='complete' if completed else 'failed',physical_time=final_time,processed_events=processed))+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('source_sha256','error')},indent=2),flush=True)
    if not completed:raise RuntimeError(error['message'])


if __name__=='__main__':main()
