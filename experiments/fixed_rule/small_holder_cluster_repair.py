"""Physical five-holder fault clusters repaired by the encoded upper procedure.

Two corrupted upper value replicas are corrected; three give a failure control.
Faults are correlated initial one-bit flips in the *physical* lower Info holders.
No random-noise threshold, arbitrary-geometry repair or full depth-two claim.
"""
import argparse,hashlib,json,resource,time
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import small_holder_resident_gather as gpu,small_holder_resident_mixed as mixed
from gacsca.fixed_rule import small_holder_rule as f,small_holder_projected as r,small_holder_quotient as q,small_holder_program as p,small_holder_core as c,small_holder_native as native
from gacsca.fixed_rule.wordcode import Program
from experiments.fixed_rule.small_holder_execution import initial_ring


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def raw_array(cells):return native.array_from_cells(tuple(r.lift(x) for x in cells))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--reference',required=True);parser.add_argument('--output',required=True);args=parser.parse_args();stem=Path(args.output);reference=Path(args.reference)
    for ext in ('.json','.npz','.progress.json'):
        if stem.with_suffix(ext).exists():raise FileExistsError('preserve evidence')
    baseline=json.loads(reference.with_suffix('.json').read_text());assert baseline['passed'] and baseline['physical_rule_description']==f.self_description().digest()
    assert digest(reference.with_suffix('.npz'))==baseline['artifact_sha256']
    started=time.perf_counter();top=initial_ring();g=p.layout();raw=tuple(r.lift(x) for x in top)
    healthy=tuple(r.lift(r.project(x)) for x in native.step_ring(raw));results=[];frames=[];initial_frames=[];gpu_seconds=0.
    with np.load(reference.with_suffix('.npz'),allow_pickle=False) as archive:
        np.testing.assert_array_equal(raw_array(top),native.array_from_cells(tuple(r.lift(x) for x in r.cells_from_array(archive['initial_top']))))
        np.testing.assert_array_equal(native.array_from_cells(healthy),archive['decoded'][0])
        for offsets in ((-1,1),(-1,0,1)):
            faulty=list(top);logical={};faults=[]
            for e in offsets:
                col=7+e;field=f's{2-e}_value';address=g.info[f.COL[field]];old=getattr(faulty[col],field);wrong=old^1
                faulty[col]=replace(faulty[col],**{field:wrong})
                logical[col*f.Q+address]=q.Cell(address=address,data=wrong)
                faults.append(dict(upper_holder=col,upper_field=field,lower_logical_position=col*f.Q+address,old_word=old,new_word=wrong))
            expected=tuple(r.lift(r.project(x)) for x in native.step_ring(tuple(r.lift(x) for x in faulty)))
            assert (expected==healthy)==(len(offsets)==2)
            probe=tuple(sorted({pos+d for pos in logical for d in range(-7,8)}))
            with gpu.World(top) as clean:
                clean_raw=clean.physical_cells(probe)
            with gpu.World(top,logical=logical) as world:
                actual_raw=world.physical_cells(probe);differences=[]
                for position,a,b in zip(probe,clean_raw,actual_raw):
                    for name,_ in f.SCHEMA:
                        if getattr(a,name)!=getattr(b,name):
                            assert name in tuple(f's{i}_data' for i in range(5))
                            assert getattr(a,name)^getattr(b,name)==1
                            differences.append((position,name))
                expected_differences={(pos+e,f's{2-e}_data') for pos in logical for e in f.OFFSETS}
                assert set(differences)==expected_differences
                assert world.decode()==tuple(faulty);initial_frames.append(raw_array(faulty))
                tick=time.perf_counter();world.advance(1);gpu_seconds+=time.perf_counter()-tick
                assert world.decode()==tuple(faulty) # all five lower holders agree on the wrong word
                for target in (f.CAPTURE_AGE,f.U):
                    while world.time<target:
                        tick=time.perf_counter()
                        with patch.object(Program,'evaluate',side_effect=AssertionError('host evaluator')),patch.object(f,'local_step',side_effect=AssertionError('host upper rule')),patch.object(r,'local_step',side_effect=AssertionError('host upper rule')),patch.object(native,'local_step',side_effect=AssertionError('host rule')):
                            world.advance(min(c.T,target-world.time))
                        gpu_seconds+=time.perf_counter()-tick
                        stem.with_suffix('.progress.json').write_text(json.dumps(dict(status='running',corrupted_upper_copies=len(offsets),physical_time=world.time,gpu_run_seconds=gpu_seconds))+'\n')
                    if target==f.CAPTURE_AGE:
                        assert world.decode()==tuple(faulty)
                        for e,fault in zip(offsets,faults):
                            word=f.COL[fault['upper_field']]
                            addresses=tuple(g.history(stage,e,word) for stage in range(3))+(g.votes[(e+7)*f.FIELDS+word],)
                            records=world.logical_cells(tuple(7*f.Q+a for a in addresses))
                            assert all(x.data==fault['new_word'] for x in records)
                        hold=[]
                        for col in range(len(top)):
                            records=world.logical_cells(tuple(col*f.Q+a for a in g.hold));hold.append([x.data for x in records])
                        np.testing.assert_array_equal(np.array(hold,dtype=np.uint64),native.array_from_cells(expected))
                decoded=raw_array(world.decode());np.testing.assert_array_equal(decoded,native.array_from_cells(expected));frames.append(decoded)
                rejoins=False
                if len(offsets)==2:
                    # Continue both actual states through the next local reset.
                    # No healthy state is installed into the damaged world.
                    with mixed.World.from_stored(archive['first_stored']) as clean:
                        tick=time.perf_counter();world.advance(1);gpu_seconds+=time.perf_counter()-tick;clean.advance(1)
                        np.testing.assert_array_equal(world.stored(),clean.stored())
                        for col in range(len(top)):
                            for start in range(g.computation_cells,f.Q-5,256):
                                positions=tuple(col*f.Q+a for a in range(start,min(f.Q-5,start+256)))
                                assert world.logical_cells(positions)==clean.logical_cells(positions)
                        rejoins=True
                result=dict(corrupted_upper_copies=len(offsets),physical_one_bit_faults=len(differences),faults=faults,physical_fault_fields=differences,persists_after_first_lower_tick=True,fault_reaches_all_three_histories_and_vote=True,hold_matches_complete_upper_rule=True,decoded_equals_healthy=(expected==healthy),simulated_write=int(decoded[7,f.COL['s2_data']]),complete_physical_rejoin_at_next_reset=rejoins,physical_time=world.time)
                results.append(result);print(json.dumps({k:v for k,v in result.items() if k not in ('faults','physical_fault_fields')}),flush=True)
    np.savez_compressed(stem.with_suffix('.npz'),healthy_initial=raw_array(top),faulty_initial=np.array(initial_frames),healthy_next=native.array_from_cells(healthy),faulty_next=np.array(frames))
    paths=[Path(__file__),Path(gpu.__file__),Path(gpu.__file__).with_suffix('.cu'),Path(mixed.__file__),Path('experiments/fixed_rule/small_holder_execution.py')]
    result=dict(passed=True,cases=results,gpu_run_seconds=gpu_seconds,seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,descriptor_sha256=f.self_description().digest(),baseline_manifest_sha256=digest(reference.with_suffix('.json')),baseline_artifact_sha256=digest(reference.with_suffix('.npz')),artifact_sha256=digest(stem.with_suffix('.npz')),source_sha256={str(path):digest(path) for path in paths},binary_sha256=digest(gpu.library()._name),limitations=['targeted correlated initial physical clusters, not independent stochastic noise','one simulation link/two scales; no full nested upper work period','only procedure-value repair, not arbitrary geometry/metadata faults','three corrupted upper replicas are outside the two-holder majority contract and intentionally fail'])
    stem.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');stem.with_suffix('.progress.json').write_text(json.dumps(dict(status='complete'))+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('cases','source_sha256')},indent=2),flush=True)


if __name__=='__main__':main()
