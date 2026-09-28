"""Bounded printed-flag probe for a certified stationary suffix.

Starts from the audited million-tick physical state, evolves the same physical
rule on CUDA until Q/2+64 ticks after cutoff, and tests complete-ring stationarity
using the independent CPU packed implementation. No stationarity is assumed.
"""
import argparse,hashlib,io,json,tarfile,time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import delivery_rule as f
from gacsca.fixed_rule.flag_cuda_fixed import advance,libraries


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def execute(stem,source):
    stem,source=Path(stem),Path(source)
    if any(stem.with_suffix(e).exists() for e in ('.json','.npz','.tar.gz')):raise FileExistsError('preserve evidence')
    x=json.loads(source.with_suffix('.json').read_text());assert x['passed'] and x['ticks']==1048576 and sha(source.with_suffix('.npz'))==x['artifact_sha256']
    root=Path(__file__).resolve().parents[2]
    files=[Path(__file__),*[root/'gacsca/fixed_rule'/n for n in ('flag_cuda_fixed.py','flag_cuda_fixed.cu','flag_cuda_reference.c','flag_words.c','flag_words.py')],root/'tests/fixed_rule/test_flag_cuda_fixed.py'];hashes={}
    with tarfile.open(stem.with_suffix('.tar.gz'),'x:gz') as archive:
        for p in files:
            data=p.read_bytes();name=str(p.relative_to(root));hashes[name]=sha(p);info=tarfile.TarInfo(name);info.size=len(data);archive.addfile(info,io.BytesIO(data))
    with np.load(source.with_suffix('.npz'),allow_pickle=False) as a:initial=a['final_dense']
    libraries();advance(initial,0);target=f.Q//2+64;elapsed=x['ticks'];state=initial;records=[];started=time.monotonic()
    while elapsed<target:
        ticks=min(1048576,target-elapsed);before=time.monotonic();state=advance(state,ticks,age=98*f.Q+elapsed);elapsed+=ticks
        row=dict(ticks_after_cutoff=elapsed,gpu_seconds=time.monotonic()-before);records.append(row);print(json.dumps(row),flush=True)
        np.savez_compressed(stem.with_suffix('.checkpoint.npz'),final_dense=state,ticks=np.array(elapsed,dtype=np.uint64))
    before=time.monotonic();one=advance(state,1,age=98*f.Q+target,reference=True);equal=np.array_equal(one,state);check_seconds=time.monotonic()-before
    counts=[int(np.unpackbits(state[:,k].copy().view(np.uint8)).sum()) for k in range(2)]
    np.savez_compressed(stem.with_suffix('.npz'),final_dense=state,one_step=one)
    result=dict(scope=__doc__,ticks_after_cutoff=target,stationary=equal,cpu_full_ring_check_seconds=check_seconds,counts=counts,records=records,seconds=time.monotonic()-started,source=str(source),input_json_sha256=sha(source.with_suffix('.json')),input_artifact_sha256=x['artifact_sha256'],source_sha256=hashes,artifact_sha256=sha(stem.with_suffix('.npz')),archive_sha256=sha(stem.with_suffix('.tar.gz')),binary_sha256=[sha(lib._name) for lib in libraries()],certified_quiet_ticks_to_U=(f.U-98*f.Q-target if equal else 0),limitation='physical flags only; no independent GPU trajectory replay beyond the inherited million-tick comparison; complete controller composition is separate')
    stem.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();execute(a.output,a.input)
