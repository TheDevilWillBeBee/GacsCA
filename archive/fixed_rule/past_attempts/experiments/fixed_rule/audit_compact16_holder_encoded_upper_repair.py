"""Read-only independent audit of the retained 63-cell, two-period repair.

No GPU evolution or replacement of saved states. Scalar upper transitions,
instruction replay, independent SSA last writers, all sparse controller fields,
and streamed full physical commit transitions are checked separately.
"""
import json
from pathlib import Path
import time
import numpy as np
from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_projected as r
from gacsca.fixed_rule import compact16_holder_program as p, compact16_holder_records as q
from gacsca.fixed_rule import compact16_holder_packed as packed, compact16_holder_resident_period as period
from gacsca.fixed_rule import compact16_holder_terminal_reference as reference
from gacsca.fixed_rule import compact16_holder_literal_cone as cone
from experiments.fixed_rule.audit_compact16_holder_all_scratch import terminal_rows
from experiments.fixed_rule.run_compact16_holder_streamed_depth2 import sha


def scalar_step(raw):
    cells=tuple(f.decode_cell(row) for row in raw)
    return np.array([f.encode_cell(r.lift(r.project(f.local_step(tuple(cells[(i+d)%len(cells)] for d in range(-7,8))))))
                     for i in range(len(cells))],dtype=np.uint64)


def check_records(saved,label,signals):
    """Check all stored active fields, including presence and absence of records.

    Data and Age cached inside packed records may be stale: rp_read obtains them
    from the complete bank and shared clock. They are checked via those owners.
    """
    bank=saved[label+'_bank'];rows=saved[label+'_packed_records'];counts=saved[label+'_counts']
    assert rows.shape==(len(bank),period.SLOTS,packed.WORDS)
    assert counts.shape==(len(bank),) and np.all(counts<=period.SLOTS)
    unpacked=packed.unpack(rows);checked=0
    for col,count in enumerate(map(int,counts)):
        assert not np.any(rows[col,count:]),'nonzero unexported padding'
        actual={}
        for row in unpacked[col,:count]:
            a=int(row[q.COL['address']]);assert 0<=a<f.Q and a not in actual
            values=tuple(int(row[q.COL[name]]) for name in period.ACTIVE)
            assert any(values),'unexpected empty active record'
            for name in ('f1','f2','wf1','wf2'):assert row[q.COL[name]]==0
            actual[a]=values;checked+=len(period.ACTIVE)
        expected={}
        for a,bit in [(a,int(signals[col,0])<<(5-a)) for a in range(1,6)]+[(a,int(signals[col,1])<<(f.Q-1-a)) for a in range(f.Q-5,f.Q)]:
            if bit:expected[a]=tuple(bit if name=='signal' else 0 for name in period.ACTIVE)
        assert actual==expected,(label,col,actual,expected)
    return checked


def main():
    root=Path('figs/fixed_rule');receipt_path=root/'compact16_holder_encoded_upper_repair_v1.json'
    output=root/'compact16_holder_encoded_upper_repair_audit_v1.json'
    if output.exists():raise FileExistsError(output)
    started=time.perf_counter();receipt=json.loads(receipt_path.read_text());assert receipt['passed']
    assert sha(receipt['artifact'])==receipt['artifact_sha256']
    for path,digest in receipt['source_sha256'].items():assert sha(path)==digest,path
    assert sha(receipt['fixture'])==receipt['fixture_sha256']
    fixture=json.loads(Path(receipt['fixture']).read_text())
    assert sha(fixture['artifact'])==fixture['artifact_sha256']
    assert receipt['descriptor_sha256']==f.self_description().digest()
    assert receipt['ROM_sha256']==r.identity()['ROM_sha256']
    g=p.layout();bank_words=0;ssa_words=0;commit_words=0;active_words=0;scalar_outputs=0;results=[]
    with np.load(receipt['artifact'],allow_pickle=False) as z, np.load(fixture['artifact'],allow_pickle=False) as origin:
        healthy=z['initial_healthy_upper'];damaged=z['initial_damaged_upper'];n=len(healthy)
        assert n==63
        first=receipt['upper_window_original_first']
        np.testing.assert_array_equal(healthy,origin['checkpoint_raw'][first:first+n])
        expected_damage=healthy.copy();maximum=r.Cell(**{name:(1<<width)-1 for name,width in r.SCHEMA})
        expected_damage[[31,32]]=f.encode_cell(r.lift(maximum))
        np.testing.assert_array_equal(damaged,expected_damage)
        assert 31-2*7>0 and 32+2*7<n-1
        initial=np.zeros((n,g.memory_count+5),dtype=np.uint64);initial[:,list(g.info)]=damaged
        np.testing.assert_array_equal(z['initial_lower_bank'],initial)
        assert int(z['initial_lower_age'])==int(z['initial_lower_time'])==0
        active_words+=check_records(z,'initial_lower',np.zeros((n,2),dtype=np.uint64))
        original_healthy=healthy.copy()
        for epoch in (1,2):
            inputs=damaged.copy();healthy=scalar_step(healthy);damaged=scalar_step(damaged);scalar_outputs+=2*n
            np.testing.assert_array_equal(healthy,z[f'healthy_upper_{epoch}'])
            np.testing.assert_array_equal(damaged,z[f'expected_upper_{epoch}'])
            np.testing.assert_array_equal(damaged,z[f'decoded_upper_{epoch}'])
            # Additional seam-free native comparison uses the original full-Q
            # fixture, without placing a periodic edge in this 63-cell window.
            whole_healthy=origin['checkpoint_raw'].copy()
            whole_damaged=whole_healthy.copy();whole_damaged[first+np.array([31,32])]=f.encode_cell(r.lift(maximum))
            for _ in range(epoch):whole_healthy=cone.step(whole_healthy);whole_damaged=cone.step(whole_damaged)
            region=slice(31-7*epoch,33+7*epoch)
            np.testing.assert_array_equal(healthy[region],whole_healthy[first+region.start:first+region.stop])
            np.testing.assert_array_equal(damaged[region],whole_damaged[first+region.start:first+region.stop])
            parents=tuple(r.project(f.decode_cell(row)) for row in inputs)
            wanted=reference.terminal(parents);ssa,ssa_signals=terminal_rows(inputs,0,n)
            np.testing.assert_array_equal(ssa,wanted['committed_bank']);ssa_words+=ssa.size
            np.testing.assert_array_equal(ssa_signals,wanted['signals'])
            for suffix,key,age,tick in (('precommit','precommit_bank',f.U-1,epoch*f.U-1),('postcommit','committed_bank',0,epoch*f.U)):
                label=f'period{epoch}_{suffix}'
                assert int(z[label+'_age'])==age and int(z[label+'_time'])==tick
                np.testing.assert_array_equal(z[label+'_bank'],wanted[key]);bank_words+=wanted[key].size
                active_words+=check_records(z,label,wanted['signals'])
            before=cone.BankImage(z[f'period{epoch}_precommit_bank'],wanted['signals'],f.U-1)
            after=cone.BankImage(z[f'period{epoch}_postcommit_bank'],wanted['signals'],0)
            for start in range(0,before.size,8192):
                stop=min(start+8192,before.size)
                window=before.cells(np.arange(start-7,stop+7))
                actual=cone.step(window)[7:-7]
                np.testing.assert_array_equal(actual,after.cells(np.arange(start,stop)),err_msg=f'physical commit {epoch} at {start}')
                commit_words+=actual.size
            different=damaged!=healthy
            result=dict(period=epoch,raw_differences_from_healthy=int(np.count_nonzero(different)),different_sites_from_healthy=int(np.count_nonzero(np.any(different,axis=1))),complete_decoded_words=damaged.size)
            assert result['raw_differences_from_healthy']==receipt['periods'][epoch-1]['different_raw_words_from_healthy']
            results.append(result);print(json.dumps(result),flush=True)
        assert results[0]['raw_differences_from_healthy']==32 and results[1]['raw_differences_from_healthy']==0
        # Ensure this is an active upper computation rather than a fixed point.
        assert np.any(original_healthy!=healthy)
    result=dict(passed=True,reference=str(receipt_path),reference_sha256=sha(receipt_path),artifact_sha256=receipt['artifact_sha256'],
                source_sha256={str(Path(x)):sha(x) for x in (__file__,reference.__file__,scalar_step.__code__.co_filename)},
                descriptor_sha256=f.self_description().digest(),ROM_sha256=r.identity()['ROM_sha256'],
                periods=results,independent_scalar_upper_outputs=scalar_outputs,
                complete_bank_words_checked=bank_words,independent_SSA_bank_words_checked=ssa_words,
                complete_native_physical_commit_words_checked=commit_words,stored_active_record_fields_checked=active_words,
                initial_bank_words_checked=initial.size,full_Q_reference_repair_cone_matches=True,
                seconds=time.perf_counter()-started,
                scope='Independent scalar two-step upper repair, full terminal banks via instruction and SSA references, complete stored controller/mail/Signal records, and every physical output at both commits. Continuous in-period evolution relies on the guarded event backend and its existing certificates/parity tests; not an independent literal replay of 2U ticks, a full upper colony, or general amplification.')
    with output.open('x') as stream:stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
