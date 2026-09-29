"""Independent raw fault-map and complete-description repair/failure audit."""
import argparse,hashlib,json,time,resource
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import small_holder_rule as f,small_holder_projected as r,small_holder_initial as initial,small_holder_native as native,small_holder_program as p,small_holder_resident_gather as gpu


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--input',required=True);parser.add_argument('--output',required=True);args=parser.parse_args();stem=Path(args.input);out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    started=time.perf_counter();m=json.loads(stem.with_suffix('.json').read_text());assert m['passed']
    for path,wanted in m['source_sha256'].items():assert digest(path)==wanted,path
    assert digest(gpu.library()._name)==m['binary_sha256'];assert digest(stem.with_suffix('.npz'))==m['artifact_sha256']
    desc=f.self_description();assert desc.digest()==m['descriptor_sha256']
    with np.load(stem.with_suffix('.npz'),allow_pickle=False) as archive:data={k:archive[k] for k in archive.files}
    healthy=tuple(f.decode_cell(row.tolist()) for row in data['healthy_initial']);top=tuple(r.project(x) for x in healthy)
    expected_healthy=tuple(r.lift(r.project(x)) for x in native.step_ring(healthy))
    np.testing.assert_array_equal(native.array_from_cells(expected_healthy),data['healthy_next'])
    for case_index,case in enumerate(m['cases']):
        faulty=tuple(f.decode_cell(row.tolist()) for row in data['faulty_initial'][case_index]);bad_top=tuple(r.project(x) for x in faulty)
        scalar=f.step_ring(faulty);assert scalar==native.step_ring(faulty)
        for i,actual in enumerate(scalar):
            inputs=tuple(word for j in f.NEIGHBORHOOD for word in f.encode_cell(faulty[(i+j)%len(faulty)]))
            assert f.decode_cell(desc.evaluate(inputs))==actual
        expected=tuple(r.lift(r.project(x)) for x in scalar)
        np.testing.assert_array_equal(native.array_from_cells(expected),data['faulty_next'][case_index])
        positive=case['corrupted_upper_copies']==2
        assert (expected==expected_healthy)==positive==case['decoded_equals_healthy']
        assert expected[7].s2_data==0x123456789ABCDEF0^(0 if positive else 1)
        actual_upper_changes={(i,name) for i,(a,b) in enumerate(zip(healthy,faulty)) for name,_ in f.SCHEMA if getattr(a,name)!=getattr(b,name)}
        assert actual_upper_changes=={(row['upper_holder'],row['upper_field']) for row in case['faults']}
        positions={row['lower_logical_position']+d for row in case['faults'] for d in range(-7,8)}
        changes=set()
        for position in positions:
            a=r.lift(initial.cell_at(top,1,position));b=r.lift(initial.cell_at(bad_top,1,position))
            for name,_ in f.SCHEMA:
                if getattr(a,name)!=getattr(b,name):
                    assert getattr(a,name)^getattr(b,name)==1
                    changes.add((position,name))
        assert changes=={tuple(x) for x in case['physical_fault_fields']}
        assert len(changes)==5*case['corrupted_upper_copies']==case['physical_one_bit_faults']
        assert case['persists_after_first_lower_tick'] and case['fault_reaches_all_three_histories_and_vote']
        assert case['complete_physical_rejoin_at_next_reset']==positive
    result=dict(passed=True,all_raw_decoded_fields_match_scalar_native_and_descriptor=True,physical_fault_map_matches_independent_encoder=True,two_upper_copy_case_repairs=True,three_upper_copy_case_fails_as_expected=True,initial_physical_one_bit_fault_counts=[x['physical_one_bit_faults'] for x in m['cases']],manifest_sha256=digest(stem.with_suffix('.json')),artifact_sha256=digest(stem.with_suffix('.npz')),audit_source_sha256=digest(__file__),seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,scope='Saved raw states independently prove fault mapping and decoded repair/failure. Full physical rejoin and history persistence are runtime assertions in the separately hashed experiment driver, not reconstructed from this small archive.',limitation='targeted correlated initial faults through one simulation link; no stochastic noise threshold or full nested work-period claim')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
