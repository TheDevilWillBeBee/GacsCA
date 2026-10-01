"""Space-time pictures of a front candidate on the GPU, with injected errors.

Figures (PNG, written to figs/spacetime/):

  <cand>_period.png   one fault-free work period: what changes where (mail,
                      lanes, front, Hold/scratch, Info commit, flags), plus a
                      stride-1 zoom of the gathers and the first front passes.
  <cand>_defects.png  several periods of rings with injected errors, each
                      compared site by site with a fault-free reference ring
                      (same initial state): where local structure (Address,
                      Age, flags) differs, where only simulation fields
                      differ, and how many decoded upper cells are wrong after
                      every period.
  <cand>_e0_zoom.png  stride-1 close-ups of single level-0 errors: how the
                      difference spreads and whether it disappears.

Errors replace the whole state of a site by random bits (gpu.noise). Time
runs downward. Snapshots in the multi-period figure are taken every
`stride` ticks, so transient differences shorter than that are not shown
there (the zoom figures use stride 1).
"""
import argparse
import json
import os
import time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from gacsca import candidates, codec, gpu

OUT = os.path.join(candidates.ROOT, 'figs', 'spacetime')
STRUCT = ('addr', 'age', 'f1', 'f2')


def rows_of(cand, fields):
    return [cand.row[(f, i)] for f, w in cand.schema if f in fields for i in range(w)]


def healthy_upper(cand, n1, rng):
    """Random upper cells with consecutive upper Addresses and equal Age."""
    up = codec.random_upper(cand, n1, rng)
    cand.set_field(up, 'addr', np.arange(n1) % cand.p.Q)
    cand.set_field(up, 'age', np.full(n1, 5))
    for f in ('f1', 'f2', 'wf1', 'wf2'):
        cand.set_field(up, f, np.zeros(n1, dtype=int))
    return up


def unpack_rows(snap_ring, N):
    """(T, nrows, NW) uint64 -> (T, nrows, N) bool."""
    T, R, NW = snap_ring.shape
    b = np.unpackbits(snap_ring.view(np.uint8).reshape(T, R, NW * 8), axis=2, bitorder='little')
    return b[:, :, :N].astype(bool)


def any_rows(B, rows_idx):
    return B[:, rows_idx, :].any(axis=1)


# ------------------------------------------------------------------ period
def fig_period(cand, C, args, rng):
    p = cand.p
    ncol = 4
    up = healthy_upper(cand, ncol, rng)
    X0 = C.pack(codec.encode(cand, up))
    rows = list(range(cand.W))
    groups = dict(mail=rows_of(cand, ('mr', 'ml')), lanes=rows_of(cand, ('ln', 'h1', 'h2')),
                  front=rows_of(cand, ('reg',)), work=rows_of(cand, ('hold', 'scr', 'pend', 'pkind', 'pval')),
                  info=rows_of(cand, ('info',)), flags=rows_of(cand, ('f1', 'f2', 'wf1', 'wf2')))
    sim = gpu.GpuSim(cand, 1, ncol)
    sim.set_state(X0)
    stride = max(1, p.U // 1024)
    snap = sim.run(p.U, rows=rows, stride=stride)
    B = unpack_rows(snap[:, 0], sim.N)
    zoom_t = min(p.U, p.E0 + 3 * p.Q)
    sim.set_state(X0)
    snapz = sim.run(zoom_t, rows=rows, stride=1)
    Bz = unpack_rows(snapz[:, 0], sim.N)[:, :, :2 * p.Q]
    # end of the period: last passes, commit at Age U-1, next gathers
    end0, end_len = p.U - 2 * p.Q, 3 * p.Q
    sim.set_state(X0)
    sim.run(end0)
    snape = sim.run(end_len, rows=rows, stride=1)
    Be = unpack_rows(snape[:, 0], sim.N)[:, :, :2 * p.Q]

    def composite(B, mail_values, front_color=(0, 0, 0)):
        T, _, N = B.shape
        img = np.ones((T, N, 3))
        if mail_values:     # mail tracks carry Info bits; they shift one cell per tick
            mr = B[:, rows_of(cand, ('mr',)), :].any(axis=1)
            ml = B[:, rows_of(cand, ('ml',)), :].any(axis=1)
            img[mr] = (0.8, 0.93, 0.8)
            img[ml] = (0.93, 0.88, 0.75)
            img[mr & ml] = (0.75, 0.85, 0.7)
        front = B[:, groups['front'], :].any(axis=1)
        front = front | np.roll(front, 1, axis=1) | np.roll(front, -1, axis=1)
        img[front] = front_color
        prev = np.concatenate([B[:1], B[:-1]])
        ch = B != prev
        colors = dict(lanes=(0.3, 0.75, 0.95), work=(0.2, 0.3, 0.95),
                      info=(0.9, 0.1, 0.1), flags=(0.8, 0.1, 0.8))
        for g, col in colors.items():
            m = ch[:, groups[g], :].any(axis=1)
            m[0] = False
            img[m] = col
        return img

    fig, ax = plt.subplots(1, 3, figsize=(16, 7.5), gridspec_kw=dict(width_ratios=[2, 1, 1]))
    ax[0].imshow(composite(B, False, (0.7, 0.7, 0.7)), aspect='auto', interpolation='nearest',
                 extent=(0, sim.N, p.U, 0))
    ax[0].set_title(f'{args.candidate}: one work period, {ncol} colonies (Q={p.Q}, U={p.U}),\n'
                    f'sampled every {stride} ticks (front in gray; writes between samples in color)',
                    fontsize=10)
    ax[0].set_xlabel('site'); ax[0].set_ylabel('tick')
    for c in range(1, ncol):
        ax[0].axvline(c * p.Q, color='0.6', lw=0.5)
    ax[0].axhline(p.E0, color='0.3', lw=0.6, ls='--')
    ax[0].text(sim.N * 0.01, p.E0, ' evaluation window starts', va='bottom', fontsize=8)
    ax[1].imshow(composite(Bz, True), aspect='auto', interpolation='nearest', extent=(0, 2 * p.Q, zoom_t, 0))
    ax[1].set_title('stride 1, start of period:\nthree-way mail gathers, then front passes', fontsize=10)
    ax[1].set_xlabel('site')
    ax[2].imshow(composite(Be, True), aspect='auto', interpolation='nearest',
                 extent=(0, 2 * p.Q, end0 + end_len, end0))
    ax[2].set_title('stride 1, end of period:\nlast passes, commit at Age U-1, next gathers', fontsize=10)
    ax[2].set_xlabel('site')
    for a in ax[1:]:
        a.axvline(p.Q, color='0.6', lw=0.5)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in
               [(0, 0, 0), (0.8, 0.93, 0.8), (0.93, 0.88, 0.75), (0.3, 0.75, 0.95), (0.2, 0.3, 0.95),
                (0.9, 0.1, 0.1), (0.8, 0.1, 0.8)]]
    fig.legend(handles, ['front (register file present)', 'right mail bit = 1', 'left mail bit = 1',
                         'lane / history captured', 'Hold / scratch written', 'Info changed (commit)',
                         'flags changed'],
               loc='lower center', ncol=7, fontsize=8, frameon=False)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    path = os.path.join(OUT, f'{args.candidate}_period.png')
    fig.savefig(path, dpi=110)
    plt.close(fig)
    return path


# ----------------------------------------------------------------- defects
def scenarios(cand, ncol, seed):
    p = cand.p
    Q, E0 = p.Q, p.E0
    t_eval = E0 + 37 * Q + Q // 3        # inside the evaluation window
    c3 = 3 * Q
    singles = [(c3 + Q // 2, 1, 200, 1, 1.0),              # gather phase, mid colony
               (c3 + 5 * Q // 4, 1, t_eval, 1, 1.0),        # evaluation, colony 4
               (5 * Q + 2, 1, t_eval + 7 * Q, 1, 1.0),      # evaluation, near a colony boundary
               (6 * Q + Q // 2, 2, p.U - 40, 1, 1.0)]       # pair, just before the commit
    side = min(200, Q // 4)
    return [
        ('four isolated level-0 errors', gpu.noise(seed, boxes=singles)),
        ('E0 grid G=50 (dense level-0 noise, every period)', gpu.noise(seed + 1, e0_grid=50)),
        (f'{side}x{side} burst (level-1 size) at colony 3, eval', gpu.noise(seed + 2, boxes=[(c3 + Q // 4, side, t_eval, side, 1.0)])),
        ('whole colony 3 randomized for 200 ticks', gpu.noise(seed + 3, boxes=[(c3, Q, t_eval, 200, 1.0)])),
        ('colonies 3-4 randomized for 2Q ticks', gpu.noise(seed + 4, boxes=[(c3, 2 * Q, t_eval, 2 * Q, 1.0)])),
    ], singles


def fig_defects(cand, C, args, rng):
    p = cand.p
    ncol = args.colonies
    up = healthy_upper(cand, ncol, rng)
    X0 = C.pack(codec.encode(cand, up))
    sc, singles = scenarios(cand, ncol, args.seed)
    R = 1 + len(sc)
    sim = gpu.GpuSim(cand, R, ncol)
    sim.set_state(X0)
    sim.set_noise([gpu.noise()] + [cfg for _, cfg in sc])
    rows = list(range(cand.W))
    srows = rows_of(cand, STRUCT)
    flags = rows_of(cand, ('f1', 'f2'))
    other = [r for r in rows if r not in srows]
    stride = max(1, args.periods * p.U // 1024)
    per_ring = [[] for _ in range(R)]
    upper_wrong = [[] for _ in range(R)]
    upper_ref = up
    t0 = time.time()
    for k in range(args.periods):
        snap = sim.run(p.U, rows=rows, stride=stride)
        S = sim.state()
        upper_ref = cand.step_numpy(upper_ref)
        ref_dec = codec.decode(cand, C.unpack(S[0], sim.N))
        assert np.array_equal(ref_dec, upper_ref), 'reference ring must close'
        for r in range(R):
            dec = codec.decode(cand, C.unpack(S[r], sim.N))
            upper_wrong[r].append(int((dec != upper_ref).any(axis=0).sum()))
        B0 = unpack_rows(snap[:, 0], sim.N)
        for r in range(1, R):
            Br = unpack_rows(snap[:, r], sim.N)
            d = Br != B0
            per_ring[r].append((any_rows(d, srows), any_rows(d, other), any_rows(Br, flags)))
        print(f'period {k + 1}: upper cells wrong per ring {[u[-1] for u in upper_wrong]} '
              f'({time.time() - t0:.0f} s)', flush=True)

    fig, ax = plt.subplots(1, R - 1, figsize=(3.3 * (R - 1), 8), sharey=True)
    for r in range(1, R):
        ds = np.concatenate([x[0] for x in per_ring[r]])
        do = np.concatenate([x[1] for x in per_ring[r]])
        fl = np.concatenate([x[2] for x in per_ring[r]])
        img = np.full(ds.shape + (3,), 0.97)
        img[do] = (1.0, 0.65, 0.2)
        img[ds] = (0.75, 0.0, 0.0)
        img[fl] = (0.0, 0.0, 0.0)
        a = ax[r - 1]
        a.imshow(img, aspect='auto', interpolation='nearest', extent=(0, sim.N, args.periods * p.U, 0))
        for c in range(1, ncol):
            a.axvline(c * p.Q, color='0.8', lw=0.4)
        for k in range(1, args.periods):
            a.axhline(k * p.U, color='0.5', lw=0.5, ls=':')
        a.set_title(f'{sc[r - 1][0]}\nwrong upper cells per period: {upper_wrong[r]}', fontsize=8)
        a.set_xlabel('site')
    ax[0].set_ylabel('tick')
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in [(0.75, 0, 0), (1, 0.65, 0.2), (0, 0, 0)]]
    fig.legend(handles, ['Address/Age/flags differ from reference', 'only simulation fields differ',
                         'Flag1 or Flag2 set'], loc='lower center', ncol=3, fontsize=9, frameon=False)
    fig.suptitle(f'{args.candidate} (Q={p.Q}, U={p.U}): {ncol} colonies, {args.periods} periods, '
                 f'errors vs a fault-free reference ring (sampled every {stride} ticks)', fontsize=10)
    fig.tight_layout(rect=(0, 0.03, 1, 0.97))
    path = os.path.join(OUT, f'{args.candidate}_defects.png')
    fig.savefig(path, dpi=110)
    plt.close(fig)
    return path, dict(scenarios=[s for s, _ in sc], upper_wrong_per_period=upper_wrong[1:]), X0, singles


def fig_e0_zoom(cand, C, args, X0, singles):
    """Stride-1 difference maps around each single error of scenario 1."""
    p = cand.p
    ncol = args.colonies
    rows = list(range(cand.W))
    srows = rows_of(cand, STRUCT)
    flags = rows_of(cand, ('f1', 'f2'))
    other = [r for r in rows if r not in srows]
    fig, ax = plt.subplots(1, len(singles), figsize=(3.4 * len(singles), 6.3))
    info = []
    for i, (x0, w, te, h, _) in enumerate(singles):
        sim = gpu.GpuSim(cand, 2, ncol)
        sim.set_state(X0)
        sim.set_noise([gpu.noise(), gpu.noise(args.seed, boxes=[(x0, w, te, h, 1.0)])])
        before = max(0, te - 8)
        sim.run(before)
        span = min(args.zoom_ticks, p.U * args.periods - before)
        snap = sim.run(span, rows=rows, stride=1)
        B0 = unpack_rows(snap[:, 0], sim.N)
        B1 = unpack_rows(snap[:, 1], sim.N)
        d = B1 != B0
        ds, do, fl = any_rows(d, srows), any_rows(d, other), any_rows(B1, flags)
        lo = max(0, x0 - args.zoom_sites // 2)
        hi = min(sim.N, lo + args.zoom_sites)
        img = np.full(ds.shape + (3,), 0.97)
        img[do] = (1.0, 0.65, 0.2)
        img[ds] = (0.75, 0.0, 0.0)
        img[fl] = (0.0, 0.0, 0.0)
        a = ax[i]
        a.imshow(img[:, lo:hi], aspect='auto', interpolation='nearest', extent=(lo, hi, before + span, before))
        last_s = np.nonzero(ds.any(axis=1))[0]
        last_o = np.nonzero(do.any(axis=1))[0]
        last_a = np.nonzero(d.any(axis=(1, 2)))[0]
        rec = dict(site=x0, width=w, tick=te,
                   structure_differs_until=int(before + last_s[-1] + 1) if len(last_s) else None,
                   any_difference_until=int(before + last_a[-1] + 1) if len(last_a) else None,
                   any_difference_at_end=bool(d[-1].any()),
                   sites_differing_at_end=int((d[-1].any(axis=0)).sum()))
        info.append(rec)
        a.set_title(f'error at site {x0}, tick {te}\nstructure differs until tick '
                    f'{rec["structure_differs_until"]}\nany field differs until tick '
                    f'{rec["any_difference_until"]}\nsites differing after {span} ticks: '
                    f'{rec["sites_differing_at_end"]}', fontsize=8)
        a.set_xlabel('site')
        if p.Q * (x0 // p.Q) > lo:
            a.axvline(p.Q * (x0 // p.Q), color='0.6', lw=0.5)
    ax[0].set_ylabel('tick')
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in [(0.75, 0, 0), (1, 0.65, 0.2), (0, 0, 0)]]
    fig.legend(handles, ['Address/Age/flags differ', 'only simulation fields differ', 'Flag1 or Flag2 set'],
               loc='lower center', ncol=3, fontsize=9, frameon=False)
    fig.suptitle(f'{args.candidate}: single level-0 errors, stride 1', fontsize=10)
    fig.tight_layout(rect=(0, 0.04, 1, 0.97))
    path = os.path.join(OUT, f'{args.candidate}_e0_zoom.png')
    fig.savefig(path, dpi=110)
    plt.close(fig)
    return path, info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidate', default='R1')
    ap.add_argument('--colonies', type=int, default=8)
    ap.add_argument('--periods', type=int, default=4)
    ap.add_argument('--seed', type=int, default=11)
    ap.add_argument('--zoom-ticks', type=int, default=600)
    ap.add_argument('--zoom-sites', type=int, default=160)
    ap.add_argument('--skip-period', action='store_true')
    ap.add_argument('--zoom-only', action='store_true', help='only the stride-1 level-0 figure')
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    cand = candidates.load(args.candidate)
    C = cand.c_backend()
    rng = np.random.default_rng(args.seed)
    rec = dict(candidate=args.candidate, identity={k: v for k, v in candidates.summary(cand).items()
                                                    if k != 'schema'}, args=vars(args))
    if args.zoom_only:
        up = healthy_upper(cand, args.colonies, rng)
        X0 = C.pack(codec.encode(cand, up))
        _, singles = scenarios(cand, args.colonies, args.seed)
        zpath, zinfo = fig_e0_zoom(cand, C, args, X0, singles)
        print(zpath, json.dumps(zinfo), flush=True)
        return
    if not args.skip_period:
        rec['period_png'] = fig_period(cand, C, args, rng)
        print(rec['period_png'], flush=True)
    path, res, X0, singles = fig_defects(cand, C, args, rng)
    rec['defects_png'] = path
    rec.update(res)
    print(path, flush=True)
    zpath, zinfo = fig_e0_zoom(cand, C, args, X0, singles)
    rec['e0_zoom_png'], rec['e0_zoom'] = zpath, zinfo
    print(zpath, json.dumps(zinfo), flush=True)
    with open(os.path.join(OUT, f'{args.candidate}_spacetime.json'), 'w') as fh:
        json.dump(rec, fh, indent=1)


if __name__ == '__main__':
    main()
