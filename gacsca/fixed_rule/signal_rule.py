"""Candidate signal extension; no compiled self-simulation ROM yet.

Gray pp.33,35,41: five copies of a reserved SimBit, late stage-three
capture from locally delivered data, and computed-geometry Wf initiation.
D10 choice: Wf reads the voted old signal, before remote structural clearing.
This finite radius-five choice is NOT asserted equivalent on damaged geometry
to reading a neighbor's entire post-transition signal. See SIGNAL.md.
"""
from dataclasses import dataclass,replace
from functools import lru_cache
from . import clock_rule as base

Q,U,NEIGHBORHOOD=base.Q,base.U,base.NEIGHBORHOOD
STATIC,CONTROL=base.STATIC,base.CONTROL
SCHEMA=base.SCHEMA+(('signal',5),)
COL={name:i for i,(name,_) in enumerate(SCHEMA)}
FIELDS,WIDTH=len(SCHEMA),sum(width for _,width in SCHEMA)
CAPTURE_AGE=79*Q  # computed Age, proposal to be certified with the future ROM


@dataclass(frozen=True)
class Cell(base.Cell):
    signal:int=0
    def __post_init__(self):
        super().__post_init__()
        if not isinstance(self.signal,int) or not 0<=self.signal<32:
            raise ValueError('signal outside fixed five-bit alphabet')


def encode_cell(cell):return tuple(getattr(cell,name) for name,_ in SCHEMA)
def decode_cell(words):
    if len(words)!=FIELDS:raise ValueError('all raw controller and signal words required')
    return Cell(**dict(zip((name for name,_ in SCHEMA),map(int,words))))
def base_cell(cell):return base.Cell(**{name:getattr(cell,name) for name,_ in base.SCHEMA})


def voted_signal(cells,target):
    """Logical bit at center+target; holders target-2..target+2.

    Slot d+2 at holder y stores the primary bit at y+d. The caller must
    supply only the eleven actual old neighbors, never a global accessor.
    """
    if len(cells)!=11 or not -3<=target<=3:raise ValueError('signal vote exceeds radius five')
    return int(sum((cells[5+target+e].signal>>(2-e))&1 for e in range(-2,3))>=3)


def local_step(cells):
    if len(cells)!=11:raise ValueError('exact radius-five neighborhood required')
    old=cells[5];out=base.local_step(tuple(base_cell(c) for c in cells))
    signal=0
    for d in range(-2,3):
        value=voted_signal(cells,d)
        if out.age==CAPTURE_AGE and out.address+d in (3,Q-3):value=old.data&1
        signal|=value<<(d+2)
    wf1=wf2=0
    if 96*Q<=out.age<98*Q:
        if Q-5<=out.address<Q:wf1=voted_signal(cells,Q-3-out.address)
        if out.address<=4 and not out.f1:wf2=voted_signal(cells,3-out.address)
    if out.f1 and out.address!=old.address:signal=wf1=wf2=0
    return Cell(**{**{name:getattr(out,name) for name,_ in base.SCHEMA},'signal':signal,'wf1':wf1,'wf2':wf2})


def step_ring(cells):
    return tuple(local_step(tuple(cells[(i+j)%len(cells)] for j in NEIGHBORHOOD)) for i in range(len(cells)))

@lru_cache(maxsize=1)
def self_description():
    from .signal_description import build
    return build()

def identity():
    return dict(schema=SCHEMA,width=WIDTH,words=FIELDS,neighborhood=NEIGHBORHOOD,Q=Q,U=U,
                description_sha256=self_description().digest(),signal_semantics='voted-old-before-remote-clear',capture_computed_age=CAPTURE_AGE)
