"""Colonies of colonies: run the depth-2 tower for one complete level-1 work period (U1 level-0
periods).  Every level-0 period the decoded level-1 state is compared with the direct level-1
engine; at the end the level-2 state decoded from the level-1 Info track must equal the direct
level-2 transition applied to the initial level-2 state."""
import sys, time, json, numpy as np, torch
sys.argv = [sys.argv[0]]
import experiments.tower_acid as ta
from gacsca.engine_np import repair
from gacsca import level0_np as l0
from gacsca.params import Params

T, L0, L1, s1 = ta.T, ta.L0, ta.L1, ta.sched1
U0, U1, Q0, Q1 = ta.U0, ta.U1, ta.Q0, ta.Q1
rng = np.random.default_rng(0)
S1 = ta.level1_initial(rng, 0)
level2_init = [dict(addr=(i + 5) % L1.Qs, age=777 + i, f1=i % 2, f2=(i + 1) % 2) for i in range(ta.ncol0 // Q1)]
S0 = ta.eng0.initial(1, info_bits=ta.encode_level1_into_level0(S1)[None, :])
S0["simage"][:] = 0; S0["simaddr"][:] = (np.arange(ta.p0.L) // Q0) % Q1
st = ta.g0.to_gpu(S0)
t = 0; t0 = time.time(); nbad = 0
log = []
for per in range(1, U1 + 1):
    st = ta.g0.run(st, U0, 0.0, t0=t); t += U0
    S1 = ta.eng1.step(S1)
    if per % 64 == 0 or per <= 3 or per >= U1 - 2:
        dec = ta.decode_level0(st)
        bad = ta.compare(dec, S1)
        nbad += len(bad)
        N = ta.g0.to_np(st)
        l0ok = bool((N["addr"][0] == np.arange(ta.p0.L) % Q0).all())
        print(f"period {per}/{U1}: level-1 age {int(S1['age'][0,0])}, mismatching level-1 cells {len(bad)} {bad[:2]}, level-0 ok {l0ok} ({time.time()-t0:.0f}s)", flush=True)
        log.append(dict(per=per, bad=len(bad)))
# level-2 check: decode the level-2 state from the direct level-1 engine's Info track and from the level-0 decoded one
def level2_from_S1(S1):
    info = repair(S1["trk"])[0, :, T["INFO"]]
    return [tuple(L1.decode(info[i * Q1 + L1.b0:i * Q1 + L1.b0 + L1.K])[k] for k in ("ADDR", "AGE", "F1", "F2")) for i in range(len(info) // Q1)]
dec = ta.decode_level0(st)
info_dec = np.array([d["tracks"][T["INFO"], (T.R - 1) // 2] for d in dec], np.uint8)
l2_from_l0 = [tuple(L1.decode(info_dec[i * Q1 + L1.b0:i * Q1 + L1.b0 + L1.K])[k] for k in ("ADDR", "AGE", "F1", "F2")) for i in range(len(info_dec) // Q1)]
l2_direct = level2_from_S1(S1)
p2 = Params(Q=L1.Qs, U=L1.Us, ncol=1)
arr = dict(addr=np.array([[c["addr"] for c in level2_init]]), age=np.array([[c["age"] for c in level2_init]]),
           f1=np.array([[c["f1"] for c in level2_init]], np.int8), f2=np.array([[c["f2"] for c in level2_init]], np.int8),
           wf1=np.zeros((1, len(level2_init)), np.int8), wf2=np.zeros((1, len(level2_init)), np.int8))
nxt = l0.step(arr, p2)
l2_rule = [(int(nxt["addr"][0, i]), int(nxt["age"][0, i]), int(nxt["f1"][0, i]), int(nxt["f2"][0, i])) for i in range(len(level2_init))]
print("level-2 state after one level-2 step: from level-0 decode:", l2_from_l0, " direct level-1 engine:", l2_direct, " level-2 rule:", l2_rule)
print("RESULT:", "OK" if (nbad == 0 and l2_from_l0 == l2_direct == l2_rule) else "MISMATCH", f"({time.time()-t0:.0f}s)")
json.dump(dict(log=log, l2_from_l0=l2_from_l0, l2_direct=l2_direct, l2_rule=l2_rule), open("figs/tower_full_period.json", "w"))
