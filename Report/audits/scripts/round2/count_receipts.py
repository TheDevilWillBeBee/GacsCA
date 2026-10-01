"""Recount report headline quantities from the published on-disk JSON receipts."""
import json
from collections import Counter
from pathlib import Path

BASE = Path('figs/fixed_rule/design_optimization')
read = lambda p: json.loads(p.read_text())

for candidate, batch in [('G14', 'b71'), ('G14', 'b72'), ('G14', 'b73')] + [
        ('G15', b) for b in ('b61', 'b62', 'b63', 'b64', 'b65', 'b66', 'b67',
                             'b68', 'b69', 'b81', 'b82', 'b91', 'b92', 'b93', 'b95', 'b96')]:
    fs = sorted((BASE / 'level1_campaign').glob(f'{candidate}_{batch}*.json'))
    if batch == 'b91':
        fs = [p for p in fs if 'holder_' not in p.name and 'logical_' not in p.name]
    ds = [read(p) for p in fs]
    sums = Counter()
    for d in ds:
        for k, v in d['summary'].items():
            if isinstance(v, int):
                sums[k] += v
    print(candidate, batch, len(fs), dict(sums))

root = BASE / 'three_level'
fs = sorted(root.glob('G15_*.json'))
counts = Counter()
bad = []
residue = []
for p in fs:
    d = read(p)
    if d['cmd'] not in ('repair2', 'copy2'):
        continue
    counts[d['cmd'] + '_files'] += 1
    for j, row in enumerate(d['level2'][0]['rings']):
        if d['cmd'] == 'repair2' and row['wipe_colonies'] < 3:
            counts['excluded_small_or_control'] += 1
            continue
        counts['total'] += 1
        counts[d['cmd']] += 1
        first = row['level2_cells_wrong']
        later = [x['rings'][j] for x in d['level2'][1:]]
        if first:
            counts['one_wrong_first'] += 1
            if first != [0]:
                bad.append((p.name, j, 'first', first))
        else:
            counts['clean_first'] += 1
            if row['level1_cells_differing']:
                bad.append((p.name, j, 'L1 not clean first', row['level1_cells_differing']))
        if any(x['level2_cells_wrong'] or (x['level1_cells_differing'] and not d.get('level1_noise_grid')) for x in later):
            bad.append((p.name, j, 'later', later))
        if d['cmd'] == 'repair2':
            if 'physical_at_handoff' in d:
                hand = d['physical_at_handoff'][j]
                residue.append((p.name, hand.get('sites_not_explained_by_level1_difference'),
                                hand.get('unexplained_bits_in_represented_info_slots'),
                                hand.get('unexplained_bits_elsewhere')))
            for phys in d['physical'][1:]:
                if phys['rings'][j]['level1_closure_bad_away_from_ends']:
                    bad.append((p.name, j, 'closure', phys['rings'][j]['level1_closure_bad_away_from_ends']))
print('three-level counts', dict(counts))
print('three-level violations', bad)
print('handoff residue positive', [x for x in residue if x[1]])
all_handoff = [r for p in fs for r in read(p).get('physical_at_handoff', [])]
print('handoff field check', 'recorded', len(all_handoff),
      'outside_Info', sum(bool(set(r.get('fields_differing_from_reference', {})) - {'info'})
                          for r in all_handoff),
      'represented_slots_recorded', sum('unexplained_bits_in_represented_info_slots' in r
                                        for r in all_handoff),
      'represented_slot_bits', sum(r.get('unexplained_bits_in_represented_info_slots', 0)
                                   for r in all_handoff))
ph = read(root / 'G15_phases_n2_2.json')
print('phases', ph['stages'], 'results', {k:(len(v),sum(r['level1_exact'] for r in v),sum(r['level2_exact'] for r in v)) for k,v in ph['results'].items()})
for p in sorted(root.glob('G15_closure2*.json')):
    d = read(p)
    print('closure2', p.name, len(d['steps']), sum(x['exact'] for x in d['steps']))
for p in sorted((BASE / 'level0').glob('G*.json')):
    d = read(p)
    if d.get('healthy'):
        print('level0', p.name, d['trials'], d['failures'])

# Broad campaign aggregate.  There are duplicate rerun/attribution receipts,
# so print both raw receipt totals and a conservative per-scenario dedup.
raw = Counter()
unique = {}
for p in sorted((BASE / 'level1_campaign').glob('*.json')):
    d = read(p)
    if 'rings' not in d or 'summary' not in d:
        continue
    a = d['args']
    ident = d.get('identity', {}).get('candidate_sha256', '')
    for i, r in enumerate(d['rings']):
        if r['kind'] != 'E1':
            continue
        raw['rings'] += 1
        raw['steps'] += len(r['steps'])
        key = (a.get('candidate'), ident, a.get('upper_age'), a.get('target'), a.get('slice'),
               a.get('seed'), a.get('mode'), a.get('e0_all'), r.get('noise_seed'),
               r.get('phase'), r.get('place'), r.get('x0'), r.get('t0'), repr(r.get('boxes')),
               a.get('side'), a.get('wipe'), a.get('height'), a.get('density'),
               a.get('pairs'), a.get('density_count'), i if r.get('phase') == 'random' else None)
        if key not in unique or len(r['steps']) > len(unique[key]['steps']):
            unique[key] = r
tot = Counter()
for r in unique.values():
    tot['rings'] += 1
    tot['steps'] += len(r['steps'])
    n = sum(bool(s.get('wrong_upper_cells')) for s in r['steps'])
    tot['never_wrong' if n == 0 else 'one_wrong_time' if n == 1 else 'multiple_wrong_times'] += 1
print('campaign raw all receipts', dict(raw))
print('campaign dedup by scenario', dict(tot))

for batch, original in [('b1', 'G8_b1_age0_mid.json'),
                        ('b2', 'G8_b2_eval_front.json'),
                        ('b3', 'G8_b3_precommit_mid.json')]:
    a = read(BASE / 'level1_campaign' / original)
    b = read(BASE / 'level1_campaign' / f'G8_{batch}_commit_rerun_sameseeds.json')
    old = {r['place']: [x['physical_sites_differing'] for x in r['steps']]
           for r in a['rings'] if r['phase'] == 'commit'}
    new = {r['place']: (r['noise_seed'], [x['physical_sites_differing'] for x in r['steps']])
           for r in b['rings']}
    print('G8 same-fault rerun', batch, old, new,
          'same_first_three', all(old[k] == v[1][:3] for k, v in new.items()))
