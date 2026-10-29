"""GMW4: explicit affine-IO evaluator variants, not a Gray refinement.

The Q-code/13-bit-PC target and a separate64K/16-bit-PC diagnostic variant
are total physical machines. Both retain Q8192/U128Q/lambda24/c104. They
inherit h1, holder-computed service GF, immutable instruction/CODE fetch,
mutable ProgramBit copies and zero Workspace outputs from GMW2. Removing
XORI, adding affine physical IO and saturating scalar multiplication are
explicit ISA changes. No whole-rule or virtual-HeadStep syscall is used.
"""
from pathlib import Path
import hashlib,sys,types
import gray_moving_word_v2 as base

AFFINE_WIDTHS=(4,13,10,4,10,4,5,4,2)
EXTENSION='''
_base_instruction_bits=instruction_bits
_base_decode=decode
_base_start_io=start_io
_base_generic_alu=generic_alu
OP_NAMES=tuple('AFFREAD' if i==27 else n for i,n in enumerate(OP_NAMES))
OP=dict(OP);OP.pop('XORI');OP.update(AFFREAD=27,AFFWRITE=27)
ARGS=dict(ARGS);ARGS.pop('XORI');ARGS['AFFREAD']=ARGS['AFFWRITE']=AFFINE_WIDTHS
LENGTH=dict(LENGTH);LENGTH[27]=62
ALU_NAMES=ALU_NAMES+('SATMUL',)

def instruction_bits(name,*args):
    if name not in ('AFFREAD','AFFWRITE'):return _base_instruction_bits(name,*args)
    assert len(args)==len(AFFINE_WIDTHS)
    value=27|(32 if name=='AFFWRITE' else 0);shift=6
    for argument,width in zip(args,AFFINE_WIDTHS):
        assert -(1<<(width-1))<=argument<1<<width
        value|=(argument&((1<<width)-1))<<shift;shift+=width
    assert shift==62
    return [(value>>i)&1 for i in range(62)]

def decode(value):
    if (value&31)!=27:return _base_decode(value)
    shift=6;arguments=[]
    for width in AFFINE_WIDTHS:
        arguments.append((value>>shift)&((1<<width)-1));shift+=width
    return ('AFFWRITE' if (value>>5)&1 else 'AFFREAD'),tuple(arguments)

def instruction_length(value):
    return 62 if (value&31)==27 else 26 if (value&63)==63 else LENGTH[value&31]

def generic_alu(op,a,b,c):
    if op==13:return min(MASK,a*b)
    return _base_generic_alu(op,a,b,c)

def start_io(packet,address,nextpc,name,arguments):
    if name not in ('AFFREAD','AFFWRITE'):
        return _base_start_io(packet,address,nextpc,name,arguments)
    dst,base,scale1,index1,scale2,index2,width,lane_index,channel=arguments
    registers=list(packet.regs)
    pointer=base+scale1*registers[index1]+scale2*registers[index2]
    lane=5 if name=='AFFWRITE' else registers[lane_index]
    if not 1<=width<=20 or pointer+width>Q or not 0<=lane<=10:return fail(packet)
    if name=='AFFREAD':registers[dst]=0
    return replace(packet,pc=nextpc,mode=SEEK,start=pointer,width=width,index=0,
        kind=3 if name=='AFFREAD' else 4,dst=dst,lane=lane,
        source=channel if name=='AFFREAD' else 0,dest=(channel&1) if name=='AFFWRITE' else 0,
        regs=tuple(registers),move=1 if address<pointer else 2 if address>pointer else 0)
'''


def generated_source(capacity=8192,pc_bits=13):
    assert (capacity,pc_bits) in ((8192,13),(65536,16))
    source=Path(base.__file__).read_text()
    changes={
        'CODE_CAPACITY=65536':'CODE_CAPACITY='+str(capacity),
        "('pc',16)":"('pc',%d)"%pc_bits,
        "ARGS['BNZ']=(4,16);ARGS['JMP']=(16,)":"ARGS['BNZ']=(4,%d);ARGS['JMP']=(%d,)"%(pc_bits,pc_bits),
        'v=beta_word(beta,p.pc,29)':'v=beta_word(beta,p.pc,62)',
        "('LOAD5','LOADC','LOADCOL','WRITE','LOADR','WRITER')":
            "('LOAD5','LOADC','LOADCOL','WRITE','LOADR','WRITER','AFFREAD','AFFWRITE')",
    }
    for old,new in changes.items():
        assert source.count(old)==1,(old,source.count(old));source=source.replace(old,new)
    source=source.replace('65535','(CODE_CAPACITY-1)')
    return source+'\nAFFINE_WIDTHS='+repr(AFFINE_WIDTHS)+'\n'+EXTENSION


_ENGINES={}
def engine(capacity=8192,pc_bits=13):
    key=(capacity,pc_bits)
    if key not in _ENGINES:
        name='_gray_affine_'+str(capacity);module=types.ModuleType(name);module.__file__=__file__
        sys.modules[name]=module
        exec(compile(generated_source(*key),__file__+'::'+name,'exec'),module.__dict__)
        module.generated_source_sha256=hashlib.sha256(generated_source(*key).encode()).hexdigest()
        _ENGINES[key]=module
    return _ENGINES[key]
