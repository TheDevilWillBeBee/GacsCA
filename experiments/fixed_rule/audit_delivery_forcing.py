"""Audit complete stored-state composition and whole-ring flags at 98Q.

The long physical replay is recorded by delivery_forcing_execution. This audit
checks its representation/provenance and independently recomputes the controller
quotient; it does not claim an independent second flag trajectory algorithm.
"""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile
import time
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import delivery_rule as f,delivery_projected as r,delivery_program as p
from gacsca.fixed_rule.delivery_control_world import World
from gacsca.fixed_rule.wordcode import Program


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def audit(stem,output):
    stem,output=Path(stem),Path(output)
    if output.exists():raise FileExistsError('preserve prior audit')
    started=time.monotonic();root=Path(__file__).resolve().parents[2];x=json.loads(stem.with_suffix('.json').read_text())
    assert sha(stem.with_suffix('.npz'))==x['artifact_sha256'] and sha(stem.with_suffix('.tar.gz'))==x['archive_sha256']
    with tarfile.open(stem.with_suffix('.tar.gz')) as archive:
        assert set(archive.getnames())==set(x['source_sha256'])
        for name,digest in x['source_sha256'].items():assert sha(root/name)==digest==hashlib.sha256(archive.extractfile(name).read()).hexdigest(),name
    assert x['rule']==json.loads(json.dumps(r.identity()))
    prefix=Path(x['input_prefix']);assert sha(prefix.with_suffix('.npz'))==x['input_artifact_sha256']
    with np.load(prefix.with_suffix('.npz'),allow_pickle=False) as a:initial=a['stored_final'];old=a['initial_lifted'];top=a['initial_top']
    assert sha(x['checkpoint'])==x['checkpoint_sha256']
    with np.load(x['checkpoint'],allow_pickle=False) as a:cutoff={name:a[name] for name in a.files}
    with np.load(stem.with_suffix('.npz'),allow_pickle=False) as a:saved={name:a[name] for name in a.files}
    g=p.layout();n=len(old);ticks=2*f.Q+1
    assert x['start_age']==96*f.Q-1 and x['final_age']==98*f.Q and x['physical_ticks']==ticks
    assert x['physical_sites']==n*f.Q
    np.testing.assert_array_equal(saved['flags_t0'],np.array([(n*f.Q//64,0,0)],dtype=np.uint64))
    runs=saved['flags_t'+str(ticks)];np.testing.assert_array_equal(runs,cutoff['runs'])
    for name in ('left_signals','right_signals'):np.testing.assert_array_equal(saved[name],cutoff[name])
    assert runs.dtype==np.uint64 and runs.ndim==2 and runs.shape[1]==3
    assert all(int(a)<int(b) for a,b in zip([0,*runs[:-1,0]],runs[:,0])) and int(runs[-1,0])==n*f.Q//64
    stored=saved['stored_final'];expected=saved['controller_final'].copy()
    assert stored.shape==expected.shape==(n*(g.computation_cells+5),len(r.SCHEMA))
    for name,width in r.SCHEMA:
        if width<64:assert np.all(stored[:,r.COL[name]]<1<<width)
    addresses=[*range(g.computation_cells),*range(f.Q-5,f.Q)]
    # Walk the physical RLE independently, rather than the executor's search
    # and vectorized shifting, and verify every explicitly stored physical bit.
    row=0;counts=[0,0];begin=0
    for end,a,b in map(lambda v:tuple(map(int,v)),runs):
        counts[0]+=(end-begin)*a.bit_count();counts[1]+=(end-begin)*b.bit_count();begin=end
    for c in range(n):
        for j,address in enumerate(addresses):
            position=c*f.Q+address
            while int(runs[row,0])*64<=position:row+=1
            for k,name in enumerate(('f1','f2')):expected[c*len(addresses)+j,r.COL[name]]=(int(runs[row,k+1])>>(position%64))&1
    np.testing.assert_array_equal(stored,expected);assert counts==x['flag_counts']
    assert not np.any(stored[:,[r.COL['wf1'],r.COL['wf2']]])
    with World(initial) as world:
        with patch.object(Program,'evaluate',side_effect=AssertionError('host evaluator')),patch.object(f,'local_step',side_effect=AssertionError('host transition')):world.run(ticks)
        np.testing.assert_array_equal(world.stored,saved['controller_final'])
        assert sha(world.lib._name)==x['binary_sha256']['controller']
    a=stored.reshape(n,g.computation_cells+5,len(r.SCHEMA));np.testing.assert_array_equal(a[:,np.array(g.info),r.COL['data']],old)
    decoded=r.decode_cores(np.ascontiguousarray(a[:,:g.computation_cells].reshape(-1,len(r.SCHEMA))))
    np.testing.assert_array_equal(r.array_from_cells(decoded),saved['decoded']);np.testing.assert_array_equal(saved['decoded'],top)
    result=dict(passed=True,verifier_sha256=sha(__file__),source_files=len(x['source_sha256']),physical_ticks=ticks,final_age=98*f.Q,complete_stored_sites=len(stored),physical_sites=n*f.Q,flag_counts=counts,raw_controller_and_info_preserved=True,controller_replay_exact=True,all_stored_flag_bits_independently_checked=True,prior_cutoff_identical=True,recorded_native_cross_checks=x['complete_native_cross_checks'],seconds=time.monotonic()-started,artifact_sha256=x['artifact_sha256'],limitation='30Q flag suffix remains; this audit checks replay artifacts and composition, not an independent long flag algorithm')
    output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();audit(args.input,args.output)
