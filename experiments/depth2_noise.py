"""Depth-2 noise characterisation: level-1 error rate (any of the 220 decoded bits of a level-1
cell differing from the direct level-1 engine's one-step prediction) vs level-0 noise eps."""
import sys, time, json, numpy as np, torch
sys.argv = [sys.argv[0]]
import experiments.tower_acid as ta
from gacsca.engine_np import repair
T, L0, U0, Q0, Q1 = ta.T, ta.L0, ta.U0, ta.Q0, ta.Q1
def state_from_decoded(dec, S1_template):
    S = {k: v.copy() for k, v in S1_template.items()}
    for i, d in enumerate(dec):
        S["addr"][0, i] = d["ADDR"]; S["age"][0, i] = d["AGE"]; S["f1"][0, i] = d["F1"]; S["f2"][0, i] = d["F2"]
        S["wf1"][0, i] = d["WF1"]; S["wf2"][0, i] = d["WF2"]; S["simage"][0, i] = d["SIMAGE"]; S["simaddr"][0, i] = d["SIMADDR"]
        S["trk"][0, i] = d["tracks"]
    return S
res = {}
for eps in [0.0, 1e-5, 3e-5, 1e-4, 3e-4]:
    rng = np.random.default_rng(1)
    age1 = 1300
    S1 = ta.level1_initial(rng, age1)
    S0 = ta.eng0.initial(1, info_bits=ta.encode_level1_into_level0(S1)[None, :])
    S0["simage"][:] = age1; S0["simaddr"][:] = (np.arange(ta.p0.L) // Q0) % Q1
    st = ta.g0.to_gpu(S0); ta.g0.seed = 5
    prev = ta.decode_level0(st); t = 0; errs = []; t0 = time.time()
    for per in range(1, 9):
        st = ta.g0.run(st, U0, eps, t0=t); t += U0
        cur = ta.decode_level0(st)
        pred = ta.eng1.step(state_from_decoded(prev, S1))
        bad = ta.compare(cur, pred)
        errs.append(len(bad) / ta.ncol0)
        prev = cur
    res[eps] = errs
    print(f"eps={eps:g}: level-1 error rate per cell-period {np.mean(errs[1:]):.4f} per period {np.round(errs, 3).tolist()} ({time.time()-t0:.0f}s)", flush=True)
json.dump(res, open("figs/depth2_noise.json", "w"))
