"""Paired actual GPU trajectories under independent full-state space-time noise."""
import argparse,json,resource,time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_projected as r,retimed_holder_program as p
from gacsca.fixed_rule import retimed_holder_noise_schedule as noise,retimed_holder_pulse_domain as domain
from gacsca.fixed_rule import retimed_holder_resident_general as general,retimed_holder_general_faults as faults,retimed_holder_cuda_general_snapshot as snapshots
from experiments.fixed_rule.run_retimed_holder_cpu_periods import parents
from experiments.fixed_rule.retimed_holder_cuda_encoded_repair import forbidden,raw
from experiments.fixed_rule.run_retimed_holder_streamed_repair import sha


def digest_snapshot(state):
    import hashlib
    digest=hashlib.sha256()
    for key in sorted(state):digest.update(key.encode());digest.update(state[key].tobytes())
    return digest.hexdigest()


def same(a,b):return all(np.array_equal(a[key],b[key]) for key in a)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);parser.add_argument('--seed',type=int,default=2026092711);parser.add_argument('--expected-marks',type=float,default=128);parser.add_argument('--colonies',type=int,default=15);parser.add_argument('--periods',type=int,default=2);args=parser.parse_args()
    if not 1<=args.colonies<=15 or not 1<=args.periods<=3:raise ValueError('bounded pilot size required')
    out=Path(args.output);artifact=out.with_suffix('.npz')
    if out.exists() or artifact.exists():raise FileExistsError(out)
    started=time.perf_counter();n=args.colonies;horizon=args.periods*f.U;sites=n*f.Q;g=p.layout();top=parents(n)
    sampled=noise.sample(sites=sites,ticks=horizon,expected_marks=args.expected_marks,seed=args.seed);schedule=sampled.pop('schedule');replacements=sampled.pop('replacements')
    saved=dict(schedule=schedule,replacements=replacements,initial_top=raw(top));groups={}
    for index,(at,pos,draw) in enumerate(schedule):groups.setdefault(int(at),[]).append(index)
    boundaries={period*f.U:period for period in range(1,args.periods+1)};targets=sorted(set(groups)|set(boundaries));events=[];periods=[];metrics=[];peak=0;complete=False;error=None
    expected=top
    with general.World(top,device_budget=32*1024**2) as background,general.World(top,device_budget=32*1024**2) as healthy,faults.World(background) as actual:
        def read_actual(positions):
            positions=list(map(int,positions));chunks=[]
            for start in range(0,len(positions),256):chunks.append(raw(actual.read(positions[start:start+256])))
            return np.concatenate(chunks) if chunks else np.empty((0,f.FIELDS),dtype=np.uint64)
        def read_healthy(positions):return raw(healthy.physical_cells(tuple(map(int,positions))))
        def save_state(prefix,state):
            for key,value in state.items():saved[prefix+'_'+key]=value
        def advance(target):
            with forbidden():
                row=actual.advance(target-actual.time,literal_budget=4096)
                healthy.advance(target-healthy.time,extra_device_budget=32*1024**2)
            metrics.append(row)
        try:
            for at_index,target in enumerate(targets):
                advance(target);indices=groups.get(target,[])
                if indices:
                    positions=sorted({int(schedule[index,1]) for index in indices});prefix=f'event{len(events)}'
                    a,b=snapshots.snapshot(background),snapshots.snapshot(healthy);pre_match=not actual.positions and same(a,b)
                    zero_context=not np.any(b['flags']) and not (f.WF_START<=healthy.age<f.WF_END and np.any(b['signals']))
                    eligible=pre_match and zero_context and domain.locally_two_sparse(positions,size=sites)
                    halo=sorted({(pos+d)%sites for pos in positions for d in range(-28,29)})
                    saved[prefix+'_halo_positions']=np.array(halo,dtype=np.uint64);saved[prefix+'_healthy_initial']=read_healthy(halo)
                    changes={}
                    for index in indices:changes[int(schedule[index,1])]=r.decode_cell(replacements[index])
                    saved[prefix+'_before_at_faults']=read_actual(positions)
                    actual.inject(changes);saved[prefix+'_actual_initial']=read_actual(halo)
                    row=dict(time=target,mark_indices=indices,distinct_fault_sites=len(positions),pre_fault_complete_match=pre_match,theorem_premises_before_fault=eligible,actual_readback_word_changes=int(np.count_nonzero(read_actual(positions)!=saved[prefix+'_before_at_faults'])),literal_steps=[])
                    events.append(row)
                if target in boundaries:
                    period=boundaries[target];expected=r.step_ring(expected);a,b=snapshots.snapshot(background),snapshots.snapshot(healthy)
                    save_state(f'period{period}_actual',a);save_state(f'period{period}_healthy',b)
                    saved[f'period{period}_exception_positions']=np.array(actual.positions,dtype=np.uint64);saved[f'period{period}_exception_rows']=read_actual(actual.positions)
                    try:decoded=raw(actual.decode());decode_error=None
                    except ValueError as exc:decoded=np.empty((0,f.FIELDS),dtype=np.uint64);decode_error=str(exc)
                    wanted=raw(expected);saved[f'period{period}_decoded']=decoded;saved[f'period{period}_expected']=wanted
                    row=dict(period=period,time=target,decode_error=decode_error,all_decoded_raw_words_equal=decoded.shape==wanted.shape and np.array_equal(decoded,wanted),complete_physical_match=not actual.positions and same(a,b),physical_exceptions=len(actual.positions))
                    periods.append(row);print(json.dumps(dict(stage='period',**row,seconds=time.perf_counter()-started)),flush=True)
                if indices:
                    next_target=targets[at_index+1] if at_index+1<len(targets) else horizon
                    for tick in range(1,min(2,next_target-target)+1):
                        with forbidden():step=actual.step();healthy.step()
                        probes=sorted({(pos+d)%sites for pos in positions for d in range(-7*tick,7*tick+1)})
                        saved[prefix+f'_tick{tick}_positions']=np.array(probes,dtype=np.uint64)
                        saved[prefix+f'_tick{tick}_actual']=read_actual(probes);saved[prefix+f'_tick{tick}_healthy']=read_healthy(probes)
                        a,b=snapshots.snapshot(background),snapshots.snapshot(healthy);match=not actual.positions and same(a,b)
                        events[-1]['literal_steps'].append(dict(tick=tick,**step,complete_physical_match=match,actual_background_sha256=digest_snapshot(a),healthy_sha256=digest_snapshot(b)))
                    if len(events)%32==0:print(json.dumps(dict(stage='noise',groups=len(events),time=actual.time,exceptions=len(actual.positions),seconds=time.perf_counter()-started)),flush=True)
                peak=max(peak,background.device_bytes+healthy.device_bytes+actual.device_bytes+2*(32*n*(f.Q//64)+2*n)+8*n*(g.memory_count+5+32*6+1));assert peak<64*1024**2
            complete=True
        except Exception as exc:error=dict(type=type(exc).__name__,message=str(exc));print(json.dumps(dict(stage='stopped',error=error,time=actual.time)),flush=True)
        # Preserve the exact represented state even if a resource/domain guard
        # stops execution; a stopped run is not counted as a noise failure/success.
        save_state('final_actual',snapshots.snapshot(background));save_state('final_healthy',snapshots.snapshot(healthy))
        saved['final_exception_positions']=np.array(actual.positions,dtype=np.uint64);saved['final_exception_rows']=read_actual(actual.positions)
        actual_time=actual.time
    np.savez_compressed(artifact,**saved)
    result=dict(passed=complete,completed=complete,error=error,noise=sampled,colonies=n,physical_sites=sites,requested_ticks=horizon,actual_ticks=actual_time,periods=periods,event_groups=events,advance_metrics=metrics,all_period_decodes_match=complete and all(x['all_decoded_raw_words_equal'] for x in periods),all_period_physical_states_match=complete and all(x['complete_physical_match'] for x in periods),marks_filtered_or_resampled=0,explicit_GPU_peak_bound_bytes=peak,seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,artifact_sha256=sha(artifact),descriptor_sha256=f.self_description().digest(),source_sha256={str(x):sha(x) for x in (Path(__file__),Path(noise.__file__),Path(domain.__file__),Path(general.__file__),Path(faults.__file__),Path(snapshots.__file__))},scope='Independent Poisson full-state noise across two actual lower work periods with paired healthy comparison, literal fault evolution and complete physical/decoded observations. Finite low-rate pilot; no threshold, high-rate robustness or complete noisy depth-two work-period claim.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('event_groups','advance_metrics')},indent=2),flush=True)
    if not complete:raise SystemExit(1)

if __name__=='__main__':main()
