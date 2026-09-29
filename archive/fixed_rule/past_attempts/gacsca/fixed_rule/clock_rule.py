"""Fixed word rule with local Gray stage clocks, votes, resets and commit.

This revision still lacks fivefold spatial redundancy and flag-signal/trickle
initiation. Stage four is reserved; Wf is constrained to its source time window.
All implemented clock and memory operations are in the complete description.
"""
from dataclasses import replace
from functools import lru_cache
from . import word_rule as w
from .word_rule import (Cell,SCHEMA,COL,WIDTH,FIELDS,NEIGHBORHOOD,STATIC,CONTROL,
    Q,U,MEM,LOOP,SEND,LOAD,META,WAIT,FETCH,READ_A,READ_B,WRITE,TRANSMIT,READ_LOAD,
    READ_META,WAIT_META,RIGHT,LEFT,ALU_KINDS,NAND,ADD,SHR,EQ,LT,LIT,MASK,
    encode_cell,decode_cell,maintenance,advance,reflect_left,receive,waiting)

HALT=12
VOTE=1<<5
INFO=1<<6
RESET_AGES=(0,32*Q,64*Q,96*Q,112*Q)
ACTIVE_ENDS=(16*Q,48*Q,80*Q,104*Q,120*Q)
VOTE_AGES=(72*Q,112*Q)
SIMULATION=('data','head',*CONTROL,*(n for n,_ in SCHEMA if n.startswith(('lp_','rp_'))),'wf1','wf2')


def active(age):return any(lo<=age<hi for lo,hi in zip(RESET_AGES,ACTIVE_ENDS))
def halted(c):return c.head and not c.direction and c.phase==FETCH and c.kind==HALT and c.index==c.pc

def entry(c,stage):
    return ((c.a>>(32*stage)) if stage<2 else (c.b>>(32*(stage-2))) if stage<4 else c.d)&0xFFFFFFFF

def local_step(cells):
    if len(cells)!=11:raise ValueError('exact radius-five neighborhood required')
    c=cells[5]
    quiet=tuple(replace(x,head=0) if halted(x) else x for x in cells)
    result=w.local_step(quiet)
    if not active(c.age):result=replace(result,**{name:getattr(c,name) for name in SIMULATION})
    stage=RESET_AGES.index(c.age) if c.age in RESET_AGES else None
    if stage is not None:
        change={name:0 for name in SIMULATION if name!='data'}
        if c.first or (c.kind==MEM and (c.a>>stage)&1):change['data']=0
        if c.first:change.update(head=1,pc=entry(c,stage))
        result=replace(result,**change)
    if c.age==VOTE_AGES[0]:
        # Second entry in stage three uses the same program as stage five.
        change={name:0 for name in ('head',*CONTROL)}
        if c.first:change.update(head=1,pc=entry(c,4))
        result=replace(result,**change)
    if c.kind==MEM and not c.first and c.a&VOTE and c.age in VOTE_AGES:
        a,b,d=cells[4].data,cells[6].data,cells[7].data
        result=replace(result,data=(a&b)|(a&d)|(b&d))
    if c.kind==MEM and not c.first and c.a&INFO and c.age==U-1:
        result=replace(result,data=cells[6].data)
    if not 96*Q<=result.age<98*Q:result=replace(result,wf1=0,wf2=0)
    # Reapply source priority after rest/reset/vote/commit overrides.
    if result.f1:
        result=replace(result,**{n:0 for n,_ in SCHEMA if n.startswith(('lp_','rp_'))})
        if result.address!=c.address:result=replace(result,**{n:0 for n in ('data','head',*CONTROL,'wf1','wf2')})
    return result


def step_ring(cells):return tuple(local_step(tuple(cells[(i+j)%len(cells)] for j in NEIGHBORHOOD)) for i in range(len(cells)))

@lru_cache(maxsize=1)
def self_description():
    from .clock_description import build
    return build()

def identity():return dict(schema=SCHEMA,width=WIDTH,words=FIELDS,neighborhood=NEIGHBORHOOD,Q=Q,U=U,description_sha256=self_description().digest())
