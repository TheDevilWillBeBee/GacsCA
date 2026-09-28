"""Independent CPU audit of complete streamed depth-two endpoint artifacts."""
import argparse,hashlib,json,resource,time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_projected as r,retimed_holder_program as p
from gacsca.fixed_rule import retimed_holder_terminal_dag as dag,retimed_holder_endpoint_image_array as image


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(8*1024**2),b''):h.update(block)
    return h.hexdigest()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--reference',required=True);parser.add_argument('--output',required=True);args=parser.parse_args();reference=Path(args.reference);out=Path(args.output)
    if out.exists():raise FileExistsError(out)
    started=time.perf_counter();receipt=json.loads(reference.read_text());assert receipt['passed'] and receipt['initial_encoded_depth']==2 and receipt['periods']==2 and receipt['top_cells']==1
    assert receipt['descriptor_sha256']==f.self_description().digest() and receipt['rom_sha256']==hashlib.sha256(p.base_rom().tobytes()).hexdigest()
    for path,digest in receipt['source_sha256'].items():assert sha(path)==digest,path
    assert sha(receipt['binary'])==receipt['binary_sha256']
    assert sha(receipt['small_artifact_path'])==receipt['small_artifact_sha256']
    assert sha(receipt['initial_info_path'])==receipt['initial_info_sha256']
    for path,digest in receipt['bank_sha256'].items():assert sha(path)==digest,path
    g=p.layout();results=[]
    with np.load(receipt['small_artifact_path'],allow_pickle=False) as z:
        initial_top=z['initial_top'];top=tuple(r.project(f.decode_cell(row)) for row in initial_top)
        initial_bank=np.zeros((1,g.memory_count+5),dtype=np.uint64);initial_bank[:,list(g.info)]=initial_top
        expected_initial=image.render(initial_bank,np.zeros((1,2),dtype=np.uint64),0)
        actual_initial=np.load(receipt['initial_info_path'],mmap_mode='r');np.testing.assert_array_equal(actual_initial,expected_initial)
        initial_words=actual_initial.size;del actual_initial,expected_initial
        for epoch in (1,2):
            np.testing.assert_array_equal(z[f'period{epoch}_input_top'],[f.encode_cell(r.lift(x)) for x in top])
            terminal=dag.terminal(top)
            for phase,key in (('C','precommit_bank'),('B','committed_bank')):np.testing.assert_array_equal(z[f'period{epoch}_upper_{phase}_bank'],terminal[key])
            np.testing.assert_array_equal(z[f'period{epoch}_upper_signals'],terminal['signals'])
            raw_C=image.render(terminal['precommit_bank'],terminal['signals'],f.U-1)
            raw_B=image.render(terminal['committed_bank'],terminal['signals'],0)
            bank=np.load(receipt['period_results'][epoch-1]['bank_path'],mmap_mode='r')
            assert bank.shape==(f.Q,g.memory_count+5) and bank.dtype==np.uint64
            hashes=z[f'period{epoch}_tile_hashes'];assert len(hashes)==f.Q//128
            for batch,start in enumerate(range(0,f.Q,128)):
                block=bank[start:start+128]
                assert hashlib.sha256(block.tobytes()).hexdigest()==hashes[batch]
                np.testing.assert_array_equal(block[:,list(g.info)],raw_B[start:start+128])
            np.testing.assert_array_equal(z[f'period{epoch}_signals'],raw_B[:,[f.COL['f2'],f.COL['f1']]])
            decoded=bank[list(g.info),g.info[f.COL['s2_data']]]
            np.testing.assert_array_equal(decoded,z[f'period{epoch}_output_top'][0])
            following=r.step_ring(top)
            np.testing.assert_array_equal(decoded,f.encode_cell(r.lift(following[0])))
            positions=z[f'period{epoch}_sample_positions'];samples=z[f'period{epoch}_sample_banks'];assert len(positions)==14
            for index,pos in enumerate(positions):
                pos=int(pos);inputs=tuple(r.project(f.decode_cell(raw_C[(pos+offset)%f.Q])) for offset in f.NEIGHBORHOOD)
                expected=dag.terminal(inputs)['committed_bank'][7]
                np.testing.assert_array_equal(bank[pos],expected,err_msg=f'full scratch at {pos}')
                np.testing.assert_array_equal(bank[pos],samples[index])
            results.append(dict(period=epoch,all_complete_bank_words_hashed=int(bank.size),all_intermediate_raw_words_checked=int(raw_B.size),all_top_raw_fields_checked=f.FIELDS,independently_recomputed_complete_scratch_rows=len(positions),independently_recomputed_scratch_words=len(positions)*(g.memory_count+5)))
            del block,bank,raw_C,raw_B;top=following
    result=dict(passed=True,initial_complete_raw_Info_words_checked=int(initial_words),periods=results,seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,reference=str(reference),reference_sha256=sha(reference),source_sha256={str(path):sha(path) for path in (Path(__file__),Path(image.__file__),Path(dag.__file__))},scope='Independent CPU verification of complete encoded initialization, every decoded intermediate/top raw field, whole bank integrity, and 28 complete scratch rows across two accelerated depth-two endpoints. Not exhaustive independent recomputation of every scratch word or a proof of arbitrary CUDA backend parity.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
