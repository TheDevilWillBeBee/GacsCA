"""GMW0: isolated total radius-five moving-head WORD kernel, native prefix only.

This is an explicitly changed physical primitive, not Gray's complete rule.
Immutable code is beta(raw Address); memory and head are mutable five-copy SF.
No operation calls the whole rule. Native WF outputs are fixed zero here.
"""
from dataclasses import dataclass, replace
from itertools import combinations
import literal_maintenance

Q=8192
U=128*Q
LAMBDA=24
ERROR_SEPARATION=104
WORD=20
MASK=(1<<WORD)-1
SLOTS=(0,-2,-1,1,2)
FETCH,SEEK,LOAD,WRITE,HALT,ERROR=range(6)
LOAD_FIVE,LOAD_CENTRE,LOAD_COLUMN,WRITE_WORD=range(4)
META=(('p',1),('move',2),('mode',3),('pc',13),('ret',13),
      ('buf',29),('count',5),('need',5),('target',13),('width',5),
      ('index',5),('start',13),('kind',2),('dst',4),('side',1))
HEAD_BITS=sum(w for _,w in META)+16*WORD
FRAME_BITS=37+5*HEAD_BITS+5*11+5+5
PRIMARY_START=Q//2-FRAME_BITS//2
NATIVE_COLUMNS={'addr':(PRIMARY_START,13),'age':(PRIMARY_START+13,20),
                'f1':(PRIMARY_START+33,1),'f2':(PRIMARY_START+34,1),
                'wf1':(PRIMARY_START+35,1),'wf2':(PRIMARY_START+36,1)}
ENTRY=PRIMARY_START+64
OP_NAMES=('HLT','NOP','MOV','MOVI','ADD','ADDI','SUB','AND','ANDI','OR',
          'XOR','EQ','NE','LT','LTI','MAJ','WINCNT','BIT','NOT','LOAD5',
          'LOADC','LOADCOL','WRITE','BNZ','JMP','MI5','POPCOUNT','XORI')
OP={name:i for i,name in enumerate(OP_NAMES)}
# Widths of the encoded operands, following the five-bit opcode. Immediate
# arithmetic is in-place; signed immediates are their twenty-bit residues.
ARGS={
 'HLT':(),'NOP':(),'MOV':(4,4),'MOVI':(4,20),'ADD':(4,4,4),
 'ADDI':(4,20),'SUB':(4,4,4),'AND':(4,4,4),'ANDI':(4,20),
 'OR':(4,4,4),'XOR':(4,4,4),'EQ':(4,4,4),'NE':(4,4,4),
 'LT':(4,4,4),'LTI':(4,20),'MAJ':(4,4,4),
 'WINCNT':(4,4,4,4,4,4),'BIT':(4,4,5),'NOT':(4,4),
 'LOAD5':(13,5,1),'LOADC':(4,13,5),'LOADCOL':(4,13),
 'WRITE':(4,13,5),'BNZ':(4,13),'JMP':(13,),
 'MI5':(4,4,4,4,1),'POPCOUNT':(4,4,4,4),'XORI':(4,20)}
LENGTH={OP[name]:5+sum(widths) for name,widths in ARGS.items()}


@dataclass(frozen=True)
class Packet:
    p:int=0;move:int=0;mode:int=0;pc:int=0;ret:int=0
    buf:int=0;count:int=0;need:int=0;target:int=0
    width:int=0;index:int=0;start:int=0;kind:int=0;dst:int=0;side:int=0
    regs:tuple=(0,)*16


ZERO=Packet()


def pack(packet):
    value=0;shift=0
    for name,width in META:
        value|=(getattr(packet,name)&((1<<width)-1))<<shift;shift+=width
    for register in packet.regs:
        value|=(register&MASK)<<shift;shift+=WORD
    return value


def unpack(value):
    values={};shift=0
    for name,width in META:
        values[name]=(value>>shift)&((1<<width)-1);shift+=width
    values['regs']=tuple((value>>(shift+WORD*i))&MASK for i in range(16))
    return Packet(**values)


def vote(values):
    """Bitwise three-of-five, on arbitrarily wide finite words."""
    assert len(values)==5
    return _vote(values)


def _vote(values):
    result=0
    for i,j,k in combinations(range(5),3):result|=values[i]&values[j]&values[k]
    return result


def encode_instruction(name,*args):
    widths=ARGS[name]
    assert len(args)==len(widths)
    value=OP[name];shift=5
    for arg,width in zip(args,widths):
        assert -(1<<(width-1))<=arg<(1<<width)
        value|=(arg&((1<<width)-1))<<shift;shift+=width
    return [(value>>i)&1 for i in range(shift)]


def decode_instruction(value):
    opcode=value&31
    if opcode>=len(OP_NAMES):return None
    name=OP_NAMES[opcode];args=[];shift=5
    for width in ARGS[name]:
        args.append((value>>shift)&((1<<width)-1));shift+=width
    return name,tuple(args)


def signed4(value):return value if value<8 else value-16


def seek(packet,current,target,mode):
    return replace(packet,mode=mode,target=target,
        move=1 if current<target else 2 if current>target else 0)


def fail(packet):return replace(packet,p=1,mode=ERROR,move=0)


def fetch_after(packet,current,pc):
    # Instruction bits are walked, one immutable GF lookup per fetch tick.
    packet=replace(packet,pc=pc&8191,buf=0,count=0,need=0,ret=pc&8191)
    return seek(packet,current,pc&8191,FETCH if current==(pc&8191) else SEEK)


def execute_instruction(packet,current,decoded,nextpc):
    """Generic finite word operations. Returns the next packet, no tape reads."""
    if decoded is None:return fail(packet)
    name,a=decoded;r=list(packet.regs)
    if name=='HLT':return replace(packet,mode=HALT,move=0)
    if name=='NOP':pass
    elif name=='MOV':r[a[0]]=r[a[1]]
    elif name=='MOVI':r[a[0]]=a[1]
    elif name in ('ADDI','ANDI','LTI','XORI'):
        d,v=a
        r[d]={'ADDI':lambda:(r[d]+v)&MASK,'ANDI':lambda:r[d]&v,
              'LTI':lambda:int(r[d]<v),'XORI':lambda:r[d]^v}[name]()
    elif name=='NOT':r[a[0]]=int(not r[a[1]])
    elif name in ('ADD','SUB','AND','OR','XOR','EQ','NE','LT'):
        d,ai,bi=a;av,bv=r[ai],r[bi]
        r[d]={'ADD':lambda:(av+bv)&MASK,'SUB':lambda:(av-bv)&MASK,
          'AND':lambda:av&bv,'OR':lambda:av|bv,'XOR':lambda:av^bv,
          'EQ':lambda:int(av==bv),'NE':lambda:int(av!=bv),
          'LT':lambda:int(av<bv)}[name]()
    elif name=='BIT':r[a[0]]=(r[a[1]]>>a[2])&1 if a[2]<20 else 0
    elif name=='MAJ':
        d,e,default=a;found=None
        for v in r[:5]:
            if r[:5].count(v)>=3:found=v;break
        r[d]=r[default] if found is None else found
        r[e]=int(found is not None) # If d=e, this second write wins.
    elif name in ('WINCNT','POPCOUNT'):
        if name=='WINCNT':d,m,ad,ex,lo,hi=a
        else:d,m,lo,hi=a
        lo,hi=signed4(lo),signed4(hi)
        if not -5<=lo<=hi<=5:return fail(packet)
        r[d]=sum(((r[m]>>(j+5))&1) and
             (name=='POPCOUNT' or (r[ex]!=0 and 0<=r[ad]+j<Q))
             for j in range(lo,hi+1))
    elif name=='MI5':
        d,ref,ad,ex,side=a
        r[d]=sum(r[i]!=r[ref] and r[ex]!=0 and
                 0<=r[ad]+(i+1)*(1 if side else -1)<Q for i in range(5))
    elif name in ('BNZ','JMP'):
        target=a[1] if name=='BNZ' and r[a[0]] else a[0] if name=='JMP' else nextpc
        return fetch_after(replace(packet,regs=tuple(r)),current,target)
    elif name in ('LOAD5','LOADC','LOADCOL','WRITE'):
        if name=='LOAD5':start,width,side=a;dst=0;kind=LOAD_FIVE
        elif name=='LOADC':dst,start,width=a;side=0;kind=LOAD_CENTRE
        elif name=='LOADCOL':dst,start=a;width=1;side=0;kind=LOAD_COLUMN
        else:dst,start,width=a;side=0;kind=WRITE_WORD
        if not 1<=width<=20 or start+width>Q:return fail(packet)
        if kind==LOAD_FIVE:r[:5]=[0]*5
        elif kind!=WRITE_WORD:r[dst]=0
        packet=replace(packet,regs=tuple(r),pc=nextpc&8191,ret=nextpc&8191,
            buf=0,count=0,need=0,start=start,width=width,index=0,
            dst=dst,kind=kind,side=side)
        return seek(packet,current,start,SEEK)
    else:return fail(packet)
    return fetch_after(replace(packet,regs=tuple(v&MASK for v in r)),current,nextpc)


def step_packet(packet,address,mem11,beta):
    """One head tick after migration, at the destination's old raw Address.

    No external input/output port: one current tape column and immutable bit.
    Returns (packet, optional one-bit output-column write).
    """
    if not packet.p:return ZERO,None
    if packet.move==3 or packet.mode>=6:return fail(packet),None
    if packet.mode in (HALT,ERROR):return replace(packet,move=0),None
    if packet.mode==SEEK:
        if address!=packet.target:return seek(packet,address,packet.target,SEEK),None
        if packet.count==0 and packet.need==0 and packet.target==packet.pc:
            packet=replace(packet,mode=FETCH,move=0)
        else:packet=replace(packet,mode=WRITE if packet.kind==WRITE_WORD else LOAD,move=0)
    if packet.mode==FETCH:
        if address!=packet.pc:return seek(packet,address,packet.pc,SEEK),None
        if packet.count>=29 or packet.need>29:return fail(packet),None
        value=packet.buf|((beta[address]&1)<<packet.count);count=packet.count+1
        need=packet.need
        if count==5:
            need=LENGTH.get(value&31,0)
            if not need:return fail(packet),None
        if need and count==need:
            return execute_instruction(packet,address,decode_instruction(value),address+1),None
        if address==Q-1:return fail(packet),None
        return replace(packet,buf=value,count=count,need=need,pc=address+1,move=1),None
    if packet.mode not in (LOAD,WRITE):return fail(packet),None
    if not 1<=packet.width<=20 or packet.start+packet.width>Q or packet.index>=packet.width:
        return fail(packet),None
    target=packet.start+packet.index
    if address!=target:return seek(packet,address,target,SEEK),None
    r=list(packet.regs);write=None
    if packet.mode==WRITE:
        if packet.kind!=WRITE_WORD:return fail(packet),None
        write=(r[packet.dst]>>packet.index)&1
    elif packet.kind==LOAD_FIVE:
        for i in range(5):
            lane=5+(i+1)*(1 if packet.side else -1)
            r[i]|=((mem11>>lane)&1)<<packet.index
    elif packet.kind==LOAD_CENTRE:r[packet.dst]|=((mem11>>5)&1)<<packet.index
    elif packet.kind==LOAD_COLUMN:r[packet.dst]=mem11&2047
    else:return fail(packet),None
    packet=replace(packet,regs=tuple(r),index=packet.index+1)
    if packet.index==packet.width:
        return fetch_after(replace(packet,index=0,width=0),address,packet.ret),write
    return replace(packet,move=1),write


def initial_packet():return Packet(p=1,mode=FETCH,pc=ENTRY,ret=ENTRY,target=ENTRY)


def incoming(packets):
    """Packets voted at logical offsets -1,0,+1, in that order."""
    candidates=[]
    for index in (1,0,2): # deterministic precedence self,left,right
        p=packets[index]
        if p.p and ((index==1 and p.move in (0,3)) or
                    (index==0 and p.move==1) or (index==2 and p.move==2)):
            candidates.append(p)
    if not candidates:return ZERO
    if len(candidates)>1:return fail(candidates[0])
    return candidates[0]


@dataclass(frozen=True)
class Cell:
    addr:int=0;age:int=0;f1:int=0;f2:int=0;wf1:int=0;wf2:int=0
    heads:tuple=(0,)*5;mem:tuple=(0,)*5;out:tuple=(0,)*5;info:tuple=(0,)*5


def local_transition(cells,beta):
    """Closed, all-raw-state, radius-five cell update for the stated primitive.

    cells is indexed -5..5. Every mutable field has finite-width masking.
    Beta is fixed, total, immutable, and has exactly Q binary entries.
    Native workspace outputs zero are an explicit changed component interface.
    """
    assert len(beta)==Q and len(cells)==11
    def native(c):
        return dict(addr=c.addr&8191,age=c.age&MASK,f1=c.f1&1,f2=c.f2&1,
                    wf1=c.wf1&1,wf2=c.wf2&1)
    c=cells[0];computed=literal_maintenance.scalar({j:native(v) for j,v in cells.items()})
    newage=computed['age'];active=112*Q+1<newage<=120*Q
    reset=newage in (0,112*Q);birth=newage==112*Q+1
    wipe=computed['f1'] and computed['addr']!=(c.addr&8191)
    headvalues=[];memvalues=[];outvalues=[];infovalues=[]
    def logical(name,y):
        return vote([getattr(cells[y-s],name)[i] for i,s in enumerate(SLOTS)])
    for slot in SLOTS:
        y=slot;mem=logical('mem',y)&2047;out=logical('out',y)&1
        info=out if newage==0 else logical('info',y)&1
        if reset:head=ZERO;newout=0
        elif birth:
            head=initial_packet() if (cells[y].addr&8191)==ENTRY else ZERO;newout=out
        elif active:
            head=incoming([unpack(logical('heads',y+j)) for j in (-1,0,1)])
            head,write=step_packet(head,cells[y].addr&8191,mem,beta)
            newout=out if write is None else write
        else:head=unpack(logical('heads',y));newout=out
        if wipe:head=ZERO;mem=newout=info=0
        headvalues.append(pack(head));memvalues.append(mem)
        outvalues.append(newout);infovalues.append(info)
    return Cell(computed['addr'],newage,computed['f1'],computed['f2'],0,0,
        tuple(headvalues),tuple(memvalues),tuple(outvalues),tuple(infovalues))


def tape_from_native(cells):
    tape={}
    for field,(start,width) in NATIVE_COLUMNS.items():
        for bit in range(width):
            tape[start+bit]=sum(((cells[j][field]>>bit)&1)<<(j+5) for j in range(-5,6))
    return tape


def native_word_programme():
    """Explicit compact word programme for the literal 35 native outputs only."""
    rows=[]
    def emit(name,*args):rows.append((name,args))
    def label(name):rows.append(('LABEL',(name,)))
    def threshold(reg,n):emit('LTI',reg,n);emit('NOT',reg,reg)
    addr,age,f1,f2,wf1,wf2=(NATIVE_COLUMNS[n][0] for n in ('addr','age','f1','f2','wf1','wf2'))
    emit('LOADC',12,addr,13);emit('LOADC',13,age,20)
    emit('LOAD5',addr,13,1)
    for i in range(5):emit('ADDI',i,-i-1);emit('ANDI',i,8191)
    emit('MAJ',6,7,12)
    emit('LOAD5',age,20,1);emit('MAJ',8,9,13)
    emit('NOT',14,7);emit('NOT',5,9);emit('OR',14,14,5)
    emit('LOAD5',addr,13,0)
    for i in range(5):emit('ADDI',i,i+1);emit('ANDI',i,8191)
    emit('MAJ',10,5,12);emit('MI5',5,6,6,7,0);threshold(5,3);emit('OR',14,14,5)
    emit('LOAD5',age,20,0);emit('MAJ',11,5,13)
    emit('MI5',5,8,6,7,0);threshold(5,3);emit('OR',14,14,5)
    emit('LOADCOL',0,f1);emit('LOADCOL',1,f2);emit('LOADCOL',2,wf1);emit('LOADCOL',3,wf2)
    emit('WINCNT',4,0,6,7,1,5);emit('MOV',5,4);threshold(5,3);emit('OR',14,14,5)
    emit('BIT',5,0,5);threshold(4,2);emit('AND',5,5,4);emit('OR',14,14,5)
    emit('WINCNT',4,2,6,7,-5,5);threshold(4,3);emit('OR',14,14,4)
    emit('NOT',4,7);emit('MOV',5,11);emit('ADDI',5,1);emit('ANDI',5,15)
    emit('LTI',5,1);emit('AND',4,4,5) # source3
    emit('WINCNT',9,3,6,7,-5,5);threshold(9,3) # source4
    emit('WINCNT',15,1,6,7,-5,-1);threshold(15,4)
    emit('POPCOUNT',5,1,-5,-1);threshold(5,4);emit('AND',5,5,14)
    emit('OR',15,15,5);emit('OR',15,15,4);emit('OR',15,15,9)
    emit('MOV',5,1);emit('XORI',5,2047);emit('WINCNT',5,5,6,7,-5,-1)
    emit('LTI',5,1);emit('NOT',2,14);emit('AND',5,5,2) # printed erase(a)
    emit('POPCOUNT',3,1,-5,-1);emit('LTI',3,1);emit('AND',3,3,14)
    emit('OR',5,5,3);emit('NOT',5,5);emit('OR',5,5,4);emit('OR',5,5,9)
    emit('BIT',3,1,5);emit('BNZ',3,'keep');emit('JMP','afterkeep')
    label('keep');emit('MOV',15,5);label('afterkeep')
    emit('NOT',2,14);emit('OR',2,2,15);emit('AND',2,2,7);emit('BNZ',2,'right')
    emit('MOV',6,10);emit('MOV',8,11);label('right');emit('ADDI',8,1)
    emit('WRITE',6,addr,13);emit('WRITE',8,age,20)
    emit('WRITE',14,f1,1);emit('WRITE',15,f2,1);emit('HLT')
    labels={};cursor=ENTRY
    for name,args in rows:
        if name=='LABEL':labels[args[0]]=cursor
        else:cursor+=5+sum(ARGS[name])
    assert cursor<Q
    beta=[0]*Q;listing=[];cursor=ENTRY
    for name,args in rows:
        if name=='LABEL':continue
        args=tuple(labels[a] if isinstance(a,str) else a for a in args)
        bits=encode_instruction(name,*args)
        beta[cursor:cursor+len(bits)]=bits
        encoded_value=sum(bit<<i for i,bit in enumerate(bits))
        listing.append(dict(address=cursor,opcode=name,
                            operands=list(decode_instruction(encoded_value)[1]),bits=len(bits)))
        cursor+=len(bits)
    return tuple(beta),listing,labels


def abstract_execute(beta,tape,limit=65536,record=False):
    """Same emitted physical head step, one logical head in a quiet colony."""
    address=ENTRY;packet=initial_packet();out={};history=[]
    for tick in range(limit):
        address+=1 if packet.move==1 else -1 if packet.move==2 else 0
        if not 0<=address<Q:raise AssertionError('head left colony')
        before=packet
        packet,write=step_packet(packet,address,tape.get(address,0),beta)
        if write is not None:out[address]=write
        if record:history.append((address,before,packet,write))
        if packet.mode in (HALT,ERROR):return out,tick+1,packet,history
    raise AssertionError('programme exceeded fifth-stage budget')


def native_output(out):
    return {field:sum(out.get(start+b,0)<<b for b in range(width))
            for field,(start,width) in NATIVE_COLUMNS.items() if field not in ('wf1','wf2')}
