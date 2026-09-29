"""Resume the exact retained packet-emission boundary of high-rate case4."""
import json
from pathlib import Path
import time
import numpy as np
from gacsca.fixed_rule import compact16_holder_late_mail_events as events,compact16_holder_literal_cone as cone
from gacsca.fixed_rule import compact16_holder_rule as f,compact16_holder_projected as r,compact16_holder_program as p
from experiments.fixed_rule.validate_compact16_holder_endpoint import guard
from experiments.fixed_rule.run_compact16_holder_streamed_depth2 import sha


def main():
    output=Path('figs/fixed_rule/compact16_holder_mail_macrostep_v1.json');artifact=output.with_suffix('.npz')
    if output.exists() or artifact.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();prior_path=Path('figs/fixed_rule/compact16_holder_all_noise_macrosteps_v2.json');prior=json.loads(prior_path.read_text())
    record=prior['trials'][4];assert not record['completed'] and record['stopped_age']==514889820
    assert record['error']=="RuntimeError('resident prefix step rejected: -4')"
    assert sha(record['checkpoint_artifact'])==record['checkpoint_artifact_sha256']
    with np.load(record['checkpoint_artifact'],allow_pickle=False) as z:raw=z['case4_stopped_raw'].copy();expected=z['expected_upper_raw'].copy()
    g=p.layout();saved=dict(initial_raw=raw,expected_upper_raw=expected);trace=[]
    with events.World(raw) as world:
        np.testing.assert_array_equal(world.raw(),raw)
        with guard():metrics=world.advance(1)
        emitted=world.raw();np.testing.assert_array_equal(emitted,cone.step(raw));saved['emitted_raw']=emitted
        assert emitted[2862,f.COL['s2_lp_valid']]==1
        trace.append(dict(age=world.age,metrics=metrics));print(json.dumps(trace[-1]),flush=True)
        for age in (f.ACTIVE_ENDS[-1]-1,f.ACTIVE_ENDS[-1],f.U-2,f.U-1):
            tick=time.perf_counter()
            with guard():metrics=world.advance(age-world.age)
            saved[f'age{age}']=world.raw();trace.append(dict(age=world.age,metrics=metrics,seconds=time.perf_counter()-tick))
            print(json.dumps(trace[-1]),flush=True)
        before=world.raw()
        with guard():commit_metrics=world.advance(1)
        actual=world.raw();np.testing.assert_array_equal(actual,cone.step(before));saved['postcommit']=actual
        decoded=actual[list(g.info),f.COL['s2_data']];saved['decoded']=decoded
        widths=[name for (name,width),value in zip(f.SCHEMA,decoded) if int(value)>=1<<width]
        projected_differences=None;projection_valid=False
        if not widths:
            cell=f.decode_cell(decoded);projection_valid=np.array_equal(f.encode_cell(r.lift(r.project(cell))),decoded)
            projected_differences=[name for (name,_),a,b in zip(r.SCHEMA,r.encode_cell(r.project(cell)),r.encode_cell(r.project(f.decode_cell(expected)))) if a!=b]
        device=world.device_bytes
    np.savez_compressed(artifact,**saved)
    result=dict(passed=True,reference=str(prior_path),reference_sha256=sha(prior_path),resumed_case=4,starting_age=int(raw[0,f.COL['age']]),
                exact_same_time_restore=True,real_packet_emission_checked=True,trace=trace,commit_metrics=commit_metrics,
                decoded_matches_intended_rule=np.array_equal(decoded,expected),raw_decoded_differences=int(np.count_nonzero(decoded!=expected)),
                invalid_word_width_fields=widths,decoded_fixed_projection_valid=projection_valid,projected_differing_fields=projected_differences,
                final_age=0,explicit_device_bytes=device,artifact=str(artifact),artifact_sha256=sha(artifact),seconds=time.perf_counter()-start,
                descriptor_sha256=f.self_description().digest(),source_sha256={str(Path(x)):sha(x) for x in (__file__,events.__file__)},
                scope='One previously stopped actual noisy state, exact packet-preserving continuation to actual commit. Completes the last of eight retained histories; no threshold or next-period/cross-level claim.')
    with output.open('x') as out:out.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='trace'}),flush=True)


if __name__=='__main__':main()
