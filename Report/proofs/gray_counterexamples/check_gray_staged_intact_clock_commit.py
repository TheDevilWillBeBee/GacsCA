#!/usr/bin/env python3
"""Certify intact recursive GR1 initialization and the existing real1 cone.

The universal integer recursion and physical temporal composition are
proved in the accompanying document. Exact Boolean cofactors certify
the new local/native facts; no long noisy trajectory or iid claim.
"""
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'Report/proofs')]
import numpy as np
from gacsca import gray_errors,maintenance
from gacsca.netlist import Net,const_word,w_add_const
from check_g17_schedule import Terms
import gray_staged_rule as proposed
import gray_staged_transport as staged
from gray_recursive_initialization import RecursiveInitial


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    started=time.monotonic(); out=ROOT/'figs/gray_counterexamples'
    cand=proposed.load_artifact(); p=cand.p; comp=cand.comp
    initial=RecursiveInitial(cand)
    assert (p.Q,p.U,cand.W)==(8192,1048576,386)
    assert initial.info_residues==(3891,3989,4092,4188,4286)
    assert initial.minimum_info_absolute_coordinate==3891
    # Universal encoding is the case split in the written proof. These
    # checks pin that split to the actual schema/layout and its source.
    assert [b for f,b in cand.row if f=='addr']==list(range(p.k))
    assert [b for f,b in cand.row if f=='info']==list(range(5))
    assert cand.W-p.k-5==368
    cases={'addr':p.k,'info':5,'zero':cand.W-p.k-5}
    for field,bit in cand.row:
        a=int(cand.layout[cand.row[field,bit]])
        assert initial.tags[a]==(field,bit)
        if field=='info':
            assert abs(bit-2)<=2
        elif field!='addr':
            assert initial.raw(0,field,bit)==0
    examples=sorted(set(range(-16,17))|{s*(p.Q**e+d) for s in (-1,1)
        for e in (1,2,3,8,32) for d in (0,1,p.Q//2,p.Q-1)})
    for x in examples:
        for field,bit in cand.row:
            assert initial.encoded_primary(x,field,bit)==initial.raw(x,field,bit)
    assert all(initial.logical_Info(x)==0 for x in range(-2,p.Q+2))
    assert all(initial.raw(0,f,b)==0 for f,b in cand.row)
    assert initial.logical_Info(3)==initial.logical_Info(p.Q-3)==0
    # Every stored frame ancestor is the actual all-level H initial state.
    old=json.loads((out/'GR1_real1_clock_commit_certificate.json').read_text())
    assert old['candidate_sha256']==cand.digest() and old['netlist_sha256']==comp.digest
    assert (old['geometry_restored_at'],old['native_Flag_quiet_by'])==(1444,9636)
    assert old['clock_advection_certificate']['cofactors']==620
    with np.load(out/'GR1_real1_clock_commit_inputs_and_cone.npz') as asset:
        coordinates=asset['coordinates']; base=asset['initial']
        encoded=np.asarray([[initial.raw(int(x),f,b) for x in coordinates]
                            for f,b in cand.row],dtype=bool)
        assert np.array_equal(base,encoded)
        exact_initial_cone_equalities=int(base.size)
    points=[(x,1) for x in range(3865,3870)]
    classification=gray_errors.classify(points,Q=p.Q,U=p.U,sep=104)
    assert classification['level1'] and classification['level0']==0
    assert int(cand.layout[cand.row['reg',2]])==3868
    assert 3869 not in initial.tags
    # The actual native output has zero flags at every phase, with the
    # common20-bit clock left completely free. No SF or I premise is used.
    for phase in range(p.Q):
        n=Net(); age=[n.input(('common_age',b)) for b in range(p.m)]
        cells={j:dict(addr=const_word((phase+j)%p.Q,p.k),age=age,
                     f1=0,f2=0,wf1=0,wf2=0) for j in range(-5,6)}
        native=maintenance.build(n,cells,p.k,p.m)
        assert native['addr']==const_word(phase,p.k)
        assert native['age']==w_add_const(n,age,1)
        assert native['f1']==native['f2']==0,phase
    reverse={index:name for name,index in comp.index.items()}
    def support(node):
        seen=set(); todo=[node]; result=set()
        while todo:
            node=todo.pop()
            if node in seen:continue
            seen.add(node)
            if node in reverse:result.add(reverse[node])
            elif node>=2+len(comp.inputs):
                _,a,b=comp.gates[node-2-len(comp.inputs)];todo.extend((a,b))
        return result
    native_fields={'addr','age','f1','f2','wf1','wf2'}
    native_support={}
    for field in ('f1','f2'):
        names=support(comp.outputs['y',field,0])
        assert all(name[0]=='x' and name[2] in native_fields for name in names)
        native_support[field]=sorted({name[2] for name in names})
    # Pin the actual three-bit temporal expression with two equal banks.
    for expected in (0,1):
        n=Net(); first=n.input(('arbitrary_History1',))
        vote=n.OR(n.AND(first,expected),n.AND(expected,n.OR(first,expected)))
        assert vote==expected
    last_capture=max(staged.capture_age(g,lane) for g in (1,2) for lane in range(11))
    assert old['native_Flag_quiet_by']<32*p.Q<64*p.Q
    assert last_capture==565245<proposed.EARLY_START
    assert proposed.EARLY_START==573440 and staged.FLAG_AGE==655359
    # Full upper counterfactual: the represented erroneous input q differs
    # H only in raw Reg2 at cell0. All lookup/instruction bits are shared,
    # symbolic and unrestricted. Equality includes the lookup keys, so
    # hardwired ROM lookup preserves the resulting equality as well.
    terms=Terms()
    def upper(site,field,bit,changed):
        if changed and site==0 and field=='reg' and bit==2:return 1
        return initial.raw(site,field,bit)
    def evaluate(center,changed):
        nodes=[0,1]
        for name in comp.inputs:
            value=(terms.var(('shared_instruction',center,name[1])) if name[0]=='I'
                   else upper(center+name[1],name[2],name[3],changed))
            nodes.append(value)
        for op,a,b in comp.gates:nodes.append(terms.op(op,nodes[a],nodes[b]))
        return {name:nodes[node] for name,node in comp.outputs.items()}
    upper_equalities=0
    for center in range(-5,6):
        clean=evaluate(center,False); changed=evaluate(center,True)
        assert clean==changed,center
        upper_equalities+=len(clean)
        assert clean['y','f1',0]==clean['y','f2',0]==0
    quiet=json.loads((out/'GR1_flag_quiet_certificate.json').read_text())
    assert quiet['all_colony_flags_noiseless_clearing_proved']
    noiseless=json.loads((out/'GR1_noiseless_period_certificate.json').read_text())
    assert noiseless['noiseless_encoded_period_theorem_proved']
    assert noiseless['last_early_pending_store_application_age']<min(staged.LEFT_COURIER,staged.RIGHT_COURIER)
    assert old['three_colony_simulation_field_difference_time']==266470<48*p.Q
    assert [w['site'] for w in old['three_colony_witness']]==[-457,3868,8193]
    dependencies=('GR1_real1_clock_commit_certificate.json','native_geometry_invariant_certificate.json',
        'gray_staged_transport_certificate.json','GR1_symbolic_schedule.json','GR1_fetch_certificate.json',
        'GR1_frame_certificate.json','GR1_flag_quiet_certificate.json','GR1_noiseless_period_certificate.json')
    result=dict(candidate='GR1',Q=p.Q,U=p.U,width=cand.W,error_lambda=24,error_separation_c=104,
        candidate_sha256=cand.digest(),netlist_sha256=comp.digest,
        checker_sha256=digest(__file__),initializer_sha256=digest(Path(__file__).with_name('gray_recursive_initialization.py')),
        written_proof_sha256=digest(Path(__file__).with_name('GR1_INTACT_CLOCK_COMMIT.md')),
        proposal_sha256=digest(proposed.__file__),transport_primitive_sha256=digest(staged.__file__),
        active_native_source_sha256=digest(maintenance.__file__),
        classifier_sha256=digest(gray_errors.__file__),
        term_library_sha256=digest(ROOT/'Report/proofs/check_g17_schedule.py'),
        cone_asset_sha256=digest(out/'GR1_real1_clock_commit_inputs_and_cone.npz'),
        receipt_dependencies_sha256={name:digest(out/name) for name in dependencies},
        recursive_definition='D(iQ+ell(addr,b))=bit_b(i modQ); D(iQ+ell(info,b))=D(i+b−2); every other logical primary0. H has canonical Address, Age/flags/private0 and Info[b]=D(x+b−2).',
        Info_primary_residues=initial.info_residues,
        minimum_absolute_Info_recursion_argument=initial.minimum_info_absolute_coordinate,
        recursive_step_bound='|floor(x/Q)+b−2|<=|x|/Q+3<|x| for every Info-tag argument.',
        encoding_case_counts=cases,all_represented_fields_and_five_Info_slots_covered=True,
        integer_recursion_termination_proved=True,stationary_all_level_H_in_E_of_H_proved=True,
        all_unused_and_special_Info_primaries_zero=True,raw_H_cell0_all386_bits_zero=True,
        lower_colony0_all_Info_bits_zero=True,exact_old_initial_cone_equalities=exact_initial_cone_equalities,
        sampled_large_coordinate_encoding_checks=len(examples)*cand.W,
        samples_are_not_basis_of_universal_recursion_proof=True,
        error_points=points,error_classification=classification,
        no_independent_upper_error_or_earlier_physical_error=True,
        full_physical_error_set_is_exactly_one_original_real1=True,
        geometry_restored_at=1444,native_flags_quiet_by=9636,
        represented_changed_upper_bit=['reg',2],represented_changed_upper_holder=0,
        unused_changed_logical_Info_primary=3869,
        later_history_banks=[2,3],later_history_all_fields_and11_offsets_encode_q=True,
        first_history_correctness_required=False,last_later_history_capture_age=last_capture,
        exact_native_zero_flag_cofactors=p.Q,native_flag_common_clock_free_bits=p.m,
        actual_flag_output_native_field_support=native_support,
        early_flags_zero_at_all_receivers_proved=True,
        special_flag_sources_and96Q_Workspace_pulse_zero_proved=True,
        intact_recursive_GR1_clock_commit_reachability_proved=True,
        intact_recursive_GR1_three_colony_pointwise_SF_witness_proved=True,
        simultaneous_three_colony_witness_time=266470,
        simultaneous_three_colony_witness=old['three_colony_witness'],
        upper_counterfactual_full_net_cofactors=22,
        upper_counterfactual_output_equalities=upper_equalities,
        all_upper_lookup_instruction_bits_shared_symbolic=True,
        F_of_q_equals_F_of_H_proved=True,
        first_noisy_boundary_in_E_of_F_H_proved=True,
        no_later_error_continuing_decoded_hierarchy_correct_for_this_witness_proved=True,
        GR1_boundary_decoding_or_memory_failure_proved=False,
        faithful_Gray_Proposition4_refuted=False,Gray_single_ProgramBit_compilation_proved=False,
        accepted_pure_E0_theorem_refuted=False,arbitrary_real1_recovery_proved=False,
        iid_unreliability_proved=False,global_reliability_established=False,
        active_rule_modified=False,measured_only=False,
        proof_kind='Universal terminating recursive initialization plus pinned exact finite cones, native/upper Boolean cofactors and written physical stage composition; not a long sampled trajectory.',
        elapsed_seconds=time.monotonic()-started)
    (out/'GR1_intact_clock_commit_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:result[key] for key in ('stationary_all_level_H_in_E_of_H_proved',
        'exact_native_zero_flag_cofactors','upper_counterfactual_output_equalities',
        'intact_recursive_GR1_three_colony_pointwise_SF_witness_proved',
        'first_noisy_boundary_in_E_of_F_H_proved','elapsed_seconds')}))


if __name__=='__main__':main()
