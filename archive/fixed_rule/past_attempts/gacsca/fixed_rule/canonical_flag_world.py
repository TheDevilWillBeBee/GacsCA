"""Exact sparse projection of current clock-rule physical flags.

Canonical Address/uniform Age make the four flags a closed subsystem of the
CURRENT rule (which has no signal-triggered Wf yet). This is not a full-state
executor, self-simulation experiment, or implementation of future trickle-down.
Every changed flag is computed from eleven adjacent old flag records.
"""
from . import clock_rule as f

NAMES=('f1','f2','wf1','wf2')


def local_step(neighbors,address,age):
    if len(neighbors)!=11 or any(not isinstance(x,int) or not 0<=x<16 for x in neighbors):raise ValueError('eleven four-bit states required')
    if not 0<=address<f.Q or not 0<=age<f.U:raise ValueError('invalid fixed structural fields')
    c=neighbors[5];inside=lambda j:0<=address+j<f.Q
    right=sum(neighbors[j+5]&1 for j in range(1,6) if inside(j))
    flag1=int(sum((neighbors[j+5]>>2)&1 for j in range(-5,6) if inside(j))>=3 or right>=3 or ((c&1) and right>=2))
    left=[(neighbors[j+5]>>1)&1 for j in range(-1,-6,-1)]
    d4=sum((neighbors[j+5]>>3)&1 for j in range(-5,6) if inside(j))>=3
    on=sum((neighbors[j+5]>>1)&1 for j in range(-1,-6,-1) if inside(j))>=4 or (flag1 and sum(left)>=4) or d4
    erase=(not flag1 and all(not inside(j) or (neighbors[j+5]&2) for j in range(-1,-6,-1))) or (flag1 and not any(left))
    flag2=int((d4 or not erase) if c&2 else on)
    keep_wf=age not in f.RESET_AGES and 96*f.Q<=(age+1)%f.U<98*f.Q
    return flag1|(flag2<<1)|(c&12 if keep_wf else 0)


class FlagProjection:
    def __init__(self,states,*,colonies=1,age=0):
        if not isinstance(colonies,int) or colonies<1 or not isinstance(age,int) or not 0<=age<f.U:raise ValueError('invalid canonical ring')
        self.size=colonies*f.Q;self.age=age;self.time=0;self.states={};self.evaluations=0
        for position,value in states.items():
            if not isinstance(position,int) or not 0<=position<self.size or not isinstance(value,int) or not 0<=value<16:raise ValueError('invalid initial flags')
            if value:self.states[position]=value
    def at(self,position):return self.states.get(position%self.size,0)
    def record(self,position):
        value=self.at(position)
        return f.Cell(address=position%f.Q,age=self.age,**{name:(value>>bit)&1 for bit,name in enumerate(NAMES)})
    def step(self):
        # Outside this dependency support all eleven flags are zero, whose
        # output is zero for every canonical Address and every Age.
        support={((position+j)%self.size) for position in self.states for j in range(-5,6)}
        updated={}
        for position in support:
            value=local_step(tuple(self.at(position+j) for j in range(-5,6)),position%f.Q,self.age)
            if value:updated[position]=value
        self.states=updated;self.age=(self.age+1)%f.U;self.time+=1;self.evaluations+=len(support)
    def run(self,steps):
        if not isinstance(steps,int) or steps<0:raise ValueError('nonnegative physical ticks required')
        for _ in range(steps):self.step()
        return self
