"""Size a comb candidate (G family with fronts > 1).

  1. probe: compile the three programs with generous page budgets (each
     phase starts right after the previous one) and record the passes each
     needs;
  2. tight: NPe, MP, NP from those needs plus `slack`, nb from E0b + NP + 1,
     and compile the real ROM (compiler.compile_candidate, fixed page
     ranges, every phase replayed against the netlist).
Prints one JSON line per stage and writes
figs/sweep/<tag>.json.
"""
import argparse
import json
import math
import os
import time
from dataclasses import replace
from gacsca import candidates, compiler, multifront

OUT = os.path.join(candidates.ROOT, 'figs', 'sweep')


def build(params, recipe):
    fam = candidates.FAMILIES['G']
    p = fam(**params).check()
    layout = compiler.default_layout(p, recipe['spread'])
    layout = compiler.proportional_layout(p, layout)
    skew, _ = compiler.choose_skew(p, layout, seed=recipe['skew_seed'])
    return replace(p, skew=skew).check(), layout


def sized(params, NP):
    fam = candidates.FAMILIES['G']
    tmp = fam(**{**params, 'NP': NP, 'nb': 1, 'm': 1})
    nb = tmp.E0b + NP + 1
    return dict(params, NP=NP, nb=nb, m=tmp.PB + (nb - 1).bit_length())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default='G12')
    ap.add_argument('--params', default='{}', help='JSON parameter overrides')
    ap.add_argument('--mf', default='{}', help='JSON multifront options')
    ap.add_argument('--slack', type=float, default=0.08)
    ap.add_argument('--tag', required=True)
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    r = candidates.RECIPES[args.base]
    params = dict(r['params'])
    params.update(json.loads(args.params))
    mf = dict(lookahead=300, ooo=32, reassoc=True, cut=False, combine='spread', ctrl_fields=[])
    mf.update(json.loads(args.mf))
    rec = dict(base=args.base, params_override=json.loads(args.params), mf=mf, stages=[])
    t = time.time()
    probe = sized(dict(params, NPe=250, MP=1051), 3000)
    p, layout = build(probe, r)
    out, _ = multifront.compile_phases(p, layout, p.fronts, p.delta, **{k: v for k, v in mf.items()
                                                                        if k not in ('lookahead', 'ooo')},
                                       lookahead=mf['lookahead'], ooo=mf['ooo'])
    need = {ph: out[ph]['passes'] for ph in ('early', 'a', 'final')}
    rec['stages'].append(dict(stage='probe', seconds=round(time.time() - t), PL=out['PL'], need=need,
                              replay_bad={ph: out[ph]['replay_bad'] for ph in need}))
    print(json.dumps(rec['stages'][-1]), flush=True)
    s = 1 + args.slack
    NPe = int(math.ceil(need['early'] * s)) + 2            # the early program ends one pass early
    MP = NPe + int(math.ceil(need['a'] * s)) + 1
    MP += 1 - MP % 2
    NP = MP + 1 + int(math.ceil(need['final'] * s)) + 2
    tight = sized(dict(params, NPe=NPe, MP=MP), NP)
    t = time.time()
    try:
        p2, layout2 = build(tight, r)
        prog = compiler.compile_candidate(p2, layout2, lookahead=mf['lookahead'], ooo=mf['ooo'],
                                          multifront={k: v for k, v in mf.items()
                                                      if k not in ('lookahead', 'ooo')})
        st = prog.stats
        rec['stages'].append(dict(stage='tight', seconds=round(time.time() - t), NPe=NPe, MP=MP, NP=NP,
                                  nb=p2.nb, m=p2.m, U=p2.U, Q=p2.Q, PL=p2.PL,
                                  QU_log2=round(math.log2(p2.Q * p2.U), 3), U_over_Q=round(p2.U / p2.Q, 1),
                                  used={ph: st[ph]['passes'] for ph in ('early', 'a', 'final')},
                                  replay_bad={ph: st[ph]['replay_bad'] for ph in ('early', 'a', 'final')},
                                  instructions=len(prog.listing), gates=len(p2.fam().cached(p2)[1].gates),
                                  params={k: v for k, v in tight.items() if k != 'skew'}))
    except Exception as e:
        rec['stages'].append(dict(stage='tight', NPe=NPe, MP=MP, NP=NP, error=repr(e)[:400]))
    print(json.dumps(rec['stages'][-1]), flush=True)
    with open(os.path.join(OUT, args.tag + '.json'), 'w') as fh:
        json.dump(rec, fh, indent=1)


if __name__ == '__main__':
    main()
