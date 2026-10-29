"""Finite structural contracts for the frozen complete GAW0D emission.

The accompanying written proof supplies the compositional word algebra.
This checks its exact emitted instances, helper preservation, width guards,
loop syntax, dispatch data, address bounds and phase partition.
No new raw-cell execution samples are generated.
"""
from pathlib import Path
from collections import Counter,deque
import json,sys,hashlib,time
import gaw1_compositional_cost as cost
k=cost.k;ROM=cost.ROM;ROWS=cost.ROWS;LABEL=cost.LABEL
ROOT=Path(__file__).resolve().parents[4]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw1'


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def signature(pc):
    row=ROWS[pc];return row['opcode'],tuple(row['operands'])

def roweq(pc,name,*args):assert signature(pc)==(name,args),(pc,signature(pc),(name,args))

def writes(row):
    op=row['opcode'];args=row['operands']
    if op in ('MOVI','ALU','ALUI','ALUX','LDX','CODE','BITCODE','READMASK','FULLCOL'):return {args[0]}
    if op=='READ5':return {0}
    return set()


def native_normal_form(start,centre,suffix):
    """Normalize input-acquisition syntax, not native Boolean/arithmetic code.

    Every remaining instruction is compared literally with the centre8 body.
    Native sources use FULLCOL>>centre-5, centre8 uses READMASK.
    """
    stop=LABEL['native_right'+suffix]+2
    jumps={LABEL['native_keep'+suffix]:'keep',LABEL['native_afterkeep'+suffix]:'afterkeep',LABEL['native_right'+suffix]:'right'}
    result=[];pc=start
    while pc<stop:
        op,args=signature(pc)
        if op=='MOVI' and args[0]==11 and pc+1<stop:
            # Native raw field reads: one optional lane MOVI then LDX.
            offset=args[1];n=pc+1
            if signature(n)==('MOVI',(7,centre)):n+=1
            no,na=signature(n)
            if no=='LDX' and na[1:]==(k.PRIMARY_START,11,7,0):
                assert offset in (0,1);result.append(('OLD',na[0],offset));pc=n+1;continue
            if no=='READ5' and na[0]==11:
                assert offset in (k.PRIMARY_START,k.PRIMARY_START+1) and na[2]==centre
                result.append(('FIVE',offset-k.PRIMARY_START,na[1]));pc=n+1;continue
        if op=='MOVI' and args[0]==9 and pc+1<stop:
            no,na=signature(pc+1)
            if no in ('READMASK','FULLCOL'):
                offset=args[1]-k.PRIMARY_START;assert offset in (2,3,4,5) and na[1]==9
                result.append(('FLAGS',na[0],offset));pc+=2
                if no=='FULLCOL':
                    roweq(pc,'ALUI',na[0],k.ALU['RSHIFT'],na[0],centre-5)
                    roweq(pc+1,'ALUI',na[0],k.ALU['AND'],na[0],2047);pc+=2
                else:assert centre==8
                continue
        if op=='BNZ':args=(args[0],jumps[args[1]])
        elif op=='JMP':args=(jumps[args[0]],)
        result.append((op,*args));pc+=1
    return result


def main(write=True):
    started=time.monotonic();checks={}
    # Lock the exact actual ROM, listing, slot and virtual-dispatch words.
    actual=json.loads((ROOT/'figs/gray_counterexamples/unregistered_gaw0/GAW0D_listing.json').read_text())
    assert actual['instructions']==cost.LISTING and actual['labels']==LABEL
    rawrom=json.loads((ROOT/'figs/gray_counterexamples/unregistered_gaw0/GAW0D_rom.json').read_text())
    assert rawrom['bits']==list(ROM.bits) and [int(v,16) for v in rawrom['dictionary']]==list(ROM.dictionary)
    for pc,row in ROWS.items():
        masked=tuple(v&((1<<w)-1) for v,w in zip(row['operands'],k.ARGS[row['opcode']]))
        assert k.decode(k.beta_word(ROM,pc))==(row['opcode'],masked)
    assert k.beta_word(ROM,LABEL['slots'])==sum((v&15)<<(4*i) for i,v in enumerate(k.SLOTS))
    names=('v_halt','v_jmpr','v_imm','v_alu','v_ldx','v_stx','v_five','v_mask','v_code','v_branch','v_jump','v_alui','v_alux','v_bitcode','v_fullcol')
    for i,name in enumerate(names):assert k.beta_word(ROM,LABEL['dispatch']+i)==LABEL[name]
    assert max(ROWS)<k.CODE_CAPACITY and all(0<=pc<k.CODE_CAPACITY for pc in LABEL.values())
    checks['exact_ROM_listing_slot_dispatch']=dict(instructions=len(ROWS),code_words=ROM.token_count,dispatch_cases=15)
    # All seven native bodies have exactly the same normalized arithmetic.
    template=native_normal_form(0,8,'')
    for i in range(6):assert native_normal_form(LABEL['source_'+str(i)],6+i,'_'+str(i))==template
    assert template[-2:]==[('ALUI',8,k.ALU['ADD'],8,1),('ALUI',8,k.ALU['AND'],8,k.SMALL_MASK)]
    checks['native_recipe_instances']=7
    # Vote helper is exactly the bitwise >=3 recurrence and preserves callers.
    helper=[ROWS[q] for q in range(LABEL['vote'],LABEL['slots'])]
    changed=set().union(*(writes(r) for r in helper))
    assert changed=={0,1,3,4,5,6,7,8,11}
    assert not changed & {9,10,12,13,14,15}
    roweq(LABEL['vote_loop']+7,'ALU',1,k.ALU['AND'],4,0,0)
    roweq(LABEL['vote_loop']+8,'ALU',5,k.ALU['OR'],5,1,0)
    roweq(LABEL['vote_loop']+9,'ALU',1,k.ALU['AND'],3,0,0)
    roweq(LABEL['vote_loop']+10,'ALU',4,k.ALU['OR'],4,1,0)
    roweq(LABEL['vote_loop']+11,'ALU',3,k.ALU['OR'],3,0,0)
    roweq(LABEL['vote_loop']+12,'ALUI',11,k.ALU['ADD'],11,1)
    roweq(LABEL['vote_loop']+13,'ALUI',8,k.ALU['ADD'],8,1)
    roweq(LABEL['vote_loop']+14,'ALUI',6,k.ALU['LT'],8,5)
    roweq(LABEL['vote_loop']+15,'BNZ',6,LABEL['vote_loop'])
    assert LABEL['vote_loop']-LABEL['vote']==4 and LABEL['slots']-LABEL['vote_loop']==18
    for bits in range(32):
        u=v=w=0
        for i in range(5):
            b=(bits>>i)&1;w|=v&b;v|=u&b;u|=b
        assert w==int(bits.bit_count()>=3)
    actual_calls=[pc for pc,row in ROWS.items() if row['opcode']=='JMP' and row['operands']==[LABEL['vote']]]
    for pc in actual_calls:
        roweq(pc-1,'MOVI',15,pc+1)
        assert cost.recent(pc,15)==pc+1
    checks['vote_contract']=dict(single_bit_patterns=32,instruction_updates=4+5*16+2,call_sites=len(actual_calls),preserved_registers=[9,10,12,13,14,15])
    # Raw copy slots address physical holders, including source and shifted gathers.
    holders=[]
    for centre in range(5,12):
        for i,s in enumerate(k.SLOTS):
            lane=centre-s;assert 0<=lane<17
            holders.append((centre,i,s,lane))
    checks['actual_holder_lane_coordinates']=holders
    # Every finite loop has an explicit syntactic counter increment/guard.
    loop_contracts={}
    for end,target in cost.BACK.items():
        n=cost.LOOPS[target]
        if target==LABEL['baseline_loop'] or target==LABEL['incoming_loop']:
            roweq(end-2,'ALUI',13,k.ALU['ADD'],13,1)
            roweq(end-1,'ALUI',6,k.ALU['LT'],13,n)
        elif target==LABEL['io_five_loop']:
            roweq(end-2,'ALUI',13,k.ALU['ADD'],13,1)
            roweq(end-1,'ALUI',6,k.ALU['LT'],13,5)
        elif target==LABEL['wipe_loop']:
            roweq(target,'STX',0,k.PRIMARY_START,11,0)
            roweq(end-2,'ALUI',11,k.ALU['ADD'],11,1)
            roweq(end-1,'ALUI',6,k.ALU['LT'],11,k.FRAME_WORDS)
        elif any(n.startswith('zero_head_') for n in cost.LABEL_AT[target]):
            roweq(end-3,'ALUI',11,k.ALU['ADD'],11,5)
            roweq(end-2,'ALUI',13,k.ALU['ADD'],13,1)
            roweq(end-1,'ALUI',6,k.ALU['LT'],13,22)
        else:
            assert target==LABEL['io_mask_loop']
            roweq(end-1,'ALU',6,k.ALU['LT'],13,6,0)
            assert any(signature(q)==('ALUI',(13,k.ALU['ADD'],13,1)) for q in range(target,end))
            roweq(LABEL['mask_full_bound'],'MOVI',6,17)
            assert any(signature(q)==('MOVI',(6,11)) for q in range(target,end))
        loop_contracts[str(target)]=dict(end=end,maximum_iterations=n)
    roweq(LABEL['copy_done'],'ALUI',14,k.ALU['ADD'],14,1)
    roweq(LABEL['copy_done']+1,'ALUI',6,k.ALU['LT'],14,5)
    roweq(LABEL['copy_done']+2,'BNZ',6,LABEL['copy_loop'])
    checks['loop_syntax']=loop_contracts
    # Cached temporaries are disjoint from readonly Mem and output tracks.
    temp_offsets=[]
    for pc,row in ROWS.items():
        if row['opcode'] in ('LDX','STX') and row['operands'][1]==k.PRIMARY_START+128:
            idx=row['operands'][2];offset=cost.recent(pc,idx);assert 0<=offset<=21
            temp_offsets.append(offset)
    checks['temporary_scratch_offsets']=sorted(set(temp_offsets))
    # Definite scratch initialization: exact static CFG, actual helper returns,
    # all payload/control branches, all loop back edges. Finite intersection
    # dataflow strengthens the written cache-interface proof independently
    # of the bounded-cost traversal.
    dispatch_targets=tuple(LABEL[name] for name in names)
    def successors(state):
        pc,ret=state;op,args=signature(pc)
        if op=='HLT':return ()
        if op=='JMP':
            if args[0]==LABEL['vote']:return ((args[0],cost.recent(pc,15)),)
            return ((args[0],ret),)
        if op=='JMPR':
            if pc==LABEL['slots']-1:
                assert ret is not None;return ((ret,None),)
            assert args==(6,) and ret is None
            return tuple((target,None) for target in dispatch_targets)
        if op=='BNZ':return ((pc+1,ret),(args[1],ret))
        return ((pc+1,ret),)
    initial=(0,None);before={initial:frozenset()};todo=deque([initial]);updates=0
    while todo:
        state=todo.popleft();pc,ret=state;have=before[state];op,args=signature(pc)
        if op=='STX' and args[1]==k.PRIMARY_START+128:have=have|{cost.recent(pc,args[2])}
        for nxt in successors(state):
            candidate=have if nxt not in before else before[nxt]&have
            if nxt not in before or candidate!=before[nxt]:before[nxt]=candidate;todo.append(nxt);updates+=1
    checked_reads=0
    for state,have in before.items():
        op,args=signature(state[0])
        if op=='LDX' and args[1]==k.PRIMARY_START+128:
            assert cost.recent(state[0],args[2]) in have,(state,have,args)
            checked_reads+=1
    checks['definite_temporary_initialization']=dict(CFG_states=len(before),fixed_point_updates=updates,actual_read_states=checked_reads)

    # The phase partition must include every scalar EQ/LT threshold and the
    # strict moving-lane elapsed thresholds. This is a literal algebra check.
    bound=json.loads((D/'GAW1_compositional_cost.json').read_text());cuts=set(bound['phase_partition'])
    required={0,1,k.U}
    for pc,row in ROWS.items():
        if row['opcode']=='ALUI':
            d,fn,s,v=row['operands']
            if d==6 and s==8 and fn in (k.ALU['EQ'],k.ALU['LT']) and (LABEL['workspace']<=pc<LABEL['workspace_choose'] or LABEL['copy_loop']<=pc<LABEL['active']):
                required.add(v)
                if fn==k.ALU['EQ']:required.add(v+1)
    required|={32*k.Q+1}|{(32+i)*k.Q+1 for i in range(9)}
    assert {p for p in required if 0<=p<=k.U}<=cuts,sorted(required-cuts)
    # Verify the retained measurement is covered without new executions.
    measured=json.loads((ROOT/'figs/gray_counterexamples/unregistered_gaw0/GAW0D_prepared_replays.json').read_text())
    covered=[]
    intervals=list(zip(bound['phase_partition'],bound['phase_partition'][1:],bound['records']))
    for record in measured:
        cells={j-8:k.cell_from_words([int(v,16) for v in ws]) for j,ws in enumerate(record['inputs'])}
        new_age=k.native_at(cells)['age'];b=next(r['tick_bound'] for lo,hi,r in intervals if lo<=new_age<hi)
        assert record['ticks']<=b,(record['name'],record['ticks'],b,new_age)
        covered.append(dict(name=record['name'],computed_age=new_age,retained_ticks=record['ticks'],bound=b))
    checks['retained_measurements_covered_without_new_runs']=covered
    data=dict(name='GAW1 exact emitted compositional contracts',checks=checks,
        structural_checks_pass=True,proof_scope='universal upper raw words; prepared coherent lower execution',
        no_new_raw_input_samples=True,frozen_rule_modified=False,
        sources_sha256={str(p.relative_to(ROOT)):digest(p) for p in (Path(k.__file__),ROOT/'Report/proofs/gray_counterexamples/unregistered_gaw0/build_gray_wider_word_gaw0.py',Path(cost.__file__),Path(__file__))},
        elapsed_seconds=time.monotonic()-started)
    if write:(D/'GAW1_contracts.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(dict(passed=True,native_instances=7,vote_patterns=32,retained_checks=len(covered),maximum_bound=bound['maximum_ticks'],elapsed=data['elapsed_seconds'])))
    return data

if __name__=='__main__':main()
