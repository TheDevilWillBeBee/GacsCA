"""Continuous work periods of a G-family candidate with trickle-down probes.

Physical execution is the C kernel only (no skipping, no host transitions).
Read-only probes between kernel calls check, per colony:
  * after the special procedure (Age T_sig+1): logical SimBits at Addresses
    Q-3 and 3 equal the upper cell's new Flag1 and Flag2 (Gray p. 35);
  * during the Workspace-flag window: Wf1 is set in the five right-end cells
    exactly of colonies whose new upper Flag1 is 1, Wf2 in the five left-end
    cells exactly where new upper Flag2 is 1 and physical Flag1 is 0
    (Gray p. 41), and physical Flag1/Flag2 waves appear there;
  * at the boundary: decoded upper ring == rule applied upstairs, colony
    geometry healthy, all fivefold Info copies agree, all flags back to 0.
"""
import argparse
import hashlib
import json
import os
import time
import numpy as np
from gacsca import candidates, codec

OUT = os.path.join(candidates.ROOT, 'figs', 'g_periods')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidate', default='G1')
    ap.add_argument('--colonies', type=int, default=12)
    ap.add_argument('--periods', type=int, default=3)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--threads', type=int, default=8)
    ap.add_argument('--coherent', action='store_true',
                    help='upper Address consecutive, common Age, flags 0; other fields random')
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    cand = candidates.load(args.candidate)
    p, C = cand.p, cand.c_backend()
    n1, Q = args.colonies, p.Q
    rng = np.random.default_rng(args.seed)
    up = codec.random_upper(cand, n1, rng)
    if args.coherent:
        base = int(rng.integers(0, Q))
        cand.set_field(up, 'addr', (base + np.arange(n1)) % Q)
        cand.set_field(up, 'age', np.full(n1, getattr(p, 'age_code', lambda t: t)(int(rng.integers(0, p.U)))))
        for f in ('f1', 'f2', 'wf1', 'wf2'):
            up[cand.row[(f, 0)]] = False
    P = C.pack(codec.encode(cand, up))
    N = n1 * Q
    probes = [p.T_sig + 1, p.T_wf + 2, p.T_wf + Q // 2, p.T_wf + 2 * Q + 1]
    periods = []
    t_start = time.time()
    for period in range(args.periods):
        ref = cand.step_numpy(up)
        f1_new = ref[cand.row[('f1', 0)]]
        f2_new = ref[cand.row[('f2', 0)]]
        age = 0
        rec = dict(period=period + 1, upper_f1=int(f1_new.sum()), upper_f2=int(f2_new.sum()))
        wave = dict(max_f1_cells=0, max_f2_cells=0)
        for t in probes + [p.U]:
            P = C.run_packed(P, t - age, threads=args.threads)
            age = t
            if t == p.U:
                break
            X = C.unpack(P, N)
            info, _ = codec.logical_info(cand, X)
            f1 = X[cand.row[('f1', 0)]].reshape(n1, Q)
            f2 = X[cand.row[('f2', 0)]].reshape(n1, Q)
            wf1 = X[cand.row[('wf1', 0)]].reshape(n1, Q)
            wf2 = X[cand.row[('wf2', 0)]].reshape(n1, Q)
            wave['max_f1_cells'] = max(wave['max_f1_cells'], int(f1.sum()))
            wave['max_f2_cells'] = max(wave['max_f2_cells'], int(f2.sum()))
            if t == p.T_sig + 1:
                sim = info.reshape(n1, Q)
                assert np.array_equal(sim[:, Q - 3], f1_new), 'SimBit Q-3 != new upper Flag1'
                assert np.array_equal(sim[:, 3], f2_new), 'SimBit 3 != new upper Flag2'
                rec['special_procedure'] = 'ok'
            if t == p.T_wf + 2:
                # Wf1 at right-end cells iff upper Flag1; Wf2 at left end iff Flag2 and not Flag1 there
                assert np.array_equal(wf1[:, Q - 5:].all(axis=1), f1_new.astype(bool))
                assert not wf1[:, :Q - 5].any()
                exp_wf2 = f2_new.astype(bool) & ~f1[:, :5].any(axis=1)
                assert np.array_equal(wf2[:, :5].any(axis=1), exp_wf2)
                assert not wf2[:, 5:].any()
                rec['wf_window'] = dict(colonies_wf1=int(wf1[:, Q - 5:].all(axis=1).sum()),
                                        colonies_wf2=int(wf2[:, :5].any(axis=1).sum()))
        X = C.unpack(P, N)
        dec = codec.decode(cand, X)
        health = codec.colony_health(cand, X)
        rec.update(decoded_equal=bool(np.array_equal(dec, ref)),
                   changed_bits=int((ref != up).sum()), health=health, waves=wave,
                   state_sha256=hashlib.sha256(P.tobytes()).hexdigest())
        periods.append(rec)
        print(json.dumps(rec), flush=True)
        if not rec['decoded_equal'] or not health['info_copies_agree'] or health['flags']:
            break
        up = ref
    receipt = dict(candidate=args.candidate, identity={k: v for k, v in candidates.summary(cand).items()
                                                        if k != 'schema'},
                   c_kernel_source_sha256=C.source_sha256, colonies=n1, seed=args.seed,
                   periods=periods, wall_seconds=round(time.time() - t_start, 1))
    tag = '_coherent' if args.coherent else ''
    path = os.path.join(OUT, f'{args.candidate}_c{n1}_s{args.seed}{tag}.json')
    with open(path, 'w') as fh:
        json.dump(receipt, fh, indent=1)
    print(path)


if __name__ == '__main__':
    main()
