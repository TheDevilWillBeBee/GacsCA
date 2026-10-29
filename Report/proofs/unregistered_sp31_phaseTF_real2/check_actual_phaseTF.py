#!/usr/bin/env python3
"""Issue once, then replay the intact-start phase-TF fault without edits."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
OUT=ROOT/'figs/robustness/unregistered_sp31_phaseTF_real2'
PROOF=HERE/'SP31_ACTUAL_PHASE_TF_ALIAS_FAULT.md'
CERT=OUT/'actual_phaseTF_certificate.json'
PARENT=ROOT/'figs/robustness/unregistered_sp31_upper_alias_pulse/prepared_alias_certificate.json'
sys.path.insert(0,str(HERE));import probe_intact_background as probe
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def components(xs,link):
    ans=[]
    for x in sorted(xs):
        if not ans or x-ans[-1][-1]>=link:ans.append([])
        ans[-1].append(x)
    return ans
def support_proof_checks():
    Q=1024;U=475136;TF=278401
    upper=set(range(-15*Q,0))|set(range(1019,1024))
    assert len(upper)==15365 and max(upper)-min(upper)+1==16*Q
    assert len(components(upper,24*Q))==1 and len(upper)>Q
    assert max(upper)-min(upper)<16*Q
    assert {-15*Q+i for i in range(4)}<=upper
    lower=set()
    for x in range(-14*Q-512,0):lower.update(x*Q+68-s for s in range(-2,3))
    for x in (*range(-15*Q,-14*Q-512),*range(-512,0)):
        lower.update(x*Q+88-s for s in range(-2,3))
    for s in range(-2,3):lower.update((1021-s)*Q+94+s-k for k in range(-2,3))
    assert len(lower)==79385
    assert (min(lower),max(lower))==(-15728554,1047646)
    parts=components(lower,24*Q)
    assert len(parts)==2 and all(p[-1]-p[0]+1>Q for p in parts)
    assert parts[1][-1]-parts[1][0]+1==4097
    assert len(components(lower,24*Q*Q))==1
    assert Q*Q<max(lower)-min(lower)+1<=Q**3
    assert max(lower)-min(lower)<16*Q*Q
    a=-15*Q*Q+88
    assert {a+k for k in range(-2,2)}|{a+Q+k for k in range(-2,2)}<=lower
    assert len(probe.level0_points([(x,TF) for x in upper]))==0
    assert len(probe.level0_points([(x,TF*U) for x in lower]))==0
    assert 172*39<14*Q+512
    assert (TF*U+171*U,TF*U+172*U)==(132359585792,132360060928)
    return dict(upper_points=len(upper),upper_width=16*Q,upper_lambdaQ_components=1,
        upper_E0_E1_empty_original_real2=True,lower_points=len(lower),lower_width=max(lower)-min(lower)+1,
        lower_lambdaQ_component_widths=[p[-1]-p[0]+1 for p in parts],lower_lambdaQ2_components=1,
        lower_E0_E1_E2_empty_original_real3=True,original_lambda=24,original_separation=16,
        joint_projection_radius_bound=39,transferred_steps=172,
        first_represented_right_GF_absolute_row=132359585792,first_represented_edge_GF_absolute_row=132360060928)
def payload():
    return dict(rule='unchanged isolated F31',Q=1024,U=475136,TF=278401,
        initializer='H.GF(x)=x modQ; H.Info[s](x)=A(x+s); all other mutable fields0; actual immutable programme',
        A_definition='divmod(y,Q)=(g,p); bit(p-59,g modQ) for59<=p<=68; A(g+p-94) for92<=p<=96; otherwise0',
        actual_old_upper_row='Y=R^TF(H)',upper_replacement='retain Y(x) whole record except listed bits',
        upper_GF_offset512_interval=[-14848,0],upper_F1_one_intervals=[[-15360,-14848],[-512,0]],
        upper_Info_one_logical_primary=1021,upper_Info_holders=[dict(x=1021-s,slot=s,component=s+2) for s in range(-2,3)],
        actual_old_lower_row='R^(TF*U)(H)=E(Y)',lower_replacement='retain complete E(Y)(x); change only ordinary Info holder bits so resulting full row is exactly E(C)',
        lower_GF_bit9_primary_formula='upper_x*Q+68; all five holders primary-slot',
        lower_F1_primary_formula='upper_x*Q+88; all five holders primary-slot',
        lower_Info_primary_formula='(1021-s)*Q+94+s; all five holders primary-copy',
        upper_actual_changed_locations=15365,lower_actual_changed_locations=79385,
        complete_symbolic_old_and_replacement_record_specification=True,
        numerical_all842bit_old_payloads_or_TF_T0_full_CA_trajectory_computed=False,
        no_later_errors=True,rule_ROM_constants_or_G17_changed=False,global_reliability_established=False)
def assets():
    pinned=dict(json.loads(PARENT.read_text())['assets_sha256'])
    pinned[str(PARENT.relative_to(ROOT))]=sha(PARENT)
    paths=[PROOF,Path(__file__),HERE/'probe_intact_background.py',OUT/'intact_background_probe01_receipt.json',
        OUT/'probe01.log',OUT/'startup_failure01.log',OUT/'actual_phaseTF_payload_descriptor.json',
        ROOT/'Report/proofs/SP31_OWN_RULE.md',ROOT/'figs/robustness/SP31_encoded_certificate.json',ROOT/'gacsca/gray_errors.py']
    for module in list(sys.modules.values()):
        f=getattr(module,'__file__',None)
        if f:
            p=Path(f).resolve()
            if p.suffix=='.py' and p.is_relative_to(ROOT):paths.append(p)
    for p in paths:
        rel=str(p.relative_to(ROOT));h=sha(p)
        assert rel not in pinned or pinned[rel]==h,rel
        pinned[rel]=h
    for rel,h in pinned.items():assert sha(ROOT/rel)==h,rel
    return dict(sorted(pinned.items()))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--issue',action='store_true');args=ap.parse_args();start=time.monotonic()
    if args.issue:assert not CERT.exists()
    else:
        frozen=json.loads(CERT.read_text())
        for rel,h in frozen['assets_sha256'].items():assert sha(ROOT/rel)==h,rel
    # Rebuild the actual full-R finite supplement; never overwrite discovery.
    old=json.loads((OUT/'intact_background_probe01_receipt.json').read_text());new=probe.compute()
    assert {k:v for k,v in old.items() if k!='seconds'}=={k:v for k,v in new.items() if k!='seconds'}
    assert len(old['selected_native_cofactors'])==80
    assert not old['all_time_intact_native_alias_or_genuine_fault_trajectory_proved_by_this_probe']
    assert json.loads((OUT/'actual_phaseTF_payload_descriptor.json').read_text())==payload()
    support=support_proof_checks()
    # Independently replay the exact prepared trace used for causal comparison.
    result=subprocess.run([sys.executable,str(ROOT/'Report/proofs/unregistered_sp31_upper_alias_pulse/check_prepared_alias.py')],capture_output=True,text=True)
    assert result.returncode==0,(result.stdout,result.stderr)
    parent_replay=json.loads(result.stdout)
    assert parent_replay['passed'] and parent_replay['readonly'] and parent_replay['first_right_wrong_upper_GF']==171
    encoded=json.loads((ROOT/'figs/robustness/SP31_encoded_certificate.json').read_text())
    assert encoded['complete_start_noiseless_and_all_period_pure_E0_simulation_proved']
    cert=dict(passed=True,Q=1024,U=475136,TF=278401,radius=37,
        proof_sha256=sha(PROOF),checker_sha256=sha(__file__),candidate_sha256=old['candidate_sha256'],netlist_sha256=old['netlist_sha256'],
        explicit_terminating_all_integer_unshifted_H_equals_E_H_proved=True,
        actual_all_time_intact_native_flags_and_all_four_Info_alias_groups_zero_proved=True,
        all_time_scope_supplied_by_written_minimal_first_command_proof_not_samples=True,
        actual_phaseTF_old_fields_retained_and_one_original_real2_fault_proved=True,
        complete_encoded_actual_intact_start_one_original_real3_fault_proved=True,
        joint_projection_causality_transfer_first_right_GF171_edge_GF172_proved=True,
        complete_lower_encoding_lift_and_actual_bit9_event_times_proved=True,
        raw_lower_GF_and_clock_canonical_common_at_every_row=True,
        selected_native_cofactors=80,selected_finite_checks_measured_supplements=True,
        support=support,symbolic_complete_payload_descriptor=True,numerical_all_old842bit_payloads_computed=False,
        prepared512_step_endpoint_transferred=False,original_J225_same_fault_or_TF_alias_provenance_proved=False,
        higher_error_envelope_violation_or_persistent_failure_proved=False,
        general_higher_error_repair_positive_iid_rate_memory_or_globally_sufficient_minimum_proved=False,
        Gray_G17_Gacs_or_iid_refutation=False,rule_ROM_constants_or_G17_changed=False,
        global_reliability_established=False,assets_sha256=assets())
    if args.issue:CERT.write_text(json.dumps(cert,indent=2)+'\n')
    else:assert cert==frozen,'Read-only certificate differs.'
    print(json.dumps(dict(passed=True,readonly=not args.issue,assets_verified=len(cert['assets_sha256']),certificate_sha256=sha(CERT),
        selected_native_cofactors=80,upper_original_real2_points=15365,lower_original_real3_points=79385,
        first_right_native_GF_relative_step=171,first_edge_native_GF_relative_step=172,
        numerical_TF_T0_full_CA_or_all_old_payloads_computed=False,original_J225_or_higher_failure_or_iid_claim=False,
        parent_prepared_readonly_seconds=parent_replay['seconds'],seconds=time.monotonic()-start)),flush=True)
if __name__=='__main__':main()
