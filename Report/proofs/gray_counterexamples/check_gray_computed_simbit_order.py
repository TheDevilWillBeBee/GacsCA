#!/usr/bin/env python3
"""Pin locality/order witnesses and an explicitly changed local interface.

New component sources/receipts only; accepted GT0 files are not changed.
No full self-programme, encoded reachability or iid theorem is supplied.
"""
from pathlib import Path
from itertools import combinations,product
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,const_word,at_least
from gacsca import maintenance,gray_errors
import literal_maintenance
import gray_raw_gather as gt0
import gray_workspace_voted_current as voted
import check_computed_simbit_radius as original


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def age_configuration(changed):
    cells={x:dict(addr=x%gt0.Q,age=original.TIME,f1=0,f2=int(-2<=x<=2),wf1=0,wf2=0)
           for x in range(-5,9)}
    cells[6]['age']=cells[7]['age']=gt0.U-1
    cells[8]['age']=gt0.U-1 if changed else original.TIME
    return cells


def gt0_source(native,raw_address,remove_wipe=False):
    n=Net();p=gt0
    data={j:{f:[int(f=='simbit')]*(5*w) for f,w in p.FIELDS} for j in range(-5,6)}
    flags=[n.input(('free_early_flag',i)) for i in range(2)]
    writes={s:(n.input(('free_write_enable',s)),n.input(('free_write_value',s))) for s in p.SLOTS}
    wipe=int(native['f1'] and native['addr']!=raw_address)
    outputs=p.build(n,data,const_word(native['addr'],p.K),const_word(native['age'],p.M),
                    native['f1'],0 if remove_wipe else wipe,*flags,writes)
    out=outputs['simbit',0,0]
    assert out in (0,1),out
    return out,wipe


def main():
    p=gt0;directory=ROOT/'figs/gray_counterexamples';native_count=0
    age_rows=[]
    good,bad=age_configuration(False),age_configuration(True)
    assert [x for x in good if good[x]!=bad[x]]==[8]
    for changed,cells in ((False,good),(True,bad)):
        native={x:original.exact_native(cells,x,literal_maintenance.build) for x in (0,3)}
        corrected={x:original.exact_native(cells,x,maintenance.build) for x in (0,3)}
        native_count+=4
        assert native==corrected
        assert native[0]==dict(addr=0,age_now=original.TIME,age=original.TIME+1,f1=0,f2=0)
        assert native[3]==dict(addr=3,age_now=p.U-1 if changed else original.TIME,
            age=0 if changed else original.TIME+1,f1=int(changed),f2=int(changed))
        final,wipe=gt0_source(native[3],cells[3]['addr'])
        prewipe,_=gt0_source(native[3],cells[3]['addr'],True)
        assert wipe==0 and final==prewipe==int(not changed)
        n=Net()
        # All current logical SimBits are1. Other data/ports are irrelevant
        # for the explicitly changed voted-current interface.
        data={j:dict(simbit=[1]*5) for j in range(-5,6)}
        repaired=voted.interface(n,data,const_word(native[0]['addr'],p.K),
            const_word(native[0]['age'],p.M),native[0]['f1'],0)
        assert repaired==dict(wf1=0,wf2=1)
        age_rows.append(dict(changed_Age8=changed,raw_native_neighbourhood=cells,
            computed_native=native,native_wipe3=wipe,GT0_final_primary_SimBit3=final,
            GT0_scheduled_prewipe_primary_SimBit3=prewipe,
            literal_WF2_reader0=prewipe,GV0_voted_current_WF2_reader0=repaired['wf2'],
            all_GT0_future_programme_ports_symbolic=True))
    # Distinguish the changed expression also on the accepted GF/wipe pair.
    gf_rows=[]
    for changed in (False,True):
        cells=original.configuration(changed)
        native={x:original.exact_native(cells,x,literal_maintenance.build) for x in (0,3)}
        native_count+=2
        final,wipe=gt0_source(native[3],cells[3]['addr'])
        prewipe,_=gt0_source(native[3],cells[3]['addr'],True)
        assert final==int(not changed) and prewipe==1 and wipe==int(changed)
        n=Net();data={j:dict(simbit=[1]*5) for j in range(-5,6)}
        actual=voted.interface(n,data,const_word(native[0]['addr'],p.K),
            const_word(native[0]['age'],p.M),native[0]['f1'],0)
        assert actual==dict(wf1=0,wf2=1)
        gf_rows.append(dict(changed_Address8=changed,GT0_final_primary_SimBit3=final,
            GT0_scheduled_prewipe_primary_SimBit3=prewipe,GV0_voted_current_WF2_reader0=1))
    # Local E0 false-positive of raw current-primary reading. Current
    # primary3 alone is overwritten; its four secondary copies remain0.
    e0_rows=[]
    for receiver in range(5):
        cells={j:dict(addr=(receiver+j)%p.Q,age=original.TIME,f1=0,f2=0,wf1=0,wf2=0)
               for j in range(-5,6)}
        n=Net();constant={j:dict(addr=const_word(r['addr'],p.K),age=const_word(r['age'],p.M),
            **{f:r[f] for f in ('f1','f2','wf1','wf2')}) for j,r in cells.items()}
        native=literal_maintenance.build(n,constant,p.K,p.M)
        assert native['addr']==const_word(receiver,p.K)
        assert native['age']==const_word(original.TIME+1,p.M)
        assert (native['f1'],native['f2'])==(0,0)
        native_count+=1
        source=3-receiver
        for overwrite in (False,True):
            n=Net()
            # Other logical Info values are free; only the source group
            # and one designated stored copy are constrained.
            logical={x:n.input(('other_logical_Info',x)) for x in range(-7,8)}
            logical[source]=0
            data={j:dict(simbit=[logical[j+s] for s in p.SLOTS]) for j in range(-5,6)}
            data[source]['simbit'][0]=int(overwrite)
            actual=voted.interface(n,data,const_word(receiver,p.K),
                const_word(original.TIME+1,p.M),0,0)
            assert actual['wf2']==0
            current_primary=data[source]['simbit'][0]
            assert current_primary==int(overwrite)
            e0_rows.append(dict(receiver=receiver,primary_copy_overwritten=overwrite,
                raw_current_primary_WF2=int(overwrite),GV0_voted_current_WF2=actual['wf2'],
                unrelated_logical_SimBits_symbolic=True))
    majority_cases=0
    for value in (0,1):
        for size in (0,1,2):
            for wrong in combinations(range(5),size):
                for replacement in product((0,1),repeat=size):
                    holders=[value]*5
                    for i,v in zip(wrong,replacement):holders[i]=v
                    n=Net();out=at_least(n,holders,3)
                    assert out==value
                    majority_cases+=1
    assert majority_cases==102
    # Complete clock/address predicate partition with unconstrained raw
    # source copies and reader controls. No canonical native premise is
    # used for this interface equation check.
    age_boundaries=[0,96*p.Q,98*p.Q,p.U]
    address_boundaries=sorted(set(range(6))|set(range(p.Q-5,p.Q+1)))
    route_assertions=0
    for age in age_boundaries[:-1]:
        for address in address_boundaries[:-1]:
            n=Net();data={j:dict(simbit=[n.input(('raw_copy',j,b)) for b in range(5)])
                          for j in range(-5,6)}
            f1=n.input(('free_reader_Flag1',));wipe=n.input(('free_reader_wipe',))
            actual=voted.interface(n,data,const_word(address,p.K),const_word(age,p.M),f1,wipe)
            pulse=96*p.Q<=age<98*p.Q
            v1=voted.vote(n,data,p.Q-3-address) if p.Q-5<=address<p.Q else 0
            v2=voted.vote(n,data,3-address) if 0<=address<5 else 0
            expected=dict(wf1=n.AND(int(pulse),n.AND(v1,n.NOT(wipe))),
                          wf2=n.AND(int(pulse),n.AND(v2,n.NOT(f1))))
            assert actual==expected,(age,address)
            route_assertions+=2
    assert route_assertions==66
    comp=voted.compiled()
    assert max(abs(name[1]) for name in comp.inputs)==5
    graph=directory/'GV0_voted_current_workspace_transitions.json'
    graph.write_text(json.dumps(dict(name='GV0 changed voted-current Workspace interface, not a full CA',
        Q=p.Q,U=p.U,inputs=comp.inputs,gates=comp.gates,outputs=list(comp.outputs.items()),
        netlist_sha256=comp.digest,source_interpretation_changed=True),separators=(',',':'))+'\n')
    e0=gray_errors.classify([(3,original.TIME)],Q=p.Q,U=p.U,sep=104)
    assert e0['level0']==1 and not e0['level1']
    # Geometry only: two E0 groups can meet a two-tick radius8 cone,
    # while no radius5 two-tick cone can contain both sites0 and24.
    points=[(0,1),(24,1)]
    isolated=gray_errors.classify(points,Q=p.Q,U=p.U,sep=104)
    assert isolated['level0']==2 and not isolated['level1']
    center=12;two_tick_radius8=[center-16,center+16]
    assert all(two_tick_radius8[0]<=x<=two_tick_radius8[1] for x,t in points)
    assert 24>2*(2*5)
    # Dependency upper bound for a radius5 source transition, independent
    # of any programme choice or raw state. No full source port supplied.
    support1=set();support2=set()
    for a in range(p.Q-5,p.Q):support1.update(p.Q-3-a+j for j in range(-5,6))
    for a in range(5):support2.update(3-a+j for j in range(-5,6))
    assert sorted(support1)==list(range(-7,8))
    assert sorted(support2)==list(range(-6,9))
    slots=range(-8,9)
    frame=p.FRAME_BITS+5*(3*(len(slots)-11)+(len(slots)-11))
    assert frame==397 and 8*p.Q+2<16*p.Q
    proof=Path(__file__).with_name('GRAY_COMPUTED_SIMBIT_ORDER.md')
    result=dict(name='Gray computed SimBit ordering/locality interface audit',Q=p.Q,U=p.U,
        error_lambda=24,error_separation_c=104,exact_native_cofactors=native_count,
        scheduled_prewipe_age_witness=age_rows,previous_final_vs_prewipe_comparison=gf_rows,
        scheduled_prewipe_source_radius_lower_bound=8,
        deleting_source_wipe_alone_resolves_locality=False,
        age_witness_independent_of_printed_or_h1_Flag2=True,
        raw_current_primary_local_E0_false_positive=e0_rows,
        raw_current_primary_singleton_E0_classification=e0,
        raw_current_primary_E0_copy_transparency_refuted_locally=True,
        exact_vote_at_most_two_fault_cofactors=majority_cases,
        GV0_complete_clock_partition=age_boundaries,
        GV0_complete_address_partition=address_boundaries,
        GV0_symbolic_raw_copy_and_reader_control_route_equalities=route_assertions,
        GV0_source_expression_changed_to_voted_CURRENT=True,
        GV0_maximum_raw_input_distance=5,GV0_netlist_sha256=comp.digest,
        GV0_native_equation_radius5_composed=True,GV0_all_raw_state_locality_proved=True,
        GV0_local_copy_transparency_with_correct_reader_controls_proved=True,
        final_radius5_source_composition_support_WF1=sorted(support1),
        final_radius5_source_composition_support_WF2=sorted(support2),
        conditional_final_source_composition_radius8_sufficient_proved=True,
        radius8_paper_error_geometry_radius_independent=True,
        radius8_two_tick_cone_E0_example=dict(points=points,classification=isolated,
            center=center,cone=two_tick_radius8,actual_two_tick_error_survival_proved=False),
        radius8_gather_offsets=list(slots),radius8_last_capture_delay=8*p.Q+2,
        radius8_preliminary_frame_bits=frame,original_gather_active_duration=16*p.Q,
        geometry_or_sufficient_window_is_full_noisy_refinement=False,
        actual_programme_runtime_or_final_layout_proved=False,
        actual_faithful_Gray_whole_rule_compiled=False,
        GV0_whole_rule_E0_or_higher_theorem_proved=False,
        encoded_history_reachability_proved=False,decoded_memory_or_iid_failure_proved=False,
        universal_Gray_completion_nonexistence_proved=False,
        faster_U_used=False,active_rule_modified=False,global_reliability_established=False,
        checker_sha256=digest(__file__),written_proof_sha256=digest(proof),
        GV0_primitive_sha256=digest(voted.__file__),emitted_GV0_graph_sha256=digest(graph),
        GT0_primitive_sha256=digest(gt0.__file__),original_conditional_checker_sha256=digest(original.__file__),
        literal_module_sha256=digest(literal_maintenance.__file__),
        generated_literal_maintenance_sha256=literal_maintenance.source_sha256(),
        native_maintenance_sha256=digest(ROOT/'gacsca/maintenance.py'),
        netlist_library_sha256=digest(ROOT/'gacsca/netlist.py'),
        classifier_sha256=digest(ROOT/'gacsca/gray_errors.py'),
        gray_text_sha256=digest(ROOT/'papers_txt/gray_readers_guide.txt'),
        gray_pdf_sha256=digest(next((ROOT/'papers').glob('A Reader*'))),
        original_page_images_sha256={f'Gray_page{page}.png':digest(directory/f'Gray_page{page}.png')
            for page in (14,21,33,34,41)},
        receipt_dependencies_sha256={name:digest(directory/name) for name in
            ('GT0_raw_gather_certificate.json','GT0_radius_integration_certificate.json')},
        measured_only=False)
    (directory/'Gray_computed_simbit_order_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('exact_native_cofactors',
        'scheduled_prewipe_source_radius_lower_bound','GV0_all_raw_state_locality_proved',
        'exact_vote_at_most_two_fault_cofactors','radius8_preliminary_frame_bits',
        'actual_faithful_Gray_whole_rule_compiled')}))


if __name__=='__main__':main()
