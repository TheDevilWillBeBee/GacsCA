"""Seeded sizing of a G15-like comb candidate (scratch copy), after experiments/search_comb.py.
usage: GACS_COPIES=3 python3 search3.py <q> <margin> <seed> <tag> [rounds]"""
import sys, os, json, math, time, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dataclasses import replace, asdict
import numpy as np
from gacsca import candidates, compiler, multifront, rule_g

q, margin, seed, tag = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
rounds = int(sys.argv[5]) if len(sys.argv) > 5 else 8
r = candidates.RECIPES['G15']
L = int(sys.argv[6]) if len(sys.argv) > 6 else 64
params = dict(r['params'], q=q, margin=margin, L=L)
mf = dict(reassoc=True, cut=False, combine='spread', ctrl_fields=[], order_seed=seed, owner_seed=seed)

def build(params):
    p = rule_g.ParamsG(**params).check()
    layout = compiler.default_layout(p, r['spread'])
    layout = compiler.proportional_layout(p, layout)
    skew, _ = compiler.choose_skew(p, layout, seed=r['skew_seed'])
    return replace(p, skew=skew).check(), layout

def sized(params, NP):
    tmp = rule_g.ParamsG(**{**params, 'NP': NP, 'nb': 1, 'm': 1})
    nb = tmp.E0b + NP + 1
    return dict(params, NP=NP, nb=nb, m=tmp.PB + (nb - 1).bit_length())

def layout_of(ranges):
    be, ba, bf = ranges
    NPe = be + 1
    MP = NPe + ba
    MP += 1 - MP % 2
    NP = MP + 1 + bf
    return NPe, MP, NP

p, layout = build(sized(dict(params, NPe=250, MP=1051), 3000))
out, _ = multifront.compile_phases(p, layout, p.fronts, p.delta, check=False, lookahead=300, ooo=32, **mf)
need = [out[ph]['passes'] for ph in ('early', 'a', 'final')]
rec = dict(copies=rule_g.NC, q=q, margin=margin, seed=seed, probe=need, rounds=[])
print(json.dumps(dict(seed=seed, probe=need)), flush=True)
ranges = [int(math.ceil(x * 1.08)) + 1 for x in need]
best = None
for rnd in range(rounds):
    NPe, MP, NP = layout_of(ranges)
    tight = sized(dict(params, NPe=NPe, MP=MP), NP)
    t = time.time()
    try:
        p2, layout2 = build(tight)
        prog = compiler.compile_candidate(p2, layout2, lookahead=300, ooo=32, multifront=mf)
        used = [prog.stats[ph]['passes'] for ph in ('early', 'a', 'final')]
        row = dict(round=rnd, ranges=ranges, NPe=NPe, MP=MP, NP=NP, U=p2.U, Q=p2.Q, PL=p2.PL, nb=p2.nb, m=p2.m,
                   width=rule_g.width(p2), gates=len(rule_g.cached(p2)[1].gates), instructions=len(prog.listing),
                   QU_log2=round(math.log2(p2.Q * p2.U), 3), used=used, ok=True, seconds=round(time.time() - t))
        if best is None or p2.U < best['U']:
            best = dict(row)
            np.savez(os.path.join(HERE, f'cand_{tag}.npz'), rom=prog.rom, layout=np.asarray(layout2),
                     params=json.dumps(asdict(p2)))
        new = [u + 1 for u in used]
        if new == ranges:
            rec['rounds'].append(row); print(json.dumps(row), flush=True)
            break
        ranges = [min(a, b) for a, b in zip(ranges, new)]
    except compiler.CompileError as e:
        msg = str(e)
        row = dict(round=rnd, ranges=ranges, NPe=NPe, MP=MP, NP=NP, ok=False, error=msg[:120])
        lp = re.search(r"'last_page': (\d+)", msg)
        last = int(lp.group(1)) if lp else NP
        ph = 0 if last < NPe else (1 if last < MP else 2)
        ranges = list(ranges)
        ranges[ph] = int(math.ceil(ranges[ph] * 1.08)) + 1
    rec['rounds'].append(row)
    print(json.dumps(row), flush=True)
rec['best'] = best
print(json.dumps(dict(seed=seed, best=best)), flush=True)
json.dump(rec, open(os.path.join(HERE, f'search_{tag}.json'), 'w'), indent=1)
