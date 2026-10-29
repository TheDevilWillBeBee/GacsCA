#!/usr/bin/env python3
"""Exact local GR1 real1 clock-wrap commit; no iid or Gray attribution.

The five-site error changes only Age and Hold at time1, starting in GR1's
broad E family. A finite Boolean cone certifies the unintended Age0 commit
and its persistent Info output. The finite ring boundary lies outside every
checked dependency cone; it is not an assumed physical boundary condition.
"""
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
import numpy as np
from gacsca import gray_errors,machine,maintenance
from gacsca.netlist import Net,const_word,w_add_const
import gray_staged_rule as proposed


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prove_clock_advection(p):
    """A five-cell phase-minus2 block travels right3 until its colony edge.

    Four representative unequal clock pairs and every Flag1 on/left of the
    island are checked. Universality over clock values follows separately:
    each five-word list contains only these two values, so its vote is the
    one whose multiplicity is at least3. The native inconsistency rule uses
    only equality of those votes. Its only other clock predicate, d3, is
    disabled by the canonical Address majority. The final increment is the
    same word increment on the selected vote. Right Flags, Flag2/WF are0.
    """
    count=0
    templates=[(4096,5)]+[(p.Q-d,5) for d in range(5,11)]+[(p.Q-r,r) for r in range(1,5)]
    for a,length in templates:
        for residue in range(4):
            for x in range(a-5,a+length+5):
                n=Net()
                good=const_word(residue+2,p.m)
                wrong=w_add_const(n,good,-2)
                cells={j:dict(addr=const_word((x+j)%p.Q,p.k),
                    age=wrong if a<=x+j<a+length else good,
                    f1=n.input(('free_left_Flag1',j)) if x+j<a+length and 0<=x+j<p.Q else 0,
                    f2=0,wf1=0,wf2=0) for j in range(-5,6)}
                actual=maintenance.build(n,cells,p.k,p.m)
                wrong_next=(length>=3 and a+3<=x<=min(a+length+2,p.Q-1))
                expected_age=w_add_const(n,wrong if wrong_next else good,1)
                assert actual['addr']==const_word(x%p.Q,p.k)
                assert actual['age']==expected_age,(a,length,residue,x,'clock')
                assert actual['f2']==0,(a,length,residue,x,'Flag2')
                if x>=min(a+length+2,p.Q-1)+1:
                    assert actual['f1']==0,(a,length,residue,x,'right_Flag1')
                count+=1
    return dict(cofactors=count,templates=templates,representative_unequal_clock_pairs=4,
        arbitrary_clock_label_transfer='Every directional list has only two distinct values; whole-word majority selects the multiplicity>=3 value. All age-dependent Flag decisions use equality of these labels; d3 is0 because canonical GF exists. The final increment is applied to the selected word.',
        free_left_Flag1_bits=True,wrong_clock_phase=-2,
        five_site_clock_island_advects_right3=True,true_colony_edge_blocks_the_island=True)


def main():
    started=time.monotonic()
    out=ROOT/'figs/gray_counterexamples'
    cand=proposed.load_artifact(); p=cand.p
    center=int(cand.layout[cand.row['addr',0]])
    N=512; half=N//2; maximum_ticks=3
    coordinates=center+np.arange(N)-half
    assert coordinates.min()>0 and coordinates.max()<p.Q
    assert half-2>5*maximum_ticks
    # In upper colony0 choose every raw upper field0. Extend to s_i with
    # canonical upper GF=i mod Q, Age0, Flags0, and other fields0. Its encoded
    # logical Info is0 everywhere in this local cone, including unrepresented
    # sites chosen0. This is an actual member of the broad E(s) family.
    base=np.zeros((cand.W,N),dtype=bool)
    cand.set_field(base,'addr',coordinates%p.Q)
    clean=cand.step_numpy(base)
    bad=clean.copy()
    sites=np.arange(half-2,half+3)
    values=cand.field(bad,'age'); values[sites]=p.U-1
    cand.set_field(bad,'age',values)
    for bit in range(dict(cand.schema)['hold']):
        bad[cand.row['hold',bit],sites]=True
    points=[(int(coordinates[i]),1) for i in sites]
    classification=gray_errors.classify(points,Q=p.Q,U=p.U,sep=104)
    assert classification['level0']==0 and classification['level1']
    geometry=[cand.row[f,b] for f,w in (('addr',p.k),('age',p.m)) for b in range(w)]
    frames=[bad.copy()]; checks=[]; steady_info=None
    changed_fields_at_error=['age','hold']
    assert not np.any(bad[cand.row['info',0]:cand.row['info',0]+5]^clean[cand.row['info',0]:cand.row['info',0]+5])
    for raw_time in range(2,maximum_ticks+1):
        clean=cand.step_numpy(clean); bad=cand.step_numpy(bad)
        radius=2+5*(raw_time-1)
        cone=slice(half-radius,half+radius+1)
        # Every input ancestor of this noise-support cone is inside the finite
        # represented array. The unchanged external global configuration is
        # handled by the canonical native invariant, not by ring wrapping.
        assert radius+5*raw_time<half
        native_addr=cand.field(bad,'addr')
        assert np.array_equal(native_addr[cone],coordinates[cone]%p.Q)
        differences=np.flatnonzero(np.any(bad[geometry,cone]^clean[geometry,cone],axis=0))+half-radius
        primary=bad[cand.row['info',2]]
        info_sites=np.flatnonzero(primary[cone])+half-radius
        exact_coherent=True
        for logical in range(half-radius+2,half+radius-1):
            copies=[bad[cand.row['info',slot+2],logical-slot] for slot in range(-2,3)]
            exact_coherent &= len(set(map(bool,copies)))==1
        checks.append(dict(time=raw_time,geometry_difference_sites=coordinates[differences].tolist(),
            primary_Info_one_sites=coordinates[info_sites].tolist(),
            Info_five_copy_coherence=bool(exact_coherent)))
        frames.append(bad.copy())
        if exact_coherent:
            steady_info=coordinates[info_sites].tolist()
    assert steady_info==[center+1,center+2],checks
    # Early commit is visible on a clean update, with Info unmodified by the
    # actual errors. On the next step its surviving Info copies agree1.
    first=frames[1]
    first_clock=cand.field(first,'age')
    first_Info_change=np.flatnonzero(first[cand.row['info',2]])
    assert first_clock[half+1]==0 and first[cand.row['info',2],half+1]
    assert all(bad[cand.row['info',slot+2],half+1-slot] for slot in range(-2,3))
    expected_geometry=list(range(center+1,center+6))
    assert checks[0]['geometry_difference_sites']==expected_geometry
    assert checks[1]['geometry_difference_sites']==[s+3 for s in expected_geometry]
    assert all(cand.field(first,'age')[i]==0 for i in range(half+1,half+6))
    assert all(cand.field(bad,'age')[i]==1 for i in range(half+4,half+9))
    assert not np.any(first[cand.row['f2',0],half-20:half+20])
    assert not np.any(first[cand.row['f1',0],half+6:half+20])
    advection=prove_clock_advection(p)
    # The first false interval begins at center+1; after t-2 updates its
    # left edge is center+1+3(t-2). Its width remains5 until truncated by Q.
    # The final length2 block heals in one update.
    restored_at=2+(p.Q-(center+1)+2)//3
    # There is no second wrap while the erroneous Age values are small. All
    # clean updates after the first wrap have Age values below the actual
    # clock, so no later Age0 commit occurs before the usual boundary.
    for t,state in enumerate(frames[1:],start=2):
        radius=2+5*(t-1)
        vals=cand.field(state,'age')[half-radius:half+radius+1]
        assert np.all(vals<=t)
        if t>2: assert np.all(vals>=1)
    # Native Flags may remain nonzero, but geometry is now the correct common
    # clock. GF-dependent wipe is0 regardless of those flags. Before96Q, WF
    # outputs remain0. The exact healthy-geometry clearing lemma supplies the
    # conservative additional Q ticks to clear both native Flags, well before
    # the second gather at32Q.
    quiet_by=restored_at+p.Q
    assert quiet_by<32*p.Q
    # Mailbox snapshots at32Q+1 and shifts one site per active tick. The local
    # counterexample changes a represented, noncourier Info site. It remains
    # changed until the boundary update; neither intermediate special write
    # can touch it. At this one later tick both streams lie in neighboring
    # colonies, while the retained Info difference remains in colony0.
    Info_target=center+1
    displacement=max(Info_target+1,p.Q-Info_target)+1
    observed_time=32*p.Q+1+displacement
    left=Info_target-displacement; right=Info_target+displacement
    assert left<0 and right>=p.Q
    assert observed_time<48*p.Q
    colonies=sorted({left//p.Q,Info_target//p.Q,right//p.Q})
    assert colonies==[-1,0,1]
    asset=out/'GR1_real1_clock_commit_inputs_and_cone.npz'
    np.savez_compressed(asset,initial=base,error_state=frames[0],states=np.stack(frames),
        coordinates=coordinates,error_points=np.asarray(points,dtype=np.int64))
    result=dict(candidate='GR1',Q=p.Q,U=p.U,width=cand.W,
        error_lambda=24,error_separation_c=104,error_points=points,
        classification=classification,changed_error_fields=changed_fields_at_error,
        replacement_Age=p.U-1,replacement_Hold_all_five_copies=1,
        raw_Info_not_overwritten=True,raw_GF_not_overwritten=True,
        raw_error_time=1,computed_Age0_commit_time=2,
        changed_primary_Info_site=Info_target,
        geometry_restored_at=restored_at,restored_coherent_primary_Info_one_sites=steady_info,
        clock_advection_certificate=advection,
        no_further_spurious_wrap_before_geometry_recovery=True,
        native_Flag_quiet_by=quiet_by,
        local_finite_cone_exact=True,finite_array_sites=N,checks=checks,
        initial_context='GR1 broad E(s): upper GF=i mod Q, upper Age0, Flags0, all other upper fields0; unrepresented logical Info0. All local Info is0 in colony0.',
        GR1_broad_encoded_context_proved=True,
        second_gather_load_time=32*p.Q+1,two_sided_stream_displacement=displacement,
        three_colony_simulation_field_difference_time=observed_time,
        three_colony_witness=[dict(site=left,colony=-1,field='ml',logical_bit=Info_target),
            dict(site=Info_target,colony=0,field='info',logical_bit=Info_target),
            dict(site=right,colony=1,field='mr',logical_bit=Info_target)],
        fixed_two_colony_pointwise_simulation_field_envelope_refuted_for_GR1=True,
        pointwise_mail_witness_uses_exact_route_composition=True,
        Gray_Proposition4_literal_pointwise_target=True,
        faithful_Gray_Proposition4_refuted=False,
        Gray_intact_recursive_initialization_reachability_proved=False,
        accepted_GR1_pure_E0_theorem_refuted=False,
        GR1_boundary_decoding_or_memory_failure_proved=False,
        iid_unreliability_proved=False,global_reliability_established=False,
        proposal_sha256=digest(proposed.__file__),candidate_sha256=cand.digest(),
        netlist_sha256=cand.comp.digest,checker_sha256=digest(__file__),
        input_asset_sha256=digest(asset),active_maintenance_sha256=digest(maintenance.__file__),
        classifier_sha256=digest(gray_errors.__file__),
        numpy_backend_sha256=digest(machine.__file__),
        transport_receipt_sha256=digest(out/'gray_staged_transport_certificate.json'),
        forwarding_receipt_sha256=digest(out/'GR1_frame_certificate.json'),
        native_geometry_receipt_sha256=digest(out/'native_geometry_invariant_certificate.json'),
        native_Flag_quiet_receipt_sha256=digest(out/'GR1_flag_quiet_certificate.json'),
        physical_noiseless_receipt_sha256=digest(out/'GR1_noiseless_period_certificate.json'),
        written_proof_sha256=digest(Path(__file__).with_name('GR1_REAL1_CLOCK_COMMIT.md')),
        primary_Info_represents_upper_field=['reg',2],
        measured_only=False,
        scope='Exact finite Boolean cone and written route composition in changed GR1. The error is real1, not E0. It refutes a GR1 analogue of the literal pointwise all-SF two-colony envelope, not the accepted E0 period theorem, Gray-verbatim recovery, boundary memory, or iid reliability.',
        elapsed_seconds=time.monotonic()-started)
    (out/'GR1_real1_clock_commit_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('computed_Age0_commit_time','geometry_restored_at',
        'restored_coherent_primary_Info_one_sites','three_colony_simulation_field_difference_time',
        'fixed_two_colony_pointwise_simulation_field_envelope_refuted_for_GR1','elapsed_seconds')}))


if __name__=='__main__':
    main()
