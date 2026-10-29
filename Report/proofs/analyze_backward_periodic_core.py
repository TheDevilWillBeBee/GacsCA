#!/usr/bin/env python3
"""Verify retained SP22 startup-core data; measurements remain finite.

Reconstruct the two-level initial encoding, verify every overwrite position
and explicit frozen value, sampled reference-copy values, every-update GF
union and boundary decodes. The shielded context's locality arithmetic is
checked independently. No universal repair or iid theorem is inferred.
"""
import argparse,copy,hashlib,json
from pathlib import Path
import sys,time
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import numpy as np
from gacsca import codec,machine,gray_errors,gpu
from check_sparse_prefix448_physical import augmented
import proposed_sparse_backward_fitted448 as proposed
import periodic_ever_gpu as observer
import check_backward_fitted448_periodic_core as driver


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--stem',choices=['SP22_periodic_startup_core','SP22_shielded_startup_core'],required=True)
    args=parser.parse_args();started=time.monotonic()
    out=ROOT/'figs/robustness';stem=args.stem
    physical=out/(stem+'_physical.json');v=json.loads(physical.read_text())
    candidate=proposed.load_artifact();p=candidate.p
    assert v['proposed_candidate_sha256']==candidate.digest() and v['proposed_netlist_sha256']==candidate.comp.digest
    assert v['proposal_source_sha256']==digest(Path(proposed.__file__))
    assert v['operator_receipt_sha256']==digest(out/'SP22_periodic_operator_certificate.json')
    assert v['observer_helper_sha256']==digest(Path(observer.__file__))
    execution=copy.copy(candidate);execution.rom=np.pad(candidate.rom,((0,(1<<p.k)-p.Q),(0,0)))
    assert v['kernel_sha256']==hashlib.sha256(observer.source(execution).encode()).hexdigest()
    assert v['completed_rom_sha256']==hashlib.sha256(execution.rom.tobytes()).hexdigest()
    normal=gpu._source(execution);observed=observer.source(execution)
    marker='/* Per-tick difference tracking'
    assert normal.split(marker)[0]==observed.split(marker)[0]
    input_asset=out/(stem+'_inputs.npz');data=out/(stem+'_tracking.npz')
    assert v['input_asset_sha256']==digest(input_asset) and v['tracking_asset_sha256']==digest(data)
    with np.load(input_asset,allow_pickle=False) as z:
        top=z['top'];upper=z['upper'];base=z['boundary_packed'];prepared=z['prepared_packed']
        cases=json.loads(str(z['cases_json']));center=int(z['center']);begin=int(z['begin'])
        assert int(z['prepared_tick'])==v['core_tau']
    assert np.array_equal(upper,augmented(candidate,top))
    assert np.array_equal(base,machine.CKernel.pack(augmented(candidate,upper)))
    assert cases==v['cases'] and center==v['center'] and begin==v['core_begin']==center+1
    assert base.shape==prepared.shape==(candidate.W,v['physical_cells']//64)
    with np.load(data,allow_pickle=False) as z:
        ticks=z['snapshot_ticks'];snapshots=z['central_snapshots_packed'];final=z['final_packed']
        overwrite_ticks=z['overwrite_ticks'];sites=z['overwrite_sites'];values=z['overwrite_values']
        ever=z['every_computed_GF_Age_ever_words'];last=z['every_tick_last_rows'];last_any=z['every_tick_last_any']
    assert len(overwrite_ticks)==17 and values.shape==(17,len(cases),candidate.W,16)
    assert overwrite_ticks.tolist()==[v['core_tau']+j for j in (*range(16),38)]
    pointset=set();frozen_checks=reference_checks=0
    bytick={int(t):pack for t,pack in zip(ticks,snapshots)}
    lo,hi=v['central_snapshot_window'];width=hi-lo
    assert width==32*p.Q and lo//64==center//64-16*(p.Q//64)
    for i,t in enumerate(overwrite_ticks):
        active=sites[i][sites[i]>=0]
        expected=np.arange(begin,begin+16) if i<16 else np.array([begin+15])
        assert np.array_equal(active,expected)
        pointset.update((int(x),int(t)) for x in active)
        for case_index,case in enumerate(cases):
            if case['mode']!='reference':
                want=driver.raw_values(candidate,case,prepared,active)
                assert np.array_equal(values[i,case_index,:,:len(active)],want)
                frozen_checks+=len(active)
            elif int(t) in bytick:
                packed=bytick[int(t)][0]
                donors=active+case['delta']-lo
                want=((packed[:,donors//64]>>(donors%64).astype(np.uint64))&1).astype(bool)
                assert np.array_equal(values[i,case_index,:,:len(active)],want)
                reference_checks+=1
    classification=gray_errors.classify(pointset,Q=p.Q,U=p.U,sep=16,exact_limit=64)
    assert json.loads(json.dumps(classification))==v['classification'] and classification['level1']
    union=np.unpackbits(ever.view(np.uint8),axis=1,bitorder='little').astype(bool)
    assert union.shape==(len(cases)+1,v['physical_cells']) and not union[0].any()
    assert not union[:,:lo].any() and not union[:,hi:].any()
    extents=[driver.extent(union[r],center) for r in range(1,len(cases)+1)]
    assert extents==v['GF_Age_ever_extents']
    assert [int(last[r].max()) for r in range(1,len(cases)+1)]==v['GF_Age_last_difference_ticks']
    assert [int(last_any[r].max()) for r in range(1,len(cases)+1)]==v['full_word_last_difference_ticks']
    rows=[candidate.row[f,b] for f,w in (('addr',p.k),('age',p.m)) for b in range(w)]
    checks={row['tick']:row for row in v['checks']}
    boundary_results=[]
    virtual=upper.copy()
    for period in range(1,v['completed_periods']+1):
        virtual=execution.step_numpy(virtual)
        tick=period*p.U
        packed=bytick[tick]
        ref=machine.CKernel.unpack(packed[0],width)
        decoded_ref=codec.decode(candidate,ref)
        start=lo//p.Q
        assert np.array_equal(decoded_ref,virtual[:,start:start+32])
        entries=[]
        for ring,case in enumerate(cases,1):
            raw=machine.CKernel.unpack(packed[ring],width)
            decoded=codec.decode(candidate,raw)
            gf_bad=np.flatnonzero(np.any(decoded[rows]!=decoded_ref[rows],axis=0))
            full_bad=np.flatnonzero(np.any(decoded!=decoded_ref,axis=0))
            info,agree=codec.logical_info(candidate,raw)
            five_copy_GF_Age_agree=True
            for b in rows:
                primary=int(candidate.layout[b])
                physical_sites=primary+np.arange(32)*p.Q
                copies=[raw[candidate.row['info',bit],(physical_sites+off)%width]
                        for bit,off in proposed.info_copies(p)]
                five_copy_GF_Age_agree &= all(np.array_equal(copies[0],value) for value in copies[1:])
            entries.append(dict(name=case['name'],upper_GF_Age_changed_relative_colonies=(gf_bad-16).tolist(),
                upper_all_fields_changed_relative_colonies=(full_bad-16).tolist(),
                wrong_upper_GF=candidate.field(decoded,'addr')[gf_bad].tolist(),
                wrong_upper_Age=candidate.field(decoded,'age')[gf_bad].tolist(),
                five_copy_GF_Age_groups_consistent=bool(five_copy_GF_Age_agree),
                current_GF_Age_lower_native_equal=bool(np.array_equal(raw[rows],ref[rows])),
                all_Info_groups_consistent=bool(agree)))
        boundary_results.append(dict(period=period,tick=tick,rings=entries))
    expected=machine.CKernel.pack(augmented(candidate,virtual))
    assert np.array_equal(final[0],expected)
    final_check=checks[v['completed_periods']*p.U]
    for ring in range(1,len(cases)+1):
        gf=driver.masks(final[ring],final[0],rows);full=driver.masks(final[ring],final[0])
        assert driver.extent(gf,center)==final_check['rings'][ring-1]['GF_Age']
        assert driver.extent(full,center)==final_check['rings'][ring-1]['full_word']
    for t,packed in bytick.items():
        row=checks[t]
        for ring in range(1,len(cases)+1):
            gf=driver.masks(packed[ring],packed[0],rows)
            full=driver.masks(packed[ring],packed[0])
            assert int(gf.sum())==row['rings'][ring-1]['GF_Age']['count']
            assert not bool(full.any())==row['rings'][ring-1]['central_full_word_equal']
    shield=None
    if stem=='SP22_shielded_startup_core':
        assert len(cases)==1 and top.shape==(candidate.W,9)
        assert np.array_equal(candidate.field(top,'addr'),np.arange(-4,5)%p.Q)
        assert not np.delete(top,[candidate.row['addr',b] for b in range(p.k)],axis=0).any()
        primaries=set(candidate.layout.tolist())|{p.lo,p.hi-1}
        for A in np.arange(-4,5)%p.Q:
            assert all((int(A)+slot)%p.Q not in primaries for slot in range(-2,3))
        margin=min(lo,v['physical_cells']-hi)
        assert margin>12*p.U
        assert v['completed_periods']==1
        shield=dict(coarse_GF_words=list(map(int,np.arange(-4,5)%p.Q)),unused_Info_checks=45,
            initial_context_dependency_margin=margin,first_period_dependency_radius=12*p.U,
            strict_margin=margin-12*p.U,
            pristine_initial_and_single_error_central_dependency_shield_arithmetic_proved=True,
            finite_backend_equivalence_measured_only=True)
    result=dict(proposal='SP22',proposed_rule_change=False,active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        checker_sha256=digest(Path(__file__)),proposal_source_sha256=digest(Path(proposed.__file__)),
        physical_receipt_sha256=digest(physical),input_asset_sha256=digest(input_asset),tracking_asset_sha256=digest(data),
        observer_helper_sha256=digest(Path(observer.__file__)),parent_driver_sha256=digest(Path(driver.__file__)),
        experiment_stem=stem,overwrite_points_per_case=257,explicit_frozen_word_checks=frozen_checks,
        sampled_reference_batch_checks=reference_checks,central_snapshots_verified=len(bytick),
        original_word_transition_source_unmodified=True,GF_Age_ever_extents=extents,
        boundary_decodes=boundary_results,pristine_causal_shield=shield,
        measured_only=True,universal_single_island_upper_map_or_iid_failure_proved=False,
        global_reliability_established=False,seconds=time.monotonic()-started,
        scope='verified retained finite SP22 periodic data and exact decoder; shield locality arithmetic proved separately, numerical observations measured only')
    (out/(stem+'_analysis.json')).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(stem=stem,GF_ever=extents,boundaries=boundary_results,shield=shield)),flush=True)


if __name__=='__main__':
    main()
