"""Exact endpoint/class arithmetic for the changed-F30 box counterexample.

Actual reachability is J216's written induction, not a new CA simulation.
"""
from pathlib import Path
import hashlib,json,time
ROOT=Path(__file__).resolve().parents[3]


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main(write=True):
    start=time.monotonic();out=ROOT/'figs/robustness'
    dep=out/'unregistered_finite_regeneration/certificate.json';prior=json.loads(dep.read_text())
    assert prior['actual_finite_native_source_bank_alias_reset_regeneration_proved_by_written_composition']
    assert prior['pulse_periods_inclusive']==[6,278400]
    assert (prior['Q'],prior['U'],prior['T_wf'])==(1024,475136,278401)
    assert prior['proof_sha256']==sha(ROOT/'Report/proofs/unregistered_terminal/SP30_FINITE_REGENERATION.md')
    assert prior['checker_sha256']==sha(ROOT/'Report/proofs/unregistered_terminal/check_sp30_finite_regeneration.py')
    for name,h in prior['proof_dependencies_sha256'].items():assert sha(ROOT/'Report/proofs'/name)==h
    for name,h in prior['receipt_dependencies_sha256'].items():assert sha(out/name)==h
    old_path=out/'SP28_full_Address_island_certificate.json';old=json.loads(old_path.read_text())
    classified=old['physical_error_classification']
    assert classified['actual_level_at_c16']==3 and classified['actual_level_at_c104']==2
    assert classified['E0_empty'] and classified['E1_empty'] and classified['E2_empty_at_c16']
    Q,U,TF,S=1024,475136,278401,284545;length=17*Q
    assert length==classified['sites']==17408 and classified['minimum_witness_distance']==length-7==17401
    assert length-1<17*Q and length-7>=16*Q
    assert length<24*Q and length<Q*Q
    # First/last four-point witnesses each split into two linked pairs.
    witnesses=[[127*Q+i for i in range(4)],[144*Q-4+i for i in range(4)]]
    assert min(abs(a-b) for a in witnesses[0] for b in witnesses[1])==17401
    assert witnesses==[[point[0] for point in row] for row in classified['c16_separated_candidate2_witnesses']]
    assert all(max(row)-min(row)<Q for row in witnesses)
    assert max(witnesses[1])-min(witnesses[0])<24*Q*Q
    # These inequalities prove the whole ranges, not sampled classifiers.
    classes=[dict(integer_c_inclusive=[1,16],original_real_level=3),
        dict(integer_c_lower_bound=17,original_real_level=2)]
    def endpoint(p):
        assert 6<=p<TF
        K=128-6*p
        return dict(period=p,time=p*U+S,wrong_GF_interval=[(K-6)*Q-512,K*Q])
    records=[endpoint(p) for p in (6,347,29703,TF-1)]
    first,spatial,temporal,last=records
    assert first['wrong_GF_interval']==[87552,94208]
    assert spatial['wrong_GF_interval']==[-2007552,-2000896]
    sites=[spatial['wrong_GF_interval'][0],first['wrong_GF_interval'][1]-1]
    hull_width=sites[1]-sites[0]+1
    assert hull_width==2101760>2*Q*Q==2097152
    difference=temporal['time']-first['time']
    assert difference==29697*U==14110113792>U*U//16==14109638656
    assert all(r['wrong_GF_interval'][1]-r['wrong_GF_interval'][0]==6656 for r in records)
    endpoint_hull=first['wrong_GF_interval'][1]-last['wrong_GF_interval'][0]
    temporal_span=last['time']-first['time']
    assert endpoint_hull==1710459392<2*Q**3==2147483648
    assert temporal_span==132275011584<U**3//16==6703997272457216
    source=ROOT/'papers_txt/gray_readers_guide.txt'
    text=source.read_text()
    assert 'Proposition 5.' in text and 'space-time box of the form [ jQk, ( j+2) Qk)' in text
    proof=ROOT/'Report/proofs/unregistered_terminal/SP30_ERROR_ENVELOPE_COMPARISON.md'
    proofs=('Report/proofs/SP30_OWN_RULE.md','Report/proofs/SP30_FIRST_SIGNAL.md',
        'Report/proofs/SP28_FULL_ADDRESS_ISLAND.md',
        'Report/proofs/unregistered_terminal/SP30_FINITE_REGENERATION.md')
    result=dict(name='SP30 literal higher-error box comparison',Q=Q,U=U,T_wf=TF,
        checker_sha256=sha(__file__),proof_sha256=sha(proof),primary_Gray_text_sha256=sha(source),
        proof_dependencies_sha256={n:sha(ROOT/n) for n in proofs},
        receipt_dependencies_sha256={str(n.relative_to(out)):sha(n) for n in (dep,old_path)},
        actual_original_error_support=[127*Q,144*Q],error_time=0,error_locations=length,
        original_recursive_class_ranges=classes,first_last_candidate2_witnesses=witnesses,
        c16_real3_c104_real2_classification_exact=True,actual_endpoint_records=records,
        spatial_witness_sites=sites,spatial_lattice_hull_width=hull_width,
        class2_box_width=2*Q**2,spatial_excess=hull_width-2*Q**2,
        temporal_witness_span=difference,class2_box_height=U**2//16,
        temporal_excess=difference-U**2//16,
        finite_endpoint_hull_width=endpoint_hull,finite_endpoint_time_span=temporal_span,
        class3_box_width=2*Q**3,class3_box_height=U**3//16,
        literal_Proposition5_spatial_and_temporal_transplant_refuted_for_changed_F30_c_ge17=True,
        actual_unchanged_F30_history_from_J216_used=True,
        c16_class3_or_general_repair_envelope_refuted=False,
        aligned_class3_box_containment_or_intermediate_higher_damage_control_proved=False,
        largest_integer_c_promoting_this_witness_to_real3=16,
        positive_iid_or_Gray_Gacs_G17_failure_or_minimum_sufficient_change_proved=False,
        permanent_defect_or_later_upper_Workspace_recovery_proved=False,
        new_rule_or_constant_or_active_rule_change=False,numerical_whole_CA_trajectory_used=False,
        global_reliability_established=False,elapsed_seconds=time.monotonic()-start)
    if write:
        dest=out/'unregistered_envelope_comparison';dest.mkdir(exist_ok=True)
        (dest/'certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('spatial_lattice_hull_width','class2_box_width',
        'temporal_witness_span','class2_box_height',
        'literal_Proposition5_spatial_and_temporal_transplant_refuted_for_changed_F30_c_ge17',
        'c16_class3_or_general_repair_envelope_refuted','global_reliability_established','elapsed_seconds')}))
    return result


if __name__=='__main__':main()
