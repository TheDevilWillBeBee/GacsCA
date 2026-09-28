"""Seeded full-field physical pulses at a complete real depth-two checkpoint."""
import argparse,json,random,resource,time
from dataclasses import replace
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_literal_cone as cone,retimed_holder_rule as f,retimed_holder_projected as r,retimed_holder_program as p
from experiments.fixed_rule.run_retimed_holder_streamed_repair import sha


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);parser.add_argument('--ticks',type=int,default=12);args=parser.parse_args();out=Path(args.output);artifact=out.with_suffix('.npz')
    if out.exists() or artifact.exists():raise FileExistsError(out)
    started=time.perf_counter();basepath=Path('figs/fixed_rule/retimed_holder_timed_depth2_checkpoint_v1.json');base=json.loads(basepath.read_text());assert base['passed']
    bankpath=base['bank_paths'][0];assert sha(bankpath)==base['bank_sha256'][bankpath]
    assert sha(base['small_artifact'])==base['small_sha256']
    bank=np.load(bankpath,mmap_mode='r');g=p.layout()
    with np.load(base['small_artifact'],allow_pickle=False) as z:signals=z['step1_signals']
    image=cone.BankImage(bank,signals);seed=2026092707;rng=random.Random(seed);saved={};results=[]
    anchors=(0,3,5,g.info[f.COL['s2_rb']],g.memory_count-1,g.computation_cells-1,f.Q-3,f.Q-1)
    kinds=('address','age','flags','signal','procedure','full','ones')
    for anchor in anchors:
        for count in (1,2):
            for kind in kinds:
                repeats=4 if kind=='full' else 1
                for repeat in range(repeats):
                    positions=tuple(9566*f.Q+anchor+d for d in range(count));old=image.cells(positions);changes={}
                    for pos,row in zip(positions,old):
                        cell=r.project(f.decode_cell(row));values={}
                        if kind=='address':values['address']=(cell.address+f.Q//2)%f.Q
                        elif kind=='age':values['age']=(1<<32)-1
                        elif kind=='flags':values={name:1 for name,_ in r.SCHEMA if name.startswith('w') or name in ('f1','f2')}
                        elif kind=='signal':values['signal']=cell.signal^31
                        elif kind=='procedure':values={name:rng.getrandbits(width) for name,width in r.SCHEMA if name.startswith('s') and name!='signal'}
                        elif kind=='full':values={name:rng.getrandbits(width) for name,width in r.SCHEMA}
                        elif kind=='ones':values={name:(1<<width)-1 for name,width in r.SCHEMA}
                        changes[pos]=replace(cell,**values)
                    result=cone.evolve(image.cells,changes,size=image.size,ticks=args.ticks)
                    index=len(results);prefix=f'case{index}';changed=np.flatnonzero(np.any(result['actual']!=result['healthy'],axis=1))
                    saved[prefix+'_positions']=np.array(positions,dtype=np.uint64);saved[prefix+'_before']=old
                    saved[prefix+'_injected']=np.array([f.encode_cell(r.lift(changes[pos])) for pos in positions],dtype=np.uint64)
                    saved[prefix+'_last_positions']=(changed+result['left']).astype(np.uint64);saved[prefix+'_last_actual']=result['actual'][changed];saved[prefix+'_last_healthy']=result['healthy'][changed]
                    row=dict(index=index,anchor=anchor,site_count=count,kind=kind,repeat=repeat,rejoined=result['rejoined'],ticks=result['ticks'],trace=result['trace'])
                    results.append(row)
            print(json.dumps(dict(anchor=anchor,site_count=count,cases=len(results),not_rejoined=sum(not x['rejoined'] for x in results),seconds=time.perf_counter()-started)),flush=True)
    np.savez_compressed(artifact,**saved)
    summary={kind:dict(cases=sum(x['kind']==kind for x in results),rejoined=sum(x['kind']==kind and x['rejoined'] for x in results)) for kind in kinds}
    receipt=dict(passed=True,seed=seed,deadline=args.ticks,cases=results,summary=summary,all_rejoined=all(x['rejoined'] for x in results),nonrejoining_cases_preserved=True,checkpoint_receipt_sha256=sha(basepath),artifact_sha256=sha(artifact),source_sha256={str(x):sha(x) for x in (Path(__file__),Path(cone.__file__))},descriptor_sha256=f.self_description().digest(),seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,scope='Selected and seeded one/two-site full physical pulses near bottom colony boundaries and Info during a real middle computation. Exact literal G evolution; non-rejoin by deadline is not an asymptotic failure theorem. No endpoint shortcut used for any surviving defect.')
    out.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k!='cases'},indent=2),flush=True)

if __name__=='__main__':main()
