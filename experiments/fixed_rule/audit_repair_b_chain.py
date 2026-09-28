"""Join independently audited candidate-B periods through exact physical state."""
import argparse,hashlib,json,time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import repair_b_rule as f,repair_b_projected as r,repair_b_native as native


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def audit(output):
    output=Path(output)
    if output.exists():raise FileExistsError('preserve evidence')
    base=Path('figs/fixed_rule');started=time.monotonic()
    names=('repair_b_execution_v1','repair_b_macrostep_v1','repair_b_recurrent_execution_v2','repair_b_recurrent_macrostep_v1')
    checks=('repair_b_execution_audit_v1','repair_b_macrostep_audit_v2','repair_b_recurrent_audit_v1','repair_b_recurrent_macrostep_audit_v1')
    metadata=[];arrays=[];artifacts={}
    for name,check in zip(names,checks):
        stem=base/name;x=json.loads(stem.with_suffix('.json').read_text());a=json.loads((base/(check+'.json')).read_text())
        assert a['passed'] and a['artifact_sha256']==x['artifact_sha256']==sha(stem.with_suffix('.npz'))
        assert x['rule']==json.loads(json.dumps(r.identity()))
        for path in (stem.with_suffix('.json'),stem.with_suffix('.npz'),base/(check+'.json')):artifacts[str(path)]=sha(path)
        metadata.append(x)
        with np.load(stem.with_suffix('.npz'),allow_pickle=False) as data:arrays.append({k:data[k] for k in ('initial_top','decoded','stored_initial','stored_final') if k in data.files})
    np.testing.assert_array_equal(arrays[2]['stored_initial'],arrays[1]['stored_final'])
    np.testing.assert_array_equal(arrays[2]['initial_top'],arrays[1]['decoded'])
    assert metadata[2]['previous_artifact_sha256']==metadata[1]['artifact_sha256']
    assert metadata[1]['input_artifact_sha256']==metadata[0]['artifact_sha256']
    assert metadata[3]['input_artifact_sha256']==metadata[2]['artifact_sha256']
    top=r.cells_from_array(arrays[0]['initial_top']);changes=[]
    for index in (1,3):
        old=tuple(r.lift(c) for c in top);full=f.step_ring(old)
        assert full==native.cells_from_array(native.dense_step(native.array_from_cells(old)))
        described=tuple(f.decode_cell(f.self_description().evaluate(tuple(word for j in range(-5,6) for word in f.encode_cell(old[(i+j)%len(old)])))) for i in range(len(old)))
        assert full==described
        expected=tuple(r.project(c) for c in full);actual=r.cells_from_array(arrays[index]['decoded']);assert actual==expected
        changed=[name for name,*_ in r.SCHEMA if any(getattr(a,name)!=getattr(b,name) for a,b in zip(top,actual))]
        assert any(name in changed for name in ('head','pc','phase','rd','value')),'clock-only dynamics insufficient'
        changes.append(changed);top=actual
        assert metadata[index]['complete_physical_macrostep_ticks']==f.U
        final=arrays[index]['stored_final'];assert np.all(final[:,r.COL['age']]==0)
        assert not np.any(final[:,[r.COL[n] for n in ('f1','f2','wf1','wf2','head')]])
    assert int(arrays[0]['initial_top'][11,r.COL['data']])==0
    assert int(arrays[1]['decoded'][11,r.COL['data']])==0x123456789ABCDEF0
    result=dict(passed=True,verifier_sha256=sha(__file__),complete_successive_macrosteps=2,physical_ticks=2*f.U,exact_full_stored_state_handoff=True,active_controller_changed_both_periods=True,changed_raw_fields=changes,rule=r.identity(),input_sha256=artifacts,seconds=time.monotonic()-started,limitation='two noiseless canonical one-link macrosteps of explicit candidate B; organized termination, full spatial controller repair, deeper dynamics and measured noise robustness remain unproved')
    output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path);a=p.parse_args();audit(a.output)
