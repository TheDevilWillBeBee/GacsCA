"""Source, full spatial-DAG, and native-local audit of the bounded CUDA pilots."""
import argparse,hashlib,json,tarfile,time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import delivery_rule as f,delivery_native as native
from .flag_cuda_stream_compare import expand


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def audit(stem,output):
    stem,output=Path(stem),Path(output)
    if output.exists():raise FileExistsError('preserve evidence')
    started=time.monotonic();root=Path(__file__).resolve().parents[2];x=json.loads(stem.with_suffix('.json').read_text());seen={}
    def sources(prefix,meta):
        assert sha(prefix.with_suffix('.npz'))==meta['artifact_sha256'];assert sha(prefix.with_suffix('.tar.gz'))==meta['archive_sha256']
        with tarfile.open(prefix.with_suffix('.tar.gz')) as archive:
            assert set(archive.getnames())==set(meta['source_sha256'])
            for name,digest in meta['source_sha256'].items():
                assert sha(root/name)==digest==hashlib.sha256(archive.extractfile(name).read()).hexdigest(),name
                if name in seen:assert seen[name]==digest
                seen[name]=digest
    sources(stem,x);cpu=Path(x['reference']);y=json.loads(cpu.with_suffix('.json').read_text());sources(cpu,y)
    assert sha(cpu.with_suffix('.json'))==x['reference_json_sha256'] and y['artifact_sha256']==x['reference_artifact_sha256']
    assert x['passed'] and x['ticks']==y['ticks']==1048576
    assert y['final']['queries']==y['final']['verified_queries']==2084150597
    with np.load(cpu.with_suffix('.npz'),allow_pickle=False) as a:expected=expand(a['nodes'],int(a['root']),y['colonies']*(f.Q//8))
    with np.load(stem.with_suffix('.npz'),allow_pickle=False) as a:actual=a['final_dense']
    np.testing.assert_array_equal(actual,expected)
    # F1 erodes at exactly two sites per step on this particular initial input.
    # Check every bit against its derived prefix, not just aggregate counts.
    t=x['ticks'];word_pos=np.arange(f.Q//64,dtype=np.uint64)*64;length=f.Q-2*t
    expected_f1=np.where(word_pos+64<=length,np.uint64((1<<64)-1),np.uint64(0))
    if length%64:expected_f1[length//64]=(1<<(length%64))-1
    for c in range(y['colonies']):np.testing.assert_array_equal(actual[c*(f.Q//64):(c+1)*(f.Q//64),0],expected_f1 if c<11 or c>=19 else np.zeros_like(expected_f1))
    # Confirm arbitrary stored final neighborhoods against complete native F
    # for a one-step comparison with the existing independent CPU recurrence.
    from gacsca.fixed_rule.flag_cuda import advance
    one=advance(actual,1,age=98*f.Q+t,reference=True)
    total=len(actual)*64;positions={0,total-1}
    for c in range(y['colonies']):positions.update(c*f.Q+a for a in (0,1,4,5,length-5,length-1,length,length+5,f.Q-6,f.Q-1))
    rng=np.random.default_rng(517);positions.update(map(int,rng.integers(0,total,size=128)))
    for pos in positions:
        cells=[]
        for delta in range(-5,6):
            q=(pos+delta)%total;word,bit=divmod(q,64)
            cells.append(f.Cell(address=q%f.Q,age=98*f.Q+t,f1=(int(actual[word,0])>>bit)&1,f2=(int(actual[word,1])>>bit)&1))
        value=native.local_step(tuple(cells));word,bit=divmod(pos,64)
        assert ((int(one[word,0])>>bit)&1,(int(one[word,1])>>bit)&1)==(value.f1,value.f2)
    result=dict(passed=True,verifier_sha256=sha(__file__),source_files=len(seen),all_flags_equal_cpu_DAG=True,all_F1_bits_equal_derived_prefix=True,complete_native_local_comparisons=len(positions),physical_ticks=t,seconds=time.monotonic()-started,artifact_sha256=x['artifact_sha256'],limitation='CPU intermediate proofs were checked online; saved endpoint and source chain audited here, not replayed')
    output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();audit(a.input,a.output)
