"""Execute the complete audited contextual suffix with the compiled scheduler.

Compare every complete saved state and every physical event interval against
the prior independently scalar-audited Python execution. No endpoint reference
is installed into the evolving compiled state.
"""
import argparse
import json
import resource
import time
from pathlib import Path

import numpy as np

from gacsca.fixed_rule import retimed_holder_compiled_events as events
from gacsca.fixed_rule import retimed_holder_inert_storage as storage
from gacsca.fixed_rule import retimed_holder_rule as f
from experiments.fixed_rule.run_retimed_holder_streamed_repair import sha


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output',required=True)
    args = parser.parse_args()
    out = Path(args.output);artifact = out.with_suffix('.npz')
    if out.exists() or artifact.exists():raise FileExistsError(out)
    started = time.perf_counter()
    source = Path('figs/fixed_rule/retimed_holder_contextual_macrostep_v1.json')
    prior = json.loads(source.read_text())
    assert prior['completed'] and prior['error'] is None
    assert sha(source.with_suffix('.npz')) == prior['artifact_sha256']
    audit_path = Path('figs/fixed_rule/retimed_holder_contextual_macrostep_audit_v1.json')
    audit = json.loads(audit_path.read_text());assert audit['passed']
    index_path = Path('figs/fixed_rule/retimed_holder_contextual_macrostep_evidence_v1.json')
    index = json.loads(index_path.read_text());assert index['passed']
    for path,digest in index['files'].items():assert sha(path) == digest,path
    rows,completed,error = [],False,None
    with np.load(source.with_suffix('.npz'),allow_pickle=False) as saved:
        initial,signals = saved['initial_words'],saved['signals']
        begin = prior['initial_time']
        world = events.World(lambda sites:storage.raw_words(initial,signals,begin%f.U,sites),size=len(initial),time=begin)
        try:
            for k,expected in enumerate(prior['checkpoints']):
                while world.time<expected['time']:
                    world.advance(min(expected['time']-world.time,10000000))
                np.testing.assert_array_equal(world.words,saved[f'checkpoint{k}_words'])
                np.testing.assert_array_equal(world.signals,saved[f'checkpoint{k}_signals'])
                assert world.advance(0)==expected['metrics']
                assert list(world.heads)==expected['heads']
                assert len(world.trace)==expected['trace_events']
                row = dict(time=world.time,complete_procedure_words=world.words.size,
                           complete_Signal_words=world.signals.size,trace_events=len(world.trace),
                           seconds=time.perf_counter()-started)
                rows.append(row);print(json.dumps(row),flush=True)
            trace = np.array(world.trace,dtype=np.uint64).reshape(-1,3)
            np.testing.assert_array_equal(trace,saved['physical_event_trace'])
            np.testing.assert_array_equal(world.words,saved['final_words'])
            np.testing.assert_array_equal(world.signals,saved['final_signals'])
            completed = True
        except Exception as exc:
            error = f'{type(exc).__name__}: {exc}'
    np.savez_compressed(artifact,final_words=world.words,final_signals=world.signals,
                        physical_event_trace=np.array(world.trace,dtype=np.uint64).reshape(-1,3))
    sources = (Path(__file__),Path(events.__file__),Path(events.__file__).with_suffix('.cc'),
               Path(events.global_events.__file__),Path(storage.__file__),Path(f.__file__))
    binaries = (Path(events.library()._name),Path(events.native.library()._name))
    result = dict(passed=completed,error=error,checkpoints=rows,final_time=world.time,
                  complete_trace_equal=completed,final_metrics=world.advance(0),
                  source_receipt=str(source),source_receipt_sha256=sha(source),
                  source_artifact_sha256=prior['artifact_sha256'],
                  prior_scalar_audit=str(audit_path),prior_scalar_audit_sha256=sha(audit_path),
                  prior_evidence=str(index_path),prior_evidence_sha256=sha(index_path),
                  source_sha256={str(path):sha(path) for path in sources},
                  binaries={str(path):sha(path) for path in binaries},
                  descriptor_sha256=f.self_description().digest(),artifact_sha256=sha(artifact),
                  seconds=time.perf_counter()-started,
                  host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  scope='Compiled physical event scheduler matches all six complete checkpoints '
                        'and every trace interval of the independently scalar-audited noisy '
                        '17-colony suffix. No larger-window lower evolution is asserted here.')
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)
    if not completed:raise SystemExit(1)


if __name__ == '__main__':main()
