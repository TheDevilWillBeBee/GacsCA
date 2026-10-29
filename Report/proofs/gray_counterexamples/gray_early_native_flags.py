"""GE0: an isolated early native-flag prefix attached to frozen GT0.

This is a new component, not Gray's own beta or a full self-simulating CA.
Its only emitted programme evaluates the literal 35 native outputs. LOAD
reads the actual three retained GT0 histories, and two finite speed-one
couriers deliver the two output flags. Native Workspace and fifth-stage
stores remain explicit integration ports, with the printed Workspace
window enforced. Every raw component/port input has a defined evaluation.
"""
from dataclasses import dataclass
from types import FunctionType
import gray_moving_word_kernel as head
import gray_raw_gather as gather
import literal_maintenance

Q=8192
U=128*Q
LAMBDA=24
ERROR_SEPARATION=104
SLOTS=head.SLOTS
HEAD_BITS=head.HEAD_BITS
FRAME_SCHEMA=(('addr',13),('age',20),('f1',1),('f2',1),('wf1',1),('wf2',1))+tuple(
    (name,5*width) for name,width in gather.FIELDS)+(
    ('heads',5*HEAD_BITS),('early_out',5),('courierL',5),('courierR',5))
FRAME_BITS=sum(width for _,width in FRAME_SCHEMA)
PRIMARY_START=Q//2-FRAME_BITS//2
NATIVE_COLUMNS={'addr':(PRIMARY_START,13),'age':(PRIMARY_START+13,20),
    'f1':(PRIMARY_START+33,1),'f2':(PRIMARY_START+34,1),
    'wf1':(PRIMARY_START+35,1),'wf2':(PRIMARY_START+36,1)}
ENTRY=PRIMARY_START+64
RESET=69*Q+3
BIRTH=RESET+1
SEED=75*Q
LEFT_DISTANCE=NATIVE_COLUMNS['f2'][0]-3
RIGHT_DISTANCE=Q-3-NATIVE_COLUMNS['f1'][0]
WIDTHS=dict(gather.FIELDS)
ZERO_DATA=tuple((0,)*(5*w) for _,w in gather.FIELDS)


def native_programme():
    """Emit an actual bit programme, using only frozen generic instructions.

    Relocation changes the declared layout, not the frozen emitter's global
    namespace. The other Q-code bits are zero in this emitted example; a
    putative future own programme may fill any bits outside this interval.
    """
    namespace=dict(head.native_word_programme.__globals__)
    namespace.update(NATIVE_COLUMNS=NATIVE_COLUMNS,ENTRY=ENTRY)
    return FunctionType(head.native_word_programme.__code__,namespace)()


def initial_packet():
    return head.Packet(p=1,mode=head.FETCH,pc=ENTRY,ret=ENTRY,target=ENTRY)


def layout():
    tags=[(name,bit) for name,width in FRAME_SCHEMA for bit in range(width)]
    return {tag:PRIMARY_START+i for i,tag in enumerate(tags)}


@dataclass(frozen=True)
class Cell:
    addr:int=0;age:int=0;f1:int=0;f2:int=0;wf1:int=0;wf2:int=0
    data:tuple=ZERO_DATA
    heads:tuple=(0,)*5
    early_out:tuple=(0,)*5
    courierL:tuple=(0,)*5
    courierR:tuple=(0,)*5


def native_word(c):
    return dict(addr=c.addr&8191,age=c.age&head.MASK,f1=c.f1&1,
        f2=c.f2&1,wf1=c.wf1&1,wf2=c.wf2&1)


def local_transition(cells,beta,workspace_ports=(0,0),fifth_store_ports=None):
    """Total radius-five finite COMPONENT transition with declared ports.

    cells[-5..5] contain the actual old raw holders. The only programme
    lookup is beta(cells[y].raw_GF), never an upper-rule call. Two late
    Workspace outputs and five final stores remain arbitrary finite ports.
    Their inactivity before96Q is enforced, not supplied as an early oracle.
    """
    assert len(cells)==11 and len(beta)==Q
    fifth_store_ports={} if fifth_store_ports is None else fifth_store_ports
    computed=literal_maintenance.scalar({j:native_word(c) for j,c in cells.items()})
    address,age,flag1=computed['addr'],computed['age'],computed['f1']
    wipe=bool(flag1 and address!=(cells[0].addr&8191))

    cache={}
    def value(y,field,bit=0):
        key=y,field,bit
        if key in cache:return cache[key]
        if field in WIDTHS:
            index=list(WIDTHS).index(field);width=WIDTHS[field]
            values=[(cells[y-s].data[index][i*width+bit]&1)
                for i,s in enumerate(SLOTS)]
        else:
            mask=(1<<HEAD_BITS)-1 if field=='heads' else 1
            values=[getattr(cells[y-s],field)[i]&mask for i,s in enumerate(SLOTS)]
        cache[key]=head.vote(values)
        return cache[key]

    def temporal_input(y):
        result=0
        for bit in range(11):
            a,b,c=(value(y,'history'+str(i),bit) for i in (1,2,3))
            result|=((a&b)|(c&(a|b)))<<bit
        return result

    flag2_result=value(3-address,'courierL') if 1<=address<=5 else 0
    flag1_result=value(Q-3-address,'courierR') if Q-5<=address<Q else 0
    data=[]
    for field,width in gather.FIELDS:
        bits=[]
        for slot in SLOTS:
            for bit in range(width):
                route=gather.scalar_plan(age,address,slot,field,bit)
                name=route[0]
                if name=='zero':v=0
                elif name=='flag1_port':v=flag1_result
                elif name=='flag2_port':v=flag2_result
                elif name=='majority3':
                    a,b,c=(value(r[1],r[0],r[2]) for r in route[1:])
                    v=(a&b)|(c&(a|b))
                elif name=='write_port':
                    enable,output=fifth_store_ports.get(slot,(0,0))
                    v=(output&1) if enable&1 else value(slot,field,bit)
                else:v=value(route[1],name,route[2])
                if field in ('mailL','mailR') and flag1:v=0
                bits.append(0 if wipe else v)
        data.append(tuple(bits))

    heads=[];outs=[];left=[];right=[]
    for slot in SLOTS:
        oldout=value(slot,'early_out')
        if age==RESET:p,newout=head.ZERO,0
        elif age==BIRTH:
            p=initial_packet() if (cells[slot].addr&8191)==ENTRY else head.ZERO
            newout=oldout
        elif BIRTH<age<SEED:
            p=head.incoming([head.unpack(value(slot+j,'heads')) for j in (-1,0,1)])
            p,write=head.step_packet(p,cells[slot].addr&8191,temporal_input(slot),beta)
            newout=oldout if write is None else write
        else:p=head.unpack(value(slot,'heads'));newout=oldout
        service=(address+slot)%Q
        ls,rs=value(slot,'courierL'),value(slot,'courierR')
        if age==RESET:ls=rs=0
        elif age==SEED:
            ls=oldout if service==NATIVE_COLUMNS['f2'][0] else 0
            rs=oldout if service==NATIVE_COLUMNS['f1'][0] else 0
        else:
            if SEED<age<=SEED+LEFT_DISTANCE:ls=value(slot+1,'courierL')
            if SEED<age<=SEED+RIGHT_DISTANCE:rs=value(slot-1,'courierR')
        if wipe:p,newout,ls,rs=head.ZERO,0,0,0
        heads.append(head.pack(p));outs.append(newout);left.append(ls);right.append(rs)
    wf1,wf2=workspace_ports if 96*Q<=age<98*Q else (0,0)
    return Cell(address,age,flag1,computed['f2'],wf1&1,wf2&1,
        tuple(data),tuple(heads),tuple(outs),tuple(left),tuple(right))


def tape_from_native(cells):
    return {start+bit:sum(((cells[j][field]>>bit)&1)<<(j+5) for j in range(-5,6))
        for field,(start,width) in NATIVE_COLUMNS.items() for bit in range(width)}


def execute(beta,tape,record=False):
    position=ENTRY;packet=initial_packet();out={};trace=[]
    for tick in range(SEED-BIRTH-1):
        position+=1 if packet.move==1 else -1 if packet.move==2 else 0
        assert 0<=position<Q
        before=packet
        packet,write=head.step_packet(packet,position,tape.get(position,0),beta)
        if write is not None:out[position]=write
        if record:trace.append((position,before,packet,write))
        if packet.mode in (head.HALT,head.ERROR):return out,tick+1,packet,trace
    raise AssertionError('early programme missed SEED deadline')


def native_output(out):
    return {field:sum(out.get(start+bit,0)<<bit for bit in range(width))
        for field,(start,width) in NATIVE_COLUMNS.items() if field not in ('wf1','wf2')}
