"""Bind actual wider decoded states to the full-upper-colony halo witness.

This compares saved physical outputs, rather than installing upper successors.
It also checks complete lower history refresh against the healthy terminal
identity. Physical lower embedding outside the 73-colony ring remains open.
"""
import argparse
import json
from pathlib import Path
import resource
import time

import numpy as np

from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_projected as r
from gacsca.fixed_rule import retimed_holder_literal_cone as cone
from gacsca.fixed_rule import retimed_holder_terminal_reference as terminal
from experiments.fixed_rule.run_retimed_holder_streamed_repair import sha


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
    out=Path(parser.parse_args().output)
    if out.exists():raise FileExistsError(out)
    started=time.perf_counter()
    paths={
        'macro':Path('figs/fixed_rule/retimed_holder_wide_macrostep_v1.json'),
        'run':Path('figs/fixed_rule/retimed_holder_wide_next_periods_3_v2.json'),
        'halo':Path('figs/fixed_rule/retimed_holder_upper_halo_v1.json'),
        'full':Path('figs/fixed_rule/retimed_holder_upper_embedding_v1.json'),
    }
    receipts={key:json.loads(path.read_text()) for key,path in paths.items()}
    for key,path in paths.items():
        data=receipts[key]
        assert data.get('passed',data.get('completed',False)) and data.get('error') is None
        assert sha(path.with_suffix('.npz'))==data['artifact_sha256']
        for source,digest in data['source_sha256'].items():assert sha(source)==digest,source
    comparisons=[];histories=[]
    with np.load(paths['macro'].with_suffix('.npz'),allow_pickle=False) as macro, np.load(paths['run'].with_suffix('.npz'),allow_pickle=False) as run, np.load(paths['halo'].with_suffix('.npz'),allow_pickle=False) as halo, np.load(paths['full'].with_suffix('.npz'),allow_pickle=False) as full:
        target=halo['target'];selected=full['selected']
        np.testing.assert_array_equal(macro['parent_raw'],halo['initial'])
        np.testing.assert_array_equal(halo['positions'][target],selected)
        np.testing.assert_array_equal(run['decoded_before'],macro['decoded_raw'])
        normalized=cone.normalize(macro['decoded_raw'].copy())
        np.testing.assert_array_equal(normalized,run['expected_normalized_info'])
        np.testing.assert_array_equal(normalized,halo['tick0_actual'])
        np.testing.assert_array_equal(macro['expected_decoded_raw'],halo['tick0_healthy'])
        for step in range(4):
            actual=normalized if step==0 else run[f'period{step}_decoded']
            healthy=macro['expected_decoded_raw'] if step==0 else cone.normalize(np.pad(run[f'period{step}_healthy_upper'],((0,0),(len(f.STATIC),0))))
            np.testing.assert_array_equal(actual,halo[f'tick{step}_actual'])
            np.testing.assert_array_equal(healthy,halo[f'tick{step}_healthy'])
            np.testing.assert_array_equal(actual[target],full[f'tick{step}_actual'][selected])
            np.testing.assert_array_equal(healthy[target],full[f'tick{step}_healthy'][selected])
            different=np.flatnonzero(np.any(actual[target]!=healthy[target],axis=1))
            comparisons.append(dict(subsequent_periods=step,central_complete_raw_words=actual[target].size,
                                    central_upper_different_positions=selected[different].tolist()))
        for step in (2,3):
            parents=r.cells_from_array(run[f'period{step-1}_healthy_upper'])
            expected=terminal.terminal(parents)
            diff=run[f'period{step}_bank']!=expected['committed_bank']
            signal_diff=run[f'period{step}_signals']!=expected['signals']
            histories.append(dict(period=step,different_complete_bank_words=int(np.count_nonzero(diff)),
                                  different_bank_colonies=np.flatnonzero(np.any(diff,axis=1)).tolist(),
                                  different_Signal_bits=int(np.count_nonzero(signal_diff))))
        assert histories[-1]['different_complete_bank_words']==0 and histories[-1]['different_Signal_bits']==0
        retained_positions=run['retained_positions'].tolist();retained_values=run['retained_values'].tolist()
        assert len(retained_positions)==3
    sources=(Path(__file__),Path(f.__file__),Path(r.__file__),Path(cone.__file__),Path(terminal.__file__))
    result=dict(passed=True,central_upper_states_match_complete_colony=True,central_target_cells=17,
                physical_lower_colonies=73,comparisons=comparisons,healthy_terminal_comparisons=histories,
                retained_nonMEM_positions=retained_positions,retained_nonMEM_values=retained_values,
                source_receipts={str(path):sha(path) for path in paths.values()},
                source_artifacts={str(path.with_suffix('.npz')):receipts[key]['artifact_sha256'] for key,path in paths.items()},
                source_sha256={str(path):sha(path) for path in sources},
                seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                scope='Actual wider decoded outputs match every raw field of the full-upper-colony '
                      'trajectory in the central 17 cells, and third-period complete banks/Signals '
                      'match the healthy terminal identity. Does not prove full-Q lower physical '
                      'boundary transfer, physical erasure of retained Data or general robustness.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
