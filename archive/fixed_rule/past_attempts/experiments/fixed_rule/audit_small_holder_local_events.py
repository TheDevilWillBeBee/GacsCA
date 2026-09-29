"""Concrete independent audit of full physical event identities and META timing."""
import argparse,hashlib,json,random,resource,time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import small_holder_rule as f,small_holder_native as native
from gacsca.fixed_rule import small_holder_program as p,small_holder_projected as r,small_holder_core as c
from gacsca.fixed_rule.wordcode import MASK,arithmetic
from experiments.fixed_rule.certify_small_holder_local_events import cases,prepare


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--certificate',required=True);parser.add_argument('--timing',required=True);parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();certificate=json.loads(Path(args.certificate).read_text());stem=Path(args.timing);timing=json.loads(stem.with_suffix('.json').read_text())
    assert certificate['passed'] and timing['passed']
    assert sha('experiments/fixed_rule/certify_small_holder_local_events.py')==certificate['source_sha256']
    for path,wanted in timing['source_sha256'].items():assert sha(path)==wanted,path
    assert sha(stem.with_suffix('.npz'))==timing['artifact_sha256']
    rng=random.Random(2026092651);outputs=0;digest=hashlib.sha256()
    for event in cases():
        terms,raw=prepare(event);positions=range(event['at']-4,event['at']+5)
        old=[tuple(raw(pos+j) for j in f.NEIGHBORHOOD) for pos in positions];expected=[raw(pos,after=True) for pos in positions]
        for mode in ('zero','ones','random'):
            values=[]
            for node in terms.nodes:
                if node[0]=='const':value=node[1]
                elif node[0]=='variable':value=0 if mode=='zero' else (1<<node[2])-1 if mode=='ones' else rng.getrandbits(node[2])
                elif node[0]=='not':value=values[node[1]]^MASK
                elif node[0]=='op':value=arithmetic(node[1],values[node[2]],values[node[3]])
                else:raise AssertionError('unexpected symbolic primitive')
                values.append(value)
            for rows,want in zip(old,expected):
                neighborhood=tuple(f.decode_cell(tuple(values[i] for i in row)) for row in rows)
                scalar=f.local_step(neighborhood);machine=native.local_step(neighborhood)
                assert scalar==machine
                wanted=tuple(values[i] for i in want)
                assert f.encode_cell(scalar)==wanted,(event['name'],mode)
                digest.update(np.array(wanted,dtype=np.uint64).tobytes());outputs+=1
    with np.load(stem.with_suffix('.npz'),allow_pickle=False) as saved:
        addresses=tuple(map(int,saved['queries']))
        if timing['exhaustive_valid_query_domain']:assert addresses==tuple(range(f.Q))
        for selector,pc in enumerate(saved['pcs']):
            op=p.layout().instructions[int(pc)];position=p.layout().memory_count+int(pc)
            assert op.kind==c.META and op.b==selector
            duration=4*p.layout().computation_cells+op.a-position+1
            assert duration==int(saved['durations'][selector])==timing['exact_duration_by_selector'][str(selector)]
            want=np.array([r.record(a)[c.STATIC[selector]] for a in addresses],dtype=np.uint64)
            np.testing.assert_array_equal(saved['values'][selector],want)
    paths=[Path(__file__),Path('experiments/fixed_rule/certify_small_holder_local_events.py'),Path('tests/fixed_rule/test_small_holder_local_events.py')]
    result=dict(passed=True,complete_physical_outputs_checked=outputs,raw_words_per_output=f.FIELDS,symbolic_patterns=['all zero','all width-limited ones','seeded random'],output_sha256=digest.hexdigest(),META_query_results_checked=timing['actual_META_completions'],all_META_durations_recomputed=True,certificate_sha256=sha(args.certificate),timing_manifest_sha256=sha(stem.with_suffix('.json')),timing_artifact_sha256=sha(stem.with_suffix('.npz')),source_sha256={str(path):sha(path) for path in paths},seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,limitation='Independent event-term semantics and saved META-value/duration audit. Exact physical write-boundary observations are runtime assertions in the hashed GPU driver; this audit does not replay all GPU micro-trajectories or prove a whole period.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
