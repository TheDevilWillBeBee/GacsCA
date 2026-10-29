"""GBC2: NEW compact binary radius-eight completion work.

This total F_beta is an explicit changed construction, not Gray's rule.
Q=8192, U=128Q, lambda=24, c=104.  beta is at most Q immutable BITS;
there is no asserted own beta or noisy/full-period theorem yet.  The ISA
has two Word20 registers, generic bit-window arithmetic and real local
History reads.  STREAM is a five-copy field operation, never rule evaluation.
"""
from dataclasses import dataclass, replace
from itertools import combinations
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))
from gacsca import maintenance

Q=8192; U=128*Q; LAMBDA=24; ERROR_SEPARATION=104
WORD=20; MASK=(1<<WORD)-1; WORK_BITS=407; WORK_MASK=(1<<WORK_BITS)-1
CODE_BITS=Q; PC_BITS=13
SLOTS=(0,-2,-1,1,2); LANES=tuple(range(-8,9))
NATIVE=(('addr',13),('age',20),('f1',1),('f2',1),('wf1',1),('wf2',1))
META=(('p',1),('move',2),('mode',3),('pc',13),('ret',13),
      ('start',13),('index',13),('buf',2),('lane',5),('fn',4),
      ('kind',2),('a',20),('b',20),('work',407),('nc',35))
HEAD_BITS=sum(w for _,w in META)
FIELDS=(('info',1),('mailL',1),('mailR',1),('history1',17),
        ('history2',17),('history3',17),('next',1),('courierL',1),
        ('courierR',1),('head',HEAD_BITS))
FRAME_BITS=37+5*sum(w for _,w in FIELDS)
PRIMARY_START=Q//2-FRAME_BITS//2
COLLECTOR=PRIMARY_START+36
COLLECT=72*Q+3; EVALUATE=COLLECT+37; DELIVERY=80*Q-1
RESET=frozenset((0,32*Q,64*Q,96*Q,112*Q))
RUN,IO,HALT,ERROR,STREAM,SPAN=range(6)
READ_BIT,READ_VOTE,READ_WORD,WRITE_BIT=range(4)
OP_NAMES=('HLT','LIT','SWAP','ALU','SETFN','BR','JMP','READ',
          'WRITE','WGET','WSET','NATIVE','NCGET','CODE','STREAM','EXT')
OP={f:i for i,f in enumerate(OP_NAMES)}
ALU_NAMES=('add','sub','and','or','xor','eq','lt','shl','shr',
           'div','mod','not','invert','mul','min','max')
ALU={f:i for i,f in enumerate(ALU_NAMES)}

def majority(values):
    assert len(values)==5
    z=0
    for a,b,c in combinations(values,3): z|=a&b&c
    return z

def majority3(a,b,c): return (a&b)|(a&c)|(b&c)

def alu(fn,a,b):
    a&=MASK; b&=MASK
    fs=(lambda:a+b, lambda:a-b, lambda:a&b, lambda:a|b,
        lambda:a^b, lambda:int(a==b), lambda:int(a<b),
        lambda:0 if b>=WORD else a<<b,
        lambda:0 if b>=WORD else a>>b,
        lambda:0 if b==0 else a//b, lambda:0 if b==0 else a%b,
        lambda:int(a==0), lambda:~a, lambda:a*b,
        lambda:min(a,b), lambda:max(a,b))
    return fs[fn&15]()&MASK

def signed(v,width):
    v&=(1<<width)-1
    return v-(1<<width) if v&(1<<(width-1)) else v

def code_word(beta,address,width=20):
    assert len(beta)==CODE_BITS
    return sum((beta[k] if 0<=k<CODE_BITS else 0)<<i
               for i,k in enumerate(range(address,address+width)))

def encode(name,*args):
    """Bit-addressed ISA. LIT uses unary length then little-endian payload.

    LIT(v): opcode, n zero bits, one bit, n low bits of v+1; n=floor
    log2(v+1). Max LIT length is 45 bits (v=2^20-1 has n=20).
    This is not Elias gamma's customary bit order, and is specified here.
    """
    def literal(v):
        assert 0<=v<=MASK
        v+=1;n=v.bit_length()-1
        return [0]*n+[1]+[(v>>i)&1 for i in range(n)]
    if name in ('SELF','ALUI','PUSH','FILL'):
        sub={'SELF':0,'ALUI':1,'PUSH':2,'FILL':3}[name]
        bits=[(OP['EXT']>>i)&1 for i in range(4)]+[(sub>>i)&1 for i in range(2)]
        if name=='SELF':
            assert len(args)==1 and 0<=args[0]<16
            return tuple(bits+[(args[0]>>i)&1 for i in range(4)])
        if name=='ALUI':
            assert len(args)==2 and 0<=args[0]<16
            return tuple(bits+[(args[0]>>i)&1 for i in range(4)]+literal(args[1]))
        if name=='PUSH':
            assert len(args)==1 and 0<=args[0]<32
            return tuple(bits+[(args[0]>>i)&1 for i in range(5)])
        assert len(args)==2 and all(v in (0,1) for v in args)
        return tuple(bits+list(args))
    bits=[(OP[name]>>i)&1 for i in range(4)]
    if name=='LIT':
        assert len(args)==1
        return tuple(bits+literal(args[0]))
    widths={'ALU':(5,),'BR':(2,13),'READ':(2,5),'STREAM':(1,1,5),
            'WGET':(5,),'WSET':(5,)}.get(name,())
    if name=='READ' and args[0]==3:widths=(2,5,2)
    assert len(args)==len(widths)
    for v,w in zip(args,widths):
        assert 0<=v<1<<w
        bits.extend((v>>i)&1 for i in range(w))
    return tuple(bits)

def decode(beta,pc):
    """Total fetch; invalid LIT's missing delimiter is an error.

    Fetch outside beta is zero, as CODE. There is no instruction-boundary
    validity requirement on an arbitrary raw PC.
    """
    def literal(at):
        n=0
        while n<=20 and not code_word(beta,at+n,1): n+=1
        if n>20:return None
        value=(1<<n)|code_word(beta,at+1+n,n)
        if value>MASK+1:return None
        return value-1,1+2*n
    opcode=code_word(beta,pc,4); name=OP_NAMES[opcode]
    if name=='LIT':
        lit=literal(pc+4)
        return None if lit is None else (name,(lit[0],),4+lit[1])
    if name=='EXT':
        sub=code_word(beta,pc+4,2)
        if sub==0:return 'SELF',(code_word(beta,pc+6,4),),10
        if sub==1:
            lit=literal(pc+10)
            return None if lit is None else ('ALUI',(code_word(beta,pc+6,4),lit[0]),10+lit[1])
        if sub==2:return 'PUSH',(code_word(beta,pc+6,5),),11
        return 'FILL',(code_word(beta,pc+6,1),code_word(beta,pc+7,1)),8
    widths={'ALU':(5,),'BR':(2,13),'READ':(2,5),'STREAM':(1,1,5),
            'WGET':(5,),'WSET':(5,)}.get(name,())
    args=[]; offset=4
    for width in widths:
        args.append(code_word(beta,pc+offset,width)); offset+=width
    if name=='READ' and args[0]==3:
        args.append(code_word(beta,pc+offset,2)); offset+=2
    return name,tuple(args),offset

def native_buffer(work):
    tags=tuple((f,k) for f,w in NATIVE for k in range(w))
    cells={j:{f:0 for f,_ in NATIVE} for j in range(-5,6)}
    for k,(f,b) in enumerate(tags):
        for lane,j in enumerate(range(-5,6)):
            cells[j][f]|=(work>>(11*k+lane)&1)<<b
    r=maintenance.maintenance_scalar(cells,Q=Q,U=U)
    return sum((r[f]>>k&1)<<i for i,(f,k) in enumerate(tags[:35]))

@dataclass(frozen=True)
class Packet:
    p:int=0; move:int=0; mode:int=0; pc:int=0; ret:int=0
    start:int=0; index:int=0; buf:int=0; lane:int=0; fn:int=0
    kind:int=0; a:int=0; b:int=0; work:int=0; nc:int=0

ZERO=Packet()

def pack(p):
    z=0; o=0
    for f,w in META:z|=(getattr(p,f)&((1<<w)-1))<<o; o+=w
    return z

def unpack(z):
    values={}; o=0
    for f,w in META:values[f]=(z>>o)&((1<<w)-1); o+=w
    return Packet(**values)

def fail(p):return replace(p,p=1,mode=ERROR,move=0)

def incoming(packets):
    chosen=[]
    for i in (1,0,2):
        p=packets[i]
        if p.p and ((i==1 and p.move in (0,3)) or
                    (i==0 and p.move==1) or (i==2 and p.move==2)):
            chosen.append(p)
    return ZERO if not chosen else fail(chosen[0]) if len(chosen)>1 else chosen[0]

def continue_pc(p,pc):
    return fail(p) if not 0<=pc<CODE_BITS else replace(p,pc=pc,mode=RUN,move=0)

def move_to(p,address,target):
    return replace(p,move=1 if address<target else 2 if address>target else 0)

def read_vote(mem,base,q=0,aligned=False):
    """Generic interleaved-five vote from actual nearby History columns.

    For current raw-copy column q of a five-column group, mem[r-q] is
    the voted temporal History at raw-copy column r.  Aligned mode asks
    for logical source centre base+SLOTS[q], otherwise centre base.
    """
    centre=base+(SLOTS[q] if aligned else 0)
    bits=[(mem[r-q]>>(8+centre-SLOTS[r]))&1 for r in range(5)]
    return int(sum(bits)>=3)

def cpu(p,address,mem,beta):
    """One finite CPU step with data window d=-4..4 and optional ONE write.

    Every input bit pattern has a defined output. No opcode evaluates a
    host CPU, cell transition, or arbitrary supplied programme callback.
    """
    assert set(mem)==set(range(-4,5)) and 0<=address<Q
    if not p.p:return ZERO,None
    if p.move==3 or p.mode>=6:return fail(p),None
    if p.mode in (HALT,ERROR):return replace(p,move=0),None
    if p.mode==IO:
        lane=signed(p.lane,5)
        valid=(p.kind==READ_BIT and -8<=lane<=8 or
               p.kind==READ_VOTE and -6<=lane<=6 or
               p.kind==READ_WORD and lane==0 or
               p.kind==WRITE_BIT)
        if not valid:return fail(p),None
        if address!=p.start:return move_to(p,address,p.start),None
        write=p.a&1 if p.kind==WRITE_BIT else None
        value=p.a
        if p.kind==READ_BIT:value=(mem[0]>>(8+lane))&1
        elif p.kind==READ_VOTE:value=read_vote(mem,lane,address%5)
        elif p.kind==READ_WORD:value=mem[0]&((1<<17)-1)
        return continue_pc(replace(p,a=value),p.ret),write
    if p.mode==SPAN:
        # Generic bounded serial input collection. No input beyond the
        # local nine-column window is read on any update. kind0 reads
        # raw bits with stride1; kind1/2 vote aligned/unaligned at stride5;
        # kind3 reads raw bits with stride5. The accumulator is Word20 B.
        lane=signed(p.lane,5); stride=1 if p.kind==0 else 5
        limit=4 if p.kind==1 else 6 if p.kind==2 else 8
        if not -limit<=lane<=limit or not 1<=p.a<=WORD or p.index>=p.a or p.start+(p.a-1)*stride>=Q:
            return fail(p),None
        target=p.start+(p.a-p.index-1)*stride
        if address!=target:return move_to(p,address,target),None
        bit=read_vote(mem,lane,address%5,p.kind==1) if p.kind in (1,2) else (mem[0]>>(8+lane))&1
        value=(p.b|(bit<<(p.a-p.index-1)))&MASK
        if p.index==0:return continue_pc(replace(p,a=value,b=value),p.ret),None
        return replace(p,b=value,index=p.index-1,move=1),None
    if p.mode==STREAM:
        lane=signed(p.lane,5); aligned=bool(p.buf&2)
        constant=bool(p.buf&1)
        stride=5 if p.kind==1 else 1
        if not constant and not -(4 if aligned else 6)<=lane<=(4 if aligned else 6):
            return fail(p),None
        if p.kind>1 or not 1<=p.a<=Q or p.index>=p.a or p.start+(p.a-1)*stride>=Q:
            return fail(p),None
        target=p.start+(p.a-p.index-1)*stride
        if address!=target:return move_to(p,address,target),None
        q=address%5
        write=(p.lane&1) if constant else read_vote(mem,lane,q,aligned)
        if p.index==0:return continue_pc(p,p.ret),write
        return replace(p,index=p.index-1,move=1),write
    decoded=decode(beta,p.pc)
    if decoded is None:return fail(p),None
    name,args,length=decoded; nextpc=p.pc+length
    if name=='HLT':return replace(p,mode=HALT,move=0),None
    if name=='LIT':p=replace(p,a=args[0])
    elif name=='SWAP':p=replace(p,a=p.b,b=p.a)
    elif name=='ALU':
        fn=args[0]
        if fn>16:return fail(p),None
        p=replace(p,a=alu(p.fn if fn==16 else fn,p.a,p.b))
    elif name=='SETFN':p=replace(p,fn=p.a&15)
    elif name=='BR':
        cond,target=args
        take=(True,p.a==0,p.a!=0,bool(p.a&(1<<19)))[cond]
        nextpc=target if take else nextpc
    elif name=='JMP':nextpc=p.a
    elif name=='WGET':
        offset=p.a if args[0]==31 else 20*args[0]
        p=replace(p,a=0 if offset>=WORK_BITS else (p.work>>offset)&MASK)
    elif name=='WSET':
        offset=p.b if args[0]==31 else 20*args[0]
        if offset<WORK_BITS:
            mask=MASK<<offset
            p=replace(p,work=((p.work&~mask)|(p.a<<offset))&WORK_MASK)
    elif name=='NATIVE':p=replace(p,nc=native_buffer(p.work))
    elif name=='NCGET':p=replace(p,a=0 if p.b>=35 else (p.nc>>p.b)&MASK)
    elif name=='CODE':p=replace(p,a=code_word(beta,p.b))
    elif name=='SELF':
        values=(address,p.pc,p.ret,p.start,p.index,p.buf,p.lane,p.fn,
                p.kind,p.p,p.move,p.mode,p.work&MASK,p.nc&MASK,p.nc>>20,0)
        p=replace(p,a=values[args[0]]&MASK)
    elif name=='ALUI':p=replace(p,a=alu(args[0],p.a,args[1]))
    elif name=='PUSH':
        width=args[0]
        if width>WORD:return fail(p),None
        p=replace(p,work=((p.work<<width)|(p.a&((1<<width)-1)))&WORK_MASK)
    elif name in ('READ','WRITE'):
        if p.b>=Q or nextpc>=Q:return fail(p),None
        kind,lane=args[:2] if name=='READ' else (WRITE_BIT,0)
        if lane==16:lane=signed(p.fn,4)&31
        lane=signed(lane,5)
        if kind==3 and name=='READ':
            variant=args[2]; stride=1 if variant==0 else 5
            limit=4 if variant==1 else 6 if variant==2 else 8
            if not -limit<=lane<=limit or not 1<=p.a<=WORD or p.b+(p.a-1)*stride>=Q:
                return fail(p),None
            return move_to(replace(p,mode=SPAN,kind=variant,lane=lane&31,
                                   start=p.b,index=p.a-1,b=0,ret=nextpc),address,p.b),None
        valid=(kind==READ_BIT and -8<=lane<=8 or
               kind==READ_VOTE and -6<=lane<=6 or
               kind==READ_WORD and lane==0 or kind==WRITE_BIT and name=='WRITE')
        if not valid:return fail(p),None
        return move_to(replace(p,mode=IO,kind=kind,lane=lane&31,
                               start=p.b,ret=nextpc),address,p.b),None
    elif name=='STREAM':
        aligned,wide,lane=args
        if lane==16:lane=signed(p.fn,4)&31
        lane=signed(lane,5); stride=5 if wide else 1
        limit=4 if aligned else 6
        if not -limit<=lane<=limit or not 1<=p.a<=Q or p.b+(p.a-1)*stride>=Q or nextpc>=Q:
            return fail(p),None
        return move_to(replace(p,mode=STREAM,start=p.b,index=p.a-1,
                               lane=lane&31,buf=2*aligned,kind=wide,ret=nextpc),address,p.b),None
    elif name=='FILL':
        wide,value=args; stride=5 if wide else 1
        if not 1<=p.a<=Q or p.b+(p.a-1)*stride>=Q or nextpc>=Q:return fail(p),None
        return move_to(replace(p,mode=STREAM,start=p.b,index=p.a-1,
                               lane=value,buf=1,kind=wide,ret=nextpc),address,p.b),None
    return continue_pc(p,nextpc),None

@dataclass(frozen=True)
class Cell:
    addr:int=0;age:int=0;f1:int=0;f2:int=0;wf1:int=0;wf2:int=0
    info:tuple=(0,)*5;mailL:tuple=(0,)*5;mailR:tuple=(0,)*5
    history1:tuple=(0,)*5;history2:tuple=(0,)*5;history3:tuple=(0,)*5
    next:tuple=(0,)*5;courierL:tuple=(0,)*5;courierR:tuple=(0,)*5
    head:tuple=(0,)*5

def raw_native(c):return {f:getattr(c,f)&((1<<w)-1) for f,w in NATIVE}

def native_at(cells,x):
    r=maintenance.maintenance_scalar({j:raw_native(cells[x+j]) for j in range(-5,6)},Q=Q,U=U)
    return {f:r[f] for f,_ in NATIVE[:4]}

def voted(cells,logical,field):
    return majority([getattr(cells[logical-s],field)[q] for q,s in enumerate(SLOTS)])

def wipe_at(cells,x,n):return bool(n['f1'] and n['addr']!=cells[x].addr)

def final_primary(cells,x):
    n=native_at(cells,x); age=n['age']; a=n['addr']; z=voted(cells,x,'info')
    if age==0:z=voted(cells,x,'next')
    elif age==DELIVERY and a in (3,Q-3):z=voted(cells,x,'courierL' if a==3 else 'courierR')
    return 0 if wipe_at(cells,x,n) else z&1

def capture(stage,offset):return 32*stage*Q+1 if offset==0 else 32*stage*Q+2+abs(offset)*Q

def total_rule(cells,beta):
    """Total autonomous radius-eight transition for any immutable Q-bit beta.

    Compact CPU changes only Head execution. All unproved full-rule
    composition and Gray refinement obligations remain explicit.
    """
    assert set(cells)==set(LANES) and len(beta)==CODE_BITS
    n=native_at(cells,0); a=n['addr']; age=n['age']; f1=n['f1']
    wipe=wipe_at(cells,0,n); out=dict(n); pulse=96*Q<=age<98*Q
    out['wf1']=int(pulse and a>=Q-5 and final_primary(cells,Q-3-a) and not wipe)
    out['wf2']=int(pulse and a<5 and not f1 and final_primary(cells,3-a) and not wipe)
    data={f:[] for f,_ in FIELDS}
    for slot in SLOTS:
        address=(a+slot)%Q; old={f:voted(cells,slot,f) for f,_ in FIELDS}
        head=unpack(old['head']); write=None
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
        elif age==112*Q+1:head=Packet(p=int(address==PRIMARY_START))
        elif 112*Q+1<age<120*Q:
            head=incoming([unpack(voted(cells,slot+j,'head')) for j in (-1,0,1)])
            mem={d:majority3(*(voted(cells,slot+d,'history'+str(g)) for g in (1,2,3)))
                 for d in range(-4,5)}
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
                left=field=='courierL'; destination=3 if left else Q-3
                if age in RESET:z=0
                elif age==EVALUATE:
                    computed=native_buffer(unpack(old['head']).work)
                    z=int(address==COLLECTOR)*((computed>>(34 if left else 33))&1)
                elif EVALUATE<age<80*Q:
                    source=voted(cells,slot+(1 if left else -1),field)
                    z=z|source if address==destination else source if min(COLLECTOR,destination)<=address<=max(COLLECTOR,destination) else 0
            data[field].append(0 if wipe else z&((1<<width)-1))
    return Cell(**out,**{f:tuple(z) for f,z in data.items()})

def offsets():
    z={}; o=PRIMARY_START
    for f,w in NATIVE:z[f]=(o,w);o+=w
    for f,w in FIELDS:z[f]=(o,5*w);o+=5*w
    assert o==PRIMARY_START+FRAME_BITS
    return z

def encode_cell(c):
    bits=[]
    for f,w in NATIVE:bits.extend((getattr(c,f)>>k)&1 for k in range(w))
    for f,w in FIELDS:bits.extend((getattr(c,f)[q]>>k)&1 for k in range(w) for q in range(5))
    assert len(bits)==FRAME_BITS
    return tuple(bits)

def pack_cell(c):return sum(v<<i for i,v in enumerate(encode_cell(c)))

def unpack_cell(z):
    data={};offset=0
    for f,w in NATIVE:data[f]=(z>>offset)&((1<<w)-1);offset+=w
    for f,w in FIELDS:
        data[f]=tuple(sum((z>>(offset+5*k+q)&1)<<k for k in range(w)) for q in range(5))
        offset+=5*w
    assert offset==FRAME_BITS
    return Cell(**data)

assert HEAD_BITS==553 and FRAME_BITS==3087 and 2*FRAME_BITS<=Q
