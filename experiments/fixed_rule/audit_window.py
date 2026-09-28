"""Audit the complete raw trace and fixed-rule identities of a window run."""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile
import numpy as np
from gacsca.fixed_rule import windowed as r,window_rule as f,window_program as b
from gacsca.fixed_rule.windowed_native import dense_step
from gacsca.fixed_rule.window_world import library


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def audit(stem,output):
    stem,output=Path(stem),Path(output)
    if output.exists():raise FileExistsError('preserve existing audit')
    x=json.loads(stem.with_suffix('.json').read_text());root=Path(__file__).resolve().parents[2]
    assert sha(stem.with_suffix('.npz'))==x['artifact_sha256']
    assert sha(stem.with_suffix('.tar.gz'))==x['source_archive_sha256']
    with tarfile.open(stem.with_suffix('.tar.gz')) as archive:
        assert set(archive.getnames())==set(x['source_sha256'])
        for name,digest in x['source_sha256'].items():
            assert sha(root/name)==digest,name
            assert hashlib.sha256(archive.extractfile(name).read()).hexdigest()==digest
    with np.load(stem.with_suffix('.npz'),allow_pickle=False) as a:
        frames,expanded,core,rom=a['frames'],a['lifted_frames'],a['core_final'],a['rom']
        assert int(a['padding_packet_count'])==0
    assert x['physical_rule']==json.loads(json.dumps(r.identity()))
    assert sha(library()._name)==x['compiled_binary_sha256']
    np.testing.assert_array_equal(rom,r.rom())
    assert frames.shape==(len(x['periods'])+1,3,r.WIDTH)
    assert expanded.shape==frames.shape[:2]+(f.WIDTH,)
    assert np.all((frames==0)|(frames==1)) and np.all((expanded==0)|(expanded==1))
    circuit=f.self_description();previous=None
    for k in range(len(frames)):
        cells=tuple(r.decode_cell(word.tolist()) for word in frames[k])
        lifted=tuple(f.decode_cell(word.tolist()) for word in expanded[k])
        assert lifted==tuple(r.lift(c) for c in cells)
        if previous is not None:
            scalar=r.step_ring(previous)
            native=r.cells_from_array(dense_step(r.array_from_cells(previous)))
            assert cells==scalar==native
            old=tuple(r.lift(c) for c in previous)
            full=f.step_ring(old)
            described=tuple(f.decode_cell(circuit.evaluate(tuple(bit for cell in (old[i-1],old[i],old[(i+1)%3]) for bit in f.encode_cell(cell)))) for i in range(3))
            assert full==described==lifted
        previous=cells
    assert r.decode_cores(core)==previous and r.check_boundary(core)
    assert int(frames[0,1,0])==1 and int(frames[2,1,0])==0
    for p in x['periods']:
        assert p['physical_ticks']==b.layout().period_ticks
        assert p['literal_core_ticks']+p['wait_ticks_skipped']==p['physical_ticks']
        assert p['projected_mismatches']==p['lifted_mismatches']==p['pending_packets']==0
        assert p['boundary'] is True
    result=dict(source_files=len(x['source_sha256']),macrosteps=len(frames)-1,
                projected_postinitial_bits=int(frames[1:].size),lifted_postinitial_bits=int(expanded[1:].size),
                complete_scalar_native_description_agreement=True,final_decode_boundary_and_empty_padding=True,
                projected_write_at_second_macrostep=True,total_physical_ticks=x['total_ticks'],
                artifact_sha256=x['artifact_sha256'],source_archive_sha256=x['source_archive_sha256'],
                limitation='Canonical-padding acceleration tested locally; no deeper hierarchy dynamics, maintenance or noise repair')
    output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',required=True,type=Path);parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();audit(args.input,args.output)
