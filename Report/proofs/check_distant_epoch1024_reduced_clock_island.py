#!/usr/bin/env python3
"""Exact reduced native/epoch orbit; no autonomous full-rule/iid claim."""
from pathlib import Path
import hashlib,json,subprocess,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,const_word
import proposed_sparse_distant_epoch1024 as proposed


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def quiet_cofactors(p):
    refine_count=native_count=0
    build,source=proposed.proposed_build()
    clock=[6*p.Q,p.T_wf+6*p.Q]
    assert all(not(p.T_wf<=x<p.T_wf+4096) for x in clock)
    for orientation in (0,1):
        def label(x):return orientation if x<0 else 1-orientation
        for x in range(-37,38):
            n=Net()
            cells={j:dict(addr=const_word((x+j)%p.Q,p.k),
                age=const_word(p.age_code(clock[label(x+j)]),p.m))
                for j in range(-32,33)}
            result,_=proposed.local.refine_one(n,cells,p,0)
            assert result['addr']==const_word(x%p.Q,p.k)
            assert result['age']==const_word(p.age_code(clock[label(x)]),p.m)
            refine_count+=1
        for x in range(-p.Q-8,p.Q+9):
            n=Net()
            cells={j:dict(addr=const_word((x+j)%p.Q,p.k),
                age=const_word(p.age_code(clock[label(x+j)]),p.m),
                f1=int(-p.Q<=x+j<0),f2=0,wf1=0,wf2=0)
                for j in range(-5,9)}
            epoch=proposed.epoch(n,cells,p)
            assert epoch['force']==0
            result=build(n,cells,p.k,p.m,Q=p.Q,nb=p.nb,radix=p.R,
                         pos_bits=p.PB,service_force=epoch['force'])
            assert result['addr']==const_word(x%p.Q,p.k),(orientation,x,'GF')
            assert result['age']==const_word(p.age_code(clock[label(x)]+1),p.m),(orientation,x,'Age')
            assert result['f1']==int(-p.Q<=x<0),(orientation,x,'Flag1')
            assert result['f2']==0,(orientation,x,'Flag2')
            native_count+=1
    assert (refine_count,native_count)==(150,4130)
    return refine_count,native_count,hashlib.sha256(source.encode()).hexdigest()


def full_first_update(candidate,initial,first):
    p=candidate.p;comp=candidate.comp;N=initial.shape[1]
    centers=(128*p.Q,144*p.Q)
    readers=sorted(set([x+d for x in centers for d in range(-40,41)]+
                       [p.Q+d for d in (0,1,2,3,4,5,6,p.Q-8,p.Q-5,p.Q-1)]))
    values={}
    codes=np.asarray([p.age_code(t) for t in (0,p.T_wf)],dtype=np.int64)
    for name in comp.inputs:
        if name[0]=='x':
            _,off,field,bit=name
            sites=(np.asarray(readers)+off)%N
            if field=='addr':v=((sites%p.Q)>>bit)&1
            elif field=='age':v=(codes[initial[0,sites]]>>bit)&1
            elif field=='f1':v=initial[1,sites]
            elif field=='f2':v=initial[2,sites]
            else:v=np.zeros(len(readers),dtype=bool)
            values[name]=np.asarray(v,dtype=bool)
        else:values[name]=np.zeros(len(readers),dtype=bool)
    outputs=comp.evaluate(values,bool)
    equalities=0
    for idx,x in enumerate(readers):
        label=int(first[0,x])
        expected={'addr':x%p.Q,'age':p.age_code(1+label*p.T_wf),
                  'f1':int(first[1,x]),'f2':int(first[2,x])}
        for field,width in (('addr',p.k),('age',p.m),('f1',1),('f2',1)):
            for bit in range(width):
                assert int(outputs['y',field,bit][idx])==((expected[field]>>bit)&1),(x,field,bit)
                equalities+=1
    return len(readers),equalities


def main():
    started=time.monotonic();out=ROOT/'figs/robustness';p=proposed.parameters()
    source=ROOT/'Report/proofs/native_clock_island_reduced.c'
    executable=Path('/tmp/SP28_native_clock_reduced')
    subprocess.run(['cc','-O3','-std=c11',str(source),'-o',str(executable)],check=True)
    computation=subprocess.run([str(executable)],check=True,capture_output=True,text=True)
    rows=[json.loads(x) for x in computation.stdout.splitlines()]
    frames={row['stage']:np.fromfile('/tmp/SP28_native_clock_'+row['stage']+'.bin',dtype=np.uint8)
            .reshape(3,256*p.Q) for row in rows}
    initial,period=frames['initial'],frames['period']
    assert np.array_equal(period,np.roll(initial,-23*p.Q,axis=1))
    assert all(row['quiet_template'] for row in rows if row['stage']!='first')
    assert [(row['left']//p.Q,row['right_exclusive']//p.Q) for row in rows if row['stage']!='first']==[
        (128,144),(117,132),(105,121),(105,121)]
    refinement,native,native_source=quiet_cofactors(p)
    clocks=np.arange(p.U,dtype=np.int64)
    active=[(p.T_wf<=(clocks+k*p.T_wf)%p.U)&((clocks+k*p.T_wf)%p.U<p.T_wf+4096)
            for k in (0,1)]
    jumps=[(6*p.Q,p.T_wf),(p.T_wf+6*p.Q,p.U)]
    for left,right in jumps:assert not np.any(active[0][left:right]|active[1][left:right])
    candidate=proposed.load_artifact()
    readers,equalities=full_first_update(candidate,initial,frames['first'])
    proof=ROOT/'Report/proofs/SP28_REDUCED_CLOCK_ISLAND.md'
    asset=out/'SP28_reduced_clock_island_states.npz'
    np.savez_compressed(asset,**frames)
    native_receipt=out/'SP28_native_certificate.json'
    pinned=json.loads(native_receipt.read_text())
    assert pinned['full_output_native_wiring_identities']==29
    assert pinned['proposed_netlist_sha256']==candidate.comp.digest
    result=dict(proposal='SP28',reduced_operator='native/epoch with zero auxiliary inputs',Q=p.Q,U=p.U,T_wf=p.T_wf,
        epoch_force_window=4096,raw_GF_always_canonical=True,
        phase_offset=p.T_wf,two_legal_clock_labels=True,
        Workspace_and_packet_code_backward_inputs_constrained_zero_every_row=True,
        native_Flag1_and_Flag2_evolved=True,only_epoch_service_force_retained=True,
        native_Flag2_commit_reset_retained=True,
        native_reduction_general_word_proof='SP28_REDUCED_CLOCK_ISLAND.md; canonical GF, two distinct clock labels, literal count/equality predicates',
        exact_refinement_quiet_template_cofactors=refinement,
        exact_native_epoch_quiet_template_cofactors=native,
        legal_clock_rows_checked_for_exact_force_free_jumps=p.U,
        force_free_jump_intervals=jumps,
        exhaustive_pulse_rows=12*p.Q,periodic_array_cells=256*p.Q,
        initial_finite_native_exception_support=[127*p.Q,144*p.Q],
        label_support_growth_bound_per_row=3,flag_discrepancy_growth_bound_per_row=8,
        maximum_extra_flag_influence_cells=96*p.Q,
        infinite_line_pulse_lift_proved=True,stage_summaries=rows,
        first_full_literal_netlist_readers_checked=readers,
        first_full_literal_native_bit_equalities=equalities,
        literal_first_step_check_is_supplementary=True,
        exact_reduced_period_translation_cells=-23*p.Q,
        exact_reduced_all_period_travelling_clock_island_proved=True,
        reduced_native_finite_island_eroder_refuted=True,
        pointwise_eventual_recovery_compatible=True,
        full_autonomous_SP28_realization_proved=False,
        full_rule_finite_island_eroder_refuted=False,
        iid_unreliability_proved=False,Gray_or_Gacs_refuted=False,
        sufficient_reliability_rule_change_proved=False,global_reliability_established=False,
        proposed_rule_change=False,active_G17_modified=False,
        checker_sha256=digest(__file__),C_source_sha256=digest(source),
        C_executable_sha256=digest(executable),written_proof_sha256=digest(proof),
        proposal_source_sha256=digest(proposed.__file__),
        distant_native_refinement_source_sha256=digest(proposed.local.__file__),
        literal_native_maintenance_source_sha256=native_source,
        full_generated_source_sha256=hashlib.sha256(proposed.generated_source(p).encode()).hexdigest(),
        native_wiring_receipt_sha256=digest(native_receipt),
        proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        state_asset_sha256=digest(asset),compiler_version=subprocess.check_output(['cc','--version'],text=True).splitlines()[0],
        seconds=time.monotonic()-started,
        scope='Exact all-time travelling clock island of the explicitly auxiliary-zero reduced operator; not an autonomous SP28, Gray or iid counterexample')
    (out/'SP28_reduced_clock_island_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('exact_refinement_quiet_template_cofactors',
        'exact_native_epoch_quiet_template_cofactors','exact_reduced_period_translation_cells',
        'reduced_native_finite_island_eroder_refuted','full_autonomous_SP28_realization_proved','seconds')}),flush=True)


if __name__=='__main__':main()
