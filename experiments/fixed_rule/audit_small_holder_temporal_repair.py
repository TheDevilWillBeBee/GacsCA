"""Independent complete-rule audit of the combined temporal-fault experiment."""
import argparse,hashlib,json,resource,time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import small_holder_rule as f,small_holder_projected as r,small_holder_native as native,small_holder_program as p
from gacsca.fixed_rule import small_holder_general_faults as overlay,small_holder_resident_general as general


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--input',required=True);parser.add_argument('--output',required=True);args=parser.parse_args();stem=Path(args.input);out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    started=time.perf_counter();m=json.loads(stem.with_suffix('.json').read_text());assert m['passed']
    for path,h in m['source_sha256'].items():assert sha(path)==h,path
    assert sha(stem.with_suffix('.npz'))==m['artifact_sha256'];assert sha(overlay.library()._name)==m['fault_binary_sha256'];assert sha(general.library()._name)==m['controller_binary_sha256']
    with np.load(stem.with_suffix('.npz'),allow_pickle=False) as z:data={k:z[k] for k in z.files}
    desc=f.self_description();assert desc.digest()==m['physical_rule_description']
    old=tuple(f.decode_cell(row.tolist()) for row in data['initial']);bad=tuple(f.decode_cell(row.tolist()) for row in data['faulty_upper_initial'])
    healthy=native.step_ring(old);faulty=f.step_ring(bad);assert faulty==native.step_ring(bad)
    for i,cell in enumerate(faulty):
        words=tuple(word for j in f.NEIGHBORHOOD for word in f.encode_cell(bad[(i+j)%len(bad)]));assert f.decode_cell(desc.evaluate(words))==cell
    wanted=tuple(r.lift(r.project(x)) for x in healthy);repaired=tuple(r.lift(r.project(x)) for x in faulty);assert wanted==repaired
    for key in ('expected','hold_after_simulated_repair','decoded'):np.testing.assert_array_equal(data[key],native.array_from_cells(wanted))
    np.testing.assert_array_equal(data['after_first_lower_tick'],data['faulty_upper_initial'])
    upper_changes={(i,name) for i,(a,b) in enumerate(zip(old,bad)) for name,_ in f.SCHEMA if getattr(a,name)!=getattr(b,name)}
    assert upper_changes=={(6,'s3_value'),(8,'s1_value')}
    expected_faults=set()
    for col,name in upper_changes:
        target=col*f.Q+p.layout().info[f.COL[name]]
        expected_faults.update((target+d,f's{2-d}_data') for d in (-1,0,1))
    assert expected_faults=={tuple(x) for x in m['initial_physical_one_bit_faults']} and len(expected_faults)==6
    positions=tuple(map(int,data['late_probe_positions']));before={pos:f.decode_cell(row.tolist()) for pos,row in zip(positions,data['late_before_faults'])};after={pos:f.decode_cell(row.tolist()) for pos,row in zip(positions,data['late_after_faults'])};nextstate={pos:f.decode_cell(row.tolist()) for pos,row in zip(positions,data['late_after_one_tick'])}
    changes=[(pos,name,getattr(before[pos],name),getattr(after[pos],name)) for pos in positions for name,_ in f.SCHEMA if getattr(before[pos],name)!=getattr(after[pos],name)]
    assert changes==[tuple(x) for x in m['late_changed_raw_fields']]
    assert {pos for pos,_,_,_ in changes}==set(m['late_fault_sites'])
    front=m['late_fault_sites'][-1];assert [(name,a,b) for pos,name,a,b in changes if pos==front]==[('f1',1,0)]
    assert all(r.lift(r.project(x))==x for x in after.values())
    checked=0
    for pos in positions:
        if not all(pos+j in after for j in f.NEIGHBORHOOD):continue
        cells=tuple(after[pos+j] for j in f.NEIGHBORHOOD);a=f.local_step(cells);assert a==native.local_step(cells)
        assert a==f.decode_cell(desc.evaluate(tuple(word for cell in cells for word in f.encode_cell(cell))))
        assert r.lift(r.project(a))==nextstate[pos];checked+=1
    assert checked==31
    deltas=np.bitwise_xor(data['delayed_flags'],data['healthy_flags_same_time']);difference=[sum(int(v).bit_count() for v in deltas[:,i]) for i in range(2)];assert sum(difference)>0
    assert m['complete_physical_rejoin_time']==f.U+1 and m['all_decoded_fields_match']
    result=dict(passed=True,complete_decoded_repair_matches_scalar_native_descriptor=True,early_fault_map_correct=True,late_projected_fault_map_correct=True,late_full_physical_causal_cone_sites=checked,physical_flag_differences_after_256_ticks=difference,manifest_sha256=sha(stem.with_suffix('.json')),artifact_sha256=sha(stem.with_suffix('.npz')),audit_source_sha256=sha(__file__),seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,scope='Saved complete upper outputs and late first-tick physical cones independently checked; complete physical rejoin is a runtime assertion in the hashed experiment driver, not reconstructed from the small archive. Targeted faults through one simulation link, no stochastic threshold.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
