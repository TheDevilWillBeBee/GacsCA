"""Continue all retained dense-noise failures through a colony-length interval."""
import json
from pathlib import Path
import time
import numpy as np
from gacsca.fixed_rule import compact16_holder_canonical_gpu as gpu
from gacsca.fixed_rule import compact16_holder_literal_cone as cone
from gacsca.fixed_rule import compact16_holder_rule as f
from experiments.fixed_rule.validate_compact16_holder_endpoint import guard
from experiments.fixed_rule.audit_compact16_holder_dense_noise import restore
from experiments.fixed_rule.diagnose_compact16_holder_dense_noise import heads
from experiments.fixed_rule.run_compact16_holder_streamed_depth2 import sha

CHECKPOINTS=(1,512,2048,8192,16383,16384)


def main():
    output=Path('figs/fixed_rule/compact16_holder_canonical_noise_v1.json');artifact=output.with_suffix('.npz')
    if output.exists() or artifact.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();prior_path=Path('figs/fixed_rule/compact16_holder_dense_noise_v1.json');prior=json.loads(prior_path.read_text())
    assert prior['passed'] and sha(prior['artifact'])==prior['artifact_sha256']
    saved={};healthy={};trials=[]
    with np.load(prior['artifact'],allow_pickle=False) as z:
        base=z['healthy_512'].copy();saved['healthy_0']=base
        with gpu.World(base) as world:
            device_bytes=world.device_bytes;previous=0
            for tick in CHECKPOINTS:
                with guard():world.run(tick-previous)
                raw=world.read();saved[f'healthy_{tick}']=raw;healthy[tick]=raw;previous=tick
                print(json.dumps(dict(case='healthy',tick=tick)),flush=True)
        for case in range(8):
            raw=restore(z,case,512);first=cone.step(raw);previous=0;trace=[];before=None
            with gpu.World(raw) as world:
                assert world.device_bytes==device_bytes
                for tick in CHECKPOINTS:
                    t=time.perf_counter()
                    with guard():world.run(tick-previous)
                    actual=world.read();seconds=time.perf_counter()-t
                    if tick==1:np.testing.assert_array_equal(actual,first)
                    if tick==16383:before=actual.copy()
                    if tick==16384:np.testing.assert_array_equal(actual,cone.step(before))
                    different=actual!=healthy[tick];indices=np.flatnonzero(different.ravel()).astype(np.uint64)
                    saved[f'case{case}_t{tick}_indices']=indices;saved[f'case{case}_t{tick}_values']=actual.ravel()[indices]
                    fields={name:int(np.count_nonzero(different[:,k])) for k,(name,_) in enumerate(f.SCHEMA) if np.any(different[:,k])}
                    row=dict(additional_ticks=tick,total_quiet_ticks=520+tick,different_sites=int(np.count_nonzero(np.any(different,axis=1))),
                             different_raw_words=len(indices),different_fields=fields,actual_primary_heads=heads(actual),seconds=seconds)
                    trace.append(row);previous=tick
                    print(json.dumps(dict(case=case,**{k:v for k,v in row.items() if k!='different_fields'})),flush=True)
            trials.append(dict(case=case,trace=trace))
    np.savez_compressed(artifact,**saved)
    result=dict(passed=True,reference=str(prior_path),reference_sha256=sha(prior_path),
                descriptor_sha256=f.self_description().digest(),all_eight_failures_retained=True,
                every_physical_tick_executed=True,checkpoints=list(CHECKPOINTS),trials=trials,
                complete_site_transitions=9*f.Q*16384,explicit_peak_device_bytes=device_bytes,
                artifact=str(artifact),artifact_sha256=sha(artifact),seconds=time.perf_counter()-start,
                source_sha256={str(Path(path)):sha(path) for path in (__file__,gpu.__file__,Path(gpu.__file__).with_suffix('.cu'))},
                scope='All eight saved high-rate failures continued16384ticks with exact canonical-geometry factorization; no omitted physical ticks or continuing faults. No full-period or cross-level stochastic claim.')
    with output.open('x') as out:out.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(output=str(output),seconds=result['seconds'])),flush=True)


if __name__=='__main__':main()
