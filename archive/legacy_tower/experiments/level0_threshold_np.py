"""Level-0 recovery probability vs per-cell-per-step error rate (NumPy, small)."""
import numpy as np, time, json
from gacsca.params import Params
from gacsca.sim_np import run
p = Params(Q=271, ncol=4)
Tn, Tr, B = 500, 400, 8
res = {}
for eps in [0.02, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.5]:
    t0 = time.time()
    rec, S = run(p, Tn + Tr, lambda t: eps if t <= Tn else 0.0, B=B, seed=2, record=("addr", "age"), every=Tn + Tr)
    L = p.L
    addr_ok = (S["addr"] == np.arange(L) % p.Q).all(1)
    age_ok = (S["age"] == (Tn + Tr) % p.U).all(1)
    frac_addr = (S["addr"] == np.arange(L) % p.Q).mean(1)
    res[eps] = dict(addr_recovered=float(addr_ok.mean()), age_recovered=float(age_ok.mean()), mean_frac_addr_ok=float(frac_addr.mean()))
    print(f"eps={eps:.2f} addr_rec={addr_ok.mean():.2f} age_rec={age_ok.mean():.2f} frac_addr_ok={frac_addr.mean():.3f} ({time.time()-t0:.0f}s)", flush=True)
json.dump(res, open("figs/level0_threshold_np.json", "w"), indent=1)
