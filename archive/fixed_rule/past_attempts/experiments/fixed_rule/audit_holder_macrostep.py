"""Independent immutable-source, raw-state and local-transition macrostep audit."""
import argparse,hashlib,json,tarfile,time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import holder_rule as f,holder_projected as r,holder_program as p,holder_quotient as q,holder_native as native,holder_initial as initial,holder_flag_profile as profile
from gacsca.fixed_rule.holder_control_world import library
from .prove_holder_flag_profile import prove


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def audit(stem,output):
    stem,output=Path(stem),Path(output)
    if output.exists():raise FileExistsError('preserve evidence')
    start=time.monotonic();root=Path(__file__).resolve().parents[2];x=json.loads(stem.with_suffix('.json').read_text());prefix=Path(x['prefix'])
    assert sha(stem.with_suffix('.npz'))==x['artifact_sha256'] and sha(stem.with_suffix('.tar.gz'))==x['archive_sha256']
    assert sha(prefix.with_suffix('.json'))==x['prefix_json_sha256']
    previous=json.loads(prefix.with_suffix('.json').read_text());assert sha(prefix.with_suffix('.npz'))==previous['artifact_sha256']
    for name,digest in previous['source_sha256'].items():assert sha(root/name)==digest,name
    with tarfile.open(stem.with_suffix('.tar.gz')) as archive:
        assert set(archive.getnames())==set(x['source_sha256'])
        for name,digest in x['source_sha256'].items():
            assert sha(root/name)==digest,name
            assert hashlib.sha256(archive.extractfile(name).read()).hexdigest()==digest,name
    assert x['rule']==json.loads(json.dumps(r.identity())) and sha(library()._name)==x['binary_sha256']
    with np.load(stem.with_suffix('.npz'),allow_pickle=False) as data:a={name:data[name] for name in data.files}
    with np.load(prefix.with_suffix('.npz'),allow_pickle=False) as data:np.testing.assert_array_equal(a['logical_initial'],data['logical_stored_final'])
    proof=prove();assert proof['passed']
    old=tuple(r.lift(cell) for cell in r.cells_from_array(a['initial_top']));full=f.step_ring(old);assert full==native.step_ring(old)
    assert full==tuple(f.decode_cell(f.self_description().evaluate(tuple(word for j in range(-7,8) for word in f.encode_cell(old[(i+j)%len(old)])))) for i in range(len(old)))
    expected=native.array_from_cells(tuple(r.lift(r.project(cell)) for cell in full));np.testing.assert_array_equal(a['expected'],expected)
    np.testing.assert_array_equal(a['decoded'],r.array_from_cells(tuple(r.project(cell) for cell in full)))
    assert a['sample_inputs'].shape==(x['complete_native_checks'],15,f.FIELDS) and a['sample_outputs'].shape==(x['complete_native_checks'],f.FIELDS)
    for raw,want in zip(a['sample_inputs'],a['sample_outputs']):
        cells=native.cells_from_array(raw);actual=r.lift(r.project(native.local_step(cells)))
        np.testing.assert_array_equal(f.encode_cell(actual),want)
    g=p.layout();n=len(old);final=a['logical_final'].reshape(n,g.computation_cells+5,len(q.SCHEMA))
    addresses=np.array([*range(g.computation_cells),*range(f.Q-5,f.Q)],dtype=np.uint64)
    np.testing.assert_array_equal(final[:,:,q.COL['address']],np.broadcast_to(addresses,final.shape[:2]))
    assert not np.any(final[:,:,q.COL['age']])
    assert not np.any(final[:,:,[q.COL[name] for name in ('head','f1','f2','wf1','wf2','lp_valid','rp_valid')]])
    np.testing.assert_array_equal(final[:,g.info,q.COL['data']],expected);np.testing.assert_array_equal(final[:,g.hold,q.COL['data']],expected)
    signals=np.zeros(final.shape[:2],dtype=np.uint64);signals[:,-5:]=[16,8,4,2,1];np.testing.assert_array_equal(final[:,:,q.COL['signal']],signals)
    # The complete physical backups at commit are determined by adjacent records,
    # including core/gap/colony seams. No nonexistent padding copy is omitted.
    def logical(pos):
        colony,address=divmod(pos%(n*f.Q),f.Q)
        if address<g.computation_cells:return q.decode_cell(final[colony,address].tolist())
        if address>=f.Q-5:return q.decode_cell(final[colony,g.computation_cells+address-f.Q+5].tolist())
        return q.Cell(address=address)
    for colony in range(n):
        for address in (*range(7),*range(g.computation_cells-3,g.computation_cells+3),*range(f.Q-7,f.Q),*g.info):
            cell=initial.coherent_cell(logical,colony*f.Q+address)
            for d in f.OFFSETS:
                expected_logical=logical(colony*f.Q+address+d)
                for name,_ in f.PROCEDURE:assert getattr(cell,f's{d+2}_{name}')==getattr(expected_logical,name)
    metrics=x['metrics'];assert sum(metrics[k] for k in ('literal_core_ticks','quiet_ticks_skipped','scan_ticks_skipped'))==metrics['physical_ticks']==f.U-profile.START
    assert previous['metrics']['physical_ticks']+metrics['physical_ticks']==x['total_macrostep_ticks']==f.U
    result=dict(passed=True,source_files=len(x['source_sha256']),complete_macrostep_ticks=f.U,physical_sites=n*f.Q,stored_logical_records=n*(g.computation_cells+5),full_physical_width=r.WIDTH,all_raw_154_fields_match=True,active_simulated_WRITE=True,actual_prefix_handoff=True,flag_profile_symbolically_verified=True,local_transition_samples=x['complete_native_checks'],seconds=time.monotonic()-start,artifact_sha256=x['artifact_sha256'],scope='one complete one-link macrostep; coherent physical backups reconstructed, no depth-two or arbitrary-noise claim')
    output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',required=True,type=Path);parser.add_argument('--output',required=True,type=Path);args=parser.parse_args();audit(args.input,args.output)
