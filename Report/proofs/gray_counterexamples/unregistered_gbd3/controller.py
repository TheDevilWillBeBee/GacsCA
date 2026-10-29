"""GBD3 finite Head/ISA block, parameterized by ONE counted binary beta.

Not a complete CA: native computed ports, stage reset/birth and other SF
operators are absent. No full-R/native evaluator, dictionary or host opcode
is used. The declared generic data/ALU functions are literal finite logic.
"""
from dataclasses import dataclass,replace
from itertools import combinations

Q=8192;U=128*Q;WORD=20;MASK=(1<<WORD)-1
S=(0,-2,-1,1,2);INV=(0,4,3,2,1)
RUN,TRAVEL,STOP,BAD_MODE=range(4)
ALU_NAMES=('add','sub','and','or','xor','not','eq','lt','mul','div',
           'mod','shl','shr','min','max','copy','ne','le')
# Every table here describes fixed ISA wiring, not stored beta data.
OPS={'HALT':0,'LIT':1,'ALU':2,'BR':3,'READ':4,'WRITE':5,'CODE':6,
     'MOVE':7,'CALL':8,'RET':9,'GETHEAD':10,'SETHEAD':11,
     'ALUR':12,'QUORUM':13,'READQ':14}

@dataclass(frozen=True)
class Head:
    present:int=0
    move:int=0
    mode:int=0
    pc:int=0
    ret:int=0
    target:int=0
    regs:tuple=(0,)*8

HEAD_FIELDS=(('present',1),('move',2),('mode',2),('pc',13),
             ('ret',13),('target',13))
HEAD_BITS=sum(n for _,n in HEAD_FIELDS)+8*20
assert HEAD_BITS==204

def pack_head(h):
    z=b=0
    for name,n in HEAD_FIELDS:
        z|=(getattr(h,name)&((1<<n)-1))<<b;b+=n
    for v in h.regs:
        z|=(v&MASK)<<b;b+=20
    return z

def unpack_head(z):
    values={};b=0
    for name,n in HEAD_FIELDS:
        values[name]=(z>>b)&((1<<n)-1);b+=n
    values['regs']=tuple((z>>(b+20*i))&MASK for i in range(8))
    return Head(**values)

def majority5(values):
    z=0
    for a,b,c in combinations(values,3):z|=a&b&c
    return z

def equal_quorum(values,fallback):
    # Fixed length five, universal WORD values, exact threshold three.
    for v in values:
        if sum(v==w for w in values)>=3:return v&MASK
    return fallback&MASK

def alu(fn,a,b):
    a&=MASK;b&=MASK
    if fn==0:z=a+b
    elif fn==1:z=a-b
    elif fn==2:z=a&b
    elif fn==3:z=a|b
    elif fn==4:z=a^b
    elif fn==5:z=~a
    elif fn==6:z=int(a==b)
    elif fn==7:z=int(a<b)
    elif fn==8:z=a*b
    elif fn==9:z=a//b if b else 0
    elif fn==10:z=a%b if b else 0
    elif fn==11:z=a<<b if b<20 else 0
    elif fn==12:z=a>>b if b<20 else 0
    elif fn==13:z=min(a,b)
    elif fn==14:z=max(a,b)
    elif fn==15:z=a
    elif fn==16:z=int(a!=b)
    elif fn==17:z=int(a<=b)
    else:z=0
    return z&MASK

def branch(cond,a,b):
    a&=MASK;b&=MASK
    return (True,a==0,a!=0,a==b,a!=b,a<b,a<=b,False)[cond&7]

def take(bits,p,n):
    if p<0 or p+n>len(bits):return None
    return sum(bits[p+i]<<i for i in range(n))

def instruction(beta,pc):
    """Total all-PC decode, including noninstruction-aligned raw PCs.

    Beta has <=Q actual binary bits, no extended fetch or large dictionary.
    Out-of-stream operands and raw LIT widths21..31 decode INVALID.
    """
    pc&=Q-1
    op=take(beta,pc,4)
    if op is None or op>=15:return ('INVALID',(),0)
    name=tuple(OPS)[op]
    p=pc+4;args=[]
    shapes={0:(),1:(3,5),2:(5,3,3,3),3:(3,3,3,13),
            4:(3,3,3,3,1),5:(3,3,3,1),6:(3,3,3),7:(3,),
            8:(13,),9:(),10:(3,3),11:(3,3),12:(3,3,3,3),
            13:(1,3,3,3,3,3,3,3),14:(3,3,3,3,1)}
    for n in shapes[op]:
        v=take(beta,p,n)
        if v is None:return ('INVALID',(),0)
        args.append(v);p+=n
    if op==1:
        n=args[1]
        if n>20:return ('INVALID',(),0)
        v=take(beta,p,n)
        if v is None:return ('INVALID',(),0)
        args.append(v);p+=n
    return (name,tuple(args),p-pc)

def code_word(beta,index,count):
    if not (0<=count<=20):return 0
    # Indexed by the whole raw Word20, not silently reduced moduloQ.
    return sum((beta[index+i] if 0<=index+i<len(beta) else 0)<<i
               for i in range(count))&MASK

def encode(name,*args):
    op=OPS[name]
    shapes={0:(),1:(3,5,lambda a:a[1]),2:(5,3,3,3),3:(3,3,3,13),
            4:(3,3,3,3,1),5:(3,3,3,1),6:(3,3,3),7:(3,),
            8:(13,),9:(),10:(3,3),11:(3,3),12:(3,3,3,3),
            13:(1,3,3,3,3,3,3,3),14:(3,3,3,3,1)}
    widths=shapes[op]
    assert len(args)==len(widths)
    out=[(op>>i)&1 for i in range(4)]
    for v,n in zip(args,widths):
        n=n(args) if callable(n) else n
        assert 0<=v<(1<<n) if n else v==0
        out.extend((v>>i)&1 for i in range(n))
    return tuple(out)

@dataclass(frozen=True)
class Cell:
    addr:int=0                    # EXPLICIT computed native output port
    age:int=0                     # EXPLICIT computed native output port
    head:tuple=(0,)*5             # five independent raw Head204 slots
    mem:tuple=(0,)*5              # five independent raw Mem340 slots
    out:tuple=(0,)*5              # five independent raw Out20 slots

def vote(cells,y,field,mask):
    return majority5([getattr(cells[y+s],field)[INV[h]]
                      for h,s in enumerate(S)])&mask

def head_vote(cells,y):return unpack_head(vote(cells,y,'head',(1<<204)-1))

def read(cells,x,q,lane,phase,stride,count,diagonal=False):
    # READQ is a generic two-level five-bit vote. It uses five selected
    # lane/phase pairs, NOT one majority across25 ungrouped raw bits.
    lane_ok=(2<=lane<=14) if diagonal else (0<=lane<17)
    if not (lane_ok and 0<=phase<20 and stride in (1,5)
            and 0<=count<=20):return 0
    y=x+S[q];z=0
    for i in range(count):
        if diagonal:
            values=[]
            for h in range(5):
                chunk,bit=divmod(phase+stride*i+INV[h],20)
                v=vote(cells,y-2+chunk,'mem',(1<<340)-1)
                values.append((v>>(20*(lane+S[h])+bit))&1)
            z|=int(sum(values)>=3)<<i
        else:
            chunk,bit=divmod(phase+stride*i,20)
            v=vote(cells,y-2+chunk,'mem',(1<<340)-1)
            z|=((v>>(20*lane+bit))&1)<<i
    return z&MASK

def execute(h,a,t,read_value,beta):
    """One stationary RUN instruction. Ports/special WRITE are explicit.

    read_value is the already wired generic READ result, not a rule callback.
    WRITE affects Out in a separate literal receiver equation below.
    """
    h=unpack_head(pack_head(h));a&=Q-1;t&=U-1
    if not h.present:return h
    if h.mode!=RUN:return replace(h,present=0,move=0,mode=STOP)
    name,args,n=instruction(beta,h.pc)
    if name in ('HALT','INVALID'):
        return replace(h,present=0,move=0,mode=STOP)
    regs=list(h.regs);pc=(h.pc+n)&(Q-1);r=h.ret;target=h.target
    mode=RUN;present=h.present;move=0
    if name=='LIT':dst,_,v=args;regs[dst]=v
    elif name=='ALU':fn,dst,l,rhs=args;regs[dst]=alu(fn,regs[l],regs[rhs])
    elif name=='ALUR':fn,dst,l,rhs=args;regs[dst]=alu(regs[fn],regs[l],regs[rhs])
    elif name=='BR':cond,l,rhs,to=args;pc=to if branch(cond,regs[l],regs[rhs]) else pc
    elif name in ('READ','READQ'):dst,_,_,_,_=args;regs[dst]=read_value&MASK
    elif name=='WRITE':pass
    elif name=='CODE':dst,index,count=args;regs[dst]=code_word(beta,regs[index],regs[count])
    elif name=='MOVE':(src,)=args;target=regs[src]&(Q-1);mode=TRAVEL
    elif name=='CALL':(to,)=args;r=pc;pc=to
    elif name=='RET':pc=r
    elif name=='GETHEAD':
        dst,selector=args
        regs[dst]=(h.present,h.move,h.mode,h.pc,h.ret,h.target,a,t)[selector]
    elif name=='SETHEAD':
        src,selector=args;v=regs[src]
        if selector==0:present=v&1
        elif selector==1:move=v&3
        elif selector==2:mode=v&3
        elif selector==3:pc=v&(Q-1)
        elif selector==4:r=v&(Q-1)
        elif selector==5:target=v&(Q-1)
        # Native ports selectors6/7 cannot be written by this opcode.
    elif name=='QUORUM':
        kind,dst,fall,*indices=args
        values=[regs[i] for i in indices]
        regs[dst]=(majority5(values)&MASK if kind else equal_quorum(values,regs[fall]))
    else:raise AssertionError(name)
    return Head(present,move,mode,pc,r,target,tuple(v&MASK for v in regs))

def actor(cells,x,q,beta):
    """Total one-cell movement and stationary execution with real votes.

    Holder-centre computedGF plus copy offset determines service Address.
    Self stationary head > incoming left > incoming right is the explicit
    collision priority. Incoming travel packets settle for one tick.
    No reset/birth/active-Age gate is supplied by this component.
    """
    y=x+S[q];a=(cells[x].addr+S[q])&(Q-1);t=cells[x].age&(U-1)
    own=head_vote(cells,y);left=head_vote(cells,y-1);right=head_vote(cells,y+1)
    if own.present and own.mode!=TRAVEL:
        value=0;name,args,_=instruction(beta,own.pc)
        if own.mode==RUN and name in ('READ','READQ'):
            dst,lane,phase,count,st=args
            value=read(cells,x,q,own.regs[lane],own.regs[phase],
                       5 if st else 1,own.regs[count],name=='READQ')
        return execute(own,a,t,value,beta)
    if own.present and own.mode==TRAVEL and own.target==a:
        return replace(own,mode=RUN,move=0)
    if left.present and left.mode==TRAVEL and left.target>((a-1)&(Q-1)):
        return replace(left,mode=RUN if left.target==a else TRAVEL,
                       move=0 if left.target==a else 2)
    if right.present and right.mode==TRAVEL and right.target<((a+1)&(Q-1)):
        return replace(right,mode=RUN if right.target==a else TRAVEL,
                       move=0 if right.target==a else 1)
    return Head()

def write_request(h,beta,cap):
    if not h.present or h.mode!=RUN:return None
    name,args,_=instruction(beta,h.pc)
    if name!='WRITE':return None
    src,phase,count,st=args
    phase=h.regs[phase];count=h.regs[count];stride=5 if st else 1
    if not (0<=phase<20 and 0<=count<=cap):return None
    return (h.regs[src]&MASK,phase,stride,count)

def patches(request,base):
    if request is None:return {}
    data,phase,stride,count=request;out={}
    for i in range(count):
        chunk,bit=divmod(phase+stride*i,20)
        d=base+chunk;mask,value=out.get(d,(0,0))
        mask|=1<<bit;value|=((data>>i)&1)<<bit;out[d]=(mask,value)
    return out

def write_out(cells,x,q,beta,base=0,cap=16):
    """Literal receivers; every collision uses increasing source priority.

    cap16/base0 reads exactly radius8. cap20/base0 is a REJECTED radius9
    interface. cap20/base-2 is an explicit balanced radius7 alternative.
    WRITE eligibility uses OLD stationary Head, not arriving/computed Head.
    """
    assert (base,cap) in ((0,16),(0,20),(-2,20))
    y=x+S[q];value=vote(cells,y,'out',MASK)
    last=(19+5*(cap-1))//20 if cap else 0
    for chunk in range(last,-1,-1):
        z=y-base-chunk
        req=write_request(head_vote(cells,z),beta,cap)
        patch=patches(req,base).get(y-z)
        if patch:
            mask,data=patch;value=(value&~mask)|data
    return value&MASK

def local(cells,x,beta,base=0,cap=16):
    assert len(beta)<=Q and all(b in (0,1) for b in beta)
    hs=tuple(pack_head(actor(cells,x,q,beta)) for q in range(5))
    outs=tuple(write_out(cells,x,q,beta,base,cap) for q in range(5))
    return replace(cells[x],head=hs,out=outs)

def coherent_cell(x,t,heads,memory,outputs):
    return Cell(x%Q,t,
        tuple(pack_head(heads(x+s)) for s in S),
        tuple(memory(x+s)&((1<<340)-1) for s in S),
        tuple(outputs(x+s)&MASK for s in S))
