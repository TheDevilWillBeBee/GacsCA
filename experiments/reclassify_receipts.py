"""Re-certify the Gray class of every campaign error with the fixed classifier (AUDIT2 finding 2).

For each error ring of each level-1 campaign receipt the realized error set is rebuilt and
classified with gray_errors.classify:
  * dense boxes and sparse clusters: the points of the ring's boxes;
  * Bernoulli boxes: the kernel's own error masks;
  * rings with dense level-0 noise (--e0-all): the box plus the E0-grid hits around it, taken
    from the kernel's masks. The box alone is then classified against that full local set
    (Gray's isolation (iv) fails when a hit lies within 23 of the box), and so is the box
    together with the hits linked to it (S'). The E0 grid keeps distinct hits at least 25 apart
    (tested), so every hit not linked to the box is an isolated level-0 error, and S' is the
    only error set in the run that is not level-0.
Writes figs/level1_campaign/reclassified.json and prints, per
receipt, how many errors keep and change their recorded verdict.
"""
import glob
import json
import os
import numpy as np
from gacsca import candidates, gpu, gray_errors

DIR = os.path.join(candidates.ROOT, 'figs', 'level1_campaign')
SKIP = ('smoke',)


def ring_points(r):
    return {(x + dx, t + dt) for (x, w, t, h, _) in r['boxes'] for dx in range(w) for dt in range(h)}


def main():
    out = {}
    sims = {}
    for fn in sorted(glob.glob(os.path.join(DIR, '*.json'))):
        name = os.path.basename(fn)[:-5]
        if name.startswith(SKIP) or name == 'reclassified':
            continue
        d = json.load(open(fn))
        if 'rings' not in d or not any('gray' in r for r in d['rings']):
            continue
        cand = candidates.load(d['candidate'])
        Q, U = cand.p.Q, cand.p.U
        N = d['physical_sites']
        rows = []
        for i, r in enumerate(d['rings'], 1):
            if r.get('kind') != 'E1' or 'boxes' not in r:
                continue
            old = r.get('gray', {}).get('level1')
            dense = all(b[4] >= 1.0 for b in r['boxes'])
            noisy = bool(r.get('with_level0_noise'))
            row = dict(ring=i, phase=r['phase'], place=r['place'], recorded=old)
            if dense and not noisy:
                S = ring_points(r)
                if len(r['boxes']) == 1 and (r['boxes'][0][1] > 104 or r['boxes'][0][3] > 104):
                    g = dict(level1=False, method='extent > 104')     # the driver's own shortcut
                else:
                    g = gray_errors.classify(S, Q=Q, U=U)
                row.update(level1=g['level1'], method=g['method'])
            else:
                key = (d['candidate'], N)
                if key not in sims:
                    sims[key] = gpu.GpuSim(cand, 1, N // Q, mode='grid')
                sim = sims[key]
                cfg = gpu.noise(r['noise_seed'], boxes=r['boxes'], mode=d['args'].get('mode', 'random'),
                                shift_sites=Q, e0_grid=50 if noisy else 0)
                x_lo = min(b[0] for b in r['boxes']) - 48
                x_hi = max(b[0] + b[1] for b in r['boxes']) + 48
                t_lo = max(0, min(b[2] for b in r['boxes']) - 48)
                t_hi = max(b[2] + b[3] for b in r['boxes']) + 48
                m = sim.error_masks(cfg, 0, t_lo, t_hi - t_lo)
                ts, xs = np.nonzero(m[:, max(0, x_lo):min(N, x_hi)])
                E = set(zip((xs + max(0, x_lo)).tolist(), (ts + t_lo).tolist()))
                if not noisy:
                    g = gray_errors.classify(E, Q=Q, U=U)
                    row.update(level1=g['level1'], method=g['method'], realized_points=len(E))
                else:
                    g = gray_errors.classify_burst_in_noise(ring_points(r), E, Q=Q, U=U)
                    row.update(level1=g['alone']['level1'], method=g['alone']['method'],
                               hits_in_window=g['linked_points'] + g['other_points'],
                               hits_linked_to_the_box=g['linked_points'],
                               with_linked_hits=dict(level1=g['with_linked']['level1'],
                                                     method=g['with_linked']['method']))
            rows.append(row)
        same = sum(r['level1'] == r['recorded'] for r in rows)
        out[name] = dict(errors=len(rows), level1=sum(bool(r['level1']) for r in rows),
                         unchanged=same, changed=len(rows) - same,
                         with_linked_hits_level1=sum(bool(r.get('with_linked_hits', {}).get('level1'))
                                                     for r in rows if 'with_linked_hits' in r),
                         rows=rows)
        print(f"{name:42s} errors {len(rows):3d}  level-1 {out[name]['level1']:3d}  "
              f"verdict unchanged {same:3d}  changed {len(rows) - same:3d}"
              + (f"  burst+linked hits level-1 {out[name]['with_linked_hits_level1']}"
                 if any('with_linked_hits' in r for r in rows) else ''), flush=True)
    with open(os.path.join(DIR, 'reclassified.json'), 'w') as fh:
        json.dump(out, fh, indent=1)


if __name__ == '__main__':
    main()
