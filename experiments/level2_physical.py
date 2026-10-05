"""A full physical level-2 step: U^2 ticks of a ring of n2 level-2 cells.

Random level-2 cells are encoded twice (level 2 -> n2*Q level-1 cells -> n2*Q^2
physical sites) and the physical ring is run for U level-1 steps of U ticks
each, with no hand-off to the level-1 automaton. Checked:

  * every --check-every level-1 steps: the decoded level-1 ring equals the
    level-1 automaton (the same rule on the n2*Q level-1 cells, run on the C
    kernel), and the physical colonies are healthy;
  * at the same points (kernel 'roles'): the next level-1 step is run again
    from the same state on the reference CUDA kernel (gpu.GpuSim) and the two
    physical states must be equal bit for bit;
  * at the end: the twice-decoded level-2 ring equals the rule applied to the
    initial level-2 ring.

The state is checkpointed every --checkpoint-minutes; --resume continues.
Usage: level2_physical.py --candidate G16 [--n2 1] [--seed 0] [--tag NAME]
Receipt: figs/three_level/<tag>.json
"""
import argparse
import hashlib
import json
import os
import subprocess
import time
import numpy as np
from gacsca import candidates, codec, gpu, gpu_roles

OUT = os.path.join(candidates.ROOT, 'figs', 'three_level')


def gpu_name():
    try:
        return subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],
                              capture_output=True, text=True).stdout.strip()
    except OSError:
        return 'unknown'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidate', default=candidates.CURRENT)
    ap.add_argument('--n2', type=int, default=1, help='level-2 cells in the ring')
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--kernel', default='roles', choices=('roles', 'reference'))
    ap.add_argument('--check-every', type=int, default=64, help='level-1 steps between checks')
    ap.add_argument('--no-parity', action='store_true', help='skip the reference-kernel comparison')
    ap.add_argument('--checkpoint-minutes', type=float, default=20)
    ap.add_argument('--max-steps', type=int, default=0, help='stop after this many level-1 steps (smoke test)')
    ap.add_argument('--resume', action='store_true')
    ap.add_argument('--tag', default='')
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    cand = candidates.load(args.candidate)
    p, C = cand.p, cand.c_backend()
    Q, U = p.Q, p.U
    tag = args.tag or f'{args.candidate}_level2_physical_n{args.n2}_s{args.seed}'
    path, ckpt = os.path.join(OUT, tag + '.json'), os.path.join(OUT, tag + '.ckpt.npz')
    n1, N = args.n2 * Q, args.n2 * Q * Q
    rng = np.random.default_rng(args.seed)
    L2 = codec.random_upper(cand, args.n2, rng)
    L1 = codec.encode(cand, L2)
    F_L2 = cand.step_numpy(L2)
    total = args.max_steps or U

    if args.kernel == 'roles':
        sim = gpu_roles.RoleSim(cand, n1)
        kernel_sha = sim.source_sha256
        ref = None if args.no_parity else gpu.GpuSim(cand, 1, n1, mode='grid')
    else:
        sim = gpu.GpuSim(cand, 1, n1, mode='grid')
        kernel_sha, ref = sim.source_sha256, None
    get = (lambda: sim.state()) if args.kernel == 'roles' else (lambda: sim.state()[0])

    rows, k, wall0 = [], 0, 0.0
    ref1 = C.pack(L1)                          # level-1 automaton, packed, at level-1 time k
    if args.resume and os.path.exists(ckpt):
        z = np.load(ckpt, allow_pickle=False)
        assert str(z['tag']) == tag and int(z['seed']) == args.seed
        P, ref1, k, wall0 = z['state'], z['ref1'], int(z['k']), float(z['wall'])
        rows = json.loads(str(z['rows']))
        print(f'resumed at level-1 step {k}', flush=True)
    else:
        P = C.pack(codec.encode(cand, L1))
    sim.set_state(P)
    t_start = t_ckpt = time.time()
    gpu_ms = 0.0

    def checkpoint(P):
        tmp = ckpt + '.tmp.npz'
        np.savez(tmp, state=P, ref1=ref1, k=k, wall=wall0 + time.time() - t_start, rows=json.dumps(rows),
                 tag=tag, seed=args.seed)
        os.replace(tmp, ckpt)

    def check(P):
        """Level-1 closure and health of the physical state P at level-1 time k."""
        X = C.unpack(P, N)
        dec1 = codec.decode(cand, X)
        want1 = C.unpack(ref1, n1)
        health = codec.colony_health(cand, X)
        row = dict(level1_step=k, level1_exact=bool(np.array_equal(dec1, want1)),
                   level1_cells_wrong=int((dec1 != want1).any(axis=0).sum()), health=health)
        return row, dec1

    pending_parity = None                      # (state at the last check, row to complete)
    while k < total:
        sim.run(U)
        gpu_ms += sim.last_ms
        k += 1
        ref1 = C.run_packed_scalar(ref1.copy(), 1)
        if pending_parity is not None:
            P_prev, row = pending_parity
            ref.set_state(P_prev)
            ref.run(U)
            row['next_step_equals_reference_kernel'] = bool(np.array_equal(get(), ref.state()[0]))
            pending_parity = None
        if k % args.check_every == 0 or k == total:
            P = get()
            row, dec1 = check(P)
            row.update(us_per_tick=round(sim.last_ms * 1000 / U, 2),
                       hours=round((wall0 + time.time() - t_start) / 3600, 3))
            rows.append(row)
            eta = (time.time() - t_start) / max(1, k - (rows[0]['level1_step'] - args.check_every if len(rows) > 1 else 0))
            print(json.dumps(row), f'| {k}/{total}', flush=True)
            if ref is not None and k < total:
                pending_parity = (P, row)
            if not row['level1_exact']:
                print('level-1 closure failed; stopping', flush=True)
                break
            if time.time() - t_ckpt > 60 * args.checkpoint_minutes:
                checkpoint(P)
                t_ckpt = time.time()
    P = get()
    checkpoint(P)
    X = C.unpack(P, N)
    dec1 = codec.decode(cand, X)
    dec2 = codec.decode(cand, dec1)
    full = k == U
    rec = dict(candidate=args.candidate,
               identity={a: b for a, b in candidates.summary(cand).items() if a != 'schema'},
               kernel=args.kernel, kernel_source_sha256=kernel_sha, gpu=gpu_name(),
               n2=args.n2, seed=args.seed, physical_sites=N, level1_cells=n1, Q=Q, U=U,
               level1_steps_run=k, ticks_run=k * U, full_level2_step=full,
               check_every=args.check_every, checks=rows,
               all_level1_checks_exact=all(r['level1_exact'] for r in rows),
               all_healthy=all(r['health']['addr'] and r['health']['age'] for r in rows),
               parity_checks=sum('next_step_equals_reference_kernel' in r for r in rows),
               parity_all_equal=all(r.get('next_step_equals_reference_kernel', True) for r in rows),
               level2_changed_bits=int((F_L2 != L2).sum()),
               wall_hours=round((wall0 + time.time() - t_start) / 3600, 3),
               state_sha256=hashlib.sha256(P.tobytes()).hexdigest())
    if full:
        rec.update(level2_exact=bool(np.array_equal(dec2, F_L2)),
                   level2_cells_wrong=int((dec2 != F_L2).any(axis=0).sum()),
                   level2_bits_wrong=int((dec2 != F_L2).sum()),
                   level1_equals_automaton=bool(np.array_equal(dec1, C.unpack(ref1, n1))),
                   automaton_decodes_to_F=bool(np.array_equal(codec.decode(cand, C.unpack(ref1, n1)), F_L2)))
    with open(path, 'w') as fh:
        json.dump(rec, fh, indent=1)
    print(json.dumps({a: b for a, b in rec.items() if a not in ('checks', 'identity')}), flush=True)
    print(path)


if __name__ == '__main__':
    main()
