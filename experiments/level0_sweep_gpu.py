"""GPU sweep: level-0 recovery probability vs error rate (noise for Tn steps, then Tr noiseless).
Also records the steady-state fraction of correct Addresses during the noisy phase."""
import sys, json, time, numpy as np, torch
from gacsca.params import Params, Variant
from gacsca import gpu

def sweep(Q, ncol, eps_list, B=256, Tn=500, Tr=500, seed=0, variant=Variant(), tag=""):
    p = Params(Q=Q, ncol=ncol)
    res = []
    for eps in eps_list:
        t0 = time.time()
        g = gpu.Level0GPU(p, variant, seed=seed)
        st = gpu.initial(p, B)
        fr = []
        def cb(t, s):
            if t % 50 == 0 and t <= Tn:
                fr.append((~gpu.damage_mask(s, p)).float().mean().item())
        st = g.run(st, Tn, eps, callback=cb)
        st = g.run(st, Tr, 0.0, t0=Tn)
        addr_ok = (~gpu.damage_mask(st, p)).all(1)
        both_ok = (~gpu.damage_mask(st, p, t=Tn + Tr)).all(1)
        r = dict(Q=Q, ncol=ncol, eps=eps, B=B, Tn=Tn, Tr=Tr, addr_rec=addr_ok.float().mean().item(),
                 full_rec=both_ok.float().mean().item(), frac_ok_noisy=float(np.mean(fr[-4:])), variant=variant.__dict__)
        res.append(r)
        print(f"{tag} Q={Q} ncol={ncol} eps={eps:.3f} addr_rec={r['addr_rec']:.3f} full_rec={r['full_rec']:.3f} frac_ok_noisy={r['frac_ok_noisy']:.3f} ({time.time()-t0:.1f}s)", flush=True)
    return res

if __name__ == "__main__":
    out = []
    eps_list = [0.05, 0.1, 0.2, 0.3, 0.34, 0.36, 0.38, 0.40, 0.42, 0.44, 0.46, 0.48, 0.5, 0.55, 0.6]
    out += sweep(271, 4, eps_list, B=256, tag="main")
    out += sweep(271, 4, eps_list, B=256, variant=Variant.masumori(), tag="masumori-variant")
    for Q in [32, 64, 128, 512, 1024]:
        out += sweep(Q, 4, [0.3, 0.34, 0.38, 0.40, 0.42, 0.44, 0.48], B=256, tag=f"Qdep")
    for ncol in [2, 8, 16, 32]:
        out += sweep(271, ncol, [0.36, 0.38, 0.40, 0.42, 0.44], B=128, tag="Ndep")
    json.dump(out, open("figs/level0_sweep_gpu.json", "w"), indent=1)
