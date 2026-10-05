"""CPU burst experiment on a two-level slice ring (C kernel only, no GPU).

The ring is a slice of n consecutive cells of one healthy upper colony (an encoded random
top cell), encoded physically: n colonies. A reference ring runs without errors. Each
scenario replaces every site of a w x h space-time box by random bits (one burst), at a
named phase of the work period and a named place relative to the boundary between the two
middle colonies jL = n/2-1 and jR = n/2.

Recorded per scenario:
  * local structure (Address, Age, Flag1, Flag2): ticks from the end of the box until the
    last difference from the reference (resolution `stride`), and the leftmost / rightmost
    site that ever differs, relative to the box;
  * Info copies: leftmost / rightmost site that differs during the observation window;
  * at the first period boundary: upper cells whose decoded state differs from the
    reference ring, and the colonies whose working-area logical Info differs;
  * at the second boundary: the same, and whether the whole physical state is identical.

Run from errlevels/repo:  PYTHONPATH=. python3 ../burst_cpu.py --candidate G16 --widths 72,137,200
"""
import argparse
import json
import os
import time
from multiprocessing import Pool
import numpy as np
from gacsca import candidates, codec

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'results')
G = {}


def setup(name, n, seed):
    cand = candidates.load(name, check_manifest=False)
    p, C = cand.p, cand.c_backend()
    rng = np.random.default_rng(seed)
    top = codec.random_upper(cand, 1, rng)
    full = codec.encode(cand, top)
    up = full[:, (np.arange(n) + p.Q // 2 - n // 2) % p.Q]
    X0 = codec.encode(cand, up)
    srows = [cand.row[(f, i)] for f, w in cand.schema if f in ('addr', 'age', 'f1', 'f2') for i in range(w)]
    irows = [cand.row[('info', i)] for i in range(dict(cand.schema)['info'])]
    arows = [cand.row[(f, i)] for f, w in cand.schema if f in ('addr', 'age') for i in range(w)]
    G.update(cand=cand, p=p, C=C, up=up, X0=X0, n=n, N=n * p.Q, srows=srows, irows=irows, arows=arows)


def phases(p):
    Q, PL = p.Q, p.PL
    g = p.gathers_q
    ph = {'gather1_mid': g[0] * Q + 3 * Q,
          'rest1': g[0] * Q + 6 * Q,
          'gather2_start': g[1] * Q - 100,
          'gather2_mid': g[1] * Q + 3 * Q,
          'gather3_mid': g[2] * Q + 3 * Q,
          'eval_early': p.E0 + 2 * PL + PL // 3,
          'special_proc': p.T_sig - 100,
          'trickle': p.T_wf + Q // 2,
          'match_pass': p.E0 + p.MP * PL + PL // 2 - 30,
          'final_prog': p.E0 + (p.MP + (p.NP - p.MP) // 2) * PL + PL // 3,
          'commit': p.U - 100}
    return ph


def places(p, n, w):
    Q = p.Q
    b = (n // 2) * Q                       # boundary between colonies jL and jR
    reach = p.lo - p.H - 2                 # first cell of jR that holds front state is b + reach
    return {'mid': b - Q // 2 - w // 2,    # middle of colony jL
            'edge': b - w // 2,            # centred on the boundary
            'edgeR': b + reach - w,        # box ends just before jR's front state
            'edgeL': b - reach,            # box starts just after jL's front state
            'reachL': b + 10 - w,          # 10 cells of jR's left margin, the rest in jL
            'in10': b + 10,                # entirely inside jR, starting 10 cells after its left end
            'leftm': b - w}                # entirely inside jL, ending at the boundary


def site_span(orr, N):
    bits = np.unpackbits(orr.view(np.uint8), bitorder='little')[:N]
    nz = np.nonzero(bits)[0]
    return (int(nz[0]), int(nz[-1])) if len(nz) else None


def run_scenario(args):
    name, phase, place, t_b, x0, w, h, seed, snap_path, stride, obs, mode = args
    cand, p, C, n, N = G['cand'], G['p'], G['C'], G['n'], G['N']
    Q, U = p.Q, p.U
    z = np.load(snap_path)
    Pr = z[f't{t_b}'].copy()
    Pf = Pr.copy()
    ref_U, ref_2U = z['ref_U'], z['ref_2U']
    rng = np.random.default_rng(seed)
    NW = Pf.shape[1]
    # packed masks of the box's sites
    mask = np.zeros(NW, dtype=np.uint64)
    for s in range(x0, x0 + w):
        mask[(s % N) // 64] |= np.uint64(1) << np.uint64((s % N) % 64)
    words = np.nonzero(mask)[0]
    m = mask[words]
    t = t_b
    marks = {}

    def note(P, t):
        if t == U:
            marks['U'] = P.copy()
        if t == 2 * U:
            marks['2U'] = P.copy()
    for _ in range(h):
        Pf = C.run_packed(Pf, 1, 1)
        t += 1
        if mode == 'random':
            r = rng.integers(0, 1 << 63, size=(cand.W, len(words)), dtype=np.uint64) * np.uint64(2) \
                + rng.integers(0, 2, size=(cand.W, len(words)), dtype=np.uint64)
        else:
            # 'shift': every site of the box takes the state of the site d cells to its right
            # (d = Q/2 + 7): a block whose Addresses and Ages agree with each other but not
            # with its place, i.e. a misaligned partial colony. 'copy': d = Q, the state of the
            # same Address one colony further (plausible but wrong SimBits and front state).
            d = Q if mode == 'copy' else Q // 2 + 7
            Xf = C.unpack(Pf, N)
            r = C.pack(np.roll(Xf, -d, axis=1))[:, words]
        Pf[:, words] = (Pf[:, words] & ~m) | (r & m)
        note(Pf, t)
    # reference to the end of the box (may cross U)
    tr = t_b
    for stop in sorted({U, 2 * U, t}):
        if tr < stop <= t:
            Pr = C.run_packed(Pr, stop - tr, 1)
            tr = stop
    srows, irows = G['srows'], G['irows']
    last_struct, smin, smax, imin, imax, max_struct_sites = -1, None, None, None, None, 0
    arows = G['arows']
    last_aa, amin, amax, max_aa_sites = -1, None, None, 0
    k = 0
    while k < obs and t < 2 * U:
        step = min(stride, 2 * U - t, (U - t) if t < U else stride)
        Pf = C.run_packed(Pf, step, 1)
        Pr = C.run_packed(Pr, step, 1)
        t += step
        k += step
        note(Pf, t)
        d = Pf ^ Pr
        so = np.bitwise_or.reduce(d[srows], axis=0)
        if so.any():
            last_struct = k
            a, b = site_span(so, N)
            smin = a if smin is None else min(smin, a)
            smax = b if smax is None else max(smax, b)
            max_struct_sites = max(max_struct_sites, b - a + 1)
        ao = np.bitwise_or.reduce(d[arows], axis=0)
        if ao.any():
            last_aa = k
            a, b = site_span(ao, N)
            amin = a if amin is None else min(amin, a)
            amax = b if amax is None else max(amax, b)
            max_aa_sites = max(max_aa_sites, b - a + 1)
        io = np.bitwise_or.reduce(d[irows], axis=0)
        if io.any():
            a, b = site_span(io, N)
            imin = a if imin is None else min(imin, a)
            imax = b if imax is None else max(imax, b)
    for stop in (U, 2 * U):
        if t < stop:
            Pf = C.run_packed(Pf, stop - t, 1)
            t = stop
            note(Pf, t)
    rec = dict(candidate=name, phase=phase, place=place, mode=mode, t=t_b, x0=x0, w=w, h=h, seed=seed,
               box_rel_boundary=[x0 - (n // 2) * Q, x0 + w - 1 - (n // 2) * Q],
               structure_recovery_ticks=last_struct, structure_window_exhausted=bool(last_struct >= obs - stride),
               structure_span_rel_box=None if smin is None else [smin - x0, smax - (x0 + w - 1)],
               structure_island_max=max_struct_sites,
               addr_age_recovery_ticks=last_aa, addr_age_island_max=max_aa_sites,
               addr_age_span_rel_box=None if amin is None else [amin - x0, amax - (x0 + w - 1)],
               info_span_rel_box=None if imin is None else [imin - x0, imax - (x0 + w - 1)])
    lo, hi = p.lo, p.hi
    for key, ref in (('U', ref_U), ('2U', ref_2U)):
        Xf, Xr = C.unpack(marks[key], N), C.unpack(ref, N)
        wrong = np.nonzero((codec.decode(cand, Xf) != codec.decode(cand, Xr)).any(axis=0))[0]
        lf, _ = codec.logical_info(cand, Xf)
        lr, _ = codec.logical_info(cand, Xr)
        dl = (lf != lr).reshape(n, Q)
        rec[f'wrong_upper_{key}'] = [int(v) for v in wrong]
        rec[f'colonies_work_info_{key}'] = [int(v) for v in np.nonzero(dl[:, lo:hi].any(axis=1))[0]]
        rec[f'identical_{key}'] = bool(np.array_equal(marks[key], ref))
        rec[f'sites_differ_{key}'] = int(np.unpackbits(np.bitwise_or.reduce(marks[key] ^ ref, axis=0).view(np.uint8)).sum())
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidate', default='G16')
    ap.add_argument('--colonies', type=int, default=32)
    ap.add_argument('--widths', default='72,137,200')
    ap.add_argument('--places', default='mid,edge,edgeR,edgeL')
    ap.add_argument('--phases', default='')
    ap.add_argument('--seed', type=int, default=7)
    ap.add_argument('--stride', type=int, default=4)
    ap.add_argument('--obs', type=int, default=0, help='ticks of lockstep observation after the box (default 3Q)')
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--tag', default='')
    ap.add_argument('--mode', default='random', choices=('random', 'shift', 'copy'))
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    setup(args.candidate, args.colonies, args.seed)
    cand, p, C, n, N = G['cand'], G['p'], G['C'], G['n'], G['N']
    Q, U = p.Q, p.U
    obs = args.obs or 3 * Q
    ph = phases(p)
    if args.phases:
        ph = {k: v for k, v in ph.items() if k in args.phases.split(',')}
    widths = [int(x) for x in args.widths.split(',')]
    sc = []
    for w in widths:
        pl = places(p, n, w)
        for pi, (phase, t_b) in enumerate(ph.items()):
            for place in args.places.split(','):
                tb = t_b if phase != 'commit' else U - w // 2
                seed = args.seed * 1000003 + w * 1009 + pi * 31 + list(pl).index(place)
                sc.append((args.candidate, phase, place, int(tb), int(pl[place]), w, w, seed))
    # reference pass with snapshots
    t0 = time.time()
    need = sorted({s[3] for s in sc})
    snaps = {}
    P = C.pack(G['X0'])
    t = 0
    for stop in need + [U, 2 * U]:
        if stop > t:
            P = C.run_packed(P, stop - t, threads=args.workers)
            t = stop
        if stop == U:
            snaps['ref_U'] = P.copy()
        elif stop == 2 * U:
            snaps['ref_2U'] = P.copy()
        if stop in need:
            snaps[f't{stop}'] = P.copy()
    up = G['up']
    d1 = codec.decode(cand, C.unpack(snaps['ref_U'], N))
    f1 = cand.step_numpy(up)
    d2 = codec.decode(cand, C.unpack(snaps['ref_2U'], N))
    f2 = cand.step_numpy(f1)
    closure = dict(period1=bool(np.array_equal(d1, f1)), period2=bool(np.array_equal(d2, f2)),
                   health1=codec.colony_health(cand, C.unpack(snaps['ref_U'], N)),
                   ref_seconds=round(time.time() - t0, 1))
    print(json.dumps(dict(candidate=args.candidate, Q=Q, U=U, colonies=n, closure=closure)), flush=True)
    tag = args.tag or args.candidate
    snap_path = os.path.join(OUT, f'snap_{tag}.npz')
    np.savez(snap_path, **snaps)
    jobs = [s + (snap_path, args.stride, obs, args.mode) for s in sc]
    recs = []
    with Pool(args.workers, initializer=setup, initargs=(args.candidate, args.colonies, args.seed)) as pool:
        for rec in pool.imap(run_scenario, jobs):
            recs.append(rec)
            print(json.dumps(rec), flush=True)
    os.remove(snap_path)
    out = dict(candidate=args.candidate, Q=Q, U=U, margin=p.margin, lo=p.lo, hi=p.hi, H=p.H, colonies=n,
               gathers_q=list(p.gathers_q), seed=args.seed, mode=args.mode, obs=obs, stride=args.stride, closure=closure,
               gray_bound=lambda_bound(Q), results=recs, seconds=round(time.time() - t0))
    with open(os.path.join(OUT, f'burst_{tag}.json'), 'w') as fh:
        json.dump(out, fh, indent=1)


def lambda_bound(Q):
    return {str(B): 2 * Q + 3 * B + 2.5 * B for B in (72, 137, 150, 200)}


if __name__ == '__main__':
    main()
