#!/usr/bin/env python3
"""Exact certificates for isolated stage-gated transport/reset primitives.

All clock/address classes and coherent logical bits are checked without
sampling. The native controls and programme writes are explicit premises;
this does not certify a full physical self-simulator or iid reliability.
"""
from pathlib import Path
import hashlib,json,sys,time
from itertools import combinations,product
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,const_word,at_least
import gray_staged_transport as staged
import gray_protocol_spec as spec


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    started=time.monotonic(); out=ROOT/'figs/gray_counterexamples'
    ages=staged.clock_boundaries(); addresses=staged.address_boundaries()
    assert ages[0]==0 and ages[-1]==spec.U
    assert addresses[0]==0 and addresses[-1]==spec.Q
    equalities=0; rest_equalities=0
    for age in ages[:-1]:
        print_age=(age%spec.Q==0)
        if print_age:
            print(json.dumps(dict(checking_computed_age=age)),flush=True)
        for address in addresses[:-1]:
            n=Net()
            symbolic={(f,x,b):n.input(('logical',f,x,b)) for f,w in staged.FIELDS
                      for x in range(-7,8) for b in range(w)}
            cells={x:{f:[symbolic[f,x+slot,b] for slot in staged.SLOTS for b in range(w)]
                      for f,w in staged.FIELDS} for x in range(-5,6)}
            f1=n.input(('computed_native_flag1',)); wipe=n.input(('computed_native_wipe',))
            actual=staged.build(n,cells,const_word(address,13),const_word(age,20),f1,wipe)
            def expression(command):
                if command[0]=='zero':
                    return 0
                if command[0]=='majority3':
                    a,b,c=[expression(item) for item in command[1:]]
                    return n.OR(n.AND(a,b),n.AND(c,n.OR(a,b)))
                return symbolic[command]
            is_rest=any(s.active_end<=age<s.end for s in spec.STAGES)
            for f,w in staged.FIELDS:
                for slot in staged.SLOTS:
                    for b in range(w):
                        command=staged.plan(age,address,slot,f,b)
                        expected=expression(command)
                        if f in ('mr','ml'):
                            expected=n.AND(expected,n.NOT(f1))
                        expected=n.AND(expected,n.NOT(wipe))
                        assert actual[f,slot,b]==expected,(age,address,f,slot,b,command)
                        equalities+=1
                        if is_rest:
                            assert command==(f,slot,b),(age,address,f,slot,b,command)
                            rest_equalities+=1
    # This is an exhaustive truth table, not a stochastic experiment: each
    # position pair and all three Boolean inputs (common correct bit, two
    # arbitrary replacement bits) covers the two-fault fivefold lemma.
    majority_cases=0
    for i,j in combinations(range(5),2):
        for correct,a,b in product((0,1),repeat=3):
            values=[correct]*5; values[i]=a; values[j]=b
            assert at_least(Net(),values,3)==correct
            majority_cases+=1
    # Full-site arbitrary replacements affect atmosttwo of a logical bit's
    # five physical holders. The preceding lemma restores each helper input;
    # the checked routing then gives the exact next coherent output. This
    # commutation argument is conditional on identical correct control inputs.
    gathers=[]
    for g,stage in enumerate(spec.STAGES[:3]):
        for lane,(off,skew) in enumerate(zip(staged.LANES,staged.SKEW)):
            age=staged.capture_age(g,lane)
            if off==0:
                assert age==stage.start+1
                displacement=0
            else:
                distance=age-(stage.start+1)-1
                displacement=-distance if off<0 else distance
                assert distance==abs(off)*spec.Q+(skew if off<0 else -skew)
                assert skew+displacement==off*spec.Q
            assert stage.start<age<stage.active_end
            gathers.append(dict(stage=g+1,offset=off,skew=skew,
                load_computed_age=stage.start+1,capture_computed_age=age,
                destination_shift=skew,source_displacement=displacement))
    assert staged.LEFT_COURIER+1+(staged.LO-3)==staged.FLAG_AGE
    assert staged.RIGHT_COURIER+1+(spec.Q-3-(staged.HI-1))==staged.FLAG_AGE
    assert 64*spec.Q<min(staged.LEFT_COURIER,staged.RIGHT_COURIER)
    assert staged.FLAG_AGE<80*spec.Q
    result=dict(Q=spec.Q,U=spec.U,error_lambda=24,error_separation_c=104,
        schema=list(staged.FIELDS),stored_simulation_bits_per_holder=5*sum(w for _,w in staged.FIELDS),
        input_radius=5,clock_partition_boundaries=ages,address_partition_boundaries=addresses,
        clock_classes=len(ages)-1,address_classes=len(addresses)-1,
        symbolic_logical_bits_per_class=15*sum(w for _,w in staged.FIELDS),
        output_route_equalities=equalities,rest_route_equalities=rest_equalities,
        exact_two_fault_majority_cofactors=majority_cases,gather_coordinates=gathers,
        courier_left_load_computed_age=staged.LEFT_COURIER,
        courier_right_load_computed_age=staged.RIGHT_COURIER,
        flag_delivery_computed_age=staged.FLAG_AGE,stage_partition_checked=True,
        all_clock_address_route_classes_proved=True,noiseless_rest_stuttering_proved_conditionally=True,
        three_separate_snapshots_and_stage5_vote_proved=True,
        selective_tracked_field_resets_proved=True,
        two_fault_copy_transparency_proved_conditionally=True,
        native_control_premise='Every physical holder receives the correct computedAddress, common computedAge, computedFlag1 and native wipe for the compared trajectory.',
        copy_transparency_input_premise='Before arbitrary replacements at at most two physical sites, each logical simulation bit has five identical physical copies; computed controls are unchanged by those replacements.',
        courier_premise='A separately verified early programme must put its Flag2/Flag1 in coherent Hold at LO/HI−1 before the respective load clocks.',
        commit_premise='A separately verified fifth-stage programme must populate coherent Hold with the final upper state before120Q.',
        tracked_only=True,interpreter_front_fields_included=False,
        actual_interpreter_or_own_programme_verified=False,computed_SimBit_Workspace_refinement_verified=False,
        full_physical_E0_lift_proved=False,physical_self_simulation_proved=False,
        iid_reliability_proved=False,global_reliability_established=False,
        primitive_sha256=digest(staged.__file__),specification_sha256=digest(spec.__file__),
        checker_sha256=digest(__file__),netlist_library_sha256=digest(ROOT/'gacsca/netlist.py'),
        gray_text_sha256=digest(ROOT/'papers_txt/gray_readers_guide.txt'),
        elapsed_seconds=time.monotonic()-started)
    (out/'gray_staged_transport_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('clock_classes','address_classes','output_route_equalities',
        'rest_route_equalities','exact_two_fault_majority_cofactors','all_clock_address_route_classes_proved',
        'full_physical_E0_lift_proved','elapsed_seconds')}),flush=True)


if __name__=='__main__':
    main()
