"""Census of the level-1 campaign receipts (AUDIT2 finding 1).

Counts, over an explicit list of receipts, how the decoded upper state behaved after each error:
never wrong; wrong at exactly one upper time in at most two adjacent cells, all inside the colonies
the error touched; or anything else. Errors are split by the number of colonies they touch:
  * at most two colonies: level-1-scale errors (bursts, certified level-1 errors, 1-2 colony wipes);
  * three or more: errors that only level 2 can clear (3-colony wipes, straddling 2-colony wipes,
    the 1000 x 1000 box over three colonies), reported separately.
Inclusion: every receipt in figs/.../level1_campaign except smoke tests, analyses that are not
campaign batches, and reruns of the same faults (which repeat a batch's scenarios exactly); the
excluded files and the reason for each are listed in the output.
Writes Report/campaign_census.json (tracked), with the sha256 of
every receipt counted.
"""
import glob
import hashlib
import json
import os
from gacsca import candidates

DIR = os.path.join(candidates.ROOT, 'figs', 'level1_campaign')
OUT = os.path.join(candidates.ROOT, 'Report', 'campaign_census.json')
EXCLUDE = {
    'smoke': 'smoke test',
    'smoke2_G14': 'smoke test',
    'reclassified': 'analysis output, not a batch',
    'G15_prop4_fields_box100_random': 'field-by-field analysis, not a batch',
    'G15_b91_full_wipe1_holder_attribution': 'same faults as G15_b91_full_wipe1 (earlier Info check)',
    'G15_b91_full_wipe1_logical_attribution': 'same faults as G15_b91_full_wipe1 (earlier Info check)',
    'G8_b1_commit_rerun_sameseeds': 'same faults as the commit rings of G8_b1_age0_mid (longer run)',
    'G8_b2_commit_rerun_sameseeds': 'same faults as the commit rings of G8_b2_eval_front (longer run)',
    'G8_b3_commit_rerun_sameseeds': 'same faults as the commit rings of G8_b3_precommit_mid (longer run)',
}
RERUN_SUFFIX = ('_track', '_track_l2')       # per-tick reruns of earlier batches with the same faults


def touched(r, Q, side):
    if 'extent' in r:
        lo, hi = r['extent']['x_lo'], r['extent']['x_hi']
    else:
        lo, hi = r['x0'], r['x0'] + side - 1
    return sorted(set(range(lo // Q, hi // Q + 1)))


def main():
    included, excluded = [], {}
    rows = []
    for fn in sorted(glob.glob(os.path.join(DIR, '*.json'))):
        name = os.path.basename(fn)[:-5]
        if name in EXCLUDE:
            excluded[name] = EXCLUDE[name]
            continue
        if name.endswith(RERUN_SUFFIX):
            excluded[name] = 'per-tick rerun of an earlier batch with the same faults (counted there)'
            continue
        d = json.load(open(fn))
        if 'rings' not in d or 'summary' not in d and 'upper_cells' not in d:
            excluded[name] = 'not a campaign batch'
            continue
        Q = d.get('identity', {}).get('Q') or candidates.load(d['candidate']).p.Q
        ncol = d['upper_cells']
        side = d.get('side') or d['args'].get('side', 200)
        included.append(dict(receipt=name, sha256=hashlib.sha256(open(fn, 'rb').read()).hexdigest()))
        for r in d['rings']:
            if r.get('kind') != 'E1':
                continue
            cols = touched(r, Q, side)
            steps = r.get('steps', [])
            wrong = [(s['upper_step'], s['wrong_upper_cells']) for s in steps if s['wrong_upper_cells']]
            inside = all(set(x % ncol for x in w) <= set(c % ncol for c in cols) for _, w in wrong)
            small = all(len(w) <= 2 and (len(w) < 2 or (w[1] - w[0]) % ncol in (1, ncol - 1)) for _, w in wrong)
            kind = ('never wrong' if not wrong else
                    'one upper time, at most 2 adjacent cells, inside the touched colonies'
                    if len(wrong) == 1 and small and inside else 'other')
            rows.append(dict(receipt=name, candidate=d['candidate'], phase=r.get('phase'), place=r.get('place'),
                             touched_colonies=len(cols), upper_steps=len(steps), outcome=kind,
                             wrong=[[k, w[:12]] for k, w in wrong]))
    out = dict(rule=__doc__.strip().split('\n\n')[1], included=included, excluded=excluded, scopes={})
    for scope, test in (('at most two colonies', lambda r: r['touched_colonies'] <= 2),
                        ('three or more colonies', lambda r: r['touched_colonies'] >= 3)):
        sel = [r for r in rows if test(r)]
        out['scopes'][scope] = dict(
            error_rings=len(sel), upper_steps=sum(r['upper_steps'] for r in sel),
            outcomes={k: sum(r['outcome'] == k for r in sel) for k in
                      ('never wrong', 'one upper time, at most 2 adjacent cells, inside the touched colonies',
                       'other')},
            other=[{k: r[k] for k in ('receipt', 'phase', 'place', 'touched_colonies', 'wrong')}
                   for r in sel if r['outcome'] == 'other'])
    with open(OUT, 'w') as fh:
        json.dump(out, fh, indent=1)
    for scope, v in out['scopes'].items():
        print(scope, json.dumps({k: v[k] for k in ('error_rings', 'upper_steps', 'outcomes')}))
    print('receipts counted', len(included), 'excluded', len(excluded))


if __name__ == '__main__':
    main()
