"""Rebuild named candidates from their recipes and compare with the cache.

The compile is deterministic, so a fresh build must reproduce the cached ROM
and layout exactly. Usage:

  build_candidates.py --only G14          one candidate -> receipts/build/<name>.json
  build_candidates.py --combine           all per-candidate receipts -> receipts/candidates.json
  build_candidates.py --combine --write-manifest
                                          also write the trusted digests of the fresh builds
                                          to gacsca/.../manifest.json (only if every fresh
                                          build reproduced its cache)
  build_candidates.py                     every candidate in turn, then --combine

The manifest is written from fresh builds, never from caches: it pins what
the recipes and the code produce, and candidates.load() checks caches
against it.
"""
import argparse
import hashlib
import json
import os
import time
import numpy as np
from gacsca.fixed_rule.design_optimization import candidates, machine

OUT = os.path.join(candidates.ROOT, 'figs', 'fixed_rule', 'design_optimization', 'receipts')
PER = os.path.join(OUT, 'build')


def build_one(name):
    t = time.time()
    p, layout, prog = candidates.build(name)
    fresh = machine.Candidate(p, prog.rom, layout)
    cached = candidates.load(name, check_manifest=False)
    dig_f, dig_c = candidates.digests(fresh), candidates.digests(cached)
    dig_f['recipe_sha256'] = candidates.recipe_digest(name)
    ident = candidates.summary(fresh)
    row = dict(name=name, reproduced=all(dig_f[k] == dig_c[k] for k in dig_c), build_seconds=round(time.time() - t, 1),
               Q=ident['Q'], U=ident['U'], width=ident['width'], gates=ident['gates'],
               instructions=ident['rom_nonzero_words'], passes_used=ident['recipe_passes_used'],
               fronts=getattr(p, 'fronts', 1), fresh=dig_f, cached=dig_c, params=ident['params'])
    os.makedirs(PER, exist_ok=True)
    with open(os.path.join(PER, name + '.json'), 'w') as fh:
        json.dump(row, fh, indent=1)
    print(json.dumps({k: row[k] for k in ('name', 'reproduced', 'Q', 'U', 'width', 'gates',
                                          'instructions', 'passes_used', 'build_seconds')}), flush=True)
    return row


def combine(write_manifest):
    rows = []
    for name in candidates.RECIPES:
        path = os.path.join(PER, name + '.json')
        if not os.path.exists(path):
            raise SystemExit(f'missing build receipt for {name}')
        with open(path) as fh:
            rows.append(json.load(fh))
    src = {}
    pkg = os.path.join(candidates.ROOT, 'gacsca', 'fixed_rule', 'design_optimization')
    for fn in sorted(os.listdir(pkg)):
        if fn.endswith('.py'):
            with open(os.path.join(pkg, fn), 'rb') as fh:
                src[fn] = hashlib.sha256(fh.read()).hexdigest()
    date = time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())
    with open(os.path.join(OUT, 'candidates.json'), 'w') as fh:
        json.dump(dict(candidates=rows, source_sha256=src, date=date), fh, indent=1)
    bad = [r['name'] for r in rows if not r['reproduced']]
    print('reproduced', len(rows) - len(bad), 'of', len(rows), 'mismatches', bad)
    if write_manifest:
        if bad:
            raise SystemExit('not writing the manifest: some fresh builds differ from their caches')
        man = dict(note='Trusted digests of fresh builds of every recipe (build_candidates.py). '
                        'candidates.load() checks cached candidates against them.',
                   date=date, candidates={r['name']: r['fresh'] for r in rows})
        with open(candidates.MANIFEST, 'w') as fh:
            json.dump(man, fh, indent=1, sort_keys=True)
        print('manifest written:', candidates.MANIFEST)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', default='')
    ap.add_argument('--combine', action='store_true')
    ap.add_argument('--write-manifest', action='store_true')
    args = ap.parse_args()
    if args.only:
        build_one(args.only)
    elif args.combine:
        combine(args.write_manifest)
    else:
        for name in candidates.RECIPES:
            build_one(name)
        combine(args.write_manifest)


if __name__ == '__main__':
    main()
