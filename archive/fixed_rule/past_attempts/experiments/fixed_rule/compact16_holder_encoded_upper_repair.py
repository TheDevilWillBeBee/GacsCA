"""Execute two macrosteps repairing two full projected upper-cell defects.

63 simulated cells provide an explicit periodic seam outside the repair cone.
The upper states contain an actually running evaluator, including all replicas.
Only initial upper data are damaged; this is not a new lower-noise experiment.
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


def snapshot(world,saved,label):
    bank,records,counts=world.core.snapshot()
    assert world._flags is None and world.age in (0,f.U-1)
    saved[label+'_bank']=bank;saved[label+'_packed_records']=records;saved[label+'_counts']=counts
    saved[label+'_age']=np.array(world.age,dtype=np.uint64);saved[label+'_time']=np.array(world.time,dtype=np.uint64)
    return bank


def main():
    root=Path('figs/fixed_rule');output=root/'compact16_holder_encoded_upper_repair_v1.json';artifact=output.with_suffix('.npz')
    if output.exists() or artifact.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();fixture_path=root/'compact16_holder_active_faults_v1.json';fixture=json.loads(fixture_path.read_text())
    assert fixture['passed'] and sha(fixture['artifact'])==fixture['artifact_sha256']
    center=fixture['rom_operands']['b'];first=center-31
    with np.load(fixture['artifact'],allow_pickle=False) as z:healthy=z['checkpoint_raw'][first:first+63].copy()
    damaged=healthy.copy();maximum=r.Cell(**{name:(1<<width)-1 for name,width in r.SCHEMA})
    for site in (31,32):damaged[site]=f.encode_cell(r.lift(maximum))
    healthy1=cone.step(healthy);healthy2=cone.step(healthy1);expected1=cone.step(damaged);expected2=cone.step(expected1)
    assert np.any(expected1!=healthy1);np.testing.assert_array_equal(expected2,healthy2)
    # The possible two-step damage cone cannot reach the periodic seam.
    assert 31-14>0 and 32+14<62
    parents=tuple(r.project(f.decode_cell(row)) for row in damaged)
    saved=dict(initial_healthy_upper=healthy,initial_damaged_upper=damaged,healthy_upper_1=healthy1,healthy_upper_2=healthy2,
               expected_upper_1=expected1,expected_upper_2=expected2);rows=[];g=p.layout()
    with epochs.World(parents) as world:
        initial=snapshot(world,saved,'initial_lower')
        np.testing.assert_array_equal(initial[:,list(g.info)],damaged)
        for period in (1,2):
            t=time.perf_counter()
            with guard():metrics=world.advance(f.U-1)
            snapshot(world,saved,f'period{period}_precommit')
            with guard():commit=world.advance(1)
            bank=snapshot(world,saved,f'period{period}_postcommit');decoded=bank[:,list(g.info)].copy();saved[f'decoded_upper_{period}']=decoded
            expected=expected1 if period==1 else expected2
            np.testing.assert_array_equal(decoded,expected)
            healthy_expected=healthy1 if period==1 else healthy2
            difference=decoded!=healthy_expected
            rows.append(dict(period=period,physical_ticks=f.U,decoded_complete_raw_words=decoded.size,
                             different_upper_sites_from_healthy=int(np.count_nonzero(np.any(difference,axis=1))),
                             different_raw_words_from_healthy=int(np.count_nonzero(difference)),
                             matches_intended_G_macrostep=True,metrics=metrics,commit_metrics=commit,seconds=time.perf_counter()-t))
            print(json.dumps(rows[-1]),flush=True)
        device=world.device_bytes
    np.savez_compressed(artifact,**saved)
    result=dict(passed=True,fixture=str(fixture_path),fixture_sha256=sha(fixture_path),upper_sites=63,lower_physical_sites=63*f.Q,
                raw_projected_upper_defect_sites=[31,32],all_105_mutable_fields_maximized=True,upper_window_original_first=first,
                upper_age=fixture['age'],initial_upper_evaluator_instruction=fixture['rom_instruction'],
                explicit_periodic_seam=True,seam_outside_two_step_repair_cone=True,
                complete_rejoin_after_second_macrostep=True,actual_continuous_lower_work_periods=2,
                no_reencoding_between_periods=True,complete_bank_and_controller_snapshots=True,periods=rows,
                explicit_final_device_bytes=device,artifact=str(artifact),artifact_sha256=sha(artifact),seconds=time.perf_counter()-start,
                descriptor_sha256=f.self_description().digest(),ROM_sha256=r.identity()['ROM_sha256'],
                source_sha256={str(Path(x)):sha(x) for x in (__file__,epochs.__file__,image.__file__)},
                scope='Actual encoded upper-layer two-site repair over two continuous lower periods, with a running upper evaluator and complete raw controller comparison. Upper ring63 has an explicit seam outside the repair cone; not a complete Q-cell upper colony/top macrostep, new stochastic lower-fault process, or general amplification theorem.')
    with output.open('x') as out:out.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(output=str(output),seconds=result['seconds'],device_bytes=device)),flush=True)


if __name__=='__main__':main()
