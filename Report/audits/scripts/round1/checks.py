"""Independent, bounded checks of design-optimization receipts and cache loading."""
import json
import os
from pathlib import Path
import tempfile
import numpy as np

from gacsca.fixed_rule.design_optimization import candidates, codec


ROOT = Path('figs/fixed_rule/design_optimization')


def cache_check():
    source = candidates.CACHE
    original = candidates.load('R1')
    with tempfile.TemporaryDirectory(prefix='gacsca_audit_') as tmp:
        with np.load(Path(source) / 'R1.npz', allow_pickle=False) as z:
            a = {k: z[k] for k in z.files}
        a['rom'] = a['rom'].copy()
        nz = np.argwhere(a['rom'] != 0)[0]
        a['rom'][tuple(nz)] ^= np.uint32(1)
        np.savez(Path(tmp) / 'R1.npz', **a)
        candidates.CACHE = tmp
        try:
            altered = candidates.load('R1')
        finally:
            candidates.CACHE = source
    print('cache_mutation', {'accepted': True, 'same_netlist': original.comp.digest == altered.comp.digest,
                             'same_rom': bool(np.array_equal(original.rom, altered.rom)),
                             'same_candidate_digest': original.digest() == altered.digest()})


def candidate_table():
    for name in candidates.RECIPES:
        if name == 'R0':
            continue
        c = candidates.load(name)
        p = c.p
        nonzero_cols = np.nonzero(c.rom.any(axis=0))[0]
        last_page = int(max(nonzero_cols & ((1 << p.logNP) - 1))) + 1
        print('candidate', name, 'Q', p.Q, 'U', p.U, 'QU', p.Q * p.U,
              'width', c.W, 'gates', len(c.comp.gates),
              'physical_passes_used', last_page,
              'reported_recipe_passes_used', candidates.summary(c)['recipe_passes_used'],
              'fronts', getattr(p, 'fronts', 1))


def campaign_table():
    names = ['G8_b1_age0_mid', 'G8_b2_eval_front', 'G8_b3_precommit_mid',
             'G8_b4_density_pairs', 'G11_b11s17_age0_mid', 'G11_b11_age0_mid',
             'G11_b12_eval_front', 'G11_b13_precommit_mid', 'G11_b15_density_pairs',
             'G12_b21_age0_mid', 'G12_b22_eval_front', 'G10_b16_age0_mid',
             'G11_b14_full_eval_front', 'G13_b31_age0_mid', 'G13_b32_eval_front',
             'G13_b33_final_front', 'G13_b34_age0_mid', 'G13_b35_eval_front',
             'G13_b36_final_front']
    for name in names:
        d = json.loads((ROOT / 'level1_campaign' / (name + '.json')).read_text())
        s = d['summary']
        assert all(d['reference_exact'])
        assert len(d['rings']) >= s['total']
        print('campaign', name, 'sha', d['identity']['candidate_sha256'][:12],
              *(s[k] for k in ('total', 'damage_ok', 'repaired', 'identical')))


def gray_box_witness():
    d = json.loads((ROOT / 'level1_campaign' / 'G13_b34_age0_mid.json').read_text())
    s = next(r for r in d['rings'] if r['kind'] == 'E1' and r['phase'] == 'gather1_mid')
    x, t, side = s['x0'], s['t0'], d['side']
    # Each pair consists of two disjoint singleton candidate level-0 errors,
    # linked within a 24x24 box. The two pairs are 104x104 separated.
    a, b = [(x, t), (x + 1, t)], [(x + 150, t), (x + 151, t)]
    linked_inside = all(abs(pair[1][0] - pair[0][0]) < 24 and
                        abs(pair[1][1] - pair[0][1]) < 24 for pair in (a, b))
    separated = min(y[0] - z[0] for z in a for y in b) >= 104
    within_box = all(x <= z[0] < x + side and t <= z[1] < t + side for z in a + b)
    print('gray_dense_box', {'side': side, 'candidate_level1_pairs': [a, b],
                              'linked_inside': linked_inside, 'separated_104': separated,
                              'within_box': within_box})


def comb_geometry():
    for name in ('G13', 'G14'):
        p = candidates.load(name).p
        left_max = p.hi - 1 + p.H + 2
        right_min = p.Q + p.lo - p.H - 2
        gap = right_min - left_max
        print('comb', name, 'support_endpoint_gap', gap,
              'burst_span', 199, 'margin_formula', 2 * p.margin - 2 * p.H - 3)


def small_closure():
    for name, periods in (('R1', 3), ('G13', 2), ('G14', 1)):
        c = candidates.load(name)
        rng = np.random.default_rng(2897)
        up = codec.random_upper(c, 3, rng)
        C = c.c_backend()
        P = C.pack(codec.encode(c, up))
        for k in range(1, periods + 1):
            P = C.run_packed(P, c.p.U, threads=3)
            ref = c.step_numpy(up)
            X = C.unpack(P, 3 * c.p.Q)
            print(name + '_closure', k, 'equal', bool(np.array_equal(codec.decode(c, X), ref)),
                  'changed_bits', int((ref != up).sum()), flush=True)
            up = ref


if __name__ == '__main__':
    cache_check()
    candidate_table()
    campaign_table()
    gray_box_witness()
    comb_geometry()
    small_closure()
