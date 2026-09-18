"""Depth-2 island: a misaligned *level-1* island (two full level-1 colonies = 128 level-0 colonies,
shifted by `shift` level-0 colonies) inside a 1024-colony ring (16 level-2 cells).  The level-0
structure is intact; the level-1 layer is misaligned.  Level-1 rules alone cannot erode it; with
level-2 trickle-down (interpreted into the level-1 cells' Workspace flags) it should be eliminated.
Logs per level-0 period: number of level-0 colonies whose decoded level-1 (ADDR, AGE) is wrong.
Usage: depth2_island.py <trickle2: 0|1> <nper> <shift>"""
import sys, time, json, numpy as np, torch
from gacsca.build import make_tower
from gacsca.hierarchy import encode_info
from gacsca.engine_np import repair
from gacsca import interp as _interp
trickle2 = int(sys.argv[1]) if len(sys.argv) > 1 else 1
nper = int(sys.argv[2]) if len(sys.argv) > 2 else 12000
shift = int(sys.argv[3]) if len(sys.argv) > 3 else 20
ncol0 = 1024
sys0, sys1 = make_tower(ncol0=ncol0)
if not trickle2:
    sys0.sched.ictx.trickle_up = (0, 0)     # level-2 -> level-1 trickle-down disabled (baseline)
p0, T, L0, L1 = sys0.p, sys0.T, sys0.L, sys1.L
U0, Q0, Q1, U1 = p0.U, p0.Q, sys1.p.Q, sys1.p.U
eng0, eng1 = sys0.np_engine(), sys1.np_engine()
g0 = sys0.gpu_engine()
# level-1 ground state ring (1024 cells = 16 level-1 colonies) with level-2 states encoded
level2 = [dict(addr=i % L1.Qs, age=0, f1=0, f2=0) for i in range(ncol0 // Q1)]
S1 = eng1.initial(1, info_bits=encode_info(level2, L1, Q1)[None, :])
# misaligned level-1 island: level-1 cells [c0+shift, c0+shift+128) get addresses 0..127 mod 64 and the
# Info pattern of two full level-1 colonies
c0 = 128
lo, hi = c0 + shift, c0 + shift + 2 * Q1
src = {k: S1[k][:, c0:c0 + 2 * Q1].copy() for k in ("addr", "age", "f1", "f2", "wf1", "wf2", "simage", "simaddr", "trk")}
for k in src: S1[k][:, lo:hi] = src[k]
def encode_level1(S1):
    cells = [dict(addr=int(S1["addr"][0, i]), age=int(S1["age"][0, i]), f1=int(S1["f1"][0, i]), f2=int(S1["f2"][0, i]),
                  wf1=int(S1["wf1"][0, i]), wf2=int(S1["wf2"][0, i]), simage=int(S1["simage"][0, i]), simaddr=int(S1["simaddr"][0, i]),
                  tracks=S1["trk"][0, i]) for i in range(S1["addr"].shape[1])]
    return encode_info(cells, L0, Q0)
S0 = eng0.initial(1, info_bits=encode_level1(S1)[None, :])
S0["simage"][:] = 0
S0["simaddr"][:] = np.repeat(S1["addr"][0], Q0)
st = g0.to_gpu(S0)
ref1 = np.arange(ncol0) % Q1
t = 0; t0 = time.time(); log = []
for per in range(1, nper + 1):
    st = g0.run(st, U0, 0.0, t0=t); t += U0
    if per % 16 == 0 or per <= 2:
        info = g0.info_bits(st).cpu().numpy()[0]
        addr1 = np.array([L0.decode(info[i * Q0 + L0.b0:i * Q0 + L0.b0 + L0.K])["ADDR"] for i in range(ncol0)])
        bad = np.where(addr1 != ref1)[0]
        N = g0.to_np(st)
        l0bad = int((N["addr"][0] != np.arange(p0.L) % Q0).sum())
        rec = dict(per=per, l1_bad=int(len(bad)), l1_lo=int(bad.min()) if len(bad) else -1, l1_hi=int(bad.max()) if len(bad) else -1, l0_bad=l0bad)
        log.append(rec)
        print(f"trickle2={trickle2} period {per} (level-1 age {per % U1}, level-2 step {per // U1}): level-1 misaligned cells {rec['l1_bad']} in [{rec['l1_lo']},{rec['l1_hi']}], level-0 damaged {l0bad} ({time.time()-t0:.0f}s)", flush=True)
        if len(bad) == 0 and l0bad == 0:
            print("healed at period", per); break
json.dump(log, open(f"figs/depth2_island_t{trickle2}_s{shift}.json", "w"))
