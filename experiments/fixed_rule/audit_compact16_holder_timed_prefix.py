"""Literal full-physical coupling from incoherent timed pulses to saved runs.

Only complete radius-seven physical transitions run on CPU here. No represented
middle transition is replaced by a host call. Every output in the entire causal
cone is checked; outside that cone the two initial neighborhoods are identical.
"""
import argparse,json,resource,time
from functools import lru_cache
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import compact16_holder_rule as f,compact16_holder_projected as r,compact16_holder_program as p,compact16_holder_native as native
from experiments.fixed_rule.run_compact16_holder_streamed_depth2 import sha


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output);artifact=out.with_suffix('.npz')
    if out.exists() or artifact.exists():raise FileExistsError(out)
    started=time.perf_counter();basepath=Path('figs/fixed_rule/compact16_holder_timed_depth2_checkpoint_v1.json');base=json.loads(basepath.read_text());assert base['passed']
    bankpath=base['bank_paths'][0];assert sha(bankpath)==base['bank_sha256'][bankpath]
    bank=np.load(bankpath,mmap_mode='r');g=p.layout();size=len(bank)*f.Q
    with np.load(base['small_artifact'],allow_pickle=False) as z:signals=z['step1_signals']
    fixture=Path(base['fixture']);receipt=json.loads(fixture.read_text());assert sha(fixture)==base['fixture_sha256']
    assert sha(fixture.with_suffix('.npz'))==receipt['artifact_sha256']
    with np.load(fixture.with_suffix('.npz'),allow_pickle=False) as z:upper={count:z[f'case{count}_faults'] for count in (2,3)}
    @lru_cache(maxsize=None)
    def original(pos):
        col,a=divmod(pos%size,f.Q);values=dict(address=a)
        if 1<=a<=5:values['signal']=int(signals[col,0])<<(5-a)
        elif a>=f.Q-5:values['signal']=int(signals[col,1])<<(f.Q-1-a)
        for offset in f.OFFSETS:
            owner,address=divmod((pos+offset)%size,f.Q)
            index=address if address<g.memory_count else g.memory_count+address-(f.Q-5) if address>=f.Q-5 else None
            if index is not None:values[f's{offset+2}_data']=int(bank[owner,index])
        return np.array(f.encode_cell(r.lift(r.Cell(**values))),dtype=np.uint64)
    def pulse(count,offsets):
        changes={}
        for col,field,xor in upper[count]:
            primary=int(col)*f.Q+g.info[int(field)]
            for offset in offsets:
                pos=(primary-offset)%size;changes.setdefault(pos,{})[f.COL[f's{offset+2}_data']]=int(xor)
        return changes
    def raw(pos,changes):
        row=original(pos).copy()
        for field,xor in changes.get(pos,{}).items():row[field]^=np.uint64(xor)
        return row
    saved={};results=[]
    for name,count,offsets,reference_offsets in (('lower_repairs',2,(-2,-1),()),('middle_repairs',2,(-2,-1,0),f.OFFSETS),('three_copy_control',3,(-2,-1,0),f.OFFSETS)):
        damaged=pulse(count,offsets);reference=pulse(count,reference_offsets)
        frontier=sorted({(pos-j)%size for pos in set(damaged)|set(reference) for j in f.NEIGHBORHOOD})
        actual=[];expected=[];before=[];reference_before=[]
        for pos in frontier:
            before.append(raw(pos,damaged));reference_before.append(raw(pos,reference))
            for changes,target in ((damaged,actual),(reference,expected)):
                neighbors=tuple(f.decode_cell(raw((pos+j)%size,changes)) for j in f.NEIGHBORHOOD)
                result=native.local_step(neighbors)
                assert result==f.local_step(neighbors),'native/scalar physical parity'
                target.append(f.encode_cell(result))
        actual=np.array(actual,dtype=np.uint64);expected=np.array(expected,dtype=np.uint64)
        np.testing.assert_array_equal(actual,expected)
        assert np.any(np.array(before)!=np.array(reference_before))
        # Confirm the first literal tick retains the wrong coherent Info for
        # the cross-level cases instead of mistaking normalization for repair.
        for col,field,xor in upper[count]:
            primary=int(col)*f.Q+g.info[int(field)];index=frontier.index(primary)
            wanted=int(bank[int(col),g.info[int(field)]])^(int(xor) if reference_offsets else 0)
            assert int(actual[index,f.COL['s2_data']])==wanted
        def fault_rows(changes):return np.array(sorted((pos,field,xor) for pos,row in changes.items() for field,xor in row.items()),dtype=np.uint64).reshape(-1,3)
        saved[name+'_positions']=np.array(frontier,dtype=np.uint64);saved[name+'_before']=np.array(before);saved[name+'_reference_before']=np.array(reference_before)
        saved[name+'_after']=actual;saved[name+'_reference_after']=expected;saved[name+'_faults']=fault_rows(damaged);saved[name+'_reference_faults']=fault_rows(reference)
        row=dict(case=name,physical_faults=sum(map(len,damaged.values())),reference_physical_faults=sum(map(len,reference.values())),entire_causal_outputs=len(frontier),complete_raw_fields_per_output=f.FIELDS,coupled_after_literal_ticks=1,encoded_wrong_values_retained=bool(reference_offsets));results.append(row);print(json.dumps(row),flush=True)
    np.savez_compressed(artifact,**saved)
    result=dict(passed=True,cases=results,physical_fault_time=receipt['age']*f.U,checkpoint_receipt_sha256=sha(basepath),checkpoint_bank_sha256=base['bank_sha256'][bankpath],artifact_sha256=sha(artifact),source_sha256={str(x):sha(x) for x in (Path(__file__),Path(native.__file__),Path(f.__file__))},seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,scope='Literal complete physical first-tick coupling for incoherent 4/6/9-bit timed pulses to respectively healthy/10-bit/15-bit coherent trajectories. Determinism permits reuse of their subsequent noiseless endpoints; no incoherent input is silently projected into the shortcut domain.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__':main()
