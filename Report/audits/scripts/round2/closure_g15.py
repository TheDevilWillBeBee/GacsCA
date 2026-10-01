"""Independent three-period G15 physical closure on nonzero upper data."""
import numpy as np
from gacsca.fixed_rule.design_optimization import candidates, codec, gpu

c = candidates.load('G15')
rng = np.random.default_rng(276)
up0 = codec.random_upper(c, 8, rng)
healthy = codec.encode(c, codec.random_upper(c, 1, rng))
up1 = healthy[:, (np.arange(8) + c.p.Q//2 - 4) % c.p.Q]
upper = [up0, up1]
C = c.c_backend()
sim = gpu.GpuSim(c, 2, 8, mode='grid')
sim.set_state(np.stack([C.pack(codec.encode(c, x)) for x in upper]))
sim.set_noise([gpu.noise(), gpu.noise()])
for k in range(1,4):
    sim.run(c.p.U)
    S=sim.state()
    for r in range(2):
        got=codec.decode(c,C.unpack(S[r],sim.N))
        want=c.step_numpy(upper[r])
        print('step',k,'ring',r,'exact',bool(np.array_equal(got,want)),
              'changed_bits',int((want!=upper[r]).sum()),'wrong_cells',
              int((got!=want).any(axis=0).sum()),flush=True)
        upper[r]=want
