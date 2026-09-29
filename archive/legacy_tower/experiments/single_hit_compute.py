"""Batched single-hit diagnostic: each trial gets exactly one whole-cell hit at a random site and a
random age inside the compute window; report how many trials end with a wrong level-1 state."""
import sys, numpy as np, torch, collections
from gacsca.build import make_system
from gacsca.hierarchy import encode_info
from gacsca.params import Params
from gacsca import level0_np as l0
ncol, Q, U = 64, 256, 16384
sysm = make_system(Q=Q, U=U, ncol=ncol, R=3, D=3)
p, T, L, sched = sysm.p, sysm.T, sysm.L, sysm.sched
g = sysm.gpu_engine(seed=0); eng = sysm.np_engine()
level1 = [dict(addr=i % Q, age=0, f1=0, f2=0) for i in range(ncol)]
B = 64; nbatch = int(sys.argv[1]) if len(sys.argv) > 1 else 30
lo, hi = sched.compute_start, sched.compute_end
rng = np.random.default_rng(0)
def decode(st):
    info = g.info_bits(st).cpu().numpy()
    return [[tuple(L.decode(info[b, i * Q + L.b0:i * Q + L.b0 + L.K])[k] for k in ("ADDR", "AGE", "F1", "F2")) for i in range(ncol)] for b in range(info.shape[0])]
S0 = eng.initial(1, info_bits=encode_info(level1, L, Q)[None, :])
ref = decode(g.run(g.to_gpu(S0), U, 0.0))[0]
bad = []; ntr = 0
for nb in range(nbatch):
    S = eng.initial(B, info_bits=np.tile(encode_info(level1, L, Q)[None, :], (B, 1)))
    st = g.to_gpu(S)
    t_hit = rng.integers(lo, hi, B); xs = rng.integers(0, p.L, B)
    # advance all trials to age lo-1, then step one at a time applying each trial's hit at its age
    st = g.run(st, lo - 1, 0.0)
    buf = torch.empty_like(st)
    for t in range(lo, hi + 1):
        sel = np.where(t_hit == t)[0]
        if len(sel):
            for b in sel:
                x = int(xs[b])
                w = rng.integers(0, 2**32, g.W, dtype=np.uint64).astype(np.uint32)
                w[0] = rng.integers(0, Q); w[1] = rng.integers(0, U); w[2] = rng.integers(0, 16)
                w[3] = rng.integers(0, U) | (rng.integers(0, Q) << 16)
                st[b, x, :] = torch.from_numpy(w).cuda()
        g.step(st, buf, t, 0.0); st, buf = buf, st
    st = g.run(st, U - hi, 0.0, t0=hi + 1)
    dec = decode(st)
    for b in range(B):
        ntr += 1
        diff = [i for i in range(ncol) if dec[b][i] != ref[i]]
        if diff: bad.append((int(t_hit[b]) - lo, int(xs[b] % Q), diff[:3], dec[b][diff[0]], ref[diff[0]]))
    print(f"batch {nb}: {len(bad)} corrupting hits so far / {ntr} trials", flush=True)
print("corrupting single hits:", len(bad), "of", ntr)
for b_ in bad[:20]: print("  age offset in compute", b_[0], "addr", b_[1], "affected colonies", b_[2], "dec", b_[3], "ref", b_[4])
