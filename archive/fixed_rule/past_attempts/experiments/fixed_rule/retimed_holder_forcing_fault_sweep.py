"""Fault pulses on actual executed forcing/clearing/controller checkpoints."""
import argparse,json,random,resource,time
from dataclasses import replace
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_literal_cone as cone,retimed_holder_rule as f,retimed_holder_projected as r,retimed_holder_program as p
from gacsca.fixed_rule import retimed_holder_resident_general as general,retimed_holder_cuda_general_snapshot as snapshots
from experiments.fixed_rule.run_retimed_holder_cpu_periods import parents
from experiments.fixed_rule.retimed_holder_cuda_encoded_repair import forbidden,raw
from experiments.fixed_rule.run_retimed_holder_streamed_repair import sha


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);parser.add_argument('--ticks',type=int,default=12);args=parser.parse_args();out=Path(args.output);artifact=out.with_suffix('.npz')
    if out.exists() or artifact.exists():raise FileExistsError(out)
    started=time.perf_counter();seed=2026092708;rng=random.Random(seed);saved={};results=[];contexts=[];g=p.layout()
    with general.World(parents(1),device_budget=32*1024**2) as world:
        for context,age in enumerate((f.WF_START+100,f.WF_END+100,f.RESET_AGES[4]+100)):
            with forbidden():world.advance(age-world.time,extra_device_budget=32*1024**2)
            snapshot=snapshots.snapshot(world)
            for key,value in snapshot.items():saved[f'context{context}_'+key]=value
            first=np.flatnonzero(np.unpackbits(np.ascontiguousarray(snapshot['flags'][:,0]).view(np.uint8),bitorder='little'))
            anchors=sorted({0,3,f.Q-3,f.Q-1,*( (int(first[0])-1,int(first[0])) if len(first) else (99,100) )})
            positions=sorted({pos%f.Q for anchor in anchors for pos in range(anchor-14*args.ticks,anchor+14*args.ticks+2)})
            values=raw(world.physical_cells(positions));table={pos:row for pos,row in zip(positions,values)}
            saved[f'context{context}_positions']=np.array(positions,dtype=np.uint64);saved[f'context{context}_raw']=values
            def initial(requested):return np.array([table[int(pos)%f.Q] for pos in requested],dtype=np.uint64)
            contexts.append(dict(age=age,flag1_sites=len(first),signals=snapshot['signals'].tolist(),anchors=anchors,initial_raw_cells=len(positions)))
            for anchor in anchors:
                for count in (1,2):
                    for kind in ('address','signal','full','ones'):
                        locations=tuple(anchor+d for d in range(count));old=initial(locations);changes={}
                        for pos,row in zip(locations,old):
                            cell=r.project(f.decode_cell(row))
                            if kind=='address':fields=dict(address=(cell.address+f.Q//2)%f.Q)
                            elif kind=='signal':fields=dict(signal=cell.signal^31)
                            elif kind=='full':fields={name:rng.getrandbits(width) for name,width in r.SCHEMA}
                            else:fields={name:(1<<width)-1 for name,width in r.SCHEMA}
                            changes[pos]=replace(cell,**fields)
                        result=cone.evolve(initial,changes,size=f.Q,ticks=args.ticks);index=len(results);prefix=f'case{index}'
                        changed=np.flatnonzero(np.any(result['actual']!=result['healthy'],axis=1))
                        saved[prefix+'_positions']=np.array(locations,dtype=np.int64);saved[prefix+'_before']=old
                        saved[prefix+'_injected']=np.array([f.encode_cell(r.lift(changes[pos])) for pos in locations],dtype=np.uint64)
                        saved[prefix+'_last_positions']=(changed+result['left'])%f.Q;saved[prefix+'_last_actual']=result['actual'][changed];saved[prefix+'_last_healthy']=result['healthy'][changed]
                        results.append(dict(index=index,context=context,age=age,anchor=anchor,site_count=count,kind=kind,rejoined=result['rejoined'],ticks=result['ticks'],trace=result['trace']))
            print(json.dumps(dict(context=context,age=age,cases=len(results),not_rejoined=sum(not x['rejoined'] for x in results),seconds=time.perf_counter()-started)),flush=True)
    np.savez_compressed(artifact,**saved)
    result=dict(passed=True,seed=seed,deadline=args.ticks,contexts=contexts,cases=results,all_rejoined=all(x['rejoined'] for x in results),nonrejoining_cases_preserved=True,artifact_sha256=sha(artifact),source_sha256={str(x):sha(x) for x in (Path(__file__),Path(cone.__file__),Path(general.__file__))},descriptor_sha256=f.self_description().digest(),seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,scope='Exact literal physical fault cones initialized from actually executed forcing, clearing and active-controller checkpoints. Non-rejoining cases are retained and never passed to a noiseless endpoint shortcut. Finite deadline is not an asymptotic failure claim.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2),flush=True)

if __name__=='__main__':main()
