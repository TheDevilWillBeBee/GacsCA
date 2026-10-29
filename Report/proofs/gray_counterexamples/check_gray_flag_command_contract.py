#!/usr/bin/env python3
"""New conditional Gray flag interface audit; no emitted rule modification."""
from pathlib import Path
from dataclasses import replace
from itertools import combinations,product
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'Report/proofs'))
import gray_token_gather_v7 as k
import literal_maintenance as literal
import check_gmw7_intact_hierarchy as initial


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def null_bank():
    """Four raw null words never give a3/5 adjusted Address majority."""
    count=0;signature=hashlib.sha256()
    for live in range(1,6):
        for value in range(k.Q):
            adjusted=[((value if j==live else 0)-j)%k.Q for j in range(1,6)]
            assert max(adjusted.count(v) for v in adjusted)<=2
            signature.update(bytes((live,0)));count+=1
    phases=tuple(range(6))+tuple(range(k.Q-5,k.Q))
    ages=tuple(range(32))+tuple(range(k.U-17,k.U))
    native_checks=0
    for g,A,live,value in product(phases,ages,range(1,6),(0,1,5,k.Q//2,k.Q-2,k.Q-1)):
        cells={j:dict(addr=(g+j)%k.Q if j<0 else g if j==0 else value if j==live else 0,
            age=A if j<0 else (12345 if j==0 else j),f1=j%2,f2=0,wf1=0,wf2=0)
            for j in range(-5,6)}
        printed=literal.scalar(cells);corrected=k.predecessor.scalar_native(cells)
        expected=dict(addr=g,age=(A+1)%k.U,f1=1,f2=int((A+1)%16==0))
        assert {n:printed[n] for n in expected}==expected
        assert {n:corrected[n] for n in expected}==expected
        assert printed['age_now']==A
        native_checks+=1
    assert count==40960 and native_checks==16170
    # No force follows from missing C alone or from a clock jump alone.
    cells={j:dict(addr=0,age=0,f1=0,f2=0,wf1=0,wf2=0) for j in range(-5,6)}
    assert literal.scalar(cells)['f2']==0
    cells={j:dict(addr=(5+j)%k.Q,age=(j<0),f1=0,f2=0,wf1=0,wf2=0)
        for j in range(-5,6)}
    assert literal.scalar(cells)['f2']==0
    # Three null words allow two others to manufacture a majority.
    raw=[0,0,0,3,4]  # adjusted[-1,-2,-3,-1,-1].
    adjusted=[(v-j)%k.Q for j,v in enumerate(raw,1)]
    assert adjusted.count(k.Q-1)==3
    return dict(all_single_nonnull_word_values_checked=count,
        actual_printed_and_h1_native_input_cofactors=native_checks,
        adjusted_vote_signature_sha256=signature.hexdigest(),
        all_legal_Ages_and_phases_extension_proved_algebraically=True,
        missing_colony_alone_or_clock_jump_alone_does_not_force_Flag2=True,
        three_null_right_words_not_universally_sufficient=True)


def workspace_seed():
    """Actual native Flag2 on-source with a five-site Workspace2 seed."""
    # For x in0..4 the union of needed native neighbourhoods is[-5,9].
    # Same shared physical support is used for every reader, not separate
    # independently selected errors at each centre.
    sites=tuple(range(-5,10));supports=[()]+[(x,) for x in sites]+list(combinations(sites,2))
    checks=0;signature=hashlib.sha256()
    for support in supports:
        for bits in range(16**len(support)):
            row={x:dict(addr=x%k.Q,age=96*k.Q,f1=0,f2=0,wf1=0,wf2=int(0<=x<=4))
                for x in sites}
            for q,x in enumerate(support):
                payload=(bits>>(4*q))&15
                row[x]=dict(addr=(x+123+q)%k.Q,age=(k.U-1-17*q)%k.U,
                    f1=payload&1,f2=(payload>>1)&1,wf1=(payload>>2)&1,wf2=(payload>>3)&1)
            for centre in range(5):
                cells={j:row[centre+j] for j in range(-5,6)}
                for scalar in (literal.scalar,k.predecessor.scalar_native):
                    result=scalar(cells)
                    assert result['addr']==centre and result['f2']==1
                signature.update(bytes((centre,1)));checks+=1
    assert len(supports)==121 and checks==135605
    # This is the exact p41 predicate given final computed source values.
    pulse_checks=0
    for address,age,source,flag1 in product((0,1,2,3,4,5,k.Q-1),
        (96*k.Q-1,96*k.Q,98*k.Q-1,98*k.Q),range(2),range(2)):
        actual=int(0<=address<=4 and 96*k.Q<=age<98*k.Q and source==1 and flag1==0)
        assert actual==int(address<5 and age in (96*k.Q,98*k.Q-1) and source and not flag1)
        pulse_checks+=1
    return dict(shared_single_row_supports_checked=len(supports),
        actual_native_reader_and_flag_payload_cofactors=checks,
        every_payload_checked_in_both_printed_and_h1_scalars=True,
        source_predicate_finite_boundary_checks=pulse_checks,
        source_and_reader_signature_sha256=signature.hexdigest(),
        arbitrary_GF_Age_and_flag_payload_extension_proved_by_two_counts=True,
        enumerated_supports_test_local_density_not_all_classified_E0=True,
        source_to_native_Flag2_additional_update_latency=1,
        continuing_E0_or_erosion_theorem=False)


def actual_first_window():
    # Immutable accepted native orbit, with h_t saturation before either
    # pulse. Actual Info holds globally by the Info branch induction.
    B=17*k.Q;h=k.Q
    def cell(x,t):
        c=initial.initial_cell(x)
        return replace(c,age=(t+int(0<=x<B))%k.U,
            f1=int(-h<=x<0 or B-h<=x<B))
    beta=k.ROM((0,)*k.Q,(0,)*k.DICTIONARY_SIZE,0,0)
    # The ROM here is arbitrary for this inactive prefix: no fetch is
    # performed. It is not substituted for the actual own programme.
    checks=0;source_slots=0
    phases=(32*k.Q-2,32*k.Q-1,32*k.Q,37*k.Q-2,37*k.Q-1,37*k.Q,
        96*k.Q-2,96*k.Q-1,96*k.Q,98*k.Q-3,98*k.Q-2,98*k.Q-1)
    for g,residue,t in product((-1,0,1,13,14,15,16,17,18),(3,k.Q-3),phases):
        x=g*k.Q+residue;cells={j:cell(x+j,t) for j in range(-5,6)}
        output=k.local_transition(cells,beta)
        native=k.predecessor.scalar_native({j:{n:getattr(c,n) for n in k.NATIVE_NAMES}
            for j,c in cells.items()})
        assert native['addr']==x%k.Q and native['age']!=0
        assert output.info==initial.initial_cell(x).info==(0,)*5
        assert output.wf1==output.wf2==0
        checks+=1;source_slots+=5
    # Precise inclusive input-row sets for computed-age window96Q..98Q-1.
    ranges=[]
    for label in (0,1):
        lo=96*k.Q-1-label;hi=98*k.Q-2-label
        assert lo+1+label==96*k.Q and hi+1+label==98*k.Q-1
        assert hi-lo+1==2*k.Q and hi<112*k.Q and hi+1+label<k.U
        ranges.append(dict(clock_label=label,input_rows_inclusive=[lo,hi],
            output_rows_inclusive=[lo+1,hi+1]))
    assert checks==216 and source_slots==1080
    assert k.FIELD['info']==176 and k.PRIMARY_START==4001
    assert not k.PRIMARY_START<=3<k.PRIMARY_START+k.FRAME_WORDS
    assert not k.PRIMARY_START<=k.Q-3<k.PRIMARY_START+k.FRAME_WORDS
    return dict(actual_F7_source_neighbourhood_checks=checks,
        actual_zero_source_output_slots_checked=source_slots,pulse_input_rows=ranges,
        source_zeros_and_global_Info_hold_proved_for_entire_first_window=True,
        actual_intact_clock_only_real2_history_reused_without_upper_errors=True,
        arbitrary_inactive_ROM_lookup_irrelevant_not_a_replacement_evaluator=True,
        no_third_stage_evaluator_or_special_source_write_in_current_F7=True,
        earliest_head_birth_computed_age=112*k.Q+1,
        earliest_execution_computed_age=112*k.Q+2,
        original_early_write_deadline_computed_age=80*k.Q,
        mere_p41_pulse_predicate_substitution_has_zero_first_window_sources=True,
        no_modified_candidate_emitted=True)


def calculate():return dict(null_bank=null_bank(),workspace_seed=workspace_seed(),first_window=actual_first_window())


def main():
    started=time.monotonic();source=Path(__file__).parent;directory=ROOT/'figs/gray_counterexamples'
    result=calculate()
    receipt=dict(name='Conditional Gray flag-bank and Workspace command contract; GMW7 early-source gap',
        Q=k.Q,U=k.U,lambda_original=24,c_original=104,
        checker_sha256=digest(__file__),proof_sha256=digest(source/'GRAY_FLAG_COMMAND_CONTRACT.md'),
        source_dependencies_sha256={name:digest(source/name) for name in
            ('gray_token_gather_v7.py','gray_moving_word_v2.py','gray_moving_word_kernel.py',
             'literal_maintenance.py','GRAY_COMPUTED_SIMBIT_ORDER.md')},
        root_initializer_source_sha256=digest(initial.__file__),
        root_initializer_proof_sha256=digest(ROOT/'Report/proofs/GMW7_INTACT_HIERARCHY.md'),
        receipt_dependencies_sha256={name:digest(directory/name) for name in
            ('GMW7_single_gather_period_certificate.json','GMW7_WF0_clock_island_certificate.json')},
        retained_initial_checker_failure_assets_sha256={name:digest(directory/name) for name in
            ('Gray_flag_command_contract_initial_checker.py.txt','Gray_flag_command_contract_initial_checker_failure.txt')},
        initial_checker_bitwise_vs_whole_word_vote_assertion_removed=True,
        primary_gray_text_sha256=digest(ROOT/'papers_txt/gray_readers_guide.txt'),
        primary_locations={'native':'pp21-22','early_flags':'pp34-35','organized_repair_context':'pp37-40',
            'Workspace_pulse_and_waves':'pp41-43'},
        results=result,Workspace_SimBit_premise_is_final_computed_not_pre_wipe=True,
        actual_damaged_Gray_input_bank_Age_progression_and_early_evaluator_refinement=False,
        full_corrected_Gray_rule_reconstruction_or_reliability=False,
        changed_GMW7_first_window_interface_gap_only=True,
        active_rule_modified=False,modified_candidate_emitted=False,
        Gray_Gacs_Address_decoded_memory_or_iid_refuted=False,
        elapsed_seconds=time.monotonic()-started)
    path=directory/'Gray_flag_command_contract_certificate.json'
    path.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(results=result,receipt_sha256=digest(path),elapsed_seconds=receipt['elapsed_seconds'])))


if __name__=='__main__':main()
