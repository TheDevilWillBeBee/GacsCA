"""Probe + tight compile of a G15-like comb candidate in the scratch copy.
usage: GACS_COPIES=3 python3 probe.py <q> <margin> <seed|none> <tag> [L]"""
import sys, os, json, math, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dataclasses import replace
from gacsca import candidates, compiler, multifront, rule_g

q, margin = int(sys.argv[1]), int(sys.argv[2])
seed = None if sys.argv[3] == 'none' else int(sys.argv[3])
tag = sys.argv[4]
L = int(sys.argv[5]) if len(sys.argv) > 5 else 64
r = candidates.RECIPES['G15']
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

rec = dict(copies=rule_g.NC, q=q, margin=margin, seed=seed, L=L)
t = time.time()
p, layout = build(sized(dict(params, NPe=250, MP=1051), 3000))
comp = rule_g.cached(p)[1]
rec.update(width=rule_g.width(p), gates=len(comp.gates), PL=p.PL, W=p.hi - p.lo)
out, _ = multifront.compile_phases(p, layout, p.fronts, p.delta, lookahead=300, ooo=32, **mf)
need = {ph: out[ph]['passes'] for ph in ('early', 'a', 'final')}
rec['probe'] = dict(seconds=round(time.time() - t), need=need,
                    replay_bad={ph: out[ph]['replay_bad'] for ph in need})
print(json.dumps(rec), flush=True)
for slack in (0.08, 0.2):
    s = 1 + slack
    NPe = int(math.ceil(need['early'] * s)) + 2
    MP = NPe + int(math.ceil(need['a'] * s)) + 1
    MP += 1 - MP % 2
    NP = MP + 1 + int(math.ceil(need['final'] * s)) + 2
    tight = sized(dict(params, NPe=NPe, MP=MP), NP)
    t = time.time()
    try:
        p2, layout2 = build(tight)
        prog = compiler.compile_candidate(p2, layout2, lookahead=300, ooo=32, multifront=mf)
        st = prog.stats
        rec['tight'] = dict(slack=slack, seconds=round(time.time() - t), NPe=NPe, MP=MP, NP=NP, nb=p2.nb, m=p2.m,
                            U=p2.U, Q=p2.Q, PL=p2.PL, QU_log2=round(math.log2(p2.Q * p2.U), 3),
                            U_over_Q=round(p2.U / p2.Q, 1),
                            used={ph: st[ph]['passes'] for ph in ('early', 'a', 'final')},
                            replay_bad={ph: st[ph]['replay_bad'] for ph in ('early', 'a', 'final')},
                            instructions=len(prog.listing), gates=len(rule_g.cached(p2)[1].gates),
                            width=rule_g.width(p2),
                            params={k: v for k, v in tight.items() if k != 'skew'})
        import numpy as np
        np.savez(os.path.join(HERE, f'cand_{tag}.npz'), rom=prog.rom, layout=np.asarray(layout2),
                 params=json.dumps({k: (list(v) if isinstance(v, tuple) else v) for k, v in p2.__dict__.items()}))
        break
    except Exception as e:
        rec['tight_error_%s' % slack] = repr(e)[:300]
print(json.dumps(rec), flush=True)
json.dump(rec, open(os.path.join(HERE, f'probe_{tag}.json'), 'w'), indent=1)
