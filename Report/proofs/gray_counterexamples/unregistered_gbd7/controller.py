"""GBD7 explicitly changed generic absolute-access/vector binary ISA.

All raw Head204 states have a finite local transition. Absolute access is
multi-update travel followed by a LOCAL read/write, never a remote syscall.
The opcode equations are generic word/bit operations, not native/full-R.
"""
from pathlib import Path
import importlib.util,sys
from dataclasses import replace

BASE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('gbd7_old_cpu',BASE/'unregistered_gbd4/controller.py')
old=importlib.util.module_from_spec(spec);sys.modules[spec.name]=old;spec.loader.exec_module(old)
Q=old.Q;U=old.U;MASK=old.MASK;S=old.S;INV=old.INV;WORD=20;P=2403
Head=old.Head;Cell=old.Cell;HEAD_BITS=old.HEAD_BITS;HEAD_FIELDS=old.HEAD_FIELDS
pack_head=old.pack_head;unpack_head=old.unpack_head
majority5=old.majority5;equal_quorum=old.equal_quorum
alu=old.alu;branch=old.branch;code_word=old.code_word;take=old.take
vote=old.vote;head_vote=old.head_vote;read=old.read;patches=old.patches
coherent_cell=old.coherent_cell;ALU_NAMES=old.ALU_NAMES
RUN,TRAVEL,READ_PENDING,WRITE_PENDING=range(4)
OPS={'HALT':0,'LIT':1,'ALU':2,'BR':3,'READ':4,'WRITE':5,'CODE':6,
     'MOVE':7,'CALL':8,'RET':9,'GETHEAD':10,'SETHEAD':11,
     'ALUR':12,'QUORUM':13,'VECTOR':14,'FIELD':15}
SHAPES={0:(),1:(3,5),2:(5,3,3,3),3:(3,3,3,13),
    4:(3,3,3,3,1,1),5:(3,3,3,1),6:(3,3,3),7:(3,),
    8:(13,),9:(),10:(3,3),11:(3,3),12:(3,3,3,3),
    13:(2,3,3,3,3,3,3,3),14:(5,3,3,3,2),15:(2,3,3,3,1,1)}

def instruction(beta,pc):
    pc&=Q-1;op=take(beta,pc,4)
    if op is None:return ('INVALID',(),0)
    at=pc+4;args=[]
    for width in SHAPES[op]:
        value=take(beta,at,width)
        if value is None:return ('INVALID',(),0)
        args.append(value);at+=width
    if op==1:
        width=args[1]
        if width>20:return ('INVALID',(),0)
        value=take(beta,at,width)
        if value is None:return ('INVALID',(),0)
        args.append(value);at+=width
    return (tuple(OPS)[op],tuple(args),at-pc)

def encode(name,*args):
    op=OPS[name];widths=SHAPES[op]+((args[1],) if op==1 else ())
    assert len(args)==len(widths)
    result=[(op>>i)&1 for i in range(4)]
    for value,width in zip(args,widths):
        assert 0<=value<(1<<width) if width else value==0
        result.extend((value>>i)&1 for i in range(width))
    return tuple(result)

def field_plan(h,beta):
    name,args,size=instruction(beta,h.pc)
    if name!='FIELD':return None
    kind,data,descriptor,lane,st,bank=args
    word=h.regs[descriptor]&MASK
    if bank:
        base=word&(Q-1);count=(word>>13)&31;phase=0;target=(base+2)%Q
    else:
        base=word&4095;count=(word>>12)&31;phase=base%20
        target=(P+2+base//20)%Q
    return dict(kind=kind,data=data,descriptor=descriptor,lane=h.regs[lane]&MASK,
        stride=5 if st else 1,bank=bank,base=base,count=count,phase=phase,
        target=target,size=size)

def field_values(cells,x,q,h,beta):
    plan=field_plan(h,beta)
    if plan is None:return (0,)*5
    k=plan['kind'];bank=plan['bank'];count=plan['count'];lane=plan['lane']
    phase=plan['phase'];stride=plan['stride']
    if not 0<=count<=20:return (0,)*5
    if k==0:
        return (read(cells,x,q,0 if bank else lane,phase,stride,count,False,bank),0,0,0,0)
    if k==1:
        return ((0 if bank else read(cells,x,q,lane,phase,stride,count,True,0)),0,0,0,0)
    if k==3:
        if bank:
            # Five consecutive Out words. Forced stride1/phase0 is part of
            # the total opcode; retaining stride5 here would exceed radius8.
            return tuple(read(cells,x+i,q,0,0,1,count,False,1) for i in range(5))
        return tuple(read(cells,x,q,lane+i,phase,stride,count,False,0) for i in range(5))
    return (0,)*5

def quorum(kind,values,fallback):
    values=tuple(v&MASK for v in values)
    if kind==0:
        for value in values:
            if sum(value==v for v in values)>=3:return value,1
        return fallback&MASK,0
    if kind==1:return majority5(values)&MASK,0
    if kind==2:return sum(values)&MASK,0
    return sum((value&1)<<i for i,value in enumerate(values)),0

def execute(h,a,t,value,beta):
    h=unpack_head(pack_head(h));a&=Q-1;t&=U-1
    if not h.present:return h
    if h.mode!=RUN:return replace(h,present=0,move=0)
    name,args,size=instruction(beta,h.pc)
    if name in ('HALT','INVALID'):return replace(h,present=0,move=0,mode=RUN)
    regs=list(h.regs);pc=(h.pc+size)&(Q-1);link=h.ret;target=h.target
    mode=RUN;present=h.present;move=0
    if name=='LIT':dst,_,v=args;regs[dst]=v
    elif name=='ALU':fn,dst,l,r=args;regs[dst]=alu(fn,regs[l],regs[r])
    elif name=='ALUR':fn,dst,l,r=args;regs[dst]=alu(regs[fn],regs[l],regs[r])
    elif name=='BR':cond,l,r,to=args;pc=to if branch(cond,regs[l],regs[r]) else pc
    elif name=='READ':regs[args[0]]=value&MASK
    elif name=='WRITE':pass
    elif name=='CODE':dst,index,count=args;regs[dst]=code_word(beta,regs[index],regs[count])
    elif name=='MOVE':target=regs[args[0]]&(Q-1);mode=TRAVEL
    elif name=='CALL':link=pc;pc=args[0]
    elif name=='RET':pc=link
    elif name=='GETHEAD':
        dst,selector=args
        regs[dst]=(h.present,h.move,h.mode,h.pc,h.ret,h.target,a,t)[selector]
    elif name=='SETHEAD':
        source,selector=args;v=regs[source]
        if selector==0:present=v&1
        elif selector==1:move=v&3
        elif selector==2:mode=v&3
        elif selector==3:pc=v&(Q-1)
        elif selector==4:link=v&(Q-1)
        elif selector==5:target=v&(Q-1)
    elif name=='QUORUM':
        kind,dst,fall,*indices=args
        v,status=quorum(kind,[regs[i] for i in indices],regs[fall])
        regs[dst]=v;regs[(dst+1)%8]=status
    elif name=='VECTOR':
        fn,dst,source,scalar,operand=args
        result=[]
        for i in range(5):
            b=regs[scalar] if operand==0 else (regs[scalar]+i)&MASK if operand==1 else (
                (regs[scalar]>>i)&1 if operand==2 else 0)
            result.append(alu(fn,regs[(source+i)%8],b))
        for i,v in enumerate(result):regs[(dst+i)%8]=v
    elif name=='FIELD':
        plan=field_plan(h,beta);target=plan['target'];pc=h.pc
        mode=WRITE_PENDING if plan['kind']==2 else READ_PENDING
    else:raise AssertionError(name)
    return Head(present,move,mode,pc,link,target,tuple(v&MASK for v in regs))

def finish(h,a,t,values,beta):
    plan=field_plan(h,beta)
    if plan is None or plan['target']!=h.target or a!=h.target:
        return replace(h,present=0,move=0,mode=RUN)
    if (h.mode==WRITE_PENDING)!=(plan['kind']==2):
        return replace(h,present=0,move=0,mode=RUN)
    regs=list(h.regs)
    if plan['kind']!=2:
        count=5 if plan['kind']==3 else 1
        for i in range(count):regs[(plan['data']+i)%8]=values[i]&MASK
    return replace(h,mode=RUN,move=0,pc=(h.pc+plan['size'])&(Q-1),regs=tuple(regs))

def actor(cells,x,q,beta):
    y=x+S[q];a=(cells[x].addr+S[q])&(Q-1);t=cells[x].age&(U-1)
    own=head_vote(cells,y);left=head_vote(cells,y-1);right=head_vote(cells,y+1)
    if own.present and own.mode==RUN:
        value=0;name,args,_=instruction(beta,own.pc)
        if name=='READ':
            dst,lane,phase,count,st,bank=args
            value=read(cells,x,q,own.regs[lane],own.regs[phase],
                5 if st else 1,own.regs[count],False,bank)
        return execute(own,a,t,value,beta)
    if own.present and own.target==a:
        if own.mode==TRAVEL:return replace(own,mode=RUN,move=0)
        return finish(own,a,t,field_values(cells,x,q,own,beta),beta)
    if left.present and left.mode!=RUN and left.target>((a-1)&(Q-1)):
        return replace(left,move=0 if left.target==a else 2)
    if right.present and right.mode!=RUN and right.target<((a+1)&(Q-1)):
        return replace(right,move=0 if right.target==a else 1)
    return Head()

def write_request(h,beta,a,cap=20):
    if not h.present:return None
    name,args,_=instruction(beta,h.pc)
    if h.mode==RUN and name=='WRITE':
        src,phase,count,st=args
        phase=h.regs[phase];count=h.regs[count];stride=5 if st else 1
    elif h.mode==WRITE_PENDING:
        plan=field_plan(h,beta)
        if plan is None or plan['kind']!=2 or plan['target']!=h.target or a!=h.target:return None
        src=plan['data'];phase=plan['phase'];count=plan['count'];stride=plan['stride']
    else:return None
    if not (0<=phase<20 and 0<=count<=cap):return None
    return (h.regs[src]&MASK,phase,stride,count)

def write_out(cells,x,q,beta,base=-2,cap=20):
    assert (base,cap)==(-2,20)
    y=x+S[q];a=(cells[x].addr+S[q])&(Q-1);value=vote(cells,y,'out',MASK)
    last=(19+5*(cap-1))//20
    for chunk in range(last,-1,-1):
        z=y+2-chunk;req=write_request(head_vote(cells,z),beta,(a+2-chunk)%Q,cap)
        patch=patches(req,base).get(y-z)
        if patch:
            mask,data=patch;value=(value&~mask)|data
    return value&MASK

def local(cells,x,beta,base=-2,cap=20):
    assert len(beta)<=Q and all(b in (0,1) for b in beta)
    return replace(cells[x],head=tuple(pack_head(actor(cells,x,q,beta)) for q in range(5)),
        out=tuple(write_out(cells,x,q,beta,base,cap) for q in range(5)))
