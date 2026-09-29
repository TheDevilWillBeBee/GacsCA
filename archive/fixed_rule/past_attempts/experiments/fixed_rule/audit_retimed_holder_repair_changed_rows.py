"""Recompute complete scratch rows selected from actual repair differences."""
import argparse,hashlib,json,resource,time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_projected as r,retimed_holder_terminal_dag as dag,retimed_holder_endpoint_image_array as image


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError(out)
    started=time.perf_counter();prior=Path('figs/fixed_rule/retimed_holder_streamed_repair_audit_v1.json');audit=json.loads(prior.read_text());assert audit['passed']
    receipts={}
    for name in ('healthy','two'):
        path=Path(f'figs/fixed_rule/retimed_holder_streamed_repair_{name}_v1.json');assert sha(path)==audit['references'][str(path)];receipts[name]=json.loads(path.read_text())
        assert sha(receipts[name]['small_artifact_path'])==receipts[name]['small_artifact_sha256']
    rows=[]
    with np.load(receipts['healthy']['small_artifact_path'],allow_pickle=False) as h,np.load(receipts['two']['small_artifact_path'],allow_pickle=False) as d:
        ht,dt=h['period1_tile_hashes'],d['period1_tile_hashes'];different=np.flatnonzero(ht!=dt);assert len(different)>0
        hb=np.load(receipts['healthy']['period_results'][0]['bank_path'],mmap_mode='r');db=np.load(receipts['two']['period_results'][0]['bank_path'],mmap_mode='r')
        selected=[]
        for at in np.linspace(0,len(different)-1,min(8,len(different)),dtype=int):
            tile=int(different[at]);start=tile*128;a,b=hb[start:start+128],db[start:start+128]
            assert hashlib.sha256(a.tobytes()).hexdigest()==ht[tile] and hashlib.sha256(b.tobytes()).hexdigest()==dt[tile]
            counts=np.count_nonzero(a!=b,axis=1);pos=start+int(np.argmax(counts));assert counts[pos-start]>0;selected.append(pos)
        for name,z,bank in (('healthy',h,hb),('two',d,db)):
            top=tuple(r.project(f.decode_cell(row)) for row in z['period1_input_top']);terminal=dag.terminal(top)
            raw=image.render(terminal['precommit_bank'],terminal['signals'],f.U-1)
            for pos in selected:
                neighbors=tuple(r.project(f.decode_cell(raw[(pos+offset)%f.Q])) for offset in f.NEIGHBORHOOD)
                expected=dag.terminal(neighbors)['committed_bank'][7]
                np.testing.assert_array_equal(bank[pos],expected)
                rows.append(dict(case=name,physical_colony=pos,complete_bank_words=len(expected),actual_pair_different_words=int(np.count_nonzero(hb[pos]!=db[pos]))))
            del raw
    result=dict(passed=True,changed_tiles=int(len(different)),selected_changed_colonies=selected,complete_rows_recomputed=rows,seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,prior_full_audit=str(prior),prior_full_audit_sha256=sha(prior),source_sha256={str(path):sha(path) for path in (Path(__file__),Path(image.__file__),Path(dag.__file__))},scope='Independent full-scratch recomputation at colonies selected from actual healthy/damaged differences; supplements the full decoded-field and bank-rejoin audit.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
