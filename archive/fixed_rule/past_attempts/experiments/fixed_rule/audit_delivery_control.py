"""Raw-state/source audit and deterministic replay of mail-free controller suffix.

This validates the controller quotient only. Physical flag completion is a
separate obligation, so this record does not certify a complete macrostep.
"""
import argparse
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import random
import tarfile
import time
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import delivery_rule as f,delivery_projected as r,delivery_program as p,delivery_native as native
from gacsca.fixed_rule.delivery_control_world import World,library
from gacsca.fixed_rule.wordcode import Program


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def audit(stem,output):
    stem,output=Path(stem),Path(output)
    if output.exists():raise FileExistsError('preserve prior evidence')
    started=time.monotonic();root=Path(__file__).resolve().parents[2];x=json.loads(stem.with_suffix('.json').read_text())
    assert sha(stem.with_suffix('.npz'))==x['artifact_sha256'] and sha(stem.with_suffix('.tar.gz'))==x['archive_sha256']
    with tarfile.open(stem.with_suffix('.tar.gz')) as archive:
        assert set(archive.getnames())==set(x['source_sha256'])
        for name,digest in x['source_sha256'].items():assert sha(root/name)==digest==hashlib.sha256(archive.extractfile(name).read()).hexdigest(),name
    assert x['rule']==json.loads(json.dumps(r.identity()));assert sha(library()._name)==x['binary_sha256']
    prefix=Path(x['input_prefix']);assert sha(prefix.with_suffix('.json'))==x['input_json_sha256']
    assert sha(prefix.with_suffix('.npz'))==x['input_artifact_sha256']
    with np.load(prefix.with_suffix('.npz'),allow_pickle=False) as a:initial=a['stored_final'];old=a['initial_lifted'];top=r.cells_from_array(a['initial_top'])
    with np.load(stem.with_suffix('.npz'),allow_pickle=False) as a:saved={name:a[name] for name in a.files}
    full=f.step_ring(tuple(r.lift(c) for c in top));dense=native.cells_from_array(native.dense_step(native.array_from_cells(tuple(r.lift(c) for c in top))))
    assert full==dense
    described=tuple(f.decode_cell(f.self_description().evaluate(tuple(word for j in range(-5,6) for word in old[(i+j)%len(top)]))) for i in range(len(top)))
    assert full==described
    expected=tuple(r.project(c) for c in full);raw=np.array([f.encode_cell(r.lift(c)) for c in expected],dtype=np.uint64)
    np.testing.assert_array_equal(saved['decoded'],r.array_from_cells(expected));np.testing.assert_array_equal(saved['lifted'],raw)
    neighbors=np.stack([old[(np.arange(len(top))+j)%len(top)] for j in range(-5,6)],axis=1).reshape(len(top),-1)
    assert saved['votes'].shape==(1,len(top),11*f.FIELDS)
    for row in saved['votes']:np.testing.assert_array_equal(row,neighbors)
    assert saved['holds'].shape==(3,len(top),f.FIELDS)
    for row in saved['holds']:np.testing.assert_array_equal(row,raw)
    g=p.layout();checks=0;rng=random.Random(953);mail=[name for name,_ in r.SCHEMA if name.startswith(('lp_','rp_'))];flags=('f1','f2','wf1','wf2')
    with World(initial) as w:
        for age in (104*f.Q,112*f.Q,120*f.Q,f.U-1,f.U):
            with patch.object(Program,'evaluate',side_effect=AssertionError('host evaluator')),patch.object(f,'local_step',side_effect=AssertionError('host upper transition')):w.run(age-(96*f.Q-1)-w.time)
            np.testing.assert_array_equal(w.stored,saved['age'+str(age)])
            a=w.stored.reshape(len(top),g.computation_cells+5,len(r.SCHEMA))
            assert not np.any(a[:,:,[r.COL[n] for n in (*flags,*mail)]])
            np.testing.assert_array_equal(a[:,np.array(g.info),r.COL['data']],raw if age==f.U else old)
            # Independently check the factorization at actual saved controller
            # states, with arbitrary legal physical flags and coherent signals.
            for c in range(len(top)):
                for address in (0,3,g.info[0],g.hold[0],g.computation_cells+50,f.Q-3):
                    cells=tuple(r.lift(w.cell(*divmod((c*f.Q+address+j)%(len(top)*f.Q),f.Q))) for j in range(-5,6))
                    dirty=tuple(replace(cell,**{name:rng.randrange(2) for name in flags}) for cell in cells)
                    actual=native.local_step(dirty);clean=native.local_step(cells)
                    for name,_ in f.SCHEMA:
                        if name not in (*flags,*mail):assert getattr(actual,name)==getattr(clean,name)
                    assert all(getattr(actual,name)==0 for name in mail)
                    checks+=1
        assert w.decode()==expected
    metrics=x['metrics'];assert metrics['physical_ticks']==32*f.Q+1==sum(metrics[n] for n in ('literal_core_ticks','quiet_ticks_skipped','scan_ticks_skipped'))
    result=dict(passed=True,source_files=len(x['source_sha256']),physical_ticks=metrics['physical_ticks'],full_native_scalar_description_agree=True,saved_controller_frames_replayed=5,raw_history_vote_and_hold_checked=True,active_simulated_write=int(raw[11,f.COL['data']]),factorization_native_neighborhood_pairs=checks,seconds=time.monotonic()-started,artifact_sha256=x['artifact_sha256'],limitation='controller quotient through commit only; actual physical flags after 98Q remain uncomputed, so no complete macrostep claim')
    output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();audit(args.input,args.output)
