#!/usr/bin/env python3
"""J117: SP18 own-rule incorporation and complete-encoding E0 premises.

Pin the exact J116 native transition, own ROM, universal schedule, unchanged
physical data equations at a common native-controller cut and actual commit
identities. The full encoding induction is in ROBUSTNESS. No iid threshold.
"""
from dataclasses import asdict
from pathlib import Path
from types import FunctionType
import hashlib
import json
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,Compiled
import check_commit_reset448_incorporation as reset
import proposed_sparse_epoch448 as proposed

PACKET_FIELDS={'wf2','packet_valid','packet_tag','packet_count'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def common_controller_cut(n,p):
    def controller(net,*args,**kwargs):
        return dict(addr=[net.input(('proof_same_controller','GF',b)) for b in range(p.k)],
            age_now=[net.input(('proof_same_controller','Age_now',b)) for b in range(p.m)],
            age=[net.input(('proof_same_controller','Age_next',b)) for b in range(p.m)],
            f1=net.input(('proof_same_controller','Flag1')),f2=net.input(('proof_same_controller','Flag2')))
    old,_=proposed.previous.full_net(p,net_class=lambda:n,maintenance=controller)
    before=dict(old.outputs)
    n.outputs={}
    new,_=proposed.full_net(p,net_class=lambda:n,maintenance=controller)
    assert set(before) == set(new.outputs)
    identical=packet=0
    for key,node in before.items():
        if key[0] == 'y' and key[1] in PACKET_FIELDS:
            packet += 1
        else:
            assert new.outputs[key] == node,key
            identical += 1
    assert (identical,packet) == (319,17)
    return identical,packet


def encoding_arithmetic(p):
    primaries=set(proposed.layout(p).tolist())|{p.lo,p.hi-1}
    assert primaries == set(range(p.lo,p.lo+317))|{p.hi-1}
    allowed=0
    for phase in range(p.Q):
        for slot in range(-2,3):
            primary=(phase+slot)%p.Q
            if primary in primaries:
                assert 0 <= phase+slot < p.Q
                allowed += 1
    assert (len(primaries),allowed,p.Q*5-allowed) == (318,1590,650)
    assert min(primaries)-2 >= 0 and max(primaries)+2 < p.Q
    assert p.T_wf+1150 == 30015 < p.T_wf+1792 == 30657 < p.U-1
    assert p.T_wf+1793 == 30658 < p.E0+p.NP*p.PL == 56320 < p.U-1 == 67583
    return dict(allowed_Info_primaries=318,Info_phase_slot_checks=p.Q*5,
        allowed_Info_copy_slots=allowed,unused_Info_copy_slots_zero=p.Q*5-allowed,
        unconditional_canonical_source_birth_clock=p.T_wf+1,
        Workspace1_source_free_clock=p.T_wf+898,
        all_C_Flag1_quiet_E0_clock=p.T_wf+1150,
        last_active_proper_packet_clock=p.T_wf+1792,
        all_packet_code_components_computed_empty_clock=p.T_wf+1793,
        evaluation_end_input_clock=p.E0+p.NP*p.PL,commit_input_clock=p.U-1)


def main():
    candidate=proposed.load_artifact()
    p=candidate.p
    assert asdict(p) == asdict(proposed.previous.parameters()) == asdict(proposed.starter.parameters())
    n,source=proposed.actual_net(p)
    assert Compiled(n).digest == candidate.comp.digest
    out=ROOT/'figs/robustness'
    epoch=json.loads((out/'right_epoch_starter_certificate.json').read_text())
    assert candidate.comp.digest == epoch['module_raw_netlist_sha256']
    assert hashlib.sha256(source.encode()).hexdigest() == epoch['module_generated_source_sha256']
    assert proposed.proposed_build()[1] == proposed.previous.proposed_build()[1]
    identical,packet=common_controller_cut(Net(),p)
    commit=FunctionType(reset.commit_identities.__code__,dict(reset.__dict__,proposed=proposed),
        reset.commit_identities.__name__,reset.commit_identities.__defaults__)
    zeros,info=commit(p)
    assert (zeros,info) == (283,5)
    schedule=json.loads((out/'SP18_symbolic_schedule.json').read_text())
    build=json.loads((out/'SP18_program_build.json').read_text())
    assert schedule['proposed_candidate_sha256'] == build['proposed_candidate_sha256'] == candidate.digest()
    assert (schedule['key_equalities'],schedule['early_flag_equalities'],schedule['final_hold_equalities'],
            schedule['history_ranks_checked']) == (19,2,316,12)
    assert schedule['counts']['hold_writes'] == 318
    assert max(schedule['early_flag_store_ages'].values()) < min(p.courier_ticks()[1:])
    assert (build['gates'],build['instructions'],build['usage']) == (34607,45341,dict(NPe=47,MP=73,NP=111,MP_min=65))
    assert build['build_complete'] and build['random_replay_mismatches'] == 0
    dependencies={key:digest(out/name) for key,name in (
        ('build_receipt_sha256','SP18_program_build.json'),
        ('programme_receipt_sha256','SP18_symbolic_schedule.json'),
        ('front_receipt_sha256','SP18_front_certificate.json'),
        ('epoch_starter_receipt_sha256','right_epoch_starter_certificate.json'),
        ('SP17_incorporation_receipt_sha256','SP17_incorporation_encoded_certificate.json'),
        ('SP16_quiet_native_receipt_sha256','SP16_quiet_region_certificate.json'),
        ('SP16_period_native_receipt_sha256','SP16_period_barrier_certificate.json'),
        ('SP16_encoded_receipt_sha256','SP16_encoded_certificate.json'),
        ('buffered_service_receipt_sha256','buffered_framed_service_certificate.json'))}
    receipt=dict(proposal='SP18',proposed_rule_change=True,active_G17_modified=False,
        SP17_modified=False,SP16_modified=False,SP15_modified=False,
        Q=p.Q,U=p.U,width=candidate.W,radius=12,
        proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        checker_sha256=digest(Path(__file__)),proposal_source_sha256=digest(Path(proposed.__file__)),
        epoch_source_sha256=digest(Path(proposed.starter.__file__)),
        base_SP17_proposal_source_sha256=digest(Path(proposed.previous.__file__)),
        helpers_sha256=digest(ROOT/'gacsca/netlist.py'),
        commit_checker_sha256=digest(Path(reset.__file__)),
        actual_maintenance_source_sha256=hashlib.sha256(proposed.proposed_build()[1].encode()).hexdigest(),
        full_generated_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        buffered_service_source_sha256=digest(Path(proposed.service.__file__)),
        **dependencies,**encoding_arithmetic(p),
        full_parameters_identical_to_J116_module=True,
        full_raw_transition_netlist_and_generated_source_identical_to_J116_module=True,
        common_native_controller_cut_all_nonpacket_literal_output_equalities=identical,
        common_native_controller_cut_replaced_packet_output_bits=packet,
        literal_commit_native_Flag2_component_and_workspace_zero_bits=zeros,
        literal_commit_forwarded_Hold_Info_mask_identities=info,
        all_J116_native_proofs_allow_arbitrary_I_and_apply_to_own_ROM=True,
        native_GF_Age_global_canonical_two_mode_induction_allows_arbitrary_pressure=True,
        canonical_birth_unconditional_in_every_colony_and_closed_at_all_other_clocks=True,
        common_count_packet_and_code_erasure_allows_overlapping_frames=True,
        native_Flag1_quiet_before_commit_from_unchanged_suffix_proof=True,
        native_Flag2_quiet_before_commit_not_required=True,
        healthy_physical_copy_capture_gather_front_match_induction_transfers_J105=True,
        all316_upper_outputs_and_two_flag_duplicates_are_of_changed_own_rule=True,
        complete_initial_encoding_and_global_E0_required_for_encoding_theorem=True,
        full_boundary_encoding_identity_before_current_overwrites=True,
        raw_boundary_five_copy_decoder_exact_under_current_E0=True,
        complete_encoded_noiseless_and_all_period_E0_simulation_proved=True,
        intact_noiseless_infinite_hierarchy_exists=True,
        J116_all_time_native_halfline_arbitrary_other_fields_theorem_for_actual_own_rule=True,
        general_GF_Age_damaged_seed_reconstruction_or_upper_error_map_established=False,
        iid_threshold_established=False,minimal_sufficient_global_reliability_change_established=False,
        global_reliability_established=False,
        scope='ROBUSTNESS J117: separate SP18 with universally verified own ROM; complete noiseless/E0 encoding closure and J116 native theorem transfer; no general GF/Age damaged-seed recovery, full upper map or iid threshold')
    (out/'SP18_incorporation_encoded_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(candidate=candidate.digest(),netlist=candidate.comp.digest,
        own_programme=True,nonpacket_equalities=identical,commit_zeros=zeros,
        complete_encoded_E0_only_simulation=True,global_reliability_established=False)),flush=True)


if __name__ == '__main__':
    main()
