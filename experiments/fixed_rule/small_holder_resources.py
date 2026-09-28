"""Measure the small-rule identity, budgets and bounded CUDA building block."""
import argparse,hashlib,json,resource,time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import small_holder_rule as f,small_holder_core as c,small_holder_program as p,small_holder_projected as r,small_holder_quotient as q,small_holder_cuda_local as gpu


def execute(output):
    output=Path(output)
    if output.exists():raise FileExistsError('preserve evidence')
    started=time.monotonic();g=p.layout()
    neighborhoods=np.array([[q.encode_cell(q.Cell(address=(center+j)%f.Q,age=1,data=(center+j)%f.Q)) for j in range(-5,6)] for center in range(160)],dtype=np.uint64)
    result,metrics=gpu.step(neighborhoods);assert np.all(result[:,q.COL['age']]==2)
    rests=[later-end for end,later in zip(c.ACTIVE_ENDS,(*c.RESET_AGES[1:],f.U))]
    row=dict(passed=True,rule=r.identity(),timing=g.timing_certificate(),memory_rows=g.memory_count,rom_instructions=len(g.instructions),minimum_rest_ticks=min(rests),gray_local_repair_estimate=2*f.Q+1100,gray_estimate_is_not_a_new_noise_theorem=True,forcing_ticks=c.WF_END-c.WF_START,**metrics,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,seconds=time.monotonic()-started,
             depth_two_cells_per_top_cell=f.Q**2,depth_two_ticks_per_top_step=f.U**2,
             dense_double_buffer_bytes_per_top_cell=2*((r.WIDTH+63)//64)*8*f.Q*f.Q,
             hypothetical_data_bank_bytes_per_top_cell=f.Q*g.memory_count*8,
             hypothetical_data_bank_bytes_for_15_top_cells=15*f.Q*g.memory_count*8,
             data_bank_only_executor_implemented=False,complete_gpu_executor_implemented=False,
             depth_two_dynamic_execution_completed=False,binary_sha256=hashlib.sha256(Path(gpu.library()._name).read_bytes()).hexdigest())
    files=[Path(__file__),Path('gacsca/fixed_rule/small_holder_parameters.py'),Path('gacsca/fixed_rule/small_holder_cuda_local.py'),Path('gacsca/fixed_rule/small_holder_cuda_local.cu'),Path('gacsca/fixed_rule/small_holder_packed.py')]
    row['source_sha256']={str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in files}
    output.write_text(json.dumps(row,indent=2)+'\n')
    print(json.dumps({k:v for k,v in row.items() if k not in ('rule','source_sha256')},indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path)
    execute(parser.parse_args().output)
