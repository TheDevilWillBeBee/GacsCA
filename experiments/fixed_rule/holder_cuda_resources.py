"""Measure bounded CUDA local execution without a large host/device allocation."""
import argparse,hashlib,json,resource,time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import holder_rule as f,holder_quotient as q,holder_program as p,holder_packed as packed,holder_cuda_local as gpu


def execute(output):
    output=Path(output)
    if output.exists():raise FileExistsError('preserve evidence')
    start=time.monotonic();count=160
    a=np.array([[q.encode_cell(q.Cell(address=(center+j)%f.Q,age=1,data=(center+j)%f.Q)) for j in range(-5,6)] for center in range(count)],dtype=np.uint64)
    out,metrics=gpu.step(a);assert np.all(out[:,q.COL['age']]==2)
    rows=3601*(p.layout().computation_cells+5)
    result=dict(passed=True,elapsed_seconds=time.monotonic()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,test_neighborhoods=count,**metrics,benchmark_only_local_kernel=True,large_gpu_executor_implemented=False,packed_double_state_bytes_for_3601_colonies=2*rows*packed.WORDS*8,unpacked_double_state_bytes_for_3601_colonies=2*rows*len(q.SCHEMA)*8,rule_identity=f.identity(),binary_sha256=hashlib.sha256(Path(gpu.library()._name).read_bytes()).hexdigest())
    root=Path(__file__).resolve().parents[2];files=[Path(__file__),root/'gacsca/fixed_rule/holder_cuda_local.py',root/'gacsca/fixed_rule/holder_cuda_local.cu',root/'gacsca/fixed_rule/holder_packed.py',root/'tests/fixed_rule/test_holder_cuda_local.py']
    result['source_sha256']={str(path.relative_to(root)):hashlib.sha256(path.read_bytes()).hexdigest() for path in files};output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('source_sha256','rule_identity')},indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path);execute(parser.parse_args().output)
