"""Corrected Gray native subsystem at his original printed constants.

The one explicit rule change is candidate-B's healthy Flag2 erasure
threshold h=1. Workspace flag OUTPUTS are zero, a justified restriction
only while all computed Ages stay below the published3U/4 pulse.
There is no self-simulation programme in this native test object.
"""
from dataclasses import dataclass,asdict
from functools import lru_cache
import sys
import numpy as np
from gacsca import machine,maintenance
from gacsca.netlist import Net,Compiled

OFFSETS=tuple(range(-5,6))


@dataclass(frozen=True)
class ParamsNative:
    k:int=13
    m:int=20
    Q:int=8192
    U:int=1048576
    IW:int=1
    PW:int=1
    NPT:int=2

    def check(self):
        assert self.Q == 1<<self.k and self.U == 128*self.Q == 1<<self.m
        return self

    def fam(self):
        return sys.modules[__name__]


def schema(p):
    return [('addr',p.k),('age',p.m),('f1',1),('f2',1),('wf1',1),('wf2',1)]


def width(p):
    return sum(w for _,w in schema(p))


@lru_cache(maxsize=2)
def cached(p):
    net=Net()
    cells={j:{field:[net.input(('x',j,field,bit)) for bit in range(w)]
              for field,w in schema(p)} for j in OFFSETS}
    cells={j:{field:bits if field in ('addr','age') else bits[0]
              for field,bits in cell.items()} for j,cell in cells.items()}
    net.input(('I',0))
    out=maintenance.build(net,cells,p.k,p.m)
    for field,w in schema(p):
        values=([0] if field.startswith('wf') else
                out[field] if field in ('addr','age') else [out[field]])
        for bit,node in enumerate(values):
            net.set_output(('y',field,bit),node)
    net.set_output(('psel',0),0)
    net.set_output(('arrive',0),0)
    for bit in range(p.k):
        net.set_output(('laddr',bit),0)
    return net,Compiled(net)


def identity(p):
    _,comp=cached(p)
    return dict(params=asdict(p),width=width(p),radius=5,netlist_sha256=comp.digest,
                self_simulation_programme=False,corrected_healthy_flag2_threshold=1)


def candidate():
    p=ParamsNative().check()
    return machine.Candidate(p,np.zeros((p.Q,p.NPT),dtype=np.uint32),np.arange(width(p)))
