#!/usr/bin/env python3
"""Retain the new architecture's complete emissions and actual executions.

Q fit can fail. The distinct64K diagnostic is an explicit extra-ROM rule,
and every input is preloaded, not an intact Gray hierarchy. Universal beta
identity/deadline and full gathering/flag composition remain separate.
"""
from pathlib import Path
import hashlib,json,random,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
import gray_word_tape_v5 as machine
import build_gray_word_tape_v5 as builder


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save_failure(name,k,cells,beta,expected,actual,ticks,last,why):
    directory=ROOT/'figs/gray_counterexamples';i=1
    while (directory/('GMW5_execution_failure_%02d.json'%i)).exists():i+=1
    stem='GMW5_execution_failure_%02d'%i;sources={}
    for p in (Path(machine.__file__),Path(builder.__file__),Path(__file__)):
        target=directory/(stem+'_'+p.name+'.txt');target.write_bytes(p.read_bytes());sources[target.name]=digest(target)
    receipt=dict(name=name,capacity=k.CODE_CAPACITY,why=why,measured_ticks=ticks,
        last_head=[hex(v) for v in [getattr(last,n) for n in k.META]+list(last.regs)],
        inputs=[[hex(v) for v in k.cell_words(cells[j])] for j in range(-5,6)],
        expected=[hex(v) for v in expected],actual=[hex(v) for v in actual],
        beta_sha256=hashlib.sha256(np.packbits(np.array(beta,np.uint8),bitorder='little').tobytes()).hexdigest(),
        source_snapshots_sha256=sources,changed_implementation_failure=True,Gray_or_iid_failure_proved=False)
    (directory/(stem+'.json')).write_text(json.dumps(receipt,indent=2)+'\n')
    raise AssertionError(stem+' '+name+' '+why)


def fixture(k,packet=None,age=0,seed=0,position=0):
    rng=random.Random(seed);packet=k.ZERO if packet is None else packet
    logical={y:{field:rng.getrandbits((11 if field=='mem' else 1)*k.WORD)
        for field in ('mem','out','info','scratch','program')} for y in range(-7,8)} if seed else {}
    return {j:k.Cell(addr=j%k.Q,age=age,
        heads=tuple(k.pack(packet) if j+s==position else 0 for s in k.SLOTS),
        **{field:tuple(logical.get(j+s,{}).get(field,0) for s in k.SLOTS)
            for field in ('mem','out','info','scratch','program')}) for j in range(-5,6)}


def dense_fixture(k,kind,seed=71):
    """A legal prepared raw input with stationary SEEK heads at every source.

    Only each centre head is accepted.  Its target is its own logical
    Address, so all five output copies perform the selected word IO.
    This is not a recursively intact initial configuration.
    """
    rng=random.Random(seed)
    logical={y:{field:rng.getrandbits((11 if field=='mem' else 1)*k.WORD)
        for field in ('mem','out','info','scratch','program')} for y in range(-7,8)}
    heads={y:k.pack(k.Packet(p=1,mode=k.SEEK,target=y%k.Q,
        args=k.descriptor(kind,7,lane=3,source=kind,dest=kind&1,side=kind&1),
        regs=tuple(rng.getrandbits(k.WORD) for _ in range(16)))) for y in range(-7,8)}
    return {j:k.Cell(addr=j%k.Q,age=112*k.Q+1,
        heads=tuple(heads[j+s] for s in k.SLOTS),
        **{field:tuple(logical[j+s][field] for s in k.SLOTS)
            for field in ('mem','out','info','scratch','program')}) for j in range(-5,6)}


def native(k,directory):
    code,listing,labels,errors=builder.programme(True,engine=k).assemble();assert not errors and len(code)<8192
    beta=tuple(code+[0]*(k.CODE_CAPACITY-len(code)));rng=random.Random(0x574F5244);inputs=[];outputs=[];times=[]
    for case in range(128):
        cells={j:k.Cell(addr=rng.randrange(k.Q),age=rng.randrange(k.U),
            **{n:rng.randrange(2) for n in ('f1','f2','wf1','wf2')}) for j in range(-5,6)}
        if case<16:
            cells={j:k.Cell(addr=(case+j)%k.Q,age=case*k.Q,
                **{n:rng.randrange(2) for n in ('f1','f2','wf1','wf2')}) for j in range(-5,6)}
        expect=k.cell_words(k.local_transition(cells,beta))[:6]
        out,ticks,last,_=k.execute(beta,k.input_tape(cells),limit=65535)
        actual=[out.get(k.PRIMARY_START+i,0) for i in range(6)]
        if last.mode!=k.HALT or actual!=expect:save_failure('native_'+str(case),k,cells,beta,expect,actual,ticks,last,'native output')
        inputs.append([[hex(v) for v in k.cell_words(cells[j])] for j in range(-5,6)]);outputs.append(expect);times.append(ticks)
    file=directory/'GMW5_native_word_replays.json';file.write_text(json.dumps(dict(inputs=inputs,outputs=outputs,ticks=times),separators=(',',':'))+'\n')
    return dict(programme_bits=len(code),instructions=len(listing),finite_comparisons=128,
        min_ticks=min(times),max_ticks=max(times),asset_sha256=digest(file),measured_only=True)


def emission(k,directory):
    code,listing,labels,errors=builder.programme(engine=k).assemble();stem='GMW5_'+('Q' if k.CODE_CAPACITY==8192 else '64K')
    bits=directory/(stem+'_full_attempt_beta.bin');bits.write_bytes(np.packbits(np.array(code,np.uint8),bitorder='little').tobytes())
    listfile=directory/(stem+'_full_attempt_listing.json');listfile.write_text(json.dumps(dict(instructions=listing,labels=labels,errors=errors),separators=(',',':'))+'\n')
    row=dict(name=stem,capacity=k.CODE_CAPACITY,pc_bits=k.PC_BITS,programme_bits=len(code),instructions=len(listing),
        invalid_instruction_references=len(errors),invalid_labels={name:v for name,v in labels.items() if v>=k.CODE_CAPACITY},
        fits=len(code)<=k.CODE_CAPACITY and not errors,beta_sha256=digest(bits),listing_sha256=digest(listfile))
    return code,listing,labels,row


def prepared_deadline(k,beta,directory):
    cells=dense_fixture(k,3);expected=k.cell_words(k.local_transition(cells,beta))
    out,ticks,last,trace=k.execute(beta,k.input_tape(cells),limit=65535,record=True)
    actual=[out.get(k.PRIMARY_START+i,0) for i in range(k.FRAME_WORDS)]
    wrong=[i for i,(a,b) in enumerate(zip(actual,expected)) if a!=b]
    assert ticks==65535 and last.mode==k.SEEK and wrong==[20,75]
    hb=(k.HEAD_BITS+7)//8;wb=(k.WORD+7)//8
    def bytes_rows(values,width):return np.frombuffer(b''.join(v.to_bytes(width,'little') for v in values),np.uint8).reshape(len(values),width)
    def words(values):return bytes_rows(values,wb)
    path=directory/'GMW5_64K_dense_mask_deadline.npz'
    np.savez_compressed(path,
        input_words=words([v for j in range(-5,6) for v in k.cell_words(cells[j])]).reshape(11,k.FRAME_WORDS,wb),
        expected=words(expected),truncated=words(actual),
        addresses=np.array([r[0] for r in trace],np.uint16),
        before=bytes_rows([k.pack(r[1]) for r in trace],hb),
        after=bytes_rows([k.pack(r[2]) for r in trace],hb),
        out_write_present=np.array([r[3] is not None for r in trace],np.uint8),
        scratch_write_present=np.array([r[4] is not None for r in trace],np.uint8),
        out_writes=words([r[3] or 0 for r in trace]),scratch_writes=words([r[4] or 0 for r in trace]))
    tape=k.input_tape(cells);scratch={}
    for address,_,_,_,sw in trace:
        if sw is not None:scratch[address]=sw
    position=trace[-1][0]
    def physical(x,clock):
        return {j:k.Cell(addr=(x+j)%k.Q,age=clock,
            heads=tuple(k.pack(last) if x+j+s==position else 0 for s in k.SLOTS),
            mem=tuple(tape.get(x+j+s,0) for s in k.SLOTS),
            out=tuple(out.get(x+j+s,0) for s in k.SLOTS),
            scratch=tuple(scratch.get(x+j+s,0) for s in k.SLOTS),
            program=tuple(beta[(x+j+s)%k.Q]&1 for s in k.SLOTS)) for j in range(-5,6)}
    rest=0
    for clock in (120*k.Q,120*k.Q+1,k.U-2):
        for q,s in enumerate(k.SLOTS):
            result=k.local_transition(physical(position-s,clock),beta)
            assert result.heads[q]==k.pack(last)
            rest+=1
    commits=[]
    for i in wrong:
        target=k.PRIMARY_START+i
        for q,s in enumerate(k.SLOTS):
            result=k.local_transition(physical(target-s,k.U-1),beta)
            assert result.info[q]==actual[i] and result.out[q]==0
            commits.append(dict(field_word=i,actual_holder=target-s,copy_slot=s,
                Info=hex(result.info[q]),expected_upper_word=hex(expected[i])))
    return dict(asset_sha256=digest(path),execution_updates=ticks,pending_mode=last.mode,
        pending_pc=last.pc,pending_position=position,different_field_words=wrong,
        wrong_primaries=[k.PRIMARY_START+i for i in wrong],
        all_five_actual_Info_commits_per_word=commits,rest_assertions=rest,
        no_error_history=True,preloaded_input_not_intact_hierarchy=True,
        exact_prepared_decoded_deadline_failure=True,Gray_or_iid_failure_proved=False)


def main():
    started=time.monotonic();directory=ROOT/'figs/gray_counterexamples';kernels=[machine.engine(c) for c in (8192,65536)]
    prefix=native(kernels[0],directory);print('native',prefix,flush=True)
    variants=[]
    for k in kernels:
        code,listing,labels,row=emission(k,directory);variants.append(row);print(row['name'],len(code),len(listing),row['invalid_instruction_references'],flush=True)
    assert not variants[0]['fits'] and variants[1]['fits']
    beta=tuple(code+[0]*(k.CODE_CAPACITY-len(code)));rng=random.Random(0x1005)
    cases=[('canonical',fixture(k)),('birth',fixture(k,age=112*k.Q)),('commit',fixture(k,age=k.U-1))]
    for op in k.OP_NAMES:
        record=next(row for row in listing if row['opcode']==op)
        for value in (0,1,k.MASK):
            packet=k.Packet(p=1,pc=record['address'],regs=(value,)*16)
            cases.append(('RUN_'+op+'_'+str(value),fixture(k,packet,112*k.Q+1,seed=37)))
    for kind in range(4):
        for target in (0,k.HEAD_ADDRESS,k.Q-1,k.MASK):
            p=k.Packet(p=1,mode=k.SEEK,target=target,args=k.descriptor(kind,7,lane=3,source=kind,dest=kind&1,side=kind&1),
                regs=tuple(rng.getrandbits(k.WORD) for _ in range(16)))
            cases.append(('SEEK_'+str(kind)+'_'+str(target),fixture(k,p,112*k.Q+1,seed=39)))
        cases.append(('DENSE_SEEK_'+str(kind),dense_fixture(k,kind)))
    inputs=[];outputs=[];times=[];names=[]
    for name,cells in cases:
        expected=k.cell_words(k.local_transition(cells,beta));out,ticks,last,_=k.execute(beta,k.input_tape(cells),limit=350000)
        actual=[out.get(k.PRIMARY_START+i,0) for i in range(k.FRAME_WORDS)]
        if last.mode!=k.HALT or actual!=expected:save_failure(name,k,cells,beta,expected,actual,ticks,last,'complete physical field comparison')
        names.append(name);inputs.append([[hex(v) for v in k.cell_words(cells[j])] for j in range(-5,6)]);outputs.append([hex(v) for v in actual]);times.append(ticks)
        if name in ('canonical','birth','commit'):print(name,ticks,flush=True)
    asset=directory/'GMW5_64K_full_replays.json';asset.write_text(json.dumps(dict(names=names,inputs=inputs,outputs=outputs,ticks=times),separators=(',',':'))+'\n')
    deadline=prepared_deadline(k,beta,directory)
    certificate=dict(name='GMW5 complete word-tape attempt',Q=k.Q,U=k.U,lambda_original=24,c_original=104,
        kernel_sha256=digest(machine.__file__),builder_sha256=digest(builder.__file__),checker_sha256=digest(__file__),
        frame_words=k.FRAME_WORDS,word_bits=k.WORD,mutable_Info_Mem_Out_Scratch_Program_word_width_change_explicit=True,
        native_h1_computed_GF_and_zero_Workspace_departures_explicit=True,larger_diagnostic_ROM_departure_explicit=True,
        physical_operand_travel=True,no_whole_rule_HeadStep_or_native_syscall=True,variants=variants,native=prefix,
        full_measured_cases=len(cases),min_ticks=min(times),max_ticks=max(times),times=times,asset_sha256=digest(asset),
        exact_prepared_deadline_failure=deadline,
        universal_beta_equivalence_proved=False,universal_execution_deadline_proved=False,Q_own_beta_fit_proved=False,
        intact_start_or_Gray_refinement_or_iid_theorem_proved=False,active_rule_modified=False,wall_seconds=time.monotonic()-started)
    (directory/'GMW5_word_tape_execution_certificate.json').write_text(json.dumps(certificate,indent=2)+'\n')
    print(json.dumps(dict(cases=len(cases),min_ticks=min(times),max_ticks=max(times),wall_seconds=certificate['wall_seconds'])))


if __name__=='__main__':main()
