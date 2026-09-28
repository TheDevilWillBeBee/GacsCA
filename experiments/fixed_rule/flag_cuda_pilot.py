"""Small isolated GPU timing/parity pilot of literal physical flag evolution.

No substantial suffix run; 4096 ticks of the actual immutable cutoff state.
CPU comparison uses the existing independently checked RLE executor.
"""
import argparse,hashlib,io,json,tarfile,time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule.flag_cuda import advance,libraries
from gacsca.fixed_rule.flag_words import World,WORDS
from gacsca.fixed_rule import delivery_rule as f


def dense(runs):
    result=np.empty((int(runs[-1,0]),2),dtype=np.uint64);start=0
    for end,a,b in runs:result[start:int(end)]=[a,b];start=int(end)
    return result


def execute(stem,source):
    stem=Path(stem);source=Path(source)
    if any(stem.with_suffix(e).exists() for e in ('.json','.npz','.tar.gz')):raise FileExistsError('preserve evidence')
    root=Path(__file__).resolve().parents[2]
    files=[root/'gacsca/fixed_rule'/name for name in ('flag_cuda.py','flag_cuda.cu','flag_cuda_reference.c','flag_words.c','flag_words.py','delivery_rule.py','delivery_native.py')]+[Path(__file__),root/'tests/fixed_rule/test_flag_cuda.py']
    hashes={}
    with tarfile.open(stem.with_suffix('.tar.gz'),'x:gz') as archive:
        for p in files:
            data=p.read_bytes();name=str(p.relative_to(root));hashes[name]=hashlib.sha256(data).hexdigest();info=tarfile.TarInfo(name);info.size=len(data);archive.addfile(info,io.BytesIO(data))
    with np.load(source,allow_pickle=False) as a:runs=a['runs'];right=a['right_signals'];left=a['left_signals']
    initial=dense(runs);libraries();rows=[];last=None
    for ticks in (1,512,4096):
        before=time.monotonic();gpu=advance(initial,ticks);gpu_seconds=time.monotonic()-before
        before=time.monotonic()
        with World(right,left,age=98*f.Q,runs=runs) as world:world.run(ticks);expected=dense(world.runs);cpu_metrics=world.info
        cpu_seconds=time.monotonic()-before
        np.testing.assert_array_equal(gpu,expected);last=gpu
        rows.append(dict(physical_ticks=ticks,gpu_seconds=gpu_seconds,cpu_seconds=cpu_seconds,complete_ring_equal=True,cpu_metrics=cpu_metrics));print(json.dumps(rows[-1]),flush=True)
    # Non-power-of-two complete-colony ring with arbitrary dense flags.
    rng=np.random.default_rng(714);random=rng.bit_generator.random_raw(6*WORDS).reshape(3*WORDS,2)
    np.testing.assert_array_equal(advance(random,17),advance(random,17,reference=True))
    np.savez_compressed(stem.with_suffix('.npz'),initial_runs=runs,final_dense=last)
    result=dict(passed=True,scope=__doc__,input_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),source_sha256=hashes,archive_sha256=hashlib.sha256(stem.with_suffix('.tar.gz').read_bytes()).hexdigest(),artifact_sha256=hashlib.sha256(stem.with_suffix('.npz').read_bytes()).hexdigest(),binary_sha256=[hashlib.sha256(Path(lib._name).read_bytes()).hexdigest() for lib in libraries()],physical_sites=len(initial)*64,rows=rows,three_colony_random_parity=True)
    stem.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();execute(a.output,a.input)
