"""Audit complete word-controller traces, repair and mandatory program regeneration."""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile
import numpy as np
from gacsca.fixed_rule import word_projected as r,word_rule as f,word_program as b
from gacsca.fixed_rule.word_native import dense_step,array_from_cells,cells_from_array
from gacsca.fixed_rule.word_world import World,library


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
    n=x['represented_cells'];assert n==23
    assert frames.shape==(len(x['periods'])+1,n,len(r.SCHEMA))
    assert expanded.shape==frames.shape[:2]+(f.FIELDS,)
    assert frames.dtype==expanded.dtype==np.uint64
    description=f.self_description();previous=None;regenerated=0
    for k in range(len(frames)):
        cells=r.cells_from_array(frames[k]);lifted=cells_from_array(expanded[k])
        assert lifted==tuple(r.lift(c) for c in cells)
        if previous is not None:
            scalar=r.step_ring(previous);old=tuple(r.lift(c) for c in previous)
            full=f.step_ring(old);native=cells_from_array(dense_step(array_from_cells(old)))
            described=tuple(f.decode_cell(description.evaluate(tuple(word for j in f.NEIGHBORHOOD for word in f.encode_cell(old[(i+j)%n])))) for i in range(n))
            assert full==native==described
            assert cells==scalar==tuple(r.project(c) for c in full)
            assert lifted==tuple(r.lift(r.project(c)) for c in full)
            regenerated+=sum(a!=z for a,z in zip(full,lifted))
        previous=cells
    assert r.decode_cores(core)==previous
    with World(core) as boundary:assert boundary.check_boundary()
    assert int(frames[0,11,r.COL['address']])==143 and int(frames[1,11,r.COL['address']])==111
    assert int(frames[1,11,r.COL['age']])==0 and int(frames[2,11,r.COL['age']])==1
    assert np.all(frames[:,11,r.COL['f2']]==1) # printed persistence remains
    assert int(frames[0,12,r.COL['data']])==0xFEDCBA9876543210 and int(frames[2,12,r.COL['data']])==0
    assert regenerated>0
    for p in x['periods']:
        assert p['physical_ticks']==b.layout().period_ticks
        assert p['literal_core_ticks']+p['wait_ticks_skipped']==p['physical_ticks']
        assert p['projected_mismatches']==p['lifted_mismatches']==p['pending_packets']==0 and p['boundary'] is True
    result=dict(source_files=len(x['source_sha256']),macrosteps=len(frames)-1,
                projected_postinitial_words=int(frames[1:].size),lifted_postinitial_words=int(expanded[1:].size),
                projected_postinitial_bits=(len(frames)-1)*n*r.WIDTH,lifted_postinitial_bits=(len(frames)-1)*n*f.WIDTH,
                complete_scalar_native_description_agreement=True,final_decode_boundary_and_empty_padding=True,
                active_write_at_second_macrostep=True,address_and_age_repaired_at_first_macrostep=True,
                printed_flag2_persistence_preserved=True,raw_records_requiring_program_regeneration=regenerated,
                total_physical_ticks=x['total_ticks'],artifact_sha256=x['artifact_sha256'],source_archive_sha256=x['source_archive_sha256'],
                limitation='healthy physical structure only; unclocked evaluator; no five-stage/redundancy/noise robustness or deeper dynamics')
    output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',required=True,type=Path);parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();audit(args.input,args.output)
