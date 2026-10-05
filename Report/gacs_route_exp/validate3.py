"""Physical checks of a scratch candidate (C kernel): closure over periods with the
run_g_period probes, then the level-0 one-tick test (after experiments/level0_one_tick.py).
usage: GACS_COPIES=3 python3 validate3.py cand_<tag>.npz [periods] [trials]"""
import sys, os, json, time, hashlib
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np
from collections import Counter
from gacsca import candidates, machine, codec, rule_g

z = np.load(os.path.join(HERE, sys.argv[1]), allow_pickle=False)
periods = int(sys.argv[2]) if len(sys.argv) > 2 else 2
trials = int(sys.argv[3]) if len(sys.argv) > 3 else 2000
THREADS = 3
params = json.loads(str(z['params']))
for key in ('skew', 'gathers_q'):
    params[key] = tuple(params[key])
p = rule_g.ParamsG(**params).check()
cand = machine.Candidate(p, z['rom'], z['layout'])
C = cand.c_backend()
ident = cand.identity()
print(json.dumps(dict(copies=rule_g.NC, Q=p.Q, U=p.U, width=ident['width'], gates=ident['gates'],
                      netlist=ident['netlist_sha256'][:16])), flush=True)
Q = p.Q

def closure(n1, seed, coherent):
    rng = np.random.default_rng(seed)
    up = codec.random_upper(cand, n1, rng)
    if coherent:
        base = int(rng.integers(0, Q))
        cand.set_field(up, 'addr', (base + np.arange(n1)) % Q)
        cand.set_field(up, 'age', np.full(n1, p.age_code(int(rng.integers(0, p.U)))))
        for f in ('f1', 'f2', 'wf1', 'wf2'):
            up[cand.row[(f, 0)]] = False
    P = C.pack(codec.encode(cand, up))
    N = n1 * Q
    probes = [p.T_sig + 1, p.T_wf + 2]
    for period in range(periods):
        ref = cand.step_numpy(up)
        f1_new = ref[cand.row[('f1', 0)]]; f2_new = ref[cand.row[('f2', 0)]]
        age = 0
        rec = dict(period=period + 1, coherent=coherent, upper_f1=int(f1_new.sum()), upper_f2=int(f2_new.sum()))
        for t in probes + [p.U]:
            P = C.run_packed(P, t - age, threads=THREADS); age = t
            if t == p.U:
                break
            X = C.unpack(P, N)
            info, _ = codec.logical_info(cand, X)
            f1 = X[cand.row[('f1', 0)]].reshape(n1, Q)
            wf1 = X[cand.row[('wf1', 0)]].reshape(n1, Q); wf2 = X[cand.row[('wf2', 0)]].reshape(n1, Q)
            if t == p.T_sig + 1:
                sim = info.reshape(n1, Q)
                rec['special_ok'] = bool(np.array_equal(sim[:, Q - 3], f1_new) and np.array_equal(sim[:, 3], f2_new))
            if t == p.T_wf + 2:
                exp_wf2 = f2_new.astype(bool) & ~f1[:, :5].any(axis=1)
                rec['wf_ok'] = bool(np.array_equal(wf1[:, Q - 5:].all(axis=1), f1_new.astype(bool)) and not wf1[:, :Q - 5].any()
                                    and np.array_equal(wf2[:, :5].any(axis=1), exp_wf2) and not wf2[:, 5:].any())
        X = C.unpack(P, N)
        dec = codec.decode(cand, X)
        health = codec.colony_health(cand, X)
        rec.update(decoded_equal=bool(np.array_equal(dec, ref)), changed_bits=int((ref != up).sum()), health=health)
        print(json.dumps(rec), flush=True)
        if not rec['decoded_equal']:
            print('mismatching bits', int((dec != ref).sum()))
            return False
        up = ref
    return True

t0 = time.time()
ok = closure(6, 0, False) and closure(6, 1, True)
print('closure', ok, round(time.time() - t0), 's', flush=True)

def level0(seed, mode, n=16, times_n=20):
    rng = np.random.default_rng(seed)
    top = codec.random_upper(cand, 1, rng)
    full = codec.encode(cand, top)
    up = full[:, (np.arange(n) + Q // 2 - n // 2) % Q]
    lo_site, hi_site = (n // 2 - 1) * Q, (n // 2 + 1) * Q - 1
    X0 = codec.encode(cand, up); N = X0.shape[1]
    times = np.sort(rng.integers(0, p.U - 1, times_n))
    per = trials // len(times)
    P = C.pack(X0); t_prev = 0; total = fails = 0; ex = []
    for t in times:
        P = C.run_packed(P, int(t - t_prev), threads=THREADS); t_prev = int(t)
        X = C.unpack(P, N)
        ref1 = C.unpack(C.run_packed_scalar(P.copy(), 1), N)
        for _ in range(per):
            x = int(rng.integers(lo_site, hi_site))
            sites = [x, x + 1] if rng.random() < 0.5 else [x]
            Y = X.copy()
            for s in sites:
                if mode == 'random': Y[:, s] = rng.random(cand.W) < 0.5
                elif mode == 'invert': Y[:, s] = ~Y[:, s]
                elif mode == 'zero': Y[:, s] = False
                else: Y[:, s] = True
            Y1 = C.unpack(C.run_packed_scalar(C.pack(Y), 1), N)
            total += 1
            if (Y1 != ref1).any():
                fails += 1
                if len(ex) < 5: ex.append(dict(t=int(t), sites=sites, bits=int((Y1 != ref1).sum())))
    print(json.dumps(dict(level0_mode=mode, trials=total, failures=fails, examples=ex)), flush=True)

if ok and trials:
    for mode in ('random', 'invert', 'zero', 'one'):
        t0 = time.time(); level0(7, mode); print(round(time.time() - t0), 's', flush=True)
    # negative control: three adjacent sites must be able to fail for a 3-copy stride-2 code? (2 of 3 copies hit needs sites x, x+2)
