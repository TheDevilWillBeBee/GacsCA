"""Complete coherent physical suffix on the certified right-one/left-zero family.

This is a representation of the same holder rule. The raw simulated state is
never stepped here. Controller instructions evolve locally; the exact, separately
proved flag recurrence is represented by its interval endpoints. Arbitrary flag
patterns, incoherent backups or mail are rejected, not silently approximated.
"""
from dataclasses import replace
import numpy as np
from . import parallel_holder_rule as f,parallel_holder_program as p,parallel_holder_quotient as q,parallel_holder_initial as initial,parallel_holder_flag_profile as profile
from .parallel_holder_control_world import World as Control


class World:
    def __init__(self,controller):
        self.control=Control(controller);self.valid=True
        try:
            if self.control.epoch!=profile.START:raise ValueError('certified zero-flag prefix endpoint required')
            a=self.control.stored.reshape(self.colonies,p.layout().computation_cells+5,len(q.SCHEMA))
            if np.any(a[:,3,q.COL['signal']]) or np.any(a[:,-3,q.COL['signal']]!=4):raise ValueError('right Signal one and left Signal zero required')
        except Exception:self.close();raise
    def close(self):self.valid=False;self.control.close()
    def __enter__(self):return self
    def __exit__(self,*args):self.close()
    def check(self):
        if not self.valid:raise ValueError('closed or invalidated state')
    @property
    def colonies(self):return self.control.colonies
    @property
    def time(self):self.check();return self.control.time
    @property
    def age(self):return profile.START+self.time
    def run(self,ticks,**options):
        self.check()
        try:return self.control.run(ticks,**options)
        except Exception:self.valid=False;raise
    def logical_cell(self,colony,address):
        self.check();state=self.control.cell(colony,address)
        return replace(state,**dict(zip(('f1','f2','wf1','wf2'),profile.bits(self.age,address))))
    def cell(self,colony,address):
        self.check()
        if not 0<=colony<self.colonies or not 0<=address<f.Q:raise ValueError('site outside ring')
        def read(pos):
            c,a=divmod(pos,f.Q);return self.logical_cell(c%self.colonies,a)
        return initial.coherent_cell(read,colony*f.Q+address)
    @property
    def logical_stored(self):
        self.check();g=p.layout();a=self.control.stored.reshape(self.colonies,g.computation_cells+5,len(q.SCHEMA))
        addresses=np.array([*range(g.computation_cells),*range(f.Q-5,f.Q)],dtype=np.uint64);lo,hi=profile.interval(self.age)
        a[:,:,q.COL['f1']]=(addresses>=lo)&(addresses<hi)
        a[:,:,q.COL['wf1']]=(addresses>=f.Q-5)&(96*f.Q<=self.age<98*f.Q)
        return a.reshape(-1,len(q.SCHEMA))
    def decode(self):
        g=p.layout();a=self.logical_stored.reshape(self.colonies,g.computation_cells+5,len(q.SCHEMA))
        return q.decode_cores(np.ascontiguousarray(a[:,:g.computation_cells].reshape(-1,len(q.SCHEMA))))
