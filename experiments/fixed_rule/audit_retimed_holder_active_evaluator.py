"""Independent full-lattice step audit of actual live checkpoint artifacts."""
import argparse, hashlib, json, resource, time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_native as native
from gacsca.fixed_rule import retimed_holder_active_snapshot as active


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--input',required=True);parser.add_argument('--output',required=True);args=parser.parse_args()
    path=Path(args.input);out=Path(args.output)
    if out.exists():raise FileExistsError(out)
    started=time.perf_counter();receipt=json.loads(path.read_text());assert receipt['passed']
    artifact=path.with_suffix('.npz');assert sha(artifact)==receipt['artifact_sha256']
    for name,digest in receipt['source_sha256'].items():assert sha(name)==digest,name
    fields=('bank','active_rows','counts','flags','signals','age','time');checks=[]
    with np.load(artifact,allow_pickle=False) as saved:
        for label in ('previous','checkpoint','after','second'):
            state={key:saved[label+'_'+key] for key in fields}
            np.testing.assert_array_equal(active.render(state),saved[label+'_raw'])
        for before,after in (('previous','checkpoint'),('checkpoint','after'),('after','second')):
            source=np.ascontiguousarray(saved[before+'_raw']);target=np.empty_like(source)
            # Complete F, all 32768 sites, all 154 fields; Address is canonical,
            # so the output metadata already matches G's projection.
            native.library().retimed_holder_ring(native.pointer(source),native.pointer(target),len(source))
            np.testing.assert_array_equal(target,saved[after+'_raw'])
            checks.append(dict(before=before,after=after,raw_words=target.size))
            print(json.dumps(checks[-1]),flush=True)
        healthy=saved['after_raw'];checkpoint=saved['checkpoint_raw']
        for count in (2,3):
            source=checkpoint.copy();faults=saved[f'case{count}_faults'];frontier=saved[f'case{count}_frontier'].astype(np.int64)
            assert len(faults)==count
            for pos,field,xor in faults:source[int(pos),int(field)]^=xor
            assert np.count_nonzero(source!=checkpoint)==count
            # Audit the entire faulty lattice, not merely the saved causal cone.
            target=np.empty_like(source)
            native.library().retimed_holder_ring(native.pointer(source),native.pointer(target),len(source))
            np.testing.assert_array_equal(target[frontier],saved[f'case{count}_after'])
            mask=np.ones(f.Q,dtype=bool);mask[frontier]=False
            np.testing.assert_array_equal(target[mask],healthy[mask])
            changed=int(np.count_nonzero(target!=healthy))
            assert (changed==0)==(count==2)
            assert changed==receipt['cases'][count-2]['raw_output_differences']
            checks.append(dict(fault_copies=count,raw_words=target.size,changed_raw_words=changed))
        for key in fields:np.testing.assert_array_equal(saved['healthy_terminal_'+key],saved['repaired_terminal_'+key])
    result=dict(passed=True,checks=checks,total_complete_lattice_steps=5,total_raw_output_words_checked=5*f.Q*f.FIELDS,source_receipt_sha256=sha(path),artifact_sha256=sha(artifact),seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,audit_source_sha256=sha(__file__),scope='All raw fields of three adjacent healthy physical ticks and both fault-case ticks; CPU full descriptor independently executes every lattice site. Whole terminal snapshot equality. Shared descriptor parity is not an independent proof of source fidelity.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__':main()
