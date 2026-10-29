#!/usr/bin/env python3
"""Retain full-emission fit/failures and finite GMW4 physical-code comparisons.

Space checks are exact for this emitter. Execution comparisons are measured
only; all fixtures are preloaded, not an intact own hierarchy. Both code
variants are explicit departures from Gray's ProgrammeBits protocol.
"""
from pathlib import Path
import hashlib,json,random,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
import gray_affine_word_machine as implementation
import build_gray_affine_word_machine as builder


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def emit(capacity,pc_bits,directory):
    k=implementation.engine(capacity,pc_bits);a=builder.programme(capacity,pc_bits)
    code,listing,labels,errors=a.assemble();name='GMW4_'+('Q' if capacity==8192 else '64K')
    source=directory/(name+'_generated_rule.py.txt');source.write_text(implementation.generated_source(capacity,pc_bits))
    compiler=directory/(name+'_generated_builder.py.txt');compiler.write_text(builder.generated_source(pc_bits))
    bits=directory/(name+'_full_attempt_beta.bin');bits.write_bytes(np.packbits(np.array(code,np.uint8),bitorder='little').tobytes())
    listing_path=directory/(name+'_full_attempt_listing.json')
    listing_path.write_text(json.dumps(dict(instructions=listing,labels=labels,errors=errors,
        programme_bits=len(code),bitstream_has_masked_references=bool(errors)),separators=(',',':'))+'\n')
    outlabels={label:address for label,address in labels.items() if address>=capacity}
    result=dict(name=name,capacity=capacity,pc_bits=pc_bits,frame_bits=k.FRAME_BITS,
        programme_bits=len(code),instructions=len(listing),out_of_range_instruction_references=len(errors),
        out_of_range_code_labels=outlabels,emitted_full_attempt_fits_capacity=len(code)<=capacity and not errors,
        invalid_attempt_retained=bool(errors or len(code)>capacity),source_sha256=digest(source),
        generated_builder_sha256=digest(compiler),beta_sha256=digest(bits),listing_sha256=digest(listing_path),
        source_dependency_sha256=digest(implementation.base.__file__),
        previous_builder_sha256=digest(builder.previous.__file__),
        universal_own_beta_equivalence_proved=False,full_Gray_or_iid_failure_proved=False)
    for row in listing:
        actual=k.decode(sum(code[row['address']+i]<<i for i in range(row['bits'])))
        operands=tuple(v&((1<<w)-1) for v,w in zip(row['operands'],k.ARGS[row['opcode']]))
        assert actual==(row['opcode'],operands) and k.instruction_length(sum(code[row['address']+i]<<i for i in range(row['bits'])))==row['bits']
    return k,code,listing,labels,result


def fixture(k,packet=None,commonage=0,seed=0,head_position=0):
    rng=random.Random(seed);packet=k.ZERO if packet is None else packet
    logical={y:{f:rng.randrange(2048 if f=='mem' else 2) for f in ('mem','out','info','scratch','program')}
        for y in range(-7,8)} if seed else {}
    return {j:k.Cell(addr=j%k.Q,age=commonage,
        heads=tuple(k.pack(packet) if j+s==head_position else 0 for s in k.SLOTS),
        **{f:tuple(logical.get(j+s,{}).get(f,0) for s in k.SLOTS) for f in ('mem','out','info','scratch','program')})
        for j in range(-5,6)}


def retain_failure(name,k,cells,actual,expected,code,directory,ticks,last):
    serial=1
    while (directory/('GMW4_semantic_failure_%02d.json'%serial)).exists():serial+=1
    stem='GMW4_semantic_failure_%02d'%serial;asset=directory/(stem+'.npz')
    np.savez_compressed(asset,input_bits=np.array([k.cell_bits(cells[j]) for j in range(-5,6)],np.uint8),
        actual=np.array(actual,np.uint8),expected=np.array(expected,np.uint8),beta=np.array(code,np.uint8))
    snapshots={}
    for path in (Path(implementation.__file__),Path(builder.__file__),Path(__file__)):
        saved=directory/(stem+'_'+path.name+'.txt');saved.write_bytes(path.read_bytes());snapshots[saved.name]=digest(saved)
    (directory/(stem+'.json')).write_text(json.dumps(dict(fixture=name,measured_ticks=ticks,last_mode=last.mode,
        last_pc=last.pc,different_field_bits=np.flatnonzero(np.array(actual)!=np.array(expected)).tolist(),
        asset_sha256=digest(asset),source_snapshots_sha256=snapshots,
        changed_emitter_bug=True,Gray_or_iid_failure_proved=False),indent=2)+'\n')
    raise AssertionError(stem+' '+name)


def canonical_deadline(k,beta,directory):
    """Exact inner recurrence and actual physical commits, prepared input.

    The five-copy physical closure is a separate word/geometry argument;
    the stored recurrence covers every one of the65535 execution updates.
    """
    cells=fixture(k);tape=k.input_tape(cells);expected=k.cell_bits(k.local_transition(cells,beta))
    p=k.initial_packet();position=k.HEAD_ADDRESS;out={};scratch={};age=112*k.Q+1
    before=[];after=[];addresses=[];writes=[];scratchwrites=[]
    for i in range(65535):
        target=position+(1 if p.move==1 else -1 if p.move==2 else 0)
        assert 0<=target<k.Q
        before.append(list(k.pack(p).to_bytes(48,'little')))
        p,ow,sw=k.step_packet(p,target,tape.get(target,0),out.get(target,0),scratch.get(target,0),beta[target],beta)
        after.append(list(k.pack(p).to_bytes(48,'little')));addresses.append(target)
        writes.append(-1 if ow is None else ow);scratchwrites.append(-1 if sw is None else sw)
        if ow is not None:out[target]=ow
        if sw is not None:scratch[target]=sw
        position=target;age+=1
    output=[out.get(k.PRIMARY_START+i,0) for i in range(k.FRAME_BITS)]
    different=np.flatnonzero(np.array(output)!=np.array(expected)).tolist()
    assert age==120*k.Q and p.mode!=k.HALT
    assert 2006 in different and output[2006]==0 and expected[2006]==beta[2]==1
    def physical(x,clock):
        return {j:k.Cell(addr=(x+j)%k.Q,age=clock,
            heads=tuple(k.pack(p) if x+j+s==position else 0 for s in k.SLOTS),
            mem=tuple(tape.get(x+j+s,0) for s in k.SLOTS),
            out=tuple(out.get(x+j+s,0) for s in k.SLOTS),
            scratch=tuple(scratch.get(x+j+s,0) for s in k.SLOTS),
            program=tuple(beta[(x+j+s)%k.Q] for s in k.SLOTS)) for j in range(-5,6)}
    resting=k.local_transition(physical(position,age),beta)
    assert resting.heads[0]==k.pack(p) and resting.out==tuple(out.get(position+s,0) for s in k.SLOTS)
    target=k.PRIMARY_START+2006;commits=[]
    for q,s in enumerate(k.SLOTS):
        result=k.local_transition(physical(target-s,k.U-1),beta)
        assert result.info[q]==0 and result.out[q]==0
        commits.append(dict(actual_holder=target-s,copy_slot=s,Info=0,expected_upper_ProgramBit=1))
    path=directory/'GMW4_64K_prepared_deadline.npz'
    np.savez_compressed(path,input_bits=np.array([k.cell_bits(cells[j]) for j in range(-5,6)],np.uint8),
        expected=np.array(expected,np.uint8),truncated=np.array(output,np.uint8),
        addresses=np.array(addresses,np.uint16),before=np.array(before,np.uint8),after=np.array(after,np.uint8),
        out_writes=np.array(writes,np.int8),scratch_writes=np.array(scratchwrites,np.int8))
    return dict(execution_updates=65535,prepared_input_not_intact_hierarchy=True,
        pending_mode=p.mode,pending_pc=p.pc,pending_position=position,
        different_field_bits=different,wrong_frame_bit=2006,wrong_primary=target,
        wrong_output=0,expected_output=1,all_five_actual_Info_commits=commits,
        exact_no_error_prepared_deadline_failure=True,asset_sha256=digest(path))


def main():
    started=time.monotonic();directory=ROOT/'figs/gray_counterexamples';emissions=[]
    for capacity,pc in ((8192,13),(65536,16)):
        k,code,listing,labels,row=emit(capacity,pc,directory);emissions.append(row)
        print(row['name'],len(code),len(listing),len(row['out_of_range_code_labels']),flush=True)
    assert emissions[0]['invalid_attempt_retained'] and not emissions[0]['emitted_full_attempt_fits_capacity']
    assert emissions[1]['emitted_full_attempt_fits_capacity']
    beta=tuple(code+[0]*(k.CODE_CAPACITY-len(code)))
    choices={row['opcode']:row for row in listing};rng=random.Random(0x414646)
    fixtures=[('canonical',fixture(k)),('native_birth',fixture(k,commonage=112*k.Q)),
        ('native_commit',fixture(k,commonage=k.U-1))]
    for opcode,record in choices.items():
        regs=[rng.randrange(1<<20) for _ in range(16)]
        # Includes the full arbitrary-register guard for affine instructions.
        p=k.Packet(p=1,pc=record['address'],regs=tuple(regs))
        fixtures.append(('RUN_'+opcode,fixture(k,p,112*k.Q+1,seed=17)))
    for name in ('AFFREAD','AFFWRITE'):
        record=choices[name]
        for value in (0,1,4,1023,(1<<20)-1):
            p=k.Packet(p=1,pc=record['address'],regs=(value,)*16)
            fixtures.append((name+'_uniform_'+str(value),fixture(k,p,112*k.Q+1,seed=31)))
    for kind in range(5):
        p=k.Packet(p=1,mode=k.LOAD,kind=kind,start=0,width=3,index=0,lane=1,dst=7,
            source=kind%4,dest=kind%2,regs=tuple(rng.randrange(1<<20) for _ in range(16)))
        fixtures.append(('LOAD_KIND_'+str(kind),fixture(k,p,112*k.Q+1,seed=kind+2)))
    inputs=[];outputs=[];tickcounts=[];names=[]
    for name,cells in fixtures:
        tape=k.input_tape(cells)
        out,ticks,last,_=k.execute(beta,tape,limit=350000)
        expected=k.cell_bits(k.local_transition(cells,beta));actual=[out.get(k.PRIMARY_START+i,0) for i in range(k.FRAME_BITS)]
        if last.mode!=k.HALT or actual!=expected:
            retain_failure(name,k,cells,actual,expected,code,directory,ticks,last)
        names.append(name);inputs.append([k.cell_bits(cells[j]) for j in range(-5,6)]);outputs.append(actual);tickcounts.append(ticks)
        if name in ('canonical','native_birth','native_commit'):print(name,ticks,flush=True)
    asset=directory/'GMW4_64K_full_attempt_replays.npz';np.savez_compressed(asset,
        names=np.array(names),input_bits=np.array(inputs,np.uint8),outputs=np.array(outputs,np.uint8),
        measured_ticks=np.array(tickcounts,np.int64))
    deadline=canonical_deadline(k,beta,directory)
    row=dict(name='GMW4 complete affine-IO compiler attempt',Q=8192,U=1048576,lambda_original=24,c_original=104,
        kernel_sha256=digest(implementation.__file__),builder_sha256=digest(builder.__file__),checker_sha256=digest(__file__),
        proof_sha256=digest(Path(__file__).with_name('GMW4_AFFINE_COMPILER_ATTEMPT.md')),
        dependency_sources_sha256={path.name:digest(path) for path in (
            Path(implementation.base.__file__),Path(builder.previous.__file__),
            Path(implementation.base.old.__file__),Path(implementation.base.old.literal_maintenance.__file__),
            ROOT/'gacsca/gray_errors.py')},
        variants=emissions,affine_instructions_have_real_operand_travel=True,
        immutable_instruction_CODE_and16bit_diagnostic_departure_explicit=True,
        no_whole_rule_HeadStep_or_native_evaluation_syscall=True,
        read_physical_address_equation='base+s1*R[i1]+s2*R[i2]',arbitrary_overflow_rejects_without_PC_advance=True,
        finite_comparisons_measured_only=True,finite_comparisons=len(fixtures),fixture_names=names,
        measured_ticks=tickcounts,asset_sha256=digest(asset),all_raw_radius5_by_existing_geometry=True,
        exact_prepared_deadline_failure=deadline,
        Q_own_programme_fit_proved=False,universal_own_beta_equivalence_proved=False,
        full_physical_Gray_simulation_or_intact_counterexample_proved=False,shorter_U_proved=False,
        global_reliability_established=False,active_rule_modified=False,wall_seconds=time.monotonic()-started)
    (directory/'GMW4_affine_full_attempt_certificate.json').write_text(json.dumps(row,indent=2)+'\n')
    print(json.dumps(dict(programme_bits=[r['programme_bits'] for r in emissions],finite_comparisons=len(fixtures),
        min_ticks=min(tickcounts),max_ticks=max(tickcounts),wall_seconds=row['wall_seconds'])))


if __name__=='__main__':main()
