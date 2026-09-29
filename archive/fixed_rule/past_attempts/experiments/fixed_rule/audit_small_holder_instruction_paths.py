"""Audit ordinary path catalog, full native leaves and physical checkpoints."""
import argparse
import hashlib
import json
import random
import resource
import time
from pathlib import Path

import numpy as np
from gacsca.fixed_rule import small_holder_rule as f, small_holder_native as native, small_holder_program as p, small_holder_core as c, small_holder_quotient as q
from gacsca.fixed_rule.wordcode import LIT
from experiments.fixed_rule import certify_small_holder_instruction_paths as proof
from experiments.fixed_rule import small_holder_instruction_path_execution as execution
from experiments.fixed_rule.audit_small_holder_position_events import evaluate,sha


def check_catalog(certificate):
    seen=set();L=len(p.base_rom());count=0
    for pc,kind,third,duration,head,segments in certificate['rows']:
        op=p.layout().instructions[pc];assert kind==op.kind and kind!=c.META
        assert (pc,third) not in seen;seen.add((pc,third))
        targets=(op.a,op.b,op.d) if kind in c.ALU_KINDS else (op.d,) if kind==LIT else (op.a,) if kind in (c.SEND,c.LOAD) else ()
        position=p.layout().memory_count+pc+1;elapsed=1
        for target in targets:
            assert 0<=target<p.layout().memory_count
            travel=target-position if target>=position else (L-1-position)+1+(L-1)+1+target
            assert travel>=0;elapsed+=travel+1;position=target+1
        assert elapsed==duration
        if kind==c.HALT or (kind==c.IF_THIRD and not third):position=-1
        assert head==position and segments>=1;count+=1
    expected={(pc,third) for pc,op in enumerate(p.layout().instructions) if op.kind!=c.META for third in ((0,1) if op.kind==c.IF_THIRD else (0,))}
    assert seen==expected and count==certificate['path_count']
    return count


def audit_leaves():
    rng=random.Random(2026092702);count=0
    for key in proof.nonmemory_cases():
        for interval in proof.clock.regular_intervals():
            terms,raw=proof.leaf_prepare(key,interval)
            old=[tuple(raw(pos+j) for j in f.NEIGHBORHOOD) for pos in range(-4,5)];want=[raw(pos,after=True) for pos in range(-4,5)]
            for age,mode in ((interval[0],'zero'),(interval[1],'ones'),(rng.randint(*interval),'random')):
                assignments={node[1]:0 if mode=='zero' else (1<<node[2])-1 if mode=='ones' else rng.getrandbits(node[2]) for node in terms.nodes if node[0]=='variable'}
                assignments.update(physical_age=age,meta_0_kind=1 if mode=='zero' else 15 if mode=='ones' else rng.randrange(1,16))
                values=evaluate(terms,assignments);assert terms.hypotheses_hold(values)
                for rows,wanted in zip(old,want):
                    neighbors=tuple(f.decode_cell(tuple(values[x] for x in row)) for row in rows)
                    result=f.local_step(neighbors);assert result==native.local_step(neighbors)
                    assert f.encode_cell(result)==tuple(values[x] for x in wanted);count+=1
    return count


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--certificate',required=True);parser.add_argument('--execution',required=True);parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();certificate=json.loads(Path(args.certificate).read_text());stem=Path(args.execution);run=json.loads(stem.with_suffix('.json').read_text())
    assert certificate['passed'] and run['passed'] and certificate['source_sha256']==sha(proof.__file__)
    assert certificate['descriptor_sha256']==run['descriptor_sha256']==f.self_description().digest()
    for path,wanted in run['source_sha256'].items():assert sha(path)==wanted,path
    assert sha(stem.with_suffix('.npz'))==run['artifact_sha256']
    catalog=check_catalog(certificate);leaves=audit_leaves();records=0;boundaries=0;digest=hashlib.sha256()
    durations={(row[0],row[2]):row[3] for row in certificate['rows']}
    with np.load(stem.with_suffix('.npz'),allow_pickle=False) as saved:
        if not run['pilot']:assert tuple(map(int,saved['pcs']))==execution.selected_pcs()
        for case_number,case in enumerate(run['cases']):
            pc,age=case['pc'],case['start_age'];trace=execution.frames(pc,age)
            models={frame['time']:execution.logical_model(pc,age,frame) for frame in trace}
            assert case['checkpoint_times']==[frame['time'] for frame in trace]
            branch=int(p.layout().instructions[pc].kind==c.IF_THIRD and c.RESET_AGES[2]<=age<c.ACTIVE_ENDS[2])
            assert case['duration']==trace[-1]['time']==durations[pc,branch]
            begin=case['records_start'];end=begin+case['records_count']
            for row,index in zip(saved['records'][begin:end],saved['indices'][begin:end]):
                ipc,iage,elapsed,col,address=map(int,index);assert (ipc,iage)==(pc,age)
                model=models[elapsed];position=col*f.Q+address
                assert tuple(map(int,row))==q.encode_cell(model(position))
                digest.update(np.array(execution.expected_raw(model,position),dtype=np.uint64).tobytes());records+=1
            col=case_number%6
            for before,after in zip(trace,trace[1:]):
                if after['time']-before['time']!=1:continue
                old=models[before['time']];new=models[after['time']]
                oldhead=before['head'];assert oldhead is not None
                for address in (oldhead-2,oldhead,oldhead+2,oldhead if after['head'] is None else after['head']):
                    position=col*f.Q+address
                    neighborhood=tuple(f.decode_cell(execution.expected_raw(old,position+j)) for j in f.NEIGHBORHOOD)
                    result=f.local_step(neighborhood);assert result==native.local_step(neighborhood)
                    assert f.encode_cell(result)==execution.expected_raw(new,position),(pc,age,before['time'],address)
                    boundaries+=1
    assert records==run['complete_logical_records_saved']==run['complete_raw_probe_records_checked']
    assert digest.hexdigest()==run['raw_probe_sha256']
    paths=[Path(__file__),Path(proof.__file__),Path(execution.__file__),Path('tests/fixed_rule/test_small_holder_instruction_paths.py')]
    result=dict(passed=True,actual_ROM_catalog_paths_checked=catalog,new_leaf_full_scalar_native_outputs=leaves,checkpoint_boundary_full_scalar_native_outputs=boundaries,
                saved_complete_logical_records_checked=records,expected_raw_probe_records_rehashed=records,raw_probe_sha256=digest.hexdigest(),
                certificate_sha256=sha(args.certificate),execution_manifest_sha256=sha(stem.with_suffix('.json')),execution_artifact_sha256=sha(stem.with_suffix('.npz')),
                source_sha256={str(path):sha(path) for path in paths},seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                limitation='Catalog and concrete semantic/checkpoint audit. GPU probe checks are assertions in the hashed driver; no full microstep replay, packet continuation, whole period or nested/noisy theorem.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
