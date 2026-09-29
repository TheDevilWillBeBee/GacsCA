"""Complete evaluator with local CLEAR/LOAD/META program-record regeneration.

The three added opcodes reuse existing controller registers and phase bits. META
reads ONLY the static record at the head's current cell after a physical scan.
Address is still static here; real maintenance is a separate next integration.
"""
from dataclasses import dataclass,replace
from functools import lru_cache
from . import addressed,communicating
from .circuit import Builder

MEM,GATE,LOOP,SEND,LOAD,CLEAR,META=range(7)
FETCH,READ_A,READ_B,WRITE,TRANSMIT,READ_LOAD,READ_META,WAIT_META=range(8)
RIGHT,LEFT=0,1
SCHEMA=(('kind',3),)+addressed.SCHEMA[1:]
WIDTH=sum(width for _,width in SCHEMA)
STATIC=('kind','index','a','b','d','first','last')
STATIC_SCHEMA=tuple((name,width) for name,width in SCHEMA if name in STATIC)
STATIC_WIDTH=sum(width for _,width in STATIC_SCHEMA)
CONTROL=communicating.CONTROL
NEIGHBORHOOD=(-1,0,1)


@dataclass(frozen=True)
class Cell(addressed.Cell):
    def __post_init__(self):
        for name,width in SCHEMA:
            if not isinstance(getattr(self,name),int) or not 0<=getattr(self,name)<1<<width:
                raise ValueError(f'{name} outside fixed regenerative alphabet')


def encode_cell(cell):
    return tuple((getattr(cell,name)>>i)&1 for name,width in SCHEMA for i in range(width))


def decode_cell(bits):
    if len(bits)!=WIDTH or any(bit not in (0,1) for bit in bits):
        raise ValueError('complete binary regenerative word required')
    values,offset={},0
    for name,width in SCHEMA:
        values[name]=sum(int(bits[offset+i])<<i for i in range(width)); offset+=width
    return Cell(**values)


def static_bit(cell,selector):
    for name,width in STATIC_SCHEMA:
        if selector<width:
            return (getattr(cell,name)>>selector)&1
        selector-=width
    return 0


def fallback_bit(address,selector):
    return (address>>(selector-3))&1 if 3<=selector<19 else 0


def advance(cell):
    out={name:getattr(cell,name) for name in CONTROL[:-1]}
    if cell.phase==FETCH and cell.index==cell.pc:
        if cell.kind in (GATE,SEND):
            out.update(phase=READ_A if cell.kind==GATE else TRANSMIT,ra=cell.a,rb=cell.b,rd=cell.d)
        elif cell.kind==LOOP:
            out['pc']=0
        elif cell.kind==LOAD:
            out.update(phase=READ_LOAD,ra=cell.a)
        elif cell.kind==CLEAR:
            out.update(rd=0,pc=(cell.pc+1)&65535)
        elif cell.kind==META:
            out.update(phase=READ_META,ra=cell.a,rb=cell.b,value=0)
    elif cell.phase==READ_META and cell.value and cell.address==cell.rd:
        out.update(phase=WAIT_META,value=static_bit(cell,cell.rb),rd=cell.ra)
    elif cell.kind==MEM:
        if cell.phase==READ_A and cell.index==cell.ra:
            out.update(value=cell.bit,phase=READ_B)
        elif cell.phase==READ_B and cell.index==cell.rb:
            out.update(value=1-(cell.value&cell.bit),phase=WRITE)
        elif cell.phase==READ_LOAD and cell.index==cell.ra:
            out.update(rd=((cell.rd<<1)|cell.bit)&65535,phase=FETCH,pc=(cell.pc+1)&65535)
        elif ((cell.phase==WRITE and cell.index==cell.rd) or
              (cell.phase==TRANSMIT and cell.index==cell.ra)):
            out.update(phase=FETCH,pc=(cell.pc+1)&65535)
    return out


def reflect_left(cell):
    out={name:getattr(cell,name) for name in CONTROL[:-1]}
    if cell.phase==READ_META:
        if not cell.value:
            out['value']=1  # begin the full lookup pass
        else:
            out.update(value=fallback_bit(cell.rd,cell.rb),rd=cell.ra,phase=WRITE)
    elif cell.phase==WAIT_META:
        out['phase']=WRITE
    return out


def local_step(left,center,right):
    control,head=dict.fromkeys(CONTROL,0),0
    if right.head and right.direction==LEFT and not right.first:
        head,control=1,{name:getattr(right,name) for name in CONTROL}
    if left.head and left.direction==RIGHT and not left.last:
        head,control=1,dict(advance(left),direction=RIGHT)
    if center.head and ((center.direction==RIGHT and center.last) or
                        (center.direction==LEFT and center.first)):
        head=1
        control=advance(center) if center.direction==RIGHT else reflect_left(center)
        control['direction']=1-center.direction
    lp,hit_l,bit_l=communicating.receive(right,center,'lp',right.first)
    rp,hit_r,bit_r=communicating.receive(left,center,'rp',left.last)
    bit=bit_r if hit_r else bit_l if hit_l else center.bit
    if center.head and center.direction==RIGHT and center.kind==MEM:
        if center.phase==WRITE and center.index==center.rd:
            bit=center.value
        if center.phase==TRANSMIT and center.index==center.ra:
            channel,packet=('lp',lp) if center.rd&1 else ('rp',rp)
            packet.update({channel+'_target':center.rb,channel+'_bit':center.bit,
                           channel+'_cross':0,channel+'_valid':1})
    return replace(center,bit=bit,head=head,**control,**lp,**rp)


def step_ring(cells):
    return tuple(local_step(cells[i-1],cell,cells[(i+1)%len(cells)]) for i,cell in enumerate(cells))


@lru_cache(maxsize=1)
def self_description():
    b=Builder(3*WIDTH)
    records,offset=[],2
    for _ in range(3):
        record={}
        for name,width in SCHEMA:
            record[name]=tuple(range(offset,offset+width)); offset+=width
        records.append(record)
    left,center,right=records

    def eq(r,name,value):
        return b.eq(r[name],b.const(value,len(r[name])))

    def any_(*bits):
        out=0
        for bit in bits: out=b.either(out,bit)
        return out

    def condition(r,phase,field):
        return b.both(b.both(eq(r,'kind',MEM),eq(r,'phase',phase)),b.eq(r['index'],r[field]))

    def select_bit(values,selector):
        values=list(values)+[0]*(128-len(values))
        for i in range(7):
            values=[b.mux(selector[i],values[j+1],values[j]) for j in range(0,len(values),2)]
        return b.both(values[0],b.eq(selector[7:],b.const(0,9)))

    def metadata(r):
        return select_bit([wire for name,_ in STATIC_SCHEMA for wire in r[name]],r['rb'])

    def fallback(r):
        return select_bit([0]*3+list(r['rd'])+[0]*50,r['rb'])

    def advanced(r):
        fetch=b.both(eq(r,'phase',FETCH),b.eq(r['index'],r['pc']))
        gate,send,loop,load,clear,meta=(b.both(fetch,eq(r,'kind',kind))
                                     for kind in (GATE,SEND,LOOP,LOAD,CLEAR,META))
        operands=b.either(gate,send)
        a,c,d,sent,loaded=(condition(r,phase,field) for phase,field in
                          ((READ_A,'ra'),(READ_B,'rb'),(WRITE,'rd'),(TRANSMIT,'ra'),(READ_LOAD,'ra')))
        met_read=b.both(eq(r,'phase',READ_META),b.both(r['value'][0],b.eq(r['address'],r['rd'])))
        done=any_(d,sent,loaded,clear)
        result={name:r[name] for name in CONTROL[:-1]}
        result['ra']=b.select(any_(operands,load,meta),r['a'],r['ra'])
        result['rb']=b.select(b.either(operands,meta),r['b'],r['rb'])
        rd=b.select(operands,r['d'],r['rd'])
        rd=b.select(clear,b.const(0,16),rd)
        rd=b.select(loaded,(r['bit'][0],)+r['rd'][:-1],rd)
        result['rd']=b.select(met_read,r['ra'],rd)
        phase=r['phase']
        for predicate,value in ((gate,READ_A),(send,TRANSMIT),(load,READ_LOAD),(meta,READ_META),
                                (a,READ_B),(c,WRITE),(done,FETCH),(met_read,WAIT_META)):
            phase=b.select(predicate,b.const(value,3),phase)
        result['phase']=phase
        result['pc']=b.select(loop,b.const(0,16),b.select(done,b.increment(r['pc']),r['pc']))
        value=b.mux(c,b.nand(r['value'][0],r['bit'][0]),b.mux(a,r['bit'][0],r['value'][0]))
        value=b.mux(meta,0,value)
        result['value']=(b.mux(met_read,metadata(r),value),)
        return result

    def reflected(r):
        scanning=eq(r,'phase',READ_META)
        missing=b.both(scanning,r['value'][0])
        ready=b.both(scanning,b.inv(r['value'][0]))
        write=b.either(missing,eq(r,'phase',WAIT_META))
        result={name:r[name] for name in CONTROL[:-1]}
        result['phase']=b.select(write,b.const(WRITE,3),r['phase'])
        result['rd']=b.select(missing,r['ra'],r['rd'])
        result['value']=(b.mux(missing,fallback(r),b.mux(ready,1,r['value'][0])),)
        return result

    from_left=b.both(left['head'][0],b.both(b.inv(left['direction'][0]),b.inv(left['last'][0])))
    from_right=b.both(right['head'][0],b.both(right['direction'][0],b.inv(right['first'][0])))
    reflect=b.both(center['head'][0],b.mux(center['direction'][0],center['first'][0],center['last'][0]))
    left_control,center_control,left_reflection=advanced(left),advanced(center),reflected(center)
    out=dict(center)
    out['head']=(any_(reflect,from_left,from_right),)
    for name in CONTROL[:-1]:
        value=b.select(from_right,right[name],b.const(0,len(right[name])))
        value=b.select(from_left,left_control[name],value)
        own=b.select(center['direction'][0],left_reflection[name],center_control[name])
        out[name]=b.select(reflect,own,value)
    out['direction']=(b.mux(reflect,b.inv(center['direction'][0]),b.both(b.inv(from_left),from_right)),)
    executing=b.both(center['head'][0],b.inv(center['direction'][0]))
    sending=b.both(executing,condition(center,TRANSMIT,'ra'))
    bit=center['bit'][0]
    for channel,source,edge in (('lp',right,right['first'][0]),('rp',left,left['last'][0])):
        crossed=b.either(source[channel+'_cross'][0],edge)
        valid=b.both(source[channel+'_valid'][0],b.inv(b.both(source[channel+'_cross'][0],edge)))
        hit=b.both(b.both(valid,crossed),b.both(eq(center,'kind',MEM),b.eq(center['index'],source[channel+'_target'])))
        moving=b.both(valid,b.inv(hit))
        bit=b.mux(hit,source[channel+'_bit'][0],bit)
        emit=b.both(sending,center['rd'][0] if channel=='lp' else b.inv(center['rd'][0]))
        for suffix,value,fresh in (('target',source[channel+'_target'],center['rb']),
                                   ('bit',source[channel+'_bit'],center['bit']),
                                   ('cross',(crossed,),(0,)),('valid',(1,),(1,))):
            out[channel+'_'+suffix]=b.select(emit,fresh,b.select(moving,value,b.const(0,len(value))))
    out['bit']=(b.mux(b.both(executing,condition(center,WRITE,'rd')),center['value'][0],bit),)
    return b.finish([wire for name,_ in SCHEMA for wire in out[name]])


def identity():
    return dict(schema=SCHEMA,width=WIDTH,neighborhood=NEIGHBORHOOD,
                description_sha256=self_description().digest())
