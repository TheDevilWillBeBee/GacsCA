"""Exact finite interfaces supporting the written SP30 history induction.

This composes frozen proofs; it does not simulate 278395 whole CA periods.
The written induction, rather than a recurrence sample, supplies that lift.
"""
from pathlib import Path
from itertools import product
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'Report/proofs'))
import proposed_sparse_signal_reservation1024 as proposed


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main(write=True):
    started=time.monotonic();out=ROOT/'figs/robustness';p=proposed.parameters()
    assert (p.Q,p.U,p.T_wf,p.PL,p.PB,p.nb)==(1024,475136,278401,928,10,512)
    Q,U,TF,S=p.Q,p.U,p.T_wf,p.T_wf+6144
    candidate=proposed.load_artifact();comp=candidate.comp
    assert candidate.digest()=='add9c6c446d80fcd1f19e7b154944479421a0d40c86db8af8f4c0c2de8f9eb8e'
    assert comp.digest=='dc8b5065401fc4e363082224535317ee8814a9a94e6e48e6d1769939793fa19b'
    names=('SP30_native_certificate.json','SP30_sixth_signal_certificate.json',
        'SP30_seventh_signal_certificate.json','SP30_GF_bank_closure_certificate.json',
        'SP30_translation_class_certificate.json','SP30_zero_GF_prefix_certificate.json',
        'SP30_left_source_contract_certificate.json','SP29_next_ghost_signal_certificate.json',
        'unregistered_pulse_store/certificate.json','unregistered_quiet_frame/certificate.json')
    receipts={name:json.loads((out/name).read_text()) for name in names}
    for record in receipts.values():assert record['global_reliability_established'] is False
    native,sixth,seventh,bank,translation,right,left,guards,store,protocol=[receipts[n] for n in names]
    assert native['legal_clock_increment_cases']==U
    assert sixth['actual_sixth_translating_projected_pulse_on_Z_proved']
    assert sixth['sixth_endpoint_template_L_R']==[92,98]
    assert sixth['actual_sixth_bank_and_seventh_complete_foreign_sources_proved']
    assert seventh['actual_sixth_boundary_native_fixed_bit_enclosure_proved']
    assert seventh['actual_commit_alias_and_partial_zeros_proved']
    assert seventh['recovered_zero_Info_copies']==330
    rows=seventh['sixth_native_source_cofactor_records']
    for r in rows:
        j=r['colony'];w=r['constant_output_words']
        if j<=90:assert w==dict(addr=j,age=p.age_code(6),f1=0,wf1=0)
        if 104<=j<=120:assert w==dict(addr=0,age=None,f1=1,wf1=0)
    assert any(r['colony']==90 for r in rows) and any(r['colony']==120 for r in rows)
    # We only use stored GF/F1 at edge90, not its unprotected late Age/WF.
    assert bank['universal_conditional_zero_GF_bank_closure_proved']
    assert (bank['literal_commit_reset_bits'],bank['literal_forwarded_Hold_Info_mask_identities'])==(807,5)
    assert translation['conditional_width_preserving_translation_class_on_Z_proved']
    assert translation['all_integer_Q_translations_and_all_legal_period_indices_covered']
    baseline=translation['finite_runs'][0]
    assert baseline['endpoint_template_L_R']==[122,128]
    assert baseline['all_row_GF_support_hull']==[123456,137216]
    assert baseline['all_row_GF_support_hull']==[128*Q-7616,134*Q]
    assert baseline['endpoint_wrong_GF_width']==6656
    assert translation['MF1021_fixed_zero_offset_ranges_from_K']==[[-56,-6],[-1,5]]
    assert left['universal_complete_local_GF_Flag1_and_claimed_Age_contract_proved']
    assert left['Workspace1_zero_under_explicit_Age_below_TF_contract_proved']
    assert left['correct_mixed_Age_radix928_block512_increment_used']
    assert right['universal_complete_local_identity_proved']
    assert right['conditional_zero_GF_prefix_gather_and_own_programme_contract_proved']
    assert protocol['conditional_Mail_Info_and_complete_frame_execution_proved']
    assert protocol['native_outputs_structurally_instruction_independent']==31
    assert protocol['all_other_Match_registers_discarded_before_definedness']
    assert protocol['complete_frame_SF_holder_interval']==[1,1023]
    assert protocol['native_footprint_interval']==[-36,1060]
    assert protocol['protected_full_left_frame_native_clearance']==540
    assert store['recovered_zero_GF_F1_Info_copies']==330
    assert store['pending_presence_kind_cases']==256 and store['Hold_ROM_keys']==90112
    for r in store['Hold_issue_records']:
        assert r['materialized']==r['input_issue']+2
        if r['phase_shift']==0:assert r['materialized']<TF
        else:assert r['input_issue']>S

    # Exact legal clock codes and the increment used by the left contract.
    # Padding positions928..1023 are never interpreted as legal ticks.
    previous=-1
    for t in range(U):
        block,pos=divmod(t,928);code=p.age_code(t)
        assert code==(block<<10)+pos and code>previous
        assert 0<=block<512 and 0<=pos<928
        next_code=(code+1 if pos<927 else ((block+1)%512)<<10)
        assert next_code==p.age_code((t+1)%U)
        previous=code
    closed=0
    for t in (*range(TF),*range(S,U)):
        code=p.age_code(t)
        assert code!=p.age_code(TF)
        assert not (p.age_code(TF)<=code<p.age_code(TF+2048))
        assert not (p.age_code(TF)<=code<p.age_code(TF+2*Q-1)+1)
        closed+=1
    assert closed==guards['closed_legal_clock_guard_cases']==468992

    # All relative hull reserves, rather than the earlier1022 endpoint.
    full_right=-9*Q+1060;edge_right=-8*Q+88+2+37
    right_left=6*Q+59-2-37
    assert -7616-full_right==540 and -7616-edge_right==449
    assert right_left-6*Q==20
    assert set(range(0,6))|set(range(6,24))==set(range(24))
    assert set(range(23)).issubset(set(range(24)))
    assert 28-6+1==23 and 28-5==23
    mask=(set(range(58,901))-{509,515})|{901,902,965}
    alias_cases=0
    for phase,shift,slot in product((3,509,515,1021),(0,512),proposed.SLOTS):
        virtual=((phase-slot+shift)%Q+slot)%Q
        assert virtual not in mask;alias_cases+=1
    assert alias_cases==40
    alias_geometry=[]
    for j,phase in product(range(-3,10),(509,1021)):
        y=j*Q+phase
        sides=[int(-512<=y-slot<6*Q) for slot in proposed.SLOTS]
        assert len(set(sides))==1
        virtual=(phase+512*sides[0])%Q
        active=virtual==1021
        assert active==((0<=j<6) if phase==509 else (j<=-2 or j>=6))
        alias_geometry.append([j,phase,virtual,active])
    assert [r[2] for r in alias_geometry if (r[0],r[1]) in ((-1,509),(5,1021))]==[509,509]
    # Structural all-31 native outputs: a late arbitrary Match word suffices.
    deps=[0,0]+[(1<<key[1]) if key[0]=='I' else 0 for key in comp.inputs]
    for _,a,b in comp.gates:deps.append(deps[a]|deps[b])
    for field,width in (('addr',p.k),('age',p.m),('f1',1),('wf1',1)):
        for bit in range(width):assert deps[comp.outputs[('y',field,bit)]]==0

    # Universal-period arithmetic for precisely the finite inductive horizon.
    period_digest=hashlib.sha256();corners=0
    for period in range(6,TF):
        K=128-6*period;R=K+6;newK=K-6;newR=K
        A=p.age_code(period)
        assert 0<A<p.age_code(TF) and p.age_code(period+1)<=p.age_code(TF)
        corner=K%Q in (1023,0,1)
        assert corner==(period%512==192)
        corners+=corner
        assert newK<newR and newK<=K and newR<=R-1
        assert K-9==newK-3 and K-8==newK-2
        assert newK+6==K and newK+28==K+22
        assert R<=R+17==K+23==K+28-5
        assert K*Q-(newK*Q-512)==6656
        period_digest.update(f'{period}:{K}:{A}:{newK}\n'.encode())
    count=TF-6;assert count==278395
    proof=ROOT/'Report/proofs/unregistered_terminal/SP30_FINITE_REGENERATION.md'
    proof_paths=('SP30_FIRST_SIGNAL.md','SP30_GF_BANK_CLOSURE.md','SP30_SIXTH_SIGNAL.md',
        'SP30_SEVENTH_SIGNAL.md','SP30_TRANSLATION_CLASS.md','SP30_ZERO_GF_PREFIX.md',
        'SP30_LEFT_SOURCE_CONTRACT.md','unregistered_terminal/SP30_PULSE_STORE_PROTECTION.md',
        'unregistered_terminal/SP30_QUIET_FRAME_PROTOCOL.md')
    source_paths=('gacsca/rule.py','gacsca/rule_g.py','gacsca/netlist.py',
        'Report/proofs/proposed_sparse_signal_reservation1024.py',
        'Report/proofs/check_short_force1024_GF_bank_closure.py',
        'Report/proofs/check_short_force1024_next_ghost_signal.py',
        'Report/proofs/unregistered_terminal/check_sp30_quiet_frame_protocol.py',
        'Report/proofs/unregistered_terminal/check_sp30_pulse_store_protection.py')
    result=dict(name='SP30 finite actual-history regeneration before upper Workspace',
        checker_sha256=sha(__file__),proof_sha256=sha(proof),Q=Q,U=U,T_wf=TF,pulse_end=S,
        candidate_sha256=candidate.digest(),netlist_sha256=comp.digest,
        proof_dependencies_sha256={name:sha(ROOT/'Report/proofs'/name) for name in proof_paths},
        source_dependencies_sha256={name:sha(ROOT/name) for name in source_paths},
        receipt_dependencies_sha256={name:sha(out/name) for name in names},
        legal_clock_increment_cases=U,closed_lower_clock_guard_cases=closed,
        bootstrap_period=6,bootstrap_template_L_R=[92,98],bootstrap_full_left_last_colony=89,
        bootstrap_edge_GF_F1_colony=90,bootstrap_right_GF_zero_colonies=[98,120],
        bootstrap_edge_Age_WF_stored_correctness_assumed=False,
        invariant_boundaries_inclusive=[6,TF],pulse_periods_inclusive=[6,TF-1],
        pulse_endpoints=count,inductive_period_arithmetic_sha256=period_digest.hexdigest(),
        nonzero_Age_corner_periods=corners,last_endpoint_time=(TF-1)*U+S,
        last_boundary_time=TF*U,last_boundary_template_L_R=[128-6*TF,134-6*TF],
        constant_wrong_GF_width=6656,pulse_translation_sites=-6*Q,
        full_left_native_clearance=540,edge_early_GF_F1_clearance=449,right_early_GF_clearance=20,
        alias_commit_cases=alias_cases,alias_geometry_classes=alias_geometry,
        actual_finite_native_source_bank_alias_reset_regeneration_proved_by_written_composition=True,
        fresh_reencoding_at_intermediate_boundaries_assumed=False,
        arbitrary_original_upper_Info_allowed=True,later_physical_errors_allowed=False,
        initial_error_class_c16=3,initial_error_class_c104=2,
        horizon_stops_before_upper_Workspace_activities=True,
        full_upper_data_or_general_eroder_or_permanent_defect_proved=False,
        higher_error_map_or_positive_iid_or_Gray_refutation_or_minimal_global_change_proved=False,
        numerical_whole_CA_trajectory_used=False,active_rule_or_frozen_SP30_modified=False,
        initial_checker_extra_four_site_reserve_error_corrected=True,
        retained_initial_checker_sha256=sha(out/'SP30_finite_regeneration_initial_checker.py.txt'),
        retained_initial_run_sha256=sha(out/'SP30_finite_regeneration_initial_run.log'),
        global_reliability_established=False,elapsed_seconds=time.monotonic()-started)
    if write:
        dest=out/'unregistered_finite_regeneration';dest.mkdir(exist_ok=True)
        (dest/'certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('pulse_endpoints','last_endpoint_time',
        'last_boundary_time','actual_finite_native_source_bank_alias_reset_regeneration_proved_by_written_composition',
        'global_reliability_established','elapsed_seconds')}),flush=True)
    return result


if __name__=='__main__':main()
