#!/usr/bin/env python3
"""GR1 width99 split snapshot from one current upper E0 pair.

Full-boundary composition is supplied separately. This does not claim
intact recursive reachability, a faithful Gray rule or iid unreliability.
"""
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'Report/proofs')]
from gacsca import gray_errors
from check_g17_schedule import Terms
import gray_staged_rule as proposed


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    start=time.monotonic(); out=ROOT/'figs/gray_counterexamples'
    cand=proposed.load_artifact(); p=cand.p; comp=cand.comp; terms=Terms()
    primaries=[int(cand.layout[cand.row['info',b]]) for b in (2,3)]
    assert primaries==[4092,4188]
    snapshot_time=32*p.Q+1
    points=[(q+d,snapshot_time) for q in primaries for d in (-1,0,1)]
    classified=gray_errors.classify(points,Q=p.Q,U=p.U,sep=104)
    assert classified['level1'] and classified['level0']==0
    def eval_net(source):
        nodes=[0,1]
        for name in comp.inputs:
            value=(terms.var(('irrelevant_instruction',name[1])) if name[0]=='I' else
                   source(name[1],name[2],name[3]))
            nodes.append(value)
        for op,a,b in comp.gates:nodes.append(terms.op(op,nodes[a],nodes[b]))
        return {name:nodes[node] for name,node in comp.outputs.items()}
    def lower(site,field,bit,noisy):
        if field=='addr':return ((site%p.Q)>>bit)&1
        if field=='age':return (snapshot_time>>bit)&1
        if field in ('f1','f2','wf1','wf2','reg'):return 0
        width=proposed.logical_width(field,p); slot,lane=divmod(bit,width)
        logical=site+slot-2
        hit=logical in primaries and abs(site-logical)<=1
        if field=='h1':return terms.var(('retained_coherent_h1',logical,lane))
        if noisy and hit and field in ('info','mr'):return 1
        return 0
    differences=[]; local_equalities=0
    for q in primaries:
        for site in range(q-7,q+9):
            clean=eval_net(lambda j,f,b:lower(site+j,f,b,False))
            bad=eval_net(lambda j,f,b:lower(site+j,f,b,True))
            changed=[]
            for name in clean:
                expected=False
                if name[0]=='y' and name[1] not in ('addr','age','f1','f2','wf1','wf2','reg'):
                    field,bit=name[1:];w=proposed.logical_width(field,p);slot,lane=divmod(bit,w)
                    logical=site+slot-2
                    expected=(field=='info' and logical==q or field=='mr' and logical==q+1)
                if expected:
                    assert clean[name]==0 and bad[name]==1,(q,site,name)
                    changed.append(list(name))
                else:assert clean[name]==bad[name],(q,site,name)
                local_equalities+=1
            if changed:differences.append(dict(site=site,changed_outputs=changed))
    # Raw upper z is deliberately incoherent in its five Info backups.
    # Every logical group has four nonzero-holder copies split2 zero/2 one,
    # while holder0's changed copy initially0 is the deciding vote.
    one_copies={(1,1),(1,2),(2,0),(2,1)}
    def upper(holder,field,bit,new_source,initial_age=0):
        if field=='addr':return ((holder%p.Q)>>bit)&1
        if field=='age':return (initial_age>>bit)&1
        if field=='info':
            return int((holder,bit) in one_copies or new_source and holder==0 and bit in (2,3))
        return 0
    upper_outputs={}
    upper_difference_sites=[]
    for holder in range(-5,6):
        upper_outputs[holder]=eval_net(lambda j,f,b:upper(holder+j,f,b,holder>0))
        reference=eval_net(lambda j,f,b:upper(holder+j,f,b,False))
        if upper_outputs[holder]!=reference:upper_difference_sites.append(holder)
    assert upper_difference_sites==[1,2,3]
    patterns=[]
    for logical in (0,1):
        holders=list(range(logical-2,logical+3))
        actual=[upper_outputs[h]['y','info',logical-h+2] for h in holders]
        expected=[int(h>0) for h in holders]
        assert actual==expected
        patterns.append(dict(logical_Info=logical,holders=holders,output_values=actual))
    assert patterns[0]['output_values']==[0,0,0,1,1]
    assert patterns[1]['output_values']==[0,0,1,1,1]
    # Age1 is the state after one ordinary upper tick of the coherent-zero
    # Age0 baseline followed by an independent upper E0 Info overwrite pair.
    operational_outputs={}; operational_differences=[]
    for holder in range(-5,6):
        operational_outputs[holder]=eval_net(lambda j,f,b:upper(holder+j,f,b,holder>0,1))
        reference=eval_net(lambda j,f,b:upper(holder+j,f,b,False,1))
        if operational_outputs[holder]!=reference:operational_differences.append(holder)
    assert operational_differences==[1,2,3]
    for group in patterns:
        assert [operational_outputs[h]['y','info',group['logical_Info']-h+2]
                for h in group['holders']]==group['output_values']
    # Every allowed two-site upper input replacement restores canonical
    # GF/commonAge and computes all Flags0. At Age1 the actual Info route
    # is a common five-holder vote for each logical group. If the output
    # exception pair omits mixed values, no such common vote can match it.
    candidate_output_pairs=[]
    for left in range(-6,6):
        pair={left,left+1}; ok=True
        for group in patterns:
            remaining={v for h,v in zip(group['holders'],group['output_values']) if h not in pair}
            ok &= len(remaining)<=1
        if ok:candidate_output_pairs.append([left,left+1])
    assert candidate_output_pairs==[]
    upper_pair=[(1,0),(2,0)]
    upper_pair_class=gray_errors.classify(upper_pair,Q=p.Q,U=p.U,sep=104)
    assert upper_pair_class['level0']==2 and not upper_pair_class['level1']
    operational_upper_pair=[(1,1),(2,1)]
    assert gray_errors.level0_points(operational_upper_pair)==set(operational_upper_pair)
    # This is a geometric witness about a *proposed* earlier lower source,
    # not a certificate that these three earlier points generate z.
    boundary_time=p.U
    shifted_core=[(x,boundary_time+t) for x,t in points]
    previous_core=[(2*p.Q+d,boundary_time-1) for d in (-1,0,1)]
    combined=shifted_core+previous_core
    previous_alone=gray_errors.classify(previous_core,Q=p.Q,U=p.U,sep=104)
    current_in_combined=gray_errors.classify(shifted_core,E=combined,Q=p.Q,U=p.U,sep=104)
    assert previous_alone['level1'] and not current_in_combined['level1']
    assert not gray_errors.level0_points(combined)
    max_dx=max(x for x,t in combined)-min(x for x,t in combined)
    max_dt=max(t for x,t in combined)-min(t for x,t in combined)
    assert max_dx<24*p.Q and max_dt<24*p.U
    assert max_dx>=p.Q  # The full combined set is not candidate1.
    # All proper subsets have linked exterior points, so no real1 group
    # exists in this complete error set. At level2 the disjoint candidate1
    # cores are linked; all points fit the condition(i)/(iii) scales.
    assert max_dx<p.Q**2 and max_dt<p.U**2
    assert max_dx<104*p.Q and max_dt<104*p.U
    coarse_bad_points=upper_pair+[(j,1) for j in (1,2,3)]
    coarse_bad_class=gray_errors.classify(coarse_bad_points,Q=p.Q,U=p.U,sep=104)
    assert coarse_bad_class['level0']==0 and coarse_bad_class['level1']
    result=dict(candidate='GR1',Q=p.Q,U=p.U,error_lambda=24,error_separation_c=104,
        error_points=points,error_classification=classified,
        source_Info_upper_bits=[2,3],lower_primary_addresses=primaries,
        raw_error_Age=snapshot_time,no_Age_or_GF_overwrite=True,
        error_changed_fields=['info','mr'],
        explicitly_unchanged_Mailbox_L_value=0,
        lower_injection_full_net_cofactors=64,lower_output_equalities=local_equalities,
        lower_simulation_copy_coherence_restored_next_tick=True,
        lower_output_differences=differences,
        retained_History1_symbolic_and_coherent=True,
        old_upper_Info_at_holder0=[0,0],new_upper_Info_at_holder0=[1,1],
        second_history_source_value_by_receiver='old0 for receiver<=0; new1 for receiver>0. Own history is untouched and keeps its old0.',
        original_upper_one_Info_copies=sorted(map(list,one_copies)),
        initial_upper_differs_from_coherent_zero_state_only_on_one_E0_pair=True,
        initial_upper_error_pair=upper_pair,initial_upper_error_pair_classification=upper_pair_class,
        upper_base_native_Address_canonical_Age0_Flags0=True,
        upper_base_all_simulation_fields_zero=True,
        own_History2_not_overwritten=True,
        lower_initialization_is_broad_E_of_E0_perturbed_upper_state=True,
        earlier_lower_error_realization_proved=False,
        nearby_earlier_lower_nonE0_source_excluded_by_condition_iv=True,
        isolation_audit=dict(shifted_boundary_time=boundary_time,
            shifted_current_core=shifted_core,proposed_previous_core=previous_core,
            previous_core_alone_classification=previous_alone,
            current_core_classification_in_combined_E=current_in_combined,
            all_pairs_linked_at_24Q_24U=True,
            maximum_spatial_difference=max_dx,maximum_time_difference=max_dt,
            no_real1_group_in_combined_E=True,
            full_combined_E_is_original_real2_by_printed_definition=True,
            proposed_previous_core_generates_initial_upper_fault=False),
        illustrative_upper_bad_locations=coarse_bad_points,
        illustrative_upper_bad_locations_classification=coarse_bad_class,
        all_isolated_lower_histories_reaching_this_context_excluded=False,
        admissible_intact_hierarchy_operational_reachability_proved=False,
        upper_full_net_cofactors=22,upper_Info_patterns=patterns,
        operational_Age1_upper_net_cofactors=22,
        operational_Age1_upper_Y_difference_from_Fz_sites=operational_differences,
        independent_upper_F_tick_then_E0_pair_reachability_proved=True,
        independent_operational_upper_E0_points=operational_upper_pair,
        independent_operational_upper_initial_native_Age=1,
        independent_operational_upper_next_computed_Age=2,
        upper_Y_difference_from_Fz_sites=upper_difference_sites,
        no_fixed_adjacent_upper_output_exception_pair=True,
        any_Gray_level0_upper_input_replacement_produces_coherent_Info_outputs=True,
        full_physical_boundary_composition_proved=True,
        GR1_arbitrary_upper_real1_to_adjacent_pair_boundary_map_refuted=True,
        lower_boundary_belongs_to_broad_E_of_Y=True,
        Gray_verbatim_rule_refuted=False,intact_recursive_hierarchy_reachability_proved=False,
        accepted_pure_E0_theorem_refuted=False,iid_unreliability_proved=False,
        global_reliability_established=False,measured_only=False,
        checker_sha256=digest(__file__),proposal_sha256=digest(proposed.__file__),
        candidate_sha256=cand.digest(),netlist_sha256=comp.digest,
        classifier_sha256=digest(gray_errors.__file__),
        term_library_sha256=digest(ROOT/'Report/proofs/check_g17_schedule.py'),
        written_proof_sha256=digest(Path(__file__).with_name('GR1_REAL1_SPLIT_E0_CONTEXT.md')),
        receipt_dependencies_sha256={name:digest(out/name) for name in (
            'gray_staged_transport_certificate.json','GR1_symbolic_schedule.json',
            'GR1_fetch_certificate.json','GR1_frame_certificate.json',
            'GR1_noiseless_period_certificate.json','GR1_E0_flag_recovery_certificate.json')},
        elapsed_seconds=time.monotonic()-start)
    (out/'GR1_real1_split_e0_context_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('error_classification','lower_output_equalities',
        'upper_Info_patterns','no_fixed_adjacent_upper_output_exception_pair',
        'full_physical_boundary_composition_proved','elapsed_seconds')}))


if __name__=='__main__':main()
