"""Independent raw-array/source audit of physical computed-flag delivery."""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile
import numpy as np
from gacsca.fixed_rule import holder_rule as f,holder_projected as r,holder_program as p,holder_native as native,holder_quotient as q
from gacsca.fixed_rule.holder_recurrent_prefix_world import library


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def audit(stem,output):
    stem,output=Path(stem),Path(output)
    if output.exists():raise FileExistsError('preserve prior audit')
    root=Path(__file__).resolve().parents[2];x=json.loads(stem.with_suffix('.json').read_text())
    assert sha(stem.with_suffix('.npz'))==x['artifact_sha256'] and sha(stem.with_suffix('.tar.gz'))==x['archive_sha256']
    with tarfile.open(stem.with_suffix('.tar.gz')) as archive:
        assert set(archive.getnames())==set(x['source_sha256'])
        for name,digest in x['source_sha256'].items():
            assert sha(root/name)==digest,name
            assert hashlib.sha256(archive.extractfile(name).read()).hexdigest()==digest,name
    assert x['rule']==json.loads(json.dumps(r.identity()))
    assert sha(library()._name)==x['binary_sha256']
    assert x['timing']==p.layout().timing_certificate() and x['timing']['fits']
    with np.load(stem.with_suffix('.npz'),allow_pickle=False) as data:
        a={name:data[name] for name in data.files}
    previous=Path(x['previous']);assert sha(previous.with_suffix('.json'))==x['previous_json_sha256']
    prior=json.loads(previous.with_suffix('.json').read_text());assert sha(previous.with_suffix('.npz'))==prior['artifact_sha256']
    with np.load(previous.with_suffix('.npz'),allow_pickle=False) as data:np.testing.assert_array_equal(a['logical_initial'],data['logical_final']);np.testing.assert_array_equal(a['initial_top'],data['decoded'])
    top=r.cells_from_array(a['initial_top']);old=tuple(r.lift(c) for c in top);n=len(top);g=p.layout();assert n==15
    np.testing.assert_array_equal(a['initial_lifted'],native.array_from_cells(old))
    full=f.step_ring(old)
    assert full==native.step_ring(old)
    described=tuple(f.decode_cell(f.self_description().evaluate(tuple(word for j in range(-7,8) for word in f.encode_cell(old[(i+j)%n])))) for i in range(n))
    assert full==described
    lifted=tuple(r.lift(r.project(c)) for c in full);expected=native.array_from_cells(lifted)
    np.testing.assert_array_equal(a['expected_hold'],expected)
    assert int(expected[7,f.COL['s2_data']])==0x123456789ABCDEF0
    assert np.all(expected[:,f.COL['f1']]==1) and not np.any(expected[:,f.COL['f2']])
    for frame in a['repair_frames']:np.testing.assert_array_equal(frame,a['initial_lifted'])
    assert a['hold_frames'].shape==(5,n,f.FIELDS)
    for frame in a['hold_frames']:np.testing.assert_array_equal(frame,expected)
    neighbors=np.stack([a['initial_lifted'][(np.arange(n)+j)%n] for j in range(-7,8)],axis=1).reshape(n,-1)
    assert a['history_frames'].shape==(6,n,15*f.FIELDS)
    for frame in a['history_frames']:np.testing.assert_array_equal(frame,neighbors)
    for frame in a['vote_frames']:np.testing.assert_array_equal(frame,neighbors)
    np.testing.assert_array_equal(a['history_keys'],[(16*f.Q,0),(48*f.Q,0),(48*f.Q,1),(72*f.Q,0),(72*f.Q,1),(72*f.Q,2)])
    payload=np.repeat(expected[:,[f.COL['f2'],f.COL['f1']]],5,axis=1)
    assert a['buffer_frames'].shape==(5,n,10)
    for frame in a['buffer_frames']:np.testing.assert_array_equal(frame,payload)
    signals=np.concatenate((expected[:,f.COL['f2'],None]*np.array([16,8,4,2,1]),expected[:,f.COL['f1'],None]*np.array([16,8,4,2,1])),axis=1)
    assert a['signal_frames'].shape==(5,n,10)
    for frame in a['signal_frames'][:2]:np.testing.assert_array_equal(frame,a['carried_signal'])
    for frame in a['signal_frames'][2:]:np.testing.assert_array_equal(frame,signals)
    stored=a['logical_stored_final'].reshape(n,g.computation_cells+5,len(q.SCHEMA));assert np.all(stored[:,:,q.COL['age']]==96*f.Q-1)
    np.testing.assert_array_equal(stored[:,np.array(g.info),q.COL['data']],a['initial_lifted'])
    np.testing.assert_array_equal(stored[:,np.array(g.hold),q.COL['data']],expected)
    index=np.array([*range(1,6),*range(g.computation_cells,g.computation_cells+5)])
    np.testing.assert_array_equal(stored[:,index,q.COL['data']],payload)
    np.testing.assert_array_equal(stored[:,index,q.COL['signal']],signals)
    flags=[q.COL[name] for name in ('f1','f2','wf1','wf2')];assert np.all(stored[:,:,flags]==0)
    assert not np.any(stored[:,:,q.COL['head']])
    for name in ('lp_valid','rp_valid'):assert not np.any(stored[:,:,q.COL[name]])
    addresses=np.array([*range(g.computation_cells),*range(f.Q-5,f.Q)])
    np.testing.assert_array_equal(stored[:,:,q.COL['address']],np.broadcast_to(addresses,(n,len(addresses))))
    np.testing.assert_array_equal(a['rom'],p.base_rom())
    assert all(probe['pending']==0 for probe in x['probes'])
    metrics=x['metrics'];assert sum(metrics[k] for k in ('literal_core_ticks','quiet_ticks_skipped','scan_ticks_skipped'))==metrics['physical_ticks']==96*f.Q-1
    result=dict(source_files=len(x['source_sha256']),passed=True,complete_scalar_native_description_agreement=True,full_154_word_redundant_controller=True,physical_radius=7,coherent_state_representation=True,temporal_vote_executed_by_local_NANDs=True,
                all_raw_fields_gathered_and_evaluated=True,computed_upper_flags_delivered_to_all_ten_buffers=True,
                signals_captured_and_held_until_before_Wf=True,simulated_active_controller=True,exact_previous_physical_handoff=True,
                represented_cells=n,physical_ticks=metrics['physical_ticks'],artifact_sha256=x['artifact_sha256'],archive_sha256=x['archive_sha256'],
                limitation='stops before physical Wf/flag waves and before stage-five recomputation/commit; not a full new-rule macrostep or deeper dynamic execution')
    output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();audit(args.input,args.output)
