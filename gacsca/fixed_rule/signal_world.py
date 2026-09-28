"""Exact sparse signal/flag experiment in a constrained full-state family.

Uniform Age, canonical Address, immutable LOOP cells, zero evaluator/mail and
fixed one-bit Data imply a closed subsystem of signal_rule. Its transitions
produce Wf locally; no preseeded Wf or host replacements. Initial Data at the
signal holders is permitted for testing capture, but is NOT computed upper
flags or a delivered-message demonstration. This family is not the ROM layout.
"""
from . import signal_rule as r
from .canonical_flag_world import local_step as old_flag_step


def local_step(neighbors,address,age,data):
    if len(neighbors)!=11 or any(not isinstance(v,int) or not 0<=v<512 for v in neighbors):raise ValueError('eleven nine-bit signal/flag words required')
    if data not in (0,1):raise ValueError('one-bit immutable payload required')
    flags=old_flag_step(tuple(v&15 for v in neighbors),address,age)&3
    new_age=(age+1)%r.U
    def vote(d):return int(sum((neighbors[5+d+e]>>(6-e))&1 for e in range(-2,3))>=3)
    signal=0
    for d in range(-2,3):
        bit=data if new_age==r.CAPTURE_AGE and address+d in (3,r.Q-3) else vote(d)
        signal|=bit<<(d+2)
    wf1=wf2=0
    if 96*r.Q<=new_age<98*r.Q:
        if address>=r.Q-5:wf1=vote(r.Q-3-address)
        if address<=4 and not flags&1:wf2=vote(3-address)
    return flags|(wf1<<2)|(wf2<<3)|(signal<<4)


class SignalWorld:
    def __init__(self,states,*,data=None,colonies=1,age=0):
        if not isinstance(colonies,int) or colonies<1 or not isinstance(age,int) or not 0<=age<r.U:raise ValueError('invalid canonical ring')
        self.size=colonies*r.Q;self.age=age;self.time=0;self.evaluations=0;self.quiet_ticks=0;self.states={};self.data={}
        for position,value in states.items():
            if not isinstance(position,int) or not 0<=position<self.size or not isinstance(value,int) or not 0<=value<512:raise ValueError('invalid signal/flags')
            if value:self.states[position]=value
        for position,value in (data or {}).items():
            if not isinstance(position,int) or not 0<=position<self.size or value not in (0,1):raise ValueError('invalid local capture payload')
            if value:self.data[position]=value
    def at(self,position):return self.states.get(position%self.size,0)
    def record(self,position):
        position%=self.size;value=self.at(position)
        return r.Cell(kind=r.base.LOOP,address=position%r.Q,age=self.age,data=self.data.get(position,0),signal=value>>4,
                      f1=value&1,f2=(value>>1)&1,wf1=(value>>2)&1,wf2=(value>>3)&1)
    def step(self):
        support={((position+j)%self.size) for position in self.states for j in range(-5,6)}
        # Nonzero local payload can create signal even from a zero signal/flag
        # neighborhood at capture. Omitting these dependencies is incorrect.
        if (self.age+1)%r.U==r.CAPTURE_AGE:support.update(self.data)
        updated={}
        for position in support:
            value=local_step(tuple(self.at(position+j) for j in range(-5,6)),position%r.Q,self.age,self.data.get(position,0))
            if value:updated[position]=value
        self.states=updated;self.age=(self.age+1)%r.U;self.time+=1;self.evaluations+=len(support)
    def skip_quiet(self,ticks):
        # In this interval there is no capture, Wf window, or stage reset.
        # LOOP/no-head/no-mail leaves Data and every raw controller word fixed.
        # Check the signal fixed point on its complete dependency support.
        if not isinstance(ticks,int) or ticks<0 or not r.CAPTURE_AGE<=self.age<=self.age+ticks<=96*r.Q-1:
            raise ValueError('quiet jump crosses a signal or clock event')
        if any(v&15 for v in self.states.values()):raise ValueError('physical flags invalidate quiet proof')
        support={((p+j)%self.size) for p in self.states for j in range(-5,6)}
        for p in support:
            if local_step(tuple(self.at(p+j) for j in range(-5,6)),p%r.Q,self.age,self.data.get(p,0))!=self.at(p):
                raise ValueError('signal copies are not a fixed point')
        self.age+=ticks;self.time+=ticks;self.quiet_ticks+=ticks
        return self
    def run(self,steps):
        if not isinstance(steps,int) or steps<0:raise ValueError('nonnegative physical ticks required')
        for _ in range(steps):self.step()
        return self


def seed_signals(*,colonies=1,flag1=True,flag2=True):
    states={}
    for colony in range(colonies):
        for target,bit in ((r.Q-3,flag1),(3,flag2)):
            if bit:
                for e in range(-2,3):
                    holder=colony*r.Q+target+e
                    states[holder]=states.get(holder,0)|(1<<(6-e))
    return states
