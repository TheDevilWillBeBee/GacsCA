#!/usr/bin/env python3
"""J114: SP17 full-rule reset identities, canonical births and E0 premises.

The complete encoding induction is written in ROBUSTNESS. This checker
pins the new own ROM and full Boolean equations. It supplies no general
damaged-input repair, hierarchy error map or positive iid threshold.
"""
from itertools import combinations
from pathlib import Path
from types import FunctionType
import hashlib
import json
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,Compiled,const_word,w_eq_const,w_eq,w_in_range,w_add_const_mod
from check_g17_schedule import Terms
from check_buffered448_command import forwarded_hold
from check_buffered448_period_barrier import RESET_FIELDS
import check_buffered448_incorporation as old_checker
import proposed_sparse_commit_reset448 as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def maintenance_nodes(n,p):
    read=lambda j,f,b: n.input(('x',j,f,b))
    service=proposed.service.build(n,{j:dict(packet_tag=[read(j,'packet_tag',b) for b in range(4)],
        packet_valid=read(j,'packet_valid',0),packet_count=[read(j,'packet_count',b) for b in range(11)],
        wf2=read(j,'wf2',0),flag_valid=read(j,'service_valid',0),
        flag_position=[read(j,'service_position',b) for b in range(9)],
        flag_count=[read(j,'service_count',b) for b in range(11)]) for j in range(-5,6)})
    cells={j:dict(addr=[read(j,'addr',b) for b in range(p.k)],age=[read(j,'age',b) for b in range(p.m)],
        **{f:read(j,f,0) for f in ('f1','f2','wf1','wf2')}) for j in range(-12,13)}
    return proposed.proposed_build()[0](n,cells,p.k,p.m,Q=p.Q,nb=p.nb,radix=p.R,pos_bits=p.PB,
        service_force=service['service_force'])


def normalized(n):
    terms=Terms()
    names={node:key for key,node in n.input_node.items()}
    value=[0,1]
    for node in range(2,len(n.kind)):
        if n.kind[node] == 'IN':
            value.append(terms.var(names[node]))
        else:
            op,a,b=n.gate[node]
            value.append(terms.op(op,value[a],value[b]))
    return value


def full_output_identities(p):
    shared=Net()
    old,old_source=old_checker.full_net(p,net_class=lambda:shared)
    old_outputs=dict(old.outputs)
    shared.outputs={}
    new,new_source=proposed.full_net(p,net_class=lambda:shared)
    assert set(new.outputs) == set(old_outputs)
    mt=maintenance_nodes(shared,p)
    commit=w_eq_const(shared,mt['age_now'],p.age_code(p.U-1))
    expected={}
    unchanged=reset=info=0
    for key,node in old_outputs.items():
        if key[0] == 'y' and key[1] in proposed.COMMIT_RESET_FIELDS:
            expected[key]=shared.AND(node,shared.NOT(commit))
            reset += 1
        elif key[0] == 'y' and key[1] == 'info':
            slot=key[2]-2
            address=w_add_const_mod(shared,mt['addr'],slot%p.Q,p.Q)
            allowed=shared.OR(w_in_range(shared,address,p.lo,p.lo+proposed.width(p)+1),
                w_eq_const(shared,address,p.hi-1))
            mask=shared.OR(shared.NOT(commit),allowed)
            expected[key]=shared.AND(node,mask)
            info += 1
        else:
            expected[key]=node
            assert new.outputs[key] == node,key
            unchanged += 1
    values=normalized(shared)
    for key,node in expected.items():
        assert values[new.outputs[key]] == values[node],key
    assert (unchanged,reset,info) == (292,39,5),(unchanged,reset,info,len(old_outputs))
    return unchanged,reset,info,hashlib.sha256(old_source.encode()).hexdigest(),hashlib.sha256(new_source.encode()).hexdigest()


def commit_identities(p):
    def controller(n,*args,**kwargs):
        return dict(addr=[n.input(('proof','free_computed_GF',b)) for b in range(p.k)],
            age_now=const_word(p.age_code(p.U-1),p.m),age=const_word(0,p.m),
            f1=n.input(('proof','free_computed_F1')),f2=n.input(('proof','free_computed_F2')))
    n,_=proposed.full_net(p,maintenance=controller)
    zeros=0
    for field,width in proposed.schema(p):
        if field in (*RESET_FIELDS,*proposed.COMMIT_RESET_FIELDS):
            for bit in range(width):
                assert n.outputs['y',field,bit] == 0,(field,bit)
                zeros += 1
    assert zeros == 283 and n.outputs['y','wf1',0] == 0
    gf=[n.input(('proof','free_computed_GF',b)) for b in range(p.k)]
    raw=[n.input(('x',0,'addr',b)) for b in range(p.k)]
    keep=n.NOT(n.AND(n.input(('proof','free_computed_F1')),n.NOT(w_eq(n,gf,raw))))
    expected={}
    for slot in range(-2,3):
        address=w_add_const_mod(n,gf,slot%p.Q,p.Q)
        allowed=n.OR(w_in_range(n,address,p.lo,p.lo+proposed.width(p)+1),w_eq_const(n,address,p.hi-1))
        expected[slot]=n.AND(keep,n.AND(allowed,forwarded_hold(n,p,0,slot)))
    values=normalized(n)
    for slot,node in expected.items():
        assert values[n.outputs['y','info',slot+2]] == values[node],slot
    return zeros,5


def encoding_arithmetic(p):
    primaries=set(proposed.layout(p).tolist()) | {p.lo,p.hi-1}
    assert primaries == set(range(p.lo,p.lo+proposed.width(p)+1)) | {p.hi-1}
    assert len(primaries) == 318
    checks=allowed_count=0
    for phase in range(p.Q):
        for slot in range(-2,3):
            address=(phase+slot)%p.Q
            allowed=address in primaries
            if allowed:
                assert 0 <= phase+slot < p.Q
                allowed_count += 1
            else:
                assert phase+slot not in primaries
            checks += 1
    assert (checks,allowed_count) == (2240,1590)
    assert min(primaries)-2 >= 0 and max(primaries)+2 < p.Q
    source1_free=p.T_wf+2*p.Q+1
    source2_free=p.T_wf+1793
    clean_F1=source1_free+224
    clean_flags=max(clean_F1,source2_free)+224
    E0_F1=source1_free+252
    E0_flags=max(E0_F1,source2_free)+247
    assert (p.T_sig,p.T_wf,source1_free,source2_free,clean_flags,E0_flags) == (28864,28865,29762,30658,30882,30905)
    assert E0_flags < p.E0+p.NP*p.PL == 56320 < p.U-1 == 67583
    assert source2_free < p.U-1
    return dict(allowed_Info_primaries=len(primaries),Info_primary_mask_phase_slot_checks=checks,
        allowed_physical_Info_copy_slots=allowed_count,unrepresented_Info_copy_slots_zero=checks-allowed_count,
        T_sig=p.T_sig,T_wf=p.T_wf,Workspace1_source_free_clock=source1_free,
        all_components_computed_empty_by_clock=source2_free,
        all_computed_structural_flags_quiet_clean_clock=clean_flags,
        all_computed_structural_flags_quiet_E0_clock=E0_flags,
        evaluation_end_input_clock=p.E0+p.NP*p.PL,commit_input_clock=p.U-1)


def main():
    candidate=proposed.load_artifact()
    p=candidate.p
    n,_=proposed.full_net(p)
    assert Compiled(n).digest == candidate.comp.digest
    unchanged,reset,info,old_source,new_source=full_output_identities(p)
    zeros,commit_info=commit_identities(p)
    arithmetic=encoding_arithmetic(p)
    birth=FunctionType(old_checker.canonical_birth.__code__,
        dict(old_checker.__dict__,full_net=proposed.full_net,proposed=proposed),
        old_checker.canonical_birth.__name__,old_checker.canonical_birth.__defaults__)
    birth_cases=0
    for address in range(1,6):
        for faults in combinations(range(-6,7),2):
            birth(p,address,faults)
            birth_cases += 1
        print(json.dumps(dict(canonical_birth_cases=birth_cases)),flush=True)
    assert birth_cases == 390
    out=ROOT/'figs/robustness'
    schedule=json.loads((out/'SP17_symbolic_schedule.json').read_text())
    build=json.loads((out/'SP17_program_build.json').read_text())
    assert (schedule['final_hold_equalities'],schedule['history_ranks_checked']) == (316,12)
    assert max(schedule['early_flag_store_ages'].values()) < min(p.courier_ticks()[1:])
    assert build['build_complete'] and build['random_replay_mismatches'] == 0
    receipt=dict(proposal='SP17',proposed_rule_change=True,active_G17_modified=False,
        SP16_modified=False,SP15_modified=False,Q=p.Q,U=p.U,width=candidate.W,radius=12,
        proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        checker_sha256=digest(Path(__file__)),proposal_source_sha256=digest(Path(proposed.__file__)),
        helpers_sha256=digest(ROOT/'gacsca/netlist.py'),base_rule_source_sha256=digest(ROOT/'gacsca/rule_g.py'),
        SP16_proposal_source_sha256=digest(Path(proposed.previous.__file__)),
        full_rule_checker_sha256=digest(Path(old_checker.__file__)),
        algebra_checker_sha256=digest(ROOT/'Report/proofs/check_g17_schedule.py'),
        forwarded_Hold_helper_sha256=digest(ROOT/'Report/proofs/check_buffered448_command.py'),
        work_reset_helper_sha256=digest(ROOT/'Report/proofs/check_buffered448_period_barrier.py'),
        actual_maintenance_source_sha256=hashlib.sha256(proposed.proposed_build()[1].encode()).hexdigest(),
        buffered_service_source_sha256=digest(Path(proposed.service.__file__)),
        SP16_generated_source_with_SP17_params_sha256=old_source,full_generated_source_sha256=new_source,
        build_receipt_sha256=digest(out/'SP17_program_build.json'),
        programme_receipt_sha256=digest(out/'SP17_symbolic_schedule.json'),
        front_receipt_sha256=digest(out/'SP17_front_certificate.json'),
        SP16_encoding_receipt_sha256=digest(out/'SP16_encoded_certificate.json'),
        guard6_receipt_sha256=digest(out/'packet_guard6_certificate.json'),
        packet_pressure_receipt_sha256=digest(out/'packet_pressure_certificate.json'),
        buffered_service_receipt_sha256=digest(out/'buffered_framed_service_certificate.json'),
        full_unrestricted_output_equalities_unchanged=unchanged,
        full_unrestricted_component_Flag2_output_mask_identities=reset,
        full_unrestricted_Info_output_mask_identities=info,
        literal_commit_workspace_native_Flag2_and_component_zero_bits=zeros,
        literal_commit_Info_forwarded_Hold_allowed_primary_identities=commit_info,
        commit_reset_fields=list(proposed.COMMIT_RESET_FIELDS),
        canonical_thirteen_site_two_fault_birth_cofactors=birth_cases,**arithmetic,
        shared_net_normalization_uses_only_sound_Boolean_identities=True,
        all_full_outputs_unchanged_off_computed_commit_clock=True,
        no_added_raw_state_or_input_offset=True,
        conditional_commit_component_Flag2_and_Info_margin_reset_unrestricted_raw_fields=True,
        correct_commit_controllers_required_for_conditional_reset=True,
        full_native_Flag1_reset_not_added=True,
        native_canonical_GF_Age_preservation_induction_transfers_J105=True,
        canonical_source_count_erasure_overlap_proof_transfers_J105=True,
        healthy_twelve_rank_copy_gather_and_match_induction_transfers_J105=True,
        changed_own_programme_all316_outputs_used=True,
        complete_initial_encoding_and_global_E0_required_for_complete_encoding_theorem=True,
        boundary_full_word_identity_before_current_overwrites=True,
        complete_encoded_noiseless_and_E0_only_simulation_proved=True,
        noiseless_intact_infinite_hierarchy_closure=True,
        J112_halfline_valid_seed_complete_boundary_extension_proved_by_this_checker=False,
        general_damaged_seed_recovery_full_upper_map_or_iid_threshold_established=False,
        minimal_sufficient_global_reliability_change_established=False,
        global_reliability_established=False,
        scope='ROBUSTNESS J114: separate SP17 own-ROM and complete initial encoding E0 closure, plus full-rule commit reset identities; halfline damaged-seed extension, all-level error map and iid threshold unproved')
    (out/'SP17_incorporation_encoded_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(unchanged=unchanged,reset_outputs=reset,Info_masks=info,
        commit_zero_bits=zeros,birth_cofactors=birth_cases,**arithmetic,global_reliability_established=False)),flush=True)


if __name__ == '__main__':
    main()
