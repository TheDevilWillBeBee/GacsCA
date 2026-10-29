"""GBD3 explicit packing -> Head reset/birth -> CPU port-level binding.

This is a total local SF component, not a complete autonomous CA: computed
native ports and three actual History banks remain stated input premises.
Every whole-bit Head/data/tag/collision mode has an assigned equation.
"""
from dataclasses import dataclass,replace
import controller as cpu
import packing_kernel as p


@dataclass(frozen=True)
class Cell(p.Cell):
    head:tuple=(0,)*5
    out:tuple=(0,)*5


ENTRY=p.P+2
BIRTH=p.DONE+1


def head_birth(a):
    return cpu.Head(1,0,cpu.RUN,0,0,0,(0,)*8) if a==ENTRY else cpu.Head()


def local(cells,x,beta):
    """Every access is an actual old raw holder in radius7.

    All Head copies are cleared at ages SEED..DONE inclusive; at BIRTH
    they are overwritten from the centre's computed native Address plus
    their actual copy offset. Other ages use the literal old CPU equation.
    Packing and CPU read OLD data independently in the synchronous update.
    During reset and birth, Out is its voted old value (no old-Head WRITE).
    All other fields are held except the explicit packing/CPU updates.
    """
    packed=p.local(cells,x)
    t=cells[x].age&p.AGE_MASK
    view={z:cpu.Cell(c.addr,c.age,c.head,c.data,c.out) for z,c in cells.items()}
    active=not (p.SEED<=t<=BIRTH)
    if active:
        computed=cpu.local(view,x,beta,-2,20)
        hs=computed.head;outs=computed.out
    else:
        hs=tuple(cpu.pack_head(head_birth((cells[x].addr+s)&(p.Q-1))
                               if t==BIRTH else cpu.Head()) for s in p.SLOTS)
        outs=tuple(cpu.vote(view,x+s,'out',cpu.MASK) for s in p.SLOTS)
    return replace(packed,head=hs,out=outs)
