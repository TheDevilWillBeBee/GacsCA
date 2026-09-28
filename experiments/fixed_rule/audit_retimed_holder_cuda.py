"""Independent saved-state audit of initialized-history GPU evaluation evidence."""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time
import numpy as np
from gacsca.fixed_rule import retimed_holder_core as c,retimed_holder_rule as f
from gacsca.fixed_rule import retimed_holder_program as p,retimed_holder_projected as r
from gacsca.fixed_rule import retimed_holder_cpu_events as cpu,retimed_holder_packed as packed


def validate(data,colonies):
    g=p.layout();n=colonies
    shapes={'initial_data':(n,f.Q),'initial_heads':(n,len(cpu.CONTROL)),'initial_where':(n,),
            'cpu_final_data':(n,f.Q),'cpu_final_heads':(n,len(cpu.CONTROL)),'cpu_final_where':(n,),
            'gpu_bank':(n,g.memory_count+5),'gpu_sparse_rows':(n,64,packed.WORDS),'gpu_counts':(n,),'expected_Hold':(n,f.FIELDS)}
    for key,shape in shapes.items():
        assert key in data,'missing complete state: '+key
        assert data[key].shape==shape and data[key].dtype==np.uint64,key
    assert int(data['initial_age'])==c.RESET_AGES[4]+1
    assert int(data['final_age'])==c.RESET_AGES[4]+g.schedule(*g.stage_ranges[4])[0]
    assert np.all(data['initial_heads'][:,0]==1),'absent active computation'
    assert not np.any(data['cpu_final_heads']) and not np.any(data['gpu_counts'])
    assert not np.any(data['gpu_sparse_rows']),'stale controller or uninitialized padding'
    for name in ('initial_data','cpu_final_data'):
        assert not np.any(data[name][:,g.memory_count:f.Q-5]),'outside represented zero Data domain'
    full=np.concatenate((data['cpu_final_data'][:,:g.memory_count],data['cpu_final_data'][:,f.Q-5:]),axis=1)
    np.testing.assert_array_equal(full,data['gpu_bank'])
    raw=tuple(f.decode_cell(row[list(g.info)]) for row in data['initial_data'])
    for cell in raw:assert r.lift(r.project(cell))==cell,'missing or incorrect upper metadata'
    expected=[]
    program=f.self_description()
    for col in range(n):
        neighbors=tuple(raw[(col+j)%n] for j in f.NEIGHBORHOOD)
        scalar=f.local_step(neighbors)
        described=f.decode_cell(program.evaluate(tuple(word for cell in neighbors for word in f.encode_cell(cell))))
        assert scalar==described,'independent upper oracles disagree'
        expected.append(f.encode_cell(r.lift(r.project(scalar))))
    expected=np.array(expected,dtype=np.uint64)
    np.testing.assert_array_equal(expected,data['expected_Hold'])
    np.testing.assert_array_equal(expected,data['cpu_final_data'][:,list(g.hold)])
    np.testing.assert_array_equal(expected,data['gpu_bank'][:,list(g.hold)])
    return dict(colonies=n,all_Data_and_controllers_match=True,all_raw_Hold_matches_scalar_and_descriptor=True,complete_raw_output_words=n*f.FIELDS,output_sha256=hashlib.sha256(expected.tobytes()).hexdigest())


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--input',required=True);parser.add_argument('--output',required=True);args=parser.parse_args()
    path=Path(args.input);out=Path(args.output)
    if out.exists():raise FileExistsError(out)
    start=time.perf_counter();receipt=json.loads(path.read_text());artifact=path.with_suffix('.npz')
    assert receipt['passed'] and receipt['full_final_evaluation']
    assert hashlib.sha256(artifact.read_bytes()).hexdigest()==receipt['artifact_sha256']
    for name,digest in receipt['source_sha256'].items():assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==digest,name
    assert receipt['descriptor_sha256']==f.self_description().digest()
    assert receipt['rom_sha256']==hashlib.sha256(p.base_rom().tobytes()).hexdigest()
    with np.load(artifact,allow_pickle=False) as data:result=validate(data,receipt['colonies'])
    prior=Path('figs/fixed_rule/retimed_holder_cpu_evaluation_v1.json')
    if receipt['colonies']==15:
        old=json.loads(prior.read_text());assert result['output_sha256']==old['output_sha256'];result['matches_frozen_CPU_Hold']=True
    result.update(passed=True,input=str(path),input_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__':main()
