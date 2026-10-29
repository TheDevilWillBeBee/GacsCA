#!/usr/bin/env python3
"""Full-SP28 Address-phase travelling island; no iid or G17 claim."""
from pathlib import Path
import hashlib,json,subprocess,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,const_word
import proposed_sparse_distant_epoch1024 as proposed
import check_distant_epoch1024_full_clock_island as clock

LABEL,F1LO,F1HI,F2LO,F2HI,WF1HI=range(6)
DELTA=512

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read_state(path,N):
    raw=Path(path).read_bytes();assert len(raw)==6*N
    return np.frombuffer(raw,dtype=np.uint8).reshape(6,N).copy()

def template(x,p):
    a=128*p.Q-DELTA;b=144*p.Q
    return int(a<=x<b),int(127*p.Q<=x<a or b-DELTA<=x<b)

def quiet_cofactors(p):
    a=128*p.Q-DELTA;b=144*p.Q
    refine_cases=native_cases=0;build,source=proposed.proposed_build()
    for edge in (a,b):
        for x in range(edge-40,edge+41):
            n=Net();age=[n.input(('free_common_clock',k)) for k in range(p.m)]
            cells={j:dict(addr=const_word((x+j+DELTA*template(x+j,p)[0])%p.Q,p.k),age=age)
                   for j in range(-32,33)}
            got,_=proposed.local.refine_one(n,cells,p,0)
            assert got['addr']==cells[0]['addr'] and got['age']==age
            refine_cases+=1
    readers=sorted(set(range(a-p.Q-40,a+p.Q+41))|set(range(b-p.Q-40,b+p.Q+41)))
    for x in readers:
        n=Net();age=[n.input(('free_common_clock',k)) for k in range(p.m)]
        cells={j:dict(addr=const_word((x+j+DELTA*template(x+j,p)[0])%p.Q,p.k),age=age,
                     f1=template(x+j,p)[1],f2=0,wf1=0,wf2=0) for j in range(-5,9)}
        got=build(n,cells,p.k,p.m,Q=p.Q,nb=p.nb,radix=p.R,pos_bits=p.PB,service_force=0)
        assert got['addr']==cells[0]['addr'] and got['age_now']==age
        assert got['f1']==template(x,p)[1] and got['f2']==0
        native_cases+=1
    assert (refine_cases,native_cases)==(162,4258)
    return refine_cases,native_cases,hashlib.sha256(source.encode()).hexdigest()

def literal_corner_updates(candidate,traces):
    p=candidate.p;comp=candidate.comp;N=256*p.Q
    readers_checked=equalities=0
    offsets=(0,1,1791,1792,2047,2048,4095,4096)
    for offset in offsets:
        t=p.T_wf+offset;old=traces[t];new=traces[t+1]
        edges=np.flatnonzero(old[LABEL]!=np.roll(old[LABEL],1))
        ones=np.flatnonzero(old[LABEL]);mid=(int(ones[len(ones)//2])//p.Q)*p.Q
        readers=np.array(sorted(set([int(x)+d for x in edges for d in range(-40,41)]+
            list(range(mid,mid+p.Q))+list(range(16*p.Q,17*p.Q)))),dtype=np.int64)
        for upper in (False,True):
            f1plane=F1HI if upper else F1LO;f2plane=F2HI if upper else F2LO
            values={}
            for name in comp.inputs:
                if name[0]!='x':value=np.zeros(len(readers),dtype=bool)
                else:
                    _,off,field,bit=name;sites=(readers+off)%N
                    if field=='addr':word=(sites+DELTA*old[LABEL,sites].astype(np.int64))%p.Q
                    elif field=='age':word=np.full(len(readers),p.age_code(t%p.U),dtype=np.int64)
                    elif field=='f1':word=old[f1plane,sites]
                    elif field=='f2':word=old[f2plane,sites]
                    elif field=='wf1':word=old[WF1HI,sites] if upper else np.zeros(len(readers),dtype=np.uint8)
                    else:word=np.zeros(len(readers),dtype=np.uint8)
                    value=((word>>bit)&1).astype(bool)
                values[name]=value
            got=comp.evaluate(values,bool)
            expected=dict(addr=(readers+DELTA*new[LABEL,readers].astype(np.int64))%p.Q,
                age=np.full(len(readers),p.age_code((t+1)%p.U),dtype=np.int64),
                f1=new[f1plane,readers],f2=new[f2plane,readers])
            for field,width in (('addr',p.k),('age',p.m),('f1',1),('f2',1)):
                for bit in range(width):
                    assert np.array_equal(got['y',field,bit],((expected[field]>>bit)&1).astype(bool)),(t,upper,field,bit)
                    equalities+=len(readers)
            readers_checked+=len(readers)
    return readers_checked,equalities

def main():
    start=time.monotonic();out=ROOT/'figs/robustness';p=proposed.parameters()
    source=ROOT/'Report/proofs/native_address_island_auxiliary_bounds.c'
    executable=Path('/tmp/SP28_Address_bounds_certificate')
    subprocess.run(['cc','-O3','-std=c11',str(source),'-o',str(executable)],check=True)
    run=subprocess.run([str(executable),str(DELTA)],check=True,capture_output=True,text=True)
    log=out/'SP28_full_Address_island_pulse_run.jsonl';log.write_text(run.stdout)
    rows=[json.loads(line) for line in run.stdout.splitlines()]
    N=256*p.Q
    frames={row['stage']:read_state('/tmp/SP28_Address_bounds_'+row['stage']+'.bin',N) for row in rows}
    assert np.array_equal(frames['period'],np.roll(frames['initial'],-12*p.Q,axis=1))
    assert all(row['quiet_template'] for row in rows)
    assert [(r['left'],r['right_exclusive']) for r in rows]==[(128*p.Q-DELTA,144*p.Q),
        (116*p.Q-DELTA,132*p.Q),(116*p.Q-DELTA,132*p.Q)]
    assert rows[-1]['distinct_Address_quorums']==73728
    offsets=(0,1,2,1791,1792,1793,2047,2048,2049,4095,4096,4097)
    traces={p.T_wf+t:read_state('/tmp/SP28_Address_bounds_trace_'+str(p.T_wf+t)+'.bin',N) for t in offsets}
    candidate=proposed.load_artifact()
    refine_cases,native_cases,native_sha=quiet_cofactors(p)
    readers,equalities=literal_corner_updates(candidate,traces)
    mono_cases,mono_edges,_,_=clock.check_monotone_Flag2()
    classification=clock.check_dense_error_class(p)
    classification['universal_proof']='SP28_FULL_ADDRESS_ISLAND.md and the same dense-row classification proved in SP28_FULL_CLOCK_ISLAND.md'
    dependencies=('SP28_full_clock_island_certificate.json','SP28_auxiliary_lifetime_certificate.json',
                  'SP28_native_certificate.json','SP28_encoding_family_certificate.json')
    payload={**frames,**{'t'+str(t):state for t,state in traces.items()}}
    asset=out/'SP28_full_Address_island_states.npz';np.savez_compressed(asset,**payload)
    result=dict(proposal='SP28',Q=p.Q,U=p.U,T_wf=p.T_wf,width=candidate.W,Address_displacement=DELTA,
        common_legal_clock_and_two_Address_phase_alphabet_closure_proved=True,
        packet_code_backward_forces_redundant_within_global_epoch_proved=True,
        no_auxiliary_force_outside_global_epoch_proved=True,
        arbitrary_private_fields_and_instruction_inputs_allowed=True,
        WF1_arbitrary_signal_enclosed_by_literal_GF_clock_guard=True,
        native_flag_monotone_enclosure_proved=True,
        exact_quiet_refinement_cofactors=refine_cases,exact_quiet_native_cofactors=native_cases,
        native_maintenance_generated_source_sha256=native_sha,
        literal_Flag2_monotone_assignments=mono_cases,literal_Flag2_monotone_edges=mono_edges,
        exhaustive_pulse_rows=6*p.Q,periodic_array_cells=N,distinct_Address_output_quorums=73728,
        ambiguous_Address_output_quorums=0,pulse_summaries=rows,
        force_free_jump_intervals=[[0,p.T_wf],[p.T_wf+6*p.Q,p.U]],
        Address_support_growth_per_row=3,flag_discrepancy_growth_per_row=8,
        maximum_extra_influence_cells=48*p.Q,infinite_line_pulse_lift_proved=True,
        full_autonomous_native_Address_travelling_island_proved=True,
        boundary_Address_translation_per_period=-12*p.Q,wrong_Address_sites_each_boundary=16*p.Q+DELTA,
        high_Address_bit_wrong_on_whole_island=True,whole_full_state_periodicity_proved=False,
        supplementary_full_native_corner_updates=16,supplementary_full_native_corner_readers=readers,
        supplementary_full_native_corner_bit_equalities=equalities,
        supplementary_corners_are_not_basis_of_universal_projection_proof=True,
        intact_recursive_hierarchy_single_physical_error_realization_proved=True,
        physical_error_classification=classification,
        fixed_finite_higher_error_Address_confinement_refuted=True,
        finite_native_Address_eroder_refuted=True,pointwise_eventual_Address_recovery_compatible=True,
        restoring_c104_removes_orbit=False,
        changing_only_private_programme_or_ROM_while_preserving_projection_removes_orbit=False,
        G17_or_Gray_or_Gacs_refuted=False,iid_unreliability_proved=False,
        iid_threshold_established=False,global_reliability_established=False,
        smallest_sufficient_reliability_change_proved=False,proposed_rule_change=False,active_G17_modified=False,
        checker_sha256=digest(__file__),written_proof_sha256=digest(ROOT/'Report/proofs/SP28_FULL_ADDRESS_ISLAND.md'),
        C_source_sha256=digest(source),C_executable_sha256=digest(executable),
        proposal_source_sha256=digest(proposed.__file__),proposed_candidate_sha256=candidate.digest(),
        proposed_netlist_sha256=candidate.comp.digest,
        full_generated_source_sha256=hashlib.sha256(proposed.generated_source(p).encode()).hexdigest(),
        reused_monotonicity_and_classification_checker_sha256=digest(clock.__file__),
        state_asset_sha256=digest(asset),pulse_run_log_sha256=digest(log),
        receipt_dependencies_sha256={name:digest(out/name) for name in dependencies},
        seconds=time.monotonic()-start,
        scope='Full autonomous native Address-phase/common-Age island; universal private/WF1 enclosure, intact finite error realization; no G17/Gray/iid theorem')
    (out/'SP28_full_Address_island_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('exact_quiet_refinement_cofactors','exact_quiet_native_cofactors',
        'supplementary_full_native_corner_bit_equalities','full_autonomous_native_Address_travelling_island_proved',
        'iid_unreliability_proved','seconds')}),flush=True)

if __name__=='__main__':main()
