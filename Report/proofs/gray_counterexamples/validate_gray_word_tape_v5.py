#!/usr/bin/env python3
"""Read-only GMW5 emission, prepared replays and wrong-commit validation."""
from pathlib import Path
import hashlib,json,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
import gray_word_tape_v5 as implementation
import build_gray_word_tape_v5 as builder
import check_gray_word_tape_v5 as check


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def failures(directory):
    names=['GMW5_first_Q_full_attempt.json','GMW5_initial_generator_assertion_failure.json']+[
        'GMW5_execution_failure_%02d.json'%i for i in range(1,4)]
    for name in names:
        row=json.loads((directory/name).read_text())
        for file,value in row['source_snapshots_sha256'].items():assert digest(directory/file)==value
    first=json.loads((directory/names[0]).read_text())
    assert (first['programme_bits'],first['instructions'],first['out_of_range_instruction_references'],
        len(first['out_of_range_labels']))==(26024,887,105,70)
    assert first['beta_sha256']==digest(directory/'GMW5_first_Q_full_attempt_beta.bin')
    assert first['listing_sha256']==digest(directory/'GMW5_first_Q_full_attempt_listing.json')
    assert first['specified_compiler_fit_failure'] and not first['full_code_or_Gray_refutation']
    for name in names[2:]:
        row=json.loads((directory/name).read_text())
        assert row['changed_implementation_failure'] and not row['Gray_or_iid_failure_proved']
    generator=json.loads((directory/names[1]).read_text())
    assert not generator['transition_or_error_classifier_disagreement'] and not generator['Gray_or_iid_refutation']
    return {name:digest(directory/name) for name in names}


def validate(directory=None):
    directory=directory or ROOT/'figs/gray_counterexamples'
    row=json.loads((directory/'GMW5_word_tape_execution_certificate.json').read_text())
    for key,path in (('kernel_sha256',implementation.__file__),('builder_sha256',builder.__file__),
        ('checker_sha256',check.__file__)):
        assert row[key]==digest(path),(key,path)
    assert (row['Q'],row['U'],row['lambda_original'],row['c_original'])==(8192,1048576,24,104)
    assert row['frame_words']==191 and row['word_bits']==100
    for key in ('mutable_Info_Mem_Out_Scratch_Program_word_width_change_explicit',
        'native_h1_computed_GF_and_zero_Workspace_departures_explicit','larger_diagnostic_ROM_departure_explicit',
        'physical_operand_travel','no_whole_rule_HeadStep_or_native_syscall'):
        assert row[key]
    for key in ('universal_beta_equivalence_proved','universal_execution_deadline_proved',
        'Q_own_beta_fit_proved','intact_start_or_Gray_refinement_or_iid_theorem_proved','active_rule_modified'):
        assert not row[key]
    for variant,capacity,bits,badrefs,badlabels in zip(row['variants'],(8192,65536),(26137,26542),(105,0),(70,0)):
        k=implementation.engine(capacity);code,listing,labels,errors=builder.programme(engine=k).assemble()
        assert (len(code),len(listing),len(errors),sum(v>=capacity for v in labels.values()))==(bits,891,badrefs,badlabels)
        assert (variant['capacity'],variant['programme_bits'],variant['instructions'],
            variant['invalid_instruction_references'],len(variant['invalid_labels']))==(capacity,bits,891,badrefs,badlabels)
        assert variant['invalid_labels']=={n:v for n,v in labels.items() if v>=capacity}
        assert variant['fits']==(len(code)<=capacity and not errors)
        name=variant['name'];binary=directory/(name+'_full_attempt_beta.bin');document=directory/(name+'_full_attempt_listing.json')
        assert digest(binary)==variant['beta_sha256'] and digest(document)==variant['listing_sha256']
        assert json.loads(document.read_text())==dict(instructions=listing,labels=labels,errors=errors)
        data=np.unpackbits(np.fromfile(binary,np.uint8),bitorder='little')
        assert data[:len(code)].tolist()==code and not data[len(code):].any()
        for item in listing:
            word=sum(code[item['address']+i]<<i for i in range(item['bits']))
            masked=tuple(v&((1<<w)-1) for v,w in zip(item['operands'],k.ARGS[item['opcode']]))
            assert k.decode(word)==(item['opcode'],masked)
    beta=tuple(code+[0]*(k.CODE_CAPACITY-len(code)))
    prefix=json.loads((directory/'GMW5_native_word_replays.json').read_text())
    assert digest(directory/'GMW5_native_word_replays.json')==row['native']['asset_sha256']
    small=implementation.engine(8192);native_code,native_listing,_,native_errors=builder.programme(True,engine=small).assemble()
    assert (len(native_code),len(native_listing),len(native_errors))==(3613,133,0)
    native_beta=tuple(native_code+[0]*(8192-len(native_code)))
    for words,expected,ticks in zip(prefix['inputs'],prefix['outputs'],prefix['ticks']):
        cells={j:small.cell_from_words([int(v,16) for v in words[j+5]]) for j in range(-5,6)}
        assert small.cell_words(small.local_transition(cells,native_beta))[:6]==expected
        out,count,last,_=small.execute(native_beta,small.input_tape(cells),limit=65535)
        assert last.mode==small.HALT and count==ticks
        assert [out.get(small.PRIMARY_START+i,0) for i in range(6)]==expected
    assert len(prefix['inputs'])==128 and (min(prefix['ticks']),max(prefix['ticks']))==(150,152)
    replay=json.loads((directory/'GMW5_64K_full_replays.json').read_text())
    assert digest(directory/'GMW5_64K_full_replays.json')==row['asset_sha256']
    assert replay['ticks']==row['times'] and len(replay['names'])==62
    for words,expected,ticks in zip(replay['inputs'],replay['outputs'],replay['ticks']):
        cells={j:k.cell_from_words([int(v,16) for v in words[j+5]]) for j in range(-5,6)}
        target=k.cell_words(k.local_transition(cells,beta));out,count,last,_=k.execute(beta,k.input_tape(cells),limit=350000)
        assert last.mode==k.HALT and count==ticks
        assert [out.get(k.PRIMARY_START+i,0) for i in range(k.FRAME_WORDS)]==target==[int(v,16) for v in expected]
    assert (min(replay['ticks']),max(replay['ticks']))==(23358,68254)
    deadline=row['exact_prepared_deadline_failure'];path=directory/'GMW5_64K_dense_mask_deadline.npz'
    assert digest(path)==deadline['asset_sha256']
    with np.load(path) as asset:
        arrays={name:asset[name].copy() for name in asset.files}
    def integers(a):return [int.from_bytes(v.tobytes(),'little') for v in a]
    words=arrays['input_words'];assert words.shape==(11,191,13)
    cells={j:k.cell_from_words(integers(words[j+5])) for j in range(-5,6)}
    assert cells==check.dense_fixture(k,3)
    expected=integers(arrays['expected']);truncated=integers(arrays['truncated'])
    assert expected==k.cell_words(k.local_transition(cells,beta))
    before=integers(arrays['before']);after=integers(arrays['after'])
    ow=integers(arrays['out_writes']);sw=integers(arrays['scratch_writes'])
    tape=k.input_tape(cells);out={};scratch={};p=k.Packet(p=1);position=k.HEAD_ADDRESS
    assert len(before)==len(after)==len(arrays['addresses'])==65535
    for tick in range(65535):
        assert k.pack(p)==before[tick]
        position+=1 if p.move==1 else -1 if p.move==2 else 0
        assert position==int(arrays['addresses'][tick]) and 0<=position<k.Q
        p,write,swrite=k.step_packet(p,position,tape.get(position,0),out.get(position,0),scratch.get(position,0),beta[position],beta)
        assert k.pack(p)==after[tick]
        assert bool(arrays['out_write_present'][tick])==(write is not None)
        assert bool(arrays['scratch_write_present'][tick])==(swrite is not None)
        assert ow[tick]==(0 if write is None else write) and sw[tick]==(0 if swrite is None else swrite)
        if write is not None:out[position]=write
        if swrite is not None:scratch[position]=swrite
    assert (p.mode,p.pc,position)==(1,23773,4113)==(deadline['pending_mode'],deadline['pending_pc'],deadline['pending_position'])
    actual=[out.get(k.PRIMARY_START+i,0) for i in range(191)]
    assert actual==truncated and [i for i in range(191) if actual[i]!=expected[i]]==[20,75]
    def physical(x,clock):
        return {j:k.Cell(addr=(x+j)%k.Q,age=clock,
            heads=tuple(k.pack(p) if x+j+s==position else 0 for s in k.SLOTS),
            mem=tuple(tape.get(x+j+s,0) for s in k.SLOTS),
            out=tuple(out.get(x+j+s,0) for s in k.SLOTS),
            scratch=tuple(scratch.get(x+j+s,0) for s in k.SLOTS),
            program=tuple(beta[(x+j+s)%k.Q]&1 for s in k.SLOTS)) for j in range(-5,6)}
    rest=0
    for clock in (120*k.Q,120*k.Q+1,k.U-2):
        for q,s in enumerate(k.SLOTS):
            result=k.local_transition(physical(position-s,clock),beta)
            assert result.heads[q]==k.pack(p);rest+=1
    commits=[]
    for i in (20,75):
        target=k.PRIMARY_START+i
        for q,s in enumerate(k.SLOTS):
            result=k.local_transition(physical(target-s,k.U-1),beta)
            assert result.info[q]==actual[i] and result.out[q]==0
            commits.append(dict(field_word=i,actual_holder=target-s,copy_slot=s,
                Info=hex(result.info[q]),expected_upper_word=hex(expected[i])))
    assert commits==deadline['all_five_actual_Info_commits_per_word'] and rest==deadline['rest_assertions']==15
    assert deadline['no_error_history'] and deadline['preloaded_input_not_intact_hierarchy']
    assert deadline['exact_prepared_decoded_deadline_failure'] and not deadline['Gray_or_iid_failure_proved']
    return dict(specified_Q_bits=26137,diagnostic_64K_bits=26542,native_measured_comparisons=128,
        full_measured_comparisons=62,exact_deadline_updates=65535,wrong_words=[20,75],
        all_five_wrong_commits=len(commits),rest_checks=rest,
        failures_sha256=failures(directory),receipt_sha256=digest(directory/'GMW5_word_tape_execution_certificate.json'),
        universal_beta_or_Gray_or_iid_proved=False)


if __name__=='__main__':
    started=time.monotonic();result=validate();result['elapsed_seconds']=time.monotonic()-started
    print(json.dumps(result))
