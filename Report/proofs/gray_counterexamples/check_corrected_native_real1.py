#!/usr/bin/env python3
"""Hypothesis-valid bounded-clock attack on corrected Gray Proposition2.

Native radius5 rule only. The whole-word Age bound disables published
Workspace pulses throughout the claimed U/32 recovery horizon, making
the native field restriction independent of the simulation completion.
Numerical trajectories remain measurements, not universal proofs.
"""
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'Report/proofs'))
import numpy as np
from gacsca import gray_errors,gpu,machine
import periodic_ever_gpu as observer
import corrected_native_rule as native

MODES=('shift1_clock0','shift_minus1_clockhalf','shift_half_clockhalf',
       'flat_address_ramp_clock','five_colours','independent_checkerboard',
       'random_raw_words','false_colony_start')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def replace_bits(state,row,sites,values):
    words=sites//64
    bits=np.left_shift(np.uint64(1),(sites%64).astype(np.uint64))
    mask=np.zeros(state.shape[1],dtype=np.uint64)
    data=np.zeros_like(mask)
    np.bitwise_or.at(mask,words,bits)
    np.bitwise_or.at(data,words,bits*np.asarray(values,dtype=np.uint64))
    state[row]=(state[row]&~mask)|data


def replacement(cand,mode,sites,seed):
    rng=np.random.default_rng(seed)
    count=len(sites); index=np.arange(count); address=sites%cand.p.Q
    maximum_age=5*cand.p.U//8
    flags=np.zeros((4,count),dtype=np.int64)
    if mode==0:
        address=(address+1)%cand.p.Q; age=np.zeros(count,dtype=np.int64)
    elif mode==1:
        address=(address-1)%cand.p.Q; age=np.full(count,cand.p.U//2); flags[0]=1
    elif mode==2:
        address=(address+cand.p.Q//2)%cand.p.Q; age=np.full(count,cand.p.U//2); flags[:]=1
    elif mode==3:
        address=np.zeros(count,dtype=np.int64); age=(17*index)%(maximum_age+1); flags[1]=1
    elif mode==4:
        address=(address+409*(index%5))%cand.p.Q; age=(index%5)*(maximum_age//4)
        flags[:]=rng.integers(0,2,(4,count))
    elif mode==5:
        address=(address+(index%2)*(cand.p.Q//2))%cand.p.Q
        age=(1-index%2)*maximum_age; flags[0]=index%2; flags[1]=1-index%2
    elif mode==6:
        address=rng.integers(0,cand.p.Q,count); age=rng.integers(0,maximum_age+1,count)
        flags[:]=rng.integers(0,2,(4,count))
    elif mode==7:
        address=(sites-sites[0])%cand.p.Q; age=np.full(count,maximum_age)
    else:
        raise ValueError(mode)
    result=np.zeros((cand.W,count),dtype=bool)
    for field,values in (('addr',address),('age',age)):
        for bit in range(dict(cand.schema)[field]):
            result[cand.row[field,bit]]=((values>>bit)&1).astype(bool)
    for f,field in enumerate(('f1','f2','wf1','wf2')):
        result[cand.row[field,0]]=flags[f].astype(bool)
    return result,address,age


def main():
    started=time.monotonic(); out=ROOT/'figs/gray_counterexamples'
    cand=native.candidate(); p=cand.p
    columns=48; N=columns*p.Q; horizon=p.U//32+1
    maximum_age=5*p.U//8
    assert maximum_age+horizon < 3*p.U//4
    assert 2*5*horizon+2*150 < N
    positions=(-52,1,p.Q//2-52,p.Q-104)
    cases=[(mode,position) for mode in range(len(MODES)) for position in positions]
    begins=np.array([N//2+position for _,position in cases],dtype=np.int64)
    initial_edge_margin=int(min(begins.min()-23,N-begins.max()-127))
    assert initial_edge_margin > 5*horizon
    classifications=[]; event_sets=[]
    for begin in begins:
        points=gray_errors.dense_box(int(begin),24,104,104)+[(int(begin)-23,1),(int(begin)+126,150)]
        result=gray_errors.classify(points,Q=p.Q,U=p.U,sep=104)
        assert result['level1'] and result['level0']==0,result
        classifications.append(result); event_sets.append(np.asarray(points,dtype=np.int64))
    base=np.zeros((cand.W,N),dtype=bool)
    cand.set_field(base,'addr',np.arange(N)%p.Q)
    baseline=machine.CKernel.pack(base)
    initial=np.broadcast_to(baseline,(len(cases)+1,)+baseline.shape).copy()
    geometry_rows=[cand.row[field,bit] for field,w in (('addr',p.k),('age',p.m)) for bit in range(w)]
    sim=observer.sim(cand,len(cases)+1,columns)
    sim.set_state(initial,t=0)
    sim.set_noise([gpu.noise() for _ in range(len(cases)+1)])
    sim.track(geometry_rows)
    direct_ever=np.zeros((len(cases)+1,N),dtype=bool)
    retained_values=[]; retained_sites=[]; retained_times=[]
    events=[1]+list(range(24,128))+[150]
    print(json.dumps(dict(cases=len(cases),Q=p.Q,U=p.U,N=N,horizon=horizon,maximum_age=maximum_age)),flush=True)
    for state_index in events:
        sim.run(state_index-sim.t)
        packed=sim.state()
        batch_values=np.zeros((len(cases),cand.W,104),dtype=bool)
        batch_sites=np.full((len(cases),104),-1,dtype=np.int64)
        for case,(mode,_) in enumerate(cases):
            begin=begins[case]
            sites=(np.array([begin-23]) if state_index==1 else np.array([begin+126])
                   if state_index==150 else begin+np.arange(104))
            values,addresses,ages=replacement(cand,mode,sites,20261011+case*1000+state_index)
            assert np.all(ages<=maximum_age)
            for row in range(cand.W):
                replace_bits(packed[case+1],row,sites,values[row])
            direct_ever[case+1,sites[(addresses!=sites%p.Q)|(ages!=state_index)]]=True
            batch_values[case,:,:len(sites)]=values
            batch_sites[case,:len(sites)]=sites
        retained_values.append(batch_values); retained_sites.append(batch_sites); retained_times.append(state_index)
        sim.set_state(packed,t=state_index)
    input_asset=out/'corrected_native_real1_inputs.npz'
    np.savez_compressed(input_asset,baseline=baseline,cases=np.asarray(cases,dtype=np.int64),
        error_points=np.stack(event_sets),times=np.asarray(retained_times),
        sites=np.stack(retained_sites),values=np.stack(retained_values),direct_geometry_ever=direct_ever)
    checks=[]; geometry_restored=False
    while sim.t < horizon:
        next_check=min(horizon,1024 if sim.t<1024 else sim.t+1024)
        sim.run(next_check-sim.t)
        final=sim.state()
        wrong=np.count_nonzero(final[:,geometry_rows]^final[0,geometry_rows],axis=(1,2))
        checks.append(dict(time=sim.t,wrong_geometry_words=wrong[1:].tolist()))
        print(json.dumps(dict(time=sim.t,uncorrected_cases=int(np.count_nonzero(wrong[1:])))),flush=True)
        if not np.any(wrong[1:]):
            geometry_restored=True; break
    tracking=sim.tracking(); ever=observer.ever_sites(sim)|direct_ever
    support=[]
    for case in range(1,len(cases)+1):
        sites=np.flatnonzero(ever[case])
        cols=np.unique(sites//p.Q)
        support.append(dict(case=case-1,minimum_site=int(sites.min()),maximum_site=int(sites.max()),
            colonies=cols.tolist(),fits_two_adjacent_colonies=bool(cols[-1]-cols[0]<=1),
            last_computed_geometry_difference=int(tracking['last_rows'][case].max())))
    asset=out/'corrected_native_real1_tracking.npz'
    np.savez_compressed(asset,final=final,computed_geometry_ever=observer.ever_words(sim),
                        direct_geometry_ever=direct_ever,**tracking)
    reference_expected=baseline.copy()
    for bit in range(p.m):
        reference_expected[cand.row['age',bit]]=np.uint64(2**64-1) if (sim.t>>bit)&1 else 0
    assert np.array_equal(final[0,geometry_rows],reference_expected[geometry_rows])
    source=observer.source(cand); raw=gpu._source(cand)
    assert source.split('/* Per-tick difference tracking')[0] == raw.split('/* Per-tick difference tracking')[0]
    result=dict(Q=p.Q,U=p.U,radius=5,width=cand.W,cases=len(cases),mode_names=list(MODES),
        positions=list(positions),physical_sites=N,colonies=columns,maximum_error_age=maximum_age,
        proposition2_geometry_horizon=horizon,measured_stop_time=sim.t,
        age_guard_slack=3*p.U//4-maximum_age-horizon,
        pristine_initial_context_edge_margin=initial_edge_margin,
        largest_native_dependency_radius=5*horizon,
        continuing_noise=False,error_separation_c=104,error_lambda=24,
        classifications=classifications,input_asset_sha256=digest(input_asset),
        tracking_asset_sha256=digest(asset),checker_sha256=digest(__file__),
        corrected_native_source_sha256=digest(native.__file__),
        active_maintenance_sha256=digest(ROOT/'gacsca/maintenance.py'),
        observer_source_sha256=digest(observer.__file__),cuda_kernel_sha256=sim.source_sha256,
        generated_observer_sha256=hashlib.sha256(source.encode()).hexdigest(),
        operator_receipt_sha256=digest(out/'corrected_native_operator_certificate.json'),
        geometry_invariant_receipt_sha256=digest(out/'native_geometry_invariant_certificate.json'),
        candidate_sha256=cand.digest(),netlist_sha256=cand.comp.digest,
        geometry_restored=geometry_restored,checks=checks,support=support,
        every_observed_damage_fits_two_adjacent_colonies=all(row['fits_two_adjacent_colonies'] for row in support),
        measured_only=True,candidate_counterexample_observed=not geometry_restored or
            not all(row['fits_two_adjacent_colonies'] for row in support),
        rigorous_counterexample_proved=False,
        full_gray_physical_programme_verified=False,global_reliability_established=False,
        scope='Bounded-clock native restriction; numerical evidence and exact error locations, not a universal recovery proof.',
        elapsed_seconds=time.monotonic()-started)
    (out/'corrected_native_real1_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:result[key] for key in ('cases','measured_stop_time','geometry_restored','every_observed_damage_fits_two_adjacent_colonies','candidate_counterexample_observed','elapsed_seconds')}),flush=True)


if __name__=='__main__':
    main()
