"""Compare complete saved wide/narrow burst states without evolving either."""
import argparse
import json
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f
from experiments.fixed_rule.run_retimed_holder_streamed_repair import sha


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
    out=Path(parser.parse_args().output)
    if out.exists():raise FileExistsError(out)
    paths=[Path('figs/fixed_rule/retimed_holder_'+name+'_burst_v1.json') for name in ('contextual','wide')]
    receipts=[json.loads(path.read_text()) for path in paths]
    for path,receipt in zip(paths,receipts):
        assert receipt['completed'] and sha(path.with_suffix('.npz'))==receipt['artifact_sha256']
    shift=receipts[1]['center_colony']-receipts[0]['center_colony']
    rows=[]
    with np.load(paths[0].with_suffix('.npz'),allow_pickle=False) as old,np.load(paths[1].with_suffix('.npz'),allow_pickle=False) as wide:
        np.testing.assert_array_equal(old['upper_context'],wide['upper_context'])
        np.testing.assert_array_equal(old['selected_upper_positions'],wide['selected_upper_positions'][shift:shift+17])
        for key in ('inherited_bank','inherited_signals'):
            np.testing.assert_array_equal(old[key],wide[key][shift:shift+17])
        for key in ('schedule','replacements'):
            np.testing.assert_array_equal(old[key],wide[key])
        for tick in range(35):
            prefix='checkpoint' if tick==0 else f'tick{tick}'
            a,b=old[prefix+'_bank'],wide[prefix+'_bank'][shift:shift+17]
            different=np.flatnonzero(np.any(a!=b,axis=1)).tolist()
            # The full seven-parent neighborhoods of these three old colonies
            # lie inside its 17-cell parent window; complete banks must agree.
            for col in (7,8,9):
                for key in ('bank','active_rows','counts','signals'):
                    np.testing.assert_array_equal(old[prefix+'_'+key][col],wide[prefix+'_'+key][shift+col])
            if tick:
                np.testing.assert_array_equal(old[prefix+'_positions']+shift*f.Q,wide[prefix+'_positions'])
                np.testing.assert_array_equal(old[prefix+'_values'],wide[prefix+'_values'])
            rows.append(dict(tick=tick,background_bank_mismatch_old_columns=different,
                             central_three_complete_banks_and_controllers_equal=True,
                             translated_complete_exceptions_equal=bool(tick)))
    result=dict(passed=True,physical_position_shift=shift*f.Q,rows=rows,
                same_complete_initial_inherited_banks=True,same_unfiltered_noise=True,
                all_34_complete_exception_sets_equal_after_translation=True,
                source_receipts={str(path):sha(path) for path in paths},
                source_artifacts={str(path.with_suffix('.npz')):receipt['artifact_sha256'] for path,receipt in zip(paths,receipts)},
                source_sha256={str(Path(__file__)):sha(__file__),str(Path(f.__file__)):sha(f.__file__)},
                scope='Saved burst-state comparison only. Complete central lower banks and controllers '
                      'agree; remote background banks differ. No later transfer, noisy commit or repair claimed.')
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'passed':True,'ticks':34,'initial_background_mismatches':rows[0]['background_bank_mismatch_old_columns']}))


if __name__=='__main__':main()
