"""Seeded search for the shortest comb program (G family, fronts > 1).

For each seed (order_seed: depth-first root/child order; owner_seed: which
front owns which upper bit) the three programs are sized as in
sweep_comb.py, then refitted: a phase that overflows its page range gets 8%
more, and after a success every range is shrunk to what was used plus one
pass, until a refit fails. Prints one JSON line per compile and the best
configuration; writes figs/fixed_rule/design_optimization/sweep/<tag>.json.
"""
import argparse
import json
import math
import os
import re
import time
from gacsca.fixed_rule.design_optimization import candidates, compiler, multifront
from sweep_comb import OUT, build, sized


def layout_of(ranges):
    be, ba, bf = ranges
    NPe = be + 1
    MP = NPe + ba
    MP += 1 - MP % 2
    NP = MP + 1 + bf
    return NPe, MP, NP


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default='G12')
    ap.add_argument('--params', default='{}')
    ap.add_argument('--mf', default='{}')
    ap.add_argument('--seed', type=int, required=True)
    ap.add_argument('--tag', required=True)
    ap.add_argument('--rounds', type=int, default=6)
    args = ap.parse_args()
    r = candidates.RECIPES[args.base]
    params = dict(r['params'])
    params.update(json.loads(args.params))
    mf = dict(lookahead=300, ooo=32, reassoc=True, cut=False, combine='spread', ctrl_fields=[],
              order_seed=args.seed, owner_seed=args.seed)
    mf.update(json.loads(args.mf))
    probe = sized(dict(params, NPe=250, MP=1051), 3000)
    p, layout = build(probe, r)
    out, _ = multifront.compile_phases(p, layout, p.fronts, p.delta, check=False,
                                       **{k: v for k, v in mf.items()})
    need = [out[ph]['passes'] for ph in ('early', 'a', 'final')]
    rec = dict(seed=args.seed, params=json.loads(args.params), mf=mf, probe=need, rounds=[])
    print(json.dumps(dict(seed=args.seed, probe=need)), flush=True)
    ranges = [int(math.ceil(x * 1.08)) + 1 for x in need]
    best = None
    for rnd in range(args.rounds):
        NPe, MP, NP = layout_of(ranges)
        tight = sized(dict(params, NPe=NPe, MP=MP), NP)
        t = time.time()
        try:
            p2, layout2 = build(tight, r)
            prog = compiler.compile_candidate(p2, layout2, lookahead=mf['lookahead'], ooo=mf['ooo'],
                                              multifront={k: v for k, v in mf.items()
                                                          if k not in ('lookahead', 'ooo')})
            used = [prog.stats[ph]['passes'] for ph in ('early', 'a', 'final')]
            row = dict(round=rnd, ranges=ranges, NPe=NPe, MP=MP, NP=NP, U=p2.U, nb=p2.nb, m=p2.m,
                       QU_log2=round(math.log2(p2.Q * p2.U), 3), used=used, ok=True,
                       seconds=round(time.time() - t))
            if best is None or p2.U < best['U']:
                best = dict(row, params={k: v for k, v in tight.items() if k != 'skew'})
            new = [u + 1 for u in used]
            if new == ranges:
                rec['rounds'].append(row)
                print(json.dumps(row), flush=True)
                break
            ranges = [min(a, b) for a, b in zip(ranges, new)]
        except compiler.CompileError as e:
            msg = str(e)
            # which phase overflowed: the one whose page range ended first
            row = dict(round=rnd, ranges=ranges, NPe=NPe, MP=MP, NP=NP, ok=False, error=msg[:160])
            # grow the phase that failed (the compile stops at the first failure)
            lp = re.search(r"'last_page': (\d+)", msg)
            last = int(lp.group(1)) if lp else NP
            ph = 0 if last < NPe else (1 if last < MP else 2)
            ranges = list(ranges)
            ranges[ph] = int(math.ceil(ranges[ph] * 1.08)) + 1
        rec['rounds'].append(row)
        print(json.dumps(row), flush=True)
    rec['best'] = best
    print(json.dumps(dict(seed=args.seed, best=best and {k: best[k] for k in ('U', 'QU_log2', 'NPe', 'MP', 'NP', 'used')})), flush=True)
    with open(os.path.join(OUT, args.tag + '.json'), 'w') as fh:
        json.dump(rec, fh, indent=1)


if __name__ == '__main__':
    main()
