"""Bounded exact physical G evolution with shrinking causal-cone storage.

Both actual and comparison states execute the complete local rule. No healthy
state is installed, no fields are dropped, and no simulated transition runs on
the host in place of physical evolution. Storage caps are execution resources.
"""
from functools import lru_cache
import numpy as np
from . import retimed_holder_rule as f,retimed_holder_projected as r,retimed_holder_program as p,retimed_holder_core as c,retimed_holder_native as native
from .retimed_holder_terminal_reference import metadata

RADIUS=7


@lru_cache(maxsize=1)
def rom():
    value=np.array(metadata(),dtype=np.uint64);value.flags.writeable=False;return value


def normalize(array):
    """The fixed G projection: regenerate ROM fields from the actual Address."""
    addresses=array[:,f.COL['address']]
    for offset in f.STATIC_OFFSETS:
        indices=(addresses+(f.Q+offset))%f.Q
        for selector,name in enumerate(c.STATIC):array[:,f.COL[f'p{offset+3}_{name}']]=rom()[indices,selector]
    return array


def step(array):
    if not isinstance(array,np.ndarray) or array.dtype!=np.uint64 or array.ndim!=2 or array.shape[1]!=f.FIELDS or not len(array):raise ValueError('complete raw ring required')
    source=np.ascontiguousarray(array);target=np.empty_like(source)
    native.library().retimed_holder_ring(native.pointer(source),native.pointer(target),len(source))
    return normalize(target)


class BankImage:
    """Read-only complete canonical endpoint image, with inherited scratch."""
    def __init__(self,bank,signals,age=0):
        g=p.layout()
        if not isinstance(bank,np.ndarray) or bank.dtype!=np.uint64 or bank.ndim!=2 or bank.shape[1]!=g.memory_count+5 or not len(bank):raise ValueError('complete canonical bank required')
        if not isinstance(signals,np.ndarray) or signals.dtype!=np.uint64 or signals.shape!=(len(bank),2) or np.any(signals>1):raise ValueError('localized Boolean Signals required')
        if age not in (0,f.U-1):raise ValueError('canonical endpoint clock required')
        self.bank=bank;self.signals=signals;self.age=age;self.size=len(bank)*f.Q
    def cells(self,positions):
        positions=np.asarray(positions,dtype=np.int64)
        if positions.ndim!=1 or len(positions)>65536:raise ValueError('bounded position vector required')
        pos=positions%self.size;col,a=np.divmod(pos,f.Q);g=p.layout();out=np.zeros((len(pos),f.FIELDS),dtype=np.uint64)
        out[:,f.COL['address']]=a;out[:,f.COL['age']]=self.age
        left=(a>=1)&(a<=5);right=a>=f.Q-5
        out[left,f.COL['signal']]=self.signals[col[left],0]<<((5-a[left]).astype(np.uint64))
        out[right,f.COL['signal']]=self.signals[col[right],1]<<((f.Q-1-a[right]).astype(np.uint64))
        for d in f.OFFSETS:
            owner,address=np.divmod((pos+d)%self.size,f.Q);inside=(address<g.memory_count)|(address>=f.Q-5)
            indices=np.where(address<g.memory_count,address,g.memory_count+address-(f.Q-5))
            out[inside,f.COL[f's{d+2}_data']]=self.bank[owner[inside],indices[inside]]
        return normalize(out)


def evolve(initial,changes,*,size,ticks=12,max_cells=8192):
    """Return all retained raw fields; full equality certifies global rejoin.

    Changes use nearby unwrapped integer positions (so -1 and 0 are adjacent).
    The initial interval extends 2*radius*ticks beyond their span. Discarding one
    radius at each edge per tick removes artificial periodic-boundary influence
    while still retaining the entire possible fault cone through the deadline.
    """
    if type(ticks) is not int or not 1<=ticks<=1024 or type(size) is not int or size<1 or type(max_cells) is not int or not 1<=max_cells<=65536:raise ValueError('bounded physical window and duration required')
    changes=dict(changes)
    if not changes or any(type(pos) is not int or not isinstance(cell,r.Cell) for pos,cell in changes.items()):raise ValueError('complete projected physical replacements required')
    lo=min(changes)-2*RADIUS*ticks;hi=max(changes)+2*RADIUS*ticks+1
    if hi-lo>max_cells or hi-lo>size:raise ValueError('causal window exceeds storage or aliases the ring')
    healthy=np.ascontiguousarray(initial(np.arange(lo,hi,dtype=np.int64)))
    if healthy.dtype!=np.uint64 or healthy.shape!=(hi-lo,f.FIELDS):raise ValueError('complete raw initial accessor required')
    for col,(_,width) in enumerate(f.SCHEMA):
        if width<64 and np.any(healthy[:,col]>=(np.uint64(1)<<np.uint64(width))):raise ValueError('initial field exceeds physical width')
    if not np.array_equal(healthy,normalize(healthy.copy())):raise ValueError('initial metadata outside fixed G projection')
    actual=healthy.copy()
    for pos,cell in changes.items():actual[pos-lo]=f.encode_cell(r.lift(cell))
    trace=[]
    for tick in range(1,ticks+1):
        actual=step(actual)[RADIUS:-RADIUS].copy();healthy=step(healthy)[RADIUS:-RADIUS].copy();lo+=RADIUS
        different=actual!=healthy;sites=np.flatnonzero(np.any(different,axis=1));counts=np.count_nonzero(different,axis=0)
        # The retained window contains the full possible cone; differences
        # outside it are forbidden by the declared physical neighborhood.
        for index in sites:
            assert any(abs(int(index)+lo-pos)<=RADIUS*tick for pos in changes),'difference outside causal support'
        trace.append(dict(tick=tick,different_sites=len(sites),different_raw_words=int(np.sum(counts)),fields={name:int(counts[k]) for k,(name,_) in enumerate(f.SCHEMA) if counts[k]}))
        if not len(sites):return dict(rejoined=True,ticks=tick,trace=trace,left=lo,actual=actual,healthy=healthy)
    return dict(rejoined=False,ticks=ticks,trace=trace,left=lo,actual=actual,healthy=healthy)
