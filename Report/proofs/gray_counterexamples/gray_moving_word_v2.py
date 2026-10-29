"""GMW2 changed immutable-ROM candidate: instantaneous immutable-PC code, interleaved SF.

Total physical primitive; Q8192/U128Q/lambda24/c104 retained. Explicit changes
from GMW0/Gray: h1 native, holder-computed service Address, immutable instruction access,
mutable ProgramBit copied from beta(service Address), WF outputs0. No own-beta proof
or gathering proof is asserted by this module.
"""
from dataclasses import dataclass,replace
import gray_moving_word_kernel as old

Q=8192;U=128*Q;CODE_CAPACITY=65536;WORD=20;MASK=(1<<WORD)-1;LAMBDA=24;ERROR_SEPARATION=104
SLOTS=old.SLOTS
RUN,SEEK,LOAD,WRITE,HALT,ERROR=range(6)
META=(('p',1),('move',2),('mode',3),('pc',16),('start',13),('width',5),
      ('index',5),('kind',3),('dst',4),('lane',4),('source',2),('dest',1))
HEAD_BITS=sum(w for _,w in META)+16*WORD
FRAME_BITS=37+5*HEAD_BITS+55+20
PRIMARY_START=Q//2-FRAME_BITS//2
HEAD_ADDRESS=PRIMARY_START
NATIVE_COLUMNS={'addr':(PRIMARY_START,13),'age':(PRIMARY_START+13,20),
                'f1':(PRIMARY_START+33,1),'f2':(PRIMARY_START+34,1),
                'wf1':(PRIMARY_START+35,1),'wf2':(PRIMARY_START+36,1)}
OP_NAMES=('HLT','JMPR')+old.OP_NAMES[2:]+('LOADR','WRITER','SHIFT','CODE')
OP={name:i for i,name in enumerate(OP_NAMES)}
ARGS=dict(old.ARGS);del ARGS['NOP'];ARGS['BNZ']=(4,16);ARGS['JMP']=(16,)
ARGS.update(JMPR=(4,),LOADR=(4,4,4,4,2),WRITER=(4,4,4,1),SHIFT=(4,4,6),CODE=(4,4),ALU=(4,4,4,4,4))
LENGTH={OP[name]:5+sum(widths) for name,widths in ARGS.items() if name in OP}
LENGTH[31]=14
ALU_NAMES=('MOV','ADD','SUB','AND','OR','XOR','EQ','NE','LT','NOT','BIT','SHIFT','WINDOW')


@dataclass(frozen=True)
class Packet:
    p:int=0;move:int=0;mode:int=0;pc:int=0;start:int=0;width:int=0;index:int=0
    kind:int=0;dst:int=0;lane:int=0;source:int=0;dest:int=0
    regs:tuple=(0,)*16


ZERO=Packet()


def pack(p):
    v=0;s=0
    for name,w in META:v|=(getattr(p,name)&((1<<w)-1))<<s;s+=w
    for r in p.regs:v|=(r&MASK)<<s;s+=20
    return v


def unpack(v):
    data={};s=0
    for name,w in META:data[name]=(v>>s)&((1<<w)-1);s+=w
    return Packet(**data,regs=tuple((v>>(s+20*i))&MASK for i in range(16)))


def scalar_native(cells):
    """Independent h1 calculation; original Flag2 clause is explicitly changed."""
    base=old.literal_maintenance.scalar(cells);c=cells[0]
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


def columns():
    result=[];cursor=PRIMARY_START+37
    for name,w in META+tuple(('r'+str(i),20) for i in range(16)):
        result.append((name,cursor,w));cursor+=5*w
    for name,w in (('mem',11),('out',1),('info',1),('scratch',1),('program',1)):
        result.append((name,cursor,w));cursor+=5*w
    assert cursor==PRIMARY_START+FRAME_BITS
    return tuple(result)


COLUMNS=columns();COLUMN={name:(b,w) for name,b,w in COLUMNS}


def instruction_bits(name,*args):
    widths=ARGS[name];assert len(args)==len(widths)
    v=31 if name=='ALU' else OP[name];s=6 if name in ('CODE','ALU') else 5
    if name=='ALU':v|=32
    for a,w in zip(args,widths):
        assert -(1<<(w-1))<=a<1<<w
        v|=(a&((1<<w)-1))<<s;s+=w
    return [(v>>i)&1 for i in range(s)]


def decode(v):
    name=('ALU' if (v>>5)&1 else 'CODE') if (v&31)==31 else OP_NAMES[v&31]
    a=[];s=6 if name in ('CODE','ALU') else 5
    for w in ARGS[name]:a.append((v>>s)&((1<<w)-1));s+=w
    return name,tuple(a)


def instruction_length(v):return 26 if (v&63)==63 else LENGTH[v&31]


def generic_alu(op,a,b,c):
    """Finite scalar ALU, no head/native/whole transition intrinsic.

    WINDOW uses a=11-bit mask, b=full20-bit Address, c=signed
    lo4|signed hi4<<4|existence<<8. Invalid operations/windows return high-bit sentinel.
    """
    if op>=len(ALU_NAMES):return 1<<19
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
    if op==10:return (a>>b)&1 if b<20 else 0
    if op==11:
        n=b&63;n=n if n<32 else n-64
        return ((a<<n)&MASK) if n>=0 else a>>-n
    lo=c&15;hi=(c>>4)&15;lo=lo if lo<8 else lo-16;hi=hi if hi<8 else hi-16
    if not -5<=lo<=hi<=5:return 1<<19
    return sum(((a>>(j+5))&1) and ((c>>8)&1) and 0<=b+j<Q for j in range(lo,hi+1))


def beta_word(beta,address,width=20):
    return sum((beta[address+i]&1)<<i for i in range(width) if 0<=address+i<len(beta))


def fail(p):return replace(p,p=1,mode=ERROR,move=0)


def alu(p,name,args):
    """Only GMW0's generic arithmetic/window primitives; not native/full Apply."""
    proxy=old.Packet(p=1,regs=p.regs)
    result=old.execute_instruction(proxy,0,(name,args),1)
    return fail(p) if result.mode==old.ERROR else replace(p,regs=result.regs)


def start_io(p,address,pc,name,a):
    r=list(p.regs);source=dest=0;lane=5
    if name=='LOAD5':start,width,side=a;kind=0;dst=0;lane=side;r[:5]=[0]*5
    elif name=='LOADC':dst,start,width=a;kind=1;r[dst]=0
    elif name=='LOADCOL':dst,start=a;width=1;kind=2;r[dst]=0
    elif name=='WRITE':dst,start,width=a;kind=4
    elif name=='LOADR':dst,ar,wr,lr,source=a;start,width,lane=r[ar],r[wr],r[lr];kind=3;r[dst]=0
    elif name=='WRITER':dst,ar,wr,dest=a;start,width=r[ar],r[wr];kind=4
    else:return fail(p)
    if not 1<=width<=20 or start+width>Q or not 0<=lane<=10:return fail(p)
    return replace(p,pc=pc,mode=SEEK,start=start,width=width,index=0,kind=kind,
        dst=dst,lane=lane,source=source,dest=dest,regs=tuple(r),
        move=1 if address<start else 2 if address>start else 0)


def step_packet(p,address,mem,out,scratch,program,beta):
    """One total head step; returns (head, Out-write?, Scratch-write?)."""
    if not p.p:return ZERO,None,None
    if p.move==3 or p.mode>=6:return fail(p),None,None
    if p.mode in (HALT,ERROR):return replace(p,move=0),None,None
    if p.mode==RUN:
        v=beta_word(beta,p.pc,29);name,a=decode(v);nextpc=p.pc+instruction_length(v)
        if nextpc>CODE_CAPACITY:return fail(p),None,None
        nextpc&=65535
        if name=='HLT':return replace(p,mode=HALT,move=0),None,None
        if name in ('JMP','BNZ','JMPR'):
            target=a[0] if name=='JMP' else p.regs[a[0]]&65535 if name=='JMPR' else a[1] if p.regs[a[0]] else nextpc
            return replace(p,pc=target,move=0),None,None
        if name in ('LOAD5','LOADC','LOADCOL','WRITE','LOADR','WRITER'):
            return start_io(p,address,nextpc,name,a),None,None
        if name=='CODE':
            r=list(p.regs);r[a[0]]=beta_word(beta,r[a[1]],20)
            return replace(p,pc=nextpc,move=0,regs=tuple(r)),None,None
        if name=='ALU':
            d,op,ai,bi,ci=a;r=list(p.regs);r[d]=generic_alu(r[op],r[ai],r[bi],r[ci])
            return replace(p,pc=nextpc,move=0,regs=tuple(r)),None,None
        if name=='SHIFT':
            d,s,amount=a;amount=amount if amount<32 else amount-64
            r=list(p.regs);r[d]=((r[s]<<amount)&MASK) if amount>=0 else r[s]>>-amount
            return replace(p,pc=nextpc,move=0,regs=tuple(r)),None,None
        return replace(alu(p,name,a),pc=nextpc,move=0),None,None
    if not 1<=p.width<=20 or p.start+p.width>Q or p.index>=p.width or p.kind>4 or p.lane>10:
        return fail(p),None,None
    target=p.start+p.index
    if address!=target:
        return replace(p,mode=SEEK,move=1 if address<target else 2),None,None
    p=replace(p,mode=WRITE if p.kind==4 else LOAD)
    r=list(p.regs);outwrite=scratchwrite=None
    if p.kind==0:
        if p.lane not in (0,1):return fail(p),None,None
        for i in range(5):
            lane=5+(i+1)*(1 if p.lane else -1);r[i]|=((mem>>lane)&1)<<p.index
    elif p.kind==1:r[p.dst]|=((mem>>5)&1)<<p.index
    elif p.kind==2:r[p.dst]=mem&2047
    elif p.kind==3:
        bit=((mem>>p.lane)&1) if p.source==0 else out if p.source==1 else scratch if p.source==2 else program
        r[p.dst]|=bit<<p.index
    else:
        bit=(r[p.dst]>>p.index)&1
        if p.dest:scratchwrite=bit
        else:outwrite=bit
    p=replace(p,regs=tuple(r),index=p.index+1)
    if p.index==p.width:p=replace(p,mode=RUN,index=0,width=0,move=0)
    else:p=replace(p,move=1)
    return p,outwrite,scratchwrite


@dataclass(frozen=True)
class Cell:
    addr:int=0;age:int=0;f1:int=0;f2:int=0;wf1:int=0;wf2:int=0
    heads:tuple=(0,)*5;mem:tuple=(0,)*5;out:tuple=(0,)*5;info:tuple=(0,)*5
    scratch:tuple=(0,)*5;program:tuple=(0,)*5


def incoming(packets):
    candidates=[]
    for index in (1,0,2):
        p=packets[index]
        if p.p and ((index==1 and p.move in (0,3)) or (index==0 and p.move==1) or (index==2 and p.move==2)):
            candidates.append(p)
    if not candidates:return ZERO
    return fail(candidates[0]) if len(candidates)>1 else candidates[0]


def initial_packet():return Packet(p=1)


def local_transition(cells,beta):
    assert len(beta)==CODE_CAPACITY and set(cells)==set(range(-5,6))
    native={j:{n:getattr(c,n)&(8191 if n=='addr' else MASK if n=='age' else 1)
             for n in ('addr','age','f1','f2','wf1','wf2')} for j,c in cells.items()}
    a=scalar_native(native);age=a['age'];reset=age in (0,112*Q);birth=age==112*Q+1
    active=112*Q+1<age<=120*Q;wipe=a['f1'] and a['addr']!=native[0]['addr']
    values={n:[] for n in ('heads','mem','out','info','scratch','program')}
    def logical(n,y):return old.vote([getattr(cells[y-t],n)[i] for i,t in enumerate(SLOTS)])
    for y in SLOTS:
        # Explicit changed convention: the physical holder's already computed
        # native GF plus its copy displacement, never a source's computed GF.
        address=(a['addr']+y)%Q
        mem=logical('mem',y)&2047;out=logical('out',y)&1;scratch=logical('scratch',y)&1
        info=out if age==0 else logical('info',y)&1
        pb=beta[address]&1
        if reset:head=ZERO;out=scratch=0
        elif birth:head=initial_packet() if address==HEAD_ADDRESS else ZERO
        elif active:
            head=incoming([unpack(logical('heads',y+j)) for j in (-1,0,1)])
            head,ow,sw=step_packet(head,address,mem,out,scratch,logical('program',y)&1,beta)
            if ow is not None:out=ow
            if sw is not None:scratch=sw
        else:head=unpack(logical('heads',y))
        if wipe:head=ZERO;mem=out=info=scratch=pb=0
        for n,v in (('heads',pack(head)),('mem',mem),('out',out),('info',info),('scratch',scratch),('program',pb)):
            values[n].append(v)
    return Cell(**a,**{n:tuple(v) for n,v in values.items()})


def cell_bits(c):
    result=[]
    for n,w in (('addr',13),('age',20),('f1',1),('f2',1),('wf1',1),('wf2',1)):
        result.extend((getattr(c,n)>>i)&1 for i in range(w))
    heads=[unpack(v) for v in c.heads]
    for n,b,w in COLUMNS:
        values=[getattr(p,n) if not n.startswith('r') else p.regs[int(n[1:])] for p in heads] if n not in (
                'mem','out','info','scratch','program') else getattr(c,n)
        for value in values:result.extend((value>>i)&1 for i in range(w))
    assert len(result)==FRAME_BITS
    return result


def cell_from_bits(bits):
    assert len(bits)==FRAME_BITS
    data={};cursor=0
    def take(w):
        nonlocal cursor
        v=sum(bits[cursor+i]<<i for i in range(w));cursor+=w;return v
    for n,w in (('addr',13),('age',20),('f1',1),('f2',1),('wf1',1),('wf2',1)):data[n]=take(w)
    packets=[dict(regs=[0]*16) for _ in range(5)]
    for n,b,w in COLUMNS:
        values=[take(w) for _ in range(5)]
        if n in ('mem','out','info','scratch','program'):data[n]=tuple(values)
        else:
            for i,value in enumerate(values):
                if n.startswith('r'):packets[i]['regs'][int(n[1:])]=value
                else:packets[i][n]=value
    data['heads']=tuple(pack(Packet(**{**p,'regs':tuple(p['regs'])})) for p in packets)
    return Cell(**data)


def input_tape(cells):
    raw={j:cell_bits(cells[j]) for j in range(-5,6)}
    return {PRIMARY_START+i:sum(raw[j][i]<<(j+5) for j in range(-5,6)) for i in range(FRAME_BITS)}


def execute(beta,tape,limit=65535,record=False):
    address=HEAD_ADDRESS;p=initial_packet();out={};scratch={};history=[]
    for tick in range(limit):
        address+=1 if p.move==1 else -1 if p.move==2 else 0
        assert 0<=address<Q
        oldp=p;p,ow,sw=step_packet(p,address,tape.get(address,0),out.get(address,0),
                scratch.get(address,0),beta[address],beta)
        if ow is not None:out[address]=ow
        if sw is not None:scratch[address]=sw
        if record:history.append((address,oldp,p,ow,sw))
        if p.mode in (HALT,ERROR):return out,tick+1,p,history
    return out,limit,p,history
