"""Independently check every complete physical output in the delayed-wave witness."""
import argparse,hashlib,json,time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import holder_rule as f,holder_projected as r,holder_native as native
from .prove_holder_flag_profile import prove


def audit(stem,output):
    stem,output=Path(stem),Path(output)
    if output.exists():raise FileExistsError('preserve evidence')
    start=time.monotonic();x=json.loads(stem.with_suffix('.json').read_text());root=Path(__file__).resolve().parents[2]
    assert hashlib.sha256(stem.with_suffix('.npz').read_bytes()).hexdigest()==x['artifact_sha256']
    for name,digest in x['source_sha256'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest,name
    assert x['rule']==json.loads(json.dumps(r.identity()));checks=0
    with np.load(stem.with_suffix('.npz'),allow_pickle=False) as data:
        a={key:data[key] for key in data.files}
    delta=np.argwhere(a['clean_0']!=a['damaged_0']);np.testing.assert_array_equal(delta,[[112,r.COL['f1']]])
    assert a['clean_0'][112,r.COL['f1']]==1 and a['damaged_0'][112,r.COL['f1']]==0
    for tick in range(1,9):
        start_position=x['initial_patch_start']+7*tick
        difference=np.argwhere(a[f'clean_{tick}']!=a[f'damaged_{tick}']);np.testing.assert_array_equal(difference,[[-3*tick-start_position,r.COL['f1']]])
        for kind in ('clean','damaged'):
            old=tuple(r.lift(cell) for cell in r.cells_from_array(a[f'{kind}_{tick-1}']));new=r.cells_from_array(a[f'{kind}_{tick}'])
            for i,want in enumerate(new):
                assert r.project(native.local_step(old[i:i+15]))==want,(kind,tick,i);checks+=1
    assert prove()['passed'];front=x['initial_front'];join=(front+3)//3
    assert join==x['certified_join_by_ticks'] and x['initial_age']+join<98*f.Q
    assert max(0,front-3*join)==max(0,front+1-3*join)==0
    result=dict(passed=True,full_native_output_checks=checks,single_bit_fault_confirmed=True,moving_Flag1_mismatch_through_eight_ticks=True,all_procedure_fields_equal=True,certified_join_by_ticks=join,source_files=len(x['source_sha256']),seconds=time.monotonic()-start,limitation='one specified forced-wave bit fault; not arbitrary fault recovery or a noise-rate measurement')
    output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();audit(a.input,a.output)
