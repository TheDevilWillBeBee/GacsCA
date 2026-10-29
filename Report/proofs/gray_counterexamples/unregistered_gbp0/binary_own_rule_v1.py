"""GBP1: explicitly changed register-expanded total binary radius-eight candidate, not a Gray refinement.

Immutable Q-bit code, eleven Word20 registers, generic 407-bit accumulator,
three seventeen-lane gathers, corrected h1 native erasure.  There is no own
programme certificate yet. Every lookup is a data lookup, never a rule call.
"""
from dataclasses import dataclass, replace
from pathlib import Path
from itertools import combinations
import sys

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE.parents[2]))
from gacsca import maintenance

Q=8192; U=128*Q; LAMBDA=24; ERROR_SEPARATION=104
WORD=20; MASK=(1<<WORD)-1; WORK_BITS=407; REGISTERS=11
SLOTS=(0,-2,-1,1,2); LANES=tuple(range(-8,9))
NATIVE=(('addr',13),('age',20),('f1',1),('f2',1),('wf1',1),('wf2',1))
META=(('p',1),('move',2),('mode',2),('pc',13),('target',13),
      ('index',7),('buf',5),('lane',5),('ret',13),('dst',4),
      ('width',6),('kind',3),('start',13),('nc',37))
PACKET_BITS=sum(w for _,w in META)+REGISTERS*WORD
HEAD_BITS=PACKET_BITS+WORK_BITS
FIELDS=(('info',1),('mailL',1),('mailR',1),('history1',17),
        ('history2',17),('history3',17),('next',1),('courierL',1),
        ('courierR',1),('head',HEAD_BITS))
FRAME_BITS=37+5*sum(w for _,w in FIELDS)
PRIMARY_START=Q//2-FRAME_BITS//2
COLLECTOR=PRIMARY_START+36
COLLECT=72*Q+3; EVALUATE=COLLECT+37; DELIVERY=80*Q-1
RESET=frozenset((0,32*Q,64*Q,96*Q,112*Q))
RUN,IO,HALT,ERROR=range(4)
LDC,LDV,LDB,STORE=range(4)

OP_NAMES=('HLT','MOV','LIT','ALU','BNZ','JMP','WGET','WSET',
          'NATIVE','CGET','LDV','LDC','LDB','ST','CODE','JREG')
OP={name:i for i,name in enumerate(OP_NAMES)}
ARGS={'HLT':(), 'MOV':(4,4), 'LIT':(4,20), 'ALU':(4,4,4,4),
      'BNZ':(4,13), 'JMP':(13,), 'WGET':(4,4), 'WSET':(4,4),
      'NATIVE':(), 'CGET':(4,4,5), 'LDV':(4,4,4,5),
      'LDC':(4,4,4,5), 'LDB':(4,4), 'ST':(4,4,5,3), 'CODE':(4,4), 'JREG':(4,)}
LENGTH={OP[name]:4+sum(ws) for name,ws in ARGS.items()}
ALU_NAMES=('add','sub','and','or','xor','eq','lt','shl','shr',
           'div','mod','not','invert','mul','min','max')
ALU={name:i for i,name in enumerate(ALU_NAMES)}

def majority(values):
    assert len(values)==5
    z=0
    for a,b,c in combinations(values,3):z|=a&b&c
    return z

def majority3(a,b,c):return (a&b)|(a&c)|(b&c)

def alu(fn,a,b):
    a&=MASK;b&=MASK
    operations=(lambda:a+b,lambda:a-b,lambda:a&b,lambda:a|b,
      lambda:a^b,lambda:int(a==b),lambda:int(a<b),
      lambda:0 if b>=WORD else a<<b,lambda:0 if b>=WORD else a>>b,
      lambda:0 if b==0 else a//b,lambda:0 if b==0 else a%b,
      lambda:int(a==0),lambda:~a,lambda:a*b,lambda:min(a,b),lambda:max(a,b))
    return operations[fn&15]()&MASK

def signed(value,width):
    value&=(1<<width)-1
    return value-(1<<width) if value&(1<<(width-1)) else value

def code_word(beta,address,width=20):
    # All addresses, including invalid addresses, have a defined value.
    assert len(beta)==Q and all(x in (0,1) for x in beta)
    return sum((beta[a] if 0<=a<Q else 0)<<i
               for i,a in enumerate(range(address,address+width)))

def encode(name,*args):
    widths=ARGS[name];assert len(args)==len(widths)
    z=OP[name];offset=4
    for value,w in zip(args,widths):
        assert 0<=value<1<<w
        z|=value<<offset;offset+=w
    return tuple((z>>i)&1 for i in range(offset))

def decode(word):
    opcode=word&15
    if opcode>=len(OP_NAMES):return None
    name=OP_NAMES[opcode];args=[];offset=4
    for width in ARGS[name]:args.append((word>>offset)&((1<<width)-1));offset+=width
    return name,tuple(args),offset

def native_word(cells):
    """Finite corrected-h1 primitive on eleven raw binary native words."""
    assert set(cells)==set(range(-5,6))
    r=maintenance.maintenance_scalar(cells,Q=Q,U=U)
    return sum((r[f]>>b&1)<<i for i,(f,b) in enumerate(
        tuple((f,b) for f,w in NATIVE for b in range(w))[:35]))

def native_buffer(work):
    words={j:{f:0 for f,_ in NATIVE} for j in range(-5,6)}
    tags=tuple((f,b) for f,w in NATIVE for b in range(w))
    for k,(f,b) in enumerate(tags):
        for lane,j in enumerate(range(-5,6)):
            words[j][f]|=(work>>(11*k+lane)&1)<<b
    # Workspace outputs need the final-source equation and are not supplied by
    # this native-only primitive; the upper programme computes them separately.
    return native_word(words)

@dataclass(frozen=True)
class Packet:
    p:int=0;move:int=0;mode:int=0;pc:int=0;target:int=0;index:int=0
    buf:int=0;lane:int=0;ret:int=0;dst:int=0;width:int=0;kind:int=0
    start:int=0;nc:int=0;regs:tuple=(0,)*REGISTERS;work:int=0

ZERO=Packet()

def pack(p):
    z=0;offset=0
    for f,w in META:z|=(getattr(p,f)&((1<<w)-1))<<offset;offset+=w
    for value in p.regs:z|=(value&MASK)<<offset;offset+=WORD
    z|=(p.work&((1<<WORK_BITS)-1))<<offset
    return z

def unpack(z):
    d={};offset=0
    for f,w in META:d[f]=(z>>offset)&((1<<w)-1);offset+=w
    d['regs']=tuple((z>>(offset+i*WORD))&MASK for i in range(REGISTERS))
    d['work']=(z>>(offset+REGISTERS*WORD))&((1<<WORK_BITS)-1)
    return Packet(**d)

def fail(p):return replace(p,p=1,mode=ERROR,move=0)

def incoming(packets):
    chosen=[]
    for index in (1,0,2):
        p=packets[index]
        if p.p and ((index==1 and p.move in (0,3)) or
                    (index==0 and p.move==1) or (index==2 and p.move==2)):
            chosen.append(p)
    return ZERO if not chosen else fail(chosen[0]) if len(chosen)>1 else chosen[0]

def continue_pc(p,pc):
    return fail(p) if not 0<=pc<Q else replace(p,pc=pc,mode=RUN,move=0)

def io_target(p):
    return p.start+(p.index*p.lane if p.kind==STORE else p.index)

def cpu(p,address,mem17,beta):
    """One finite CPU step after migration. Optional output is ONE tape bit.

    No host transition/callback is an opcode. ROM and native arithmetic have
    explicit finite data semantics. Corrupt mode/PC/IO fields remain total.
    """
    if not p.p:return ZERO,None
    if p.move==3:return fail(p),None
    if p.mode in (HALT,ERROR):return replace(p,move=0),None
    if p.mode==IO:
        if p.kind not in range(4):return fail(p),None
        if p.kind==LDB:
            valid=p.width==37 and p.index<37 and -3<=signed(p.lane,5)<=3
            count=37
        else:
            valid=1<=p.width<=20 and (p.kind==STORE or -6<=signed(p.lane,5)<=6)
            count=p.width*(5 if p.kind==LDV else 1)
        target=io_target(p)
        last=p.start+(p.lane*(count-1) if p.kind==STORE else count-1)
        if not valid or p.dst>=REGISTERS or p.index>=count or last>=Q or target>=Q:return fail(p),None
        if address!=target:return replace(p,move=1 if address<target else 2),None
        regs=list(p.regs);work=p.work;buf=p.buf;write=None
        if p.kind==STORE:write=(regs[p.dst]>>p.index)&1
        elif p.kind==LDB:
            window=(mem17>>(signed(p.lane,5)+3))&2047
            work=(work&~(2047<<(11*p.index)))|(window<<(11*p.index))
        elif p.kind==LDC:
            bit=(mem17>>(8+signed(p.lane,5)))&1
            regs[p.dst]=(regs[p.dst]&~(1<<p.index))|(bit<<p.index)
        else:
            bitindex,q=divmod(p.index,5)
            bit=(mem17>>(8+signed(p.lane,5)-SLOTS[q]))&1
            buf=(buf&~(1<<q))|(bit<<q)
            if q==4:
                bit=int(buf.bit_count()>=3)
                regs[p.dst]=(regs[p.dst]&~(1<<bitindex))|(bit<<bitindex)
                buf=0
        p=replace(p,regs=tuple(regs),work=work,buf=buf,index=p.index+1,move=0)
        if p.index==count:return continue_pc(p,p.ret),write
        target=io_target(p)
        return replace(p,move=1 if address<target else 2 if address>target else 0),write
    decoded=decode(code_word(beta,p.pc,20)|(code_word(beta,p.pc+20,20)<<20))
    if decoded is None:return fail(p),None
    name,a,length=decoded;regs=list(p.regs);nextpc=p.pc+length
    reg_args={'HLT':(), 'MOV':(0,1), 'LIT':(0,), 'ALU':(0,1,2),
      'BNZ':(0,), 'JMP':(), 'WGET':(0,1), 'WSET':(0,1), 'NATIVE':(),
      'CGET':(0,1), 'LDV':(0,1,2), 'LDC':(0,1,2), 'LDB':(0,1),
      'ST':(0,1), 'CODE':(0,1), 'JREG':(0,)}[name]
    if any(a[i]>=REGISTERS for i in reg_args):return fail(p),None
    if name=='HLT':return replace(p,mode=HALT,move=0),None
    if name=='MOV':regs[a[0]]=regs[a[1]]
    elif name=='LIT':regs[a[0]]=a[1]
    elif name=='ALU':regs[a[0]]=alu(a[3],regs[a[1]],regs[a[2]])
    elif name=='BNZ':nextpc=a[1] if regs[a[0]] else nextpc
    elif name=='JMP':nextpc=a[0]
    elif name=='JREG':nextpc=regs[a[0]]
    elif name=='CODE':regs[a[0]]=code_word(beta,regs[a[1]])
    elif name=='WGET':
        index=regs[a[1]]
        if index>20:return fail(p),None
        regs[a[0]]=(p.work>>(20*index))&MASK
    elif name=='WSET':
        index=regs[a[0]]
        if index>20:return fail(p),None
        mask=MASK<<(20*index)
        p=replace(p,work=((p.work&~mask)|((regs[a[1]]&MASK)<<(20*index)))&((1<<WORK_BITS)-1))
    elif name=='NATIVE':p=replace(p,nc=native_buffer(p.work))
    elif name=='CGET':
        offset=regs[a[1]];width=a[2]
        regs[a[0]]=0 if offset>=37 else (p.nc>>offset)&((1<<width)-1)&MASK
    elif name in ('LDV','LDC','LDB','ST'):
        if nextpc>=Q:return fail(p),None
        if name=='LDB':
            target,centre=a;dst=0;width=37;kind=LDB;lane=regs[centre]
        elif name=='ST':
            dst,target,width,stride=a;kind=STORE;lane=stride
        else:
            dst,target,centre,width=a;kind=LDV if name=='LDV' else LDC;lane=regs[centre]
        start=regs[target]
        if start>=Q:return fail(p),None
        if kind!=STORE and not -6<=signed(lane,20)<=6:return fail(p),None
        if kind==LDB and not -3<=signed(lane,20)<=3:return fail(p),None
        if kind in (LDC,LDV):regs[dst]=0
        if kind==LDB:p=replace(p,work=0)
        p=replace(p,regs=tuple(regs),mode=IO,start=start,target=start,
          width=width,kind=kind,lane=lane&31,index=0,buf=0,dst=dst,
          ret=nextpc,move=1 if address<start else 2 if address>start else 0)
        return p,None
    return continue_pc(replace(p,regs=tuple(regs)),nextpc),None

@dataclass(frozen=True)
class Cell:
    addr:int=0;age:int=0;f1:int=0;f2:int=0;wf1:int=0;wf2:int=0
    info:tuple=(0,)*5;mailL:tuple=(0,)*5;mailR:tuple=(0,)*5
    history1:tuple=(0,)*5;history2:tuple=(0,)*5;history3:tuple=(0,)*5
    next:tuple=(0,)*5;courierL:tuple=(0,)*5;courierR:tuple=(0,)*5
    head:tuple=(0,)*5

def raw_native(c):
    return {f:getattr(c,f)&((1<<w)-1) for f,w in NATIVE}

def native_at(cells,x):
    r=maintenance.maintenance_scalar({j:raw_native(cells[x+j]) for j in range(-5,6)},Q=Q,U=U)
    return {f:r[f] for f,_ in NATIVE[:4]}

def voted(cells,logical,field):
    return majority([getattr(cells[logical-s],field)[q] for q,s in enumerate(SLOTS)])

def wipe_at(cells,x,native):return bool(native['f1'] and native['addr']!=cells[x].addr)

def final_primary(cells,x):
    """Exact FINAL computed Info at the source's primary (copy offset zero)."""
    n=native_at(cells,x);age=n['age'];address=n['addr']
    z=voted(cells,x,'info')
    if age==0:z=voted(cells,x,'next')
    elif age==DELIVERY and address in (3,Q-3):
        z=voted(cells,x,'courierL' if address==3 else 'courierR')
    return 0 if wipe_at(cells,x,n) else z&1

def capture(stage,offset):return 32*stage*Q+1 if offset==0 else 32*stage*Q+2+abs(offset)*Q

def total_rule(cells,beta):
    """Autonomous radius-eight F_beta on EVERY bit pattern of declared Sigma.

    All physical head/data copy votes use radius at most five. Only FINAL
    source composition extends to eight. Native words have actual bit widths;
    U is a power of two, so all twenty-bit clock patterns are legal clocks.
    """
    assert set(cells)==set(LANES) and len(beta)==Q
    n=native_at(cells,0);a=n['addr'];age=n['age'];f1=n['f1']
    wipe=wipe_at(cells,0,n);out=dict(n)
    pulse=96*Q<=age<98*Q
    out['wf1']=int(pulse and a>=Q-5 and final_primary(cells,Q-3-a) and not wipe)
    out['wf2']=int(pulse and a<5 and not f1 and final_primary(cells,3-a) and not wipe)
    data={f:[] for f,_ in FIELDS}
    for slot in SLOTS:
        address=(a+slot)%Q
        old={f:voted(cells,slot,f) for f,_ in FIELDS}
        head=unpack(old['head']);write=None
        if age in RESET:head=ZERO
        elif age==COLLECT:
            work=0
            for k in range(37):
                if address==PRIMARY_START+k:
                    hist=majority3(*(old['history'+str(g)] for g in (1,2,3)))
                    work=((hist>>3)&2047)<<(11*k)
            head=replace(head,work=work)
        elif COLLECT<age<EVALUATE:
            moving=unpack(voted(cells,slot-1,'head')).work
            work=head.work|moving if address==COLLECTOR else moving if PRIMARY_START<=address<COLLECTOR else 0
            head=replace(head,work=work)
        elif age==112*Q+1:
            head=Packet(p=int(address==PRIMARY_START),mode=RUN,pc=0)
        elif 112*Q+1<age<120*Q:
            head=incoming([unpack(voted(cells,slot+j,'head')) for j in (-1,0,1)])
            mem=majority3(*(old['history'+str(g)] for g in (1,2,3)))
            head,write=cpu(head,address,mem,beta)
        for field,width in FIELDS:
            z=old[field]
            if field=='head':z=pack(head)
            elif field=='info':
                if age==0:z=old['next']
                elif age==DELIVERY and address in (3,Q-3):z=old['courierL' if address==3 else 'courierR']
            elif field=='next':
                if age in RESET:z=0
                elif write is not None:z=write
            elif field in ('mailL','mailR'):
                if age in RESET:z=0
                elif age in (1,32*Q+1,64*Q+1):z=old['info']
                elif any(32*g*Q<=age<(32*g+16)*Q for g in range(3)):
                    z=voted(cells,slot+(1 if field=='mailL' else -1),field)
                if f1:z=0
            elif field.startswith('history'):
                stage=int(field[-1])-1
                if age in (32*g*Q for g in range(stage+1)):z=0
                else:
                    for lane,offset in enumerate(LANES):
                        if age==capture(stage,offset):
                            value=old['info'] if offset==0 else old['mailR' if offset<0 else 'mailL']
                            z=(z&~(1<<lane))|((value&1)<<lane)
            elif field.startswith('courier'):
                left=field=='courierL';destination=3 if left else Q-3
                if age in RESET:z=0
                elif age==EVALUATE:
                    computed=native_buffer(unpack(old['head']).work)
                    z=int(address==COLLECTOR)*((computed>>(34 if left else 33))&1)
                elif EVALUATE<age<80*Q:
                    source=voted(cells,slot+(1 if left else -1),field)
                    z=z|source if address==destination else source if min(COLLECTOR,destination)<=address<=max(COLLECTOR,destination) else 0
            data[field].append(0 if wipe else z&((1<<width)-1))
    return Cell(**out,**{f:tuple(values) for f,values in data.items()})

def offsets():
    """Interleaved raw copy coordinates: bit b/copy q is base+5*b+q."""
    z={};index=PRIMARY_START
    for f,w in NATIVE:z[f]=(index,w);index+=w
    for f,w in FIELDS:z[f]=(index,5*w);index+=5*w
    assert index==PRIMARY_START+FRAME_BITS
    return z

def encode_cell(c):
    bits=[]
    for f,w in NATIVE:bits.extend((getattr(c,f)>>b)&1 for b in range(w))
    for f,w in FIELDS:
        bits.extend((getattr(c,f)[q]>>b)&1 for b in range(w) for q in range(5))
    assert len(bits)==FRAME_BITS
    return tuple(bits)

assert sum(w for _,w in META)==124
assert HEAD_BITS==751 and FRAME_BITS==4077 and 2*FRAME_BITS<=Q
