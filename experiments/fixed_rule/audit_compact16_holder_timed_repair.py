"""Audit explicit timed pulses, every nested scratch word and complete rejoin."""
import argparse
import json
from pathlib import Path
import time
import numpy as np
from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_core as c
from gacsca.fixed_rule import compact16_holder_program as p, compact16_holder_native as native
from experiments.fixed_rule.run_compact16_holder_streamed_depth2 import sha
from experiments.fixed_rule.audit_compact16_holder_all_scratch import terminal_rows


def observed_faults(before,after):
    assert before.shape==after.shape and before.shape[1]==f.FIELDS
    size=len(before)*f.Q;g=p.layout();rows=[]
    for col,field in np.argwhere(before!=after):
        xor=int(before[col,field]^after[col,field]);assert xor and not xor&(xor-1)
        primary=int(col)*f.Q+g.info[int(field)]
        for offset in f.OFFSETS:rows.append(((primary-offset)%size,f.COL[f's{offset+2}_data'],xor))
    return np.array(sorted(rows),dtype=np.uint64).reshape(-1,3)


def categories():
    g=p.layout();history=[]
    for wire in g.gathered_inputs:
        offset,field=wire//f.FIELDS-7,wire%f.FIELDS
        history.extend(g.history(stage,offset,field) for stage in range(3))
    groups=dict(history=history,votes=list(g.votes),info=list(g.info),hold=list(g.hold))
    covered={value for row in groups.values() for value in row}
    groups['other_scratch']=sorted(set(range(g.memory_count+5))-covered)
    return groups


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    started=time.perf_counter();receipts={};cases={};references={};g=p.layout();audited=[]
    for name in ('checkpoint','healthy','two','three'):
        path=Path(f'figs/fixed_rule/compact16_holder_timed_depth2_{name}_v1.json');receipt=json.loads(path.read_text())
        assert receipt['passed'] and receipt['case']==name and receipt['descriptor_sha256']==f.self_description().digest()
        for source,digest in receipt['source_sha256'].items():assert sha(source)==digest,source
        assert sha(receipt['small_artifact'])==receipt['small_sha256'] and sha(receipt['binary'])==receipt['binary_sha256']
        receipts[name]=receipt;references[str(path)]=sha(path)
        with np.load(receipt['small_artifact'],allow_pickle=False) as z:cases[name]={key:z[key] for key in z.files}
    assert len({r['binary_sha256'] for r in receipts.values()})==1
    fixture_path=Path(receipts['checkpoint']['fixture']);fixture=json.loads(fixture_path.read_text())
    assert sha(fixture_path)==receipts['checkpoint']['fixture_sha256'] and sha(fixture['artifact'])==fixture['artifact_sha256']
    baseline=cases['checkpoint']['step1_middle']
    with np.load(fixture['artifact'],allow_pickle=False) as z:
        np.testing.assert_array_equal(cases['checkpoint']['input_middle'],z['previous_raw'])
        np.testing.assert_array_equal(baseline,z['checkpoint_raw'])
        for name,count in (('healthy',0),('two',2),('three',3)):
            value=cases[name];faults=observed_faults(baseline,value['input_middle'])
            np.testing.assert_array_equal(faults,np.array(sorted(map(tuple,value['physical_faults'])),dtype=np.uint64).reshape(-1,3))
            assert len(faults)==5*count
            changed=np.argwhere(baseline!=value['input_middle']);assert len(changed)==count
            if count:np.testing.assert_array_equal(changed,np.array(sorted((int(pos),int(field)) for pos,field,_ in z[f'case{count}_faults'])))
            wanted=baseline.copy()
            for col,address,xor in value['bank_updates']:wanted[int(col),g.info.index(int(address))]^=xor
            np.testing.assert_array_equal(wanted,value['input_middle'])
            assert receipts[name]['complete_checkpoint_receipt_sha256']==references['figs/fixed_rule/compact16_holder_timed_depth2_checkpoint_v1.json']
    for name,receipt in receipts.items():
        source=cases[name]['input_middle']
        for step,path in enumerate(receipt['bank_paths'],1):
            assert sha(path)==receipt['bank_sha256'][path]
            expected=np.empty_like(source)
            native.library().compact16_holder_ring(native.pointer(source),native.pointer(expected),len(source))
            actual=cases[name][f'step{step}_middle'];np.testing.assert_array_equal(expected,actual)
            bank=np.load(path,mmap_mode='r',allow_pickle=False);assert bank.shape==(f.Q,g.memory_count+5)
            checked=0
            for at in range(0,f.Q,512):
                count=min(512,f.Q-at);complete,signals=terminal_rows(source,at,count)
                np.testing.assert_array_equal(bank[at:at+count],complete,err_msg=f'{name} step{step} row{at}')
                np.testing.assert_array_equal(bank[at:at+count,g.info],actual[at:at+count])
                np.testing.assert_array_equal(cases[name][f'step{step}_signals'][at:at+count],signals)
                checked+=complete.size
            audited.append(dict(case=name,step=step,all_middle_raw_words_checked=int(actual.size),all_bank_words_independently_recomputed=checked))
            print(json.dumps(dict(**audited[-1],seconds=time.perf_counter()-started)),flush=True)
            del bank;source=actual
    comparisons=[];groups=categories()
    for step in (1,2):
        np.testing.assert_array_equal(cases['healthy'][f'step{step}_middle'],cases['two'][f'step{step}_middle'])
        np.testing.assert_array_equal(cases['healthy'][f'step{step}_signals'],cases['two'][f'step{step}_signals'])
        healthy=np.load(receipts['healthy']['bank_paths'][step-1],mmap_mode='r');dirty=np.load(receipts['two']['bank_paths'][step-1],mmap_mode='r')
        totals={name:0 for name in groups};changed=[]
        for at in range(0,f.Q,512):
            diff=healthy[at:at+512]!=dirty[at:at+512]
            for name,indices in groups.items():totals[name]+=int(np.count_nonzero(diff[:,indices]))
            changed.extend((at+np.flatnonzero(np.any(diff,axis=1))).tolist())
        totals['total']=sum(totals.values())
        assert totals['info']==totals['hold']==0
        assert (totals['total']>0) if step==1 else totals['total']==0
        comparisons.append(dict(step=step,differences=totals,changed_colonies=changed,complete_rejoin=step==2))
        del healthy,dirty
    b=fixture['rom_operands']['b'];healthy=cases['healthy']['step1_middle'];triple=cases['three']['step1_middle']
    wrong=int(np.count_nonzero(healthy!=triple));assert wrong==15
    assert healthy[b+1,f.COL['s2_phase']]==c.WRITE and triple[b+1,f.COL['s2_phase']]==c.READ_B
    age=fixture['age'];assert receipts['healthy']['entry_physical_time']==age*f.U
    result=dict(passed=True,cases=audited,comparisons=comparisons,three_copy_wrong_raw_middle_words=wrong,
                physical_two_case_bit_faults=10,physical_three_case_bit_faults=15,
                complete_physical_rejoin_by=(age+2)*f.U,middle_repair_after_lower_ticks=f.U,
                all_bank_words_independently_recomputed=sum(x['all_bank_words_independently_recomputed'] for x in audited),
                all_middle_raw_words_checked=sum(x['all_middle_raw_words_checked'] for x in audited),
                references=references,seconds=time.perf_counter()-started,
                source_sha256={str(Path(__file__)):sha(__file__)},
                scope='Timed coherent physical lower pulses during a live middle evaluator; exhaustive retained-bank recomputation and complete physical rejoin. Not a stochastic threshold, broad noise theorem or generic incoherent endpoint shortcut.')
    with args.output.open('x') as out:out.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
