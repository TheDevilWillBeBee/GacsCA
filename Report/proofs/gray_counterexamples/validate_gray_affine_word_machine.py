#!/usr/bin/env python3
"""Read-only GMW4 emission, finite semantic replay and deadline validation.

No artifact is rewritten. Universal beta equivalence, Q-fit, complete Gray
refinement, intact hierarchy reachability and iid claims remain unproved.
"""
from pathlib import Path
import hashlib,json,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
import gray_affine_word_machine as implementation
import build_gray_affine_word_machine as builder
import check_gray_affine_word_machine as check


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate(directory=None):
    directory=directory or ROOT/'figs/gray_counterexamples';source=Path(__file__).parent
    row=json.loads((directory/'GMW4_affine_full_attempt_certificate.json').read_text())
    failure=json.loads((directory/'GMW4_initial_validator_receipt_race.json').read_text())
    assert failure['retained_validator_sha256']==digest(directory/failure['retained_validator'])
    assert not failure['checker_or_kernel_transition_changed_by_failure']
    assert not failure['semantic_or_deadline_disagreement'] and not failure['Gray_or_iid_failure_proved']
    for key,path in (('kernel_sha256',implementation.__file__),('builder_sha256',builder.__file__),
        ('checker_sha256',check.__file__),('proof_sha256',source/'GMW4_AFFINE_COMPILER_ATTEMPT.md')):
        assert row[key]==digest(path),(key,path)
    for name,value in row['dependency_sources_sha256'].items():
        path=(ROOT/'gacsca'/name) if name=='gray_errors.py' else source/name
        assert value==digest(path),(name,path)
    assert (row['Q'],row['U'],row['lambda_original'],row['c_original'])==(8192,1048576,24,104)
    for key in ('affine_instructions_have_real_operand_travel',
        'immutable_instruction_CODE_and16bit_diagnostic_departure_explicit',
        'no_whole_rule_HeadStep_or_native_evaluation_syscall','arbitrary_overflow_rejects_without_PC_advance',
        'finite_comparisons_measured_only','all_raw_radius5_by_existing_geometry'):
        assert row[key]
    for key in ('Q_own_programme_fit_proved','universal_own_beta_equivalence_proved',
        'full_physical_Gray_simulation_or_intact_counterexample_proved','shorter_U_proved',
        'global_reliability_established','active_rule_modified'):
        assert not row[key]
    code=None;k=None
    for variant,capacity,pc,bits,instructions,badrefs,badlabels,frame in zip(row['variants'],
        (8192,65536),(13,16),(39544,40188),(1413,1410),(165,0),(120,0),(1992,2007)):
        k=implementation.engine(capacity,pc);a=builder.programme(capacity,pc)
        code,listing,labels,errors=a.assemble();name=variant['name']
        assert (variant['capacity'],variant['pc_bits'],variant['programme_bits'],variant['instructions'],
            variant['out_of_range_instruction_references'],len(variant['out_of_range_code_labels']),
            variant['frame_bits'])==(capacity,pc,bits,instructions,badrefs,badlabels,frame)
        assert len(code)==bits and len(listing)==instructions and len(errors)==badrefs
        assert variant['source_dependency_sha256']==digest(implementation.base.__file__)
        assert variant['previous_builder_sha256']==digest(builder.previous.__file__)
        for key,file in (('source_sha256',name+'_generated_rule.py.txt'),
            ('generated_builder_sha256',name+'_generated_builder.py.txt'),
            ('beta_sha256',name+'_full_attempt_beta.bin'),('listing_sha256',name+'_full_attempt_listing.json')):
            assert variant[key]==digest(directory/file),(key,file)
        assert (directory/(name+'_generated_rule.py.txt')).read_text()==implementation.generated_source(capacity,pc)
        assert (directory/(name+'_generated_builder.py.txt')).read_text()==builder.generated_source(pc)
        emitted=json.loads((directory/(name+'_full_attempt_listing.json')).read_text())
        assert emitted==dict(instructions=listing,labels=labels,errors=errors,
            programme_bits=len(code),bitstream_has_masked_references=bool(errors))
        data=np.unpackbits(np.fromfile(directory/(name+'_full_attempt_beta.bin'),np.uint8),bitorder='little')
        assert data[:len(code)].tolist()==code and not data[len(code):].any()
        assert variant['out_of_range_code_labels']=={label:v for label,v in labels.items() if v>=capacity}
        assert variant['emitted_full_attempt_fits_capacity']==(not errors and len(code)<=capacity)
        assert variant['invalid_attempt_retained']==bool(errors or len(code)>capacity)
        assert not variant['universal_own_beta_equivalence_proved'] and not variant['full_Gray_or_iid_failure_proved']
        for item in listing:
            value=sum(code[item['address']+i]<<i for i in range(item['bits']))
            masked=tuple(v&((1<<w)-1) for v,w in zip(item['operands'],k.ARGS[item['opcode']]))
            assert k.decode(value)==(item['opcode'],masked) and k.instruction_length(value)==item['bits']
        assert k.HEAD_BITS==(376 if pc==13 else 379) and k.FRAME_BITS==frame
    assert k is not None and code is not None and row['finite_comparisons']==51
    beta=tuple(code+[0]*(k.CODE_CAPACITY-len(code)))
    replay=directory/'GMW4_64K_full_attempt_replays.npz'
    assert row['asset_sha256']==digest(replay)
    with np.load(replay) as asset:
        names=asset['names'].tolist();inputs=asset['input_bits'];outputs=asset['outputs'];ticks=asset['measured_ticks']
    assert names==row['fixture_names'] and ticks.tolist()==row['measured_ticks']
    assert inputs.shape==(51,11,2007) and outputs.shape==(51,2007)
    for i in range(51):
        cells={j:k.cell_from_bits(inputs[i,j+5].tolist()) for j in range(-5,6)}
        assert [k.cell_bits(cells[j]) for j in range(-5,6)]==inputs[i].tolist()
        expected=k.cell_bits(k.local_transition(cells,beta))
        out,count,last,_=k.execute(beta,k.input_tape(cells),limit=350000)
        actual=[out.get(k.PRIMARY_START+j,0) for j in range(k.FRAME_BITS)]
        assert last.mode==k.HALT and count==ticks[i] and expected==actual==outputs[i].tolist()
    assert ticks[:3].tolist()==[101902,76614,115920] and (min(ticks),max(ticks))==(76614,115920)

    deadline=row['exact_prepared_deadline_failure'];path=directory/'GMW4_64K_prepared_deadline.npz'
    assert deadline['asset_sha256']==digest(path)
    assert deadline['execution_updates']==65535 and deadline['prepared_input_not_intact_hierarchy']
    assert deadline['exact_no_error_prepared_deadline_failure']
    with np.load(path) as asset:
        initial=asset['input_bits'];expected=asset['expected'];truncated=asset['truncated'];addresses=asset['addresses']
        before=asset['before'];after=asset['after'];ow=asset['out_writes'];sw=asset['scratch_writes']
    assert (before.shape,after.shape,addresses.shape)==((65535,48),(65535,48),(65535,))
    cells={j:k.cell_from_bits(initial[j+5].tolist()) for j in range(-5,6)}
    assert cells==check.fixture(k) and expected.tolist()==k.cell_bits(k.local_transition(cells,beta))
    tape=k.input_tape(cells);out={};scratch={};p=k.initial_packet();position=k.HEAD_ADDRESS
    for tick in range(65535):
        assert k.pack(p)==int.from_bytes(before[tick].tobytes(),'little')
        target=position+(1 if p.move==1 else -1 if p.move==2 else 0)
        assert target==addresses[tick] and 0<=target<k.Q
        p,write,swrite=k.step_packet(p,target,tape.get(target,0),out.get(target,0),scratch.get(target,0),beta[target],beta)
        assert k.pack(p)==int.from_bytes(after[tick].tobytes(),'little')
        assert int(ow[tick])==(-1 if write is None else write) and int(sw[tick])==(-1 if swrite is None else swrite)
        if write is not None:out[target]=write
        if swrite is not None:scratch[target]=swrite
        position=target
    assert (p.mode,p.pc,position)==(0,38105,5079)==(
        deadline['pending_mode'],deadline['pending_pc'],deadline['pending_position'])
    actual=[out.get(k.PRIMARY_START+j,0) for j in range(k.FRAME_BITS)]
    assert actual==truncated.tolist() and np.flatnonzero(truncated!=expected).tolist()==[2006]==deadline['different_field_bits']
    assert actual[2006]==0 and expected[2006]==beta[2]==1
    def physical(x,clock):
        return {j:k.Cell(addr=(x+j)%k.Q,age=clock,
            heads=tuple(k.pack(p) if x+j+s==position else 0 for s in k.SLOTS),
            mem=tuple(tape.get(x+j+s,0) for s in k.SLOTS),
            out=tuple(out.get(x+j+s,0) for s in k.SLOTS),
            scratch=tuple(scratch.get(x+j+s,0) for s in k.SLOTS),
            program=tuple(beta[(x+j+s)%k.Q] for s in k.SLOTS)) for j in range(-5,6)}
    # Rest equations are time-independent in this interval: check its two
    # endpoints and a representative centre, including all five head holders.
    rest_assertions=0
    for clock in (120*k.Q,120*k.Q+1,k.U-2):
        for slot in k.SLOTS:
            x=position-slot;result=k.local_transition(physical(x,clock),beta);q=k.SLOTS.index(slot)
            assert result.heads[q]==k.pack(p)
            assert result.out[q]==out.get(position,0)
            rest_assertions+=1
    commits=[];target=k.PRIMARY_START+2006
    assert target==5099==deadline['wrong_primary']
    for q,s in enumerate(k.SLOTS):
        result=k.local_transition(physical(target-s,k.U-1),beta)
        assert result.info[q]==result.out[q]==0
        commits.append(dict(actual_holder=target-s,copy_slot=s,Info=0,expected_upper_ProgramBit=1))
    assert commits==deadline['all_five_actual_Info_commits']
    return dict(emitted_Q_bits=39544,emitted_64K_bits=40188,finite_measured_comparisons=51,
        exact_prepared_deadline_updates=65535,wrong_field_bit=2006,actual_five_commits=len(commits),
        rest_assertions=rest_assertions,universal_own_beta_equivalence_proved=False,
        intact_Gray_or_iid_counterexample_proved=False,
        receipt_sha256=digest(directory/'GMW4_affine_full_attempt_certificate.json'))


if __name__=='__main__':
    started=time.monotonic();result=validate();result['elapsed_seconds']=time.monotonic()-started
    print(json.dumps(result))
