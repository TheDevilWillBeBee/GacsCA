"""Independent saved-state comparisons for the actual bounded GPU replay."""
import argparse
import json
from pathlib import Path
import resource
import time
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f
from gacsca.fixed_rule import retimed_holder_early_flag_snapshot as view
from gacsca.fixed_rule import retimed_holder_wide_inert_storage as storage
from experiments.fixed_rule.audit_retimed_holder_prefix_embedding import sha


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
    out=Path(parser.parse_args().output)
    if out.exists():raise FileExistsError(out)
    started=time.perf_counter();root=Path('figs/fixed_rule')
    paths={name:root/('retimed_holder_'+name+'.json') for name in ('fresh_repair_gpu_v1','fresh_geometry_projection_v1','fresh_full_repair_v2')}
    for name,path in paths.items():
        doc=json.loads(path.read_text());assert doc['passed']
        for source,digest in {**doc['source_sha256'],**doc.get('binary_sha256',{})}.items():assert sha(source)==digest,source
        assert sha(path.with_suffix('.npz'))==doc['artifact_sha256']
    gpu=json.loads(paths['fresh_repair_gpu_v1'].read_text());assert gpu['same_time_attachment']['physical_transitions']==0
    keys=('bank','active_rows','counts','flags','signals','age','time')
    with np.load(paths['fresh_repair_gpu_v1'].with_suffix('.npz'),allow_pickle=False) as z:
        attached={key:z['attached_'+key] for key in keys}
        before={key:z['before_attachment_'+key] for key in keys}
        a=view.View(before,z['before_attachment_positions'],z['before_attachment_values']);b=view.View(attached)
        checked=0
        for col in range(17):
            sites=np.arange(col*f.Q,(col+1)*f.Q)
            np.testing.assert_array_equal(a.cells(sites),b.cells(sites));checked+=len(sites)*f.FIELDS
        del a,b
        with np.load(paths['fresh_geometry_projection_v1'].with_suffix('.npz'),allow_pickle=False) as geometry:
            for tick,label in ((640,'attached'),(1024,'tick1024')):
                planes=z[label+'_flags'][8*f.Q//64:9*f.Q//64]
                flags=((planes[:,None,:] >> np.arange(64,dtype=np.uint64)[None,:,None])&np.uint64(1)).reshape(f.Q,2)
                np.testing.assert_array_equal(flags,geometry[f'tick{tick}_geometry'][:,1:])
        planes=z['tick16988_flags'];assert sum(int(x).bit_count() for x in planes[:,0])==2
        assert planes[8*f.Q//64,0]==3 and not np.any(planes[:,1])
        final={key:z['final_'+key] for key in keys};image=view.View(final)
        with np.load(paths['fresh_full_repair_v2'].with_suffix('.npz'),allow_pickle=False) as cpu:
            reference=storage.raw_words(cpu['healthy_final_procedures'],cpu['healthy_final_Signals'],16989,np.arange(f.Q))
            np.testing.assert_array_equal(image.cells(8*f.Q+np.arange(f.Q)),reference)
        assert not np.any(final['flags'])
    result=dict(passed=True,lossless_attachment_complete_raw_words_rechecked=checked,
                GPU_CPU_geometry_words_compared=2*f.Q*2,
                exact_last_two_Flag1_sites_checked=True,
                GPU_CPU_complete_final_raw_words_compared=f.Q*f.FIELDS,
                source_receipt_sha256=sha(paths['fresh_repair_gpu_v1']),
                descriptor_sha256=f.self_description().digest(),input_sha256={str(path):sha(path) for path in paths.values()},
                source_sha256={str(path):sha(path) for path in (Path(__file__),Path(view.__file__),Path(storage.__file__))},
                seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                scope='CPU-only audit of saved actual GPU states: full lossless attachment, '
                      'geometry comparisons, final flag extinction and every raw output word '
                      'of the central colony against the independent CPU physical reference. '
                      'Not an independent scalar evaluation of every GPU transition.')
    with out.open('x') as stream:stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
