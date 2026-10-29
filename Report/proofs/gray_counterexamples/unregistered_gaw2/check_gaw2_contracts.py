"""Finite structural contracts for the frozen complete GAW0D emission.

The accompanying written proof supplies the compositional word algebra.
This checks its exact emitted instances, helper preservation, width guards,
loop syntax, dispatch data, address bounds and phase partition.
No new raw-cell execution samples are generated.
"""
from pathlib import Path
from collections import Counter,deque
import json,sys,hashlib,time
import gaw2_compositional_cost as cost
if len(sys.argv)>1 and sys.argv[1]=="R":
    import gaw2r_compositional_cost as cost
k=cost.k;ROM=cost.ROM;ROWS=cost.ROWS;LABEL=cost.LABEL
ROOT=Path(__file__).resolve().parents[4]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw2'
TAG='GAW2R' if cost.k.STAGE_STARTS[-1]==102*cost.k.Q else 'GAW2D'


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



def algebra(fn,a,b=0,c=0):
    def ordered(x):return repr(x)
    if fn==k.ALU['MOV']:return a
    if fn==k.ALU['SHIFT'] or fn==k.ALU['RSHIFT']:
        assert isinstance(a,int) and isinstance(b,int)
        n=(-b if fn==k.ALU['RSHIFT'] else b)
        return ((a<<n) if n>=0 else (a>>-n))&k.MASK
    if fn==k.ALU['SIGNEXT']:
        assert isinstance(a,int);a&=(1<<b)-1
        return (a-(1<<b) if a&(1<<(b-1)) else a)&k.MASK
    if fn in (k.ALU['AND'],k.ALU['OR']):
        if a==b:return a
        if fn==k.ALU['AND'] and (a==0 or b==0):return 0
        if fn==k.ALU['OR'] and a==0:return b
        if fn==k.ALU['OR'] and b==0:return a
        if isinstance(a,int) and isinstance(b,int):return a&b if fn==k.ALU['AND'] else a|b
        return ('AND' if fn==k.ALU['AND'] else 'OR',*sorted((a,b),key=ordered))
    assert isinstance(a,int) and isinstance(b,int),(fn,a,b,c)
    if fn==k.ALU['ADD']:return (a+b)&k.MASK
    if fn==k.ALU['SUB']:return (a-b)&k.MASK
    if fn==k.ALU['EQ']:return int(a==b)
    if fn==k.ALU['LT']:return int(a<b)
    raise AssertionError(('unhandled symbolic ALU',fn))


def symbolic_data_contract(bound):
    # Exact emitted region, with symbolic old WORD100 operands. The already
    # verified vote helper is abstracted by its precise field/holder function.
    instances=0;calls=0
    for clock in bound['phase_partition'][:-1]:
        for flag in (0,1):
            for copy in range(5):
                y=k.SLOTS[copy];regs=[0]*16;regs[14]=copy
                vote=lambda field,z:('OLDVOTE',field,z)
                outputs={k.FIELD[n]+copy:vote(k.FIELD[n],y) for n in k.FIELD_NAMES}
                pc=LABEL['data_updates'];steps=0
                while pc!=LABEL['commit_info']-6:
                    steps+=1;assert steps<6000
                    op,args=signature(pc)
                    if op=='JMP' and args[0]==LABEL['vote']:
                        assert regs[11] in k.FIELD.values()
                        regs[0]=vote(regs[11],regs[12]-8)
                        for z in (1,3,4,5):regs[z]=('HELPER_CLOBBER',z)
                        regs[6]=0;regs[7]=16;regs[8]=5;regs[11]+=5
                        pc=regs[15];calls+=1;continue
                    if op=='JMP':pc=args[0];continue
                    if op=='BNZ':
                        assert isinstance(regs[args[0]],int)
                        pc=args[1] if regs[args[0]] else pc+1;continue
                    if op=='MOVI':regs[args[0]]=args[1]
                    elif op=='ALU':regs[args[0]]=algebra(args[1],regs[args[2]],regs[args[3]],regs[args[4]])
                    elif op=='ALUI':regs[args[0]]=algebra(args[1],regs[args[2]],args[3])
                    elif op=='CODE':
                        assert args[1]==7 and regs[7]==LABEL['slots']
                        regs[args[0]]=k.beta_word(ROM,LABEL['slots'])
                    elif op=='LDX':
                        d,base,index,lane,source=args;offset=base-k.PRIMARY_START+regs[index]
                        assert regs[lane]==8 and source==1 and offset in (1,2),(pc,args,offset,clock)
                        regs[d]=clock if offset==1 else flag
                    elif op=='STX':
                        value,base,index,dest=args;assert dest==0
                        outputs[base-k.PRIMARY_START+regs[index]]=regs[value]
                    else:raise AssertionError(('symbolic region',pc,op,args))
                    pc+=1
                    # The final readAge and commit predicate jump around
                    # commit_info for nonzero Age: stop just before that read.
                    if pc==LABEL['commit_info']-6:break
                expected={k.FIELD[n]+copy:vote(k.FIELD[n],y) for n in k.FIELD_NAMES}
                for n,shift in (('mail_l',1),('mail_r',-1)):
                    v=vote(k.FIELD[n],y)
                    if flag or clock in k.STAGE_STARTS:v=0
                    elif clock in tuple(s+1 for s in k.GATHER_STARTS):v=vote(k.FIELD['info'],y)
                    elif any(s<=clock<s+16*k.Q for s in k.GATHER_STARTS):v=vote(k.FIELD[n],y+shift)
                    expected[k.FIELD[n]+copy]=v
                for g in (1,2,3):
                    for lane in range(17):
                        f=k.FIELD['h%d_%d'%(g,lane)];v=vote(f,y)
                        if clock in k.GATHER_STARTS[:g]:v=0
                        elif clock==k.capture(g,lane):v=vote(k.FIELD['info' if lane==8 else 'mail_r' if lane<8 else 'mail_l'],y)
                        expected[f+copy]=v
                for lane in range(17):
                    f=k.FIELD['m'+str(lane)];v=vote(f,y)
                    if clock in k.STAGE_STARTS:v=0
                    elif clock in (k.EARLY_RESET,k.STAGE_STARTS[-1]+1):
                        a,b,c=(vote(k.FIELD['h%d_%d'%(g,lane)],y) for g in (1,2,3))
                        v=algebra(k.ALU['OR'],algebra(k.ALU['AND'],a,b),algebra(k.ALU['AND'],c,algebra(k.ALU['OR'],a,b)))
                    expected[f+copy]=v
                assert outputs==expected,(clock,flag,copy,[(f,outputs[f],expected[f]) for f in outputs if outputs[f]!=expected[f]])
                instances+=1
    return dict(instances=instances,actual_vote_calls=calls,all_WORD100_inputs_symbolic=True,phase_classes=len(bound['records']))


def symbolic_courier_contract(bound):
    # All free old courier/output/Info WORD100 values are formal atoms.
    # Address comparisons are constant on the displayed exact partition.
    address_cuts=sorted({0,3,4,k.PRIMARY_START+2,k.PRIMARY_START+3,k.PRIMARY_START+4,k.Q-3,k.Q-2,k.Q})
    start=LABEL['courier_clear']-(2*len(k.STAGE_STARTS)+7)
    roweq(start,'ALUI',6,k.ALU['EQ'],8,k.STAGE_STARTS[0])
    instances=0
    for clock in bound['phase_partition'][:-1]:
        for address in address_cuts[:-1]:
            for copy in range(5):
                y=k.SLOTS[copy];regs=[0]*16;regs[8]=clock;regs[14]=copy
                vote=lambda field,z:('OLDVOTE',field,z)
                outputs={k.FIELD[n]+copy:vote(k.FIELD[n],y) for n in k.FIELD_NAMES}
                scratch={10:address};pc=start;steps=0
                while pc!=LABEL['special_after']:
                    steps+=1;assert steps<300
                    op,args=signature(pc)
                    if op=='JMP' and args[0]==LABEL['vote']:
                        f=regs[11];z=regs[12]-8;regs[0]=vote(f,z)
                        for q in (1,3,4,5):regs[q]=('HELPER_CLOBBER',q)
                        regs[6]=0;regs[7]=16;regs[8]=5;regs[11]+=5;pc=regs[15];continue
                    if op=='JMP':pc=args[0];continue
                    if op=='BNZ':
                        assert isinstance(regs[args[0]],int),(pc,args,regs[args[0]])
                        pc=args[1] if regs[args[0]] else pc+1;continue
                    if op=='MOVI':regs[args[0]]=args[1]
                    elif op=='ALU':regs[args[0]]=algebra(args[1],regs[args[2]],regs[args[3]],regs[args[4]])
                    elif op=='ALUI':regs[args[0]]=algebra(args[1],regs[args[2]],args[3])
                    elif op=='CODE':
                        assert regs[args[1]]==LABEL['slots'];regs[args[0]]=k.beta_word(ROM,LABEL['slots'])
                    elif op=='LDX':
                        d,base,index,lane,source=args;offset=base-k.PRIMARY_START+regs[index]
                        assert regs[lane]==8
                        if source==2:regs[d]=scratch[offset-128]
                        else:
                            assert source==1
                            regs[d]=clock if offset==1 else outputs[offset]
                    elif op=='STX':
                        value,base,index,dest=args;offset=base-k.PRIMARY_START+regs[index]
                        if dest==1:scratch[offset-128]=regs[value]
                        else:outputs[offset]=regs[value]
                    else:raise AssertionError(('symbolic courier region',pc,op,args))
                    pc+=1
                for n,shift,seed,target,lo,hi in (
                    ('courier_l',1,k.PRIMARY_START+3,3,3,k.PRIMARY_START+3),
                    ('courier_r',-1,k.PRIMARY_START+2,k.Q-3,k.PRIMARY_START+2,k.Q-3)):
                    f=k.FIELD[n];expected=vote(f,y)
                    if clock in k.STAGE_STARTS:expected=0
                    elif clock==75*k.Q:expected=algebra(k.ALU['AND'],vote(k.FIELD['out'],y),1) if address==seed else 0
                    elif 75*k.Q<clock<80*k.Q:
                        expected=vote(f,y+shift) if lo<=address<=hi else 0
                        if address==target:expected=algebra(k.ALU['OR'],vote(f,y),expected)
                    assert outputs[f+copy]==expected,(clock,address,copy,n,outputs[f+copy],expected)
                expected_info=vote(k.FIELD['info'],y)
                if clock==80*k.Q-1 and address in (3,k.Q-3):expected_info=vote(k.FIELD['courier_l' if address==3 else 'courier_r'],y)
                assert outputs[k.FIELD['info']+copy]==expected_info
                instances+=1
    return dict(instances=instances,address_partition=address_cuts,all_WORD100_inputs_symbolic=True)

def main(write=True):
    started=time.monotonic();checks={}
    # Lock the exact actual ROM, listing, slot and virtual-dispatch words.
    actual=json.loads((D/(TAG+'_listing.json')).read_text())
    assert actual['instructions']==cost.LISTING and actual['labels']==LABEL
    rawrom=json.loads((D/(TAG+'_rom.json')).read_text())
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
    # Every actual head-selection and virtual-opcode equation remains the
    # proved GAW0D block. Normalize only frame base and code relocation.
    frozen=json.loads((ROOT/'figs/gray_counterexamples/unregistered_gaw0/GAW0D_listing.json').read_text())
    oldrows={r['address']:r for r in frozen['instructions']};oldlabels=frozen['labels']
    oldP=3981
    def head_block(rows,labels,P):
        start=labels['active'];end=labels['copy_done'];result=[]
        for pc in range(start,end):
            r=rows[pc];op=r['opcode'];args=list(r['operands'])
            if op in ('LDX','STX'):args[1]-=P
            if op=='BNZ':args[1]-=start
            elif op=='JMP':args[0]='VOTE' if args[0]==labels['vote'] else args[0]-start
            elif op=='MOVI' and args[0]==15:args[1]-=start
            elif op=='MOVI' and args[0]==7 and args[1]==labels['slots']:args[1]='SLOTS'
            elif op=='ALUI' and args[:3]==[6,k.ALU['ADD'],9] and args[3]==labels['dispatch']:args[3]='DISPATCH'
            result.append((op,tuple(args)))
        return result
    current=head_block(ROWS,LABEL,k.PRIMARY_START);reference=head_block(oldrows,oldlabels,oldP)
    assert current==reference,[(i,a,b) for i,(a,b) in enumerate(zip(current,reference)) if a!=b][:3]
    checks['exact_inherited_head_opcode_body']=dict(instructions=len(current),normalizations=['physical_frame_base','code_and_return_relocation'])

    # Vote helper is exactly the bitwise >=3 recurrence and preserves callers.
    helper=[ROWS[q] for q in range(LABEL['vote'],LABEL['slots'])]
    changed=set().union(*(writes(r) for r in helper))
    assert changed=={0,1,3,4,5,6,7,8,11}
    assert not changed & {2,9,10,12,13,14,15}
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
    checks['vote_contract']=dict(single_bit_patterns=32,instruction_updates=4+5*16+2,call_sites=len(actual_calls),preserved_registers=[2,9,10,12,13,14,15])
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
    bound=json.loads((D/('GAW2R_compositional_cost.json' if TAG=='GAW2R' else 'GAW2_compositional_cost.json')).read_text());cuts=set(bound['phase_partition'])
    required={0,1,k.U}
    for pc,row in ROWS.items():
        if row['opcode']=='ALUI':
            d,fn,s,v=row['operands']
            if d==6 and s==8 and fn in (k.ALU['EQ'],k.ALU['LT']) and (LABEL['workspace']<=pc<LABEL['workspace_choose'] or LABEL['copy_loop']<=pc<LABEL['active']):
                required.add(v)
                if fn==k.ALU['EQ']:required.add(v+1)
    assert {p for p in required if 0<=p<=k.U}<=cuts,sorted(required-cuts)
    # Entire emitted early native pass equals the central native prefix,
    # with local native jump labels relocated and HLT replacing JMP workspace.
    prefix_stop=LABEL['workspace']
    early_start=LABEL['early_entry']
    assert early_start==ROM.early_pc
    assert signature(early_start+prefix_stop-1)==('HLT',())
    for pc in range(prefix_stop-1):
        op,args=signature(pc);eo,ea=signature(early_start+pc)
        if op=='BNZ':args=(args[0],early_start+args[1])
        elif op=='JMP':args=(early_start+args[0],)
        assert (op,args)==(eo,ea),(pc,(op,args),(eo,ea))
    checks['early_native_pass']=dict(instructions=prefix_stop,maximum_operand_waits=16,maximum_ticks=prefix_stop+16*5)
    assert checks['early_native_pass']['maximum_ticks']==213
    roweq(LABEL['data_updates'],'MOVI',11,1)
    roweq(LABEL['data_updates']+1,'MOVI',7,8)
    roweq(LABEL['data_updates']+2,'LDX',2,k.PRIMARY_START,11,7,1)
    checks['clock_cache']=dict(register=2,helper_preserves=True,first_load=LABEL['data_updates'])
    checks['symbolic_new_field_equations']=symbolic_data_contract(bound)
    checks['symbolic_courier_equations']=symbolic_courier_contract(bound)
    data=dict(name=TAG+' exact emitted compositional contracts',checks=checks,
        structural_checks_pass=True,proof_scope='universal upper raw words; prepared coherent lower execution',
        no_new_raw_input_samples=True,frozen_rule_modified=False,
        sources_sha256={str(p.relative_to(ROOT)):digest(p) for p in (Path(k.__file__),Path(cost.b.__file__),Path(cost.__file__),Path(__file__))},
        elapsed_seconds=time.monotonic()-started)
    if write:(D/(TAG+'_contracts.json')).write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(dict(passed=True,native_instances=7,vote_patterns=32,symbolic_checks=checks["symbolic_new_field_equations"]["instances"],maximum_bound=bound['maximum_ticks'],elapsed=data['elapsed_seconds'])))
    return data

if __name__=='__main__':main()
