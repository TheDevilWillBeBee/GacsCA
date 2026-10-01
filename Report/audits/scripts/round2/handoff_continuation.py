"""Continue a rich G15 midpass wipe physically beyond repair2's hand-off."""
import argparse
import time
import numpy as np
from gacsca.fixed_rule.design_optimization import candidates, codec, gpu
from experiments.fixed_rule.design_optimization.three_level_g import run_rings

ap = argparse.ArgumentParser()
ap.add_argument('--age1', type=int, default=62640)
ap.add_argument('--wipe-tick', type=int, default=40000)
ap.add_argument('--k', type=int, default=7)
ap.add_argument('--fault-seed', type=int, default=911)
args = ap.parse_args()
c = candidates.load('G15')
p, Q, U, C = c.p, c.p.Q, c.p.U, c.c_backend()
rng = np.random.default_rng(11)
top3 = codec.random_upper(c, 1, rng)
colony2 = codec.encode(c, top3)
(colony2,), _ = run_rings(c, [colony2], 60000)
n2 = 32
idx2 = (np.arange(n2) + Q // 2 - n2 // 2) % Q
L2 = colony2[:, idx2]
L1 = codec.encode(c, L2)
age1 = args.age1
(start,), _ = run_rings(c, [L1], age1)
n1, mid = 64, n2 // 2 * Q + Q // 2
sl = (np.arange(n1) + mid - n1 // 2) % L1.shape[1]
phys0 = codec.encode(c, start[:, sl])
k = args.k
x0 = (n1 // 2 - (k - 1) // 2) * Q
sim = gpu.GpuSim(c, 2, n1, mode='grid')
sim.set_state(C.pack(phys0))
sim.set_noise([gpu.noise(), gpu.noise(args.fault_seed, boxes=[(x0, k * Q, args.wipe_tick, 200, 1.0)])])
prev = None
states = []
for step in range(1, 5):
    t0 = time.time()
    sim.run(U)
    raw = sim.state()
    X = [C.unpack(raw[j], n1 * Q) for j in range(2)]
    dec = [codec.decode(c, a) for a in X]
    clos = [] if prev is None else [int(x) for x in np.flatnonzero(
        (dec[1] != c.step_numpy(prev[1])).any(axis=0)) if 6 <= x < n1 - 6]
    print('step',step,'seconds',round(time.time()-t0,1),'closure_bad_mid',clos,
          'L1_diff',int((dec[1]!=dec[0]).any(axis=0).sum()),flush=True)
    prev = dec
    states = X

ref, fault = states
decref, decfault = prev
R = fault ^ ref ^ codec.encode(c, decfault) ^ codec.encode(c, decref)
info0 = c.row[('info', 0)]
slots = R[info0:info0+5]
ii, xx = np.nonzero(slots)
print('handoff residue bits',len(xx),'sites',len(set(xx.tolist())),
      'addresses',sorted(set((xx%Q).tolist())),'special_address_bits',
      int(np.isin(xx%Q,[3,Q-3]).sum()),flush=True)

canon = codec.encode(c, decfault)
sim2 = gpu.GpuSim(c, 3, n1, mode='grid')
sim2.set_state(np.stack([C.pack(ref), C.pack(fault), C.pack(canon)]),t=4*U)
sim2.set_noise([gpu.noise()] * 3)
for k in (5,6):
    t0=time.time();sim2.run(U)
    raw=sim2.state()
    X=[C.unpack(raw[j],n1*Q) for j in range(3)]
    dec=[codec.decode(c,a) for a in X]
    expected=c.step_numpy(decfault)
    diff_actual=np.flatnonzero((dec[1]!=expected).any(axis=0))
    diff_canon=np.flatnonzero((dec[2]!=expected).any(axis=0))
    diff_pair=np.flatnonzero((dec[1]!=dec[2]).any(axis=0))
    print('continuation',k,'seconds',round(time.time()-t0,1),
          'actual_vs_one_step_F',diff_actual.tolist() if k==5 else 'n/a',
          'canonical_vs_one_step_F',diff_canon.tolist() if k==5 else 'n/a',
          'actual_vs_canonical_decoded',diff_pair.tolist(),
          'physical_sites_diff',int((X[1]!=X[2]).any(axis=0).sum()),flush=True)
    decfault=dec[1]
