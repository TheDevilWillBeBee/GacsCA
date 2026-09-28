"""Reach the actual commit from retained headless noise states, with exact guard."""
import json
from pathlib import Path
import time
import numpy as np
from gacsca.fixed_rule import compact16_holder_canonical_gpu as gpu,compact16_holder_late_idle_gpu as idle
from gacsca.fixed_rule import compact16_holder_literal_cone as cone,compact16_holder_program as p
from gacsca.fixed_rule import compact16_holder_rule as f,compact16_holder_projected as r
from experiments.fixed_rule.audit_compact16_holder_dense_noise import restore
from experiments.fixed_rule.validate_compact16_holder_endpoint import guard
from experiments.fixed_rule.run_compact16_holder_streamed_depth2 import sha


def main():
    output=Path('figs/fixed_rule/compact16_holder_headless_macrostep_v1.json');artifact=output.with_suffix('.npz')
    if output.exists() or artifact.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();prior_path=Path('figs/fixed_rule/compact16_holder_canonical_noise_v1.json');prior=json.loads(prior_path.read_text())
    fixture_path=Path('figs/fixed_rule/compact16_holder_active_faults_v1.json');fixture=json.loads(fixture_path.read_text())
    assert prior['passed'] and sha(prior['artifact'])==prior['artifact_sha256']
    assert fixture['passed'] and sha(fixture['artifact'])==fixture['artifact_sha256']
    g=p.layout();saved={};rows=[]
    with np.load(fixture['artifact'],allow_pickle=False) as z:
        initial=z['initial_top'].copy();healthy_info=z['healthy_terminal_bank'][0,list(g.info)].copy()
    # Independent scalar target transition is diagnostic only, outside execution.
    expected=np.array(f.encode_cell(r.lift(r.project(f.local_step((f.decode_cell(initial[0]),)*15)))),dtype=np.uint64)
    np.testing.assert_array_equal(healthy_info,expected)
    saved['expected_upper_raw']=expected
    with np.load(prior['artifact'],allow_pickle=False) as z:
        for case in (3,7):
            raw=restore(z,case,16384);saved[f'case{case}_initial']=raw
            with gpu.World(raw) as world:
                amount=f.U-1-world.age
                with guard():metrics=idle.advance(world,amount)
                before=world.read();saved[f'case{case}_precommit']=before
                wanted=raw.copy();wanted[:,f.COL['age']]=f.U-1
                np.testing.assert_array_equal(before,wanted)
                with guard():world.run(1)
                actual=world.read();np.testing.assert_array_equal(actual,cone.step(before))
                saved[f'case{case}_postcommit']=actual
                # Decode physical Info, retaining every raw upper controller word.
                decoded=actual[list(g.info),f.COL['s2_data']].copy();saved[f'case{case}_decoded']=decoded
                changed=np.flatnonzero(decoded!=expected)
                try:f.decode_cell(decoded);typed=True
                except ValueError:typed=False
                rows.append(dict(case=case,starting_age=int(raw[0,f.COL['age']]),skipped_idle_ticks=amount,
                                 literal_commit_ticks=1,all_idle_raw_words_checked=raw.size,full_commit_CPU_words_checked=actual.size,
                                 decoded_complete_raw_words=len(decoded),decoded_matches_intended_rule=not len(changed),decoded_well_typed=typed,
                                 differing_decoded_fields=[f.SCHEMA[k][0] for k in changed],idle_metrics=metrics,
                                 final_age=world.age,explicit_device_bytes=world.device_bytes+4))
                print(json.dumps(rows[-1]),flush=True)
    np.savez_compressed(artifact,**saved)
    result=dict(passed=True,reference=str(prior_path),reference_sha256=sha(prior_path),fixture=str(fixture_path),fixture_sha256=sha(fixture_path),
                cases=rows,descriptor_sha256=f.self_description().digest(),artifact=str(artifact),artifact_sha256=sha(artifact),seconds=time.perf_counter()-start,
                source_sha256={str(Path(x)):sha(x) for x in (__file__,idle.__file__,Path(idle.__file__).with_suffix('.cu'))},
                scope='Only the two retained headless states satisfying the complete late-idle GPU guard. Exact idle advance then actual literal commit; compare every decoded raw controller field. Other six cases and general stochastic robustness remain unresolved.')
    with output.open('x') as out:out.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(output=str(output),seconds=result['seconds'])),flush=True)


if __name__=='__main__':main()
