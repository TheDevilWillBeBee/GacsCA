"""Independent raw-state audit of the two-period physical single-bit witness."""
import argparse,hashlib,json,tarfile,time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import repair_b_rule as f,repair_b_projected as r,repair_b_program as p,repair_b_native as native,repair_b_initial as initial
from gacsca.fixed_rule.repair_b_recurrent_prefix_world import World


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def audit(stem,output):
    stem,output=Path(stem),Path(output);assert not output.exists();started=time.monotonic();root=Path(__file__).resolve().parents[2]
    x=json.loads(stem.with_suffix('.json').read_text());assert sha(stem.with_suffix('.npz'))==x['artifact_sha256'] and sha(stem.with_suffix('.tar.gz'))==x['archive_sha256']
    with tarfile.open(stem.with_suffix('.tar.gz')) as archive:
        assert set(archive.getnames())==set(x['source_sha256'])
        for name,digest in x['source_sha256'].items():assert sha(root/name)==digest==hashlib.sha256(archive.extractfile(name).read()).hexdigest(),name
    assert x['rule']==json.loads(json.dumps(r.identity()))
    with np.load(stem.with_suffix('.npz'),allow_pickle=False) as a:saved={k:a[k] for k in a.files}
    g=p.layout();clean=saved['clean_initial'];dirty=saved['fault_initial'];xor=clean^dirty
    assert sum(int(v).bit_count() for v in xor.ravel())==1
    locations=np.argwhere(xor);np.testing.assert_array_equal(locations,[[x['fault']['stored_row'],r.COL['data']]])
    assert int(xor[tuple(locations[0])])==1
    for period in range(2):
        start=saved[f'start_{period}'];np.testing.assert_array_equal(start,dirty if period==0 else saved['final_0'])
        core=start.reshape(2,g.computation_cells+5,len(r.SCHEMA))[:,:g.computation_cells].copy().reshape(-1,len(r.SCHEMA));upper=r.decode_cores(core);raw=tuple(r.lift(c) for c in upper)
        want=f.step_ring(raw);assert want==native.cells_from_array(native.dense_step(native.array_from_cells(raw)))
        described=tuple(f.decode_cell(f.self_description().evaluate(tuple(v for j in range(-5,6) for v in f.encode_cell(raw[(c+j)%2])))) for c in range(2));assert want==described
        expected=tuple(r.project(c) for c in want);np.testing.assert_array_equal(saved[f'decoded_{period}'],r.array_from_cells(expected))
        assert expected[0]==initial.terminal_data(age=period+2)[0] and expected[1].data==1
        old=np.array([f.encode_cell(c) for c in raw],dtype=np.uint64)
        neighbors=np.stack([old[(np.arange(2)+j)%2] for j in range(-5,6)],axis=1).reshape(2,-1)
        assert saved[f'gathers_{period}'].shape==(3,2,11*f.FIELDS)
        for got in saved[f'gathers_{period}']:np.testing.assert_array_equal(got,neighbors)
        upper_words=np.array([f.encode_cell(r.lift(c)) for c in expected],dtype=np.uint64)
        for got in saved[f'holds_{period}']:np.testing.assert_array_equal(got,upper_words)
        final=saved[f'final_{period}'].reshape(2,g.computation_cells+5,len(r.SCHEMA))
        np.testing.assert_array_equal(final[:,np.array(g.info),r.COL['data']],upper_words)
        assert not np.any(final[:,:,[r.COL[n] for n in ('age','head','f1','f2','wf1','wf2','lp_valid','rp_valid')]])
        for frame in saved[f'stored_suffix_{period}']:assert not np.any(frame[:,[r.COL[n] for n in ('f1','f2','wf1','wf2')]])
        with World(start) as world:
            positions=[0,*g.info,*g.hold,g.computation_cells-1,f.Q-5,f.Q-1]
            expected_local={(c,a):r.project(native.local_step(tuple(r.lift(world.cell(*divmod((c*f.Q+a+j)%(2*f.Q),f.Q))) for j in range(-5,6)))) for c in range(2) for a in positions}
            world.run(1)
            for (c,a),cell in expected_local.items():assert world.cell(c,a)==cell
    assert x['physical_ticks']==2*f.U
    result=dict(passed=True,verifier_sha256=sha(__file__),source_files=len(x['source_sha256']),single_physical_bit_verified=True,all_raw_temporal_gathers_checked=True,full_scalar_native_description_agreement=True,exact_period_handoff=True,physical_ticks=2*f.U,incorrect_simulated_Data_after_each_period=[1,1],seconds=time.monotonic()-started,artifact_sha256=x['artifact_sha256'],limitation='negative spatial-repair witness, not an independent replay of the entire long physical trajectory or proof of robustness')
    output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',required=True,type=Path);parser.add_argument('--output',required=True,type=Path);a=parser.parse_args();audit(a.input,a.output)
