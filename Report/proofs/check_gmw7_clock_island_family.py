#!/usr/bin/env python3
"""Pinned all-phase clock-island family; universal proof is in the Markdown."""
from pathlib import Path
from dataclasses import replace
import hashlib,json,sys,time
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'Report/proofs/gray_counterexamples'
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(SOURCE))
import check_gray_token_gather_v7_clock_island as old


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def state(x,h,B):return int(0<=x<B),int(-h<=x<0 or B-h<=x<B)


def cuts(h,B):
    low=-old.k.Q-6;high=B+6
    values={low,high}
    values.update(b-j for b in (0,B,-h,B-h) for j in range(-5,6))
    values.update(g*old.k.Q-j for g in range(-2,5) for j in range(-5,6))
    return sorted(x for x in values if low<=x<=high)


def actual(states,address,theta,delta):
    cells={j:dict(addr=(address+j)%old.k.Q,age=(theta+delta*v[0])%old.k.U,
        f1=v[1],f2=0,wf1=0,wf2=0) for j,v in states.items()}
    return old.k.predecessor.scalar_native(cells)


def main():
    started=time.monotonic();out=ROOT/'figs/robustness';gray=ROOT/'figs/gray_counterexamples'
    Q,U=old.k.Q,old.k.U;B=2*Q;saturation=(Q+2)//3
    previous=json.loads((gray/'GMW7_WF0_clock_island_certificate.json').read_text())
    assert previous['proof_sha256']==digest(SOURCE/'GMW7_WF0_CLOCK_ISLAND.md')
    assert previous['checker_sha256']==digest(old.__file__)
    for name,value in previous['source_dependencies_sha256'].items():assert value==digest(SOURCE/name)
    assert previous['root_initializer_checker_sha256']==digest(old.initial.__file__)
    assert previous['root_initializer_proof_sha256']==digest(ROOT/'Report/proofs/GMW7_INTACT_HIERARCHY.md')
    assert previous['native_factor_closed_for_arbitrary_legal_private_fields']
    assert not previous['Gray_Gacs_G17_Address_memory_or_iid_refuted']
    clock_cases=((0,1),(U-1,1),(0,U-1),(U//2,U//2),(U-2,2),(17,U//2+1))
    events=actual_checks=0;signature=hashlib.sha256();rows=[]
    for t in range(saturation+1):
        h=min(3*t,Q);hn=min(3*(t+1),Q);points=cuts(h,B);count=0
        for lo,hi in zip(points,points[1:]):
            neighbours={j:state(lo+j,h,B) for j in range(-5,6)}
            expected=state(lo,hn,B)
            assert expected==state(hi-1,hn,B)
            assert old.factor(neighbours,lo%Q)==expected,(t,lo,hi)
            assert [state(lo+j,h,B) for j in range(-5,6)]==[
                state(hi-1+j,h,B) for j in range(-5,6)]
            assert [0<=lo%Q+j<Q for j in range(-5,6)]==[
                0<=(hi-1)%Q+j<Q for j in range(-5,6)]
            signature.update(bytes(expected));events+=1;count+=1
            if t in (0,1,2,saturation-1,saturation):
                label,flag=expected
                for theta,delta in clock_cases:
                    clock=(theta+t)%U
                    assert actual(neighbours,lo%Q,clock,delta)==dict(addr=lo%Q,
                        age=(clock+1+delta*label)%U,f1=flag,f2=0,wf1=0,wf2=0)
                    actual_checks+=1
        rows.append(dict(tick=t,flag_suffix_width=h,next_flag_suffix_width=hn,event_segments=count))
    # Certify the actual m1 formula prefix, then its earliest violation.
    # A later test of the uncorrected formula would use counterfactual
    # clock inputs and cannot certify an actual-history update.
    m1_events=0;violation=None
    for t in range(saturation):
        h=min(3*t,Q);hn=min(3*(t+1),Q);points=cuts(h,Q)
        for lo,hi in zip(points,points[1:]):
            neighbours={j:state(lo+j,h,Q) for j in range(-5,6)}
            expected=state(lo,hn,Q);got=old.factor(neighbours,lo%Q)
            assert expected==state(hi-1,hn,Q)
            assert [state(lo+j,h,Q) for j in range(-5,6)]==[
                state(hi-1+j,h,Q) for j in range(-5,6)]
            assert [0<=lo%Q+j<Q for j in range(-5,6)]==[
                0<=(hi-1)%Q+j<Q for j in range(-5,6)]
            if got!=expected:
                assert t+1==2730 and lo==2 and got==(0,1) and expected==(1,1)
                result=actual(neighbours,lo%Q,t,1)
                assert result==dict(addr=2,age=2730,f1=1,f2=0,wf1=0,wf2=0)
                violation=dict(tick=t+1,x=lo,actual_native_output=result,
                    expected_stationary_formula_label=1,actual_label=0)
                break
            m1_events+=1
        if violation is not None:break
    assert violation is not None
    assert m1_events==152790
    # Every member of the claimed original-real2 range satisfies its
    # explicit geometry bound. Isolation/recursive conditions are written.
    for m in range(2,105):
        assert m*Q<=Q*Q and Q<m*Q and m*Q-1<104*Q
        assert {-1,m-1}.isdisjoint({0,m})
    support=out/'GMW7_clock_island_family_errors.npz'
    np.savez_compressed(support,x=np.arange(B,dtype=np.int64),t=np.zeros(B,dtype=np.int64),
        replacement_age=np.array([1],dtype=np.uint32))
    samples=[]
    for x in (0,1,old.k.PRIMARY_START,Q-1,Q,B-1):
        clean=old.initial.initial_cell(x);noisy=replace(clean,age=1)
        assert noisy!=clean and all(getattr(noisy,n)==getattr(clean,n)
            for n in clean.__dataclass_fields__ if n!='age')
        samples.append(dict(x=x,initial_words=[hex(v) for v in old.k.cell_words(clean)],
            replacement_words=[hex(v) for v in old.k.cell_words(noisy)]))
    table=out/'GMW7_clock_island_family_transients.json'
    table.write_text(json.dumps(rows,separators=(',',':'))+'\n')
    receipt=dict(name='GMW7 all-phase/aligned-width stationary native-clock island family',
        Q=Q,U=U,lambda_original=24,c_original=104,minimum_stationary_family_colonies=2,
        minimum_stationary_family_sites=B,all_integer_colonies_at_least_two_proved=True,
        all_common_initial_phases_and_nonzero_modular_offsets_proved=True,
        all_Q_aligned_integer_origins_proved=True,original_real2_colony_range=[2,104],
        actual_intact_operational_phase_start_proved=True,
        minimum_only_for_displayed_constant_offset_zero_initial_flags_stationary_formula=True,
        minimum_arbitrary_fault_support_or_sufficient_reliable_repair_proved=False,
        saturation_tick=saturation,transient_rows=len(rows),event_segment_checks=events,
        supplementary_actual_native_checks=actual_checks,clock_cases=[list(v) for v in clock_cases],
        transient_output_signature_sha256=signature.hexdigest(),
        transient_asset_sha256=digest(table),support_asset_sha256=digest(support),
        retained_smaller_error={'m':2,'theta':0,'delta':1,'origin':0,'points':B,'tick':0,
            'replacement_recipe':'replace(initial_cell(x), age=1)','all_other_fields_untouched':True,
            'no_later_errors':True,'one_original_real2_proved':True,'sampled_payloads':samples},
        m1_prefix_verified_through_tick=2729,m1_prefix_event_segment_checks=m1_events,
        m1_first_stationary_formula_violation=violation,m1_permanent_support_formula_fails=True,
        initial_m1_history_wording_correction_receipt_sha256=digest(
            out/'GMW7_clock_island_family_initial_m1_wording_correction.json'),
        written_inductions_supply_universal_family_and_infinite_time=True,
        native_factor_closed_for_arbitrary_legal_private_fields=True,
        bounded_spatial_hull_and_canonical_Address_remain=True,
        finite_temporal_clock_recovery_refuted_for_changed_WF0=True,
        Gray_Gacs_G17_Address_memory_or_iid_refuted=False,
        global_reliability_established=False,active_G17_modified=False,
        rule_programme_or_constant_change=False,numerical_whole_CA_trajectory_used=False,
        checker_sha256=digest(__file__),proof_sha256=digest(ROOT/'Report/proofs/GMW7_CLOCK_ISLAND_FAMILY.md'),
        pinned_clock_factor_receipt_sha256=digest(gray/'GMW7_WF0_clock_island_certificate.json'),
        source_dependencies_sha256={n:digest(SOURCE/n) for n in
            ('GMW7_WF0_CLOCK_ISLAND.md','check_gray_token_gather_v7_clock_island.py',
             'gray_token_gather_v7.py','gray_moving_word_v2.py','gray_moving_word_kernel.py','literal_maintenance.py')},
        root_initializer_checker_sha256=digest(old.initial.__file__),
        root_initializer_proof_sha256=digest(ROOT/'Report/proofs/GMW7_INTACT_HIERARCHY.md'),
        elapsed_seconds=time.monotonic()-started)
    path=out/'GMW7_clock_island_family_certificate.json'
    path.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({key:receipt[key] for key in ('event_segment_checks','supplementary_actual_native_checks',
        'minimum_stationary_family_sites','all_common_initial_phases_and_nonzero_modular_offsets_proved',
        'global_reliability_established','elapsed_seconds')}),flush=True)


if __name__=='__main__':main()
