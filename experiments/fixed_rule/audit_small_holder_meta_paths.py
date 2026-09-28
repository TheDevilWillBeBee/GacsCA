"""Concrete semantic/provenance audit of META path composition and GPU checkpoints."""
import argparse
import hashlib
import json
import random
import resource
import time
from pathlib import Path

import numpy as np
from gacsca.fixed_rule import small_holder_rule as f, small_holder_native as native
from gacsca.fixed_rule import small_holder_projected as r, small_holder_program as p, small_holder_core as c, small_holder_quotient as q
from gacsca.fixed_rule.wordcode import MASK, arithmetic
from experiments.fixed_rule import certify_small_holder_meta_paths as proof
from experiments.fixed_rule import small_holder_meta_path_execution as execution
from experiments.fixed_rule.audit_small_holder_position_events import evaluate, sha


def check_lookup():
    L=len(p.base_rom());checked=0
    for lo,hi in ((0,L-2),(L-1,L-1),(L,f.Q-6),(f.Q-5,f.Q-1)):
        terms=proof.Words(p.base_rom());query=terms.bounded('query',15,lo,hi)
        outputs=[terms.lookup(query,selector) for selector in range(7)]
        for address in range(lo,hi+1):
            values=[]
            for node in terms.nodes:
                if node[0]=='const':value=node[1]
                elif node[0]=='variable':value=address
                elif node[0]=='rom':
                    a=values[node[1]];selector=node[2]
                    value=int(p.base_rom()[a,selector]) if a<len(p.base_rom()) else c.fallback(a,selector)
                elif node[0]=='not':value=values[node[1]]^MASK
                elif node[0]=='op':value=arithmetic(node[1],values[node[2]],values[node[3]])
                elif node[0]=='modadd':value=(values[node[1]]+node[2])&((1<<node[3])-1)
                else:raise AssertionError(node)
                values.append(value)
            expected=r.record(address)
            assert tuple(values[x] for x in outputs)==tuple(expected[name] for name in c.STATIC)
            checked+=7
    return checked


def audit_last_leaf():
    rng=random.Random(2026092691);count=0
    for interval in proof.clock.regular_intervals():
        terms,raw=proof.leaf_prepare(proof.LAST_LEFT,interval)
        old=[tuple(raw(pos+j) for j in f.NEIGHBORHOOD) for pos in range(-4,5)]
        wanted=[raw(pos,after=True) for pos in range(-4,5)]
        for age,mode in ((interval[0],'zero'),(interval[1],'ones'),(rng.randint(*interval),'random')):
            assignments={node[1]:0 if mode=='zero' else (1<<node[2])-1 if mode=='ones' else rng.getrandbits(node[2]) for node in terms.nodes if node[0]=='variable'}
            assignments['physical_age']=age;values=evaluate(terms,assignments)
            for rows,want in zip(old,wanted):
                neighborhood=tuple(f.decode_cell(tuple(values[x] for x in row)) for row in rows)
                scalar=f.local_step(neighborhood)
                assert scalar==native.local_step(neighborhood)
                assert f.encode_cell(scalar)==tuple(values[x] for x in want)
                count+=1
    return count


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--certificate',required=True);parser.add_argument('--execution',required=True);parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();certificate=json.loads(Path(args.certificate).read_text());stem=Path(args.execution);run=json.loads(stem.with_suffix('.json').read_text())
    assert certificate['passed'] and run['passed']
    assert certificate['source_sha256']==sha(proof.__file__)
    assert certificate['descriptor_sha256']==run['descriptor_sha256']==f.self_description().digest()
    for path,wanted in run['source_sha256'].items():assert sha(path)==wanted,path
    assert run['artifact_sha256']==sha(stem.with_suffix('.npz'))
    expected_pcs=tuple(i for i,op in enumerate(p.layout().instructions) if op.kind==c.META)
    domains=tuple(map(tuple,certificate['query_domains']))
    assert {(row['pc'],tuple(row['query_domain'])) for row in certificate['paths']}=={(pc,domain) for pc in expected_pcs for domain in domains}
    assert domains==((0,len(p.base_rom())-2),(len(p.base_rom())-1,len(p.base_rom())-1),(len(p.base_rom()),f.Q-6),(f.Q-5,f.Q-1))
    lookups=check_lookup();extra_native=audit_last_leaf();native_boundaries=0;head_checks=0;probe_checks=0;probe_hash=hashlib.sha256()
    with np.load(stem.with_suffix('.npz'),allow_pickle=False) as saved:
        pcs=tuple(map(int,saved['pcs']));queries=tuple(map(int,saved['queries']));starts=tuple(map(int,saved['start_ages']))
        assert pcs==((expected_pcs[0],expected_pcs[-1]) if run['pilot'] else expected_pcs)
        for i,pc in enumerate(pcs):
            op=p.layout().instructions[pc];where=p.layout().memory_count+pc
            times=execution.frame_times(where,op.a,len(p.base_rom()))
            assert tuple(map(int,saved['frame_times'][i]))==times
            assert all(row['duration']==times[-1] for row in certificate['paths'] if row['pc']==pc)
            for j,age in enumerate(starts):
                frames=[]
                for frame in range(6):
                    cell,head=execution.expected_logical(pc,queries,age,frame);frames.append((cell,head))
                    wanted=q.array_from_cells(tuple(cell(col*f.Q+head) for col in range(len(queries))))
                    np.testing.assert_array_equal(saved['heads'][i,j,frame],wanted);head_checks+=len(queries)
                    probe=tuple((col*f.Q+a)%(len(queries)*f.Q) for col in range(len(queries)) for a in (head-2,head,head+2,where,op.a))
                    for position in probe:
                        probe_hash.update(np.array(execution.expected_raw(cell,position),dtype=np.uint64).tobytes());probe_checks+=1
                # Independent full-rule boundary checks on one rotating query per instruction/clock.
                col=(i+j)%len(queries)
                for before,after in ((0,1),(2,3),(4,5)):
                    old,oldhead=frames[before];new,newhead=frames[after]
                    assert times[after]-times[before]==1
                    for address in (oldhead-2,oldhead,oldhead+2,newhead):
                        pos=col*f.Q+address
                        neighborhood=tuple(f.decode_cell(execution.expected_raw(old,pos+d)) for d in f.NEIGHBORHOOD)
                        scalar=f.local_step(neighborhood)
                        assert scalar==native.local_step(neighborhood)
                        assert f.encode_cell(scalar)==execution.expected_raw(new,pos),(pc,age,before,address)
                        native_boundaries+=1
            if i%14==0:print(json.dumps(dict(instructions_audited=i+1,head_records=head_checks)),flush=True)
    assert probe_checks==run['complete_raw_probe_records_checked']
    assert probe_hash.hexdigest()==run['raw_probe_sha256']
    paths=[Path(__file__),Path(proof.__file__),Path(execution.__file__),Path('tests/fixed_rule/test_small_holder_meta_paths.py')]
    result=dict(passed=True,metadata_lookup_values_checked=lookups,last_marked_left_leaf_full_native_outputs=extra_native,
                reflection_and_write_full_native_outputs=native_boundaries,saved_complete_head_records_checked=head_checks,
                expected_full_raw_probe_records_rehashed=probe_checks,raw_probe_sha256=probe_hash.hexdigest(),
                certificate_sha256=sha(args.certificate),execution_manifest_sha256=sha(stem.with_suffix('.json')),execution_artifact_sha256=sha(stem.with_suffix('.npz')),
                source_sha256={str(path):sha(path) for path in paths},seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                limitation='Concrete ROM/leaf/native-boundary semantics audit, saved head comparisons and expected-probe digest reconstruction. GPU probe assertions are in the hashed driver; this does not replay every physical microstep or establish a whole period.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
