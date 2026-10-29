#!/usr/bin/env python3
"""Pin full emitted components, exact failed-prefix recurrence and E0 counts.

No all-raw own-beta theorem is inferred from finite execution comparisons.
Earlier accepted receipts are read only. This writes a separate audit receipt.
"""
from pathlib import Path
from itertools import combinations
from dataclasses import replace
from collections import Counter
import hashlib,json,sys,time
import numpy as np

ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
import gray_moving_word_v1 as k1
import build_gray_moving_word_v1 as b1
import gray_moving_word_v2 as k
import build_gray_moving_word_v2 as builder
from gacsca import candidates


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def flag_capacity():
    """Exhaust binary native flags with at most two arbitrary fault holders.

    Correct GF/Age votes/existence and discrepancy<=2 are mathematical
    word-majority premises, not restricted numerical replacement values.
    Canonical inside masks have exactly these eleven boundary classes.
    """
    sites=tuple(range(-5,6));phases=tuple(range(6))+tuple(range(k.Q-5,k.Q))
    count=0
    for phase in phases:
        inside={j:0<=phase+j<k.Q for j in sites}
        for size in range(3):
            for faults in combinations(sites,size):
                for assignment in range(1<<(4*size)):
                    flags={j:tuple((assignment>>(4*i+b))&1 for b in range(4))
                        for i,j in enumerate(faults)}
                    def f(j,b):return flags.get(j,(0,0,0,0))[b]
                    r1=sum(inside[j] and f(j,0) for j in range(1,6))
                    w1=sum(inside[j] and f(j,2) for j in sites)>=3
                    nf1=bool(w1 or r1>=3 or (f(0,0) and r1>=2))
                    left=sum(inside[j] and f(j,1) for j in range(-5,0))
                    source4=sum(inside[j] and f(j,3) for j in sites)>=3
                    on=left>=4 or (nf1 and sum(f(j,1) for j in range(-5,0))>=4) or source4
                    erase=(not nf1 and left<=1) or (nf1 and not any(f(j,1) for j in range(-5,0)))
                    nf2=bool(source4 or not erase) if f(0,1) else bool(on)
                    assert not nf1 and not nf2
                    count+=1
    # The bitwise vote lemma handles every coherent SF word bit and every
    # arbitrary assignment at up to two faulty holders, hence all widths.
    votes=0
    for correct in (0,1):
        for size in range(3):
            for faults in combinations(range(5),size):
                for assignment in range(1<<size):
                    values=[correct]*5
                    for i,j in enumerate(faults):values[j]=(assignment>>i)&1
                    assert k.old.vote(values)==correct
                    votes+=1
    return count,votes


def validate_assets(directory):
    original=json.loads((directory/'GMW1_full_own_overflow.json').read_text())
    code1,listing1,labels1,errors1=b1.programme().assemble()
    stored1=json.loads((directory/'GMW1_full_own_attempt_listing.json').read_text())
    assert (len(code1),len(listing1),len(errors1))==(42850,1829,268)
    assert stored1['instructions']==listing1 and stored1['labels']==labels1
    assert stored1['out_of_range_references']==errors1
    assert stored1['code_capacity']==k1.Q==8192
    encoded1=np.unpackbits(np.frombuffer((directory/'GMW1_full_own_invalid_masked_beta.bin').read_bytes(),np.uint8),bitorder='little')
    assert encoded1[:len(code1)].tolist()==code1 and not np.any(encoded1[len(code1):])
    for name,value in original['sources_sha256'].items():
        assert value==digest(ROOT/name)
        assert value==digest(directory/(Path(name).name+'.first_full_overflow.txt'))
    assert original['listing_sha256']==digest(directory/'GMW1_full_own_attempt_listing.json')
    assert original['invalid_masked_bitstream_sha256']==digest(directory/'GMW1_full_own_invalid_masked_beta.bin')
    assert not original['masked_bitstream_is_valid_own_beta']
    assert not original['full_emission_semantic_correctness_proved']

    code,listing,labels,errors=builder.programme().assemble()
    beta=tuple(code+[0]*(k.CODE_CAPACITY-len(code)))
    assert (len(code),len(listing),len(errors),k.FRAME_BITS,k.HEAD_BITS)==(44730,1863,0,2007,379)
    assert 2*k.FRAME_BITS<=k.Q and len(code)>k.Q and len(beta)==65536
    stored=json.loads((directory/'GMW2_full_own_listing.json').read_text())
    assert stored==dict(code_capacity=k.CODE_CAPACITY,programme_bits=len(code),instructions=listing,labels=labels,errors=errors)
    encoded=np.unpackbits(np.frombuffer((directory/'GMW2_full_own_beta.bin').read_bytes(),np.uint8),bitorder='little')
    assert encoded.tolist()==list(beta)
    for row in listing:
        actual=k.decode(k.beta_word(beta,row['address'],29))
        expected=(row['opcode'],tuple(v&((1<<w)-1) for v,w in zip(row['operands'],k.ARGS[row['opcode']])))
        assert actual==expected and k.instruction_length(k.beta_word(beta,row['address'],29))==row['bits']
    record=json.loads((directory/'GMW2_full_own_certificate.json').read_text())
    for name,path in (('kernel_sha256',k.__file__),('builder_sha256',builder.__file__),
                      ('checker_sha256',ROOT/'Report/proofs/gray_counterexamples/check_gray_moving_word_v2.py'),
                      ('beta_sha256',directory/'GMW2_full_own_beta.bin'),
                      ('listing_sha256',directory/'GMW2_full_own_listing.json'),
                      ('replays_sha256',directory/'GMW2_full_own_replays.npz')):
        assert record[name]==digest(path)
    assert record['uninterrupted_word_evaluator_replays']==70 and record['replays_measured_only']
    assert not record['full_own_programme_equivalence_proved']
    assert not record['initial_upper_state_is_intact_recursive_hierarchy']
    assert not record['uninterrupted_full_execution_after_active_end_is_actual_GMW2_execution']
    assert record['rotating_holder_prefix_counts']==[13107]*5

    old=json.loads((directory/'GMW2_first56_full_own_certificate.json').read_text())
    assert old['kernel_sha256']==digest(k.__file__) and old['builder_sha256']==digest(builder.__file__)
    assert old['checker_sha256']==digest(directory/'check_gray_moving_word_v2.py.first56.txt')
    for key,filename in (('beta_sha256','GMW2_full_own_beta.bin.first56'),
                         ('listing_sha256','GMW2_full_own_listing.json.first56'),
                         ('replays_sha256','GMW2_full_own_replays.npz.first56')):
        assert old[key]==digest(directory/filename)
    assert old['physical_preloaded_evaluator_replays']==56
    for serial in range(1,4):
        stem='GMW2_semantic_failure_%02d'%serial
        failure=json.loads((directory/(stem+'.json')).read_text())
        assert failure['asset_sha256']==digest(directory/(stem+'.npz'))
        for filename,value in failure['source_snapshots_sha256'].items():assert value==digest(directory/filename)
        with np.load(directory/(stem+'.npz')) as asset:
            assert np.flatnonzero(asset['actual']!=asset['expected']).tolist()==failure['different_field_bits']
            assert len(asset['beta'])==failure['programme_bits']
        assert not failure['Gray_or_iid_failure_proved'] and not failure['full_own_programme_equivalence_proved']
    for name in ('GMW2_initial_audit_api_failure.json','GMW2_second_audit_receipt_key_failure.json'):
        failure=json.loads((directory/name).read_text())
        assert failure['preserved_checker_sha256']==digest(directory/failure['preserved_checker'])
        assert not failure['rule_or_programme_changed'] and not failure['Gray_or_iid_failure']
    return beta,record


def validate_prefix(directory,beta):
    with np.load(directory/'GMW2_full_own_replays.npz') as a:
        assert a['input_bits'].shape==(70,11,2007) and a['outputs'].shape==(70,2007)
        for data,result in zip(a['input_bits'],a['outputs']):
            cells={j:k.cell_from_bits(data[j+5].tolist()) for j in range(-5,6)}
            assert result.tolist()==k.cell_bits(k.local_transition(cells,beta))
        assert a['ticks'][0]==102026
        cells={j:k.cell_from_bits(a['input_bits'][0,j+5].tolist()) for j in range(-5,6)}
        assert all(c.addr==j%k.Q and c.age==0 and not any(k.cell_bits(c)[13:]) for j,c in cells.items())
        expected=k.cell_bits(k.local_transition(cells,beta))
        assert expected==a['truncated_expected'].tolist()
        assert np.flatnonzero(a['truncated_output']!=a['truncated_expected']).tolist()==[2006]
        assert expected[2006]==beta[2]==1
        assert k.PRIMARY_START+2006==5099
        tape=k.input_tape(cells);out={};scratch={};position=k.HEAD_ADDRESS;p=k.initial_packet()
        assert a['prefix_before'].shape==a['prefix_after'].shape==(65535,48)
        assert np.array_equal(a['prefix_before'][1:],a['prefix_after'][:-1])
        assert np.array_equal(a['prefix_addresses'],a['truncated_positions'])
        for i,(address,before,after,ow,sw) in enumerate(zip(a['prefix_addresses'],a['prefix_before'],
                a['prefix_after'],a['prefix_out_writes'],a['prefix_scratch_writes'])):
            address=int(address)
            assert k.pack(p)==int.from_bytes(before.tobytes(),'little')
            assert address==position+(1 if p.move==1 else -1 if p.move==2 else 0)
            assert 0<=address<k.Q
            p,written,temp=k.step_packet(p,address,tape.get(address,0),out.get(address,0),
                scratch.get(address,0),beta[address],beta)
            assert k.pack(p)==int.from_bytes(after.tobytes(),'little')
            assert int(ow)==(-1 if written is None else written)
            assert int(sw)==(-1 if temp is None else temp)
            if written is not None:out[address]=written
            if temp is not None:scratch[address]=temp
            position=address
        assert p.mode==k.LOAD and p.pc==43130 and out.get(5099,0)==0
        assert [out.get(k.PRIMARY_START+i,0) for i in range(k.FRAME_BITS)]==a['truncated_output'].tolist()
        def physical(x,age):
            return {j:k.Cell(addr=(x+j)%k.Q,age=age,
                heads=tuple(k.pack(p) if x+j+s==position else 0 for s in k.SLOTS),
                mem=tuple(tape.get(x+j+s,0) for s in k.SLOTS),
                out=tuple(out.get(x+j+s,0) for s in k.SLOTS),
                scratch=tuple(scratch.get(x+j+s,0) for s in k.SLOTS),
                program=tuple(beta[(x+j+s)%k.Q] for s in k.SLOTS)) for j in range(-5,6)}
        rest=k.local_transition(physical(position,120*k.Q),beta)
        assert rest.heads[0]==k.pack(p)
        for q,s in enumerate(k.SLOTS):
            committed=k.local_transition(physical(5099-s,k.U-1),beta)
            assert committed.info[q]==0 and committed.out[q]==0

        dense={j:k.cell_from_bits(a['dense_input'][j+5].tolist()) for j in range(-5,6)}
        assert a['dense_expected'].tolist()==k.cell_bits(k.local_transition(dense,beta))
        # Exact finite runner recurrence, independent of a universal beta proof.
        for limit in (16*k.Q-2,16*k.Q-1):
            d,n,dp,_=k.execute(beta,k.input_tape(dense),limit=limit)
            dbits=[d.get(k.PRIMARY_START+i,0) for i in range(k.FRAME_BITS)]
            assert n==limit and dp.mode!=k.HALT
            assert [i for i,(x,y) in enumerate(zip(dbits,a['dense_expected'])) if x!=y]==[66]
            assert a['dense_expected'][66]==1 and dbits[66]==0
    return 65535


def retain_runtime_costs(directory,beta):
    """Uninterrupted runner costs; not physical execution after the gate."""
    assets={}
    with np.load(directory/'GMW2_full_own_replays.npz') as a:
        inputs=(a['input_bits'][0].copy(),a['dense_input'].copy())
    for name,data in zip(('canonical','dense'),inputs):
        cells={j:k.cell_from_bits(data[j+5].tolist()) for j in range(-5,6)}
        out,n,p,history=k.execute(beta,k.input_tape(cells),400000,True)
        assert p.mode==k.HALT
        assets[name+'_input_bits']=data
        assets[name+'_addresses']=np.array([h[0] for h in history],np.uint16)
        for key,index in (('before',1),('after',2)):
            assets[name+'_'+key]=np.array([list(k.pack(h[index]).to_bytes(48,'little')) for h in history],np.uint8)
        for key,index in (('out_writes',3),('scratch_writes',4)):
            assets[name+'_'+key]=np.array([-1 if h[index] is None else h[index] for h in history],np.int8)
        assets[name+'_output']=np.array([out.get(k.PRIMARY_START+i,0) for i in range(k.FRAME_BITS)],np.uint8)
    np.savez_compressed(directory/'GMW2_uninterrupted_cost_traces.npz',**assets)
    return validate_runtime_costs(directory,beta)


def validate_runtime_costs(directory,beta):
    result=[]
    with np.load(directory/'GMW2_uninterrupted_cost_traces.npz') as a:
        for name,expectedcost in (('canonical',(102026,21951,12425,67650)),
                                  ('dense',(132803,26539,14105,92159))):
            cells={j:k.cell_from_bits(a[name+'_input_bits'][j+5].tolist()) for j in range(-5,6)}
            tape=k.input_tape(cells);p=k.initial_packet();out={};scratch={};position=k.HEAD_ADDRESS
            counts=Counter();ops=Counter()
            for address,before,after,ow,sw in zip(a[name+'_addresses'],a[name+'_before'],
                    a[name+'_after'],a[name+'_out_writes'],a[name+'_scratch_writes']):
                address=int(address)
                assert k.pack(p)==int.from_bytes(before.tobytes(),'little')
                assert address==position+(1 if p.move==1 else -1 if p.move==2 else 0)
                if p.mode==k.RUN:
                    counts['instruction_updates']+=1;ops[k.decode(k.beta_word(beta,p.pc,29))[0]]+=1
                elif p.mode in (k.SEEK,k.LOAD,k.WRITE):
                    counts['operand_travel_updates' if address!=p.start+p.index else 'mutable_column_updates']+=1
                else:raise AssertionError('unexpected old halted/error packet')
                p,written,temp=k.step_packet(p,address,tape.get(address,0),out.get(address,0),
                    scratch.get(address,0),beta[address],beta)
                assert k.pack(p)==int.from_bytes(after.tobytes(),'little')
                assert int(ow)==(-1 if written is None else written)
                assert int(sw)==(-1 if temp is None else temp)
                if written is not None:out[address]=written
                if temp is not None:scratch[address]=temp
                position=address
            ticks=len(a[name+'_addresses']);assert p.mode==k.HALT
            assert (ticks,counts['instruction_updates'],counts['mutable_column_updates'],
                counts['operand_travel_updates'])==expectedcost
            assert sum(counts.values())==ticks
            expected=k.cell_bits(k.local_transition(cells,beta))
            assert a[name+'_output'].tolist()==expected==[out.get(k.PRIMARY_START+i,0) for i in range(k.FRAME_BITS)]
            result.append(dict(fixture=name,total_uninterrupted_ticks=ticks,**dict(counts),
                opcode_counts=dict(ops),post_gate_trace_is_actual_physical_execution=False))
    return result


def main():
    started=time.monotonic();directory=ROOT/'figs/gray_counterexamples';source=Path(__file__).resolve().parent
    beta,record=validate_assets(directory)
    prefix=validate_prefix(directory,beta)
    flagcofactors,votecofactors=flag_capacity()
    runtimecosts=retain_runtime_costs(directory,beta)
    assert candidates.CURRENT=='G17'
    retained={p.name:digest(p) for p in directory.glob('GMW2_semantic_failure_*')}
    retained.update({p.name:digest(p) for p in directory.glob('*first56*')})
    retained.update({p.name:digest(p) for p in directory.glob('*.first_full_overflow.txt')})
    for name in ('GMW2_initial_audit_api_failure.py.txt','GMW2_second_audit_receipt_key_failure.py.txt'):
        retained[name]=digest(directory/name)
    result=dict(name='GMW2 full-component programme audit and scoped deadline certificate',Q=k.Q,U=k.U,
        lambda_original=24,c_original=104,
        GMW1_specific_Q_code_overflow_proved=True,GMW1_out_of_range_references=268,
        GMW2_total_local_component_and_radius5_proved=True,GMW2_frame_bits=2007,
        GMW2_immutable_ROM_capacity=65536,GMW2_programme_bits=44730,GMW2_instructions=1863,
        GMW2_actual_beta_listing_identity_verified=True,
        generic_ROM_self_reference_defined_without_whole_Apply=True,
        quiet_copy_closure_by_equations_proved=True,
        E0_only_component_transparency_by_capacity_and_counts_proved=True,
        E0_native_flag_cofactors=flagcofactors,E0_SF_bit_vote_cofactors=votecofactors,
        all_native_word_replacements_covered_by_three_correct_words=True,
        prepared_input_exact_active_recurrence_updates=prefix,
        prepared_no_error_fifth_stage_ProgramBit_copy4_mismatch_proved=True,
        prepared_input_intact_recursive_initialization=False,
        dense_raw_head_16Q_output_obstruction_proved=True,
        dense_raw_head_wrong_bit_at_actual_last_precommit_tick=66,
        dense_raw_head_actual_last_precommit_usable_ticks=131070,
        instruction_and_CODE_fetch_use_one_update=True,
        serial_programme_fetch_cost_inferred_from_beta_length=False,
        uninterrupted_runtime_cost_breakdown=runtimecosts,
        finite_whole_beta_comparisons=70,finite_comparisons_measured_only=True,
        universal_full_beta_equivalence_proved=False,
        faithful_Gray_programme_gather_pulse_or_period_completed=False,
        real1_or_higher_theorem_proved=False,positive_iid_noise_rate_proved=False,
        corrected_Gray_or_iid_failure_proved=False,
        faster_U_used=False,active_rule_modified=False,global_reliability_established=False,
        checker_sha256=digest(__file__),written_proof_sha256=digest(source/'GMW2_FULL_PROGRAMME_AUDIT.md'),
        kernel_sha256=digest(k.__file__),builder_sha256=digest(builder.__file__),
        GMW1_kernel_sha256=digest(k1.__file__),GMW1_builder_sha256=digest(b1.__file__),
        receipt_dependencies_sha256={name:digest(directory/name) for name in (
            'GMW1_full_own_overflow.json','GMW2_full_own_certificate.json','GMW2_first56_full_own_certificate.json',
            'GMW2_semantic_failure_01.json','GMW2_semantic_failure_02.json','GMW2_semantic_failure_03.json',
            'GMW2_initial_audit_api_failure.json','GMW2_second_audit_receipt_key_failure.json')},
        asset_dependencies_sha256={name:digest(directory/name) for name in (
            'GMW1_full_own_attempt_listing.json','GMW1_full_own_invalid_masked_beta.bin',
            'GMW2_full_own_beta.bin','GMW2_full_own_listing.json','GMW2_full_own_replays.npz',
            'GMW2_uninterrupted_cost_traces.npz')},
        retained_failure_and_first56_sources_assets_sha256=retained,
        wall_seconds=time.monotonic()-started)
    (directory/'GMW2_full_programme_audit_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':main()
