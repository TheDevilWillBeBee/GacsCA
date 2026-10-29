#!/usr/bin/env python3
"""Six finite periodic SP22 startup-core probes; measured only.

One clean twin and six copies, each with one 257-point core. Track every
computed GF/Age differing site, not just selected snapshots. No halo is
driven and no later E0 is used. The finite initial context is two encoding
levels above a one-cell zero top; no infinite hierarchy is asserted.
"""
import argparse,copy,hashlib,json
from pathlib import Path
import sys,time
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import numpy as np
from gacsca import machine,gray_errors
from check_sparse_prefix448_physical import augmented
from check_coherent_phase_physical import replace_bits
import proposed_sparse_backward_fitted448 as proposed
import periodic_ever_gpu as observer

CASES=[
    dict(name='evolving_reference_GF_plus_one',mode='reference',delta=1),
    dict(name='frozen_TF_GF_plus_one',mode='frozen',delta=1,clock='TF'),
    dict(name='frozen_TF_GF_minus_six',mode='frozen',delta=-6,clock='TF'),
    dict(name='frozen_TF_GF_plus_sixteen',mode='frozen',delta=16,clock='TF'),
    dict(name='frozen_last_clock_GF_minus_one',mode='frozen',delta=-1,clock='last'),
    dict(name='all_one_raw_words',mode='one')]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def raw_values(candidate,case,reference,sites):
    p=candidate.p
    if case['mode']=='reference':
        donors=(sites+case['delta'])%(reference.shape[1]*64)
        return ((reference[:,donors//64]>>(donors%64).astype(np.uint64))&1).astype(bool)
    value=np.full((candidate.W,len(sites)),case['mode']=='one',dtype=bool)
    if case['mode']=='frozen':
        gf=(sites+case['delta'])%p.Q
        clock=p.T_wf if case['clock']=='TF' else p.U-1
        candidate.set_field(value,'addr',gf)
        candidate.set_field(value,'age',p.age_code(clock))
        for field in ('f1','wf1','backward_pressure'):
            candidate.set_field(value,field,1)
        eligible=(gf>=1)&(gf<=5)
        candidate.set_field(value,'wf2',eligible)
        candidate.set_field(value,'packet_valid',eligible)
        candidate.set_field(value,'packet_tag',np.where(eligible,gf-1,0))
    return value


def masks(packed,reference,rows=None):
    difference=packed^reference
    if rows is not None:
        difference=difference[rows]
    return np.unpackbits(np.bitwise_or.reduce(difference,axis=0).view(np.uint8),bitorder='little').astype(bool)


def extent(mask,center):
    points=np.flatnonzero(mask)
    return dict(count=len(points),relative_min=int(points[0]-center) if len(points) else None,
        relative_max=int(points[-1]-center) if len(points) else None)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--periods',type=int,default=2)
    args=parser.parse_args();assert args.periods>=1
    started=time.monotonic()
    out=ROOT/'figs/robustness';stem='SP22_periodic_startup_core'
    candidate=proposed.load_artifact();p=candidate.p
    cells=p.Q*p.Q;center=(p.Q//2)*p.Q;begin=center+1;tau=p.T_wf-8
    top=np.zeros((candidate.W,1),dtype=bool)
    upper=augmented(candidate,top)
    base=machine.CKernel.pack(augmented(candidate,upper))
    execution=copy.copy(candidate)
    execution.rom=np.pad(candidate.rom,((0,(1<<p.k)-p.Q),(0,0)))
    warm=observer.sim(execution,1,p.Q);warm.set_state(base)
    warm.run(tau)
    prepared=warm.state()[0];del warm
    asset=out/(stem+'_inputs.npz')
    np.savez_compressed(asset,top=top,upper=upper,boundary_packed=base,prepared_packed=prepared,
        prepared_tick=tau,cases_json=json.dumps(CASES),center=center,begin=begin)
    sim=observer.sim(execution,len(CASES)+1,p.Q)
    sim.set_state(prepared,t=tau)
    rows=[candidate.row[f,b] for f,w in (('addr',p.k),('age',p.m)) for b in range(w)]
    sim.track(rows)
    events={tau+j:np.arange(begin,begin+16) if j<16 else np.array([begin+15]) for j in (*range(16),38)}
    points={(int(x),int(t)) for t,sites in events.items() for x in sites}
    classification=gray_errors.classify(points,Q=p.Q,U=p.U,sep=16,exact_limit=64)
    assert classification['level1'] and classification['points']==257,classification
    local_clocks=sorted({p.T_wf-8,p.T_wf-1,p.T_wf,p.T_wf+1,p.T_wf+8,p.T_wf+39,
        p.T_wf+128,p.T_wf+449,p.T_wf+898,p.T_wf+1150,p.T_wf+1792,p.T_wf+1793,
        p.T_wf+1794,p.T_wf+2304,p.T_wf+4096,p.T_wf+8192,p.T_wf+12000,
        p.E0+p.NP*p.PL})
    stages={n*p.U+c for n in range(args.periods) for c in local_clocks if n*p.U+c>=tau}
    boundaries={n*p.U for n in range(1,args.periods+1)}
    checkpoints=sorted(set(events)|stages|boundaries)
    checks=[];snapshots=[];snapshot_ticks=[];overwrite_ticks=[];overwrite_sites=[];overwrite_values=[]
    lo=center-16*p.Q;hi=center+16*p.Q
    initial_delta_bound=rows
    result=dict(proposal='SP22',proposed_rule_change=False,active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)),driver_sha256=digest(Path(__file__)),
        observer_helper_sha256=digest(Path(observer.__file__)),gpu_backend_sha256=digest(ROOT/'gacsca/gpu.py'),
        augmented_helper_sha256=digest(ROOT/'Report/proofs/check_sparse_prefix448_physical.py'),
        physical_helper_sha256=digest(ROOT/'Report/proofs/check_coherent_phase_physical.py'),
        classifier_sha256=digest(ROOT/'gacsca/gray_errors.py'),
        build_receipt_sha256=digest(out/'SP22_program_build.json'),
        operator_receipt_sha256=digest(out/'SP22_periodic_operator_certificate.json'),
        input_asset_sha256=digest(asset),kernel_sha256=sim.source_sha256,
        completed_rom_sha256=hashlib.sha256(execution.rom.tobytes()).hexdigest(),
        Q=p.Q,U=p.U,width=candidate.W,radius=12,physical_cells=cells,rings=len(CASES)+1,
        center=center,core_begin=begin,core_tau=tau,classification=classification,cases=CASES,
        overwrite_batches_per_case=17,overwrite_points_per_case=257,prewarm_updates=tau,
        requested_periods=args.periods,completed_periods=0,periodic_CA_trajectories=True,
        changed_boundary_condition=False,continuing_E0=False,initial_pristine_infinite_hierarchy=False,
        entire_run_single_island_infinite_line_equivalence_established=False,
        central_snapshot_window=[lo,hi],single_island_causal_radius=12,
        latest_central_single_island_causal_tick=tau+(cells-16*p.Q-16-1)//12,
        observed_GFAge_union_tracks_every_computed_update=True,computed_state_snapshots_before_same_tick_overwrite=True,
        universal_island_confinement_or_repair_established=False,global_reliability_established=False,
        measured_only=True,checks=checks,
        scope='six finite actual periodic own-ROM startup cores; every computed GF/Age union and sampled full states; two encoding levels/finite zero top, no continuing E0 or iid theorem')
    try:
        for tick in checkpoints:
            sim.run(tick-sim.t)
            packed=sim.state();reference=packed[0]
            row=dict(tick=tick,clock=tick%p.U,boundary=tick in boundaries,rings=[])
            for ring,case in enumerate(CASES,1):
                gf=masks(packed[ring],reference,rows)
                full=masks(packed[ring],reference)
                row['rings'].append(dict(ring=ring,name=case['name'],GF_Age=extent(gf,center),full_word=extent(full,center),
                    central_full_word_equal=not bool(full[lo:hi].any())))
            checks.append(row)
            if tick in stages or tick in boundaries:
                snapshots.append(packed[:,:,lo//64:hi//64].copy());snapshot_ticks.append(tick)
                print(json.dumps(dict(tick=tick,clock=row['clock'],boundary=row['boundary'],
                    GF_counts=[v['GF_Age']['count'] for v in row['rings']],
                    full_counts=[v['full_word']['count'] for v in row['rings']],seconds=round(time.monotonic()-started,2))),flush=True)
            if tick in boundaries:
                result['completed_periods']=tick//p.U
            if tick in events:
                sites=events[tick]
                values=np.zeros((len(CASES),candidate.W,16),dtype=bool)
                saved_sites=np.full(16,-1,dtype=np.int64);saved_sites[:len(sites)]=sites
                for ring,case in enumerate(CASES,1):
                    value=raw_values(candidate,case,reference,sites)
                    values[ring-1,:,:len(sites)]=value
                    for bit in range(candidate.W):
                        replace_bits(packed[ring],bit,sites,value[bit])
                overwrite_ticks.append(tick);overwrite_sites.append(saved_sites);overwrite_values.append(values)
                sim.set_state(packed,t=tick)
        result['result']='measured: all requested finite periodic core periods completed'
    finally:
        tracking=sim.tracking();ever=observer.ever_words(sim)
        tracked_sites=np.unpackbits(ever.view(np.uint8),axis=1,bitorder='little').astype(bool)
        data=out/(stem+'_tracking.npz')
        np.savez_compressed(data,snapshot_ticks=snapshot_ticks,central_snapshots_packed=np.stack(snapshots),
            final_packed=sim.state(),overwrite_ticks=overwrite_ticks,overwrite_sites=np.stack(overwrite_sites),
            overwrite_values=np.stack(overwrite_values),every_computed_GF_Age_ever_words=ever,
            **{'every_tick_'+k:v for k,v in tracking.items()})
        result.update(tracking_asset_sha256=digest(data),recorded_overwrite_batches=len(overwrite_ticks),
            GF_Age_ever_extents=[extent(tracked_sites[ring],center) for ring in range(1,len(CASES)+1)],
            GF_Age_last_difference_ticks=[int(tracking['last_rows'][ring].max()) for ring in range(1,len(CASES)+1)],
            full_word_last_difference_ticks=[int(tracking['last_any'][ring].max()) for ring in range(1,len(CASES)+1)],
            elapsed_seconds=time.monotonic()-started)
        (out/(stem+'_physical.json')).write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(dict(result=result.get('result','incomplete'),GF_ever=result['GF_Age_ever_extents'],
            GF_last=result['GF_Age_last_difference_ticks'],seconds=result['elapsed_seconds'])),flush=True)


if __name__=='__main__':
    main()
