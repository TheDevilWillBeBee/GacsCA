"""GMW7: NEW single-middle-gather token/word-PC architecture, explicitly not literal Gray.

Q8192/U128Q/lambda24/c104;100-bit Info/Out/Scratch/Program words and an
eleven-word Mem bank replace bit IO. The token beta has Q bits; a separately counted immutable dictionary
has 512 100-bit words. This is NOT Gray's ProgrammeBits protocol. A small scalar/vector ALU, real one-site operand travel, and a
six-word descriptor replace GMW2's32-opcode bit-IO controller. H1,
holder-computed GF service and zero Workspace outputs remain changes.
Single snapshot32Q, eleven lanes frozen by37Q; MADD5 is a generic new
ALU primitive. No fit, own-beta identity or hierarchy theorem is asserted here.
"""
from dataclasses import dataclass,replace
from pathlib import Path
import sys,types
import gray_moving_word_v2 as predecessor

Q=8192;U=128*Q;WORD=100;MASK=(1<<WORD)-1;SMALL_MASK=(1<<20)-1
CODE_CAPACITY=Q;PC_BITS=13
LAMBDA=24;ERROR_SEPARATION=104;SLOTS=(0,-2,-1,1,2)
RUN,SEEK,HALT,ERROR=range(4)
META=('p','move','mode','pc','target','args')
HEAD_WORDS=len(META)+16;HEAD_BITS=HEAD_WORDS*WORD
FIELD_NAMES=META+tuple('r'+str(i) for i in range(16))+tuple('m'+str(i) for i in range(11))+(
    'out','info','scratch','program')
FRAME_WORDS=6+5*len(FIELD_NAMES);PRIMARY_START=Q//2-FRAME_WORDS//2;HEAD_ADDRESS=PRIMARY_START
FIELD={name:6+5*i for i,name in enumerate(FIELD_NAMES)}
NATIVE_NAMES=('addr','age','f1','f2','wf1','wf2')
OP_NAMES=('HLT','JMPR','MOVI','ALU','LDX','STX','READ5','READMASK','CODE','BNZ','JMP','ALUI','ALUX','BITCODE')
OP={name:i for i,name in enumerate(OP_NAMES)}
ARGS=dict(HLT=(),JMPR=(4,),MOVI=(4,20),ALU=(4,5,4,4,4),
    LDX=(4,13,4,4,2),STX=(4,13,4,1),READ5=(4,1),READMASK=(4,4),
    CODE=(4,4),BNZ=(4,PC_BITS),JMP=(PC_BITS,),ALUI=(4,5,4,20),ALUX=(4,4,4,4,4),BITCODE=(4,4))
LENGTH={OP[name]:4+sum(widths) for name,widths in ARGS.items()}
ALU_NAMES=('MOV','ADD','SUB','AND','OR','XOR','EQ','NE','LT','NOT','BIT','SHIFT','WINDOW',
    'POPCOUNT','VMAJ','VEXISTS','VADDINDEX','VNE','VINSIDE','BITNOT','SIGNEXT','RSHIFT','MADD5')
ALU={name:i for i,name in enumerate(ALU_NAMES)}


@dataclass(frozen=True)
class Packet:
    p:int=0;move:int=0;mode:int=0;pc:int=0;target:int=0;args:int=0
    regs:tuple=(0,)*16


ZERO=Packet()


def pack(p):
    words=[getattr(p,name) for name in META]+list(p.regs)
    return sum((v&MASK)<<(i*WORD) for i,v in enumerate(words))


def unpack(v):
    words=[(v>>(i*WORD))&MASK for i in range(HEAD_WORDS)]
    return Packet(**dict(zip(META,words[:6])),regs=tuple(words[6:]))


def vote(values):return predecessor.old.vote(values)


def generic_alu(op,a,b,c=0):
    """Total finite arithmetic; no native/head/whole-rule evaluation."""
    if op==0:return a
    if op==1:return (a+b)&MASK
    if op==2:return (a-b)&MASK
    if op==3:return a&b
    if op==4:return a|b
    if op==5:return a^b
    if op==6:return int(a==b)
    if op==7:return int(a!=b)
    if op==8:return int(a<b)
    if op==9:return int(not a)
    if op==10:return (a>>b)&1 if b<WORD else 0
    if op==11:
        n=(b if b<(1<<19) else b-(1<<20)) if b<(1<<20) else b if b<(1<<(WORD-1)) else b-(1<<WORD)
        if abs(n)>=WORD:return 0
        return ((a<<n)&MASK) if n>=0 else a>>-n
    if op==12:
        lo=c&15;hi=(c>>4)&15;lo=lo if lo<8 else lo-16;hi=hi if hi<8 else hi-16
        if not -5<=lo<=hi<=5:return 1<<(WORD-1)
        return sum(((a>>(j+5))&1) and ((c>>8)&1) and 0<=b+j<Q for j in range(lo,hi+1))
    if op==13:return a.bit_count()
    if op in (14,15):
        values=[(a>>(20*i))&SMALL_MASK for i in range(5)]
        found=next((v for v in values if values.count(v)>=3),None)
        return int(found is not None) if op==15 else b if found is None else found
    if op==16:
        if not 1<=c<=20:return 1<<(WORD-1)
        step=b if b<(1<<(WORD-1)) else b-(1<<WORD)
        return sum((((a>>(20*i))+step*(i+1))&((1<<c)-1))<<(20*i) for i in range(5))
    if op==17:return sum(int(((a>>(20*i))&SMALL_MASK)!=b)<<i for i in range(5))
    if op==18:
        if b>1:return 0
        return sum(int(c!=0 and 0<=a+(i+1)*(1 if b else -1)<Q)<<i for i in range(5))
    if op==19:return (~a)&MASK
    if op==20:
        if b==0:return 0
        if b>WORD:return 1<<(WORD-1)
        value=a&((1<<b)-1)
        return (value-(1<<b) if value&(1<<(b-1)) else value)&MASK
    if op==21:return a>>b if b<WORD else 0
    if op==22:return (5*a+b)&MASK
    return 1<<(WORD-1)


def instruction_bits(name,*arguments):
    widths=ARGS[name];assert len(arguments)==len(widths);v=OP[name];shift=4
    for arg,width in zip(arguments,widths):
        assert -(1<<(width-1))<=arg<1<<width
        v|=(arg&((1<<width)-1))<<shift;shift+=width
    return [(v>>i)&1 for i in range(shift)]


def decode(v):
    op=v&15
    if op>=len(OP_NAMES):return None
    name=OP_NAMES[op];args=[];shift=4
    for width in ARGS[name]:args.append((v>>shift)&((1<<width)-1));shift+=width
    return name,tuple(args)


@dataclass(frozen=True)
class ROM:
    bits:tuple
    dictionary:tuple
    token_count:int
    used_dictionary:int
    def __len__(self):return len(self.bits)
    def __getitem__(self,index):return self.bits[index]


TOKEN_BITS=9;DICTIONARY_SIZE=512


def beta_word(beta,address,width=WORD):
    """One total finite instruction-ROM lookup, not a rule evaluator.

    Address is a WORD address.  Decode its nine-bit token from beta,
    then read one fixed 100-bit dictionary entry.  Raw out-of-range
    word addresses return zero; padding token zero is literal HLT.
    Width is ignored because this primitive returns one whole word.
    """
    if not 0<=address<CODE_CAPACITY:return 0
    start=TOKEN_BITS*address
    token=sum(beta.bits[start+i]<<i for i in range(TOKEN_BITS) if start+i<len(beta.bits))
    return beta.dictionary[token]


def beta_bit(beta,address):
    return beta.bits[address] if 0<=address<len(beta.bits) else 0


def fail(p):return replace(p,p=1,move=0,mode=ERROR)


def descriptor(kind,dst=0,lane=5,source=0,dest=0,side=0):
    return kind|(dst<<2)|(lane<<6)|(source<<10)|(dest<<12)|(side<<13)


def step_packet(p,address,mem,out,scratch,program,beta):
    """One real head update at its destination, local word IO only."""
    if not p.p:return ZERO,None,None
    if p.move>=3 or p.mode>=4:return fail(p),None,None
    if p.mode in (HALT,ERROR):return replace(p,move=0),None,None
    if p.mode==RUN:
        instruction=decode(beta_word(beta,p.pc))
        if instruction is None or p.pc>=CODE_CAPACITY:return fail(p),None,None
        name,args=instruction;nextpc=(p.pc+1)%CODE_CAPACITY;r=list(p.regs)
        if name=='HLT':return replace(p,mode=HALT,move=0),None,None
        if name in ('JMP','JMPR','BNZ'):
            target=args[0] if name=='JMP' else r[args[0]] if name=='JMPR' else args[1] if r[args[0]] else nextpc
            if target>=CODE_CAPACITY:return fail(p),None,None
            return replace(p,pc=target,move=0),None,None
        if name=='MOVI':r[args[0]]=args[1]
        elif name=='CODE':r[args[0]]=beta_word(beta,r[args[1]])
        elif name=='BITCODE':r[args[0]]=beta_bit(beta,r[args[1]])
        elif name in ('ALU','ALUX','ALUI'):
            if name=='ALUI':d,op,ai,value=args;r[d]=generic_alu(op,r[ai],value,0)
            else:
                d,op,ai,bi,ci=args;op=r[op] if name=='ALUX' else op
                r[d]=generic_alu(op,r[ai],r[bi],r[ci])
        else:
            if name=='LDX':
                dst,base,index,lane,source=args
                if r[index]>=Q or base+r[index]>=Q or r[lane]>10:return fail(p),None,None
                target=base+r[index];task=descriptor(0,dst,lane=r[lane],source=source)
            elif name=='STX':
                value,base,index,dest=args
                if r[index]>=Q or base+r[index]>=Q:return fail(p),None,None
                target=base+r[index];task=descriptor(1,value,dest=dest)
            elif name=='READ5':
                index,side=args;target=r[index];task=descriptor(2,side=side)
            else:
                dst,index=args;target=r[index];task=descriptor(3,dst)
            if target>=Q:return fail(p),None,None
            return replace(p,pc=nextpc,mode=SEEK,target=target,args=task,
                move=1 if address<target else 2 if address>target else 0),None,None
        return replace(p,pc=nextpc,move=0,regs=tuple(r)),None,None
    if p.target>=Q:return fail(p),None,None
    if address!=p.target:return replace(p,move=1 if address<p.target else 2),None,None
    r=list(p.regs);kind=p.args&3;dst=(p.args>>2)&15;lane=(p.args>>6)&15
    source=(p.args>>10)&3;dest=(p.args>>12)&1;side=(p.args>>13)&1
    if kind==0:
        if lane>10:return fail(p),None,None
        r[dst]=((mem>>(lane*WORD))&MASK) if source==0 else out if source==1 else scratch if source==2 else program
    elif kind==1:
        return replace(p,move=0,mode=RUN),None if dest else r[dst],r[dst] if dest else None
    elif kind==2:
        r[0]=sum((((mem>>((5+(i+1)*(1 if side else -1))*WORD))&SMALL_MASK))<<(20*i) for i in range(5))
    else:r[dst]=sum(((mem>>(j*WORD))&1)<<j for j in range(11))
    return replace(p,move=0,mode=RUN,regs=tuple(r)),None,None


@dataclass(frozen=True)
class Cell:
    addr:int=0;age:int=0;f1:int=0;f2:int=0;wf1:int=0;wf2:int=0
    heads:tuple=(0,)*5;mem:tuple=(0,)*5;out:tuple=(0,)*5;info:tuple=(0,)*5
    scratch:tuple=(0,)*5;program:tuple=(0,)*5


def incoming(packets):
    candidates=[]
    for index in (1,0,2):
        p=packets[index]
        if p.p and ((index==1 and p.move not in (1,2)) or
            (index==0 and p.move==1) or (index==2 and p.move==2)):candidates.append(p)
    if not candidates:return ZERO
    return fail(candidates[0]) if len(candidates)>1 else candidates[0]


def local_transition(cells,beta):
    assert len(beta)==CODE_CAPACITY and set(cells)==set(range(-5,6))
    native={j:{n:getattr(c,n)&(8191 if n=='addr' else SMALL_MASK if n=='age' else 1)
        for n in NATIVE_NAMES} for j,c in cells.items()}
    a=predecessor.scalar_native(native);age=a['age'];wipe=a['f1'] and a['addr']!=native[0]['addr']
    reset=age in (0,112*Q);birth=age==112*Q+1;active=112*Q+1<age<=120*Q
    values={n:[] for n in ('heads','mem','out','info','scratch','program')}
    def logical(n,y):return vote([getattr(cells[y-t],n)[i] for i,t in enumerate(SLOTS)])
    for y in SLOTS:
        address=(a['addr']+y)%Q;mem=logical('mem',y)&((1<<(11*WORD))-1)
        # Explicit single-middle-snapshot departure.  Old Info is stable
        # across the quiet gather interval; each lane moves exactly |d|Q.
        delta=age-32*Q
        if delta==0:
            word=logical('info',y)&MASK
            mem=sum(word<<(lane*WORD) for lane in range(11))
        elif 0<delta<=5*Q:
            words=[]
            for lane in range(11):
                d=lane-5;source=y+(1 if d>0 else -1) if d and delta<=abs(d)*Q else y
                words.append((logical('mem',source)>>(lane*WORD))&MASK)
            mem=sum(word<<(lane*WORD) for lane,word in enumerate(words))
        out=logical('out',y)&MASK;scratch=logical('scratch',y)&MASK
        info=out if age==0 else logical('info',y)&MASK;pb=beta_bit(beta,address)
        if reset:head=ZERO;out=scratch=0
        elif birth:head=Packet(p=1) if address==HEAD_ADDRESS else ZERO
        elif active:
            head=incoming([unpack(logical('heads',y+j)) for j in (-1,0,1)])
            head,ow,sw=step_packet(head,address,mem,out,scratch,logical('program',y)&MASK,beta)
            if ow is not None:out=ow
            if sw is not None:scratch=sw
        else:head=unpack(logical('heads',y))
        if wipe:head=ZERO;mem=out=info=scratch=pb=0
        for n,v in (('heads',pack(head)),('mem',mem),('out',out),('info',info),('scratch',scratch),('program',pb)):
            values[n].append(v)
    return Cell(**a,**{name:tuple(v) for name,v in values.items()})


def cell_words(c):
    result=[getattr(c,n) for n in NATIVE_NAMES];packets=[unpack(v) for v in c.heads]
    for name in FIELD_NAMES:
        if name in META:result.extend(getattr(p,name) for p in packets)
        elif name.startswith('r'):result.extend(p.regs[int(name[1:])] for p in packets)
        elif name.startswith('m'):result.extend((v>>(int(name[1:])*WORD))&MASK for v in c.mem)
        else:result.extend(getattr(c,name))
    assert len(result)==FRAME_WORDS
    return result


def cell_from_words(words):
    assert len(words)==FRAME_WORDS;data=dict(zip(NATIVE_NAMES,words[:6]));packets=[dict(regs=[0]*16) for _ in range(5)]
    data['mem']=[0]*5
    for i,name in enumerate(FIELD_NAMES):
        values=words[6+5*i:11+5*i]
        if name in META:
            for q,v in enumerate(values):packets[q][name]=v
        elif name.startswith('r'):
            for q,v in enumerate(values):packets[q]['regs'][int(name[1:])]=v
        elif name.startswith('m'):
            for q,v in enumerate(values):data['mem'][q]|=v<<(int(name[1:])*WORD)
        else:data[name]=tuple(values)
    data['mem']=tuple(data['mem']);data['heads']=tuple(pack(Packet(**{**p,'regs':tuple(p['regs'])})) for p in packets)
    return Cell(**data)


def input_tape(cells):
    words={j:cell_words(cells[j]) for j in range(-5,6)}
    return {PRIMARY_START+i:sum(words[j][i]<<((j+5)*WORD) for j in range(-5,6)) for i in range(FRAME_WORDS)}


def execute(beta,tape,limit=65535,record=False):
    p=Packet(p=1);address=HEAD_ADDRESS;out={};scratch={};trace=[]
    for tick in range(limit):
        address+=1 if p.move==1 else -1 if p.move==2 else 0
        assert 0<=address<Q
        oldp=p;p,ow,sw=step_packet(p,address,tape.get(address,0),out.get(address,0),scratch.get(address,0),beta_bit(beta,address),beta)
        if ow is not None:out[address]=ow
        if sw is not None:scratch[address]=sw
        if record:trace.append((address,oldp,p,ow,sw))
        if p.mode in (HALT,ERROR):return out,tick+1,p,trace
    return out,limit,p,trace

