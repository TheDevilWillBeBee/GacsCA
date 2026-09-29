"""Complete canonical, mail-free suffix by exact component composition.

The physical rule/ROM is delivery_rule, unchanged. Controller storage is a
zero-flag quotient; the actual four flags come from flag_words. This is a
physical-state representation, with no hierarchy depth or upper interpreter.
The admitted domain ends at the work-period boundary. Failed runs invalidate
this wrapper because the component advances are not transactional.
"""
from dataclasses import replace
import numpy as np
from . import delivery_rule as f,delivery_projected as r,delivery_program as p
from .delivery_control_world import World as Control
from .flag_words import World as Flags


class World:
    def __init__(self,controller,*,flag_runs=None):
        self.control=Control(controller);self.flags=None;self.valid=True
        try:
            g=p.layout();a=controller.reshape(self.control.colonies,g.computation_cells+5,len(r.SCHEMA))
            left=((a[:,3,r.COL['signal']]>>np.uint64(2))&np.uint64(1)).tolist()
            right=((a[:,g.computation_cells+2,r.COL['signal']]>>np.uint64(2))&np.uint64(1)).tolist()
            self.flags=Flags(right,left,age=self.control.epoch,runs=flag_runs)
        except Exception:
            self.control.close();raise
    def close(self):
        self.valid=False
        self.control.close()
        if self.flags is not None:self.flags.close()
    def __enter__(self):return self
    def __exit__(self,*args):self.close()
    def check(self):
        if not self.valid:raise ValueError('closed or invalidated composed state')
        assert self.control.time==self.flags.info['time']
    @property
    def time(self):self.check();return self.control.time
    @property
    def colonies(self):return self.control.colonies
    def run(self,ticks):
        self.check()
        try:
            control=self.control.run(ticks);flags=self.flags.run(ticks)
            self.check();return dict(controller=control,flags=flags)
        except Exception:
            self.valid=False;raise
    def cell(self,colony,address):
        self.check();base=self.control.cell(colony,address);bits=self.flags.cell(colony,address)
        return replace(base,f1=bits&1,f2=(bits>>1)&1,wf1=(bits>>2)&1,wf2=(bits>>3)&1)
    @property
    def stored(self):
        self.check();g=p.layout();a=self.control.stored.reshape(self.colonies,g.computation_cells+5,len(r.SCHEMA))
        addresses=np.array([*range(g.computation_cells),*range(f.Q-5,f.Q)],dtype=np.uint64)
        positions=np.arange(self.colonies,dtype=np.uint64)[:,None]*np.uint64(f.Q)+addresses
        runs=self.flags.runs;indices=np.searchsorted(runs[:,0],positions//np.uint64(64),side='right')
        for k,name in enumerate(('f1','f2')):a[:,:,r.COL[name]]=(runs[indices,k+1]>>(positions%np.uint64(64)))&np.uint64(1)
        if 96*f.Q<=self.flags.info['age']<98*f.Q:
            right,left=self.flags.signals
            a[:,:,r.COL['wf1']]=np.array(right,dtype=np.uint64)[:,None]*(addresses>=f.Q-5)
            a[:,:,r.COL['wf2']]=np.array(left,dtype=np.uint64)[:,None]*(addresses<=4)*(a[:,:,r.COL['f1']]==0)
        return a.reshape(-1,len(r.SCHEMA))
    def decode(self):
        g=p.layout();a=self.stored.reshape(self.colonies,g.computation_cells+5,len(r.SCHEMA))
        return r.decode_cores(np.ascontiguousarray(a[:,:g.computation_cells].reshape(-1,len(r.SCHEMA))))
