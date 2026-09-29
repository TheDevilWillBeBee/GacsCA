"""Independent physical-fault, two-level decode, scratch and rejoin audit."""
import argparse,hashlib,json,resource,time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_projected as r,retimed_holder_program as p,retimed_holder_core as c
from gacsca.fixed_rule import retimed_holder_terminal_dag as dag,retimed_holder_endpoint_image_array as image


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(8*1024**2),b''):h.update(block)
    return h.hexdigest()


def observed_physical_faults(before,after):
    assert before.shape==after.shape and before.shape[1]==f.FIELDS
    size=len(before)*f.Q;rows=[];g=p.layout()
    for col,k in np.argwhere(before!=after):
        xor=int(before[col,k]^after[col,k]);assert xor and not xor&(xor-1)
        primary=int(col)*f.Q+g.info[int(k)]
        for offset in f.OFFSETS:rows.append(((primary-offset)%size,f.COL[f's{offset+2}_data'],xor))
    return np.array(sorted(rows),dtype=np.uint64).reshape(-1,3)


def difference_categories(before,after):
    assert before.shape==after.shape and before.shape[1]==p.layout().memory_count+5
    g=p.layout();groups=dict(history=sorted({g.history(stage,offset,k) for stage in range(3) for offset in f.NEIGHBORHOOD for k in range(f.FIELDS)}),votes=g.votes,info=g.info,hold=g.hold)
    covered={index for group in groups.values() for index in group};groups['other_scratch']=sorted(set(range(g.memory_count+5))-covered)
    different=before!=after;counts={key:int(np.count_nonzero(different[:,list(group)])) for key,group in groups.items()}
    counts['total']=int(np.count_nonzero(different));assert counts['total']==sum(v for k,v in counts.items() if k!='total')
    return counts


def load_case(name):
    path=Path('figs/fixed_rule')/f'retimed_holder_streamed_repair_{name}_v1.json';receipt=json.loads(path.read_text())
    assert receipt['passed'] and receipt['case']==name and receipt['initial_encoded_depth']==2
    assert receipt['periods']==(1 if name=='three' else 2)
    assert receipt['descriptor_sha256']==f.self_description().digest() and receipt['rom_sha256']==hashlib.sha256(p.base_rom().tobytes()).hexdigest()
    for source,digest in receipt['source_sha256'].items():assert sha(source)==digest,source
    assert sha(receipt['binary'])==receipt['binary_sha256']
    assert sha(receipt['small_artifact_path'])==receipt['small_artifact_sha256']
    assert sha(receipt['initial_info_path'])==receipt['initial_info_sha256']
    for bank,digest in receipt['bank_sha256'].items():assert sha(bank)==digest,bank
    return path,receipt


def audit_case(receipt):
    g=p.layout();rows=[]
    with np.load(receipt['small_artifact_path'],allow_pickle=False) as z:
        top=tuple(r.project(f.decode_cell(row)) for row in z['initial_top'])
        np.testing.assert_array_equal(z['actual_device_decoded_initial_top'],z['initial_top'])
        initial_bank=np.zeros((1,g.memory_count+5),dtype=np.uint64);initial_bank[:,list(g.info)]=z['initial_top']
        actual=np.load(receipt['initial_info_path'],mmap_mode='r')
        np.testing.assert_array_equal(actual,image.render(initial_bank,np.zeros((1,2),dtype=np.uint64),0));del actual
        for epoch in range(1,receipt['periods']+1):
            np.testing.assert_array_equal(z[f'period{epoch}_input_top'],[f.encode_cell(r.lift(x)) for x in top])
            terminal=dag.terminal(top)
            for phase,key in (('C','precommit_bank'),('B','committed_bank')):np.testing.assert_array_equal(z[f'period{epoch}_upper_{phase}_bank'],terminal[key])
            np.testing.assert_array_equal(z[f'period{epoch}_upper_signals'],terminal['signals'])
            raw_C=image.render(terminal['precommit_bank'],terminal['signals'],f.U-1);raw_B=image.render(terminal['committed_bank'],terminal['signals'],0)
            bank=np.load(receipt['period_results'][epoch-1]['bank_path'],mmap_mode='r');assert bank.shape==(f.Q,g.memory_count+5)
            hashes=z[f'period{epoch}_tile_hashes'];assert len(hashes)==f.Q//128
            for batch,start in enumerate(range(0,f.Q,128)):
                block=bank[start:start+128];assert hashlib.sha256(block.tobytes()).hexdigest()==hashes[batch]
                np.testing.assert_array_equal(block[:,list(g.info)],raw_B[start:start+128])
            following=r.step_ring(top);actual_top=bank[list(g.info),g.info[f.COL['s2_data']]]
            np.testing.assert_array_equal(actual_top,z[f'period{epoch}_output_top'][0]);np.testing.assert_array_equal(actual_top,f.encode_cell(r.lift(following[0])))
            np.testing.assert_array_equal(z[f'period{epoch}_signals'],raw_B[:,[f.COL['f2'],f.COL['f1']]])
            positions=z[f'period{epoch}_sample_positions'];assert len(positions)==14
            for index,pos in enumerate(positions):
                pos=int(pos);inputs=tuple(r.project(f.decode_cell(raw_C[(pos+d)%f.Q])) for d in f.NEIGHBORHOOD)
                wanted=dag.terminal(inputs)['committed_bank'][7]
                np.testing.assert_array_equal(bank[pos],wanted);np.testing.assert_array_equal(bank[pos],z[f'period{epoch}_sample_banks'][index])
            rows.append(dict(period=epoch,complete_intermediate_raw_words=raw_B.size,top_raw_fields=f.FIELDS,independent_complete_scratch_rows=len(positions),whole_bank_words_hashed=bank.size))
            del block,bank,raw_C,raw_B;top=following
    return rows


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError(out)
    started=time.perf_counter();loaded={name:load_case(name) for name in ('healthy','two','three')};receipts={name:value[1] for name,value in loaded.items()}
    assert len({row['binary_sha256'] for row in receipts.values()})==1
    g=p.layout();per_case={name:audit_case(row) for name,row in receipts.items()};fault_results={};comparisons=[]
    fixture_path=Path('figs/fixed_rule/retimed_holder_depth2_repair_fixture_v1.json');fixture=json.loads(fixture_path.read_text());assert sha(fixture_path.with_suffix('.npz'))==fixture['artifact_sha256']
    with np.load(fixture_path.with_suffix('.npz'),allow_pickle=False) as fixture_data:
        healthy_initial=np.load(receipts['healthy']['initial_info_path'],mmap_mode='r')
        for name in ('two','three'):
            altered=np.load(receipts[name]['initial_info_path'],mmap_mode='r');observed=observed_physical_faults(healthy_initial,altered)
            wanted=np.array(sorted(map(tuple,fixture_data[name+'_physical_faults'])),dtype=np.uint64)
            np.testing.assert_array_equal(observed,wanted)
            with np.load(receipts[name]['small_artifact_path'],allow_pickle=False) as z:
                np.testing.assert_array_equal(np.array(sorted(map(tuple,z['physical_bit_faults'])),dtype=np.uint64),wanted)
                np.testing.assert_array_equal(z['initial_top'][0],fixture_data['dirty_'+name]);np.testing.assert_array_equal(z['healthy_initial_top'][0],fixture_data['healthy'])
            fault_results[name]=dict(exact_bottom_bit_faults=len(observed),changed_middle_raw_words=int(np.count_nonzero(healthy_initial!=altered)))
            del altered
        del healthy_initial
    with np.load(receipts['healthy']['small_artifact_path'],allow_pickle=False) as healthy,np.load(receipts['two']['small_artifact_path'],allow_pickle=False) as dirty,np.load(receipts['three']['small_artifact_path'],allow_pickle=False) as triple:
        for epoch in (1,2):
            np.testing.assert_array_equal(healthy[f'period{epoch}_output_top'],dirty[f'period{epoch}_output_top'])
            np.testing.assert_array_equal(healthy[f'period{epoch}_signals'],dirty[f'period{epoch}_signals'])
            first=np.load(receipts['healthy']['period_results'][epoch-1]['bank_path'],mmap_mode='r');second=np.load(receipts['two']['period_results'][epoch-1]['bank_path'],mmap_mode='r');totals={}
            for start in range(0,f.Q,128):
                for key,value in difference_categories(first[start:start+128],second[start:start+128]).items():totals[key]=totals.get(key,0)+value
            if epoch==1:assert totals['total']>0 and totals['info']>0,'do not mistake top decode equality for physical recovery'
            else:assert totals['total']==0,'complete physical rejoin failed'
            comparisons.append(dict(period=epoch,bank_word_differences=totals,top_decodes_equal=True,all_physical_signals_equal=True,complete_physical_rejoin=epoch==2))
            del first,second
        h=healthy['period1_output_top'][0];d=dirty['period1_output_top'][0];t=triple['period1_output_top'][0]
        assert h[f.COL['s2_phase']]==c.WRITE and t[f.COL['s2_phase']]==c.READ_B
        assert h[f.COL['s2_value']]==c.arithmetic(c.NAND,int(healthy['initial_top'][0,f.COL['s2_value']]),int(healthy['initial_top'][0,f.COL['s2_data']]))
        assert np.any(h!=t) and np.array_equal(h,d)
        negative=dict(actual_three_copy_top_differs=True,raw_words_different=int(np.count_nonzero(h!=t)),healthy_phase=int(h[f.COL['s2_phase']]),three_copy_phase=int(t[f.COL['s2_phase']]))
    result=dict(passed=True,case_audits=per_case,physical_faults=fault_results,paired_comparisons=comparisons,negative_control=negative,complete_rejoin_by_physical_time=2*f.U*f.U,seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,references={str(path):sha(path) for path,_ in loaded.values()},source_sha256={str(path):sha(path) for path in (Path(__file__),Path(image.__file__),Path(dag.__file__))},scope='Exact correlated initial physical fault sets, actual GPU repair/control at depth two, all decoded fields, complete bank/Signal rejoin and 70 independently recomputed scratch rows. No independent stochastic noise, arbitrary fault times, or universal recovery claim.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
