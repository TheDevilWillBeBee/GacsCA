"""Two-level rings on the GPU: does the upper level remove what a physical
error leaves behind?

top (n2 random cells) -> upper = encode(top) (n2 healthy colonies of upper
cells) -> physical = encode(upper) (n2 * Q^2 sites), with one encode, one
width and one rule. Ring 0 is error-free; the other rings get one error
pattern each (gpu.noise), placed in upper step 1 unless stated.

After every upper step (U physical ticks) each ring is decoded and compared
with the reference upper trajectory F^k(upper0), computed by the NumPy
evaluator on the upper ring. Reported per upper step:
  wrong_upper_cells   upper cells that differ from F^k(upper0);
  closure_bad_cells   upper cells where decode(k) != F(decode(k-1)), i.e.
                      the lower level mis-simulated this upper step;
  level2_equal        the upper ring decodes to F^j(top) after j*U upper
                      steps (the level-2 state; the upper colony starts at
                      Age 0 and commits at Age U-1);
  physical_sites_differing  vs the reference ring.

A physical level-1 or colony-scale error may damage one or two upper cells
(an error of the upper level); the claim tested is that the upper level,
running the same rule, then returns to F^k(upper0) exactly.
"""
import argparse
import json
import os
import time
import numpy as np
from gacsca import candidates, codec, gpu

OUT = os.path.join(candidates.ROOT, 'figs', 'two_level_errors')


def scenario_list(p, n2, seed, which):
    Q, U = p.Q, p.U
    t1 = p.E0 + 37 * Q + Q // 3            # physical tick inside upper step 1's evaluation
    c = (Q // 2) * Q                        # physical site of upper cell Q/2 (mid upper colony)
    side = min(200, Q // 2)
    allsc = {
        'E1mid': (f'E1 {side}x{side} burst in colony Q/2 during evaluation',
                  gpu.noise(seed + 1, boxes=[(c + Q // 2 - side // 2, side, t1, side, 1.0)])),
        'E1edge': (f'E1 {side}x{side} burst across a colony boundary',
                   gpu.noise(seed + 2, boxes=[(c + Q - side // 2, side, t1, side, 1.0)])),
        'wipe1': ('colony Q/2 randomized for 200 ticks',
                  gpu.noise(seed + 3, boxes=[(c, Q, t1, 200, 1.0)])),
        'wipe2': ('colonies Q/2, Q/2+1 randomized for 2Q ticks',
                  gpu.noise(seed + 4, boxes=[(c, 2 * Q, t1, 2 * Q, 1.0)])),
        'wipe_gather': ('colony Q/2 randomized for 200 ticks during gather 1',
                        gpu.noise(seed + 5, boxes=[(c, Q, 3 * Q, 200, 1.0)])),
        'E0+wipe1': ('E0 grid G=50 throughout + colony Q/2 wiped for 200 ticks',
                     gpu.noise(seed + 6, e0_grid=50, boxes=[(c, Q, t1, 200, 1.0)])),
        'E0': ('E0 grid G=50 throughout', gpu.noise(seed + 7, e0_grid=50)),
        'wipe4_quarter': ('4 colonies randomized for U/4 ticks (small level-2 error)',
                          gpu.noise(seed + 8, boxes=[(c, 4 * Q, t1, U // 4, 1.0)])),
    }
    return [(k,) + allsc[k] for k in which]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidate', default='G6')
    ap.add_argument('--n2', type=int, default=1)
    ap.add_argument('--upper-steps', type=int, default=6)
    ap.add_argument('--scenarios', default='E1mid,wipe1,wipe2,E0+wipe1')
    ap.add_argument('--seed', type=int, default=5)
    ap.add_argument('--report-every', type=int, default=1)
    ap.add_argument('--tag', default='')
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    cand = candidates.load(args.candidate)
    p, C = cand.p, cand.c_backend()
    sc = scenario_list(p, args.n2, args.seed, args.scenarios.split(','))
    R = 1 + len(sc)
    rng = np.random.default_rng(args.seed)
    top = codec.random_upper(cand, args.n2, rng)
    upper0 = codec.encode(cand, top)
    X0 = codec.encode(cand, upper0)
    assert np.array_equal(codec.decode(cand, X0), upper0)
    sim = gpu.GpuSim(cand, R, X0.shape[1] // p.Q, mode='grid')
    sim.set_state(C.pack(X0))
    sim.set_noise([gpu.noise()] + [s[2] for s in sc])
    name = f"{args.candidate}_n2_{args.n2}_{args.tag or 'run'}_seed{args.seed}.json"
    rec = dict(candidate=args.candidate,
               identity={k: v for k, v in candidates.summary(cand).items() if k != 'schema'},
               gpu_source_sha256=sim.source_sha256, args=vars(args),
               sites=dict(top=top.shape[1], upper=upper0.shape[1], physical=X0.shape[1]),
               grid_blocks=sim.grid_blocks,
               rings=[dict(key='ref', name='reference')] +
               [dict(key=k, name=n, steps=[]) for k, n, _ in sc])
    ref_up = upper0
    prev, last_k = [upper0] * R, 0
    tops = [top]

    def top_ref(k):
        # the upper colony starts at upper Age 0 and commits at Age U-1, so the
        # level-2 state is F^j(top) after j*U upper steps
        while len(tops) <= k // p.U:
            tops.append(cand.step_numpy(tops[-1]))
        return tops[k // p.U]

    t0 = time.time()
    for k in range(1, args.upper_steps + 1):
        sim.run(p.U)
        ref_up = cand.step_numpy(ref_up)
        if k % args.report_every and k != args.upper_steps:
            continue
        S = sim.state()
        X_ref = C.unpack(S[0], sim.N)
        ok_ref = bool(np.array_equal(codec.decode(cand, X_ref), ref_up))
        rec.setdefault('reference_exact', []).append([k, ok_ref])
        line = [f'upper step {k} ({time.time() - t0:.0f} s, {sim.last_ms * 1000 / p.U:.0f} us/tick) '
                f'reference exact {ok_ref}']
        decs = [None] * R
        for r in range(1, R):
            X = C.unpack(S[r], sim.N)
            dec = decs[r] = codec.decode(cand, X)
            want = prev[r]
            for _ in range(k - last_k):
                want = cand.step_numpy(want)
            row = dict(upper_step=k,
                       wrong_upper_cells=np.nonzero((dec != ref_up).any(axis=0))[0].tolist(),
                       wrong_upper_bits=int((dec != ref_up).sum()),
                       closure_bad_cells=np.nonzero((dec != want).any(axis=0))[0].tolist(),
                       level2_equal=bool(np.array_equal(codec.decode(cand, dec), top_ref(k))),
                       physical_sites_differing=int((X != X_ref).any(axis=0).sum()),
                       health=codec.colony_health(cand, X))
            rec['rings'][r]['steps'].append(row)
            w = row['wrong_upper_cells']
            line.append(f"  {sc[r - 1][0]:<14} wrong upper {w[:12]}{'...' if len(w) > 12 else ''} "
                        f"({row['wrong_upper_bits']} bits) closure-bad {row['closure_bad_cells'][:12]} "
                        f"level2 {row['level2_equal']} phys-diff {row['physical_sites_differing']}")
        prev, last_k = decs, k
        print('\n'.join(line), flush=True)
        rec['wall_seconds'] = round(time.time() - t0, 1)
        with open(os.path.join(OUT, name), 'w') as fh:
            json.dump(rec, fh, indent=1)


if __name__ == '__main__':
    main()
