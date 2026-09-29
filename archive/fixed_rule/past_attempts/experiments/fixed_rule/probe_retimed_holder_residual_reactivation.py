"""Small literal pilot: actual repaired tail plus two fresh fault groups."""
import json
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_core as c
from gacsca.fixed_rule import retimed_holder_literal_cone as cone


def main():
    path = Path('figs/fixed_rule/retimed_holder_residual_reactivation_pilot_v1.npz')
    if path.exists():
        raise FileExistsError(path)
    with np.load('figs/fixed_rule/retimed_holder_wide_next_periods_3_v2.npz') as old:
        image = cone.BankImage(old['period3_bank'], old['period3_signals'])
        a = int(old['retained_positions'][0])
        positions = np.arange(a-200, a+203)
        comparison = image.cells(positions)
        actual = comparison.copy()
        for pos, value in zip(old['retained_positions'], old['retained_values']):
            for d in f.OFFSETS:
                actual[positions+d == pos, f.COL[f's{d+2}_data']] = value
    save = dict(initial_actual=actual, initial_comparison=comparison, initial_positions=positions)
    for tick in range(8):
        if tick == 1:
            for e in (-3, -2, -1):
                i = a+e-positions[0]
                row = comparison[i].copy()
                slot = -1-e+2
                row[f.COL[f's{slot}_head']] = 1
                row[f.COL[f's{slot}_phase']] = c.READ_A
                row[f.COL[f's{slot}_ra']] = 65
                actual[i] = comparison[i] = row
        if tick == 2:
            for e in (-5, -4, -3, 3, 4, 5):
                i = a+e-positions[0]
                row = comparison[i:i+1].copy()
                row[0, f.COL['address']] = 64+e
                cone.normalize(row)
                actual[i] = comparison[i] = row[0]
        actual = cone.step(actual)[7:-7].copy()
        comparison = cone.step(comparison)[7:-7].copy()
        positions = positions[7:-7]
        diff = np.count_nonzero(actual != comparison, axis=0)
        save[f'tick{tick+1}_actual'] = actual
        save[f'tick{tick+1}_comparison'] = comparison
        save[f'tick{tick+1}_positions'] = positions
        print(json.dumps(dict(tick=tick+1, fields={n:int(diff[j]) for j,(n,_) in enumerate(f.SCHEMA) if diff[j]},
                              center_Address=int(actual[a-positions[0],f.COL['address']]),
                              center_Flag1=int(actual[a-positions[0],f.COL['f1']]))), flush=True)
    np.savez_compressed(path, **save)


if __name__ == '__main__':
    main()
