"""Reproduce the stored healthy-terminal comparison without evolving a world."""
import argparse
import json
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_terminal_reference as terminal
from gacsca.fixed_rule import retimed_holder_projected as r
from experiments.fixed_rule.run_retimed_holder_streamed_repair import sha


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--input',required=True);args=parser.parse_args()
    record=json.loads(Path(args.input).read_text());assert record['passed']
    for source,digest in record['source_sha256'].items():assert sha(source)==digest,source
    base=Path('figs/fixed_rule')
    with np.load(base/'retimed_holder_contextual_next_periods_2_v1.npz',allow_pickle=False) as two,np.load(base/'retimed_holder_contextual_next_periods_3_v1.npz',allow_pickle=False) as three:
        for prefix in ('initial_actual','initial_normalized','normalization_actual','normalization_reference','period1','period2'):
            for name in ('bank','active_rows','counts','flags','signals','age','time'):
                np.testing.assert_array_equal(two[prefix+'_'+name],three[prefix+'_'+name])
        for name in ('retained_positions','retained_values','decoded_before','expected_normalized_info'):
            np.testing.assert_array_equal(two[name],three[name])
        observed=[]
        for step in (2,3):
            expected=terminal.terminal(r.cells_from_array(three[f'period{step-1}_healthy_upper']))
            diff=three[f'period{step}_bank']!=expected['committed_bank']
            observed.append(dict(period=step,different_bank_words=int(np.count_nonzero(diff)),different_bank_colonies=np.flatnonzero(np.any(diff,axis=1)).tolist(),different_Signal_bits=int(np.count_nonzero(three[f'period{step}_signals']!=expected['signals']))))
        assert observed==record['healthy_terminal_comparisons']
        assert len(three['retained_values'])==record['retained_nonMEM_words']==3
    assert record['all_common_saved_states_identical'] and record['reset_entry_certificate_applies_to_both_runs']
    print(json.dumps(dict(passed=True,healthy_terminal_comparisons=observed,retained_nonMEM_words=3),indent=2))


if __name__=='__main__':main()
