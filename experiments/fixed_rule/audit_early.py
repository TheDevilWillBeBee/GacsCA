"""Independent audit of complete clocked macrosteps and physical evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile
import numpy as np
from gacsca.fixed_rule import clock_rule as f,early_projected as r,early_program as p,clock_native as native
from gacsca.fixed_rule.early_world import World,library


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def audit(stem,output):
    stem,output=Path(stem),Path(output)
    if output.exists():raise FileExistsError('preserve prior audit')
    root=Path(__file__).resolve().parents[2];x=json.loads(stem.with_suffix('.json').read_text())
    assert sha(stem.with_suffix('.npz'))==x['artifact_sha256'] and sha(stem.with_suffix('.tar.gz'))==x['source_archive_sha256']
    with tarfile.open(stem.with_suffix('.tar.gz')) as archive:
        assert set(archive.getnames())==set(x['source_sha256'])
        for name,digest in x['source_sha256'].items():
            assert sha(root/name)==digest,name
            assert hashlib.sha256(archive.extractfile(name).read()).hexdigest()==digest
    with np.load(stem.with_suffix('.npz'),allow_pickle=False) as a:
        frames,lifts,holds,core,rom=a['frames'],a['lifted_frames'],a['holds'],a['core_final'],a['rom'];assert int(a['padding_packet_count'])==0
        corrupt=a['corrupt_initial'];repairs=a['repair_frames'];histories=a['history_frames'];history_keys=a['history_keys'];votes=a['vote_frames']
    assert x['physical_rule']==json.loads(json.dumps(r.identity()))
    assert sha(library()._name)==x['compiled_binary_sha256'];np.testing.assert_array_equal(rom,r.rom())
    n=23;periods=len(x['periods']);assert frames.shape==(periods+1,n,len(r.SCHEMA));assert lifts.shape==(periods+1,n,f.FIELDS)
    assert holds.shape==(2*periods,n,f.FIELDS);assert frames.dtype==lifts.dtype==holds.dtype==np.uint64
    desc=f.self_description();previous=None;regenerated=0
    for k in range(len(frames)):
        cells=r.cells_from_array(frames[k]);lifted=native.cells_from_array(lifts[k])
        if k==0:
            for i,(c,raw) in enumerate(zip(cells,lifted)):
                assert r.project(raw)==c
                expected=np.array(f.encode_cell(r.lift(c)),dtype=np.uint64)
                for name in f.STATIC:expected[f.COL[name]]^=np.uint64((1<<dict(f.SCHEMA)[name])-1)
                np.testing.assert_array_equal(expected,corrupt[i]);np.testing.assert_array_equal(lifts[0,i],corrupt[i])
        else:assert lifted==tuple(r.lift(c) for c in cells)
        if previous is not None:
            old=tuple(r.lift(c) for c in previous);full=f.step_ring(old)
            assert native.cells_from_array(native.dense_step(native.array_from_cells(old)))==full
            described=tuple(f.decode_cell(desc.evaluate(tuple(word for j in f.NEIGHBORHOOD for word in f.encode_cell(old[(i+j)%n])))) for i in range(n))
            assert full==described
            assert cells==r.step_ring(previous)==tuple(r.project(c) for c in full)
            assert lifted==tuple(r.lift(r.project(c)) for c in full);regenerated+=sum(a!=b for a,b in zip(full,lifted))
            np.testing.assert_array_equal(holds[2*(k-1)],lifts[k]);np.testing.assert_array_equal(holds[2*(k-1)+1],lifts[k])
        previous=cells
    with World(core) as final:assert final.check_boundary() and final.decode()==previous
    assert int(frames[1,5,r.COL['data']])==7 # actual simulated temporal vote
    assert int(frames[1,18,r.COL['data']])==0x1122334455667788 # actual simulated commit
    assert int(frames[1,11,r.COL['address']])==111
    assert int(frames[1,11,r.COL['age']])==2 and int(frames[2,11,r.COL['age']])==3
    assert np.all(frames[:,11,r.COL['f2']]==1)
    assert int(frames[0,12,r.COL['data']])==0xFEDCBA9876543210 and int(frames[2,12,r.COL['data']])==0
    assert regenerated>0
    assert repairs.shape==(periods,n,f.FIELDS)
    assert histories.shape==(6*periods,n,11*f.FIELDS) and history_keys.shape==(6*periods,3)
    assert votes.shape==(2*periods,n,11*f.FIELDS)
    expected_keys=[]
    for period in range(1,periods+1):
        old=np.array([f.encode_cell(r.lift(c)) for c in r.cells_from_array(frames[period-1])],dtype=np.uint64)
        np.testing.assert_array_equal(repairs[period-1],old)
        neighbors=np.stack([old[(np.arange(n)+j)%n] for j in range(-5,6)],axis=1).reshape(n,-1)
        for k in range(6):np.testing.assert_array_equal(histories[6*(period-1)+k],neighbors)
        for k in range(2):np.testing.assert_array_equal(votes[2*(period-1)+k],neighbors)
        for stage,time in enumerate((16*f.Q,48*f.Q,72*f.Q)):
            expected_keys.extend((period,time,history) for history in range(stage+1))
    np.testing.assert_array_equal(history_keys,np.array(expected_keys))
    assert sha(stem.with_suffix('.rests.npz'))==x['rest_artifact_sha256']
    with np.load(stem.with_suffix('.rests.npz'),allow_pickle=False) as rest:
        expected_names=[]
        for period in range(1,periods+1):
            for stage,(lo,hi) in enumerate(((16*f.Q,32*f.Q),(48*f.Q,64*f.Q),(80*f.Q,96*f.Q),(104*f.Q,112*f.Q),(120*f.Q,f.U-1))):
                names=[f'p{period}_s{stage}_'+part for part in ('begin','end')];expected_names.extend(names)
                begin,end=(rest[name] for name in names)
                assert begin.shape==end.shape==core.shape
                assert np.all(begin[:,r.COL['age']]==lo) and np.all(end[:,r.COL['age']]==hi)
                begin[:,r.COL['age']]=0;end[:,r.COL['age']]=0
                np.testing.assert_array_equal(begin,end)
        assert set(rest.files)==set(expected_names)
    assert len(x['probes'])==15*periods
    for row in x['probes']:
        assert row['pending']==0
        for key,value in row.items():
            if key.endswith('_mismatches'):assert value==0
            if key.endswith('_unchanged'):assert value is True
    assert sum('rest_unchanged' in row for row in x['probes'])==5*periods
    for row in x['periods']:
        assert row['physical_ticks']==f.U==sum(row[k] for k in ('literal_core_ticks','quiet_ticks_skipped','scan_ticks_skipped'))
        assert row['projected_mismatches']==row['lifted_mismatches']==row['pending_packets']==0 and row['boundary'] is True
    result=dict(source_files=len(x['source_sha256']),full_clock_periods=periods,full_scalar_native_description_agreement=True,early_repair_of_all_seven_words=True,independent_saved_history_vote_and_rest_arrays=True,
        all_three_histories_both_evaluations_five_rests_and_boundary_commit=True,simulated_vote_commit_repair_and_active_write=True,
        raw_records_requiring_regeneration=regenerated,projected_postinitial_bits=periods*n*r.WIDTH,lifted_postinitial_bits=periods*n*f.WIDTH,
        total_physical_ticks=x['total_ticks'],artifact_sha256=x['artifact_sha256'],source_archive_sha256=x['source_archive_sha256'],rest_artifact_sha256=x['rest_artifact_sha256'],
        limitation='no flag-signal/trickle initiation, spatial redundancy, physical-noise robustness or deeper dynamics')
    output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();audit(args.input,args.output)
