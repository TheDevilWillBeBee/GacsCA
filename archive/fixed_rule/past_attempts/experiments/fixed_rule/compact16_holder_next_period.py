"""Continue all eight actual committed states for one whole fault-free period.

Malformed upper encodings remain physical Data, unmasked and unchanged at input.
A projected target G is compared only when all105mutable input widths are valid.
"""
import json
from pathlib import Path
import time
import numpy as np
from gacsca.fixed_rule import compact16_holder_coherent_epochs as epochs,compact16_holder_coherent_image as image
from gacsca.fixed_rule import compact16_holder_rule as f,compact16_holder_projected as r,compact16_holder_program as p
from gacsca.fixed_rule import compact16_holder_literal_cone as cone
from experiments.fixed_rule.validate_compact16_holder_endpoint import guard
from experiments.fixed_rule.run_compact16_holder_streamed_depth2 import sha


def inspect(words):
    projected=np.array([words[f.COL[name]] for name,_ in r.SCHEMA],dtype=np.uint64)
    invalid=[dict(field=name,width=width,value=int(value)) for (name,width),value in zip(r.SCHEMA,projected) if int(value)>=1<<width]
    return projected,invalid


def target(words):
    projected,bad=inspect(words)
    if bad:return None
    cell=r.lift(r.decode_cell(projected))
    return np.array(f.encode_cell(r.lift(r.project(f.local_step((cell,)*15)))),dtype=np.uint64)


def main():
    root=Path('figs/fixed_rule');output=root/'compact16_holder_next_period_v1.json';journal=output.with_suffix('.jsonl')
    if output.exists() or journal.exists():raise FileExistsError('preserve evidence')
    started=time.perf_counter();g=p.layout();audit_path=root/'compact16_holder_all_noise_macrosteps_audit_v1.json';audit=json.loads(audit_path.read_text())
    assert audit['passed'] and audit['all_eight_histories_resolved'];rows=[]
    for case in range(8):
        source=root/('compact16_holder_mail_macrostep_v1.npz' if case==4 else f'compact16_holder_all_noise_macrosteps_v2_case{case}.npz')
        with np.load(source,allow_pickle=False) as z:
            raw=z['postcommit' if case==4 else f'case{case}_postcommit'].copy();healthy_first=z['expected_upper_raw'].copy()
        saved=dict(initial_raw=raw,healthy_expected_second=target(healthy_first));initial_info=raw[list(g.info),f.COL['s2_data']].copy()
        desired=target(initial_info);_,invalid_input=inspect(initial_info)
        if desired is not None:saved['expected_from_actual_projected_input']=desired
        trace=[];t=time.perf_counter();failure=None
        with epochs.World(raw=raw) as world:
            np.testing.assert_array_equal(world.raw(),raw)
            try:
                for age in (1,f.CAPTURE_AGE-1,f.CAPTURE_AGE,f.WF_START-1,f.WF_START+1,f.WF_END+f.Q,f.U-1):
                    moment=time.perf_counter()
                    with guard():metrics=world.advance(age-world.age)
                    actual=world.raw();saved[f'age{age}']=actual
                    if age==1:np.testing.assert_array_equal(actual,cone.step(raw))
                    if age==f.CAPTURE_AGE:np.testing.assert_array_equal(actual,cone.step(saved[f'age{age-1}']))
                    trace.append(dict(age=age,metrics=metrics,seconds=time.perf_counter()-moment));print(json.dumps(dict(case=case,**trace[-1])),flush=True)
                before=world.raw()
                with guard():commit_metrics=world.advance(1)
                actual=world.raw();np.testing.assert_array_equal(actual,cone.step(before));saved['postcommit']=actual
                decoded=actual[list(g.info),f.COL['s2_data']].copy();saved['decoded']=decoded
                _,invalid_output=inspect(decoded)
                row=dict(case=case,completed=True,input_invalid_projected_words=invalid_input,output_invalid_projected_words=invalid_output,
                         intended_G_target_defined=desired is not None,actual_projected_macrostep_matches=None if desired is None else np.array_equal(decoded,desired),
                         matches_undamaged_second_macrostep=np.array_equal(decoded,saved['healthy_expected_second']),
                         output_raw_differences_from_undamaged=int(np.count_nonzero(decoded!=saved['healthy_expected_second'])),
                         final_age=world.age,commit_metrics=commit_metrics,trace=trace,seconds=time.perf_counter()-t)
            except (ValueError,RuntimeError) as exc:
                saved['stopped_raw']=world.raw();row=dict(case=case,completed=False,stopped_age=world.age,error=repr(exc),trace=trace,seconds=time.perf_counter()-t)
        artifact=output.with_name(output.stem+f'_case{case}.npz')
        if artifact.exists():raise FileExistsError(artifact)
        np.savez_compressed(artifact,**saved);row.update(artifact=str(artifact),artifact_sha256=sha(artifact),initial_artifact=str(source),initial_artifact_sha256=sha(source))
        rows.append(row)
        with journal.open('a') as stream:stream.write(json.dumps(row)+'\n')
        print(json.dumps({k:v for k,v in row.items() if k not in ('trace','commit_metrics')}),flush=True)
    result=dict(passed=all(row['completed'] for row in rows),reference=str(audit_path),reference_sha256=sha(audit_path),cases=rows,
                all_initial_raw_states_retained=True,no_host_reencoding_or_width_masking=True,physical_periods_per_case=1,
                descriptor_sha256=f.self_description().digest(),seconds=time.perf_counter()-started,
                source_sha256={str(Path(x)):sha(x) for x in (__file__,epochs.__file__,image.__file__)},
                scope='One next full physical work period for every retained outcome, no further faults. Defined G comparison only for well-typed projected input; malformed input is evolved physically without pretending it was a valid upper state. One periodic top, not repair by healthy simulated neighbors.')
    with output.open('x') as stream:stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(output=str(output),passed=result['passed'],seconds=result['seconds'])),flush=True)


if __name__=='__main__':main()
