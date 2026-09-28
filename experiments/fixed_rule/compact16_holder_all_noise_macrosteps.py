"""Resolve every retained high-rate case through the actual current-period commit."""
import json
from pathlib import Path
import time
import numpy as np
from gacsca.fixed_rule import compact16_holder_late_events as events,compact16_holder_literal_cone as cone
from gacsca.fixed_rule import compact16_holder_rule as f,compact16_holder_projected as r,compact16_holder_program as p
from experiments.fixed_rule.audit_compact16_holder_dense_noise import restore
from experiments.fixed_rule.validate_compact16_holder_endpoint import guard
from experiments.fixed_rule.run_compact16_holder_streamed_depth2 import sha


def main():
    output=Path('figs/fixed_rule/compact16_holder_all_noise_macrosteps_v1.json');artifact=output.with_suffix('.npz')
    if output.exists() or artifact.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();prior_path=Path('figs/fixed_rule/compact16_holder_canonical_noise_v1.json');prior=json.loads(prior_path.read_text())
    fixture_path=Path('figs/fixed_rule/compact16_holder_active_faults_v1.json');fixture=json.loads(fixture_path.read_text())
    assert prior['passed'] and sha(prior['artifact'])==prior['artifact_sha256']
    assert fixture['passed'] and sha(fixture['artifact'])==fixture['artifact_sha256']
    with np.load(fixture['artifact'],allow_pickle=False) as z:initial=z['initial_top'].copy();healthy=z['healthy_terminal_bank'].copy()
    g=p.layout();expected=np.array(f.encode_cell(r.lift(r.project(f.local_step((f.decode_cell(initial[0]),)*15)))),dtype=np.uint64)
    np.testing.assert_array_equal(expected,healthy[0,list(g.info)])
    expected_projected=np.array(r.encode_cell(r.project(f.decode_cell(expected))),dtype=np.uint64)
    saved=dict(expected_upper_raw=expected);rows=[]
    with np.load(prior['artifact'],allow_pickle=False) as z:
        for case in range(8):
            raw=restore(z,case,16384);trace=[];t=time.perf_counter()
            with events.World(raw) as world:
                np.testing.assert_array_equal(world.raw(),raw)
                with guard():first_metrics=world.advance(1)
                np.testing.assert_array_equal(world.raw(),cone.step(raw))
                trace.append(dict(age=world.age,metrics=first_metrics));failed=None
                try:
                    for age in (f.ACTIVE_ENDS[-1]-1,f.ACTIVE_ENDS[-1],f.U-2,f.U-1):
                        step_start=time.perf_counter()
                        with guard():metrics=world.advance(age-world.age)
                        saved[f'case{case}_age{age}']=world.raw()
                        trace.append(dict(age=world.age,metrics=metrics,seconds=time.perf_counter()-step_start))
                        print(json.dumps(dict(case=case,**trace[-1])),flush=True)
                    before=world.raw()
                    with guard():metrics=world.advance(1)
                    actual=world.raw();saved[f'case{case}_postcommit']=actual
                    np.testing.assert_array_equal(actual,cone.step(before))
                    decoded=actual[list(g.info),f.COL['s2_data']];saved[f'case{case}_decoded']=decoded
                    changed=np.flatnonzero(decoded!=expected)
                    try:
                        cell=f.decode_cell(decoded);typed=True
                        projected=np.array(r.encode_cell(r.project(cell)),dtype=np.uint64);projection_equal=np.array_equal(f.encode_cell(r.lift(r.project(cell))),decoded)
                        differences=[name for (name,_),a,b in zip(r.SCHEMA,projected,expected_projected) if a!=b]
                    except ValueError:typed=False;projection_equal=False;differences=None
                    row=dict(case=case,completed=True,decoded_matches_intended_rule=not len(changed),raw_decoded_differences=len(changed),
                             projected_differing_fields=differences,decoded_word_widths_valid=typed,decoded_fixed_projection_valid=projection_equal,
                             final_age=world.age,explicit_device_bytes=world.device_bytes,seconds=time.perf_counter()-t,trace=trace)
                except (RuntimeError,ValueError) as exc:
                    saved[f'case{case}_stopped_raw']=world.raw()
                    row=dict(case=case,completed=False,stopped_age=world.age,error=repr(exc),trace=trace,seconds=time.perf_counter()-t)
                rows.append(row);print(json.dumps({k:v for k,v in row.items() if k!='trace'}),flush=True)
    np.savez_compressed(artifact,**saved)
    result=dict(passed=all(row['completed'] for row in rows),reference=str(prior_path),reference_sha256=sha(prior_path),fixture=str(fixture_path),fixture_sha256=sha(fixture_path),
                descriptor_sha256=f.self_description().digest(),all_eight_trials_retained=True,trials=rows,
                completed_macrosteps=sum(row['completed'] for row in rows),correct_macrosteps=sum(row.get('decoded_matches_intended_rule',False) for row in rows),
                artifact=str(artifact),artifact_sha256=sha(artifact),seconds=time.perf_counter()-start,
                source_sha256={str(Path(x)):sha(x) for x in (__file__,events.__file__)},
                scope='All eight previously retained local high-rate noise histories; exact same-time full-state restoration then guarded GPU events and actual commit. No new faults or estimated noise threshold.')
    with output.open('x') as out:out.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(output=str(output),seconds=result['seconds'],passed=result['passed'],correct_macrosteps=result['correct_macrosteps'])),flush=True)


if __name__=='__main__':main()
