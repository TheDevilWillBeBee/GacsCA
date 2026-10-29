"""GBD3 NEW K3387 packing/reset block, not a complete cellular automaton.

Computed native Address/Age are DECLARED INPUT PORTS, not a host callback.
No native update, full own programme, Head, gather or flag rule is supplied.
The block itself has total finite semantics for every port and raw SF value.
"""
from dataclasses import dataclass, replace
from itertools import combinations

Q=8192
U=128*Q
AGE_MASK=U-1
from layout import K
P=Q//2-K//2
WIDTH=20
LANES=17
DATA_BITS=WIDTH*LANES
DATA_MASK=(1<<DATA_BITS)-1
TAG_MASK=Q-1
HISTORY_MASK=(1<<LANES)-1
SLOTS=(0,-2,-1,1,2)
INV=(0,4,3,2,1)
CHUNKS=(K+WIDTH-1)//WIDTH
SEED=72*Q+3
MERGE_LAST=SEED+19
LOAD=SEED+20


def source(h):return P+20*h+min(20,K-20*h)-1
def destination(h):return P+h


MAX_TRAVEL=max(source(h)-destination(h) for h in range(CHUNKS))
DONE=LOAD+MAX_TRAVEL
assert (K,P,CHUNKS,MAX_TRAVEL,DONE)==(3387,2403,170,3217,593064)


def majority5(values):
    z=0
    for a,b,c in combinations(values,3):z|=a&b&c
    return z


def majority3(a,b,c):return (a&b)|(a&c)|(b&c)


@dataclass(frozen=True)
class Packet:
    data:int=0
    tag:int=0
    valid:int=0


ZERO=Packet()


@dataclass(frozen=True)
class Cell:
    # These are the centre's already computed native output ports.
    addr:int=0
    age:int=0
    history:tuple=((0,)*5,)*3
    data:tuple=(0,)*5
    tag:tuple=(0,)*5
    valid:tuple=(0,)*5


def packet_vote(cells,y):
    def f(name,mask):
        return majority5([getattr(cells[y+s],name)[INV[h]]
                          for h,s in enumerate(SLOTS)])&mask
    return Packet(f('data',DATA_MASK),f('tag',TAG_MASK),f('valid',1))


def history_vote(cells,y,bank):
    return majority5([cells[y+s].history[bank][INV[h]]
                      for h,s in enumerate(SLOTS)])&HISTORY_MASK


def seed_data(bits,phase):
    return sum(((bits>>lane)&1)<<(20*lane+phase) for lane in range(17))


def final_chunk_mask(h):
    n=min(20,K-20*h)
    return sum(((1<<n)-1)<<(20*lane) for lane in range(17))


def stage_action(a,t,own,left,right,temporal):
    """Generic deterministic finite controller after literal raw voting.

    Both control ports are masked to their fixed widths.  Every malformed
    tag, collision and outside-frame input has explicit behaviour.
    No data-dependent remote fetch/host simulation occurs here.
    """
    a&=Q-1;t&=AGE_MASK
    i=a-P
    inside=0<=i<K
    if t==SEED:
        return Packet(seed_data(temporal,i%20),i//20,1) if inside else ZERO
    if SEED<t<=MERGE_LAST:
        if not inside:return ZERO
        data=own.data
        if own.valid and left.valid and own.tag==left.tag:
            data|=left.data
        return Packet(data&DATA_MASK,own.tag&TAG_MASK,own.valid&1)
    if t==LOAD:
        if not inside or not (i%20==19 or i==K-1):return ZERO
        h=i//20
        if not own.valid or own.tag!=h:return ZERO
        return Packet(own.data&final_chunk_mask(h),h,1)
    if LOAD<t<=DONE:
        if not inside:return ZERO
        hold=(own.valid and 0<=own.tag<CHUNKS and a==destination(own.tag))
        ra=(a+1)&(Q-1)
        incoming=(right.valid and 0<=right.tag<CHUNKS and
                  P<=ra<P+K and ra>destination(right.tag))
        if hold and incoming:return ZERO  # fully specified collision
        if incoming:return Packet(right.data&DATA_MASK,right.tag&TAG_MASK,1)
        if hold:return Packet(own.data&DATA_MASK,own.tag&TAG_MASK,1)
        return ZERO
    return Packet(own.data&DATA_MASK,own.tag&TAG_MASK,own.valid&1)


def local(cells,x):
    """Literal raw-slot block: all accessed physical offsets are<=5.

    Copy role q at x represents logical y=x+S[q].  Its control Address is
    (computed centre native Address+S[q]) modQ, not source's computed field.
    This explicitly declared interface is quiet-coherent in the theorem;
    damaged-control refinement and native composition are unproved.
    """
    packets=[]
    for q,s in enumerate(SLOTS):
        y=x+s
        own=packet_vote(cells,y)
        left=packet_vote(cells,y-1)
        right=packet_vote(cells,y+1)
        hs=[history_vote(cells,y,k) for k in range(3)]
        temporal=majority3(*hs)&HISTORY_MASK
        packets.append(stage_action((cells[x].addr+s)&(Q-1),cells[x].age,
                                    own,left,right,temporal))
    return replace(cells[x],data=tuple(v.data for v in packets),
                   tag=tuple(v.tag for v in packets),
                   valid=tuple(v.valid for v in packets))


def coherent_cell(x,t,packets,histories):
    """Real copy convention; arbitrary coherent packet/history functions."""
    ps=[packets(x+s) for s in SLOTS]
    return Cell(addr=x%Q,age=t,
                history=tuple(tuple(histories(bank,x+s)&HISTORY_MASK
                                    for s in SLOTS) for bank in range(3)),
                data=tuple(p.data for p in ps),tag=tuple(p.tag for p in ps),
                valid=tuple(p.valid for p in ps))
