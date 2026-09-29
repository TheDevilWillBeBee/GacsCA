"""Independent raw-state and archived-source audit of regenerative macrosteps."""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile
import numpy as np
from gacsca.fixed_rule import regenerated as rule,regenerative as full,regenerative_block as block
from gacsca.fixed_rule.regenerated_native import library,dense_step


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def audit(stem,output):
    stem,output=Path(stem),Path(output)
    if output.exists():
        raise FileExistsError('existing audit evidence must be preserved')
    manifest=json.loads(stem.with_suffix('.json').read_text())
    assert sha(stem.with_suffix('.npz'))==manifest['artifact_sha256']
    assert sha(stem.with_suffix('.tar.gz'))==manifest['source_archive_sha256']
    root=Path(__file__).resolve().parents[2]
    hashes=manifest['source_sha256']
    with tarfile.open(stem.with_suffix('.tar.gz'),'r:gz') as archive:
        assert set(archive.getnames())==set(hashes)
        for name,digest in hashes.items():
            assert sha(root/name)==digest,('live source changed',name)
            assert hashlib.sha256(archive.extractfile(name).read()).hexdigest()==digest
    with np.load(stem.with_suffix('.npz'),allow_pickle=False) as artifact:
        frames,lifted=artifact['frames'],artifact['lifted_frames']
        physical,rom=artifact['physical_final'],artifact['rom']
    expected_shape=(len(manifest['periods'])+1,4,rule.WIDTH)
    assert frames.shape==expected_shape
    assert lifted.shape==expected_shape[:2]+(full.WIDTH,)
    assert np.all((frames==0)|(frames==1)) and np.all((lifted==0)|(lifted==1))
    np.testing.assert_array_equal(rom,rule.rom())
    # Normalize tuples to JSON lists to compare against the persisted manifest.
    assert manifest['fixed_rule']==json.loads(json.dumps(rule.identity()))
    lib=library()
    assert sha(lib._name)==manifest['compiled_binary_sha256']
    reference=tuple(rule.decode_cell(row.tolist()) for row in frames[0])
    circuit=full.self_description()
    for period in range(len(frames)):
        actual=tuple(rule.decode_cell(row.tolist()) for row in frames[period])
        assert actual==reference,('projected mismatch',period)
        expanded=tuple(full.decode_cell(row.tolist()) for row in lifted[period])
        assert expanded==tuple(rule.lift(cell) for cell in actual),('lift mismatch',period)
        if period<len(frames)-1:
            scalar=rule.step_ring(actual)
            native=rule.cells_from_array(dense_step(rule.array_from_cells(actual),lib))
            full_next=full.step_ring(expanded)
            described=[]
            for i in range(len(expanded)):
                triple=(expanded[i-1],expanded[i],expanded[(i+1)%len(expanded)])
                inputs=tuple(bit for cell in triple for bit in full.encode_cell(cell))
                described.append(full.decode_cell(circuit.evaluate(inputs)))
            assert scalar==native
            assert full_next==tuple(described)==tuple(rule.lift(cell) for cell in scalar)
            reference=scalar
    assert rule.decode(physical)==reference
    assert rule.check_boundary(physical)
    for log in manifest['periods']:
        assert log['physical_ticks']==block.layout().period_ticks
        assert log['raw_bit_mismatches']==log['lifted_raw_bit_mismatches']==0
        assert log['admissible_boundary'] is True
    assert manifest['total_ticks']==len(manifest['periods'])*block.layout().period_ticks
    values=[rule.decode_cell(row[1].tolist()).bit for row in frames]
    assert [i for i in range(1,len(values)) if values[i]!=values[i-1]]==[2,8]
    result=dict(source_files_verified=len(hashes),macrosteps=len(frames)-1,
                projected_postinitial_bits=int(frames[1:].size),
                lifted_postinitial_bits=int(lifted[1:].size),
                scalar_native_description_agree=True,final_decode_and_boundary=True,
                recorded_memory_writes=[2,8],total_literal_ticks=manifest['total_ticks'],
                artifact_sha256=manifest['artifact_sha256'],
                source_archive_sha256=manifest['source_archive_sha256'],
                scope='complete computing substrate with local regeneration; not colony maintenance or repair')
    output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    audit(args.input,args.output)
