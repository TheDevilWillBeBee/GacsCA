"""Gray's gather vote (p. 35): which colony's data do differing history bits carry?

G15, 64-cell slice of a healthy upper colony, damaged colony c = 32. Lane i
of colony D holds neighbour D + LANE_OFFSETS[i]'s bits; h1 is the voted lane
(gathers 1 and 2 stored, the third arrival voted into h1), h2 the raw
gather-2 copy. For each differing bit we record (holder colony, source
colony). Three errors: in transit only (a burst in colony 32's margin during
gather 2), at the source only (its working cells late in the period), both.
Usage: PYTHONPATH=. python experiments/gather_vote_check.py
"""
import sys
from collections import Counter, defaultdict
import numpy as np
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from level1_campaign import upper_state, phases
from gacsca import candidates, codec, gpu
from gacsca.rule import LANE_OFFSETS
cand = candidates.load('G15')
p, C = cand.p, cand.c_backend()
Q, U = p.Q, p.U
top, full = upper_state(cand, 7, 0)
n = 64
idx = (np.arange(n) + Q // 2 - n // 2) % Q
ring_up = full[:, idx]
c = n // 2
X0 = C.pack(codec.encode(cand, ring_up))
ph = phases(p)
g2 = p.gathers_q[1] * Q                     # gather 2 starts (mail loaded at Age 12Q)
scen = [('transport: margin of colony 32 during gather 2', c * Q + 10, g2 + 100),
        ('source: working cells of colony 32, final program', c * Q + Q // 2 - 50, ph['final_program']),
        ('both: working cells of colony 32 during gather 2', c * Q + Q // 2 - 50, g2 + 100)]
sim = gpu.GpuSim(cand, 1 + len(scen), n, mode='grid')
sim.set_state(X0)
sim.set_noise([gpu.noise()] + [gpu.noise(200 + i, boxes=[(x0, 100, t0, 100, 1.0)])
                                for i, (_, x0, t0) in enumerate(scen)])
w = len(LANE_OFFSETS)
for t in (int(0.5 * U), int(1.5 * U)):
    sim.run(t - sim.t)
    S = sim.state()
    print(f'--- t = {t / U:.2f} U (all three gathers of this period done)')
    for r, (name, _, _) in enumerate(scen, 1):
        X = C.unpack(S[r], sim.N)
        Y = C.unpack(S[0], sim.N)
        out = {}
        for f in ('h1', 'h2'):
            r0 = cand.row[(f, 0)]
            d = X[r0:r0 + 5 * w] != Y[r0:r0 + 5 * w]           # rows: slot-major, lane i = row % w
            src = Counter()
            for row, site in zip(*np.nonzero(d)):
                lane = row % w
                D = site // Q
                src[(int(D), int((D + LANE_OFFSETS[lane]) % n))] += 1
            out[f] = dict(sorted(src.items()))
        info = (X[cand.row[('info', 0)]:cand.row[('info', 0)] + 5] != Y[cand.row[('info', 0)]:cand.row[('info', 0)] + 5]).any(axis=0)
        icols = sorted(set((np.nonzero(info)[0] // Q).tolist()))
        print(f'  {name}\n    Info differs in colonies {icols}\n'
              f'    h1 (voted) differing bits by (HOLDER, SOURCE) colony: {out["h1"]}\n'
              f'    h2 (raw gather-2 copy) by (HOLDER, SOURCE):    {out["h2"]}', flush=True)
