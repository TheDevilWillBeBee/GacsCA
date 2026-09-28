"""Independent source/raw-array audit of resident GPU self-description capture."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import small_holder_rule as f,small_holder_projected as r,small_holder_quotient as q,small_holder_program as p,small_holder_native as native
from gacsca.fixed_rule import small_holder_resident_prefix as gpu,small_holder_prefix_description


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--input',required=True);parser.add_argument('--output',required=True);args=parser.parse_args();stem=Path(args.input);out=Path(args.output)
    if out.exists():raise FileExistsError('preserve prior audit')
    manifest=json.loads(stem.with_suffix('.json').read_text())
    assert manifest['passed'] and manifest['physical_rule_description']==f.self_description().digest()
    for path,wanted in manifest['source_sha256'].items():assert digest(path)==wanted,path
    assert digest(gpu.library()._name)==manifest['binary_sha256']
    with np.load(stem.with_suffix('.npz'),allow_pickle=False) as archive:data={key:archive[key] for key in archive.files}
    top=r.cells_from_array(data['initial_top']);raw=tuple(r.lift(x) for x in top);n=len(top);g=p.layout()
    scalar=f.step_ring(raw);assert scalar==native.step_ring(raw)
    described=tuple(f.decode_cell(f.self_description().evaluate(tuple(word for j in f.NEIGHBORHOOD for word in f.encode_cell(raw[(i+j)%n])))) for i in range(n))
    assert described==scalar
    expected=native.array_from_cells(tuple(r.lift(r.project(x)) for x in scalar))
    np.testing.assert_array_equal(data['initial_lifted'],native.array_from_cells(raw))
    np.testing.assert_array_equal(data['expected_hold'],expected);np.testing.assert_array_equal(data['actual_hold'],expected)
    assert int(expected[7,f.COL['s2_data']])==0x123456789ABCDEF0
    neighborhoods=np.stack([data['initial_lifted'][(np.arange(n)+j)%n] for j in f.NEIGHBORHOOD],axis=1).reshape(n,-1)
    assert data['histories'].shape==(3,n,len(f.NEIGHBORHOOD)*f.FIELDS)
    for history in data['histories']:np.testing.assert_array_equal(history,neighborhoods)
    stored=data['final_stored'].reshape(n,g.computation_cells+5,len(q.SCHEMA))
    np.testing.assert_array_equal(stored[:,np.array(g.info),q.COL['data']],data['initial_lifted'])
    np.testing.assert_array_equal(stored[:,np.array(g.hold),q.COL['data']],expected)
    np.testing.assert_array_equal(stored[:,np.array(g.votes),q.COL['data']],neighborhoods)
    np.testing.assert_array_equal(data['buffers'],np.repeat(expected[:,[f.COL['f2'],f.COL['f1']]],5,axis=1))
    signal_expected=np.concatenate((expected[:,f.COL['f2'],None]*np.array([16,8,4,2,1]),expected[:,f.COL['f1'],None]*np.array([16,8,4,2,1])),axis=1)
    indices=np.array([*range(1,6),*range(g.computation_cells,g.computation_cells+5)])
    np.testing.assert_array_equal(stored[:,indices,q.COL['signal']],signal_expected)
    assert not np.any(stored[:,:,[q.COL[x] for x in ('f1','f2','wf1','wf2','head','lp_valid','rp_valid')]])
    assert np.all(stored[:,:,q.COL['age']]==f.CAPTURE_AGE)
    stream=hashlib.sha256()
    for col in range(n):
        all_rows=np.zeros((f.Q,len(q.SCHEMA)),dtype=np.uint64);all_rows[:,q.COL['address']]=np.arange(f.Q);all_rows[:,q.COL['age']]=f.CAPTURE_AGE
        all_rows[:g.computation_cells]=stored[col,:g.computation_cells];all_rows[-5:]=stored[col,-5:]
        stream.update(all_rows.tobytes())
    assert stream.hexdigest()==manifest['complete_coherent_sha256']
    metrics=manifest['metrics'];assert metrics['physical_ticks']==f.CAPTURE_AGE==metrics['literal_ticks']+metrics['transport_or_quiet_ticks']
    result=dict(passed=True,complete_scalar_native_description_agreement=True,all_154_raw_hold_fields_match=True,all_three_gathers_and_final_vote_match=True,computed_flags_and_captured_signals_match=True,all_coherent_physical_cells_reconstructed=n*f.Q,complete_state_stream_hash_matches=True,active_simulated_write=int(expected[7,f.COL['s2_data']]),physical_ticks=f.CAPTURE_AGE,description_sha256=f.self_description().digest(),prefix_description_sha256=small_holder_prefix_description.build().digest(),rom_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest(),manifest_sha256=digest(stem.with_suffix('.json')),artifact_sha256=digest(stem.with_suffix('.npz')),source_files_checked=len(manifest['source_sha256']),limitation='GPU self-description computation and capture, not Wf/suffix/recomputation/commit or nested dynamics')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
