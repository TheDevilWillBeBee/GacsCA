"""Independent scalar/word-descriptor comparison with saved physical phase output.

Recreates only the initial fixture and expected outputs, not the physical run.
The saved execution output hash is checked against both independent references.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_core as c,retimed_holder_projected as r
from experiments.fixed_rule import run_retimed_holder_cpu_evaluation as execution
from experiments.fixed_rule.audit_small_holder_position_events import sha


def audit(path):
    saved=json.loads(Path(path).read_text());assert saved['passed']
    for source,wanted in saved['source_sha256'].items():assert sha(source)==wanted,source
    assert saved['descriptor_sha256']==f.self_description().digest()
    upper,_=execution.fixture(saved['colonies']);n=len(upper);result=[];changed=0
    for col in range(n):
        cells=tuple(r.lift(upper[(col+j)%n]) for j in f.NEIGHBORHOOD)
        raw=f.decode_cell(f.self_description().evaluate(tuple(word for cell in cells for word in f.encode_cell(cell))))
        scalar=f.local_step(cells);assert raw==scalar,('scalar/descriptor mismatch',col)
        normal=r.lift(r.project(raw));result.append(f.encode_cell(normal))
        for offset in f.OFFSETS:
            for name in ('head',*c.CONTROL):
                changed+=getattr(normal,f's{offset+2}_{name}')!=getattr(cells[7],f's{offset+2}_{name}')
    digest=hashlib.sha256(np.array(result,dtype=np.uint64).tobytes()).hexdigest()
    assert digest==saved['output_sha256'],'physical Hold hash differs from scalar/descriptor reference'
    assert changed>0,'fixture failed to exercise represented controller dynamics'
    return dict(passed=True,colonies=n,raw_words_checked=n*f.FIELDS,represented_controller_words_changed=changed,
                scalar_and_descriptor_agree=True,saved_physical_output_matches=True,output_sha256=digest,
                execution_sha256=sha(path))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--execution',action='append',required=True);parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();rows=[audit(path) for path in args.execution]
    result=dict(passed=True,cases=rows,source_sha256={str(path):sha(path) for path in (Path(__file__),Path(execution.__file__),Path(f.__file__),Path(c.__file__),Path(r.__file__))},
                input_sha256={path:sha(path) for path in args.execution},seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                limitation='Independent saved-output audit for these complete evaluation phases; initialized histories are premises. No full-period, nested-execution or noise claim.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__':main()
