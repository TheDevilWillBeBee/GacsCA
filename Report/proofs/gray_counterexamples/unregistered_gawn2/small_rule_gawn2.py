"""GAWN2: explicitly NEW fixed Q4096/U524288/radius8/Word100 instance.

Native GF/Age widths12/19, twelve-bit programme jump operands;
three gathers, native-only early pass,100Q late reset/birth,127Q stop.
Own immutable ROM is separately emitted. Original lambda24/c104 retained.
All word/immutable/radius/h1 departures from faithful Gray remain.
No damaged-lower or iid reliability theorem is asserted here.
"""
from dataclasses import dataclass,replace
from pathlib import Path
import sys,types
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[4]))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import gray_moving_word_v2 as predecessor

Q=4096;U=128*Q;WORD=100;MASK=(1<<WORD)-1;SMALL_MASK=(1<<20)-1
CODE_CAPACITY=Q;PC_BITS=12
LAMBDA=24;ERROR_SEPARATION=104;SLOTS=(0,-2,-1,1,2)
RUN,SEEK,HALT,ERROR=range(4)
META=('p','move','mode','pc','target','args')
HEAD_WORDS=len(META)+16;HEAD_BITS=HEAD_WORDS*WORD
FIELD_NAMES=META+tuple('r'+str(i) for i in range(16))+tuple('m'+str(i) for i in range(17))+(
    'out','info','scratch','program','courier_l','courier_r')
FRAME_WORDS=6+5*len(FIELD_NAMES);PRIMARY_START=Q//2-FRAME_WORDS//2;HEAD_ADDRESS=PRIMARY_START
FIELD={name:6+5*i for i,name in enumerate(FIELD_NAMES)}
NATIVE_NAMES=('addr','age','f1','f2','wf1','wf2')
OP_NAMES=('HLT','JMPR','MOVI','ALU','LDX','STX','READ5','READMASK','CODE','BNZ','JMP','ALUI','ALUX','BITCODE','FULLCOL')
OP={name:i for i,name in enumerate(OP_NAMES)}
ARGS=dict(HLT=(),JMPR=(4,),MOVI=(4,20),ALU=(4,5,4,4,4),
    LDX=(4,13,4,4,2),STX=(4,13,4,1),READ5=(4,1,4),READMASK=(4,4),
    CODE=(4,4),BNZ=(4,PC_BITS),JMP=(PC_BITS,),ALUI=(4,5,4,20),ALUX=(4,4,4,4,4),BITCODE=(4,4),FULLCOL=(4,4))
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
    token_bits:int=9
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
    start=beta.token_bits*address
    token=sum(beta.bits[start+i]<<i for i in range(beta.token_bits) if start+i<len(beta.bits))
    return beta.dictionary[token]


def beta_bit(beta,address):
    return beta.bits[address] if 0<=address<len(beta.bits) else 0


def fail(p):return replace(p,p=1,move=0,mode=ERROR)


def descriptor(kind,dst=0,lane=8,source=0,dest=0,side=0):
    return kind|(dst<<2)|(lane<<6)|(source<<11)|(dest<<13)|(side<<14)


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
                if r[index]>=Q or base+r[index]>=Q or r[lane]>16:return fail(p),None,None
                target=base+r[index];task=descriptor(0,dst,lane=r[lane],source=source)
            elif name=='STX':
                value,base,index,dest=args
                if r[index]>=Q or base+r[index]>=Q:return fail(p),None,None
                target=base+r[index];task=descriptor(1,value,dest=dest)
            elif name=='READ5':
                index,side,centre=args;target=r[index]
                if not 5<=centre<=11:return fail(p),None,None
                task=descriptor(2,lane=centre,side=side)
            else:
                dst,index=args;target=r[index];task=descriptor(3,dst,side=int(name=='FULLCOL'))
            if target>=Q:return fail(p),None,None
            return replace(p,pc=nextpc,mode=SEEK,target=target,args=task,
                move=1 if address<target else 2 if address>target else 0),None,None
        return replace(p,pc=nextpc,move=0,regs=tuple(r)),None,None
    if p.target>=Q:return fail(p),None,None
    if address!=p.target:return replace(p,move=1 if address<p.target else 2),None,None
    r=list(p.regs);kind=p.args&3;dst=(p.args>>2)&15;lane=(p.args>>6)&31
    source=(p.args>>11)&3;dest=(p.args>>13)&1;side=(p.args>>14)&1
    if kind==0:
        if lane>16:return fail(p),None,None
        r[dst]=((mem>>(lane*WORD))&MASK) if source==0 else out if source==1 else scratch if source==2 else program
    elif kind==1:
        return replace(p,move=0,mode=RUN),None if dest else r[dst],r[dst] if dest else None
    elif kind==2:
        if not 5<=lane<=11:return fail(p),None,None
        r[0]=sum((((mem>>((lane+(i+1)*(1 if side else -1))*WORD))&SMALL_MASK))<<(20*i) for i in range(5))
    else:r[dst]=sum(((mem>>((j+(0 if side else 3))*WORD))&1)<<j for j in range(17 if side else 11))
    return replace(p,move=0,mode=RUN,regs=tuple(r)),None,None


@dataclass(frozen=True)
class Cell:
    addr:int=0;age:int=0;f1:int=0;f2:int=0;wf1:int=0;wf2:int=0
    heads:tuple=(0,)*5;mem:tuple=(0,)*5;out:tuple=(0,)*5;info:tuple=(0,)*5
    scratch:tuple=(0,)*5;program:tuple=(0,)*5
    courier_l:tuple=(0,)*5;courier_r:tuple=(0,)*5


def incoming(packets):
    candidates=[]
    for index in (1,0,2):
        p=packets[index]
        if p.p and ((index==1 and p.move not in (1,2)) or
            (index==0 and p.move==1) or (index==2 and p.move==2)):candidates.append(p)
    if not candidates:return ZERO
    return fail(candidates[0]) if len(candidates)>1 else candidates[0]


def native_at(cells,centre=0):
    native={j:{n:getattr(cells[centre+j],n)&(Q-1 if n=='addr' else U-1 if n=='age' else 1)
        for n in NATIVE_NAMES} for j in range(-5,6)}
    return scalar_native(native)


def logical(cells,name,y):
    return vote([getattr(cells[y-t],name)[i] for i,t in enumerate(SLOTS)])


def _physical_primary(cells,y):
    a=native_at(cells,y);age=a['age'];addr=a['addr']
    if a['f1'] and addr!=cells[y].addr:return 0
    if age==0:return logical(cells,'out',y)&MASK
    if age==80*Q-1 and addr==3:return logical(cells,'courier_l',y)&MASK
    if age==80*Q-1 and addr==Q-3:return logical(cells,'courier_r',y)&MASK
    return logical(cells,'info',y)&MASK


def scalar_native(cells):
    """Independent h1 calculation; original Flag2 clause is explicitly changed."""
    base=predecessor.old.literal_maintenance.scalar(cells,Q=Q,U=U);c=cells[0]
    def maj(a,default):
        for v in a:
            if a.count(v)>=3:return v,True
        return default,False
    adjusted={j:(cells[j]['addr']-j)%Q for j in range(-5,6) if j}
    right,exists=maj([adjusted[j] for j in range(1,6)],c['addr'])
    inside={j:exists and 0<=right+j<Q for j in range(-5,6)}
    leftage,_=maj([cells[j]['age'] for j in range(-1,-6,-1)],c['age'])
    rightage,_=maj([cells[j]['age'] for j in range(1,6)],c['age'])
    source3=not exists and (leftage+1)%16==0
    source4=sum(inside[j] and cells[j]['wf2'] for j in range(-5,6))>=3
    left=[cells[j]['f2'] for j in range(-1,-6,-1)]
    leftinside=sum(inside[j] and cells[j]['f2'] for j in range(-1,-6,-1))
    f1=base['f1']
    on=leftinside>=4 or (f1 and sum(left)>=4) or source3 or source4
    erase=(not f1 and leftinside<=1) or (f1 and not any(left))
    f2=int(source3 or source4 or not erase) if c['f2'] else int(on)
    leftaddr,_=maj([adjusted[j] for j in range(-1,-6,-1)],c['addr'])
    voteright=exists and (not f1 or f2)
    return dict(addr=right if voteright else leftaddr,age=(rightage+1)%U if voteright else (leftage+1)%U,
                f1=f1,f2=f2,wf1=0,wf2=0)


BASE_FIELD_NAMES=FIELD_NAMES
BASE_ROM=ROM
BASE_CELL=Cell
GF_BITS=12;AGE_BITS=19
GF_MASK=Q-1;AGE_MASK=U-1
NATIVE_WIDTHS=(GF_BITS,AGE_BITS,1,1,1,1)
LATE_RESET=100*Q;LATE_BIRTH=LATE_RESET+1;ACTIVE_END=127*Q
STAGE_STARTS=(0,32*Q,64*Q,96*Q,100*Q)
GATHER_STARTS=STAGE_STARTS[:3]
EARLY_RESET=72*Q+3
EARLY_BIRTH=EARLY_RESET+1
FIELD_NAMES=BASE_FIELD_NAMES+('mail_l','mail_r')+tuple('h%d_%d'%(g,lane) for g in (1,2,3) for lane in range(17))
FIELD={name:6+5*i for i,name in enumerate(FIELD_NAMES)}
FRAME_WORDS=6+5*len(FIELD_NAMES)
PRIMARY_START=Q//2-FRAME_WORDS//2
HEAD_ADDRESS=PRIMARY_START
# Explicit diagnostic code capacity; physical Programme only has Q sites.
TOKEN_BITS=11;DICTIONARY_SIZE=2048;CODE_CAPACITY=Q

@dataclass(frozen=True)
class ROM(BASE_ROM):
    early_pc:int=0

@dataclass(frozen=True)
class Cell(BASE_CELL):
    mail_l:tuple=(0,)*5
    mail_r:tuple=(0,)*5
    history1:tuple=(0,)*5
    history2:tuple=(0,)*5
    history3:tuple=(0,)*5


def majority3(a,b,c):return (a&b)|(c&(a|b))

def capture(g,lane):
    d=lane-8;s=GATHER_STARTS[g-1]
    return s+1 if not d else s+2+abs(d)*Q


def _physical_transition(cells,beta):
    assert set(cells)==set(range(-8,9))
    a=native_at(cells);age=a['age'];addr=a['addr'];wipe=a['f1'] and addr!=cells[0].addr
    a['wf1']=a['wf2']=0
    if not wipe and 96*Q<=age<98*Q:
        if Q-5<=addr<Q:a['wf1']=computed_primary(cells,Q-3-addr)&1
        if addr<=4 and not a['f1']:a['wf2']=computed_primary(cells,3-addr)&1
    reset=age in STAGE_STARTS or age==EARLY_RESET
    birth=age in (EARLY_BIRTH,100*Q+1)
    active=EARLY_BIRTH<age<75*Q or 100*Q+1<age<=127*Q
    names=('heads','mem','out','info','scratch','program','courier_l','courier_r','mail_l','mail_r','history1','history2','history3')
    values={name:[] for name in names}
    for y in SLOTS:
        address=(addr+y)%Q
        histories=[logical(cells,'history'+str(g),y)&((1<<(17*WORD))-1) for g in (1,2,3)]
        mem=logical(cells,'mem',y)&((1<<(17*WORD))-1)
        if age in STAGE_STARTS:mem=0
        elif age in (EARLY_RESET,100*Q+1):mem=majority3(*histories)
        ml=logical(cells,'mail_l',y)&MASK;mr=logical(cells,'mail_r',y)&MASK
        if age in STAGE_STARTS:ml=mr=0
        elif age in tuple(s+1 for s in GATHER_STARTS):ml=mr=logical(cells,'info',y)&MASK
        elif any(s<=age<s+16*Q for s in GATHER_STARTS):
            ml=logical(cells,'mail_l',y+1)&MASK;mr=logical(cells,'mail_r',y-1)&MASK
        if a['f1']:ml=mr=0
        for g in (1,2,3):
            if age in GATHER_STARTS[:g]:histories[g-1]=0
            else:
                for lane in range(17):
                    if age==capture(g,lane):
                        source='info' if lane==8 else 'mail_r' if lane<8 else 'mail_l'
                        word=logical(cells,source,y)&MASK
                        histories[g-1]=(histories[g-1]&~(MASK<<(lane*WORD)))|(word<<(lane*WORD))
        out=logical(cells,'out',y)&MASK;scratch=logical(cells,'scratch',y)&MASK
        info=out if age==0 else logical(cells,'info',y)&MASK;pb=beta_bit(beta,address)
        left=logical(cells,'courier_l',y)&MASK;right=logical(cells,'courier_r',y)&MASK
        if age in STAGE_STARTS:left=right=0
        elif age==75*Q:
            left=(out&1) if address==PRIMARY_START+3 else 0
            right=(out&1) if address==PRIMARY_START+2 else 0
        elif 75*Q<age<80*Q:
            incoming_left=logical(cells,'courier_l',y+1)&MASK;incoming_right=logical(cells,'courier_r',y-1)&MASK
            left=((left|incoming_left) if address==3 else incoming_left) if 3<=address<=PRIMARY_START+3 else 0
            right=((right|incoming_right) if address==Q-3 else incoming_right) if PRIMARY_START+2<=address<=Q-3 else 0
        if age==80*Q-1:
            if address==3:info=logical(cells,'courier_l',y)&MASK
            if address==Q-3:info=logical(cells,'courier_r',y)&MASK
        if reset:head=ZERO;out=scratch=0
        elif birth:head=Packet(p=1,pc=beta.early_pc if age==EARLY_BIRTH else 0) if address==HEAD_ADDRESS else ZERO
        elif active:
            head=incoming([unpack(logical(cells,'heads',y+j)) for j in (-1,0,1)])
            head,ow,sw=step_packet(head,address,mem,out,scratch,logical(cells,'program',y)&MASK,beta)
            if ow is not None:out=ow
            if sw is not None:scratch=sw
        else:head=unpack(logical(cells,'heads',y))
        if wipe:head=ZERO;mem=out=info=scratch=pb=left=right=ml=mr=0;histories=[0]*3
        for name,value in zip(names,(pack(head),mem,out,info,scratch,pb,left,right,ml,mr,*histories)):values[name].append(value)
    return Cell(**a,**{name:tuple(v) for name,v in values.items()})


def cell_words(c):
    result=[getattr(c,n) for n in NATIVE_NAMES];packets=[unpack(v) for v in c.heads]
    for name in FIELD_NAMES:
        if name in META:result.extend(getattr(p,name) for p in packets)
        elif name.startswith('r') and name[1:].isdigit():result.extend(p.regs[int(name[1:])] for p in packets)
        elif name.startswith('m') and name[1:].isdigit():result.extend((v>>(int(name[1:])*WORD))&MASK for v in c.mem)
        elif name.startswith('h') and '_' in name:
            g,lane=map(int,name[1:].split('_'));result.extend((v>>(lane*WORD))&MASK for v in getattr(c,'history'+str(g)))
        else:result.extend(getattr(c,name))
    assert len(result)==FRAME_WORDS;return result


def cell_from_words(words):
    assert len(words)==FRAME_WORDS
    data=dict(zip(NATIVE_NAMES,words[:6]));packets=[dict(regs=[0]*16) for _ in range(5)]
    for field in ('mem','history1','history2','history3'):data[field]=[0]*5
    for i,name in enumerate(FIELD_NAMES):
        vals=words[6+5*i:11+5*i]
        if name in META:
            for q,v in enumerate(vals):packets[q][name]=v
        elif name.startswith('r') and name[1:].isdigit():
            for q,v in enumerate(vals):packets[q]['regs'][int(name[1:])]=v
        elif name.startswith('m') and name[1:].isdigit():
            for q,v in enumerate(vals):data['mem'][q]|=v<<(int(name[1:])*WORD)
        elif name.startswith('h') and '_' in name:
            g,lane=map(int,name[1:].split('_'))
            for q,v in enumerate(vals):data['history'+str(g)][q]|=v<<(lane*WORD)
        else:data[name]=tuple(vals)
    for field in ('mem','history1','history2','history3'):data[field]=tuple(data[field])
    data['heads']=tuple(pack(Packet(**{**p,'regs':tuple(p['regs'])})) for p in packets)
    return Cell(**data)


def input_tape(cells):
    words={j:cell_words(cells[j]) for j in range(-8,9)}
    return {PRIMARY_START+i:sum(words[j][i]<<((j+8)*WORD) for j in range(-8,9)) for i in range(FRAME_WORDS)}


def execute(beta,tape,limit=200000,record=False,early=False):
    p=Packet(p=1,pc=beta.early_pc if early else 0);address=HEAD_ADDRESS;out={};scratch={};trace=[]
    for tick in range(limit):
        address+=1 if p.move==1 else -1 if p.move==2 else 0
        assert 0<=address<Q
        oldp=p;p,ow,sw=step_packet(p,address,tape.get(address,0),out.get(address,0),scratch.get(address,0),beta_bit(beta,address),beta)
        if ow is not None:out[address]=ow
        if sw is not None:scratch[address]=sw
        if record:trace.append((address,oldp,p,ow,sw))
        if p.mode in (HALT,ERROR):return out,tick+1,p,trace
    return out,limit,p,trace


def project(cell):
    return replace(cell,**{name:getattr(cell,name)&((1<<width)-1)
        for name,width in zip(NATIVE_NAMES,NATIVE_WIDTHS)})

def project_neighborhood(cells):
    return {j:project(cell) for j,cell in cells.items()}

def computed_primary(cells,y):
    return _physical_primary(project_neighborhood(cells),y)

def local_transition(cells,beta):
    """Declared represented-D extension of the new physical alphabet rule."""
    return _physical_transition(project_neighborhood(cells),beta)
