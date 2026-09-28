"""Independent sample, literal physical-cone and complete-macrostep audit."""
import argparse,json,resource,time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_projected as r,retimed_holder_program as p,retimed_holder_quotient as q
from gacsca.fixed_rule import retimed_holder_noise_schedule as noise,retimed_holder_terminal_dag as dag
from experiments.fixed_rule.run_retimed_holder_streamed_repair import sha


def terminal_snapshot(terminal,at):
    g=p.layout();bank=terminal['committed_bank'];signals=terminal['signals'];n=len(bank);rows=np.zeros((n,64,len(q.SCHEMA)),dtype=np.uint64);counts=np.zeros(n,dtype=np.uint64)
    for col in range(n):
        records=[]
        for address in (*range(1,6),*range(f.Q-5,f.Q)):
            bit=int(signals[col,0] if address<6 else signals[col,1])
            if not bit:continue
            value=bit<<(5-address if address<6 else f.Q-1-address);index=address if address<g.memory_count else g.memory_count+address-(f.Q-5)
            records.append(q.Cell(address=address,data=int(bank[col,index]),signal=value))
        counts[col]=len(records)
        if records:rows[col,:len(records)]=q.array_from_cells(records)
    return dict(bank=bank,signals=signals,active_rows=rows,counts=counts,flags=np.zeros((n*f.Q//64,2),dtype=np.uint64),age=np.array(0,dtype=np.uint64),time=np.array(at,dtype=np.uint64))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--input',required=True);parser.add_argument('--output',required=True);args=parser.parse_args();path=Path(args.input);out=Path(args.output)
    if out.exists():raise FileExistsError(out)
    started=time.perf_counter();receipt=json.loads(path.read_text());assert receipt['passed'] and receipt['completed']
    assert sha(path.with_suffix('.npz'))==receipt['artifact_sha256']
    for source,digest in receipt['source_sha256'].items():assert sha(source)==digest
    sites=receipt['physical_sites'];horizon=receipt['requested_ticks'];sample=receipt['noise'];generated=noise.sample(sites=sites,ticks=horizon,expected_marks=sample['expected_marks'],seed=sample['seed'])
    checks=[];outputs=0;rejoins={};g=p.layout();theorem=0
    with np.load(path.with_suffix('.npz'),allow_pickle=False) as z:
        np.testing.assert_array_equal(z['schedule'],generated['schedule']);np.testing.assert_array_equal(z['replacements'],generated['replacements'])
        assert sample['realized_marks']==len(z['schedule']) and sample['space_time_volume']==sites*horizon
        schedule=z['schedule'];groups={}
        for index,(at,pos,draw) in enumerate(schedule):groups.setdefault(int(at),[]).append(index)
        assert [x['time'] for x in receipt['event_groups']]==sorted(groups)
        times=sorted(groups);min_gap=min((b-a for a,b in zip(times,times[1:])),default=horizon)
        # This is a fact about this unfiltered realization, not a sampler filter.
        assert min_gap>2 and all(row['pre_fault_complete_match'] for row in receipt['event_groups'])
        for index,event in enumerate(receipt['event_groups']):
            prefix=f'event{index}';assert event['mark_indices']==groups[event['time']]
            positions=sorted({int(schedule[j,1]) for j in event['mark_indices']});halo=list(map(int,z[prefix+'_halo_positions']))
            assert halo==sorted({(pos+d)%sites for pos in positions for d in range(-28,29)})
            actual=dict(zip(halo,z[prefix+'_actual_initial']));healthy=dict(zip(halo,z[prefix+'_healthy_initial']))
            changes={}
            for j in event['mark_indices']:changes[int(schedule[j,1])]=np.array(f.encode_cell(r.lift(r.decode_cell(z['replacements'][j]))),dtype=np.uint64)
            for pos in halo:np.testing.assert_array_equal(actual[pos],changes[pos] if pos in changes else healthy[pos])
            earliest=None
            for tick,record in enumerate(event['literal_steps'],1):
                old_keys=set(actual);safe=sorted(pos for pos in old_keys if all((pos+d)%sites in old_keys for d in f.NEIGHBORHOOD))
                next_states=[]
                for current in (actual,healthy):
                    following={}
                    for pos in safe:
                        neighbors=tuple(f.decode_cell(current[(pos+d)%sites]) for d in f.NEIGHBORHOOD)
                        following[pos]=np.array(f.encode_cell(r.lift(r.project(f.local_step(neighbors)))),dtype=np.uint64);outputs+=1
                    next_states.append(following)
                actual,healthy=next_states;probes=list(map(int,z[prefix+f'_tick{tick}_positions']))
                assert probes==sorted({(pos+d)%sites for pos in positions for d in range(-7*tick,7*tick+1)})
                a=np.array([actual[pos] for pos in probes]);b=np.array([healthy[pos] for pos in probes])
                np.testing.assert_array_equal(a,z[prefix+f'_tick{tick}_actual']);np.testing.assert_array_equal(b,z[prefix+f'_tick{tick}_healthy'])
                different=int(np.count_nonzero(np.any(a!=b,axis=1)));assert different==record['exceptions']
                matched=np.array_equal(a,b);assert matched==record['complete_physical_match']
                if matched and earliest is None:earliest=tick
            assert earliest is not None
            rejoins[str(earliest)]=rejoins.get(str(earliest),0)+1;theorem+=event['theorem_premises_before_fault']
            if (index+1)%32==0:print(json.dumps(dict(groups=index+1,scalar_outputs=outputs,seconds=time.perf_counter()-started)),flush=True)
        top=tuple(r.project(f.decode_cell(row)) for row in z['initial_top'])
        for row in receipt['periods']:
            period=row['period'];terminal=dag.terminal(top);expected=terminal_snapshot(terminal,period*f.U)
            for key,value in expected.items():
                np.testing.assert_array_equal(z[f'period{period}_actual_'+key],value)
                np.testing.assert_array_equal(z[f'period{period}_healthy_'+key],value)
            top=r.step_ring(top);raw=np.array([f.encode_cell(r.lift(cell)) for cell in top],dtype=np.uint64)
            np.testing.assert_array_equal(z[f'period{period}_decoded'],raw);np.testing.assert_array_equal(z[f'period{period}_expected'],raw)
            assert not len(z[f'period{period}_exception_positions'])
            checks.append(dict(period=period,complete_physical_bank_words=len(top)*(g.memory_count+5),complete_decoded_raw_words=raw.size,complete_snapshot_and_independent_terminal_equal=True))
        for key in expected:np.testing.assert_array_equal(z['final_actual_'+key],z['final_healthy_'+key])
        assert not len(z['final_exception_positions'])
    assert receipt['actual_ticks']==horizon and receipt['marks_filtered_or_resampled']==0
    assert not any(row['rebased_data_cells'] or row['rebased_flag_fields'] for row in receipt['advance_metrics'])
    result=dict(passed=True,groups=len(groups),realized_marks=sample['realized_marks'],exact_seeded_sample_reproduced=True,minimum_event_group_gap_ticks=min_gap,independent_scalar_physical_outputs=outputs,complete_rejoin_ticks_histogram=rejoins,theorem_eligible_groups=theorem,period_checks=checks,zero_representation_rebases=True,seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,source_receipt_sha256=sha(path),artifact_sha256=sha(path.with_suffix('.npz')),source_sha256={str(x):sha(x) for x in (Path(__file__),Path(noise.__file__),Path(dag.__file__),Path(f.__file__))},numpy_version=np.__version__,scope='Exact unfiltered sample, independent scalar evolution of all local fault cones and full terminal-state comparisons for the realized low-rate pilot. The realized spacing is checked, not enforced by sampling; no statistical threshold or high-rate extrapolation.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__':main()
