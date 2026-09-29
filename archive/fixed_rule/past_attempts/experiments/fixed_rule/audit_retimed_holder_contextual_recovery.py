"""Independent global scalar replay of the contextual quiet continuation."""
import argparse
import json
import resource
import time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_core as c
from gacsca.fixed_rule import retimed_holder_contextual_flags as adapter
from gacsca.fixed_rule import retimed_holder_literal_cone as cone
from experiments.fixed_rule.audit_retimed_holder_burst_recovery import flag_step, NAMES, OTHER, MAIL
from experiments.fixed_rule.run_retimed_holder_streamed_repair import sha

FIELDS = ('bank','active_rows','counts','flags','signals','age','time')


class GlobalProcedures:
    def __init__(self, view):
        self.base = view
        self.size = view.base.size
        self.words = np.empty((self.size,len(NAMES)),dtype=np.uint64)
        self.flags = []
        for col in range(self.size//f.Q):
            sites = np.arange(col*f.Q,(col+1)*f.Q)
            raw = view.cells(sites)
            np.testing.assert_array_equal(raw,cone.normalize(raw.copy()))
            np.testing.assert_array_equal(raw[:,f.COL['address']],sites % f.Q)
            assert np.all(raw[:,f.COL['age']] == view.base.age)
            assert not np.any(raw[:,[f.COL['f2'],*(f.COL[f'w{k}_{name}'] for k in range(5) for name in ('wf1','wf2'))]])
            self.words[sites] = raw[:,[f.COL['s2_'+n] for n in NAMES]]
            self.flags.append(int.from_bytes(np.packbits(raw[:,f.COL['f1']].astype(np.uint8),bitorder='little').tobytes(),'little'))
        for col in range(self.size//f.Q):
            sites = np.arange(col*f.Q,(col+1)*f.Q)
            raw = view.cells(sites)
            for d in f.OFFSETS:
                np.testing.assert_array_equal(raw[:,[f.COL[f's{d+2}_{n}'] for n in NAMES]],self.words[(sites+d)%self.size])
        assert not np.any(self.words[:,MAIL])
        self.live = set(map(int,np.flatnonzero(np.any(self.words[:,OTHER],axis=1))))
        self.rom = cone.rom()
        self.evaluations = 0

    def step(self,age):
        assert c.active(age) and age not in (*f.RESET_AGES,*f.VOTE_AGES,f.U-1)
        candidates = sorted({(pos+d)%self.size for pos in self.live for d in (-1,0,1)})
        cache = {}
        def cell(pos):
            pos %= self.size
            if pos not in cache:
                address = pos % f.Q
                values = dict(zip(c.STATIC,map(int,self.rom[address])))
                values.update(zip(NAMES,map(int,self.words[pos])))
                cache[pos] = c.Cell(address=address,age=age,**values)
            return cache[pos]
        outputs = []
        for pos in candidates:
            result = c._clock_step(tuple(cell(pos+d) for d in range(-5,6)))
            row = tuple(getattr(result,n) for n in NAMES)
            assert not any(row[i] for i in MAIL),'mail-free domain ended'
            outputs.append(row)
        self.live = set()
        for pos,row in zip(candidates,outputs):
            self.words[pos] = row
            if any(row[i] for i in OTHER):
                self.live.add(pos)
        self.flags = [flag_step(value) for value in self.flags]
        self.evaluations += len(candidates)

    def cells(self,positions,age):
        positions = np.asarray(positions,dtype=np.int64)%self.size
        result = self.base.cells(positions)
        result[:,f.COL['age']] = age
        result[:,f.COL['f2']] = 0
        for col in np.unique(positions//f.Q):
            selected = np.flatnonzero(positions//f.Q == col)
            bits = np.unpackbits(np.frombuffer(self.flags[int(col)].to_bytes(f.Q//8,'little'),dtype=np.uint8),bitorder='little')
            result[selected,f.COL['f1']] = bits[positions[selected]%f.Q]
        for d in f.OFFSETS:
            result[:,[f.COL[f's{d+2}_{n}'] for n in NAMES]] = self.words[(positions+d)%self.size]
        return result


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
    assert receipt['completed'] and receipt['error'] is None
    assert sha(path.with_suffix('.npz')) == receipt['artifact_sha256']
    assert sha(receipt['source_receipt']) == receipt['source_receipt_sha256']
    source = json.loads(Path(receipt['source_receipt']).read_text())
    assert sha(Path(receipt['source_receipt']).with_suffix('.npz')) == receipt['source_artifact_sha256'] == source['artifact_sha256']
    for name,digest in receipt['source_sha256'].items():
        assert sha(name) == digest,name
    targets = {row['tick']:row for row in receipt['observations']}
    outputs,first_primary_crossing,clear_tick = 0,None,None
    checks = []
    with np.load(path.with_suffix('.npz'),allow_pickle=False) as saved:
        def state(prefix):
            return {k:saved[prefix+'_'+k] for k in FIELDS}
        initial = state('initial')
        with np.load(Path(receipt['source_receipt']).with_suffix('.npz'),allow_pickle=False) as original:
            for k in FIELDS:
                np.testing.assert_array_equal(initial[k],original['final_background_'+k])
            for k in ('positions','values'):
                np.testing.assert_array_equal(saved['initial_'+k],original['final_'+k])
        av = adapter.View(initial,saved['initial_positions'],saved['initial_values'])
        attached = adapter.View(state('attached'),saved['attached_positions'],saved['attached_values'])
        for col in range(receipt['colonies']):
            sites = np.arange(col*f.Q,(col+1)*f.Q)
            np.testing.assert_array_equal(av.cells(sites),attached.cells(sites))
        assert receipt['attachment']['physical_transitions'] == 0
        assert receipt['attachment']['complete_raw_words_verified'] == receipt['colonies']*f.Q*f.FIELDS
        actual,healthy = GlobalProcedures(av),GlobalProcedures(adapter.View(initial))
        age = int(initial['age'])
        assert age > f.WF_END+f.Q
        assert age+receipt['elapsed_physical_ticks'] < min(x for x in (*f.RESET_AGES,*f.VOTE_AGES,f.U) if x > age)
        head = NAMES.index('head')
        for tick in range(receipt['elapsed_physical_ticks']+1):
            if tick:
                native = []
                # Full physical output at every site for the first two ticks;
                # additional literal windows include the actual crossing.
                windows = [(col*f.Q,(col+1)*f.Q) for col in range(receipt['colonies'])] if tick <= 2 else ([(9*f.Q-64,9*f.Q+64)] if 1773 <= tick <= 1778 else [])
                for lo,hi in windows:
                    positions = np.arange(lo-7,hi+7)
                    for model in (actual,healthy):
                        native.append((model,np.arange(lo,hi),cone.step(model.cells(positions,age+tick-1))[7:-7].copy()))
                        outputs += hi-lo
                actual.step(age+tick-1);healthy.step(age+tick-1)
                for model,positions,expected in native:
                    np.testing.assert_array_equal(model.cells(positions,age+tick),expected)
                if not any(actual.flags) and clear_tick is None:
                    clear_tick = tick
                extra = [p for p in actual.live if p//f.Q == 9 and actual.words[p,head] and actual.words[p,head] != healthy.words[p,head]]
                if extra and first_primary_crossing is None:
                    first_primary_crossing = tick
            if tick in targets:
                row = targets[tick]
                hv = adapter.View(state(f'observe{tick}_healthy'))
                observed = adapter.View(state(f'observe{tick}_healthy'),saved[f'observe{tick}_positions'],saved[f'observe{tick}_values'])
                pp,counts = [],np.zeros(f.FIELDS,dtype=np.int64)
                heads = []
                for col in range(receipt['colonies']):
                    sites = np.arange(col*f.Q,(col+1)*f.Q)
                    a,h = actual.cells(sites,age+tick),healthy.cells(sites,age+tick)
                    np.testing.assert_array_equal(h,hv.cells(sites))
                    np.testing.assert_array_equal(a,observed.cells(sites))
                    diff = a != h
                    selected = np.flatnonzero(np.any(diff,axis=1))
                    pp.extend(sites[selected].tolist())
                    counts += np.count_nonzero(diff,axis=0)
                    heads.extend(sites[np.flatnonzero((a[:,f.COL['s2_head']] != 0)&diff[:,f.COL['s2_head']])].tolist())
                np.testing.assert_array_equal(saved[f'observe{tick}_positions'],pp)
                assert row['discrepant_sites'] == len(pp) and row['discrepant_words'] == int(counts.sum())
                assert row['extra_primary_head_positions'] == heads
                assert row['actual_flag1_sites'] == sum(v.bit_count() for v in actual.flags) and row['actual_flag2_sites'] == 0
                checks.append(dict(tick=tick,discrepant_sites=len(pp),discrepant_words=int(counts.sum()),extra_primary_head_positions=heads))
                print(json.dumps(dict(checks[-1],seconds=time.perf_counter()-started)),flush=True)
            elif tick % 1024 == 0:
                print(json.dumps(dict(tick=tick,seconds=time.perf_counter()-started)),flush=True)
        final = adapter.View(state('final_background'),saved['final_exception_positions'],saved['final_exception_values'])
        for col in range(receipt['colonies']):
            sites = np.arange(col*f.Q,(col+1)*f.Q)
            np.testing.assert_array_equal(final.cells(sites),actual.cells(sites,age+receipt['elapsed_physical_ticks']))
    from experiments.fixed_rule import audit_retimed_holder_burst_recovery as old
    sources = (Path(__file__),Path(adapter.__file__),Path(c.__file__),Path(f.__file__),Path(cone.__file__),Path(old.__file__))
    result = dict(passed=True,all_quiet_ticks_replayed=receipt['elapsed_physical_ticks'],colonies=receipt['colonies'],scalar_core_candidate_evaluations=actual.evaluations+healthy.evaluations,complete_native_output_states=outputs,complete_native_output_words=outputs*f.FIELDS,first_extra_primary_head_in_colony9=first_primary_crossing,first_flag_clear_tick=clear_tick,observations=checks,all_mail_outputs_zero=True,source_receipt_sha256=sha(path),artifact_sha256=receipt['artifact_sha256'],source_sha256={str(p):sha(p) for p in sources},seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,scope='Every physical tick independently replays scalar procedures in all 17 colonies, including boundary transport, plus exact per-colony flags. All complete saved raw observations and final state checked. Domain is canonical/coherent/mail-free and clock-event-free; no macrostep or upper repair claim.')
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'observations'},indent=2),flush=True)


if __name__ == '__main__':
    main()
