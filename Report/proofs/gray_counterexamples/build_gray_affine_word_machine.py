"""Emit ALL GMW4 fields with real affine IO, then check the stated capacity.

This is a specified full compiler attempt, not a fit/equivalence proof.
GMW2's source is cloned without modifying it. Every changed field helper
is an emitted generic finite IO instruction, with its own virtual opcode
case included. No physical or simulated whole transition intrinsic exists.
"""
from pathlib import Path
import hashlib,types
import build_gray_moving_word_v2 as previous
import gray_affine_word_machine as machine

NEW_GET='''    def get(name,dst=0):
        b,w=k.COLUMN[name];imm(7,5);e('AFFREAD',0,b,w,14,0,14,w,7,1)
        if dst:e('MOV',dst,0)
'''
NEW_PUT='''    def put(name,value):
        if value!=0:e('MOV',0,value)
        b,w=k.COLUMN[name];e('AFFWRITE',0,b,w,14,0,14,w,7,0)
'''
NEW_READ_AT='''    def read_at(dst,base,width,source=1):
        imm(7,5);e('AFFREAD',dst,base,0,14,0,14,width,7,source)
'''
NEW_GETREG='''    def getreg(index,dst=0):
        imm(7,5);e('AFFREAD',0,k.COLUMN['r0'][0],100,index,20,14,20,7,1)
        if dst:e('MOV',dst,0)
'''
NEW_PUTREG='''    def putreg(index,value):
        if value!=0:e('MOV',0,value)
        e('AFFWRITE',0,k.COLUMN['r0'][0],100,index,20,14,20,7,0)
'''

AFFINE_CASE='''    # Opcode27 is a declared new generic address-arithmetic/physical IO.
    # Each argument is decoded through finite CODE20; field reads travel.
    def affine_arg(lo,width,dst):
        restore(3,60);e('MOV',6,3);e('ADDI',6,lo);e('CODE',dst,6);e('ANDI',dst,(1<<width)-1)
    def affine_product(index_lo,scale_lo,target):
        affine_arg(index_lo,4,8);getreg(8,1);affine_arg(scale_lo,10,2)
        generic(13,0,1,2,3)
        e('MOV',6,0);e('LTI',6,k.Q+1);ok=a.unique('affine_product_valid')
        e('BNZ',6,ok);fail();l(ok);save(0,target)
    l('v_affine');imm(0,1);save(0,80)
    affine_product(33,23,100);affine_product(47,37,120)
    affine_arg(10,13,1);restore(2,100);e('ADD',1,1,2);restore(2,120);e('ADD',1,1,2);save(1,100)
    affine_arg(51,5,2);save(2,120);affine_arg(6,4,8);save(8,140)
    affine_arg(5,1,0);e('BNZ',0,'v_affine_write')
    affine_arg(56,4,8);getreg(8,3);save(3,160)
    affine_arg(60,2,12);save(12,180)
    restore(1,100);restore(2,120);restore(8,140);restore(3,160);restore(12,180)
    imm(9,3);imm(13,0);e('JMP','io_descriptor')
    l('v_affine_write');affine_arg(60,2,13);e('ANDI',13,1)
    restore(1,100);restore(2,120);restore(8,140)
    imm(9,4);imm(3,5);imm(12,0);e('JMP','io_descriptor')

'''


def generated_source(pc_bits=13):
    assert pc_bits in (13,16)
    source=Path(previous.__file__).read_text()
    source=source.replace('import gray_moving_word_v2 as k','# k is the explicitly supplied GMW4 finite engine')
    transformations={
        "    def read_at(dst,base,width,source=1):\n        imm(11,base);imm(10,width);imm(6,5);e('LOADR',dst,11,10,6,source)\n":NEW_READ_AT,
        "    def get(name,dst=0):\n        b,w=k.COLUMN[name];imm(11,b);imm(10,w);call('getfield')\n        if dst:e('MOV',dst,0)\n":NEW_GET,
        "    def put(name,value):\n        if value!=0:e('MOV',0,value)\n        b,w=k.COLUMN[name];imm(11,b);imm(10,w);call('putfield')\n":NEW_PUT,
        "    def getreg(index,dst=0):\n        reg_address(index);call('getfield')\n        if dst:e('MOV',dst,0)\n":NEW_GETREG,
        "    def putreg(index,value):\n        if value!=0:e('MOV',0,value)\n        reg_address(index);call('putfield')\n":NEW_PUTREG,
        "    # IO descriptor decode.":AFFINE_CASE+"    # IO descriptor decode.",
        "27:'v_immediate'":"27:'v_affine'",
        "l('alu_length');imm(6,26);l(normal_len)":
            "l('alu_length');imm(6,26);l(normal_len)\n    e('MOV',1,9);imm(2,27);e('EQ',1,1,2);affine_len_done=a.unique('after_affine_length')\n    e('BNZ',1,'affine_length');e('JMP',affine_len_done);l('affine_length');imm(6,62);l(affine_len_done)",
    }
    for old,new in transformations.items():
        assert source.count(old)==1,(old[:100],source.count(old));source=source.replace(old,new)
    # The unchanged five-bit lengths table cannot represent62; its ordinary
    # value is irrelevant because the new explicit Opcode27 case overrides it.
    source=source.replace('(k.LENGTH[i]>>b)&1','((k.LENGTH[i]&31)>>b)&1')
    source=source.replace("arg(5,16,0)","arg(5,%d,0)"%pc_bits)
    source=source.replace("arg(9,16,0)","arg(9,%d,0)"%pc_bits)
    source=source.replace('65535',str((1<<pc_bits)-1))
    source=source.replace("e('SHIFT',6,9,4)","e('MOV',6,9);e('MOV',7,9);e('SHIFT',6,6,3);e('SHIFT',7,7,2);e('ADD',6,6,7);e('ADD',6,6,9)" if pc_bits==13 else "e('SHIFT',6,9,4)")
    source=source.replace('32*16','32*'+str(pc_bits)).replace('range(16)),))','range('+str(pc_bits)+')),))')
    return source


def programme(capacity=8192,pc_bits=13):
    namespace={'k':machine.engine(capacity,pc_bits),'__name__':'_gray_affine_builder','__file__':__file__}
    source=generated_source(pc_bits)
    exec(compile(source,__file__+'::generated','exec'),namespace)
    answer=namespace['programme']()
    answer.generated_builder_sha256=hashlib.sha256(source.encode()).hexdigest()
    return answer
