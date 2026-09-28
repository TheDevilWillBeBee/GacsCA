"""Actual physical META completion times, including endpoint and fallback queries.

Initial state puts the same fixed physical head at a real META instruction; no
host query result is installed. The unchanged local event executor advances it.
"""
import argparse,hashlib,json,resource,time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import small_holder_supported_events as gpu
from gacsca.fixed_rule import small_holder_rule as f,small_holder_projected as r
from gacsca.fixed_rule import small_holder_core as c,small_holder_program as p,small_holder_quotient as q
from experiments.fixed_rule.small_holder_temporal_repair import no_host
from experiments.fixed_rule.small_holder_gather_two_periods import memory


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--all-addresses',action='store_true');parser.add_argument('--output',required=True);args=parser.parse_args();stem=Path(args.output)
    for ext in ('.json','.progress.json','.npz'):
        if stem.with_suffix(ext).exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();g=p.layout();first=g.description_instruction+len(f.self_description().operations)+f.FIELDS
    pcs={selector:next(i for i in range(first,len(g.instructions)) if g.instructions[i].kind==c.META and g.instructions[i].b==selector) for selector in range(7)}
    addresses=tuple(range(f.Q)) if args.all_addresses else tuple(sorted({0,1,7,8,g.memory_count-1,g.memory_count,len(p.base_rom())-2,len(p.base_rom())-1,len(p.base_rom()),len(p.base_rom())+1,f.Q-6,f.Q-5,f.Q-1}))
    parent=r.Cell();parentwords=f.encode_cell(r.lift(parent));infomap={a:i for i,a in enumerate(g.info)}
    poison=0xDEAD123498765432;results=np.empty((7,len(addresses)),dtype=np.uint64);seconds=0.;evaluations=0;observed=[];durations={};checked=0
    for selector,pc in pcs.items():
        op=g.instructions[pc];where=g.memory_count+pc;target=op.a;ticks=4*g.computation_cells+target-where+1;durations[selector]=ticks
        for first_query in range(0,len(addresses),128):
            queries=addresses[first_query:first_query+128];logical={}
            for col,query in enumerate(queries):
                logical[col*f.Q+where]=q.Cell(address=where,age=1,head=1,pc=pc,phase=c.FETCH,ra=999,rb=777,rd=query,value=poison,alu=3)
                logical[col*f.Q+target]=q.Cell(address=target,age=1,data=poison)
            with gpu.World((parent,)*len(queries),age=1,logical=logical) as world:
                if not observed:observed.append(memory())
                tick=time.perf_counter()
                with no_host():metrics=world.batch(ticks-1)
                seconds+=time.perf_counter()-tick;evaluations+=metrics['logical_evaluations']
                cells=world.logical_cells(tuple(col*f.Q+target for col in range(len(queries))))
                expected_values=[]
                for query,cell in zip(queries,cells):
                    value=r.record(query)[c.STATIC[selector]];expected_values.append(value)
                    assert cell==q.Cell(address=target,age=ticks,head=1,pc=pc,phase=c.WRITE,ra=target,rb=selector,rd=target,value=value,alu=3,data=poison),(query,selector,'before',cell)
                tick=time.perf_counter()
                with no_host():metrics=world.batch(1)
                seconds+=time.perf_counter()-tick;evaluations+=metrics['logical_evaluations']
                positions=tuple(col*f.Q+a for col in range(len(queries)) for a in (target,target+1))
                cells=world.logical_cells(positions)
                for col,(query,value) in enumerate(zip(queries,expected_values)):
                    assert cells[2*col]==q.Cell(address=target,age=ticks+1,data=value),(query,selector,'written')
                    next_data=parentwords[infomap[target+1]] if target+1 in infomap else 0
                    assert cells[2*col+1]==q.Cell(address=target+1,age=ticks+1,data=next_data,head=1,pc=pc+1,phase=c.FETCH,ra=target,rb=selector,rd=target,value=value,alu=3),(query,selector,'after',cells[2*col+1])
                    results[selector,first_query+col]=value
                # The old instruction site has no retained controller residue.
                old=world.logical_cells(tuple(col*f.Q+where for col in range(len(queries))))
                assert all(cell==q.Cell(address=where,age=ticks+1) for cell in old)
                checked+=len(queries)
            stem.with_suffix('.progress.json').write_text(json.dumps(dict(status='running',checked=checked,selector=selector,gpu_seconds=seconds))+'\n')
        print(json.dumps(dict(selector=selector,checked=checked,gpu_seconds=seconds)),flush=True)
    np.savez_compressed(stem.with_suffix('.npz'),queries=np.array(addresses,dtype=np.uint64),values=results,pcs=np.array([pcs[i] for i in range(7)],dtype=np.uint64),durations=np.array([durations[i] for i in range(7)],dtype=np.uint64))
    paths=[Path(__file__),Path(gpu.__file__),Path('gacsca/fixed_rule/small_holder_register_events.py'),Path('experiments/fixed_rule/small_holder_temporal_repair.py')]
    result=dict(passed=True,exhaustive_valid_query_domain=args.all_addresses,queries_per_selector=len(addresses),selectors=7,actual_META_completions=checked,exact_duration_by_selector=durations,complete_before_write_after_write_and_old_site_records=True,logical_evaluations=evaluations,gpu_seconds=seconds,seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,observed_process_gpu_mib=observed,descriptor_sha256=f.self_description().digest(),binary_sha256=hashlib.sha256(Path(gpu.library()._name).read_bytes()).hexdigest(),source_sha256={str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in paths},artifact_sha256=hashlib.sha256(stem.with_suffix('.npz').read_bytes()).hexdigest(),limitation='Actual clean isolated META instructions at seven real ROM locations, all stated query addresses; no complete program/period or arbitrary incoming fault history. Duration identity is for these locations and verified finite query domain.')
    stem.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');stem.with_suffix('.progress.json').write_text(json.dumps(dict(status='complete',checked=checked))+'\n');print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__':main()
