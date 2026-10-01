"""Rebuild the data-rich level-2 colony used by repair2 and inspect health."""
import numpy as np
from gacsca.fixed_rule.design_optimization import candidates, codec
from experiments.fixed_rule.design_optimization.three_level_g import run_rings

c=candidates.load('G15')
top=codec.random_upper(c,1,np.random.default_rng(11))
X=codec.encode(c,top)
print('at age 0',codec.colony_health(c,X),'decoded exact',
      bool(np.array_equal(codec.decode(c,X),top)),flush=True)
(X,),_=run_rings(c,[X],60000)
print('at age 60000',codec.colony_health(c,X),'decoded exact',
      bool(np.array_equal(codec.decode(c,X),top)),
      'nonzero bits/cell',round(float(X.sum(axis=0).mean()),1),flush=True)
idx=(np.arange(32)+c.p.Q//2-16)%c.p.Q
sl=X[:,idx].copy()
print('central slice nonzero bits/cell',round(float(sl.sum(axis=0).mean()),1),flush=True)
for k in range(1,5):
    X=c.step_numpy(X)
    sl=c.step_numpy(sl)
    d=(X[:,idx]!=sl).any(axis=0)
    print('rich slice wrap step',k,'middle',bool(d[16]),'diff cells',int(d.sum()),flush=True)
