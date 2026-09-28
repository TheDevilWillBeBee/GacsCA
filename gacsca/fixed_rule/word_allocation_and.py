"""Compile-time result-storage reuse for the fixed rule's expression DAG.

No evolving state is interpreted here. The resulting addresses are hard-wired
into ordinary local READ/WRITE instructions. Inputs have separate fixed storage;
outputs and explicit pins remain live after the last expression operation.
"""
from dataclasses import dataclass
from bisect import bisect_left, insort
from .wordcode_and import LIT, NAND, ADD, SHR, EQ, LT, AND, MASK


@dataclass(frozen=True)
class Allocation:
    slots: tuple
    count: int
    pins: tuple
    descriptor_sha256: str


def last_uses(program, pins=()):
    if not isinstance(program.inputs,int) or program.inputs<0:
        raise ValueError('nonnegative input count required')
    last=[-1]*program.wires
    for i,(op,a,b) in enumerate(program.operations):
        wire=program.inputs+i
        if op==LIT:
            if not isinstance(a,int) or not 0<=a<=MASK or b!=0:
                raise ValueError('canonical unsigned literal required')
        elif op in (NAND,ADD,SHR,EQ,LT,AND):
            for operand in (a,b):
                if not isinstance(operand,int) or not 0<=operand<wire:
                    raise ValueError('ordered expression DAG required')
                last[operand]=i
        else:raise ValueError('unsupported fixed word operation')
    for wire in (*program.outputs,*pins):
        if not isinstance(wire,int) or not 0<=wire<program.wires:
            raise ValueError('invalid retained wire')
        last[wire]=len(program.operations)
    return last


def verify(program, allocation):
    """Symbolic owner certificate: no live operand/output can be overwritten."""
    last_uses(program,allocation.pins)
    if allocation.descriptor_sha256!=program.digest() or len(allocation.slots)!=len(program.operations):
        raise ValueError('allocation belongs to a different complete description')
    if not isinstance(allocation.count,int) or allocation.count<0:
        raise ValueError('invalid storage size')
    if any(not isinstance(s,int) or not 0<=s<allocation.count for s in allocation.slots):
        raise ValueError('result slot outside storage')
    owner=[None]*allocation.count
    def check(w):
        if w>=program.inputs and owner[allocation.slots[w-program.inputs]]!=w:
            raise ValueError('live wire overwritten')
    for i,(op,a,b) in enumerate(program.operations):
        if op!=LIT:check(a);check(b)
        owner[allocation.slots[i]]=program.inputs+i
    for wire in (*program.outputs,*allocation.pins):check(wire)
    return True


def allocate(program, *, pins=(), capacity=None):
    """Reuse dead slots; optional cap permits forward destinations to save laps.

    Inputs are laid out before the result bank by the fixed ROM compiler.
    A bounded extra bank trades cells for fewer physical controller traversals.
    The capacity is a construction-time constant, never a hierarchy-depth input.
    """
    if capacity is not None and (not isinstance(capacity,int) or capacity<1):
        raise ValueError('positive result-bank capacity required')
    pins=tuple(sorted(set(pins)));last=last_uses(program,pins)
    slots=[];free=[];count=0
    for i,(op,a,b) in enumerate(program.operations):
        floor=max((slots[w-program.inputs] for w in (a,b) if w>=program.inputs),default=0) if op!=LIT else 0
        at=bisect_left(free,floor) if capacity is not None else 0
        if at<len(free):slot=free.pop(at)
        elif capacity is None or count<capacity:slot=count;count+=1
        elif free:slot=free.pop(0)
        else:raise ValueError('result bank smaller than live storage requirement')
        slots.append(slot)
        if op!=LIT:
            for w in sorted({a,b}):
                if w>=program.inputs and last[w]==i:insort(free,slots[w-program.inputs])
        if last[program.inputs+i]<i:insort(free,slot)
    result=Allocation(tuple(slots),count,pins,program.digest())
    verify(program,result)
    return result
