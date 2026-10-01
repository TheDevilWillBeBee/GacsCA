"""Test whether decoded-away special Info can affect the next upper cell."""
import numpy as np
from gacsca.fixed_rule.design_optimization import candidates, codec, gpu

c=candidates.load('G15');p=c.p;Q,U=p.Q,p.U;C=c.c_backend()
rng=np.random.default_rng(9)
upper_full=codec.encode(c,codec.random_upper(c,1,rng))
up=upper_full[:,(np.arange(16)+Q//2-8)%Q]
X0=codec.encode(c,up)
sim=gpu.GpuSim(c,1,16,mode='grid');sim.set_state(C.pack(X0));sim.run(p.T_wf)
X=C.unpack(sim.state()[0],sim.N)
Y=X.copy();logical=8*Q+Q-3
for slot,off in p.fam().info_copies(p):
    Y[c.row[('info',slot)],(logical+off)%sim.N]^=True
print('initial same decoded',bool(np.array_equal(codec.decode(c,X),codec.decode(c,Y))),
      'perturbed copies',int((X!=Y).sum()),'original special bit',bool(X[c.row[('info',2)],logical]),flush=True)
sim2=gpu.GpuSim(c,2,16,mode='grid')
sim2.set_state(np.stack([C.pack(X),C.pack(Y)]),t=p.T_wf)
sim2.set_noise([gpu.noise(),gpu.noise()])
sim2.run(1)
S=sim2.state();A,B=[C.unpack(S[i],sim.N) for i in range(2)]
print('after one tick physical diff sites',int((A!=B).any(axis=0).sum()),
      'wf1 diff sites',np.flatnonzero(A[c.row[('wf1',0)]]!=B[c.row[('wf1',0)]]).tolist()[:20],flush=True)
sim2.run(U-p.T_wf-1)
S=sim2.state();A,B=[C.unpack(S[i],sim.N) for i in range(2)]
dA,dB=codec.decode(c,A),codec.decode(c,B)
print('at period boundary decoded diff cells',np.flatnonzero((dA!=dB).any(axis=0)).tolist(),
      'decoded diff bits',int((dA!=dB).sum()),'physical diff sites',int((A!=B).any(axis=0).sum()),flush=True)
