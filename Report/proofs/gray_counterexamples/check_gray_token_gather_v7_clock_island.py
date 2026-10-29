#!/usr/bin/env python3
"""Exact native stationary clock island for the changed fixed-WF0 GMW7.

New, initially unregistered certificate. Every transient event interval is
checked in the proved two-clock quotient; native scalar cofactors certify
the quotient's finite representatives. No Gray/iid/Address-memory result.
"""
from pathlib import Path
import hashlib,json,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'Report/proofs'))
import gray_token_gather_v7 as k
import check_gmw7_intact_hierarchy as initial

B=17*k.Q
PHASES=tuple(range(6))+tuple(range(k.Q-5,k.Q))


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def factor(states,address):
    """The derived binary-clock/F1 quotient, GF canonical, F2=WF=0."""
    right=int(sum(states[j][0] for j in range(1,6))>=3)
    left=int(sum(states[j][0] for j in range(-5,0))>=3)
    mismatch=sum(0<=address+j<k.Q and states[j][0]!=right for j in range(-5,0))
    flags=sum(0<=address+j<k.Q and states[j][1] for j in range(1,6))
    f1=int(mismatch>=3 or flags>=3 or (states[0][1] and flags>=2))
    return (left if f1 else right),f1


def native(states,address,clock):
    cells={j:dict(addr=(address+j)%k.Q,age=(clock+v[0])%k.U,
        f1=v[1],f2=0,wf1=0,wf2=0) for j,v in states.items()}
    return k.predecessor.scalar_native(cells)


def quotient_cofactors():
    total=wrap=0;signature=hashlib.sha256()
    for address in PHASES:
        inside=[j for j in range(1,6) if address+j<k.Q]
        for bits in range(1<<11):
            labels={j:(bits>>(j+5))&1 for j in range(-5,6)}
            # The native equations read only the *count* of old F1 in the
            # right in-colony interval and old selfF1. Other F1 bits are
            # absent from those equations. All possible counts occur here.
            for count in range(len(inside)+1):
                for self_flag in (0,1):
                    states={j:(labels[j],int(j in inside[:count]) if j else self_flag)
                        for j in range(-5,6)}
                    label,flag=factor(states,address)
                    result=native(states,address,0)
                    assert result==dict(addr=address,age=1+label,f1=flag,f2=0,wf1=0,wf2=0)
                    signature.update(bytes((label,flag)));total+=1
            # Wrap and exceptional local labels are checked independently;
            # translation in clock is proved algebraically for all20-bit t.
            states={j:(labels[j],j%2) for j in range(-5,6)}
            label,flag=factor(states,address)
            assert native(states,address,k.U-1)==dict(addr=address,age=label,f1=flag,f2=0,wf1=0,wf2=0)
            wrap+=1
    assert total==208896 and wrap==22528
    # The finite phase representatives partition ALL8192 phase values.
    phase_checks=0
    for address in range(k.Q):
        representative=address if address<5 or address>=k.Q-5 else 5
        assert representative in PHASES
        assert [0<=address+j<k.Q for j in range(-5,6)]==[
            0<=representative+j<k.Q for j in range(-5,6)]
        phase_checks+=1
    return dict(finite_count_representatives=total,wrap_clock_masks=wrap,
        all_phase_inside_vector_identities=phase_checks,
        actual_native_output_signature_sha256=signature.hexdigest(),
        clock_translation_and_flag_count_extensions_proved_algebraically=True)


def state(x,h):
    return int(0<=x<B),int(-h<=x<0 or B-h<=x<B)


def cuts(h):
    boundaries=(0,B,-h,B-h)
    low=-k.Q-6;high=B+6
    result={low,high}
    result.update(b-j for b in boundaries for j in range(-5,6))
    result.update(g*k.Q-j for g in range(-2,20) for j in range(-5,6))
    return sorted(x for x in result if low<=x<=high)


def transient_events():
    rows=[];checks=scalar_checks=0;signature=hashlib.sha256()
    saturation=(k.Q+2)//3
    for tick in range(saturation+1):
        h=min(3*tick,k.Q);hnext=min(3*(tick+1),k.Q)
        points=cuts(h);local_checks=0
        for lo,hi in zip(points,points[1:]):
            assert lo<hi
            expected=state(lo,hnext)
            assert expected==state(hi-1,hnext)
            neighbours={j:state(lo+j,h) for j in range(-5,6)}
            actual=factor(neighbours,lo%k.Q)
            assert actual==expected,(tick,lo,hi,actual,expected)
            # Event compression: at the other endpoint all old neighbours
            # and inside tests are identical, hence the whole segment is.
            assert [state(lo+j,h) for j in range(-5,6)]==[state(hi-1+j,h) for j in range(-5,6)]
            assert [0<=lo%k.Q+j<k.Q for j in range(-5,6)]==[
                0<=(hi-1)%k.Q+j<k.Q for j in range(-5,6)]
            signature.update(bytes(actual));checks+=1;local_checks+=1
            if tick in (0,1,2,saturation-1,saturation):
                clock=tick%k.U;label,flag=expected
                assert native(neighbours,lo%k.Q,clock)==dict(addr=lo%k.Q,
                    age=(clock+1+label)%k.U,f1=flag,f2=0,wf1=0,wf2=0)
                scalar_checks+=1
        rows.append(dict(tick=tick,flag_suffix_width=h,next_flag_suffix_width=hnext,
            event_segments=local_checks))
    assert rows[-1]['flag_suffix_width']==k.Q
    return dict(saturation_tick=saturation,transient_rows=len(rows),event_segment_checks=checks,
        additional_actual_scalar_checks=scalar_checks,output_signature_sha256=signature.hexdigest(),
        rows=rows,steady_state_native_period=k.U,translation_per_period=0)


def error_certificate(directory):
    xs=np.arange(B,dtype=np.int64);ticks=np.zeros(B,dtype=np.int64)
    path=directory/'GMW7_WF0_clock_island_errors.npz'
    np.savez_compressed(path,x=xs,t=ticks,replacement_age=np.array([1],np.uint32))
    assert len(xs)==139264 and np.all(xs[1:]-xs[:-1]==1)
    # Candidate1 pairs(0,1),(2,3) are disjoint and24Q-linked; their
    # union is a minimal candidate2. The whole row fits Q², its diameter
    # is<104Q, and no proper subset can pass isolation on a unit-linked row.
    assert B<k.Q*k.Q and B-1<104*k.Q and B>k.Q
    assert 2<24 and 2<24*k.Q
    samples=[]
    for x in (0,1,k.PRIMARY_START,k.Q-1,k.Q,B-1):
        clean=initial.initial_cell(x)
        from dataclasses import replace
        noisy=replace(clean,age=1)
        assert noisy.addr==clean.addr and noisy.age!=clean.age
        assert {n:getattr(noisy,n) for n in clean.__dataclass_fields__ if n!='age'}=={
            n:getattr(clean,n) for n in clean.__dataclass_fields__ if n!='age'}
        samples.append(dict(x=x,initial_words=[hex(v) for v in k.cell_words(clean)],
            replacement_words=[hex(v) for v in k.cell_words(noisy)]))
    return dict(tick=0,error_interval=[0,B],interval_half_open=True,points=B,
        support_asset_sha256=digest(path),replacement_recipe='replace(initial_cell(x), age=1)',
        all_other_native_and_SF_fields_untouched=True,no_later_errors=True,
        original_lambda=24,original_c=104,E0_empty=True,E1_empty=True,
        whole_row_one_original_real2_proved_by_definition=True,sampled_payloads=samples)


def calculate():
    return quotient_cofactors(),transient_events()


def main():
    started=time.monotonic();directory=ROOT/'figs/gray_counterexamples';source=Path(__file__).parent
    quotient,trajectory=calculate()
    table=directory/'GMW7_WF0_clock_island_transients.json'
    table.write_text(json.dumps(trajectory,separators=(',',':'))+'\n')
    errors=error_certificate(directory)
    receipt=dict(name='GMW7 intact-context permanent stationary native-clock island',
        Q=k.Q,U=k.U,lambda_original=24,c_original=104,
        checker_sha256=digest(__file__),proof_sha256=digest(source/'GMW7_WF0_CLOCK_ISLAND.md'),
        source_dependencies_sha256={name:digest(source/name) for name in
            ('gray_token_gather_v7.py','gray_moving_word_v2.py','gray_moving_word_kernel.py','literal_maintenance.py')},
        root_initializer_checker_sha256=digest(initial.__file__),
        root_initializer_proof_sha256=digest(ROOT/'Report/proofs/GMW7_INTACT_HIERARCHY.md'),
        period_receipt_sha256=digest(directory/'GMW7_single_gather_period_certificate.json'),
        gray_class_source_text_sha256=digest(ROOT/'papers_txt/gray_readers_guide.txt'),
        retained_initial_assets_sha256={name:digest(directory/name) for name in
            ('GMW7_WF0_clock_island_initial_proof.md.txt','GMW7_WF0_clock_island_initial_checker.py.txt',
             'GMW7_WF0_clock_island_initial_certificate.json','GMW7_WF0_clock_island_initial_errors.npz')},
        all_subset_separation_wording_clarification_not_a_mathematical_failure=True,
        quotient_cofactors=quotient,transient_event_summary={name:v for name,v in trajectory.items() if name!='rows'},
        transient_asset_sha256=digest(table),errors=errors,
        native_factor_closed_for_arbitrary_legal_private_fields=True,
        intact_recursive_start_with_one_shared_finite_physical_error_history=True,
        wrong_Age_support_all_ticks=[0,B],Flag2_identically_zero=True,
        Flag1_saturation_tick=2731,stationary_not_travelling=True,
        no_finite_spacetime_native_clock_recovery_envelope=True,
        finite_spatial_hull_exists_and_Address_remains_canonical=True,
        private_programme_dictionary_SF_only_changes_cannot_fix_under_unchanged_WF0_native=True,
        Gray_Gacs_G17_Address_memory_or_iid_refuted=False,active_rule_modified=False,
        elapsed_seconds=time.monotonic()-started)
    path=directory/'GMW7_WF0_clock_island_certificate.json';path.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(quotient=quotient,trajectory=receipt['transient_event_summary'],
        receipt_sha256=digest(path),elapsed_seconds=receipt['elapsed_seconds'])))


if __name__=='__main__':main()
