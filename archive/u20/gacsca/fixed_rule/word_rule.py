"""Word evaluator coupled to printed Gray maintenance, one fixed radius-five rule.

This revision includes real Address/Age/flag dynamics and computed-Flag1 clearing.
It does not yet implement Gray's five-stage clocked simulation, redundancy or
trickle-down. Those omissions are explicit; Age is already part of the raw rule.
"""
from dataclasses import dataclass,replace
from functools import lru_cache
from .wordcode import Builder,arithmetic,NAND,ADD,SHR,EQ,LT,LIT,MASK

Q=1<<23
U=128*Q
MEM,LOOP,SEND,LOAD,META,WAIT=0,6,7,8,9,10
FETCH,READ_A,READ_B,WRITE,TRANSMIT,READ_LOAD,READ_META,WAIT_META=range(8)
RIGHT,LEFT=0,1
ALU_KINDS=(NAND,ADD,SHR,EQ,LT)
STATIC=('kind','index','a','b','d','first','last')
CONTROL=('phase','pc','ra','rb','rd','value','alu','direction')
SCHEMA=(('kind',4),('index',32),('a',64),('b',64),('d',32),
        ('data',64),('head',1),('phase',3),('pc',32),('ra',32),('rb',64),
        ('rd',64),('value',64),('alu',3),('first',1),('last',1),('direction',1),
        ('lp_target',32),('lp_data',64),('lp_remaining',3),('lp_valid',1),
        ('rp_target',32),('rp_data',64),('rp_remaining',3),('rp_valid',1),
        ('address',23),('age',30),('f1',1),('f2',1),('wf1',1),('wf2',1))
WIDTH=sum(w for _,w in SCHEMA)
FIELDS=len(SCHEMA)
COL={name:i for i,(name,_) in enumerate(SCHEMA)}
NEIGHBORHOOD=tuple(range(-5,6))


@dataclass(frozen=True)
class Cell:
    kind:int=0
    index:int=0
    a:int=0
    b:int=0
    d:int=0
    data:int=0
    head:int=0
    phase:int=0
    pc:int=0
    ra:int=0
    rb:int=0
    rd:int=0
    value:int=0
    alu:int=0
    first:int=0
    last:int=0
    direction:int=0
    lp_target:int=0
    lp_data:int=0
    lp_remaining:int=0
    lp_valid:int=0
    rp_target:int=0
    rp_data:int=0
    rp_remaining:int=0
    rp_valid:int=0
    address:int=0
    age:int=0
    f1:int=0
    f2:int=0
    wf1:int=0
    wf2:int=0

    def __post_init__(self):
        for name,width in SCHEMA:
            value=getattr(self,name)
            if not isinstance(value,int) or not 0<=value<1<<width:
                raise ValueError(f'{name} outside fixed word-rule alphabet')


def encode_cell(cell):return tuple(getattr(cell,n) for n,_ in SCHEMA)


def decode_cell(words):
    if len(words)!=FIELDS:raise ValueError('all raw fields required')
    return Cell(**dict(zip((n for n,_ in SCHEMA),map(int,words))))


def maintenance(cells):
    """Independent scalar transcription, with literal printed Flag2 erasure."""
    c=cells[5];r={j:cells[j+5] for j in range(-5,6)}
    def majority(values,default):
        for candidate in values:
            if values.count(candidate)>=3:return candidate,True
        return default,False
    adjusted={j:(r[j].address-j)%Q for j in (*range(-5,0),*range(1,6))}
    v,exists=majority([adjusted[j] for j in range(1,6)],c.address)
    inside={j:exists and 0<=v+j<Q for j in range(-5,6)}
    age_r,age_exists=majority([r[j].age for j in range(1,6)],c.age)
    age_l,_=majority([r[j].age for j in range(-1,-6,-1)],c.age)
    incons=(not exists or not age_exists or
            sum(inside[j] and r[j].address!=(v+j)%Q for j in range(-1,-6,-1))>=3 or
            sum(inside[j] and r[j].age!=age_r for j in range(-1,-6,-1))>=3)
    flags=sum(inside[j] and r[j].f1 for j in range(1,6))
    f1=int(incons or sum(inside[j] and r[j].wf1 for j in range(-5,6))>=3 or
           flags>=3 or (c.f1 and flags>=2))
    d3=not exists and (age_l+1)%16==0
    d4=sum(inside[j] and r[j].wf2 for j in range(-5,6))>=3
    left_flags=[r[j].f2 for j in range(-1,-6,-1)]
    on=sum(inside[j] and r[j].f2 for j in range(-1,-6,-1))>=4 or (f1 and sum(left_flags)>=4) or d3 or d4
    erase=(not f1 and all(not inside[j] or r[j].f2 for j in range(-1,-6,-1))) or (f1 and not any(left_flags))
    f2=int((d3 or d4 or not erase) if c.f2 else on)
    addr_l,_=majority([adjusted[j] for j in range(-1,-6,-1)],c.address)
    vote_right=exists and (not f1 or f2)
    return dict(address=v if vote_right else addr_l,age=((age_r if vote_right else age_l)+1)%U,f1=f1,f2=f2)


def waiting(c):return c.head and not c.direction and c.phase==FETCH and c.kind==WAIT and c.index==c.pc and c.rd>0


def metadata(c,selector):return getattr(c,STATIC[selector]) if selector<len(STATIC) else 0


def fallback(address,selector):
    return LOOP if selector==0 else address if selector==1 else 0


def advance(c):
    out={name:getattr(c,name) for name in CONTROL[:-1]}
    if c.phase==FETCH and c.index==c.pc:
        if c.kind in ALU_KINDS:
            out.update(phase=READ_A,ra=c.a&0xFFFFFFFF,rb=c.b,rd=c.d,alu=c.kind)
        elif c.kind==SEND:out.update(phase=TRANSMIT,ra=c.a&0xFFFFFFFF,rb=c.b,rd=c.d)
        elif c.kind==LOOP:out['pc']=0
        elif c.kind==LOAD:out.update(phase=READ_LOAD,ra=c.a&0xFFFFFFFF)
        elif c.kind==META:out.update(phase=READ_META,ra=c.a&0xFFFFFFFF,rb=c.b,value=0)
        elif c.kind==WAIT:
            if c.rd:out['rd']=c.rd-1
            else:out['pc']=(c.pc+1)&0xFFFFFFFF
        elif c.kind==LIT:out.update(phase=WRITE,rd=c.d,value=c.a)
    elif c.phase==READ_META and c.value and c.address==c.rd:
        out.update(phase=WAIT_META,value=metadata(c,c.rb),rd=c.ra)
    elif c.kind==MEM:
        if c.phase==READ_A and c.index==c.ra:out.update(phase=READ_B,value=c.data)
        elif c.phase==READ_B and c.index==c.rb:out.update(phase=WRITE,value=arithmetic(c.alu,c.value,c.data))
        elif c.phase==READ_LOAD and c.index==c.ra:out.update(phase=FETCH,rd=c.data,pc=(c.pc+1)&0xFFFFFFFF)
        elif (c.phase==WRITE and c.index==c.rd) or (c.phase==TRANSMIT and c.index==c.ra):
            out.update(phase=FETCH,pc=(c.pc+1)&0xFFFFFFFF)
    return out


def reflect_left(c):
    out={name:getattr(c,name) for name in CONTROL[:-1]}
    if c.phase==READ_META:
        if not c.value:out['value']=1
        else:out.update(phase=WRITE,value=fallback(c.rd,c.rb),rd=c.ra)
    elif c.phase==WAIT_META:out['phase']=WRITE
    return out


def receive(source,c,channel,edge):
    count=getattr(source,channel+'_remaining')
    valid=getattr(source,channel+'_valid') and not(edge and count==0)
    count=count-int(edge and count>0)
    hit=valid and count==0 and c.kind==MEM and c.index==getattr(source,channel+'_target')
    out={channel+'_'+name:0 for name in ('target','data','remaining','valid')}
    if valid and not hit:
        out.update({channel+'_target':getattr(source,channel+'_target'),channel+'_data':getattr(source,channel+'_data'),channel+'_remaining':count,channel+'_valid':1})
    return out,hit,getattr(source,channel+'_data')


def local_step(cells):
    if len(cells)!=11:raise ValueError('exact radius-five neighborhood required')
    left,c,right=cells[4:7];out={name:0 for name in CONTROL};head=0
    if right.head and right.direction and not right.first:
        head=1;out={name:getattr(right,name) for name in CONTROL}
    if left.head and not left.direction and not left.last and not waiting(left):
        head=1;out=dict(advance(left),direction=RIGHT)
    if c.head and ((not c.direction and c.last) or (c.direction and c.first)):
        head=1;out=advance(c) if not c.direction else reflect_left(c);out['direction']=1-c.direction
    if waiting(c):head=1;out=dict(advance(c),direction=RIGHT)
    lp,hit_l,data_l=receive(right,c,'lp',right.address==0)
    rp,hit_r,data_r=receive(left,c,'rp',left.address==Q-1)
    data=data_r if hit_r else data_l if hit_l else c.data
    if c.head and not c.direction and c.kind==MEM:
        if c.phase==WRITE and c.index==c.rd:data=c.value
        if c.phase==TRANSMIT and c.index==c.ra:
            name,packet=('lp',lp) if c.rd&1 else ('rp',rp)
            packet.update({name+'_target':c.rb&0xFFFFFFFF,name+'_data':c.data,name+'_remaining':(c.rd>>1)&7,name+'_valid':1})
    result=replace(c,data=data,head=head,**out,**lp,**rp,**maintenance(cells))
    clear=result.f1 and result.address!=c.address
    updates={}
    if result.f1:
        updates.update({name:0 for name,_ in SCHEMA if name.startswith(('lp_','rp_'))})
    if clear:
        updates.update({name:0 for name in ('data','head',*CONTROL,'wf1','wf2')})
    return replace(result,**updates)


def step_ring(cells):
    return tuple(local_step(tuple(cells[(i+j)%len(cells)] for j in NEIGHBORHOOD)) for i in range(len(cells)))


@lru_cache(maxsize=1)
def self_description():
    # Imported lazily to keep the scalar transition independent of the builder.
    from .word_description import build
    return build()


def identity():return dict(schema=SCHEMA,width=WIDTH,words=FIELDS,neighborhood=NEIGHBORHOOD,Q=Q,U=U,description_sha256=self_description().digest())
