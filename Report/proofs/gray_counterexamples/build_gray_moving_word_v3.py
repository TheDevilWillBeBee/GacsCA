"""Emit full proposed GMW3 beta, preserving frozen GMW2 emission sources.

Changes: clipped threshold3 Vote, seven travel candidates, native-Age parity
for alternating fast/one-site rows. Instructions still use fixed immutable
64K bit-PC ROM. No full-rule/native/head Apply intrinsic is introduced.
"""
import gray_moving_word_v3 as k
import build_gray_moving_word_v2 as previous


def programme():
    a=previous.programme();original=a.rows
    begin=next(i for i,r in enumerate(original) if r==('LABEL',('active_copy',)))
    end=next(i for i,r in enumerate(original) if r==('LABEL',('has_candidate',)))
    a.rows=[];e=a.emit;l=a.label;call=a.call
    VAR=k.PRIMARY_START-512
    def imm(r,v):e('MOVI',r,v)
    def read_at(dst,base,width,source=1):
        imm(11,base);imm(10,width);imm(6,5);e('LOADR',dst,11,10,6,source)
    def save(r,offset):imm(11,VAR+offset);imm(10,20);e('WRITER',r,11,10,1)
    def restore(r,offset):read_at(r,VAR+offset,20,2)
    def slot(dst):
        e('SHIFT',dst,14,2);e('ADDI',dst,'slots');e('CODE',dst,dst);e('ANDI',dst,15)
        e('MOV',6,dst);e('LTI',6,8);end=a.unique('f3_slot_nonnegative');e('BNZ',6,end);e('ADDI',dst,-16);l(end)
    def logical_offset():slot(12);e('ADDI',12,5)
    def service():read_at(12,k.NATIVE_COLUMNS['addr'][0],13);slot(0);e('ADD',12,12,0);e('ANDI',12,8191)
    def vote_field(name):
        b,w=k.COLUMN[name];imm(11,b);imm(10,w);e('MOV',9,11);call('vote')
    l('active_copy');imm(0,0);save(0,0);save(0,20)
    read_at(8,k.NATIVE_COLUMNS['age'][0],20);e('BIT',0,8,0);save(0,100)
    for delta in (0,-1,-2,-3,1,2,3):
        skip=a.unique('f3_candidate_skip');accept=a.unique('f3_candidate_accept')
        logical_offset();e('ADDI',12,delta);vote_field('p')
        present=a.unique('f3_candidate_present');e('BNZ',0,present);e('JMP',skip);l(present)
        vote_field('move')
        if not delta:
            e('MOV',1,0);e('LTI',1,1);e('BNZ',1,accept)
            imm(1,3);e('EQ',1,0,1);e('BNZ',1,accept);e('JMP',skip)
        else:
            imm(1,1 if delta<0 else 2);e('EQ',1,0,1)
            direction=a.unique('f3_candidate_direction');e('BNZ',1,direction);e('JMP',skip);l(direction)
            restore(0,100);fast=a.unique('f3_candidate_fast');e('BNZ',0,fast)
            e('JMP',accept if abs(delta)==1 else skip);l(fast)
            vote_field('mode');default=a.unique('f3_candidate_default_stride')
            io=a.unique('f3_candidate_io');e('BNZ',0,io);e('JMP',default);l(io)
            e('LTI',0,4);valid=a.unique('f3_candidate_io_mode');e('BNZ',0,valid);e('JMP',default);l(valid)
            vote_field('start');save(0,120);vote_field('index');restore(1,120);e('ADD',1,1,0)
            service();e('ADDI',12,delta);e('ANDI',12,8191)
            e('LT',0,12,1) if delta<0 else e('LT',0,1,12)
            positive=a.unique('f3_candidate_positive');e('BNZ',0,positive);e('JMP',default);l(positive)
            e('SUB',1,1,12) if delta<0 else e('SUB',1,12,1)
            e('MOV',0,1);e('LTI',0,3);small=a.unique('f3_candidate_small');e('BNZ',0,small)
            imm(1,3);l(small);imm(0,abs(delta));e('EQ',0,1,0);e('BNZ',0,accept);e('JMP',skip)
            l(default);e('JMP',accept if abs(delta)==1 else skip)
        l(accept);restore(1,0);notfirst=a.unique('f3_candidate_not_first');e('BNZ',1,notfirst)
        imm(0,delta+3);save(0,20);l(notfirst)
        e('ADDI',1,1);save(1,0);l(skip)
    restore(1,0);e('BNZ',1,'has_candidate');e('JMP','zero_head')
    replacement=a.rows
    a.rows=original[:begin]+replacement+original[end:]
    headend=next(i for i,r in enumerate(a.rows) if r==('LABEL',('bulk_copy',)))
    headbegin=next(i for i,r in enumerate(a.rows) if r==('LABEL',('has_candidate',)))
    changed=0
    for i in range(headbegin,headend):
        if a.rows[i]==('ADDI',(1,-1)):
            a.rows[i]=('ADDI',(1,-3));changed+=1
    assert changed==1
    # PAD missing source-copy lanes with0; preserve all five bank strides.
    matches=[i for i,r in enumerate(a.rows) if r==('LOADR',(0,11,10,6,0))]
    assert len(matches)==1
    i=matches[0];valid=a.unique('f3_vote_valid_lane');ready=a.unique('f3_vote_lane_ready')
    a.rows[i:i+1]=[('MOVI',(0,0)),('MOV',(4,6)),('LTI',(4,11)),('BNZ',(4,valid)),('JMP',(ready,)),
        ('LABEL',(valid,)),('LOADR',(0,11,10,6,0)),('LABEL',(ready,))]
    # Re-resolve fixed data dispatch labels after the actual changed emission.
    dispatch={0:'v_halt',1:'v_jmpr',2:'v_unary',3:'v_movi',4:'v_binary',5:'v_immediate',6:'v_binary',
       7:'v_binary',8:'v_immediate',9:'v_binary',10:'v_binary',11:'v_binary',12:'v_binary',13:'v_binary',
       14:'v_immediate',15:'v_majority',16:'v_window',17:'v_bitshift',18:'v_unary',19:'v_load5',20:'v_loadc',
       21:'v_loadcol',22:'v_write',23:'v_bnz',24:'v_jmp',25:'v_mismatch',26:'v_popcount',27:'v_immediate',
       28:'v_loadr',29:'v_writer',30:'v_bitshift',31:'v_code'}
    position=next(i for i,r in enumerate(a.rows) if r==('LABEL',('dispatch',)))+1
    _,_,labels,_=a.assemble()
    a.rows[position]=('DATA',(tuple((labels[dispatch[i]]>>b)&1 for i in range(32) for b in range(16)),))
    return a
