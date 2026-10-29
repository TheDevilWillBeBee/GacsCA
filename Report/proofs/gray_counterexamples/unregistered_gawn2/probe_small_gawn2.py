"""GAWN2 changed-width structural contracts and measured own-ROM supplements.

Native normal form, formal Mail/History/courier equations, loop and definite
scratch checks are copied from the frozen GAW2 checker and use the new
actual listing. Helper supplement is copied from GAWN1. Universal claims
are stated in the companion proof; no noisy inference comes from samples.
"""
from pathlib import Path
from collections import Counter,deque
from dataclasses import asdict,replace
import hashlib,json,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE))
import build_small_gawn2 as b
import small_rule_gawn2 as k
import small_compositional_cost as cost
import derive_small_rule_gawn2 as derive
OUT=ROOT/'figs/gray_counterexamples/unregistered_gawn2'
ROM=cost.ROM;ROWS=cost.ROWS;LABEL=cost.LABEL

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

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

def helper_replay(rom,labels):
    cases=[];full_words=0
    for bits in range(32):
        for centre in range(2,15):
            words=[(k.MASK if bits>>i&1 else 0) for i in range(5)]
            full_words+=1;field=6 if bits%2 else k.FRAME_WORDS-5
            initial=tuple((1<<90)+17*q for q in range(16))
            r=list(initial);r[11]=field;r[12]=centre;r[15]=0
            p=k.Packet(p=1,pc=labels['vote'],regs=tuple(r));position=k.PRIMARY_START+field
            tape={k.PRIMARY_START+field+i:words[i]<<((centre-slot)*k.WORD) for i,slot in enumerate(k.SLOTS)}
            instructions=0;steps=0
            while True:
                oldp=p;position+=1 if p.move==1 else -1 if p.move==2 else 0
                p,ow,sw=k.step_packet(p,position,tape.get(position,0),0,0,k.beta_bit(rom,position),rom)
                assert ow is None and sw is None and p.mode not in (k.ERROR,k.HALT)
                steps+=1;instructions+=int(oldp.mode==k.RUN)
                if oldp.mode==k.RUN and k.decode(k.beta_word(rom,oldp.pc))[0]=='JMPR':break
                assert steps<=50
            u=v=w=0;last=0
            for word in words:
                w|=v&word;last=u&word;v|=last;u|=word
            expected=list(r)
            for dst,val in ((0,w),(1,last),(3,u),(4,v),(5,w),(6,0),(7,16),(8,5),(11,field+5)):expected[dst]=val
            assert tuple(expected)==p.regs and p.pc==0 and p.mode==k.RUN and p.move==0
            assert instructions==37 and steps==42 and position==k.PRIMARY_START+field+4
            cases.append(dict(bits=bits,centre=centre,field=field,instructions=instructions,updates=steps))
    return dict(cases=cases,all32_bit_masks_all13_safe_centres_both_frame_edges=full_words,
        exact_all16_return_registers_checked=True,all100_bit_positions_by_bitwise_independence_in_written_proof=True)

def remaining_contracts():
    checks={}
    names=('v_halt','v_jmpr','v_imm','v_alu','v_ldx','v_stx','v_five','v_mask','v_code','v_branch','v_jump','v_alui','v_alux','v_bitcode','v_fullcol')
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

    return checks

def syntax_and_normalization(rom,listing,labels,a):
    rebuilt,origins=derive.source()
    assert rebuilt==(HERE/'small_rule_gawn2.py').read_text()
    derivation=json.loads((OUT/'GAWN2_rule_derivation.json').read_text())
    assert derivation['source_origins_sha256']==origins
    assert derivation['rule_sha256']==sha(k.__file__)
    assert derivation['generator_sha256']==sha(derive.__file__)
    assert a.initial_unresolved_rows==b.inherited.programme(engine=k).rows
    assert Counter(s['kind'] for s in a.substitutions)=={
        'GF_vector_width':16,'native_Age_successor_modulus':8,
        'service_GF_modulus':5,'late_schedule':4}
    assert json.loads((OUT/'GAWN2_rom.json').read_text())==json.loads(json.dumps(asdict(rom)))
    assert json.loads((OUT/'GAWN2_listing.json').read_text())==dict(listing=listing,labels=labels)
    assert (k.Q,k.U,k.PC_BITS,k.GF_BITS,k.AGE_BITS,k.FRAME_WORDS,k.PRIMARY_START)==(4096,524288,12,12,19,496,1800)
    assert k.ARGS['JMP']==(12,) and k.ARGS['BNZ']==(4,12)
    assert k.SMALL_MASK==(1<<20)-1 and k.AGE_MASK==(1<<19)-1
    assert len(rom.bits)==65536 and len(rom.dictionary)==2048
    assert rom.token_count==3829 and rom.used_dictionary==1055
    assert max(ROWS)<4096 and all(0<=pc<4096 for pc in labels.values())
    for pc,row in ROWS.items():
        masked=tuple(v&((1<<w)-1) for v,w in zip(row['operands'],k.ARGS[row['opcode']]))
        assert k.decode(k.beta_word(rom,pc))==(row['opcode'],masked)
    assert k.beta_word(rom,labels['slots'])==sum((v&15)<<(4*i) for i,v in enumerate(k.SLOTS))
    names=('v_halt','v_jmpr','v_imm','v_alu','v_ldx','v_stx','v_five','v_mask','v_code','v_branch','v_jump','v_alui','v_alux','v_bitcode','v_fullcol')
    for i,name in enumerate(names):assert k.beta_word(rom,labels['dispatch']+i)==labels[name]
    mask_pcs=[];age_macro_pcs=[];raw_sf=[];vectors=[];flags=[]
    for pc,row in ROWS.items():
        op,args=signature(pc)
        if op=='LDX' and args[4]==0:
            assert args[1]==k.PRIMARY_START and args[2]==11
            if args[3]==7:
                assert signature(pc+1)[0]=='ALUI'
                width=next(m['width'] for m in a.direct_masks
                    if m['field']==(0 if signature(pc+1)[1][3]==4095 else 1))
                roweq(pc+1,'ALUI',args[0],k.ALU['AND'],args[0],(1<<width)-1)
                mask_pcs.append(pc+1)
            else:
                assert args[3]==6 and labels['vote']<=pc<labels['slots'];raw_sf.append(pc)
        if op=='READ5':
            roweq(pc-1,'MOVI',11,signature(pc-1)[1][1])
            field=signature(pc-1)[1][1]-k.PRIMARY_START;assert field in (0,1)
            if field==0:
                assert signature(pc+1) in [('MOVI',(1,-1)),('MOVI',(1,1))]
                roweq(pc+2,'MOVI',15,12)
            else:
                roweq(pc+1,'MOVI',1,0);roweq(pc+2,'MOVI',15,19)
                age_macro_pcs.append(pc)
            roweq(pc+3,'ALU',0,k.ALU['VADDINDEX'],0,1,15)
            assert not any(q in labels.values() for q in range(pc+1,pc+4))
            vectors.append(dict(pc=pc,field=field,side=args[1],centre=args[2]))
        if op in ('READMASK','FULLCOL'):
            before=signature(pc-1);assert before[0]=='MOVI' and before[1][0]==9
            field=before[1][1]-k.PRIMARY_START;assert field in (2,3,4,5)
            flags.append(dict(pc=pc,field=field,opcode=op))
    assert len(mask_pcs)==24 and len(raw_sf)==5
    assert Counter(v['field'] for v in vectors)=={0:16,1:16}
    assert len(flags)==32 and Counter(v['opcode'] for v in flags)=={'READMASK':8,'FULLCOL':24}
    assert not set(mask_pcs)&set(labels.values())
    # The added Age projection clobbers R1/R15 only after using them in
    # VADDINDEX. Both are overwritten before any subsequent use.
    def reads(op,args):
        if op=='MOVI':return set()
        if op=='BNZ':return {args[0]}
        if op in ('JMP','HLT'):return set()
        if op=='ALUI':return {args[2]}
        if op=='ALU':
            fn=args[1];r={args[2]}
            if fn not in (k.ALU['MOV'],k.ALU['NOT'],k.ALU['POPCOUNT'],k.ALU['BITNOT']):r.add(args[3])
            if fn in (k.ALU['WINDOW'],k.ALU['VADDINDEX'],k.ALU['VINSIDE']):r.add(args[4])
            return r
        if op=='LDX':return {args[2],args[3]}
        if op=='STX':return {args[0],args[2]}
        if op=='READ5':return {args[0]}
        if op in ('READMASK','FULLCOL','CODE','BITCODE'):return {args[1]}
        raise AssertionError((op,args))
    for pc in age_macro_pcs:
        pending={1,15};q=pc+4
        while pending:
            op,args=signature(q);assert not pending&reads(op,args),(pc,q,pending,op,args)
            assert op not in ('JMP','JMPR','BNZ','HLT')
            pending-=writes(ROWS[q]);q+=1
            assert q-pc<100
    template=native_normal_form(0,8,'')
    for i in range(6):assert native_normal_form(labels['source_'+str(i)],6+i,'_'+str(i))==template
    assert template[-2:]==[('ALUI',8,k.ALU['ADD'],8,1),('ALUI',8,k.ALU['AND'],8,k.AGE_MASK)]
    prefix=labels['workspace'];early=labels['early_entry']
    assert prefix==141 and rom.early_pc==early==3673
    roweq(early+prefix-1,'HLT')
    for pc in range(prefix-1):
        op,args=signature(pc)
        if op=='BNZ':args=(args[0],early+args[1])
        elif op=='JMP':args=(early+args[0],)
        assert signature(early+pc)==(op,args)
    # Upper generic READ5 remains a 20-bit operation, distinct from
    # the 19-bit native Age acquisition just proved.
    generic_masks=[pc for pc in range(labels['io_five_loop'],labels['io_mask'])
        if signature(pc)==('ALUI',(0,k.ALU['AND'],0,k.SMALL_MASK))]
    assert len(generic_masks)==1
    return dict(source_copy_derivation_recomputed=True,source_origins_sha256=origins,
        substitution_counts=dict(Counter(s['kind'] for s in a.substitutions)),
        direct_native_masks=24,native_vectors=vectors,native_flag_acquisitions=flags,
        sole_SF_helper_five_full_word_LDXs=raw_sf,
        all_Age_projection_R1_R15_clobbers_dead_until_redefined=True,
        no_partial_normalization_macro_entry=True,all7_native_body_instances_identical=True,
        early_instructions=141,early_operand_waits=16,early_bound=221,
        upper_generic_READ5_preserves20_bits=True,all_declared_PC_operand_widths_targets_and_ROM_decode_checked=True)

def cost_replay():
    previous=HERE.parent/'unregistered_gawn1/gawn1_compositional_cost.py'
    source=previous.read_text().split('\n',3)[3]
    source=source.replace('import unrolled_gawn1 as k','import small_rule_gawn2 as k').replace('import build_unrolled_gawn1 as b','import build_small_gawn2 as b')
    source=source.replace('unregistered_gawn1','unregistered_gawn2').replace('GAWN1','GAWN2')
    source=source.replace('available_ticks=18*k.Q-1','available_ticks=k.ACTIVE_END-k.LATE_BIRTH')
    assert Path(cost.__file__).read_text().split('\n',3)[3]==source
    bound=json.loads((OUT/'GAWN2_compositional_cost.json').read_text())
    required={0,1,k.U}
    for pc,row in ROWS.items():
        if row['opcode']=='ALUI':
            d,fn,s,v=row['operands']
            if d==6 and s==8 and fn in (k.ALU['EQ'],k.ALU['LT']) and (LABEL['workspace']<=pc<LABEL['workspace_choose'] or LABEL['copy_loop']<=pc<LABEL['active']):
                required.add(v)
                if fn==k.ALU['EQ']:required.add(v+1)
    assert {p for p in required if 0<=p<=k.U}==set(bound['phase_partition'])
    records=[cost.run(t) for t in bound['phase_partition'][:-1]]
    assert records==bound['records'] and len(records)==72
    assert bound['maximum_ticks']==max(r['tick_bound'] for r in records)==104572
    assert bound['available_ticks']==k.ACTIVE_END-k.LATE_BIRTH==110591
    contracts=remaining_contracts()
    contracts['symbolic_new_field_equations']=symbolic_data_contract(bound)
    contracts['symbolic_courier_equations']=symbolic_courier_contract(bound)
    return dict(all72_phase_classes_all_payload_branches_recomputed=True,
        previous_cost_source_sha256=sha(previous),exact_import_output_window_only_derivative=True,
        full_bound=104572,available_late_updates=110591,late_margin=6019,contracts=contracts)

def sample_cells(kind):
    cells={};pc_by_op={}
    for row in cost.LISTING:pc_by_op.setdefault(row['opcode'],row['address'])
    for j in range(-8,9):
        age=123 if kind in ('canonical_padding','no_GF_quorum_padding') else k.U-1 if kind=='commit_padding' else k.LATE_BIRTH
        addr=(200+(17*j if kind=='no_GF_quorum_padding' else j))%k.Q
        words=[0]*k.FRAME_WORDS;words[:6]=[addr,age,int(kind=='canonical_padding'),0,0,0]
        for f in range(6):words[f]|=(1<<(k.NATIVE_WIDTHS[f]+3+(j+8)%4))|(1<<99)
        for name,val in [('info',7),('out',(1<<99)+19),('scratch',(1<<76)+5),('program',(1<<80)+3)]:
            words[k.FIELD[name]:k.FIELD[name]+5]=[val]*5
        c=k.cell_from_words(words)
        if kind in ('active_upper_head_padding','upper_invalid_PC','upper_jmpr4095','upper_jmpr4096','upper_jmpr8191'):
            regs=[(1<<90)+r for r in range(16)];pc=0 if kind=='active_upper_head_padding' else 4096
            if kind.startswith('upper_jmpr'):
                pc=pc_by_op['JMPR'];register=next(r['operands'][0] for r in cost.LISTING if r['address']==pc)
                regs[register]=int(kind.removeprefix('upper_jmpr'))
            packet=k.Packet(p=1,pc=pc,regs=tuple(regs));c=replace(c,heads=(k.pack(packet),)*5)
        elif kind=='upper_generic_READ5_bit19':
            mem=sum((1<<19)<<(lane*k.WORD) for lane in range(17))
            c=replace(c,mem=(mem,)*5,heads=tuple(k.pack(k.Packet(p=1,mode=k.SEEK,
                target=(addr+slot)%k.Q,args=k.descriptor(2,lane=8,side=1))) for slot in k.SLOTS))
        cells[j]=c
    return cells

def selected_runs(rom):
    records=[]
    kinds=('canonical_padding','no_GF_quorum_padding','commit_padding','active_upper_head_padding',
        'upper_invalid_PC','upper_jmpr4095','upper_jmpr4096','upper_jmpr8191','upper_generic_READ5_bit19')
    for kind in kinds:
        raw=sample_cells(kind);legal=k.project_neighborhood(raw);expected=k.cell_words(k.local_transition(raw,rom))
        runs=[];early=[]
        for inputs in (raw,legal):
            out,ticks,packet,_=k.execute(rom,k.input_tape(inputs),limit=104573)
            actual=[out.get(k.PRIMARY_START+i,0) for i in range(k.FRAME_WORDS)]
            assert packet.mode==k.HALT and actual==expected,(kind,ticks,packet.mode,
                [(i,hex(v),hex(w)) for i,(v,w) in enumerate(zip(actual,expected)) if v!=w])
            runs.append(dict(ticks=ticks,all496_output_words=[hex(v) for v in actual]))
            out,ticks,packet,_=k.execute(rom,k.input_tape(inputs),limit=222,early=True)
            vals=[out.get(k.PRIMARY_START+i,0) for i in range(6)]
            assert packet.mode==k.HALT and vals==expected[:4]+[0,0]
            early.append(dict(ticks=ticks,six_native_outputs=vals))
        assert runs[0]==runs[1] and early[0]==early[1]
        if kind=='upper_generic_READ5_bit19':
            assert all(k.unpack(h).regs[0]==sum((1<<19)<<(20*i) for i in range(5))
                for h in k.local_transition(raw,rom).heads)
        records.append(dict(kind=kind,raw_inputs={str(j):[hex(v) for v in k.cell_words(c)] for j,c in raw.items()},
            expected_complete_local_output=[hex(v) for v in expected],raw_projected_full_runs=runs,raw_projected_early_runs=early))
    return records

def compute():
    started=time.monotonic();rom,listing,labels,a=b.instance()
    syntax=syntax_and_normalization(rom,listing,labels,a)
    helper=helper_replay(rom,labels);costs=cost_replay();runs=selected_runs(rom)
    return dict(explicit_new_Q_U_schedule_widths_and_own_ROM=True,Q=k.Q,U=k.U,
        structural=syntax,helper=helper,cost=costs,selected_whole_own_ROM_executions=runs,
        selected_executions_are_measured_supplements=True,universal_or_iid_proof_inferred_from_samples=False,
        G17_or_old_frozen_rules_modified=False,seconds=time.monotonic()-started)

if __name__=='__main__':
    p=OUT/'small_probe01.json';assert not p.exists(),'never overwrite frozen probe'
    data=compute();p.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(dict(passed=True,helper_cases=len(data['helper']['cases']),full_bound=data['cost']['full_bound'],
        early_bound=data['structural']['early_bound'],actual_whole_pairs=len(data['selected_whole_own_ROM_executions']),seconds=data['seconds'])))
