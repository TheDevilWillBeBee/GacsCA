"""Closed two-level ring for one fixed front candidate.

Top: n2 arbitrary (random) level-2 cells. Level 1 = encode(top), level 0 =
encode(level 1), with the *same* encode function and the same rule. The
physical ring is evolved by the C kernel only: no event skipping, no host
transition, no reinitialization, no depth argument.

Every U physical ticks the physical ring is decoded and compared with the
level-1 ring advanced by one step of the rule (independent NumPy netlist
evaluation with a full ROM lookup at every site). Every U level-1 steps the
decoded level-1 ring is decoded again and compared with the level-2 ring
advanced by the rule. The first mismatch stops the run and the full raw
state is saved.
"""
import argparse
import hashlib
import json
import os
import resource
import time
import numpy as np
from gacsca.fixed_rule.design_optimization import candidates, codec

OUT = os.path.join(candidates.ROOT, 'figs', 'fixed_rule', 'design_optimization', 'two_level')


def sha(a):
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidate', default='R1')
    ap.add_argument('--n2', type=int, default=1)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--level2-steps', type=int, default=1)
    ap.add_argument('--threads', type=int, default=8)
    ap.add_argument('--max-level1-steps', type=int, default=0,
                    help='stop early (pilot); 0 = full level-2 steps')
    ap.add_argument('--checkpoint-every', type=int, default=1024)
    ap.add_argument('--tag', default='')
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    name = f'{args.candidate}_n2_{args.n2}_seed{args.seed}{args.tag}'
    receipt_path = os.path.join(OUT, name + '.json')
    ckpt_path = os.path.join(OUT, name + '_ckpt.npz')
    log_path = os.path.join(OUT, name + '.log')

    cand = candidates.load(args.candidate)
    p = cand.p
    C = cand.c_backend()
    rng = np.random.default_rng(args.seed)
    top = codec.random_upper(cand, args.n2, rng)
    lvl1 = codec.encode(cand, top)
    phys0 = codec.encode(cand, lvl1)
    receipt = dict(candidate=args.candidate, identity={k: v for k, v in candidates.summary(cand).items()
                                                        if k != 'schema'},
                   c_kernel_source_sha256=C.source_sha256, n2=args.n2, seed=args.seed,
                   level1_cells=int(lvl1.shape[1]), physical_cells=int(phys0.shape[1]),
                   top_sha256=sha(top), level1_initial_sha256=sha(lvl1),
                   physical_initial_sha256=sha(phys0), threads=args.threads,
                   started=time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime()))
    P = C.pack(phys0)
    l1 = lvl1.copy()
    top_ref = top.copy()
    level1_changed = []
    level2 = []
    total = p.U * args.level2_steps
    if args.max_level1_steps:
        total = min(total, args.max_level1_steps)
    t_phys = 0.0
    t_ref = 0.0
    t0 = time.time()
    status = 'running'
    with open(log_path, 'a') as log:
        for step in range(1, total + 1):
            a = time.time()
            P = C.run_packed(P, p.U, threads=args.threads)
            t_phys += time.time() - a
            a = time.time()
            l1_next = cand.step_numpy(l1)
            t_ref += time.time() - a
            phys = C.unpack(P, phys0.shape[1])
            dec = codec.decode(cand, phys)
            health = codec.colony_health(cand, phys)
            ok = np.array_equal(dec, l1_next) and health['addr'] and health['age'] and health['age0'] == 0
            level1_changed.append(int((l1_next != l1).sum()))
            if not ok:
                bad = np.argwhere(dec != l1_next)[:20]
                status = 'level1-mismatch'
                receipt['first_failure'] = dict(level1_step=step, health=health,
                                                mismatches=[(cand.rows[r], int(c)) for r, c in bad])
                np.savez_compressed(os.path.join(OUT, name + f'_fail_step{step}.npz'),
                                    phys=P, level1_prev=l1, level1_expected=l1_next, top=top)
                break
            l1 = l1_next
            if step % p.U == 0:
                top_next = cand.step_numpy(top_ref)
                top_dec = codec.decode(cand, l1)
                l1_health = codec.colony_health(cand, l1)
                ok2 = np.array_equal(top_dec, top_next)
                level2.append(dict(level2_step=step // p.U, equal=bool(ok2), level1_health=l1_health,
                                   changed_bits=int((top_next != top_ref).sum()),
                                   top_sha256=sha(top_next)))
                print(json.dumps(level2[-1]), file=log, flush=True)
                if not ok2:
                    status = 'level2-mismatch'
                    np.savez_compressed(os.path.join(OUT, name + f'_fail_l2_{step}.npz'),
                                        phys=P, level1=l1, top_prev=top_ref, top_expected=top_next)
                    break
                top_ref = top_next
            if step % args.checkpoint_every == 0 or step == total:
                el = time.time() - t0
                msg = dict(level1_step=step, physical_ticks=step * p.U, elapsed_s=round(el, 1),
                           phys_s=round(t_phys, 1), ref_s=round(t_ref, 1),
                           us_per_tick=round(t_phys / (step * p.U) * 1e6, 3),
                           eta_s=round(el / step * (total - step), 0),
                           changed_mean=float(np.mean(level1_changed[-args.checkpoint_every:])),
                           health=health)
                print(json.dumps(msg), file=log, flush=True)
                np.savez_compressed(ckpt_path, phys=P, level1=l1, top=top_ref, step=step)
        else:
            status = 'completed'
    receipt.update(status=status, level1_steps_checked=len(level1_changed),
                   physical_ticks=len(level1_changed) * p.U,
                   level1_changed_bits=dict(total=int(np.sum(level1_changed)),
                                            min=int(np.min(level1_changed)) if level1_changed else 0,
                                            max=int(np.max(level1_changed)) if level1_changed else 0,
                                            zero_change_steps=int(np.sum(np.array(level1_changed) == 0))),
                   level2=level2, physical_seconds=round(t_phys, 1),
                   reference_seconds=round(t_ref, 1), wall_seconds=round(time.time() - t0, 1),
                   final_physical_sha256=sha(P),
                   peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                   finished=time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime()))
    with open(receipt_path, 'w') as fh:
        json.dump(receipt, fh, indent=1)
    print(json.dumps({k: receipt[k] for k in ('status', 'level1_steps_checked', 'physical_ticks',
                                               'level2', 'wall_seconds')}))


if __name__ == '__main__':
    main()
