"""Reproduce noise draws and audit saved physical transitions and observations."""
import argparse,hashlib,json,resource,time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import small_holder_noise as noise,small_holder_rule as f,small_holder_projected as r,small_holder_native as native
from gacsca.fixed_rule import small_holder_general_faults as overlay,small_holder_resident_general as general


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def array(cells):return native.array_from_cells(tuple(cells))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--input',required=True);parser.add_argument('--output',required=True);args=parser.parse_args();stem=Path(args.input);out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    started=time.perf_counter();m=json.loads(stem.with_suffix('.json').read_text());n=m['noise']
    for path,h in m['source_sha256'].items():assert sha(path)==h,path
    assert sha(stem.with_suffix('.npz'))==m['artifact_sha256'];assert sha(stem.with_suffix('.noise.npz'))==m['noise_archive_sha256'];assert sha(stem.with_suffix('.events.jsonl'))==m['event_log_sha256']
    assert sha(overlay.library()._name)==m['fault_binary_sha256'];assert sha(general.library()._name)==m['controller_binary_sha256']
    schedule=noise.generate(n['sites'],n['ticks'],n['seed'],n['rate_exponent'],max_events=max(2048,n['realized_events']))
    assert schedule.metadata()==n
    with np.load(stem.with_suffix('.noise.npz'),allow_pickle=False) as z:
        for name in ('times','positions','replacements'):np.testing.assert_array_equal(z[name],getattr(schedule,name))
    records=[json.loads(row) for row in stem.with_suffix('.events.jsonl').read_text().splitlines()];done=0
    for record in records:
        assert record['first_event']==done;end=done+record['count']
        assert np.all(schedule.times[done:end]==record['time'])
        assert list(map(int,schedule.positions[done:end]))==record['positions'];done=end
    assert done==m['processed_events'];assert not m['resampled']
    if m['execution_complete']:assert done==len(schedule.times)
    with np.load(stem.with_suffix('.npz'),allow_pickle=False) as z:data={k:z[k] for k in z.files}
    desc=f.self_description();assert desc.digest()==m['physical_descriptor_sha256'];physical_checks=0
    for sample,event in enumerate(map(int,data['probe_event_indices'])):
        tick=int(schedule.times[event]);assert tick==int(data['probe_times'][sample])
        positions=tuple(map(int,data['probe_positions'][sample]));before=data['probe_before_noise'][sample].copy()
        group=np.flatnonzero(schedule.times==tick);changes={int(schedule.positions[i]):r.lift(r.decode_cell(schedule.replacements[i].tolist())) for i in group}
        for index,pos in enumerate(positions):
            if pos in changes:before[index]=f.encode_cell(changes[pos])
        np.testing.assert_array_equal(before,data['probe_after_noise'][sample])
        cells={pos:f.decode_cell(row.tolist()) for pos,row in zip(positions,before)}
        saved={pos:f.decode_cell(row.tolist()) for pos,row in zip(positions,data['probe_after_local_before_noise'][sample])}
        center=int(schedule.positions[event])
        for d in range(-7,8):
            position=(center+d)%n['sites'];neighbors=tuple(cells[(position+j)%n['sites']] for j in f.NEIGHBORHOOD)
            value=f.local_step(neighbors);assert value==native.local_step(neighbors)
            assert value==f.decode_cell(desc.evaluate(tuple(word for cell in neighbors for word in f.encode_cell(cell))))
            assert r.lift(r.project(value))==saved[position];physical_checks+=1
    state=tuple(f.decode_cell(row.tolist()) for row in data['initial']);outcomes=[]
    for index,observation in enumerate(m['observations']):
        raw=f.step_ring(state);assert raw==native.step_ring(state)
        for i,value in enumerate(raw):
            inputs=tuple(word for j in f.NEIGHBORHOOD for word in f.encode_cell(state[(i+j)%len(state)]));assert value==f.decode_cell(desc.evaluate(inputs))
        state=tuple(r.lift(r.project(x)) for x in raw);expected=array(state);np.testing.assert_array_equal(data['expected'][index],expected)
        actual=data['decoded'][index];equal=bool(np.array_equal(actual,expected))
        assert equal==observation['equal_to_healthy'] and int(np.count_nonzero(actual!=expected))==observation['different_raw_words']
        try:valid=all(r.lift(r.project(f.decode_cell(row.tolist())))==f.decode_cell(row.tolist()) for row in actual)
        except ValueError:valid=False
        assert valid==observation['valid_projected_encoding'];outcomes.append(equal)
    result=dict(audit_passed=True,execution_complete=m['execution_complete'],seed=n['seed'],realized_events=n['realized_events'],noise_realization_reproduced_exactly=True,logged_events_match_schedule_prefix=True,independent_full_physical_local_checks=physical_checks,decoded_matches_healthy=outcomes,reported_final_physical_equality=m['final_physical_equal_to_healthy'],forcing_or_clearing_events=m['forcing_or_clearing_events'],manifest_sha256=sha(stem.with_suffix('.json')),audit_source_sha256=sha(__file__),seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,scope='Noise realization, every injection log and saved local/decoded observations independently checked. Full physical rejoin is a runtime comparison in the hashed driver. Very-low-rate pilot; this audit verifies recorded failures as well as successes and establishes no noise threshold.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
