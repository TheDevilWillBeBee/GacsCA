"""Complete emitted GMW6 token/word-PC transition; no whole-rule syscall.

Includes native, SF votes, head selection, actual virtual instructions,
word IO, resets and commit. A failed Q-code attempt is retained as such.
"""
import gray_token_word_v6 as k


class Assembler:
    def __init__(self,engine=k):self.k=engine;self.rows=[];self.serial=0
    def label(self,name):self.rows.append(('LABEL',(name,)))
    def emit(self,name,*args):self.rows.append((name,args))
    def unique(self,prefix):self.serial+=1;return prefix+'_'+str(self.serial)
    def assemble(self):
        k=self.k;labels={};pc=0
        for name,args in self.rows:
            if name=='LABEL':labels[args[0]]=pc
            else:pc+=len(args[0]) if name=='DATA' else 1
        words=[];listing=[];errors=[]
        for name,args in self.rows:
            if name=='LABEL':continue
            if name=='DATA':words.extend(args[0]);continue
            values=[labels[v] if isinstance(v,str) else v for v in args]
            for v,w in zip(values,k.ARGS[name]):
                if not -(1<<(w-1))<=v<1<<w:errors.append(dict(address=len(words),opcode=name,value=v,width=w))
            masked=[v&((1<<w)-1) for v,w in zip(values,k.ARGS[name])]
            raw=k.instruction_bits(name,*masked);word=sum(b<<i for i,b in enumerate(raw))
            listing.append(dict(address=len(words),opcode=name,operands=values,raw_bits=len(raw),word=hex(word)))
            words.append(word)
        dictionary=[0];index={0:0};tokens=[]
        for word in words:
            if word not in index:index[word]=len(dictionary);dictionary.append(word)
            tokens.append(index[word])
        if len(dictionary)>k.DICTIONARY_SIZE:errors.append(dict(dictionary_overflow=len(dictionary)))
        bits=[(token>>i)&1 for token in tokens for i in range(k.TOKEN_BITS)]
        dictionary+= [0]*(k.DICTIONARY_SIZE-len(dictionary))
        rom=k.ROM(tuple(bits+[0]*max(0,k.CODE_CAPACITY-len(bits))),tuple(dictionary),len(tokens),len(index))
        return rom,listing,labels,errors


def programme(native_only=False,engine=None):
    k=engine or globals()['k']
    a=Assembler(k);e=a.emit;l=a.label
    def imm(r,value):e('MOVI',r,value)
    def alu(d,op,x,y=0,z=0):e('ALU',d,k.ALU[op],x,y,z)
    def alui(d,op,x,value):e('ALUI',d,k.ALU[op],x,value)
    def mov(d,x):alu(d,'MOV',x)
    def call(name):
        ret=a.unique('ret');imm(15,ret);e('JMP',name);l(ret)
    def read_at(d,offset,source=0):imm(11,offset);imm(7,5);e('LDX',d,k.PRIMARY_START,11,7,source)
    def store_at(offset,value):imm(11,offset);e('STX',value,k.PRIMARY_START,11,0)
    def five(offset,side):imm(11,k.PRIMARY_START+offset);e('READ5',11,side)
    def mask(d,offset):imm(9,k.PRIMARY_START+offset);e('READMASK',d,9)
    def threshold(r,n):alui(r,'LT',r,n);alu(r,'NOT',r)
    def mismatch(r,vec,ref,side):
        alu(r,'VNE',vec,ref);imm(4,side);alu(4,'VINSIDE',6,4,7)
        alu(r,'AND',r,4);alu(r,'POPCOUNT',r);threshold(r,3)
    def win(d,m,lo,hi,temp=2):
        alui(temp,'SHIFT',7,8);alui(temp,'OR',temp,(lo&15)|((hi&15)<<4))
        alu(d,'WINDOW',m,6,temp)
    # Native h1 recipe. Each vector entry is an ordinary20-bit input word.
    read_at(12,0);read_at(13,1)
    five(0,1);imm(1,-1);imm(15,13);alu(0,'VADDINDEX',0,1,15)
    alu(6,'VMAJ',0,12);alu(7,'VEXISTS',0)
    five(1,1);alu(8,'VMAJ',0,13);alu(9,'VEXISTS',0)
    alu(14,'NOT',7);alu(5,'NOT',9);alu(14,'OR',14,5)
    five(0,0);imm(1,1);imm(15,13);alu(0,'VADDINDEX',0,1,15)
    alu(10,'VMAJ',0,12);mismatch(5,0,6,0);alu(14,'OR',14,5)
    five(1,0);alu(11,'VMAJ',0,13);mismatch(5,0,8,0);alu(14,'OR',14,5)
    for d,offset in enumerate((2,3,4,5)):mask(d,offset)
    win(4,0,1,5,9);mov(5,4);threshold(5,3);alu(14,'OR',14,5)
    alui(5,'BIT',0,5);threshold(4,2);alu(5,'AND',5,4);alu(14,'OR',14,5)
    win(4,2,-5,5,9);threshold(4,3);alu(14,'OR',14,4)
    alu(4,'NOT',7);alui(5,'ADD',11,1);alui(5,'AND',5,15);alui(5,'LT',5,1);alu(4,'AND',4,5)
    win(9,3,-5,5);threshold(9,3)
    win(15,1,-5,-1);threshold(15,4)
    alui(5,'AND',1,31);alu(5,'POPCOUNT',5);threshold(5,4);alu(5,'AND',5,14)
    alu(15,'OR',15,5);alu(15,'OR',15,4);alu(15,'OR',15,9)
    # Explicit h1: no complement; leftinside<=1.
    win(5,1,-5,-1);alui(5,'LT',5,2);alu(2,'NOT',14);alu(5,'AND',5,2)
    alui(3,'AND',1,31);alui(3,'LT',3,1);alu(3,'AND',3,14)
    alu(5,'OR',5,3);alu(5,'NOT',5);alu(5,'OR',5,4);alu(5,'OR',5,9)
    alui(3,'BIT',1,5);e('BNZ',3,'native_keep');e('JMP','native_afterkeep')
    l('native_keep');mov(15,5);l('native_afterkeep')
    alu(2,'NOT',14);alu(2,'OR',2,15);alu(2,'AND',2,7);e('BNZ',2,'native_right')
    mov(6,10);mov(8,11);l('native_right');alui(8,'ADD',8,1);alui(8,'AND',8,k.SMALL_MASK)
    for offset,value in ((0,6),(1,8),(2,14),(3,15)):store_at(offset,value)
    imm(0,0);store_at(4,0);store_at(5,0)
    if native_only:e('HLT');return a
    e('JMP','main')

    def slot(dst,index=14):
        imm(7,'slots');e('CODE',dst,7);alui(7,'SHIFT',index,2);alu(dst,'RSHIFT',dst,7)
        alui(dst,'SIGNEXT',dst,4)
    def logical():slot(12);alui(12,'ADD',12,5)
    def get(name,d=0):imm(7,5);e('LDX',d,k.PRIMARY_START+k.FIELD[name],14,7,1)
    def put(name,value=0):e('STX',value,k.PRIMARY_START+k.FIELD[name],14,0)
    def puti(name,value):imm(0,value);put(name)
    def indexed_address(index):
        alui(6,'SHIFT',index,2);alu(6,'ADD',6,index);alu(6,'ADD',6,14)
    def getreg(index,d=0):indexed_address(index);imm(7,5);e('LDX',d,k.PRIMARY_START+k.FIELD['r0'],6,7,1)
    def putreg(index,value=0):indexed_address(index);e('STX',value,k.PRIMARY_START+k.FIELD['r0'],6,0)
    def vote_field(name):imm(11,k.FIELD[name]);call('vote')
    def save(r,offset):imm(11,offset);e('STX',r,k.PRIMARY_START+128,11,1)
    def restore(r,offset):imm(11,offset);imm(7,5);e('LDX',r,k.PRIMARY_START+128,11,7,2)
    def arg(lo,width,d):alui(d,'SHIFT',4,-lo);alui(d,'AND',d,(1<<width)-1)
    def zero_head():
        imm(13,0);imm(11,6);alu(11,'ADD',11,14);imm(0,0)
        loop=a.unique('zero_head');l(loop);e('STX',0,k.PRIMARY_START,11,0)
        alui(11,'ADD',11,5);alui(13,'ADD',13,1);alui(6,'LT',13,k.HEAD_WORDS);e('BNZ',6,loop)
    def done():e('JMP','copy_done')
    def error():e('JMP','head_error')
    def check_less(r,n):alui(6,'LT',r,n);good=a.unique('valid');e('BNZ',6,good);error();l(good)

    l('main');read_at(1,0,1);read_at(2,0,0);alu(1,'NE',1,2);read_at(2,2,1);alu(1,'AND',1,2)
    e('BNZ',1,'wipe_all');imm(14,0)
    l('copy_loop');logical();imm(11,6);imm(13,0)
    l('baseline_loop');call('vote');alui(6,'SUB',11,5);alu(6,'ADD',6,14);e('STX',0,k.PRIMARY_START,6,0)
    alui(13,'ADD',13,1);alui(6,'LT',13,len(k.FIELD_NAMES));e('BNZ',6,'baseline_loop')
    read_at(8,1,1);alui(6,'EQ',8,0);after=a.unique('after_commit');e('BNZ',6,'commit_info');e('JMP',after)
    l('commit_info');get('out');put('info');l(after)
    read_at(12,0,1);slot(0);alu(12,'ADD',12,0);alui(12,'AND',12,8191)
    e('BITCODE',0,12);put('program')
    alui(6,'EQ',8,0);e('BNZ',6,'reset');alui(6,'EQ',8,112*k.Q);e('BNZ',6,'reset')
    alui(6,'EQ',8,112*k.Q+1);e('BNZ',6,'birth')
    alui(6,'LT',8,112*k.Q+2);e('BNZ',6,'copy_done');alui(6,'LT',8,120*k.Q+1);e('BNZ',6,'active');done()
    l('reset');zero_head();puti('out',0);puti('scratch',0);done()
    l('birth');save(12,0);zero_head();restore(12,0);alui(6,'EQ',12,k.HEAD_ADDRESS)
    end=a.unique('birth_end');e('BNZ',6,'birth_present');e('JMP',end);l('birth_present');puti('p',1);l(end);done()
    l('active');logical();save(12,0);imm(9,0);imm(10,0)
    for delta,direction in ((0,0),(-1,1),(1,2)):
        restore(12,0);alui(12,'SUB' if delta<0 else 'ADD',12,abs(delta));vote_field('p')
        absent=a.unique('candidate_absent');e('BNZ',0,absent+'_p');e('JMP',absent);l(absent+'_p')
        vote_field('move')
        if direction:alui(0,'EQ',0,direction)
        else:
            alui(1,'EQ',0,1);alui(2,'EQ',0,2);alu(0,'OR',1,2);alu(0,'NOT',0)
        accepted=a.unique('candidate_accept');e('BNZ',0,accepted);e('JMP',absent);l(accepted)
        existing=a.unique('candidate_existing');e('BNZ',9,existing);mov(10,12);l(existing);alui(9,'ADD',9,1);l(absent)
    save(9,1);e('BNZ',9,'has_head');zero_head();done()
    l('has_head');mov(12,10);imm(11,6);imm(13,0)
    l('incoming_loop');call('vote');alui(6,'SUB',11,5);alu(6,'ADD',6,14);e('STX',0,k.PRIMARY_START,6,0)
    alui(13,'ADD',13,1);alui(6,'LT',13,k.HEAD_WORDS);e('BNZ',6,'incoming_loop')
    get('pc');save(0,2);restore(9,1);alui(6,'LT',9,2);e('BNZ',6,'head_step');error()
    l('head_step');get('move');check_less(0,3);get('mode',9);check_less(9,4)
    alui(6,'LT',9,2);e('BNZ',6,'running');puti('move',0);done()
    l('running');e('BNZ',9,'io_step')
    get('pc',3);save(3,2);check_less(3,k.CODE_CAPACITY);e('CODE',4,3);alui(9,'AND',4,15);check_less(9,len(k.OP_NAMES))
    alui(6,'ADD',9,'dispatch');e('CODE',6,6);alui(6,'AND',6,k.CODE_CAPACITY-1);save(6,3)
    alui(0,'ADD',3,1);alui(0,'AND',0,k.CODE_CAPACITY-1);put('pc');restore(6,3);e('JMPR',6)
    l('v_halt');restore(0,2);put('pc');puti('mode',k.HALT);puti('move',0);done()
    l('v_jmpr');arg(4,4,8);getreg(8);check_less(0,k.CODE_CAPACITY);put('pc');puti('move',0);done()
    l('v_jump');arg(4,k.PC_BITS,0);put('pc');puti('move',0);done()
    l('v_branch');arg(4,4,8);getreg(8);no=a.unique('no_branch');e('BNZ',0,'take_branch');e('JMP',no)
    l('take_branch');arg(8,k.PC_BITS,0);put('pc');l(no);puti('move',0);done()
    l('v_imm');arg(4,4,8);arg(8,20,0);putreg(8);puti('move',0);done()
    for opcode,label in (('CODE','v_code'),('BITCODE','v_bitcode')):
        l(label);arg(8,4,8);getreg(8,1);e(opcode,0,1);arg(4,4,8);putreg(8);puti('move',0);done()
    for name,label in (('ALU','v_alu'),('ALUX','v_alux'),('ALUI','v_alui')):
        l(label)
        if name=='ALUI':
            arg(13,4,8);getreg(8,1);arg(17,20,2);imm(3,0);arg(8,5,9)
        else:
            shift=1 if name=='ALU' else 0
            arg(12+shift,4,8);getreg(8,1);arg(16+shift,4,8);getreg(8,2);arg(20+shift,4,8);getreg(8,3)
            arg(8,5 if name=='ALU' else 4,9)
            if name=='ALUX':mov(8,9);getreg(8,9)
        e('ALUX',0,9,1,2,3);arg(4,4,8);putreg(8);puti('move',0);done()
    l('v_ldx');arg(21,4,8);getreg(8,1);check_less(1,k.Q);arg(8,13,2);alu(1,'ADD',1,2);check_less(1,k.Q);save(1,4)
    arg(25,4,8);getreg(8,2);check_less(2,11);arg(29,2,3);alui(3,'SHIFT',3,10)
    alui(2,'SHIFT',2,6);alu(3,'OR',3,2);arg(4,4,2);alui(2,'SHIFT',2,2);alu(3,'OR',3,2)
    e('JMP','new_io')
    l('v_stx');arg(21,4,8);getreg(8,1);check_less(1,k.Q);arg(8,13,2);alu(1,'ADD',1,2);check_less(1,k.Q);save(1,4)
    arg(25,1,3);alui(3,'SHIFT',3,12);arg(4,4,2);alui(2,'SHIFT',2,2);alu(3,'OR',3,2);alui(3,'OR',3,1|(5<<6))
    e('JMP','new_io')
    l('v_five');arg(4,4,8);getreg(8,1);check_less(1,k.Q);save(1,4)
    arg(8,1,3);alui(3,'SHIFT',3,13);alui(3,'OR',3,2|(5<<6));e('JMP','new_io')
    l('v_mask');arg(8,4,8);getreg(8,1);check_less(1,k.Q);save(1,4)
    arg(4,4,3);alui(3,'SHIFT',3,2);alui(3,'OR',3,3|(5<<6))
    l('new_io');put('args',3);restore(1,4);put('target',1);puti('mode',k.SEEK)
    read_at(2,0,1);slot(0);alu(2,'ADD',2,0);alui(2,'AND',2,8191)
    alu(6,'LT',2,1);e('BNZ',6,'move_right');alu(6,'LT',1,2);e('BNZ',6,'move_left');puti('move',0);done()
    l('move_right');puti('move',1);done();l('move_left');puti('move',2);done()
    l('io_step');get('target',1);check_less(1,k.Q);read_at(2,0,1);slot(0);alu(2,'ADD',2,0);alui(2,'AND',2,8191)
    alu(6,'EQ',1,2);e('BNZ',6,'perform_io');alu(6,'LT',2,1);e('BNZ',6,'move_right');e('JMP','move_left')
    l('perform_io');get('args',4);alui(8,'SHIFT',4,-2);alui(8,'AND',8,15);save(8,5)
    alui(9,'AND',4,3);alui(6,'EQ',9,1);e('BNZ',6,'io_write');alui(6,'EQ',9,2);e('BNZ',6,'io_five')
    alui(6,'EQ',9,3);e('BNZ',6,'io_mask')
    alui(2,'SHIFT',4,-6);alui(2,'AND',2,15);check_less(2,11)
    alui(9,'SHIFT',4,-10);alui(9,'AND',9,3);e('BNZ',9,'io_nonmem')
    alui(6,'SHIFT',2,2);alu(6,'ADD',6,2);alu(6,'ADD',6,14);imm(7,5)
    e('LDX',0,k.PRIMARY_START+k.FIELD['m0'],6,7,1);e('JMP','io_read_result')
    l('io_nonmem');alui(6,'EQ',9,1);e('BNZ',6,'io_out');alui(6,'EQ',9,2);e('BNZ',6,'io_scratch')
    logical();vote_field('program');e('JMP','io_read_result')
    l('io_out');get('out');e('JMP','io_read_result');l('io_scratch');get('scratch')
    l('io_read_result');restore(8,5);putreg(8);e('JMP','io_done')
    l('io_write');getreg(8);alui(6,'SHIFT',4,-12);alui(6,'AND',6,1);e('BNZ',6,'io_write_scratch')
    put('out');e('JMP','io_done');l('io_write_scratch');put('scratch');e('JMP','io_done')
    l('io_five');alui(9,'SHIFT',4,-13);alui(9,'AND',9,1);save(9,6);imm(13,0);imm(0,0);save(0,7)
    l('io_five_loop');restore(9,6);alui(2,'ADD',13,1);e('BNZ',9,'five_right')
    imm(6,5);alu(2,'SUB',6,2);e('JMP','five_lane');l('five_right');alui(2,'ADD',2,5);l('five_lane')
    alui(6,'SHIFT',2,2);alu(6,'ADD',6,2);alu(6,'ADD',6,14);imm(7,5)
    e('LDX',0,k.PRIMARY_START+k.FIELD['m0'],6,7,1);alui(0,'AND',0,k.SMALL_MASK)
    alui(2,'SHIFT',13,4);alui(3,'SHIFT',13,2);alu(2,'ADD',2,3);alu(0,'SHIFT',0,2)
    restore(1,7);alu(0,'OR',0,1);save(0,7);alui(13,'ADD',13,1);alui(6,'LT',13,5);e('BNZ',6,'io_five_loop')
    imm(8,0);putreg(8);e('JMP','io_done')
    l('io_mask');imm(13,0);imm(0,0);save(0,7)
    l('io_mask_loop');alui(6,'SHIFT',13,2);alu(6,'ADD',6,13);alu(6,'ADD',6,14);imm(7,5)
    e('LDX',0,k.PRIMARY_START+k.FIELD['m0'],6,7,1);alui(0,'AND',0,1);alu(0,'SHIFT',0,13)
    restore(1,7);alu(0,'OR',0,1);save(0,7);alui(13,'ADD',13,1);alui(6,'LT',13,11);e('BNZ',6,'io_mask_loop')
    restore(8,5);putreg(8)
    l('io_done');puti('move',0);puti('mode',k.RUN);done()
    l('head_error');restore(0,2);put('pc');puti('p',1);puti('move',0);puti('mode',k.ERROR);done()
    l('copy_done');alui(14,'ADD',14,1);alui(6,'LT',14,5);e('BNZ',6,'copy_loop');e('HLT')
    l('wipe_all');imm(11,6);imm(0,0);l('wipe_loop');e('STX',0,k.PRIMARY_START,11,0)
    alui(11,'ADD',11,1);alui(6,'LT',11,k.FRAME_WORDS);e('BNZ',6,'wipe_loop');e('HLT')
    # Word-at-a-time three-of-five helper, with real five operand reads.
    l('vote');imm(3,0);imm(4,0);imm(5,0);imm(8,0)
    l('vote_loop');slot(6,8);alu(6,'SUB',12,6);e('LDX',0,k.PRIMARY_START,11,6,0)
    alu(1,'AND',4,0);alu(5,'OR',5,1);alu(1,'AND',3,0);alu(4,'OR',4,1);alu(3,'OR',3,0)
    alui(11,'ADD',11,1);alui(8,'ADD',8,1);alui(6,'LT',8,5);e('BNZ',6,'vote_loop')
    mov(0,5);e('JMPR',15)
    l('slots');e('DATA',(sum((v&15)<<(4*i) for i,v in enumerate(k.SLOTS)),))
    l('dispatch');targets=('v_halt','v_jmpr','v_imm','v_alu','v_ldx','v_stx','v_five','v_mask',
        'v_code','v_branch','v_jump','v_alui','v_alux','v_bitcode')
    original=a.assemble
    def assemble():
        a.rows.append(('DATA',(tuple(0 for _ in targets),)))
        try:_,_,labels,_=original()
        finally:a.rows.pop()
        data=tuple(labels[target] for target in targets)
        a.rows.append(('DATA',(data,)))
        try:return original()
        finally:a.rows.pop()
    a.assemble=assemble
    return a
