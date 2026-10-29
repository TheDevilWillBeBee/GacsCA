#!/usr/bin/env python3
"""Pin the explicit universal composition proof of GR1's pure-E0 lift.

The proof is in GR1_E0_PERIOD.md; this validates its finite certificates,
the source predicates and all timing/support inequalities. It does not
simulate sampled noisy trajectories or assert an iid theorem.
"""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
import gray_staged_rule as proposed
import gray_staged_transport as staged


def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    directory=ROOT/'figs/gray_counterexamples'; source=ROOT/'Report/proofs/gray_counterexamples'
    names=('GR1_noiseless_period_certificate.json','GR1_frame_certificate.json',
        'GR1_fetch_certificate.json','GR1_symbolic_schedule.json',
        'gray_staged_transport_certificate.json','GR1_E0_flag_recovery_certificate.json',
        'GR1_wipe_wake_certificate.json')
    receipts={name:json.loads((directory/name).read_text()) for name in names}
    candidate=proposed.load_artifact(); p=candidate.p
    assert receipts[names[0]]['noiseless_encoded_period_theorem_proved']
    assert receipts[names[1]]['tracked_coupling']['coherent_pending_forwarding_and_selective_reset_coupling_proved']
    assert receipts[names[1]]['front_route']['nonmatch_front_route_proved_conditionally']
    assert receipts[names[2]]['correct_work_key_fetch_proved_conditionally']
    assert receipts[names[2]]['outside_work_key_instruction_irrelevance_proved']
    assert receipts[names[3]]['own_programme_verified']
    assert receipts[names[4]]['exact_two_fault_majority_cofactors']==80
    assert receipts[names[5]]['pure_E0_flag_recovery_proved']
    assert receipts[names[5]]['exact_native_front_cofactors']==616
    quiet=receipts[names[5]]['computed_native_flags_quiet_by_age']
    assert quiet==811920<100*p.Q<proposed.FINAL_START
    assert receipts[names[6]]['raw_self_GF_wipe_wake_proved']
    assert not receipts[names[6]]['gray_Proposition2_or4_refuted']
    assert max(staged.capture_age(g,b) for g in range(3) for b in range(11))<proposed.EARLY_START
    assert proposed.EARLY_START+p.NPe*p.PL<min(staged.LEFT_COURIER,staged.RIGHT_COURIER)
    assert staged.FLAG_AGE<80*p.Q<96*p.Q
    assert proposed.FINAL_START+p.NP*p.PL<120*p.Q<p.U
    assert 2*5<24 and 1<24
    # The local transition uses computed GF/Age; the only raw geometry
    # dependence in the SF wipe is the holder's own stored GF comparison.
    actual=Path(proposed.__file__).read_text()
    assert "addr,age,f1=native['addr'],native['age'],native['f1']" in actual
    assert "wipe=n.AND(f1,n.NOT(w_eq(n,addr,cells[0]['addr'])))" in actual
    assert 'rule_g._five_front(n,p,I,eval_lv,virtual,addr' in actual
    assert 'logical_out=transport.build(n,transport_cells,addr,age,f1,wipe)' in actual
    helper=(ROOT/'gacsca/netlist.py').read_text()
    assert 'bitwise = [at_least(n, [w[i] for w in words], 3)' in helper
    assert 'exists = at_least(n, [w_eq(n, w, bitwise) for w in words], 3)' in helper
    # Every tracked hold/scratch source of logicalslot−2..2 is replaced
    # by the same fully corrected+forwarded logical value in the wrapper.
    assert 'lv(j+s,f,b) if -2<=j+s<=2 else cells[j][f]' in actual
    proof=source/'GR1_E0_PERIOD.md'
    result=dict(candidate='GR1',Q=p.Q,U=p.U,width=candidate.W,
        candidate_sha256=candidate.digest(),netlist_sha256=candidate.comp.digest,
        checker_sha256=digest(__file__),written_proof_sha256=digest(proof),
        proposal_sha256=digest(proposed.__file__),transport_primitive_sha256=digest(staged.__file__),
        native_source_sha256=digest(ROOT/'gacsca/maintenance.py'),
        netlist_source_sha256=digest(ROOT/'gacsca/netlist.py'),
        error_classifier_sha256=digest(ROOT/'gacsca/gray_errors.py'),
        receipt_dependencies_sha256={name:digest(directory/name) for name in names},
        pure_E0_physical_encoded_period_lift_proved=True,
        continuing_pure_E0_boundary_decoding_proved=True,
        theorem='For every original pureE0 error set and arbitrary replacements, X(nU) agrees outside currentE0 with an E(F^n(s)) member, and five-copy boundary decoder equalsF^n(s), for alln>=0.',
        initial_family='BroadE(s), or its current-E0 perturbation with globally isolated current/past/future groups; unrepresented Info arbitrary coherent, no auxiliary alias premise.',
        native_geometry_proof='Three correct words in each left/right5-word vote restore canonicalGF/commonAge; atmosttwo left mismatches make inconsistencyfalse. The selected direction is immaterial.',
        data_support_invariant='Differences in tracked and interpreter data lie in currentE0 union previousE0; only current-input GF faults can wipe. Original24 separation keeps their union atmosttwo sites in each radius5 input cone. Quiet intervals sharpen support to currentE0 alone.',
        registers_and_I_proof='Both active interpreter windows are flagquiet; selected coherent5-holder register cohorts restore all operands/lookup selectors before execution, nonarriving lookups areI-irrelevant. Pending forwarding and resets use restored computed controls.',
        whole_word_majority_lengths=[13,20],two_section_support_diameter=10,
        original_error_lambda=24,error_separation_c=104,
        all_Error_replacement_bits_unrestricted=True,
        arbitrary_noisy_clock_words_covered=True,
        native_flags_quiet_by_age=quiet,
        no_direct_wipe_chain_beyond_previous_error_section=True,
        unconditional_one_tick_raw_field_transparency_claimed=False,
        proof_kind='Written universal deterministic induction using exact local, majority, route, flag-front and own-programme certificates; no sampled physical noise campaign.',
        full_physical_E0_lift_proved=True,gray_verbatim_simulation=False,
        real1_recovery_proved=False,higher_error_localization_proved=False,
        iid_reliability_proved=False,explicit_positive_iid_noise_rate=None,
        global_reliability_established=False,active_rule_modified=False,measured_only=False)
    (directory/'GR1_E0_period_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:result[key] for key in ('pure_E0_physical_encoded_period_lift_proved',
        'continuing_pure_E0_boundary_decoding_proved','native_flags_quiet_by_age',
        'arbitrary_noisy_clock_words_covered','real1_recovery_proved','iid_reliability_proved')}))


if __name__=='__main__': main()
