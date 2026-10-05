"""Size a candidate compiled by the job scheduler (gacsca/jobsched.py).

For each setting (lane skew, scheduler options):
  1. probe: compile with generous NPe/MP/NP and a free match pass, and record
     the pages the schedule needs;
  2. tight: rebuild the rule with those NPe, MP, NP (they are constants of
     the netlist, so the schedule changes a little) and compile the real ROM
     with the match pass fixed; shrink or grow the three numbers until the
     compiled schedule uses exactly what the rule declares.
Prints one JSON line per setting and writes figs/sweep/<tag>.json; the best
setting is the smallest U.
"""
import argparse
import json
import math
import os
import time
from concurrent.futures import ProcessPoolExecutor
from gacsca import candidates, compiler, jobsched

OUT = os.path.join(candidates.ROOT, 'figs', 'sweep')
S1 = (-5, -4, -3, -2, -1, 1, 2, 3, 4, 5)


def make(params, NPe, MP, NP, skew):
    fam = candidates.FAMILIES['G']
    prm = dict(params, NPe=NPe, MP=MP, NP=NP, skew=tuple(skew))
    prm = {k: tuple(v) if isinstance(v, list) else v for k, v in prm.items()}
    tmp = fam(**{**prm, 'nb': 1, 'm': 1})
    nb = tmp.E0b + NP + 1
    prm.update(nb=nb, m=tmp.PB + (nb - 1).bit_length())
    p = fam(**prm).check()
    return p, compiler.end_aware_layout(p, p.fam().cached(p)[1]), prm


def size(args):
    base, over, skew, opts = args
    params = dict(candidates.RECIPES[base]['params'])
    params.update(over)
    rec = dict(base=base, over=over, skew=list(skew), opts=opts)
    t = time.time()
    try:
        p, layout, _ = make(params, 250, 1051, 3000, skew)
        use, _ = jobsched.probe(p, layout, **opts)
    except compiler.CompileError as e:
        return dict(rec, error=str(e)[:200])
    rec['probe'] = use
    want = (use['NPe'], use['MP'], use['NP'])
    good, failed, tried = None, set(), []
    for _ in range(12):
        if want in failed or (good is not None and want == good[0]):
            break
        try:
            p, layout, prm = make(params, *want, skew)
            prog = compiler.compile_candidate(p, layout, jobs=opts)
        except (compiler.CompileError, AssertionError) as e:
            failed.add(want)
            tried.append(dict(want=want, error=str(e)[:80]))
            if good is not None:
                break
            want = (want[0] + 1, want[1] + 2, want[2] + 3)      # more room everywhere
            continue
        u = prog.stats['usage']
        tried.append(dict(want=want, usage=u))
        good = (want, prm, prog.stats)
        nxt = (u['NPe'], min(want[1], u['MP_min']), u['NP'])
        if nxt == want:
            break
        want = nxt
    rec['tried'] = tried
    rec['seconds'] = round(time.time() - t)
    if good is None:
        return dict(rec, error='no fit')
    (NPe, MP, NP), prm, stats = good
    p, _, _ = make(params, NPe, MP, NP, skew)
    rec.update(params=prm, Q=p.Q, U=p.U, PL=p.PL, QU_log2=round(math.log2(p.Q * p.U), 3),
               U_over_Q=round(p.U / p.Q, 1), instr=stats['instr'], gates=stats['gates'],
               loads=stats['loads'], parks=stats['parks'], max_parked=stats['max_parked'])
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default='G15')
    ap.add_argument('--params', default='{}', help='JSON parameter overrides')
    ap.add_argument('--skews', default='1,2,3', help='multiples of the unit skew (j cells for lane j)')
    ap.add_argument('--opts', default='[{}]', help='JSON list of scheduler option sets')
    ap.add_argument('--workers', type=int, default=6)
    ap.add_argument('--tag', required=True)
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    over = json.loads(args.params)
    grid = [(args.base, over, tuple(m * x for x in S1), o)
            for m in (int(x) for x in args.skews.split(',')) for o in json.loads(args.opts)]
    recs = []
    with ProcessPoolExecutor(args.workers) as ex:
        for rec in ex.map(size, grid):
            recs.append(rec)
            print(json.dumps({k: v for k, v in rec.items() if k != 'params'}), flush=True)
    ok = [r for r in recs if 'U' in r]
    best = min(ok, key=lambda r: r['U']) if ok else None
    with open(os.path.join(OUT, args.tag + '.json'), 'w') as fh:
        json.dump(dict(records=recs, best=best), fh, indent=1)
    if best:
        print('best:', json.dumps(dict(skew=best['skew'], opts=best['opts'], Q=best['Q'], U=best['U'],
                                       params=best['params'])))


if __name__ == '__main__':
    main()
