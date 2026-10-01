"""Recompute selected claims directly from campaign receipts."""
import json
from pathlib import Path

root = Path('figs/fixed_rule/design_optimization')
for original, longer in (('G8_b1_age0_mid', 'G8_b1_commit_5steps'),
                         ('G8_b2_eval_front', 'G8_b2_commit_5steps')):
    a = json.loads((root / 'level1_campaign' / (original + '.json')).read_text())
    b = json.loads((root / 'level1_campaign' / (longer + '.json')).read_text())
    for place in ('mid', 'left', 'right'):
        i, ra = next((i, r) for i, r in enumerate(a['rings'])
                     if r['phase'] == 'commit' and r['place'] == place)
        j, rb = next((j, r) for j, r in enumerate(b['rings'])
                     if r['phase'] == 'commit' and r['place'] == place)
        print('rerun', original, place, 'same_box', (ra['x0'], ra['t0']) == (rb['x0'], rb['t0']),
              'noise_seeds', a['args']['seed'] + 50 + i, b['args']['seed'] + 50 + j,
              'step3_differences', ra['steps'][2]['physical_sites_differing'],
              rb['steps'][2]['physical_sites_differing'])

for name in ('G5', 'G6', 'G7', 'G8'):
    d = json.loads((root / 'error_levels' / (name + '_main_seed3.json')).read_text())
    e0 = next(r for r in d['rings'] if r['name'] == 'E0 dense (all periods)')
    print('dense_e0', name, [x['physical_sites_differing'] for x in e0['periods']])
