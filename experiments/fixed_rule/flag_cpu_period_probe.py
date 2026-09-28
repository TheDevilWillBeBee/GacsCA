"""Test complete-ring short recurrence after the bounded CUDA flag probe.

An exact periodic orbit, if found, can be continued through the remaining
unforced interval without assuming a guessed spatial wave profile.
"""
import argparse,hashlib,json,time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import delivery_rule as f
from gacsca.fixed_rule.flag_cuda import advance


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def execute(stem,source):
    stem,source=Path(stem),Path(source)
    if stem.with_suffix('.json').exists():raise FileExistsError('preserve evidence')
    x=json.loads(source.with_suffix('.json').read_text());assert sha(source.with_suffix('.npz'))==x['artifact_sha256']
    with np.load(source.with_suffix('.npz'),allow_pickle=False) as a:initial=a['final_dense'];expected_one=a['one_step']
    assert not np.any(initial[:,0]);state=initial;rows=[];found=None;started=time.monotonic()
    for ticks in range(1,65):
        state=advance(state,1,age=98*f.Q+x['ticks_after_cutoff']+ticks-1,reference=True)
        if ticks==1:np.testing.assert_array_equal(state,expected_one)
        equal=np.array_equal(state,initial);rows.append(dict(ticks=ticks,state_sha256=hashlib.sha256(state.tobytes()).hexdigest(),equal_to_start=equal))
        if equal:found=ticks;break
    result=dict(scope=__doc__,period=found,checked_ticks=len(rows),rows=rows,seconds=time.monotonic()-started,source=str(source),input_sha256=x['artifact_sha256'],input_json_sha256=sha(source.with_suffix('.json')),verifier_sha256=sha(__file__),limitation='only recurrence of this entire saved ring within 64 steps is tested; failure is not proof of aperiodicity')
    if found:
        remainder=(f.U-98*f.Q-x['ticks_after_cutoff'])%found
        final=advance(initial,remainder,age=98*f.Q+x['ticks_after_cutoff'],reference=True)
        np.savez_compressed(stem.with_suffix('.npz'),flags_at_U=final,period_start=initial)
        result.update(certified_ticks_to_U=f.U-98*f.Q-x['ticks_after_cutoff'],artifact_sha256=sha(stem.with_suffix('.npz')))
    stem.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='rows'}),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();execute(a.output,a.input)
