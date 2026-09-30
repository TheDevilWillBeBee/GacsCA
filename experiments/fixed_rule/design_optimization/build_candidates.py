"""Rebuild every named candidate from its recipe and compare with the cache.

The compile is deterministic, so a fresh build must reproduce the cached ROM
and layout exactly. Writes a JSON receipt with identities and hashes.
"""
import hashlib
import json
import os
import time
import numpy as np
from gacsca.fixed_rule.design_optimization import candidates, machine

OUT = os.path.join(candidates.ROOT, 'figs', 'fixed_rule', 'design_optimization', 'receipts')


def main():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for name in candidates.RECIPES:
        t = time.time()
        p, layout, prog = candidates.build(name)
        fresh = machine.Candidate(p, prog.rom, layout)
        cached = candidates.load(name)
        same = (np.array_equal(fresh.rom, cached.rom) and np.array_equal(fresh.layout, cached.layout)
                and fresh.comp.digest == cached.comp.digest)
        ident = candidates.summary(cached)
        rows.append(dict(name=name, reproduced=bool(same), build_seconds=round(time.time() - t, 1),
                         Q=ident['Q'], U=ident['U'], width=ident['width'], gates=ident['gates'],
                         netlist_sha256=ident['netlist_sha256'],
                         rom_sha256=ident['rom_sha256'], candidate_sha256=ident['candidate_sha256'],
                         instructions=ident['rom_nonzero_words'], passes_used=ident['recipe_passes_used'],
                         params=ident['params']))
        print(json.dumps({k: rows[-1][k] for k in ('name', 'reproduced', 'Q', 'U', 'width', 'gates',
                                                     'instructions', 'passes_used')}), flush=True)
    src = {}
    pkg = os.path.join(candidates.ROOT, 'gacsca', 'fixed_rule', 'design_optimization')
    for fn in sorted(os.listdir(pkg)):
        if fn.endswith('.py'):
            with open(os.path.join(pkg, fn), 'rb') as fh:
                src[fn] = hashlib.sha256(fh.read()).hexdigest()
    with open(os.path.join(OUT, 'candidates.json'), 'w') as fh:
        json.dump(dict(candidates=rows, source_sha256=src,
                       date=time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())), fh, indent=1)


if __name__ == '__main__':
    main()
