"""Exact one-colony Flag2 projection with no Flag1 or right signal.

Canonical geometry, a coherent fixed left signal, and ages from 96Q-1 through
U-1 form a closed flag subsystem (no capture during that interval). Integer
bitplanes encode physical sites, not a simulated controller or upper transition.
Each output bit reads only itself and its five left neighbors. This is not the
coupled two-wave case needed by the full executor.
"""
from .delivery_rule import Q,U


def transition(bits,wf2_on):
    if not isinstance(bits,int) or bits<0 or bits.bit_length()>Q:raise ValueError('one fixed-Q bitplane required')
    a,b,c,d,e=(bits<<j for j in range(1,6));ab=a&b;cd=c&d
    four=(ab&cd)|(ab&e&(c|d))|(cd&e&(a|b))
    # Outside-colony left neighbors are vacuously true in the printed erasure
    # predicate, and false in the inside-colony birth count.
    erase=(a|1)&(b|3)&(c|7)&(d|15)&(e|31)
    out=((~bits)&four)|(bits&~erase)|(255 if wf2_on else 0)
    return out if out.bit_length()<=Q else out&((1<<Q)-1)


class Flag2Bits:
    def __init__(self,bits=0,*,age=96*Q-1,left_signal=True):
        if not isinstance(age,int) or not 96*Q-1<=age<U:raise ValueError('post-capture age interval required')
        transition(bits,False)
        self.bits=bits;self.age=age;self.time=0;self.left_signal=bool(left_signal)
        self.wf2=bool(left_signal and 96*Q<=age<98*Q)
    def step(self):
        if self.age>=U-1:raise ValueError('cannot cross unspecified next-period capture dependencies')
        self.bits=transition(self.bits,self.wf2);self.age+=1;self.time+=1
        self.wf2=self.left_signal and 96*Q<=self.age<98*Q
    def run(self,ticks):
        if not isinstance(ticks,int) or ticks<0:raise ValueError('nonnegative ticks required')
        for _ in range(ticks):self.step()
        return self
