"""Audit complete timed depth-two checkpoints, explicit pulses and state rejoin."""
import argparse,json,resource,time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_program as p,retimed_holder_projected as r
from gacsca.fixed_rule import retimed_holder_native as native,retimed_holder_terminal_dag as dag
from experiments.fixed_rule.run_retimed_holder_streamed_repair import sha
from experiments.fixed_rule.audit_retimed_holder_streamed_repair import observed_physical_faults,difference_categories


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError(out)
    started=time.perf_counter();receipts={};references={};g=p.layout();cases={};audited=[]
    for name in ('checkpoint','healthy','two','three'):
        path=Path(f'figs/fixed_rule/retimed_holder_timed_depth2_{name}_v1.json');receipt=json.loads(path.read_text());assert receipt['passed'] and receipt['case']==name
        for source,digest in receipt['source_sha256'].items():assert sha(source)==digest,source
        for bank,digest in receipt['bank_sha256'].items():assert sha(bank)==digest,bank
        assert sha(receipt['small_artifact'])==receipt['small_sha256'];assert sha(receipt['binary'])==receipt['binary_sha256']
        assert receipt['descriptor_sha256']==f.self_description().digest()
        receipts[name]=receipt;references[str(path)]=sha(path)
        with np.load(receipt['small_artifact'],allow_pickle=False) as z:cases[name]={key:z[key] for key in z.files}
    assert len({x['binary_sha256'] for x in receipts.values()})==1
    base=cases['checkpoint']['step1_middle']
    fixture_path=Path(receipts['checkpoint']['fixture']);fixture_receipt=json.loads(fixture_path.read_text())
    assert sha(fixture_path)==receipts['checkpoint']['fixture_sha256']
    assert sha(fixture_path.with_suffix('.npz'))==fixture_receipt['artifact_sha256']
    with np.load(fixture_path.with_suffix('.npz'),allow_pickle=False) as fixture:
        np.testing.assert_array_equal(cases['checkpoint']['input_middle'],fixture['previous_raw'])
        np.testing.assert_array_equal(base,fixture['checkpoint_raw'])
        for name in ('healthy','two','three'):
            x=cases[name];observed=observed_physical_faults(base,x['input_middle'])
            np.testing.assert_array_equal(observed,np.array(sorted(map(tuple,x['physical_faults'])),dtype=np.uint64).reshape(-1,3))
            count={'healthy':0,'two':2,'three':3}[name];assert len(observed)==5*count
            changes=np.argwhere(base!=x['input_middle']);assert len(changes)==count
            if count:np.testing.assert_array_equal(changes, np.array(sorted((int(pos),int(field)) for pos,field,_ in fixture[f'case{count}_faults'])))
            wanted=base.copy()
            for col,address,xor in x['bank_updates']:wanted[int(col),g.info.index(int(address))]^=xor
            np.testing.assert_array_equal(wanted,x['input_middle'])
            assert receipts[name]['complete_checkpoint_receipt_sha256']==references[str(Path('figs/fixed_rule/retimed_holder_timed_depth2_checkpoint_v1.json'))]
    positions=(0,7,9563,9564,9565,9566,9567,9568,f.Q-1)
    for name in receipts:
        receipt=receipts[name];x=cases[name];source=x['input_middle']
        for step,path in enumerate(receipt['bank_paths'],1):
            # Independent physical descriptor executes every represented middle
            # output, including its live evaluator and all raw backups.
            expected=np.empty_like(source)
            native.library().retimed_holder_ring(native.pointer(source),native.pointer(expected),len(source))
            actual=x[f'step{step}_middle'];np.testing.assert_array_equal(expected,actual)
            bank=np.load(path,mmap_mode='r',allow_pickle=False);assert bank.shape==(f.Q,g.memory_count+5)
            for start in range(0,f.Q,128):np.testing.assert_array_equal(bank[start:start+128,g.info],actual[start:start+128])
            np.testing.assert_array_equal(x[f'step{step}_signals'],actual[:,[f.COL['f2'],f.COL['f1']]])
            for pos in positions:
                neighbors=tuple(r.project(f.decode_cell(source[(pos+d)%f.Q])) for d in f.NEIGHBORHOOD)
                oracle=dag.terminal(neighbors)
                np.testing.assert_array_equal(bank[pos],oracle['committed_bank'][7])
                np.testing.assert_array_equal(x[f'step{step}_signals'][pos],oracle['signals'][7])
            audited.append(dict(case=name,step=step,all_middle_raw_words=actual.size,complete_bank_words=bank.size,independent_complete_scratch_rows=len(positions)))
            print(json.dumps(audited[-1]),flush=True);del bank;source=actual
    comparisons=[]
    for step in (1,2):
        healthy=cases['healthy'];dirty=cases['two']
        np.testing.assert_array_equal(healthy[f'step{step}_middle'],dirty[f'step{step}_middle'])
        np.testing.assert_array_equal(healthy[f'step{step}_signals'],dirty[f'step{step}_signals'])
        h=np.load(receipts['healthy']['bank_paths'][step-1],mmap_mode='r');d=np.load(receipts['two']['bank_paths'][step-1],mmap_mode='r');totals={};changed_rows=[]
        for start in range(0,f.Q,128):
            for key,value in difference_categories(h[start:start+128],d[start:start+128]).items():totals[key]=totals.get(key,0)+value
            changed_rows.extend((start+np.flatnonzero(np.any(h[start:start+128]!=d[start:start+128],axis=1))).tolist())
        assert totals['info']==totals['hold']==0
        if step==1:assert totals['total']>0
        else:assert totals['total']==0
        comparisons.append(dict(step=step,differences=totals,changed_colonies=changed_rows,complete_rejoin=step==2));del h,d
    healthy=cases['healthy']['step1_middle'];triple=cases['three']['step1_middle']
    assert np.count_nonzero(healthy!=triple)==15
    assert int(healthy[9566,f.COL['s2_phase']])==3 and int(triple[9566,f.COL['s2_phase']])==2
    age=receipts['healthy']['middle_age'];assert receipts['healthy']['entry_physical_time']==age*f.U
    result=dict(passed=True,cases=audited,comparisons=comparisons,three_copy_wrong_raw_middle_words=15,physical_two_case_bit_faults=10,physical_three_case_bit_faults=15,complete_physical_rejoin_by=(age+2)*f.U,middle_repair_after_lower_ticks=f.U,all_complete_scratch_rows_recomputed=sum(x['independent_complete_scratch_rows'] for x in audited),all_middle_raw_words_checked=sum(x['all_middle_raw_words'] for x in audited),references=references,source_sha256={str(x):sha(x) for x in (Path(__file__),Path(dag.__file__),Path(native.__file__))},seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,scope='Complete endpoint acceleration during actual middle computation, coherent timed lower Info pulses, complete middle repair/control and complete physical bank/Signal rejoin. No stochastic threshold or generic incoherent-fault endpoint shortcut.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__':main()
