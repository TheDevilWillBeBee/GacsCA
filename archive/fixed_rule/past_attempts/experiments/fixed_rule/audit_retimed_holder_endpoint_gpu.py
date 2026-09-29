"""Read-only audit of accelerated endpoints against saved physical trajectories."""
import argparse,hashlib,json,resource,time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_terminal_checks as checks,retimed_holder_program as p,retimed_holder_rule as f


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--reference',required=True);parser.add_argument('--output',required=True);args=parser.parse_args()
    out=Path(args.output);reference=Path(args.reference)
    if out.exists():raise FileExistsError(out)
    started=time.perf_counter();receipt=json.loads(reference.read_text());assert receipt['passed']
    assert sha(reference.with_suffix('.npz'))==receipt['artifact_sha256']
    for path,digest in receipt['source_sha256'].items():assert sha(path)==digest,path
    assert sha(receipt['binary'])==receipt['binary_sha256']
    for path,digest in receipt['references'].items():assert sha(path)==digest,path
    results=[]
    physical=Path('figs/fixed_rule/retimed_holder_cuda_terminal_v2.json');physical_receipt=json.loads(physical.read_text())
    assert sha(physical.with_suffix('.npz'))==physical_receipt['artifact_sha256']
    with np.load(reference.with_suffix('.npz'),allow_pickle=False) as actual,np.load(physical.with_suffix('.npz'),allow_pickle=False) as old:
        for epoch in (1,2):
            pre=old[f'period{epoch}_precommit_bank'];post=old[f'period{epoch}_commit_bank'];signals=old[f'period{epoch}_commit_signals']
            expected=dict(precommit_bank=pre,committed_bank=post,signals=signals)
            for phase,age,at in (('precommit',f.U-1,epoch*f.U-1),('commit',0,epoch*f.U)):
                prefix=f'period{epoch}_{phase}_';state={key[len(prefix):]:actual[key] for key in actual.files if key.startswith(prefix)}
                original={key[len(prefix):]:old[key] for key in old.files if key.startswith(prefix)}
                checks.check(original,expected,age=age,time=at);details=checks.check(state,expected,age=age,time=at)
                results.append(dict(period=epoch,phase=phase,**details))
        damaged=actual['damaged_bank'];healthy=actual['healthy_bank']
        np.testing.assert_array_equal(damaged[:,list(p.layout().info)],healthy[:,list(p.layout().info)])
        different=int(np.count_nonzero(damaged!=healthy));assert different==120
        repair=Path('figs/fixed_rule/retimed_holder_cuda_encoded_repair_v1.json');repair_receipt=json.loads(repair.read_text());assert sha(repair.with_suffix('.npz'))==repair_receipt['artifact_sha256']
        with np.load(repair.with_suffix('.npz'),allow_pickle=False) as z:
            np.testing.assert_array_equal(damaged,z['boundary_1_bank']);np.testing.assert_array_equal(healthy,z['healthy_boundary_1_bank'])
    result=dict(passed=True,checkpoints=results,same_output_different_scratch_words=different,seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,reference=str(reference),reference_sha256=sha(reference),source_sha256={str(path):sha(path) for path in (Path(__file__),Path(checks.__file__))},scope='Complete one-link endpoint comparison with independent saved physical trajectories; no GPU evolution or host simulated transition is performed by this audit.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
