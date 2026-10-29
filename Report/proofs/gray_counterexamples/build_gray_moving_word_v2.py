"""Attempt an actual complete own word programme for the isolated GMW2 rule.

All operations below emit ordinary GMW2 instructions. No Apply/HeadStep/native
syscall is emitted. A too-long programme is an explicit construction failure.
This builder is not itself a fit or semantic certificate.
"""
import gray_moving_word_v2 as k
import gray_moving_word_kernel as old


class Assembler:
    def __init__(self):self.rows=[];self.serial=0
    def label(self,name):self.rows.append(('LABEL',(name,)))
    def emit(self,name,*args):self.rows.append((name,args))
    def unique(self,prefix):self.serial+=1;return prefix+'_'+str(self.serial)
    def call(self,name):
        ret=self.unique('return');self.emit('MOVI',15,ret);self.emit('JMP',name);self.label(ret)
    def assemble(self):
        labels={};cursor=0
        for name,args in self.rows:
            if name=='LABEL':labels[args[0]]=cursor
            elif name=='DATA':cursor+=len(args[0])
            else:cursor+=len(k.instruction_bits(name,*([0]*len(args))))
        listing=[];bits=[];errors=[]
        for name,args in self.rows:
            if name=='LABEL':continue
            address=len(bits)
            if name=='DATA':bits.extend(args[0]);continue
            values=tuple(labels[x] if isinstance(x,str) else x for x in args)
            for v,w in zip(values,k.ARGS[name]):
                if not -(1<<(w-1))<=v<1<<w:errors.append(dict(address=address,opcode=name,value=v,width=w))
            masked=tuple(v&((1<<w)-1) for v,w in zip(values,k.ARGS[name]))
            encoded=k.instruction_bits(name,*masked)
            bits.extend(encoded);listing.append(dict(address=address,opcode=name,operands=list(values),bits=len(encoded)))
        return bits,listing,labels,errors


def programme():
    a=Assembler();e=a.emit;l=a.label;call=a.call
    # Native words are the GMW0 explicit word recipe, with native input columns
    # relocated, the h1 predicate declared, and the final HALT replaced by JMP.
    _,native,oldlabels=old.native_word_programme();byold={v:n for n,v in oldlabels.items()}
    delta=k.PRIMARY_START-old.PRIMARY_START;replace_next=False
    for row in native:
        if row['address'] in byold:l('native_'+byold[row['address']])
        name=row['opcode'];args=row['operands'][:]
        if name=='XORI' and args==[5,2047]:replace_next=True;continue
        if replace_next and name=='LTI' and args==[5,1]:args[1]=2;replace_next=False
        if name=='LOAD5':args[0]+=delta
        elif name in ('LOADC','LOADCOL','WRITE'):args[1]+=delta
        elif name=='BNZ':args[1]='native_'+byold[args[1]]
        elif name=='JMP':args[0]='native_'+byold[args[0]]
        if name=='HLT':e('JMP','main')
        else:e(name,*args)
    assert not replace_next

    # R14: copy index. R12: logical-source offset+5 during Vote, service GF
    # during HeadStep. R13: bulk field index. R15: nonnested helper return.
    # Vote uses R0..8, preserves R9,R10,R12..15, advances R11.
    # Field access uses R6/R7/R10/R11 and preserves R1..5,R8/9,R12..15.
    def imm(r,v):e('MOVI',r,v)
    def read_at(dst,base,width,source=1):
        imm(11,base);imm(10,width);imm(6,5);e('LOADR',dst,11,10,6,source)
    def get(name,dst=0):
        b,w=k.COLUMN[name];imm(11,b);imm(10,w);call('getfield')
        if dst:e('MOV',dst,0)
    def put(name,value):
        if value!=0:e('MOV',0,value)
        b,w=k.COLUMN[name];imm(11,b);imm(10,w);call('putfield')
    def puti(name,value):imm(0,value);put(name,0)
    def reg_address(index):
        e('SHIFT',6,index,6);e('SHIFT',7,index,5);e('ADD',11,6,7)
        e('SHIFT',6,index,2);e('ADD',11,11,6);e('ADDI',11,k.COLUMN['r0'][0]);imm(10,20)
    def getreg(index,dst=0):
        reg_address(index);call('getfield')
        if dst:e('MOV',dst,0)
    def putreg(index,value):
        if value!=0:e('MOV',0,value)
        reg_address(index);call('putfield')
    def arg(lo,width,dst):
        if lo<20:
            e('SHIFT',dst,4,-lo)
            if lo+width>20:
                temp=7 if dst==6 else 6
                e('SHIFT',temp,5,20-lo);e('OR',dst,dst,temp)
        else:e('SHIFT',dst,5,-(lo-20))
        e('ANDI',dst,(1<<width)-1)
    def slot(dst):
        e('SHIFT',dst,14,2);e('ADDI',dst,'slots');e('CODE',dst,dst);e('ANDI',dst,15)
        e('MOV',6,dst);e('LTI',6,8);end=a.unique('slot_nonnegative');e('BNZ',6,end);e('ADDI',dst,-16);l(end)
    def logical_offset():slot(12);e('ADDI',12,5)
    def service():read_at(12,k.NATIVE_COLUMNS['addr'][0],13);slot(0);e('ADD',12,12,0);e('ANDI',12,8191)
    def vote_field(name,dst=0):
        b,w=k.COLUMN[name];imm(11,b);imm(10,w);e('MOV',9,11);call('vote')
        if dst:e('MOV',dst,0)
    def inc_q():e('ADDI',14,1);e('MOV',0,14);e('LTI',0,5);e('BNZ',0,'copy_loop');e('HLT')
    def generic(op,d,ai,bi,ci=3):imm(7,op);e('ALU',d,7,ai,bi,ci)
    def fail():e('JMP','head_error')
    def done():e('JMP','copy_done')

    l('main')
    # Wipe uses the represented upper physical holder's native outputs.
    read_at(1,k.NATIVE_COLUMNS['addr'][0],13)
    imm(11,k.NATIVE_COLUMNS['addr'][0]);imm(10,13);imm(6,5);e('LOADR',2,11,10,6,0)
    e('NE',1,1,2);read_at(2,k.NATIVE_COLUMNS['f1'][0],1);e('AND',1,1,2)
    e('BNZ',1,'wipe_all')
    imm(14,0)
    l('copy_loop');logical_offset()
    # Mem and baseline Out/Info/Scratch are voted old words. ProgramBit is
    # recomputed below. Explicit Age0 Info commit reads OLD voted Out.
    for name in ('mem','out','info','scratch'):
        vote_field(name);b,w=k.COLUMN[name];imm(11,b);call('putfield')
    read_at(8,k.NATIVE_COLUMNS['age'][0],20)
    imm(1,0);e('EQ',1,8,1);zeroage=a.unique('age0');afterzero=a.unique('after_age0')
    e('BNZ',1,zeroage);e('JMP',afterzero);l(zeroage)
    logical_offset();vote_field('out');put('info',0)
    l(afterzero)
    service();e('CODE',0,12);e('BIT',0,0,0);put('program',0)
    # Head reset/birth/rest/active selection. 8 is reloaded after Vote helpers.
    read_at(8,k.NATIVE_COLUMNS['age'][0],20)
    imm(1,0);e('EQ',1,8,1);e('BNZ',1,'reset_copy')
    imm(1,112*k.Q);e('EQ',1,8,1);e('BNZ',1,'reset_copy')
    imm(1,112*k.Q+1);e('EQ',1,8,1);e('BNZ',1,'birth_copy')
    e('MOV',1,8);e('LTI',1,112*k.Q+2);e('BNZ',1,'rest_copy')
    e('MOV',1,8);e('LTI',1,120*k.Q+1);e('BNZ',1,'active_copy');e('JMP','rest_copy')
    l('reset_copy');puti('out',0);puti('scratch',0);e('JMP','zero_head')
    l('birth_copy');e('JMP','zero_head_birth')
    l('rest_copy');logical_offset();e('JMP','bulk_copy')

    # Candidate count/selection are stored in scratch so Vote does not clobber
    # them. The overwrite scope is unrepresented physical scratch, not an input.
    VAR=k.PRIMARY_START-512
    def save(r,offset):imm(11,VAR+offset);imm(10,20);e('WRITER',r,11,10,1)
    def restore(r,offset):read_at(r,VAR+offset,20,2)
    l('active_copy');imm(0,0);save(0,0);save(0,20)
    for delta_source,required in ((0,None),(-1,1),(1,2)):
        logical_offset();e('ADDI',12,delta_source);vote_field('p')
        skip=a.unique('skip_candidate');e('BNZ',0,'candidate_p_'+str(delta_source));e('JMP',skip)
        l('candidate_p_'+str(delta_source));vote_field('move')
        if required is None:
            e('MOV',1,0);e('LTI',1,1);accept=a.unique('candidate_self');e('BNZ',1,accept)
            imm(1,3);e('EQ',1,0,1);e('BNZ',1,accept);e('JMP',skip);l(accept)
        else:
            imm(1,required);e('EQ',1,0,1);e('BNZ',1,'candidate_ok_'+str(delta_source));e('JMP',skip)
            l('candidate_ok_'+str(delta_source))
        restore(1,0);notfirst=a.unique('not_first');e('BNZ',1,notfirst)
        imm(0,delta_source+1);save(0,20);l(notfirst)
        e('ADDI',1,1);save(1,0);l(skip)
    restore(1,0);e('BNZ',1,'has_candidate');e('JMP','zero_head')
    l('has_candidate');restore(1,20);logical_offset();e('ADDI',1,-1);e('ADD',12,12,1)
    e('JMP','bulk_copy_active')

    # Shared field-copy loop. R8 stores continuation selector in scratch to
    # avoid the Vote's scratch registers. All28 head fields are emitted.
    l('bulk_copy');imm(0,0);save(0,40);e('JMP','bulk_start')
    l('bulk_copy_active');imm(0,1);save(0,40)
    l('bulk_start');imm(13,0)
    l('bulk_field')
    e('MOV',9,13);e('SHIFT',9,9,2);e('ADD',9,9,13);e('SHIFT',9,9,2)
    e('ADDI',9,'fields');e('CODE',9,9)
    e('SHIFT',10,9,-13);e('ANDI',10,31);e('ANDI',9,8191);e('MOV',11,9)
    call('vote');e('MOV',11,9);call('putfield')
    e('ADDI',13,1);e('MOV',0,13);e('LTI',0,28);e('BNZ',0,'bulk_field')
    restore(0,40);e('BNZ',0,'head_step');done()

    # Zero head is a field-word loop, followed by optional birth p=1.
    l('zero_head');imm(0,0);save(0,40);e('JMP','zero_start')
    l('zero_head_birth');imm(0,1);save(0,40)
    l('zero_start');imm(13,0)
    l('zero_field')
    e('MOV',9,13);e('SHIFT',9,9,2);e('ADD',9,9,13);e('SHIFT',9,9,2)
    e('ADDI',9,'fields');e('CODE',9,9)
    e('SHIFT',10,9,-13);e('ANDI',10,31);e('ANDI',9,8191);e('MOV',11,9);imm(0,0);call('putfield')
    e('ADDI',13,1);e('MOV',0,13);e('LTI',0,28);e('BNZ',0,'zero_field')
    restore(0,40);endzero=a.unique('not_birth');e('BNZ',0,'finish_birth');e('JMP',endzero)
    l('finish_birth');service();imm(0,k.HEAD_ADDRESS);e('EQ',0,12,0);put('p',0)
    l(endzero);done()

    l('head_step')
    imm(0,0);save(0,80)
    restore(0,0);e('LTI',0,2);e('BNZ',0,'one_candidate');fail()
    l('one_candidate');get('move');imm(1,3);e('EQ',1,0,1);e('BNZ',1,'head_error')
    get('mode',9);e('MOV',1,9);e('LTI',1,6);e('BNZ',1,'mode_valid');fail()
    l('mode_valid');imm(1,4);e('LT',1,9,1);e('BNZ',1,'mode_running');puti('move',0);done()
    l('mode_running');service();e('BNZ',9,'memory_step')

    # Instruction decode, ordinary PC advance, and indirect table dispatch.
    get('pc',3);save(3,60);e('CODE',4,3);e('MOV',6,3);e('ADDI',6,20);e('CODE',5,6)
    e('MOV',9,4);e('ANDI',9,31)
    e('SHIFT',6,9,2);e('ADD',6,6,9);e('ADDI',6,'lengths');e('CODE',6,6);e('ANDI',6,31)
    e('MOV',1,9);imm(2,31);e('EQ',1,1,2);normal_len=a.unique('normal_length');e('BNZ',1,'code_length');e('JMP',normal_len)
    l('code_length');e('BIT',1,4,5);e('BNZ',1,'alu_length');imm(6,14);e('JMP',normal_len)
    l('alu_length');imm(6,26);l(normal_len)
    e('ADD',3,3,6);e('MOV',1,3);e('LTI',1,k.CODE_CAPACITY+1);e('BNZ',1,'pc_valid');fail()
    l('pc_valid');e('ANDI',3,65535);put('pc',3);puti('move',0)
    e('SHIFT',6,9,4)
    e('ADDI',6,'dispatch');e('CODE',6,6);e('ANDI',6,65535);e('JMPR',6)

    l('v_halt');restore(3,60);put('pc',3);puti('mode',4);done()
    l('v_jmpr');arg(5,4,8);getreg(8);e('ANDI',0,65535);put('pc',0);done()
    l('v_jmp');arg(5,16,0);put('pc',0);done()
    l('v_bnz');arg(5,4,8);getreg(8);e('BNZ',0,'v_bnz_taken');done()
    l('v_bnz_taken');arg(9,16,0);put('pc',0);done()

    # Generic word arithmetic; the ALU has scalar arithmetic/bit/window ops,
    # never an instruction/head/native or physical transition Apply intrinsic.
    def alu_mapping():e('SHIFT',7,9,2);e('ADDI',7,'alu_map');e('CODE',7,7);e('ANDI',7,15)
    l('v_binary');arg(5,4,2);arg(9,4,8);getreg(8,1);arg(13,4,8);getreg(8,3)
    alu_mapping();e('ALU',0,7,1,3,3);putreg(2,0);done()
    l('v_immediate');arg(5,4,2);e('MOV',8,2);getreg(8,1);arg(9,20,3)
    alu_mapping();e('ALU',0,7,1,3,3);putreg(2,0);done()
    l('v_movi');arg(5,4,2);arg(9,20,0);putreg(2,0);done()
    l('v_unary');arg(5,4,2);arg(9,4,8);getreg(8,1)
    alu_mapping();e('ALU',0,7,1,1,1);putreg(2,0);done()
    l('v_bitshift');arg(5,4,2);arg(9,4,8);getreg(8,1)
    e('MOV',6,9);imm(7,17);e('EQ',6,6,7);isbit=a.unique('v_bit');afterarg=a.unique('after_bit_arg')
    e('BNZ',6,isbit);arg(13,6,3);e('JMP',afterarg);l(isbit);arg(13,5,3);l(afterarg)
    alu_mapping();e('ALU',0,7,1,3,3);putreg(2,0);done()
    l('v_code');e('BIT',6,4,5);e('BNZ',6,'v_scalar_alu')
    arg(6,4,2);arg(10,4,8);getreg(8);e('CODE',0,0);putreg(2,0);done()
    l('v_scalar_alu');arg(6,4,12);arg(10,4,8);getreg(8,9)
    arg(14,4,8);getreg(8,1);arg(18,4,8);getreg(8,2);arg(22,4,8);getreg(8,3)
    e('ALU',0,9,1,2,3);putreg(12,0);done()

    l('v_majority');arg(5,4,12);arg(9,4,13);arg(13,4,8);getreg(8,9)
    for i in (1,2,3,4,0):imm(8,i);getreg(8,i)
    e('MAJ',6,7,9);e('MOV',1,6);e('MOV',2,7);putreg(12,1);putreg(13,2);done()
    l('v_mismatch');arg(5,4,2);arg(21,1,3);arg(17,4,13)
    e('SHIFT',3,3,4);e('OR',2,2,3);e('MOV',5,2)
    arg(9,4,8);getreg(8,9);arg(13,4,8);getreg(8,12);getreg(13,13)
    for i in (1,2,3,4,0):imm(8,i);getreg(8,i)
    e('MOV',6,5);e('LTI',6,16);leftmi=a.unique('left_mi');aftermi=a.unique('after_mi')
    e('BNZ',6,leftmi);e('MI5',8,9,12,13,1);e('JMP',aftermi);l(leftmi);e('MI5',8,9,12,13,0);l(aftermi)
    e('MOV',0,8);e('ANDI',5,15);putreg(5,0);done()
    l('v_window');arg(5,4,2);arg(21,4,3);arg(25,4,6);e('SHIFT',6,6,4);e('OR',3,3,6)
    arg(9,4,8);getreg(8,1);arg(13,4,8);getreg(8,9);arg(17,4,8);getreg(8,8)
    e('MOV',6,8);e('LTI',6,1);e('NOT',6,6);e('SHIFT',6,6,8);e('OR',3,3,6)
    generic(12,0,1,9,3);e('BIT',6,0,19);e('BNZ',6,'head_error');putreg(2,0);done()
    l('v_popcount');arg(5,4,2);arg(13,4,3);arg(17,4,6);e('SHIFT',6,6,4);e('OR',3,3,6)
    arg(9,4,8);getreg(8,1);imm(9,4096);e('ADDI',3,256);generic(12,0,1,9,3)
    e('BIT',6,0,19);e('BNZ',6,'head_error');putreg(2,0);done()

    # IO descriptor decode. Fields1/2/3/8/9/12/13 are start,width,lane,dst,
    # kind,source,dest; virtual instruction words4/5 remain cached.
    l('v_load5');arg(5,13,1);arg(18,5,2);arg(23,1,3);imm(8,0);imm(9,0);imm(12,0);imm(13,0);e('JMP','io_descriptor')
    l('v_loadc');arg(5,4,8);arg(9,13,1);arg(22,5,2);imm(3,5);imm(9,1);imm(12,0);imm(13,0);e('JMP','io_descriptor')
    l('v_loadcol');arg(5,4,8);arg(9,13,1);imm(2,1);imm(3,5);imm(9,2);imm(12,0);imm(13,0);e('JMP','io_descriptor')
    l('v_write');arg(5,4,8);arg(9,13,1);arg(22,5,2);imm(3,5);imm(9,4);imm(12,0);imm(13,0);e('JMP','io_descriptor')
    l('v_loadr');arg(5,4,9);arg(9,4,8);getreg(8,1);arg(13,4,8);getreg(8,2)
    arg(17,4,8);getreg(8,3);e('MOV',8,9);arg(21,2,12);imm(13,0);imm(9,3);e('JMP','io_descriptor')
    l('v_writer');arg(5,4,9);arg(9,4,8);getreg(8,1);arg(13,4,8);getreg(8,2)
    e('MOV',8,9);arg(17,1,13);imm(3,5);imm(9,4);imm(12,0)
    l('io_descriptor')
    imm(0,1);save(0,80)
    e('BNZ',2,'io_width_nonzero');fail();l('io_width_nonzero')
    e('MOV',6,2);e('LTI',6,21);e('BNZ',6,'io_width_valid');fail();l('io_width_valid')
    e('ADD',6,1,2);e('LTI',6,k.Q+1);e('BNZ',6,'io_start_valid');fail();l('io_start_valid')
    e('MOV',6,3);e('LTI',6,11);e('BNZ',6,'io_lane_valid');fail();l('io_lane_valid')
    for name,r in (('start',1),('width',2),('lane',3),('kind',9),('dst',8),('source',12),('dest',13)):put(name,r)
    puti('index',0);puti('mode',1)
    e('MOV',6,9);e('LTI',6,4);nozero=a.unique('io_no_zero');e('BNZ',6,'io_clear_reg');e('JMP',nozero)
    l('io_clear_reg');e('BNZ',9,'io_clear_one');imm(13,0)
    l('io_clear_five');imm(0,0);putreg(13,0);e('ADDI',13,1);e('MOV',6,13);e('LTI',6,5);e('BNZ',6,'io_clear_five');e('JMP',nozero)
    l('io_clear_one');imm(0,0);putreg(8,0);l(nozero)
    service();e('LT',0,12,1);go_right=a.unique('io_right');e('BNZ',0,go_right)
    e('LT',0,1,12);e('SHIFT',0,0,1);put('move',0);done();l(go_right);puti('move',1);done()

    # SEEK/LOAD/WRITE, including partial words and all raw descriptor guards.
    l('memory_step');get('width',2);get('index',3);get('start',1);get('kind',9);get('lane',8);get('dst',13)
    e('BNZ',2,'mem_width_nonzero');fail();l('mem_width_nonzero')
    e('MOV',6,2);e('LTI',6,21);e('BNZ',6,'mem_width_valid');fail();l('mem_width_valid')
    e('LT',6,3,2);e('BNZ',6,'mem_index_valid');fail();l('mem_index_valid')
    e('ADD',6,1,2);e('LTI',6,k.Q+1);e('BNZ',6,'mem_start_valid');fail();l('mem_start_valid')
    e('MOV',6,9);e('LTI',6,5);e('BNZ',6,'mem_kind_valid');fail();l('mem_kind_valid')
    e('MOV',6,8);e('LTI',6,11);e('BNZ',6,'mem_lane_valid');fail();l('mem_lane_valid')
    e('ADD',1,1,3);e('EQ',6,12,1);e('BNZ',6,'memory_arrived')
    puti('mode',1);e('LT',0,12,1);to_right=a.unique('mem_right');e('BNZ',0,to_right)
    puti('move',2);done();l(to_right);puti('move',1);done()
    l('memory_arrived');imm(6,4);e('EQ',6,9,6);e('BNZ',6,'memory_write')
    get('mem',1)
    e('BNZ',9,'memory_notfive');e('MOV',6,8);e('LTI',6,2);e('BNZ',6,'load_five_valid');fail();l('load_five_valid')
    e('MOV',9,8);imm(13,0)
    l('load_five_loop');e('MOV',2,13);e('ADDI',2,1);e('BNZ',9,'load_five_right')
    imm(6,5);e('SUB',2,6,2);e('JMP','load_five_bit')
    l('load_five_right');e('ADDI',2,5)
    l('load_five_bit');generic(10,2,1,2,3);generic(11,2,2,3,3);getreg(13);e('OR',0,0,2);putreg(13,0)
    e('ADDI',13,1);e('MOV',6,13);e('LTI',6,5);e('BNZ',6,'load_five_loop');e('JMP','memory_advance')
    l('memory_notfive');imm(6,2);e('EQ',6,9,6);e('BNZ',6,'load_column')
    imm(6,1);e('EQ',6,9,6);e('BNZ',6,'load_centre')
    get('source',9);e('BNZ',9,'load_noninput');e('MOV',2,8);generic(10,2,1,2,3);e('JMP','load_bit')
    l('load_centre');imm(2,5);generic(10,2,1,2,3);e('JMP','load_bit')
    l('load_column');putreg(13,1);e('JMP','memory_advance')
    l('load_noninput');imm(6,1);e('EQ',6,9,6);e('BNZ',6,'load_oldout')
    imm(6,2);e('EQ',6,9,6);e('BNZ',6,'load_oldscratch')
    # Old ProgramBit is voted input, not the new hardwired result.
    logical_offset();vote_field('program');e('MOV',2,0);get('index',3);e('JMP','load_bit')
    l('load_oldout');get('out',2);e('JMP','load_bit')
    l('load_oldscratch');get('scratch',2)
    l('load_bit');generic(11,2,2,3,3);getreg(13);e('OR',0,0,2);putreg(13,0);e('JMP','memory_advance')
    l('memory_write');getreg(13,1);generic(10,2,1,3,3);get('dest');e('BNZ',0,'write_scratch')
    put('out',2);e('JMP','memory_advance');l('write_scratch');put('scratch',2)
    l('memory_advance');get('width',2);get('index',3);e('ADDI',3,1);e('EQ',6,2,3);e('BNZ',6,'memory_finish')
    put('index',3);get('kind');imm(6,4);e('EQ',6,0,6);e('BNZ',6,'memory_mode_write')
    puti('mode',2);puti('move',1);done();l('memory_mode_write');puti('mode',3);puti('move',1);done()
    l('memory_finish');puti('mode',0);puti('move',0);puti('index',0);puti('width',0);done()

    l('head_error');restore(0,80);e('BNZ',0,'io_error_restore_pc');e('JMP','error_fields')
    l('io_error_restore_pc');restore(3,60);put('pc',3)
    l('error_fields');puti('p',1);puti('move',0);puti('mode',5)
    l('copy_done');inc_q()

    l('wipe_all');imm(11,k.PRIMARY_START+37);imm(0,0);imm(10,20)
    l('wipe_words');e('WRITER',0,11,10,0);e('ADDI',11,20)
    e('MOV',1,11);e('LTI',1,k.PRIMARY_START+k.FRAME_BITS-20);e('BNZ',1,'wipe_words')
    imm(10,(k.FRAME_BITS-37)%20);e('WRITER',0,11,10,0);e('HLT')

    # Helpers are part of emitted beta, not native Python evaluator callbacks.
    l('getfield');e('MOV',6,14)
    l('get_offset');e('BNZ',6,'get_add');e('JMP','get_read')
    l('get_add');e('ADD',11,11,10);e('ADDI',6,-1);e('JMP','get_offset')
    l('get_read');imm(7,5);e('LOADR',0,11,10,7,1);e('JMPR',15)
    l('putfield');e('MOV',6,14)
    l('put_offset');e('BNZ',6,'put_add');e('JMP','put_write')
    l('put_add');e('ADD',11,11,10);e('ADDI',6,-1);e('JMP','put_offset')
    l('put_write');e('WRITER',0,11,10,0);e('JMPR',15)
    l('vote');imm(1,0);imm(2,0);imm(3,0);imm(5,0)
    l('vote_holder');e('SHIFT',8,5,2);e('ADDI',8,'slots');e('CODE',8,8);e('ANDI',8,15)
    e('MOV',6,8);e('LTI',6,8);vpos=a.unique('vote_positive');e('BNZ',6,vpos);e('ADDI',8,-16);l(vpos)
    e('SUB',6,12,8);e('LOADR',0,11,10,6,0)
    e('AND',4,2,0);e('OR',3,3,4);e('AND',4,1,0);e('OR',2,2,4);e('OR',1,1,0)
    e('ADD',11,11,10);e('ADDI',5,1);e('MOV',6,5);e('LTI',6,5);e('BNZ',6,'vote_holder')
    e('MOV',0,3);e('JMPR',15)

    # Immutable data are included in beta and accessed by CODE. They are not
    # mutable ProgramBit input and cannot be read through an arbitrary callback.
    l('slots');e('DATA',tuple((s>>b)&1 for s in k.SLOTS for b in range(4)))
    l('fields');e('DATA',tuple(((base|(width<<13))>>b)&1 for _,base,width in k.COLUMNS[:28] for b in range(20)))
    l('lengths');e('DATA',tuple((k.LENGTH[i]>>b)&1 for i in range(32) for b in range(5)))
    maps={2:0,4:1,5:1,6:2,7:3,8:3,9:4,10:5,11:6,12:7,13:8,14:8,17:10,18:9,27:5,30:11}
    l('alu_map');e('DATA',tuple((maps.get(i,0)>>b)&1 for i in range(32) for b in range(4)))
    # Dispatch data need actual labels, filled after the first assembly.
    dispatch={0:'v_halt',1:'v_jmpr',2:'v_unary',3:'v_movi',4:'v_binary',5:'v_immediate',6:'v_binary',
       7:'v_binary',8:'v_immediate',9:'v_binary',10:'v_binary',11:'v_binary',12:'v_binary',13:'v_binary',
       14:'v_immediate',15:'v_majority',16:'v_window',17:'v_bitshift',18:'v_unary',19:'v_load5',20:'v_loadc',
       21:'v_loadcol',22:'v_write',23:'v_bnz',24:'v_jmp',25:'v_mismatch',26:'v_popcount',27:'v_immediate',
       28:'v_loadr',29:'v_writer',30:'v_bitshift',31:'v_code'}
    l('dispatch');position=len(a.rows);e('DATA',(0,)*(32*16))
    _,_,labels,_=a.assemble()
    a.rows[position]=('DATA',(tuple((labels[dispatch[i]]>>b)&1 for i in range(32) for b in range(16)),))
    return a
