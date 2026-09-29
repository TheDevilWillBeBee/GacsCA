"""Independent saved-state checks; no GPU initialization or evolution."""
import argparse,hashlib,json,resource,time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_terminal_dag as dag,retimed_holder_terminal_reference as replay,retimed_holder_terminal_checks as checks
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_projected as r,retimed_holder_program as p


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def audit(z):
    parents=r.cells_from_array(z['initial_upper']);g=p.layout();n=len(parents);results=[]
    assert n==15
    assert z['initial_bank'].shape==(n,g.memory_count+5)
    np.testing.assert_array_equal(z['initial_bank'][:,list(g.info)],[f.encode_cell(r.lift(x)) for x in parents])
    assert np.count_nonzero(z['initial_bank'][:,list(g.hold)])==n*f.FIELDS
    assert z['initial_signals'].shape==(n,2) and set(z['initial_signals'].ravel())=={0,1}
    for epoch in (1,2):
        expected=dag.terminal(parents);other=replay.terminal(parents)
        for key in expected:np.testing.assert_array_equal(expected[key],other[key])
        following=r.step_ring(parents)
        np.testing.assert_array_equal(expected['committed_bank'][:,list(g.info)],[f.encode_cell(r.lift(x)) for x in following])
        for phase,age,at in (('precommit',f.U-1,epoch*f.U-1),('commit',0,epoch*f.U)):
            prefix=f'period{epoch}_{phase}_';state={key[len(prefix):]:z[key] for key in z if key.startswith(prefix)}
            result=checks.check(state,expected,age=age,time=at)
            results.append(dict(period=epoch,phase=phase,**result))
        parents=following
    return dict(passed=True,checkpoints=results,scope='Saved complete canonical terminal physical-state checks, two one-link periods; diagnostic only, no depth-two execution.')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--reference',required=True);parser.add_argument('--output',required=True);args=parser.parse_args()
    out=Path(args.output);ref=Path(args.reference);artifact=ref.with_suffix('.npz')
    if out.exists():raise FileExistsError(out)
    started=time.perf_counter();receipt=json.loads(ref.read_text());assert receipt['passed']
    assert receipt['descriptor_sha256']==f.self_description().digest() and receipt['rom_sha256']==hashlib.sha256(p.base_rom().tobytes()).hexdigest()
    assert sha(artifact)==receipt['artifact_sha256']
    for path,digest in receipt['source_sha256'].items():assert sha(path)==digest,path
    with np.load(artifact,allow_pickle=False) as z:result=audit(z)
    paths=(Path(__file__),Path(dag.__file__),Path(replay.__file__),Path(checks.__file__))
    result.update(seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,reference=str(ref),reference_sha256=sha(ref),artifact_sha256=sha(artifact),source_sha256={str(path):sha(path) for path in paths})
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
