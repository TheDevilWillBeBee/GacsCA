"""Find the smallest work period U for a G-family configuration.

Starting from a recipe (default G8) with parameter and compile overrides:
  1. probe: compile with generous budgets (early program, phase A and final
     program each get far more passes than needed) and record the passes each
     part actually uses;
  2. tight: set NPe, MP and NP to those needs (plus a small slack), pick the
     smallest U = 2^m with E0 + NP*D*Q <= U - 1, and compile again to confirm.
     NPe and MP are rule constants (the early program's end T_sig and the
     match pass), so the tight netlist differs from the probe's and is
     compiled from scratch.
Prints one JSON line per stage and writes
figs/fixed_rule/design_optimization/sweep/<tag>.json.
"""
import argparse
import json
import math
import os
import time
from dataclasses import replace
import numpy as np
from gacsca.fixed_rule.design_optimization import candidates, compiler

OUT = os.path.join(candidates.ROOT, 'figs', 'fixed_rule', 'design_optimization', 'sweep')


def compile_with_stats(p, layout, comp_kw):
    stats = []
    orig = compiler.Scheduler.run_inorder

    def wrapped(self, prog, pages, targets_hold, init, **kw):
        n0 = int(prog.used.sum())
        out = orig(self, prog, pages, targets_hold, init, **kw)
        pg = sorted(pages)
        stats.append(dict(first_page=pg[0], last_budget_page=pg[-1], last_page=int(self.last_page),
                          instr=int(prog.used.sum()) - n0, idle=int(self.last_idle),
                          reasons=dict(self.idle_reasons)))
        return out
    orig_sweep = compiler.Scheduler.run_sweep

    def wrapped_sweep(self, prog, pages, targets_hold, init, **kw):
        n0 = int(prog.used.sum())
        out = orig_sweep(self, prog, pages, targets_hold, init, **kw)
        pg = sorted(pages)
        stats.append(dict(first_page=pg[0], last_budget_page=pg[-1], last_page=int(self.last_page),
                          instr=int(prog.used.sum()) - n0, idle=0, reasons={}))
        return out
    compiler.Scheduler.run_inorder = wrapped
    compiler.Scheduler.run_sweep = wrapped_sweep
    try:
        prog = compiler.compile_candidate(p, layout, **comp_kw)
    finally:
        compiler.Scheduler.run_inorder = orig
        compiler.Scheduler.run_sweep = orig_sweep
    return prog, stats


def prepare(base, over, comp_over):
    r = candidates.RECIPES[base]
    params = dict(r['params'])
    params.update(over)
    comp_kw = dict(r['compile'])
    comp_kw.update(comp_over)
    return r, params, comp_kw


LAYOUT = dict(spread=None, interleave=False, skew='search', spread_fields=())


def spread_fields_layout(p, layout, fields):
    """Permute the default layout so that the bits of `fields` are evenly
    distributed over the used cells (other bits keep their relative order)."""
    sch = p.fam().schema(p)
    bits, b = {}, 0
    for f, w in sch:
        for i in range(w):
            bits[(f, i)] = b
            b += 1
    cells = sorted(int(x) for x in layout)
    special = [bits[(f, i)] for f, w in sch if f in fields for i in range(w)]
    rest = [x for x in range(len(bits)) if x not in set(special)]
    n = len(cells)
    slots = sorted({(j * n) // len(special) for j in range(len(special))})
    assert len(slots) == len(special)
    out = [None] * len(bits)
    it_rest = iter(rest)
    sp = iter(special)
    for k, cell in enumerate(cells):
        out[next(sp) if k in set(slots) else next(it_rest)] = cell
    return np.array(out)


def proportional_layout(p, layout, by_logical=False):
    """Every field spread evenly over the used cells: bits are ordered by
    their relative position (i + 0.5) / width within their field. With
    by_logical, a fivefold field's bit (slot*w + i) uses i / w, so the five
    copies of a logical bit sit next to each other."""
    sch = p.fam().schema(p)
    five = set(getattr(p.fam(), 'fivefold_fields', lambda p: ())(p))
    keys, b = [], 0
    for fi, (f, w) in enumerate(sch):
        lw = w // 5 if (by_logical and f in five) else w
        for i in range(w):
            j = i % lw if (by_logical and f in five) else i
            keys.append(((j + 0.5) / lw, fi, i))
            b += 1
    order = sorted(range(len(keys)), key=lambda x: keys[x])
    cells = sorted(int(x) for x in layout)
    out = [None] * len(keys)
    for rank, bit in enumerate(order):
        out[bit] = cells[rank]
    return np.array(out)


def build_params(r, params):
    p = candidates.FAMILIES[r.get('family', 'R')](**params).check()
    spread = r['spread'] if LAYOUT['spread'] is None else LAYOUT['spread']
    layout = compiler.default_layout(p, spread, interleave=LAYOUT['interleave'])
    if LAYOUT['spread_fields']:
        layout = spread_fields_layout(p, layout, set(LAYOUT['spread_fields']))
    if LAYOUT.get('proportional'):
        layout = proportional_layout(p, layout, by_logical=LAYOUT['proportional'] == 'logical')
    if LAYOUT['skew'] == 'zero':
        skew = (0,) * 10
    else:
        skew, _ = compiler.choose_skew(p, layout, seed=r['skew_seed'])
    return replace(p, skew=skew).check(), layout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default='G8')
    ap.add_argument('--params', default='{}', help='JSON parameter overrides')
    ap.add_argument('--compile', default='{}', help='JSON compile overrides')
    ap.add_argument('--slack', type=float, default=0.03)
    ap.add_argument('--tag', required=True)
    ap.add_argument('--layout', default='{}', help='JSON: spread (bool), interleave (bool), skew (search|zero)')
    args = ap.parse_args()
    LAYOUT.update(json.loads(args.layout))
    os.makedirs(OUT, exist_ok=True)
    r, params, comp_kw = prepare(args.base, json.loads(args.params), json.loads(args.compile))
    if isinstance(comp_kw.get('order_kind'), list):
        comp_kw['order_kind'] = tuple(comp_kw['order_kind'])
    rec = dict(base=args.base, params_override=json.loads(args.params),
               compile_override=json.loads(args.compile), layout=dict(LAYOUT), stages=[])
    # 1. probe
    probe = dict(params)
    Q = 1 << probe['k']
    D = 1 << probe.get('dlog', 0)
    probe.update(NPe=250, MP=251 + 400 * 2 + (1 if (251 + 800) % 2 == 0 else 0), NP=3000)
    E0q = probe.get('E0q', 24)
    exact = bool(probe.get('q'))
    if exact:
        Q = probe['q']

    def size_period(d, NP):
        """Smallest work period holding E0 + NP passes: 2^m, or nb*Q blocks
        in exact-Q mode."""
        if exact and d.get('confined'):
            fam = candidates.FAMILIES[r.get('family', 'R')]
            tmp = fam(**{**{kk: v for kk, v in d.items() if kk != 'skew'}, 'NP': NP, 'nb': 1, 'm': 1})
            d['nb'] = tmp.E0b + NP * D + 1
            d['m'] = tmp.PB + (d['nb'] - 1).bit_length()
        elif exact:
            d['nb'] = E0q + NP * D + 1
            d['m'] = d['k'] + (d['nb'] - 1).bit_length()
        else:
            d['m'] = math.ceil(math.log2((E0q + NP * D) * Q + 1))
    size_period(probe, probe['NP'])
    t = time.time()
    try:
        p, layout = build_params(r, probe)
        prog, st = compile_with_stats(p, layout, comp_kw)
    except Exception as e:
        rec['stages'].append(dict(stage='probe', error=repr(e)[:300]))
        print(json.dumps(rec['stages'][-1]), flush=True)
        return
    from gacsca.fixed_rule.design_optimization import rule_g
    width = p.fam().width(p)
    early, phase_a, final = st[0], st[1], st[2]
    need_e = early['last_page'] + 1
    need_a = phase_a['last_page'] - phase_a['first_page'] + 1
    need_f = final['last_page'] - final['first_page'] + 1
    rec['stages'].append(dict(stage='probe', seconds=round(time.time() - t), width=width, Q=Q,
                              early_passes=need_e, phase_a_passes=need_a, final_passes=need_f,
                              instructions=int(prog.used.sum()),
                              idle_reasons=[s['reasons'] for s in st]))
    print(json.dumps(rec['stages'][-1]), flush=True)
    # 2. tight
    s = 1 + args.slack
    NPe = int(math.ceil(need_e * s)) + 1
    MP = NPe + int(math.ceil(need_a * s)) + 1
    if MP % 2 == 0:
        MP += 1
    NP = MP + 1 + int(math.ceil(need_f * s)) + 2
    tight = dict(params)
    tight.update(NPe=NPe, MP=MP, NP=NP)
    size_period(tight, NP)
    m = tight['m']
    t = time.time()
    try:
        p2, layout2 = build_params(r, tight)
        prog2, st2 = compile_with_stats(p2, layout2, comp_kw)
        used = np.nonzero(prog2.used.any(axis=0))[0]
        rec['stages'].append(dict(stage='tight', seconds=round(time.time() - t), NPe=NPe, MP=MP, NP=NP,
                                  m=m, U=p2.U, Q=p2.Q, QU_log2=round(math.log2(p2.Q * p2.U), 2), width=p2.fam().width(p2),
                                  gates=len(p2.fam().cached(p2)[1].gates),
                                  last_page=int(used.max() // D), instructions=int(prog2.used.sum()),
                                  params={k: v for k, v in tight.items() if k != 'skew'}))
    except Exception as e:
        rec['stages'].append(dict(stage='tight', NPe=NPe, MP=MP, NP=NP, m=m, error=repr(e)[:300]))
    print(json.dumps(rec['stages'][-1]), flush=True)
    with open(os.path.join(OUT, args.tag + '.json'), 'w') as fh:
        json.dump(rec, fh, indent=1)


if __name__ == '__main__':
    main()
