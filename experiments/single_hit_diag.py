"""Inject exactly one random whole-cell hit per trial at a random (site, age) during one work period
(proper 256-colony ring); report which hits change the decoded level-1 state of any colony."""
import numpy as np, torch, sys, collections
from gacsca.build import make_system
from gacsca.hierarchy import encode_info
from gacsca.params import Params
from gacsca import level0_np as l0

Q, U, ncol = 256, 16384, 256
sysm = make_system(Q=Q, U=U, ncol=ncol, R=3, D=3)
p, T, L, sched = sysm.p, sysm.T, sysm.L, sysm.sched
eng = sysm.np_engine(); g = sysm.gpu_engine(seed=0)
level1 = [dict(addr=i % Q, age=0, f1=0, f2=0) for i in range(ncol)]
S0 = eng.initial(1, info_bits=encode_info(level1, L, Q)[None, :])
st0 = g.to_gpu(S0)
rng = np.random.default_rng(int(sys.argv[1]) if len(sys.argv) > 1 else 0)
ntrials = int(sys.argv[2]) if len(sys.argv) > 2 else 40


def decode_all(st):
    info = g.info_bits(st).cpu().numpy()[0]
    return [tuple(L.decode(info[i * Q + L.b0:i * Q + L.b0 + L.K])[k] for k in ("ADDR", "AGE", "F1", "F2")) for i in range(ncol)]


# reference: one clean period
stc = g.run(st0.clone(), U, 0.0)
ref = decode_all(stc)
bad = []
for trial in range(ntrials):
    t_hit = int(rng.integers(1, U)); x = int(rng.integers(0, p.L))
    st = st0.clone()
    st = g.run(st, t_hit - 1, 0.0)
    N = g.to_np(st)
    # whole-cell replacement
    N["addr"][0, x] = rng.integers(0, Q); N["age"][0, x] = rng.integers(0, U)
    for k in ("f1", "f2", "wf1", "wf2"): N[k][0, x] = rng.integers(0, 2)
    N["trk"][0, x] = rng.integers(0, 2, N["trk"].shape[2:])
    st = g.to_gpu(N)
    st = g.run(st, U - (t_hit - 1), 0.0, t0=t_hit - 1)
    dec = decode_all(st)
    diff = [i for i in range(ncol) if dec[i] != ref[i]]
    N2 = g.to_np(st)
    dmg0 = int((N2["addr"][0] != np.arange(p.L) % Q).sum())
    if diff or dmg0:
        phase = ("gather" if t_hit < sched.compute_start else "compute" if t_hit < sched.compute_end else "post")
        bad.append((t_hit, x % Q, x // Q, phase, diff[:4], [(dec[i], ref[i]) for i in diff[:2]], dmg0))
print(f"{len(bad)}/{ntrials} single hits corrupted the level-1 state")
for b in bad: print("  age", b[0], "addr", b[1], "colony", b[2], b[3], "affected colonies", b[4], "(dec,ref)", b[5], "l0dmg", b[6])
print("phases of corrupting hits:", collections.Counter(b[3] for b in bad))
