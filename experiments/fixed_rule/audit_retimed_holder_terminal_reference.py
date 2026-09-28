"""Compare a diagnostic terminal formula with independently executed GPU states."""
import argparse,hashlib,json,resource,time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_terminal_reference as model
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_projected as r,retimed_holder_program as p


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def run():
    rows=[];g=p.layout()
    for stem in ('retimed_holder_cuda_periods1_v2','retimed_holder_cuda_periods15_v1'):
        manifest=Path('figs/fixed_rule/'+stem+'.json');receipt=json.loads(manifest.read_text());assert receipt['passed']
        artifact=manifest.with_suffix('.npz');assert sha(artifact)==receipt['artifact_sha256']
        with np.load(artifact,allow_pickle=False) as z:
            parents=tuple(r.decode_cell(row) for row in z['initial_upper'])
            for epoch in range(receipt['periods']):
                tick=time.perf_counter();actual=model.terminal(parents);seconds=time.perf_counter()-tick
                np.testing.assert_array_equal(actual['committed_bank'],z['boundary_banks'][epoch])
                np.testing.assert_array_equal(actual['signals'][:,1],z['boundary_right'][epoch]);assert not np.any(actual['signals'][:,0])
                next_parents=r.step_ring(parents)
                expected=np.array([f.encode_cell(r.lift(cell)) for cell in next_parents],dtype=np.uint64)
                np.testing.assert_array_equal(actual['committed_bank'][:,list(g.info)],expected)
                rows.append(dict(execution=str(manifest),period=epoch+1,colonies=len(parents),all_bank_words_match=True,bank_words=actual['committed_bank'].size,seconds=seconds))
                parents=next_parents
    manifest=Path('figs/fixed_rule/retimed_holder_cuda_encoded_repair_v1.json');receipt=json.loads(manifest.read_text());artifact=manifest.with_suffix('.npz')
    assert receipt['passed'] and sha(artifact)==receipt['artifact_sha256']
    with np.load(artifact,allow_pickle=False) as z:
        clean=tuple(r.project(f.decode_cell(row)) for row in z['initial'])
        dirty=tuple(r.project(f.decode_cell(row)) for row in z['faulty_upper_initial'])
        healthy_first=r.step_ring(clean)
        for name,parents,key in (('damaged_first',dirty,'boundary_1_bank'),('healthy_first',clean,'healthy_boundary_1_bank'),('second',healthy_first,'boundary_2_bank')):
            tick=time.perf_counter();actual=model.terminal(parents);seconds=time.perf_counter()-tick
            np.testing.assert_array_equal(actual['committed_bank'],z[key])
            if name!='healthy_first':
                sig=z['boundary_1_signals'] if name=='damaged_first' else z['boundary_2_signals']
                np.testing.assert_array_equal(actual['signals'],sig)
            rows.append(dict(execution=str(manifest),case=name,colonies=len(parents),all_bank_words_match=True,bank_words=actual['committed_bank'].size,seconds=seconds))
        a,b=model.terminal(clean),model.terminal(dirty)
        np.testing.assert_array_equal(a['committed_bank'][:,list(g.info)],b['committed_bank'][:,list(g.info)])
        different=int(np.count_nonzero(a['committed_bank']!=b['committed_bank']));assert different>0
    return dict(passed=True,comparisons=rows,equal_decoded_output_but_different_bank_words=different,scope='Diagnostic terminal-bank formula only. No formula output was installed in a physical executor; no GPU macro-accelerator, all-entry proof or depth-two execution is established.')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError(out)
    start=time.perf_counter();result=run();result.update(seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,descriptor_sha256=f.self_description().digest(),rom_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest(),source_sha256={str(path):sha(path) for path in (Path(__file__),Path(model.__file__))})
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
