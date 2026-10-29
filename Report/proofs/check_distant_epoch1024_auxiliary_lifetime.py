#!/usr/bin/env python3
"""Full-SP28 clock alphabet / auxiliary quiet intervals; no island/iid claim."""
from pathlib import Path
import hashlib
import json
import sys
import time
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,Compiled,const_word,majority_word,w_eq_const,w_mux,w_in_range
from gacsca.rule_g import maj5
import proposed_sparse_distant_epoch1024 as proposed


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def primitive_cofactors():
    five=four=0
    for a in range(4):
        for b in range(4):
            if a==b:continue
            for default in (a,b):
                for mask in range(32):
                    n=Net()
                    words=[const_word(b if (mask>>i)&1 else a,2) for i in range(5)]
                    value,exists=majority_word(n,words,const_word(default,2))
                    assert exists==1
                    assert value==const_word(b if mask.bit_count()>=3 else a,2)
                    five+=1
                for mask in range(16):
                    n=Net()
                    values=[(const_word(b if (mask>>i)&1 else a,2),1) for i in range(4)]
                    value,exists=proposed.local.block_quorum(n,values,const_word(default,2))
                    ones=mask.bit_count()
                    expected=b if ones>=3 else a if ones<=1 else default
                    assert value==const_word(expected,2)
                    assert exists==int(ones!=2)
                    four+=1
    assert (five,four)==(768,384)
    return five,four


def canonical_GF_cofactors(p):
    build,source=proposed.proposed_build()
    refinement=native=0
    for phase in range(p.Q):
        n=Net()
        cells={j:dict(addr=const_word((phase+j)%p.Q,p.k),
                     age=[n.input((j,'age',b)) for b in range(p.m)])
               for j in range(-32,33)}
        refined,_=proposed.local.refine_one(n,cells,p,0)
        assert refined['addr']==const_word(phase,p.k)
        refinement+=1
        n=Net()
        cells={j:dict(addr=const_word((phase+j)%p.Q,p.k),
                     age=[n.input((j,'age',b)) for b in range(p.m)],
                     **{f:n.input((j,f)) for f in ('f1','f2','wf1','wf2')})
               for j in range(-5,9)}
        result=build(n,cells,p.k,p.m,Q=p.Q,nb=p.nb,radix=p.R,pos_bits=p.PB,
                     service_force=n.input(('service_force',)))
        assert result['addr']==const_word(phase,p.k)
        refinement_word=const_word(phase,p.k)
        # Full copy wipe is Flag1_new AND inequality with raw self GF.
        from gacsca.netlist import w_eq
        assert n.AND(result['f1'],n.NOT(w_eq(n,refinement_word,cells[0]['addr'])))==0
        native+=1
    return refinement,native,hashlib.sha256(source.encode()).hexdigest()


def full_wiring(p):
    n,comp=proposed.cached(p)
    raw={j:{f:[n.input(('x',j,f,b)) for b in range(w)] for f,w in proposed.schema(p)}
         for j in proposed.local.OFFSETS}
    refined=proposed.local.refine(n,raw,p)
    cells={j:dict(value,**refined[j]) if j in refined else value for j,value in raw.items()}
    service=proposed.service_build(n,{j:dict(packet_tag=cells[j]['packet_tag'],
        packet_valid=cells[j]['packet_valid'][0],packet_count=cells[j]['packet_count'],
        wf2=cells[j]['wf2'][0],flag_valid=cells[j]['service_valid'][0],
        flag_position=cells[j]['service_position'],flag_count=cells[j]['service_count'])
        for j in range(-5,6)},p)
    epoch=proposed.epoch(n,cells,p)
    backward=proposed.pulse(n,cells,p)
    mt=proposed.proposed_build()[0](n,{j:dict(addr=cells[j]['addr'],age=cells[j]['age'],
        **{f:cells[j][f][0] for f in ('f1','f2','wf1','wf2')}) for j in proposed.local.OFFSETS},
        p.k,p.m,Q=p.Q,nb=p.nb,radix=p.R,pos_bits=p.PB,
        service_force=n.any([service['service_force'],epoch['force'],backward['signal']]))
    commit=w_eq_const(n,mt['age_now'],p.age_code(p.U-1))
    keep=n.NOT(commit)
    expected={'addr':mt['addr'],'age':mt['age'],'f1':[mt['f1']],
        'f2':[n.AND(mt['f2'],keep)],
        'wf2':[n.AND(n.OR(epoch['birth'],service['wf2']),keep)],
        'packet_valid':[n.AND(n.OR(epoch['birth'],service['wf2']),keep)],
        'packet_tag':[n.AND(v,keep) for v in w_mux(n,epoch['birth'],epoch['tag'],service['packet_tag'])],
        'packet_count':[n.AND(v,keep) for v in w_mux(n,epoch['birth'],[0]*11,service['packet_count'])],
        'service_valid':[n.AND(service['flag_valid'],keep)],
        'service_position':[n.AND(v,keep) for v in service['flag_position']],
        'service_count':[n.AND(v,keep) for v in service['flag_count']],
        'backward_pressure':[n.AND(backward['signal'],keep)]}
    def info(x):
        return maj5(n,[cells[x-e]['info'][e+2] for e in range(-2,3)])
    signal=0
    for A in range(p.Q-5,p.Q):
        signal=n.OR(signal,n.AND(w_eq_const(n,mt['addr'],A),info(p.Q-3-A)))
    expected['wf1']=[n.all([w_in_range(n,mt['addr'],p.Q-5,p.Q),
        w_in_range(n,mt['age_now'],p.age_code(p.T_wf),p.age_code(p.T_wf+2*p.Q-1)+1),signal])]
    count=0
    for field,word in expected.items():
        for b,value in enumerate(word):
            assert n.outputs['y',field,b]==value,(field,b)
            count+=1
    assert count==73,count
    assert comp.digest==json.loads((ROOT/'figs/robustness/SP28_native_certificate.json').read_text())['proposed_netlist_sha256']
    return count,comp.digest


def service_endpoint_cofactors(p):
    n=Net()
    widths={'packet_tag':4,'packet_valid':1,'packet_count':11,'wf2':1,
            'flag_valid':1,'flag_position':11,'flag_count':11}
    cells={j:{f:n.input((j,f,0)) if w==1 else [n.input((j,f,b)) for b in range(w)]
              for f,w in widths.items()} for j in range(-5,6)}
    result=proposed.service_build(n,cells,p)
    for field,value in result.items():
        for bit,node in enumerate(value if isinstance(value,list) else [value]):n.set_output((field,bit),node)
    comp=Compiled(n)
    masks=np.arange(2048,dtype=np.uint16)
    counters=(0,1,1790,1791,2047)
    cases=0
    for mode in ('packet','code'):
        for counter in counters:
            values={}
            for j in range(-5,6):
                alive=((masks>>(j+5))&1).astype(bool)
                scalars=dict(packet_tag=(j+2)%16,packet_valid=alive if mode=='packet' else False,
                    packet_count=counter,wf2=alive if mode=='packet' else False,
                    flag_valid=alive if mode=='code' else False,flag_position=j+512,flag_count=counter)
                for field,w in widths.items():
                    if w==1:values[j,field,0]=np.full(2048,scalars[field],dtype=bool) if np.isscalar(scalars[field]) else scalars[field]
                    else:
                        for b in range(w):values[j,field,b]=np.full(2048,(scalars[field]>>b)&1,dtype=bool)
            outputs=comp.evaluate(values,bool)
            vote_bits=range(3,8) if mode=='packet' else range(11)
            quorum=sum(((masks>>b)&1) for b in vote_bits)>=3
            qualifies=quorum&(counter<1791)
            expected_packet=qualifies if mode=='packet' else np.zeros(2048,dtype=bool)
            assert np.array_equal(outputs['packet_valid',0],expected_packet)
            assert np.array_equal(outputs['wf2',0],expected_packet)
            assert np.array_equal(outputs['flag_valid',0],qualifies)
            any_packet=quorum if mode=='packet' else np.zeros(2048,dtype=bool)
            assert np.array_equal(outputs['packet_any_cohort',0],any_packet)
            assert np.array_equal(outputs['service_force',0],qualifies|any_packet)
            for b in range(11):
                assert np.array_equal(outputs['packet_count',b],expected_packet&bool(((counter+1)>>b)&1))
                assert np.array_equal(outputs['flag_count',b],qualifies&bool(((counter+1)>>b)&1))
                position=8 if mode=='packet' else 512
                assert np.array_equal(outputs['flag_position',b],qualifies&bool((position>>b)&1))
            for b in range(4):assert np.array_equal(outputs['packet_tag',b],expected_packet&bool((2>>b)&1))
            cases+=2048
    assert cases==20480
    return cases,comp.digest


def clock_windows(p):
    times=np.arange(p.U,dtype=np.int64)
    phases=np.stack((times,(times+p.T_wf)%p.U))
    births=(phases==p.T_wf).any(axis=0)
    assert np.flatnonzero(births).tolist()==[0,p.T_wf]
    forces=((p.T_wf<=phases)&(phases<p.T_wf+4096)).any(axis=0)
    expected=np.zeros(p.U,dtype=bool)
    expected[:4096]=True
    expected[p.T_wf:p.T_wf+4096]=True
    assert np.array_equal(forces,expected)
    backward=((p.T_wf<=phases)&(phases<=p.T_wf+1792)).any(axis=0)
    workspace_output=((p.T_wf<=phases)&(phases<p.T_wf+2*p.Q)).any(axis=0)
    assert not np.any(backward&~forces)
    workspace_input=np.roll(workspace_output,1)
    assert not np.any(workspace_input&~forces)
    codes=np.array([p.age_code(t) for t in times],dtype=np.uint32)
    assert len(np.unique(codes))==p.U
    assert not np.any(codes==np.roll(codes,-p.T_wf))
    assert min(p.T_wf,p.U-p.T_wf)==196735>4096>1794
    return p.U


def main():
    started=time.monotonic()
    p=proposed.parameters()
    assert (p.Q,p.U,p.T_wf,p.R)==(1024,475136,278401,928)
    five,four=primitive_cofactors()
    refinement,native,native_source=canonical_GF_cofactors(p)
    wiring,netlist=full_wiring(p)
    service_cases,service_net=service_endpoint_cofactors(p)
    clocks=clock_windows(p)
    proof=ROOT/'Report/proofs/SP28_TWO_CLOCK_AUXILIARY_LIFETIME.md'
    old=ROOT/'figs/robustness/SP28_native_certificate.json'
    assert json.loads(old.read_text())['legal_clock_increment_cases']==p.U
    framed=proposed.framed_build(p)
    assert framed.__globals__['Q']==1029
    assert framed.__globals__['POSITION_BITS']==11
    assert framed.__globals__['LIFETIME']==1792
    result=dict(proposal='SP28',Q=p.Q,U=p.U,T_wf=p.T_wf,
        epoch_force_window=4096,record_lifetime=1792,minimum_birth_batch_gap=196735,
        arbitrary_Age_GF_refinement_cofactors=refinement,
        arbitrary_Age_flags_and_service_native_GF_cofactors=native,
        five_vote_two_label_primitive_cofactors=five,
        four_vote_two_label_primitive_cofactors=four,
        full_literal_native_and_auxiliary_wiring_identities=wiring,
        restricted_service_endpoint_cofactors=service_cases,
        restricted_service_endpoint_counters=[0,1,1790,1791,2047],
        service_endpoint_scope='one aligned packet or coded origin; all2048 alive masks; universal ancestry proved separately in written proof',
        legal_clock_rows_and_force_windows_checked=clocks,
        possible_birth_rows_mod_U=[0,p.T_wf],
        quiet_input_row_intervals_mod_U=[[4096,p.T_wf],[p.T_wf+4096,p.U]],
        last_possible_valid_record_state_offset=1792,
        all_record_headers_zero_from_state_offset=1793,
        last_possible_computed_packet_or_code_force_input_offset=1792,
        backward_pressure_zero_from_state_offset=1794,
        WorkspaceFlag1_zero_from_state_offset=2049,
        no_further_errors_required=True,initial_GF_canonical_required=True,
        initial_two_legal_Age_phases_required_for_auxiliary_theorem=True,
        initial_Workspace_flags_and_validities_and_backward_zero_required=True,
        arbitrary_private_workspace_native_flags_and_I_allowed=True,
        global_canonical_GF_and_keep_closure_proved=True,
        full_rule_two_clock_alphabet_closure_proved=True,
        counter_ancestry_auxiliary_lifetime_proved=True,
        full_native_update_matches_reduction_on_all_quiet_rows_proved=True,
        pulse_output_aligned_template_proved=False,
        full_autonomous_travelling_clock_island_realization_proved=False,
        full_rule_finite_island_eroder_refuted=False,
        finite_island_confinement_proved=False,higher_noise_lift_proved=False,
        iid_threshold_established=False,global_reliability_established=False,
        Gray_or_Gacs_refuted=False,proposed_rule_change=False,active_G17_modified=False,
        checker_sha256=digest(__file__),written_proof_sha256=digest(proof),
        proposal_source_sha256=digest(proposed.__file__),
        distant_refinement_source_sha256=digest(proposed.local.__file__),
        service_source_sha256=digest(ROOT/'Report/proofs/proposed_framed_service.py'),
        buffered_service_source_sha256=digest(ROOT/'Report/proofs/proposed_buffered_framed_service.py'),
        backward_source_sha256=digest(ROOT/'Report/proofs/proposed_backward_pressure448.py'),
        netlist_helpers_sha256=digest(ROOT/'gacsca/netlist.py'),
        literal_native_maintenance_source_sha256=native_source,
        full_generated_source_sha256=hashlib.sha256(proposed.generated_source(p).encode()).hexdigest(),
        proposed_netlist_sha256=netlist,service_component_netlist_sha256=service_net,
        prior_native_wiring_receipt_sha256=digest(old),
        seconds=time.monotonic()-started,
        scope='Full-rule structural clock/auxiliary theorem without new errors; quiet-row reduction only, not pulse/orbit/confinement/iid theorem')
    (ROOT/'figs/robustness/SP28_auxiliary_lifetime_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('arbitrary_Age_GF_refinement_cofactors',
        'arbitrary_Age_flags_and_service_native_GF_cofactors',
        'full_literal_native_and_auxiliary_wiring_identities','restricted_service_endpoint_cofactors',
        'full_native_update_matches_reduction_on_all_quiet_rows_proved',
        'full_autonomous_travelling_clock_island_realization_proved','seconds')}),flush=True)


if __name__=='__main__':main()
