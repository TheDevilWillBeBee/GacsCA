"""Independent audit of physical faults and the decoded cap counterexample."""
import argparse
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import resource
import time
import numpy as np
from gacsca.fixed_rule import small_holder_rule as f, small_holder_projected as r
from gacsca.fixed_rule import small_holder_native as native, small_holder_boundary as cap
from experiments.fixed_rule.prove_small_holder_cap_defect import prove


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def array(cells):return native.array_from_cells(tuple(r.lift(x) if isinstance(x,r.Cell) else x for x in cells))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--input',required=True);parser.add_argument('--proof',required=True);parser.add_argument('--output',required=True);args=parser.parse_args()
    stem=Path(args.input);out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();manifest=json.loads(stem.with_suffix('.json').read_text());certificate=json.loads(Path(args.proof).read_text())
    assert manifest['passed'] and certificate['passed']
    for record in (manifest,certificate):
        for path,wanted in record['source_sha256'].items():assert digest(path)==wanted,path
    assert digest(stem.with_suffix('.npz'))==manifest['artifact_sha256']
    theorem=prove();assert theorem['descriptor_sha256']==manifest['physical_descriptor_sha256']
    outputs=0;upper_outputs=0
    with np.load(stem.with_suffix('.npz'),allow_pickle=False) as archive:
        top=(cap.cell(),)*15;np.testing.assert_array_equal(archive['initial'],array(top))
        for case in manifest['cases']:
            copies=case['physical_one_bit_faults'];prefix=f'copies{copies}_'
            positions=tuple(map(int,archive[prefix+'probe']));before=archive[prefix+'before_fault'];damaged=archive[prefix+'after_fault'];after=archive[prefix+'after_one_tick']
            changed=[]
            for i,pos in enumerate(positions):
                for name,_ in f.SCHEMA:
                    k=f.COL[name]
                    if before[i,k]!=damaged[i,k]:
                        assert int(before[i,k])^int(damaged[i,k])==1
                        changed.append((pos,name))
            assert sorted(changed)==sorted(map(tuple,case['faultmap'])) and len(changed)==copies
            for i in range(7,len(positions)-7):
                neighborhood=native.cells_from_array(damaged[i-7:i+8])
                expected=f.local_step(neighborhood);actual=native.local_step(neighborhood)
                expression=f.decode_cell(f.self_description().evaluate(tuple(x for cell in neighborhood for x in f.encode_cell(cell))))
                assert expected==actual==expression
                np.testing.assert_array_equal(after[i],f.encode_cell(actual));outputs+=1
            first=archive[prefix+'raw_info_after_one_tick'];expected_first=array(top)
            if copies==3:expected_first[7,f.COL['address']]=f.Q-2
            np.testing.assert_array_equal(first,expected_first)
            # Metadata is intentionally stale until the physical ROM regenerates it.
            if copies==3:
                lifted=r.lift(r.project(f.decode_cell(first[7].tolist())))
                assert tuple(first[7])!=f.encode_cell(lifted)
            parents=list(top)
            if copies==3:parents[7]=replace(parents[7],address=f.Q-2)
            for index,committed in enumerate(archive[prefix+'decoded']):
                raw=tuple(r.lift(x) for x in parents);next_states=[]
                for i in range(15):
                    neighborhood=tuple(raw[(i+j)%15] for j in f.NEIGHBORHOOD)
                    scalar=f.local_step(neighborhood);machine=native.local_step(neighborhood)
                    expression=f.decode_cell(f.self_description().evaluate(tuple(x for cell in neighborhood for x in f.encode_cell(cell))))
                    assert scalar==machine==expression;next_states.append(r.project(scalar));upper_outputs+=1
                parents=next_states
                np.testing.assert_array_equal(committed,array(parents))
                assert parents[7].address==(f.Q-2 if copies==3 else f.Q-1)
                assert case['checkpoints'][index]['time']==(index+1)*f.U
                assert all(x.age==index+1 and x.f1==x.f2==1 for x in parents)
    result=dict(passed=True,all_clock_geometry_invariant_reproved=True,physical_fault_bits_verified=5,complete_physical_local_outputs_checked=outputs,complete_decoded_upper_outputs_checked=upper_outputs,stale_initial_metadata_not_hidden=True,two_copy_control_repairs=True,three_copy_case_persists_two_commits=True,input_manifest_sha256=digest(stem.with_suffix('.json')),artifact_sha256=digest(stem.with_suffix('.npz')),proof_manifest_sha256=digest(args.proof),source_sha256=digest(__file__),seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,limitation='Exact invariant plus saved fault/local/decoded-output audit; does not independently replay full lower work periods or claim noisy nested amplification.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
