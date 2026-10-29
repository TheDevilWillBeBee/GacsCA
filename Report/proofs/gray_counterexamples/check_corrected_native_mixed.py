#!/usr/bin/env python3
"""Adaptive E0-pair attack on the corrected native Proposition2 geometry.

Replay twenty retained real1 bursts from check_corrected_native_real1, then
insert adjacent pairs every25 ticks at native geometry or Flag1 fronts.
The E0 locations are masked before observation. Exact replacement values
and every adaptive choice are retained; trajectories are measurements.
"""
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'Report/proofs'))
import numpy as np
from gacsca import gray_errors,gpu
import periodic_ever_gpu as observer
import corrected_native_rule as native
from check_corrected_native_real1 import replace_bits


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def extrema(words):
    where=np.flatnonzero(words)
    if not len(where):
        return None
    first,last=int(where[0]),int(where[-1])
    left=(int(words[first])&-int(words[first])).bit_length()-1
    right=int(words[last]).bit_length()-1
    return first*64+left,last*64+right


def field_at(cand,state,name,site):
    word,bit=divmod(int(site),64)
    return sum(((int(state[cand.row[name,b],word])>>bit)&1)<<b
               for b in range(dict(cand.schema)[name]))


def front_pair(cand,state,reference,geometry_rows,strategy,begin,time_index):
    bad=np.bitwise_or.reduce(state[geometry_rows]^reference[geometry_rows],axis=0)
    edge=extrema(bad)
    flags=extrema(state[cand.row['f1',0]])
    source=(edge[0] if strategy%2==0 else edge[1]) if edge else int(begin)
    if strategy==0:
        left=source-2
    elif strategy==1:
        left=source+1
    elif strategy==2:
        left=flags[0] if flags else source-2
    else:
        left=flags[1]+1 if flags else source+1
    sites=np.asarray([left,left+1],dtype=np.int64)
    phase=(field_at(cand,state,'addr',source)-source)%cand.p.Q
    age=min(field_at(cand,state,'age',source),5*cand.p.U//8)
    addresses=(sites+phase)%cand.p.Q
    values=np.zeros((cand.W,2),dtype=bool)
    for name,number in (('addr',addresses),('age',age)):
        for bit in range(dict(cand.schema)[name]):
            values[cand.row[name,bit]]=(number>>bit)&1
    if strategy!=2:
        values[cand.row['f1',0]]=True
    if strategy in (0,3):
        values[cand.row['f2',0]]=True
    # All newly inserted WF bits arezero. Existing real1 WF replacements
    # are retained from the input receipt. All Age replacements obey M.
    choice=dict(strategy=strategy,source_site=int(source),pair_left=int(left),
                phase=int(phase),age=int(age),geometry_edges=list(edge) if edge else None,
                flag1_edges=list(flags) if flags else None,time=time_index)
    return sites,values,choice


def main():
    started=time.monotonic(); out=ROOT/'figs/gray_counterexamples'
    original=out/'corrected_native_real1_inputs.npz'
    original_receipt=out/'corrected_native_real1_certificate.json'
    with np.load(original) as saved:
        selected=np.array([i for i,(mode,_) in enumerate(saved['cases'])
                           if mode in (0,1,5,6,7)],dtype=np.int64)
        baseline=saved['baseline'].copy()
        cases=saved['cases'][selected].copy()
        real1_points=saved['error_points'][selected].copy()
        times=saved['times'].copy()
        replay_sites=saved['sites'][:,selected].copy()
        replay_values=saved['values'][:,selected].copy()
        direct_ever=np.concatenate((saved['direct_geometry_ever'][:1],
                                   saved['direct_geometry_ever'][selected+1]),axis=0)
    cand=native.candidate(); p=cand.p
    nrings=len(selected)+1; columns=48; N=columns*p.Q
    horizon=p.U//32+1; maximum_age=5*p.U//8
    assert maximum_age+horizon < 3*p.U//4
    geometry_rows=[cand.row[field,bit] for field,w in (('addr',p.k),('age',p.m))
                   for bit in range(w)]
    initial=np.broadcast_to(baseline,(nrings,)+baseline.shape).copy()
    sim=observer.sim(cand,nrings,columns)
    sim.set_state(initial,t=0)
    quiet=[gpu.noise() for _ in range(nrings)]
    sim.set_noise(quiet); sim.track(geometry_rows)
    print(json.dumps(dict(cases=len(selected),Q=p.Q,U=p.U,horizon=horizon,
                          adaptive_pair_period=25)),flush=True)
    # Replay exact real1 values. These locations lie within the real1 box;
    # direct disagreements are retained separately for its spatial envelope.
    for event,T in enumerate(times):
        sim.run(int(T)-sim.t); packed=sim.state()
        for case in range(len(selected)):
            valid=replay_sites[event,case]>=0
            sites=replay_sites[event,case,valid]
            for row in range(cand.W):
                replace_bits(packed[case+1],row,sites,replay_values[event,case,row,valid])
        sim.set_state(packed,t=int(T))
    begins=real1_points[:,:,0].min(axis=1)+23
    retained_times=[]; retained_sites=[]; retained_values=[]; choices=[]; checks=[]
    geometry_restored=False
    for event,T in enumerate(range(175,horizon+1,25)):
        # One clean tick remains before the prospective E0 event. If all raw
        # geometry agrees here, cease errors and invoke the proved noiseless
        # native geometry invariant for the remainder of the horizon.
        sim.set_noise(quiet); sim.run(T-1-sim.t); packed=sim.state()
        wrong=np.count_nonzero(packed[:,geometry_rows]^packed[0,geometry_rows],axis=(1,2))
        checks.append(dict(time=sim.t,wrong_geometry_words=wrong[1:].tolist()))
        if event%20==0:
            print(json.dumps(dict(time=sim.t,uncorrected_cases=int(np.count_nonzero(wrong[1:])))),flush=True)
        if not np.any(wrong[1:]):
            geometry_restored=True; break
        batch_sites=[]; batch_values=[]; batch_choices=[]; cfgs=[gpu.noise()]
        for case in range(len(selected)):
            sites,values,choice=front_pair(cand,packed[case+1],packed[0],geometry_rows,
                                          event%4,int(begins[case]),T)
            assert np.all(sites>=0) and np.all(sites<N)
            assert min(int(sites.min()),N-1-int(sites.max())) > 5*(horizon-T)
            batch_sites.append(sites); batch_values.append(values); batch_choices.append(choice)
            cfgs.append(gpu.noise(boxes=[(int(sites[0]),2,T-1,1,1)],mode='zero'))
        # The CUDA observer excludes these same two error sites at stateT.
        # Zeroing then replacing on thehost gives one final arbitrary
        # replacement, not another error location or transition.
        sim.set_noise(cfgs); sim.run(1); packed=sim.state()
        for case,(sites,values) in enumerate(zip(batch_sites,batch_values)):
            for row in range(cand.W):
                replace_bits(packed[case+1],row,sites,values[row])
        sim.set_state(packed,t=T)
        retained_times.append(T); retained_sites.append(np.stack(batch_sites))
        retained_values.append(np.stack(batch_values)); choices.append(batch_choices)
    if not geometry_restored and sim.t<horizon:
        sim.set_noise(quiet); sim.run(horizon-sim.t); packed=sim.state()
        geometry_restored=not np.any(packed[:,geometry_rows]^packed[0,geometry_rows])
    final=sim.state(); tracking=sim.tracking()
    ever=observer.ever_sites(sim)|direct_ever
    support=[]; classifications=[]; e0counts=[]
    for case in range(len(selected)):
        e0=[(int(x),int(T)) for T,sites in zip(retained_times,retained_sites)
            for x in sites[case]]
        E=list(map(tuple,real1_points[case].tolist()))+e0
        e0actual=gray_errors.level0_points(E)
        assert e0actual==set(e0),(case,len(e0actual),len(e0))
        classified=gray_errors.classify(list(map(tuple,real1_points[case].tolist())),E,Q=p.Q,U=p.U,sep=104)
        assert classified['level1'] and classified['level0']==0,classified
        classifications.append(classified); e0counts.append(len(e0))
        sites=np.flatnonzero(ever[case+1]); cols=np.unique(sites//p.Q)
        support.append(dict(case=case,original_case=int(selected[case]),
            minimum_site=int(sites.min()),maximum_site=int(sites.max()),colonies=cols.tolist(),
            fits_two_adjacent_colonies=bool(cols[-1]-cols[0]<=1),
            last_computed_geometry_difference_outside_E0=int(tracking['last_rows'][case+1].max())))
    inputs=out/'corrected_native_mixed_inputs.npz'
    np.savez_compressed(inputs,selected_original_cases=selected,cases=cases,
        real1_error_points=real1_points,times=np.asarray(retained_times,dtype=np.int64),
        sites=np.stack(retained_sites),values=np.stack(retained_values),direct_geometry_ever=direct_ever)
    tracks=out/'corrected_native_mixed_tracking.npz'
    np.savez_compressed(tracks,final=final,computed_geometry_ever_outside_E0=observer.ever_words(sim),
                        direct_real1_geometry_ever=direct_ever,**tracking)
    choice_asset=out/'corrected_native_mixed_choices.json'
    choice_asset.write_text(json.dumps(choices,separators=(',',':'))+'\n')
    raw=gpu._source(cand); observed=observer.source(cand)
    assert observed.split('/* Per-tick difference tracking')[0] == raw.split('/* Per-tick difference tracking')[0]
    result=dict(Q=p.Q,U=p.U,radius=5,width=cand.W,cases=len(selected),physical_sites=N,
        maximum_error_age=maximum_age,age_guard_slack=3*p.U//4-maximum_age-horizon,
        proposition2_geometry_horizon=horizon,measured_stop_time=sim.t,
        adaptive_pair_period=25,adaptive_pair_events=len(retained_times),E0_points_per_case=e0counts,
        first_E0_time=175,last_real1_error_time=150,error_lambda=24,error_separation_c=104,
        classifications=classifications,every_inserted_pair_is_exactly_E0=True,
        original_input_sha256=digest(original),original_receipt_sha256=digest(original_receipt),
        input_asset_sha256=digest(inputs),tracking_asset_sha256=digest(tracks),
        choice_asset_sha256=digest(choice_asset),checker_sha256=digest(__file__),
        corrected_native_source_sha256=digest(native.__file__),
        active_maintenance_sha256=digest(ROOT/'gacsca/maintenance.py'),
        observer_source_sha256=digest(observer.__file__),cuda_kernel_sha256=sim.source_sha256,
        generated_observer_sha256=hashlib.sha256(observed.encode()).hexdigest(),
        candidate_sha256=cand.digest(),netlist_sha256=cand.comp.digest,
        operator_receipt_sha256=digest(out/'corrected_native_operator_certificate.json'),
        geometry_invariant_receipt_sha256=digest(out/'native_geometry_invariant_certificate.json'),
        geometry_restored=bool(geometry_restored),checks=checks,support=support,
        every_observed_damage_fits_two_adjacent_colonies=all(r['fits_two_adjacent_colonies'] for r in support),
        measured_only=True,candidate_counterexample_observed=not geometry_restored or
            not all(r['fits_two_adjacent_colonies'] for r in support),rigorous_counterexample_proved=False,
        errors_ceased_at_measured_stop=True,full_gray_physical_programme_verified=False,
        global_reliability_established=False,elapsed_seconds=time.monotonic()-started,
        scope='Bounded-clock corrected native restriction; finite adaptive E0 challenge, not a universal recovery proof.')
    (out/'corrected_native_mixed_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('cases','adaptive_pair_events','measured_stop_time',
        'geometry_restored','every_observed_damage_fits_two_adjacent_colonies',
        'candidate_counterexample_observed','elapsed_seconds')}),flush=True)


if __name__=='__main__':
    main()
