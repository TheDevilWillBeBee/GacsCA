"""Independent raw-state/causal-cone audit of the nested-window experiment."""
import argparse,hashlib,json,resource,time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import small_holder_rule as f,small_holder_projected as r,small_holder_initial as initial,small_holder_native as native,small_holder_program as p,small_holder_resident_mixed as gpu


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def scalar_projected(window):return r.lift(r.project(f.local_step(window)))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--input',required=True);parser.add_argument('--output',required=True);args=parser.parse_args();stem=Path(args.input);out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    started=time.perf_counter();m=json.loads(stem.with_suffix('.json').read_text());assert m['passed']
    for path,wanted in m['source_sha256'].items():assert digest(path)==wanted,path
    assert digest(gpu.library()._name)==m['binary_sha256']
    assert digest(stem.with_suffix('.npz'))==m['artifact_sha256']
    desc=f.self_description();assert desc.digest()==m['descriptor_sha256']
    assert hashlib.sha256(p.base_rom().tobytes()).hexdigest()==m['rom_bytes_sha256']
    with np.load(stem.with_suffix('.npz'),allow_pickle=False) as a:data={name:a[name] for name in a.files}
    top=r.cells_from_array(data['top']);positions=tuple(map(int,data['positions']))
    raw=tuple(r.lift(initial.cell_at(top,1,x)) for x in positions)
    np.testing.assert_array_equal(data['initial_raw'],native.array_from_cells(raw))
    assert len(raw)==62 and m['guard_per_segment']==14
    cones=[raw[:33],raw[33:]];interior_counts=[]
    for step in (1,2):
        scalar=f.step_ring(raw);assert scalar==native.step_ring(raw)
        for i,wanted in enumerate(scalar):
            words=tuple(word for j in f.NEIGHBORHOOD for word in f.encode_cell(raw[(i+j)%len(raw)]))
            assert f.decode_cell(desc.evaluate(words))==wanted
        raw=tuple(r.lift(r.project(x)) for x in scalar)
        np.testing.assert_array_equal(data['decoded'][step-1],native.array_from_cells(raw))
        cones=[tuple(scalar_projected(cone[i-7:i+8]) for i in range(7,len(cone)-7)) for cone in cones]
        margin=7*step
        assert raw[margin:33-margin]==cones[0]
        assert raw[33+margin:62-margin]==cones[1]
        interior_counts.append(sum(map(len,cones)))
        assert m['periods'][step-1]['true_ring_interior_raw_cells_match']==interior_counts[-1]
        assert raw[14+step-1].s2_head==1
        assert raw[47].s2_data==0x123456789ABCDEF0
        assert all(x.f2==0 for x in raw)
        assert 0<sum(x.f1 for x in raw)<len(raw)
    metrics=m['metrics']
    assert metrics['physical_ticks']==2*f.U==metrics['independent_ticks']+metrics['synchronous_literal_ticks']+metrics['synchronous_transport_or_quiet_ticks']
    assert metrics['colony_literal_ticks']+metrics['colony_transport_or_quiet_ticks']==len(raw)*metrics['independent_ticks']
    result=dict(passed=True,scalar_native_complete_descriptor_agreement=True,initial_states_match_independent_recursive_initializer=True,every_raw_decoded_controller_field_checked=True,true_ring_interior_cells_per_step=interior_counts,upper_controller_reset_and_motion=True,encoded_top_raw_value_preserved=True,mixed_right_flags_exercised=True,source_binary_artifact_hashes_match=True,physical_and_colony_tick_accounting_matches=True,manifest_sha256=digest(stem.with_suffix('.json')),artifact_sha256=digest(stem.with_suffix('.npz')),audit_source_sha256=digest(__file__),seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,limitation='Decoded guarded-window results match true upper-ring causal cones. This neither executes the full Q-squared bottom ring nor proves its complete physical trajectory, and it is not an upper work period/top macrostep.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
