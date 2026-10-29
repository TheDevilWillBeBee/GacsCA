#!/usr/bin/env python3
"""Full-SP28 native travelling island via universal auxiliary/WF enclosure."""
from functools import lru_cache
from pathlib import Path
import hashlib,json,subprocess,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from gacsca import gray_errors
from gacsca.netlist import Net,Compiled,at_least
import proposed_sparse_distant_epoch1024 as proposed

LABEL,F1LO,F1HI,F2LO,F2HI,PV,CV,WF1HI=range(8)


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_state(path,N):
    raw=Path(path).read_bytes()
    assert len(raw)==10*N
    return np.frombuffer(raw[:8*N],dtype=np.uint8).reshape(8,N).copy(),np.frombuffer(raw[8*N:],dtype=np.uint16).copy()


def check_monotone_Flag2():
    source=proposed.proposed_build()[1]
    start=source.index("    left = [cells[j]['f2']")
    stop=source.index('    vote_right = ',start)
    fragment=source[start:stop]
    namespace={'at_least':at_least}
    exec(compile('def build(n,cells,inside,f1,d4,service_force):\n    d3=0\n    c=cells[0]\n'+fragment+'    return f2\n',
                 '<literal unchanged SP28 Flag2 fragment>', 'exec'),namespace)
    masks=np.arange(512,dtype=np.uint16)
    identities=directed=0;digests=[]
    for inside_count in range(6):
        n=Net()
        inputs=[n.input(('bit',b)) for b in range(9)]
        cells={0:dict(f2=inputs[1])}
        cells.update({-d:dict(f2=inputs[d+1]) for d in range(1,6)})
        inside={-d:int(d<=inside_count) for d in range(1,6)}
        value=namespace['build'](n,cells,inside,inputs[0],inputs[7],inputs[8])
        n.set_output(('f2',),value);comp=Compiled(n);digests.append(comp.digest)
        bits=[((masks>>b)&1).astype(bool) for b in range(9)]
        got=comp.evaluate({('bit',b):bits[b] for b in range(9)},bool)['f2',]
        left=sum(bits[2:7]);left_inside=sum(bits[2:2+inside_count]) if inside_count else np.zeros(512,dtype=np.int64)
        on=(left_inside>=4)|(bits[0]&(left>=4))|bits[7]
        erase=(~bits[0]&(left_inside<2))|(bits[0]&(left==0))
        expected=np.where(bits[1],bits[7]|~erase,on)|bits[8]
        assert np.array_equal(got,expected)
        identities+=512
        for b in range(9):
            lower=masks[(masks&(1<<b))==0]
            assert not np.any(got[lower]&~got[lower|(1<<b)])
            directed+=len(lower)
    assert (identities,directed)==(3072,13824)
    return identities,directed,digests,hashlib.sha256(fragment.encode()).hexdigest()


def check_recursive_initialization(candidate):
    p=candidate.p
    tags={int(candidate.layout[row]):tag for tag,row in candidate.row.items()}
    assert set(tags)==set(range(59,901)) and len(tags)==842
    info=sorted(a for a,(f,b) in tags.items() if f=='info')
    assert info==list(range(92,97))
    assert not set(tags)&{3,p.Q-3,p.lo,p.hi-1}
    @lru_cache(None)
    def D(x):
        colony,residue=divmod(int(x),p.Q)
        tag=tags.get(residue)
        if tag is None:return 0
        field,bit=tag
        if field=='addr':return ((colony%p.Q)>>bit)&1
        if field=='info':
            child=colony+bit-2
            assert abs(child)<abs(x)
            return D(child)
        return 0
    def H(x,field,bit):
        if field=='addr':return ((x%p.Q)>>bit)&1
        if field=='info':return D(x+bit-2)
        return 0
    assert min(min(info),p.Q-max(info))==92
    assert 92/p.Q+3<92
    cases={'addr':0,'info':0,'zero':0}
    for field,bit in candidate.row:
        cases[field if field in ('addr','info') else 'zero']+=1
    assert cases==dict(addr=10,info=5,zero=827)
    samples=sorted(set(range(-20,21))|{s*(p.Q**e+d) for s in (-1,1)
        for e in (1,2,3,8,32) for d in (0,1,p.Q//2,p.Q-1)})
    checks=0
    for x in samples:
        for field,bit in candidate.row:
            address=int(candidate.layout[candidate.row[field,bit]])
            assert D(x*p.Q+address)==H(x,field,bit)
            checks+=1
        assert D(x*p.Q+p.lo)==D(x*p.Q+p.hi-1)==0
    assert all(H(0,f,b)==0 for f,b in candidate.row)
    return cases,checks


def check_dense_error_class(p):
    points=[(x,p.U) for x in range(127*p.Q,144*p.Q)]
    assert len(points)==17*p.Q
    assert gray_errors.level0_points(points)==set()
    # Candidate1 witnesses in the full dense set; proper sets cannot be
    # real1/real2 because the row's unit-link graph is connected.
    for group in (points[:2],points[2:4],points[-4:-2],points[-2:]):
        row=gray_errors.classify(group,E=points,Q=p.Q,U=p.U,sep=16)
        assert row['candidate_level1'] and not row['level1'] and row['level0']==0
    left,right=points[:4],points[-4:]
    assert gray_errors.linked(left[:2],left[2:],24*p.Q,24*p.U)
    assert gray_errors.linked(right[:2],right[2:],24*p.Q,24*p.U)
    assert not gray_errors.linked(left,right,16*p.Q,16*p.U)
    assert gray_errors.linked(left,right,24*p.Q**2,24*p.U**2)
    minimum_distance=min(abs(a[0]-b[0]) for a in left for b in right)
    assert minimum_distance==17*p.Q-7>=16*p.Q
    assert len(points)<=p.Q**2 and len(points)-1<104*p.Q<16*p.Q**2
    return dict(error_time=p.U,sites=len(points),support=[127*p.Q,144*p.Q],
        actual_level_at_c16=3,actual_level_at_c104=2,E0_empty=True,E1_empty=True,
        E2_empty_at_c16=True,c16_separated_candidate2_witnesses=[left,right],
        minimum_witness_distance=minimum_distance,
        universal_proof='SP28_FULL_CLOCK_ISLAND.md; connected dense row isolation, original recursive candidate/error definitions',
        exhaustive_higher_subset_enumeration_used=False)


def clock_count(t,p):
    phase=t%p.U
    return phase-(p.T_wf if phase>=p.T_wf else 0)-1


def literal_corner_updates(candidate,traces):
    p=candidate.p;comp=candidate.comp;N=256*p.Q
    offsets=(0,1,1791,1792,2048,4095,4096)
    readers_checked=equalities=0
    code_table=np.array([p.age_code(t) for t in range(p.U)],dtype=np.uint32)
    fields={'addr':p.k,'age':p.m,'f1':1,'f2':1,'wf1':1,'wf2':1,
            'packet_valid':1,'packet_tag':4,'packet_count':11,
            'service_valid':1,'service_position':11,'service_count':11}
    for begin in (0,p.T_wf):
        for offset in offsets:
            t=begin+offset
            old,position=traces[t];new,new_position=traces[t+1]
            edges=np.flatnonzero(old[LABEL]!=np.roll(old[LABEL],1)).tolist()
            ones=np.flatnonzero(old[LABEL]);mid=((int(ones[0])+int(ones[-1]))//(2*p.Q))*p.Q
            readers=np.array(sorted(set([x+d for x in edges for d in range(-40,41)]+
                list(range(mid,mid+p.Q))+list(range(16*p.Q,17*p.Q)))),dtype=np.int64)
            counter=clock_count(t,p);next_counter=clock_count(t+1,p)
            for upper in (False,True):
                f1plane=F1HI if upper else F1LO;f2plane=F2HI if upper else F2LO
                values={}
                for name in comp.inputs:
                    if name[0]!='x':v=np.zeros(len(readers),dtype=bool)
                    else:
                        _,off,field,bit=name;sites=(readers+off)%N;phase=sites%p.Q
                        if field=='addr':word=phase
                        elif field=='age':word=code_table[(t+old[LABEL,sites].astype(np.int64)*p.T_wf)%p.U]
                        elif field=='f1':word=old[f1plane,sites]
                        elif field=='f2':word=old[f2plane,sites]
                        elif field=='wf1':word=old[WF1HI,sites] if upper else np.zeros(len(readers),dtype=np.uint8)
                        elif field in ('wf2','packet_valid'):word=old[PV,sites]
                        elif field=='packet_tag':word=np.where(old[PV,sites],phase-1,0)
                        elif field=='packet_count':word=np.where(old[PV,sites],counter,0)
                        elif field=='service_valid':word=old[CV,sites]
                        elif field=='service_position':word=position[sites]
                        elif field=='service_count':word=np.where(old[CV,sites],counter,0)
                        elif field=='info':word=np.full(len(readers),31 if upper else 0,dtype=np.uint8)
                        else:word=np.zeros(len(readers),dtype=np.uint8)
                        v=((word>>bit)&1).astype(bool)
                    values[name]=v
                outputs=comp.evaluate(values,bool)
                expected=dict(addr=readers%p.Q,
                    age=code_table[(t+1+new[LABEL,readers].astype(np.int64)*p.T_wf)%p.U],
                    f1=new[f1plane,readers],f2=new[f2plane,readers],
                    wf1=new[WF1HI,readers] if upper else np.zeros(len(readers),dtype=np.uint8),
                    wf2=new[PV,readers],packet_valid=new[PV,readers],
                    packet_tag=np.where(new[PV,readers],readers%p.Q-1,0),
                    packet_count=np.where(new[PV,readers],next_counter,0),
                    service_valid=new[CV,readers],service_position=new_position[readers],
                    service_count=np.where(new[CV,readers],next_counter,0))
                for field,width in fields.items():
                    for bit in range(width):
                        assert np.array_equal(outputs['y',field,bit],((expected[field]>>bit)&1).astype(bool)),(t,upper,field,bit)
                        equalities+=len(readers)
                readers_checked+=len(readers)
    return readers_checked,equalities


def main():
    started=time.monotonic();out=ROOT/'figs/robustness';p=proposed.parameters()
    c_source=ROOT/'Report/proofs/native_clock_island_auxiliary_bounds.c'
    executable=Path('/tmp/SP28_auxiliary_clock_bounds_certificate')
    subprocess.run(['cc','-O3','-std=c11',str(c_source),'-o',str(executable)],check=True)
    completed=subprocess.run([str(executable)],check=True,capture_output=True,text=True)
    rows=[json.loads(line) for line in completed.stdout.splitlines()]
    (out/'SP28_full_clock_island_pulse_run.jsonl').write_text(completed.stdout)
    frames={row['stage']:read_state('/tmp/SP28_auxiliary_clock_'+row['stage']+'.bin',256*p.Q) for row in rows}
    initial,initial_pos=frames['initial'];period,period_pos=frames['period']
    assert np.array_equal(period,np.roll(initial,-23*p.Q,axis=1))
    assert np.array_equal(period_pos,np.roll(initial_pos,-23*p.Q))
    assert all(row['quiet_template'] for row in rows if row['stage']!='first')
    assert [(r['left']//p.Q,r['right_exclusive']//p.Q) for r in rows if r['stage']!='first']==[(128,144),(117,132),(105,121),(105,121)]
    assert rows[-1]['distinct_clock_quorums_checked']==147456
    assert all(r['ambiguous_clock_quorums']==0 for r in rows)
    times=(0,1,2,1791,1792,1793,2048,2049,4095,4096,4097)
    traces={begin+t:read_state('/tmp/SP28_auxiliary_clock_trace_'+str(begin+t)+'.bin',256*p.Q)
            for begin in (0,p.T_wf) for t in times}
    candidate=proposed.load_artifact()
    readers,equalities=literal_corner_updates(candidate,traces)
    monotone_cases,monotone_edges,monotone_nets,fragment_sha=check_monotone_Flag2()
    initialization_cases,initialization_samples=check_recursive_initialization(candidate)
    classification=check_dense_error_class(p)
    dependencies=('SP28_auxiliary_lifetime_certificate.json','SP28_reduced_clock_island_certificate.json',
        'SP28_encoding_family_certificate.json','SP28_encoded_certificate.json')
    auxiliary=json.loads((out/dependencies[0]).read_text())
    assert auxiliary['full_rule_two_clock_alphabet_closure_proved']
    assert auxiliary['full_native_update_matches_reduction_on_all_quiet_rows_proved']
    assert auxiliary['proposed_netlist_sha256']==candidate.comp.digest
    payload={}
    for name,(bits,positions) in frames.items():payload[name]=bits;payload[name+'_code_position']=positions
    for t,(bits,positions) in traces.items():payload['t'+str(t)]=bits;payload['t'+str(t)+'_code_position']=positions
    asset=out/'SP28_full_clock_island_states.npz';np.savez_compressed(asset,**payload)
    proof=ROOT/'Report/proofs/SP28_FULL_CLOCK_ISLAND.md'
    result=dict(proposal='SP28',Q=p.Q,U=p.U,T_wf=p.T_wf,width=candidate.W,
        phase_offset=p.T_wf,epoch_force_window=4096,record_lifetime=1792,
        actual_packet_and_code_dynamics_retained=True,
        backward_force_redundant_under_epoch_force_proved=True,
        WorkspaceFlag1_arbitrary_signal_enclosed_by_literal_guard=True,
        native_flag_interval_monotonicity_proved=True,
        literal_Flag2_monotonicity_assignments=monotone_cases,
        literal_Flag2_monotonicity_directed_edges=monotone_edges,
        literal_Flag2_fragment_sha256=fragment_sha,
        literal_Flag2_monotonicity_netlist_sha256=monotone_nets,
        exhaustive_pulse_rows=12*p.Q,periodic_array_cells=256*p.Q,
        distinct_clock_RF_LF_quorums_checked=147456,ambiguous_clock_output_quorums=0,
        pulse_stage_summaries=rows,force_free_jump_intervals=[[6*p.Q,p.T_wf],[p.T_wf+6*p.Q,p.U]],
        initial_exception_support=[127*p.Q,144*p.Q],label_support_growth_per_row=3,
        flag_and_header_discrepancy_growth_per_row=8,maximum_extra_influence_cells=96*p.Q,
        actual_full_native_infinite_line_pulse_lift_proved=True,
        boundary_native_translation_per_period=-23*p.Q,
        full_autonomous_native_travelling_island_proved=True,
        arbitrary_private_simulation_fields_and_instruction_inputs_allowed=True,
        whole_full_state_period_translation_proved=False,
        supplementary_literal_corner_updates=28,
        supplementary_literal_corner_readers_checked=readers,
        supplementary_literal_corner_bit_equalities=equalities,
        literal_corner_comparisons_are_not_basis_of_universal_projection_proof=True,
        recursive_encoding_cases=initialization_cases,
        recursive_large_coordinate_sample_equalities=initialization_samples,
        recursive_samples_are_not_basis_of_universal_proof=True,
        stationary_intact_SP28_H_in_E_H_proved=True,
        intact_hierarchy_single_finite_physical_error_realization_proved=True,
        physical_error_classification=classification,
        fixed_finite_higher_error_clock_confinement_refuted=True,
        finite_native_clock_eroder_refuted=True,pointwise_eventual_clock_recovery_compatible=True,
        native_GF_correct_all_time=True,restoring_c104_removes_orbit=False,
        G17_or_Gray_or_Gacs_refuted=False,iid_unreliability_proved=False,
        iid_threshold_established=False,global_reliability_established=False,
        smallest_sufficient_reliability_change_proved=False,
        proposed_rule_change=False,active_G17_modified=False,
        checker_sha256=digest(__file__),written_proof_sha256=digest(proof),
        C_source_sha256=digest(c_source),C_executable_sha256=digest(executable),
        proposal_source_sha256=digest(proposed.__file__),
        full_generated_source_sha256=hashlib.sha256(proposed.generated_source(p).encode()).hexdigest(),
        proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        state_asset_sha256=digest(asset),pulse_run_log_sha256=digest(out/'SP28_full_clock_island_pulse_run.jsonl'),
        receipt_dependencies_sha256={name:digest(out/name) for name in dependencies},
        primary_error_definition_text_sha256=digest(ROOT/'papers_txt/gray_readers_guide.txt'),
        compiler_version=subprocess.check_output(['cc','--version'],text=True).splitlines()[0],
        seconds=time.monotonic()-started,
        scope='Full native/header autonomous travelling-clock island with universal workspace enclosure; actual finite higher-error realization; no full-state periodicity or iid/Gray/G17 claim')
    (out/'SP28_full_clock_island_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('distinct_clock_RF_LF_quorums_checked',
        'ambiguous_clock_output_quorums','supplementary_literal_corner_bit_equalities',
        'full_autonomous_native_travelling_island_proved','fixed_finite_higher_error_clock_confinement_refuted',
        'iid_unreliability_proved','seconds')}),flush=True)


if __name__=='__main__':main()
