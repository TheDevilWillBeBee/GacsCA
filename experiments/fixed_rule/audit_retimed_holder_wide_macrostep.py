"""Independent physical event-trace audit using actual ROM semantic guards.

Every literal event executes scalar core procedures. Each transport segment is
checked against all instruction/operand/reflection sites read from the actual
ROM and against head collisions. Quiet intervals and whole-ring commit/reset
are checked separately. No simulated successor is installed by this audit.
"""
import argparse
from functools import lru_cache
import json
import resource
import time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_core as c
from gacsca.fixed_rule import retimed_holder_projected as r, retimed_holder_program as p
from gacsca.fixed_rule import retimed_holder_contextual_flags as adapter
from gacsca.fixed_rule import retimed_holder_literal_cone as cone
from experiments.fixed_rule.audit_retimed_holder_contextual_recovery import GlobalProcedures, FIELDS
from experiments.fixed_rule.audit_retimed_holder_burst_recovery import NAMES
from experiments.fixed_rule.run_retimed_holder_streamed_repair import sha

COL = {n:i for i,n in enumerate(NAMES)}
CONTROL = [COL[n] for n in ('head',*c.CONTROL)]


from experiments.fixed_rule import audit_retimed_holder_contextual_macrostep as original_trace
Replay, TransportGuard = original_trace.Replay, original_trace.TransportGuard


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input',required=True)
    parser.add_argument('--output',required=True)
    args = parser.parse_args()
    path,out = Path(args.input),Path(args.output)
    if out.exists():
        raise FileExistsError(out)
    started = time.perf_counter()
    receipt = json.loads(path.read_text())
    recovery = json.loads(Path(receipt['source_receipt']).read_text())
    burst = json.loads(Path(recovery['source_receipt']).read_text())
    affected_colony = int(burst['center_colony'])+1
    assert receipt['completed'] and receipt['error'] is None and receipt['pilot_ticks'] is None
    assert sha(path.with_suffix('.npz')) == receipt['artifact_sha256']
    assert sha(receipt['source_receipt']) == receipt['source_receipt_sha256']
    assert sha(Path(receipt['source_receipt']).with_suffix('.npz')) == receipt['source_artifact_sha256']
    for name,digest in receipt['source_sha256'].items():
        assert sha(name) == digest,name
    guard = TransportGuard()
    literal_ticks = transport_ticks = quiet_ticks = bulk_ticks = native_outputs = scalar_outputs = 0
    transitions,checks = [],[]
    with np.load(path.with_suffix('.npz'),allow_pickle=False) as saved, np.load(Path(receipt['source_receipt']).with_suffix('.npz'),allow_pickle=False) as original:
        state = {k:original['final_background_'+k] for k in FIELDS}
        view = adapter.View(state,original['final_exception_positions'],original['final_exception_values'])
        model = Replay(view)
        assert not any(model.flags)
        np.testing.assert_array_equal(model.words,saved['initial_words'])
        initial_signals = np.concatenate([view.cells(np.arange(start,start+f.Q))[:,f.COL['signal']] for start in range(0,model.size,f.Q)])
        np.testing.assert_array_equal(initial_signals,saved['signals'])
        clock = receipt['initial_time']
        targets = {row['time']:i for i,row in enumerate(receipt['checkpoints'])}
        verified = set()
        def check():
            if clock in targets and clock not in verified:
                i = targets[clock]
                np.testing.assert_array_equal(model.words,saved[f'checkpoint{i}_words'])
                np.testing.assert_array_equal(initial_signals,saved[f'checkpoint{i}_signals'])
                verified.add(clock)
                checks.append(dict(time=clock,complete_logical_procedure_words=model.words.size))
                print(json.dumps(dict(stage='checkpoint verified',**checks[-1],seconds=time.perf_counter()-started)),flush=True)
        def raw(words,sites,age):
            sites = np.asarray(sites,dtype=np.int64)%model.size
            value = view.cells(sites)
            value[:,f.COL['age']] = age
            for d in f.OFFSETS:
                value[:,[f.COL[f's{d+2}_{n}'] for n in NAMES]] = words[(sites+d)%model.size]
            return value
        def scalar_probes(before,after,old_age,positions):
            for pos in positions:
                inputs = raw(before,pos+np.arange(-7,8),old_age)
                expected = f.encode_cell(r.lift(r.project(f.local_step(tuple(f.decode_cell(cell) for cell in inputs)))))
                np.testing.assert_array_equal(raw(after,[pos],(old_age+1)%f.U)[0],expected)
            return len(positions)
        trace = saved['physical_event_trace']
        assert len(trace) == receipt['physical_trace_events']
        last_count = len(model.live)
        for ordinal,(kind,start,duration) in enumerate(trace):
            kind,start,duration = int(kind),int(start),int(duration)
            if start != clock:
                assert f.ACTIVE_ENDS[4] <= clock < start <= f.U-1,'unjustified physical-time gap'
                for target in sorted(t for t in targets if clock < t <= start):
                    quiet_ticks += target-clock;clock = target;check()
                quiet_ticks += start-clock;clock = start
            assert clock == start
            age = clock % f.U
            if kind == 0:
                guard.advance(model,age,duration)
                transport_ticks += duration;clock += duration
            elif kind == 1:
                assert duration == 1
                probes = []
                if literal_ticks % 1024 == 0:
                    heads = sorted(model.live)
                    if heads:
                        probes = [heads[0],next((pos for pos in heads if pos//f.Q == affected_colony),heads[-1])]
                before = model.words.copy() if probes else None
                model.step(age)
                if probes:
                    scalar_outputs += scalar_probes(before,model.words,age,sorted(set(probes)))
                literal_ticks += 1;clock += 1
            elif kind == 2:
                assert duration == 1 and age in (f.U-1,0)
                before = model.words.copy()
                rom = guard.rom
                if age == f.U-1:
                    selected = (rom[:,0] == c.MEM)&(rom[:,c.STATIC.index('first')] == 0)&((rom[:,c.STATIC.index('a')]&c.INFO) != 0)
                    addresses = np.flatnonzero(selected)
                    for col in range(model.size//f.Q):
                        sites = col*f.Q+addresses
                        model.words[sites,COL['data']] = before[sites+1,COL['data']]
                else:
                    for pos in model.live:
                        row = before[pos];address = pos % f.Q
                        if row[COL['head']] and not row[COL['direction']] and rom[address,0] == c.MEM and row[COL['phase']] == c.WRITE and rom[address,1] == row[COL['rd']]:
                            model.words[pos,COL['data']] = row[COL['value']]
                    first = rom[:,c.STATIC.index('first')] != 0
                    erase = first | ((rom[:,0] == c.MEM)&((rom[:,c.STATIC.index('a')]&1) != 0))
                    model.words[:,[COL[n] for n in NAMES if n != 'data']] = 0
                    for col in range(model.size//f.Q):
                        model.words[col*f.Q+np.flatnonzero(erase),COL['data']] = 0
                        sites = col*f.Q+np.flatnonzero(first)
                        model.words[sites,COL['head']] = 1
                        model.words[sites,COL['pc']] = rom[first,c.STATIC.index('a')] & np.uint64(0xFFFFFFFF)
                    model.live = set(range(0,model.size,f.Q))
                for start_site in range(0,model.size,f.Q):
                    sites = np.arange(start_site,start_site+f.Q)
                    expected = cone.step(raw(before,np.arange(start_site-7,start_site+f.Q+7),age))[7:-7]
                    np.testing.assert_array_equal(raw(model.words,sites,(age+1)%f.U),expected)
                    native_outputs += f.Q
                probes = {col*f.Q+d for col in range(model.size//f.Q) for d in (0,1,2,f.Q-2,f.Q-1,*list(p.layout().info)[:3])}
                probes.update(pos for pos in model.live)
                scalar_outputs += scalar_probes(before,model.words,age,sorted(probes))
                bulk_ticks += 1;clock += 1
            else:
                raise AssertionError('unknown physical trace event')
            if len(model.live) != last_count:
                transitions.append(dict(time=clock,head_positions=sorted(model.live)))
                last_count = len(model.live)
            check()
            if ordinal and ordinal % 10000 == 0:
                print(json.dumps(dict(trace_event=ordinal,physical_time=clock,scalar_core_outputs=model.evaluations,seconds=time.perf_counter()-started)),flush=True)
        assert clock == receipt['final_time'] == f.U+1 and verified == set(targets)
        np.testing.assert_array_equal(model.words,saved['final_words'])
        np.testing.assert_array_equal(initial_signals,saved['final_signals'])
        parents = tuple(r.project(f.decode_cell(cell)) for cell in saved['parent_raw'])
        expected = np.array([f.encode_cell(r.lift(cell)) for cell in r.step_ring(parents)],dtype=np.uint64)
        np.testing.assert_array_equal(expected,saved['expected_decoded_raw'])
        committed = saved[f'checkpoint{targets[f.U]}_words']
        decoded = committed[np.arange(len(parents))[:,None]*f.Q+np.array(p.layout().info),COL['data']]
        np.testing.assert_array_equal(decoded,saved['decoded_raw'])
        raw_diff = np.count_nonzero(decoded != expected,axis=1).tolist()
        mutable_diff = np.count_nonzero(decoded[:,len(f.STATIC):] != expected[:,len(f.STATIC):],axis=1).tolist()
        commit_row = receipt['checkpoints'][targets[f.U]]
        assert raw_diff == commit_row['decoded_raw_differences_by_colony']
        assert mutable_diff == commit_row['decoded_mutable_differences_by_colony']
        assert literal_ticks+transport_ticks+quiet_ticks+bulk_ticks == clock-receipt['initial_time']
    from experiments.fixed_rule import audit_retimed_holder_contextual_recovery as replay
    sources = (Path(__file__),Path(replay.__file__),Path(c.__file__),Path(f.__file__),Path(cone.__file__),Path(adapter.__file__),Path(original_trace.__file__))
    result = dict(passed=True,all_physical_trace_events_checked=len(trace),guarded_transport_ticks=transport_ticks,literal_ticks=literal_ticks,quiet_ticks=quiet_ticks,bulk_ticks=bulk_ticks,scalar_core_candidate_evaluations=model.evaluations,unique_complete_scalar_neighborhood_evaluations=model.unique_evaluations,complete_native_clock_output_states=native_outputs,complete_native_clock_output_words=native_outputs*f.FIELDS,full_scalar_G_probes=scalar_outputs,receiving_colony=affected_colony,complete_checkpoints_verified=len(checks),head_count_transitions=transitions,decoded_raw_differences_by_colony=raw_diff,decoded_mutable_differences_by_colony=mutable_diff,next_reset_heads=sorted(model.live),source_receipt_sha256=sha(path),artifact_sha256=receipt['artifact_sha256'],source_sha256={str(x):sha(x) for x in sources},seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,scope='All global physical events replayed with independent scalar procedures; transport checked against actual ROM semantic sites and collisions. Complete native clock outputs and scalar probes. No receiving-layer repair or general noise threshold claim.')
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'head_count_transitions'},indent=2),flush=True)


if __name__ == '__main__':
    main()
