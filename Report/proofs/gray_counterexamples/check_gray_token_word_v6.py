#!/usr/bin/env python3
"""Pin the actual GMW6 stores and replay additional prepared comparisons.

The universal programme/physical bound has a separate contract proof and
interval checker. These retained inputs remain measured checks.
"""
from pathlib import Path
import hashlib,json,random,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
import gray_token_word_v6 as k
import build_gray_token_word_v6 as builder
import check_gray_token_word_v6_bound as bound
import check_gray_word_tape_v5 as previous


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def retain_failure(name,cells,rom,expected,actual,ticks,last,directory):
    i=1
    while (directory/('GMW6_full_execution_failure_%02d.json'%i)).exists():i+=1
    stem='GMW6_full_execution_failure_%02d'%i;sources={}
    for path in (Path(k.__file__),Path(builder.__file__),Path(__file__)):
        target=directory/(stem+'_'+path.name+'.txt');target.write_bytes(path.read_bytes());sources[target.name]=digest(target)
    row=dict(name=name,source_snapshots_sha256=sources,measured_ticks=ticks,
        pending_head=hex(k.pack(last)),
        inputs=[[hex(v) for v in k.cell_words(cells[j])] for j in range(-5,6)],
        expected=[hex(v) for v in expected],actual=[hex(v) for v in actual],
        different_words=[i for i,(a,b) in enumerate(zip(actual,expected)) if a!=b],
        changed_implementation_failure=True,Gray_or_iid_failure_proved=False)
    (directory/(stem+'.json')).write_text(json.dumps(row,indent=2)+'\n')
    (directory/(stem+'_beta.bin')).write_bytes(np.packbits(np.array(rom.bits,np.uint8),bitorder='little').tobytes())
    (directory/(stem+'_dictionary.json')).write_text(json.dumps([hex(v) for v in rom.dictionary])+'\n')
    raise AssertionError(stem+' '+name)


def fixtures(rom,listing,labels):
    rng=random.Random(0x6C0DE)
    cases=[('canonical',previous.fixture(k)),('birth',previous.fixture(k,age=112*k.Q)),
        ('commit',previous.fixture(k,age=k.U-1))]
    for opcode in k.OP_NAMES:
        row=next(r for r in listing if r['opcode']==opcode)
        for value in (0,1,k.MASK):
            h=k.Packet(p=1,pc=row['address'],regs=(value,)*16)
            cases.append(('RUN_'+opcode+'_'+str(value),previous.fixture(k,h,112*k.Q+1,seed=37)))
    for kind in range(4):
        for target in (0,k.HEAD_ADDRESS,k.Q-1,k.MASK):
            h=k.Packet(p=1,mode=k.SEEK,target=target,args=k.descriptor(kind,7,lane=3,
                source=kind,dest=kind&1,side=kind&1),regs=tuple(rng.getrandbits(k.WORD) for _ in range(16)))
            cases.append(('SEEK_'+str(kind)+'_'+str(target),previous.fixture(k,h,112*k.Q+1,seed=39)))
        cases.append(('DENSE_SEEK_'+str(kind),previous.dense_fixture(k,kind)))
    # PCs may refer to data, padding, the final legal word, or malformed100-bit
    # values. Instruction alignment is not a theorem premise.
    for pc in range(labels['slots'],rom.token_count):
        h=k.Packet(p=1,pc=pc,regs=tuple(rng.getrandbits(k.WORD) for _ in range(16)))
        cases.append(('DATA_PC_'+str(pc),previous.fixture(k,h,112*k.Q+1,seed=43)))
    for pc in (rom.token_count,k.Q-1,k.Q,k.MASK):
        cases.append(('RAW_PC_'+str(pc),previous.fixture(k,k.Packet(p=1,pc=pc),112*k.Q+1,seed=43)))
    for mode,move in ((2,0),(3,0),(4,0),(k.MASK,0),(0,3),(1,k.MASK)):
        cases.append(('RAW_META_'+str(mode)+'_'+str(move),previous.fixture(k,k.Packet(p=k.MASK,
            mode=mode,move=move,pc=k.MASK,regs=(k.MASK,)*16),112*k.Q+1,seed=43)))
    cells=previous.fixture(k,age=112*k.Q+1,seed=47)
    cells={j:k.Cell(**{**c.__dict__,'wf1':int(j in (0,1,2)),'addr':5 if j==0 else c.addr}) for j,c in cells.items()}
    assert k.local_transition(cells,rom).f1==1
    assert k.local_transition(cells,rom).heads==(0,)*5
    cases.append(('UPPER_SF_WIPE',cells))
    return cases


def static_certificates(rom,listing,labels):
    assert (len(rom),rom.token_count,rom.used_dictionary,len(listing))==(8192,899,406,884)
    assert len(rom.dictionary)==512 and rom.dictionary[0]==0
    for row in listing:
        arguments=tuple(v&((1<<w)-1) for v,w in zip(row['operands'],k.ARGS[row['opcode']]))
        assert k.decode(k.beta_word(rom,row['address']))==(row['opcode'],arguments)
        assert k.beta_word(rom,row['address'])==int(row['word'],16)
    slotword=k.beta_word(rom,labels['slots'])
    assert [k.generic_alu(k.ALU['SIGNEXT'],k.generic_alu(k.ALU['RSHIFT'],slotword,4*i),4) for i in range(5)]==[s&k.MASK for s in k.SLOTS]
    dispatch=[]
    targets=('v_halt','v_jmpr','v_imm','v_alu','v_ldx','v_stx','v_five','v_mask',
        'v_code','v_branch','v_jump','v_alui','v_alux','v_bitcode')
    for op,label in enumerate(targets):
        assert k.beta_word(rom,labels['dispatch']+op)==labels[label]
        dispatch.append(dict(opcode=k.OP_NAMES[op],target=labels[label]))
    accesses=[]
    for copy,s in enumerate(k.SLOTS):
        for source_delta in (-1,0,1):
            for q,t in enumerate(k.SLOTS):
                logical=s+source_delta;lane=logical-t+5
                assert 0<=lane<=10 and abs(logical-t)<=5
                accesses.append(dict(copy=copy,source_delta=source_delta,raw_copy=q,
                    actual_input_cell=logical-t,lane=lane,
                    first_head_word_primary=k.PRIMARY_START+6+q))
    assert len(accesses)==75
    return dict(decoded_instructions=len(listing),dispatch=dispatch,
        raw_holder_accesses=accesses,all_raw_radius=5,total_physical_alphabet_bits=18537)


def main():
    started=time.monotonic();directory=ROOT/'figs/gray_counterexamples';source=Path(__file__).parent
    rom,listing,labels,errors=builder.programme().assemble();assert not errors
    static=static_certificates(rom,listing,labels)
    bits=directory/'GMW6_token_beta.bin';bits.write_bytes(np.packbits(np.array(rom.bits,np.uint8),bitorder='little').tobytes())
    dictionary=directory/'GMW6_dictionary.json';dictionary.write_text(json.dumps([hex(v) for v in rom.dictionary],separators=(',',':'))+'\n')
    code=directory/'GMW6_token_listing.json';code.write_text(json.dumps(dict(instructions=listing,labels=labels,errors=errors),separators=(',',':'))+'\n')
    cases=fixtures(rom,listing,labels);rows=[]
    for name,cells in cases:
        expected=k.cell_words(k.local_transition(cells,rom));out,ticks,last,_=k.execute(rom,k.input_tape(cells),limit=65535)
        actual=[out.get(k.PRIMARY_START+i,0) for i in range(k.FRAME_WORDS)]
        if last.mode!=k.HALT or actual!=expected:retain_failure(name,cells,rom,expected,actual,ticks,last,directory)
        rows.append(dict(name=name,inputs=[[hex(v) for v in k.cell_words(cells[j])] for j in range(-5,6)],
            outputs=[hex(v) for v in actual],ticks=ticks))
        if name=='canonical' or name.startswith('DENSE'):print(name,ticks,flush=True)
    replay=directory/'GMW6_full_replays.json';replay.write_text(json.dumps(rows,separators=(',',':'))+'\n')
    execution_bound=bound.validate()
    bound_path=directory/'GMW6_execution_bound.json';bound_path.write_text(json.dumps(execution_bound,indent=2)+'\n')
    deps=['gray_moving_word_v2.py','gray_moving_word_kernel.py','literal_maintenance.py','check_gray_word_tape_v5.py']
    receipt=dict(name='GMW6 changed token/dictionary prepared self-evaluator',Q=k.Q,U=k.U,
        lambda_original=24,c_original=104,kernel_sha256=digest(k.__file__),builder_sha256=digest(builder.__file__),
        checker_sha256=digest(__file__),bound_checker_sha256=digest(bound.__file__),
        proof_sha256=digest(source/'GMW6_TOKEN_WORD_EVALUATOR.md'),
        dependency_sources_sha256={name:digest(source/name) for name in deps},
        beta_sha256=digest(bits),dictionary_sha256=digest(dictionary),listing_sha256=digest(code),
        replay_sha256=digest(replay),bound_sha256=digest(bound_path),
        used_beta_bits=rom.token_count*9,beta_capacity_bits=8192,
        used_dictionary_words=rom.used_dictionary,dictionary_capacity_bits=51200,
        total_immutable_capacity_bits=59392,alphabet_bits=18537,frame_words=k.FRAME_WORDS,
        physical_word_PC_dictionary_BITCODE_and_scratch_change_explicit=True,
        no_whole_rule_or_native_or_HeadStep_syscall=True,
        prepared_no_error_upper_raw_semantics_proved_by_contracts=True,
        universal_prepared_deadline_bound=execution_bound['total_active_execution_bound'],
        static=static,finite_comparisons=len(rows),min_ticks=min(r['ticks'] for r in rows),
        max_ticks=max(r['ticks'] for r in rows),finite_comparisons_measured_only=True,
        complete_period_proved=False,Gray_faithful_Q_bit_evaluator_proved=False,
        continuing_E0_or_higher_or_intact_counterexample_proved=False,
        iid_reliability_or_shorter_U_proved=False,active_rule_modified=False,
        elapsed_seconds=time.monotonic()-started)
    path=directory/'GMW6_token_word_certificate.json';path.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(cases=len(rows),beta_bits=rom.token_count*9,total_ROM=59392,
        measured_max=receipt['max_ticks'],universal_prepared_bound=receipt['universal_prepared_deadline_bound'],elapsed_seconds=receipt['elapsed_seconds'])))


if __name__=='__main__':main()
